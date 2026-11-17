"""Recover public author images with authenticated resolution and bounded retries.

Preserve the original selection ledger; extend its size-ranked test quota to 15.
Only availability and published preparation requirements affect selection.
"""

import argparse
import hashlib
import json
import shutil
import subprocess
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import httpx
from provision_cohort import get_archive, get_dataset

from reproscout.tasks import UPSTREAM_COMMIT, sanitized_archive, write_json

ROOT = Path(__file__).resolve().parents[1]
ACCEPT = ", ".join(
    [
        "application/vnd.docker.distribution.manifest.v2+json",
        "application/vnd.oci.image.manifest.v1+json",
        "application/vnd.docker.distribution.manifest.list.v2+json",
        "application/vnd.oci.image.index.v1+json",
    ]
)


def retry_delay(attempt, header=None):
    """Respect either legal Retry-After form, with exponential local backoff."""
    seconds = 0
    if header:
        try:
            seconds = float(header)
        except ValueError:
            try:
                seconds = (
                    parsedate_to_datetime(header) - datetime.now(timezone.utc)
                ).total_seconds()
            except (ValueError, TypeError):
                seconds = 0
    return max(60 * 2**attempt, seconds)


def resolve(image):
    repository, tag = image.removeprefix("registry.codeocean.com/").rsplit(":", 1)
    with httpx.Client(timeout=90, follow_redirects=True) as client:
        auth = client.get(
            "https://codeocean.com/api/docker_auth",
            params={"service": "registry.codeocean.com", "scope": f"repository:{repository}:pull"},
        )
        auth.raise_for_status()
        token = auth.json().get("token") or auth.json()["access_token"]
        headers = {"Authorization": "Bearer " + token, "Accept": ACCEPT}
        response = client.get(
            f"https://registry.codeocean.com/v2/{repository}/manifests/{tag}", headers=headers
        )
        response.raise_for_status()
        body = response.json()
        if "manifests" in body:
            entry = next(
                m
                for m in body["manifests"]
                if m.get("platform", {}).get("architecture") == "amd64"
                and m["platform"].get("os") == "linux"
            )
            response = client.get(
                f"https://registry.codeocean.com/v2/{repository}/manifests/{entry['digest']}",
                headers=headers,
            )
            response.raise_for_status()
            body = response.json()
        digest = "sha256:" + hashlib.sha256(response.content).hexdigest()
        if response.headers.get("docker-content-digest", digest) != digest:
            raise ValueError("Registry manifest digest mismatch")
        return "registry.codeocean.com/" + repository + "@" + digest, body


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--target", type=int, default=15)
    args = parser.parse_args()
    original = json.loads((ROOT / "manifests/selection.json").read_text())
    if not (ROOT / "private/core_test.json").exists():
        get_dataset("test")
    records = {
        r["capsule_id"]: r for r in json.loads((ROOT / "private/core_test.json").read_text())
    }
    candidates = sorted(
        [r.copy() for r in original["records"] if r["split"] == "test"],
        key=lambda r: r.get("archive_bytes") or 10**15,
    )
    selected = []
    archives = {}
    for item in candidates:
        if len(selected) >= args.target:
            item.update(decision="not_selected", reason="Expanded size-ranked quota filled")
            continue
        if item.get("archive_bytes") is None or item["archive_bytes"] > 50_000_000:
            continue
        try:
            body, instructions, tag = get_archive(records[item["task_id"]])
            if "--gpus" in instructions or "--runtime=nvidia" in instructions or not tag:
                item.update(
                    decision="excluded",
                    reason="Explicit GPU requirement or no archived author image",
                )
                continue
            item.update(
                decision="selected",
                reason="Expanded size-ranked CPU cohort; no model scores used",
                image_tag=tag,
            )
            selected.append(item)
            archives[item["task_id"]] = body
        except Exception as exc:
            item.update(decision="excluded", reason=f"Archive preparation: {type(exc).__name__}")
    write_json(
        ROOT / "manifests/selection-v2.json",
        {
            "target_heldout": args.target,
            "records": candidates,
            "rule": "Original archive-size ordering; CPU author image; <=50 MB; no score-based replacements",
        },
    )
    ledger_path = ROOT / "manifests/recovery-v2.json"
    ledger = json.loads(ledger_path.read_text()) if ledger_path.exists() else {}
    ready = []
    for item in selected:
        cid = item["task_id"]
        record = records[cid]
        folder = ROOT / "data" / cid
        folder.mkdir(exist_ok=True)
        attempts = ledger.setdefault(cid, {"image_tag": item["image_tag"], "attempts": []})
        existing_manifest = ROOT / f"manifests/{cid}.json"
        if existing_manifest.exists() and any(
            event.get("status") == "ready" for event in attempts["attempts"]
        ):
            cached = json.loads(existing_manifest.read_text())
            check = subprocess.run(
                ["docker", "image", "inspect", cached["image"]], capture_output=True, check=False
            )
            if check.returncode == 0:
                info = json.loads(check.stdout)[0]
                prepared = ROOT / cached["prepared_path"]
                if (
                    cached["image"] in info["RepoDigests"]
                    and info.get("Architecture") == "amd64"
                    and prepared.is_file()
                    and hashlib.sha256(prepared.read_bytes()).hexdigest()
                    == cached["prepared_sha256"]
                ):
                    ready.append(cid)
                    print(cid, "ready (local verified cache; no registry request)", flush=True)
                    continue
        success = False
        for attempt in range(4):
            event = {"at": datetime.now(timezone.utc).isoformat()}
            started = time.monotonic()
            try:
                image, remote = resolve(item["image_tag"])
                event.update(
                    image=image,
                    manifest_status=200,
                    compressed_layer_bytes=sum(x["size"] for x in remote["layers"]),
                )
                existing = subprocess.run(
                    ["docker", "image", "inspect", image], capture_output=True, check=False
                )
                if existing.returncode:
                    free = shutil.disk_usage(ROOT).free
                    if free < max(12_000_000_000, 3 * event["compressed_layer_bytes"]):
                        raise RuntimeError(
                            "Host disk reserve reached; free only project-owned image cache before resuming"
                        )
                    log = folder / f"recovery-v2-{len(attempts['attempts']) + 1}.log"
                    with log.open("w") as output:
                        pull = subprocess.run(
                            ["docker", "pull", "--platform", "linux/amd64", image],
                            stdout=output,
                            stderr=subprocess.STDOUT,
                            timeout=1200,
                            check=False,
                        )
                    if pull.returncode:
                        raise RuntimeError("Digest pull failed; see recorded pull log")
                info = json.loads(subprocess.check_output(["docker", "image", "inspect", image]))[0]
                if info.get("Architecture") != "amd64" or info.get("Os") != "linux":
                    raise ValueError("Author image is not linux/amd64")
                if image not in info["RepoDigests"]:
                    raise ValueError("Local image does not match resolved digest")
                body = archives[cid]
                safe, inventory = sanitized_archive(body)
                (folder / "prepared.tar").write_bytes(safe)
                manifest = {
                    "task_id": cid,
                    "split": "official_test",
                    "language": record["language"],
                    "vision": item["vision"],
                    "title": record["capsule_title"],
                    "doi": record["capsule_doi"],
                    "task_prompt": record["task_prompt"],
                    "questions": {f"q{i}": q for i, q in enumerate(record["results"][0], 1)},
                    "source_commit": UPSTREAM_COMMIT,
                    "capsule_url": f"https://corebench.cs.princeton.edu/capsules/{cid}.tar.gz",
                    "capsule_sha256": hashlib.sha256(body).hexdigest(),
                    "prepared_sha256": hashlib.sha256(safe).hexdigest(),
                    "image": image,
                    "platform": "linux/amd64",
                    "prepared_path": f"data/{cid}/prepared.tar",
                    "answers_path": f"private/{cid}.answers.json",
                    "input_inventory": inventory,
                    "mode": "Prepared author environment, not unchanged Medium",
                }
                write_json(ROOT / f"manifests/{cid}.json", manifest)
                write_json(ROOT / f"private/{cid}.answers.json", record["results"])
                event.update(status="ready", image_size_bytes=info["Size"])
                success = True
            except httpx.HTTPStatusError as exc:
                event.update(
                    status="failed",
                    http_status=exc.response.status_code,
                    endpoint=str(exc.request.url).split("?")[0],
                    retry_after=exc.response.headers.get("retry-after"),
                )
            except Exception as exc:
                event.update(status="failed", error=str(exc))
            event["seconds"] = time.monotonic() - started
            attempts["attempts"].append(event)
            write_json(ledger_path, ledger)
            print(
                cid, event["status"], event.get("http_status", event.get("error", "")), flush=True
            )
            if success:
                ready.append(cid)
                break
            if "disk reserve" in event.get("error", ""):
                raise RuntimeError(event["error"])
            if attempt < 3:
                delay = retry_delay(attempt, event.get("retry_after"))
                time.sleep(delay)
        if not success:
            print("Unavailable task retained in selection ledger:", cid, flush=True)
    old = json.loads((ROOT / "experiments/prepared-v1/freeze-execution.json").read_text())
    write_json(
        ROOT / "manifests/cohort.json",
        {"development": old["cohort"]["development"], "heldout": ready},
    )
    print(f"Ready held-out images: {len(ready)}/{args.target}", flush=True)


if __name__ == "__main__":
    main()
