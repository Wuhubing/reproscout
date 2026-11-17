"""Provision a size-ranked CPU development/test cohort before agent evaluation.

This script never calls a model. Downloads remain ignored by Git. Membership is
based on archive size, platform requirements, and one development vision slot.
"""

import concurrent.futures
import hashlib
import io
import json
import re
import subprocess
import tarfile
import time
from pathlib import Path

import httpx

from reproscout.tasks import UPSTREAM_COMMIT, sanitized_archive, write_json

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "private"
CACHE.mkdir(exist_ok=True)


def get_dataset(split):
    suffix = ".json.gpg" if split == "test" else ".json"
    url = f"https://raw.githubusercontent.com/siegelz/core-bench/{UPSTREAM_COMMIT}/benchmark/dataset/core_{split}{suffix}"
    path = CACHE / f"core_{split}{suffix}"
    if not path.exists():
        r = httpx.get(url, timeout=60, follow_redirects=True)
        r.raise_for_status()
        path.write_bytes(r.content)
    if split == "test":
        subprocess.run(
            [
                "gpg",
                "--batch",
                "--yes",
                "--pinentry-mode",
                "loopback",
                "--passphrase",
                "reproducibility",
                "--output",
                str(CACHE / "core_test.json"),
                "--decrypt",
                str(path),
            ],
            capture_output=True,
            check=True,
        )
    return json.loads((CACHE / f"core_{split}.json").read_text()), url


def size(record):
    try:
        r = httpx.head(
            f"https://corebench.cs.princeton.edu/capsules/{record['capsule_id']}.tar.gz",
            timeout=30,
            follow_redirects=True,
        )
        r.raise_for_status()
        return int(r.headers["content-length"])
    except Exception:
        return None


def get_archive(record):
    cid = record["capsule_id"]
    path = ROOT / "data" / f"{cid}.tar.gz"
    path.parent.mkdir(exist_ok=True)
    if not path.exists():
        r = httpx.get(
            f"https://corebench.cs.princeton.edu/capsules/{cid}.tar.gz",
            timeout=120,
            follow_redirects=True,
        )
        r.raise_for_status()
        path.write_bytes(r.content)
    body = path.read_bytes()
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as tf:
        member = next(m for m in tf.getmembers() if m.name.endswith("/REPRODUCING.md"))
        instructions = tf.extractfile(member).read().decode()
    images = re.findall(r"registry\.codeocean\.com/published/[A-Za-z0-9:-]+", instructions)
    return body, instructions, images[0] if images else None


def main():
    selected = []
    decisions = []
    for split in ["train", "test"]:
        records, url = get_dataset(split)
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            sizes = list(pool.map(size, records))
        candidates = sorted(zip(records, sizes), key=lambda pair: pair[1] or 10**15)
        accepted = []
        target = 5 if split == "train" else 10
        for record, nbytes in candidates:
            cid = record["capsule_id"]
            decision = {
                "task_id": cid,
                "split": split,
                "archive_bytes": nbytes,
                "language": record["language"],
                "vision": any("fig" in q.lower() for q in record["results"][0]),
            }
            if nbytes is None or nbytes > 50_000_000:
                decision["decision"] = "excluded"
                decision["reason"] = "Archive unavailable or above 50 MB preparation cap"
            elif len(accepted) >= target and (
                split == "test" or any(x["vision"] for x in accepted)
            ):
                decision["decision"] = "not_selected"
                decision["reason"] = "Size-ranked quota already filled"
            else:
                try:
                    body, instructions, image = get_archive(record)
                    if "--gpus" in instructions or "--runtime=nvidia" in instructions:
                        decision["decision"] = "excluded"
                        decision["reason"] = "Explicit GPU requirement"
                    elif not image:
                        decision["decision"] = "excluded"
                        decision["reason"] = "No archived author image"
                    else:
                        item = {
                            **decision,
                            "record": record,
                            "image_tag": image,
                            "body": body,
                            "dataset_url": url,
                        }
                        if len(accepted) >= target:
                            # Reserve one development vision example without looking at scores.
                            displaced = accepted.pop()
                            for old in decisions:
                                if old["task_id"] == displaced["task_id"]:
                                    old.update(
                                        decision="not_selected",
                                        reason="Replaced to reserve a development vision example",
                                    )
                        accepted.append(item)
                        decision.update(
                            decision="selected",
                            reason="Smallest eligible archive; development includes a vision example",
                        )
                except Exception as exc:
                    decision.update(
                        decision="excluded", reason=f"Preparation failed: {type(exc).__name__}"
                    )
            decisions.append(decision)
        selected.extend(accepted)
    write_json(
        ROOT / "manifests/selection.json",
        {
            "rule": "CPU author image, <=50 MB archive, ascending size; 5 development with >=1 vision, 10 heldout",
            "records": decisions,
        },
    )

    def provision(item):
        cid = item["task_id"]
        start = time.monotonic()
        folder = ROOT / "data" / cid
        folder.mkdir(exist_ok=True)
        pull = subprocess.run(
            ["docker", "pull", "--platform", "linux/amd64", item["image_tag"]],
            capture_output=True,
            text=True,
            check=False,
        )
        (folder / "image-pull.log").write_text(pull.stdout + pull.stderr)
        if pull.returncode:
            return {
                "task_id": cid,
                "status": "image_pull_failed",
                "seconds": time.monotonic() - start,
            }
        info = json.loads(
            subprocess.check_output(["docker", "image", "inspect", item["image_tag"]])
        )[0]
        safe, inventory = sanitized_archive(item["body"])
        (folder / "prepared.tar").write_bytes(safe)
        record = item["record"]
        questions = {f"q{i}": q for i, q in enumerate(record["results"][0], 1)}
        manifest = {
            k: item[k] for k in ["task_id", "language", "vision", "archive_bytes", "dataset_url"]
        }
        manifest.update(
            title=record["capsule_title"],
            doi=record["capsule_doi"],
            split="official_" + item["split"],
            task_prompt=record["task_prompt"],
            questions=questions,
            source_commit=UPSTREAM_COMMIT,
            capsule_url=f"https://corebench.cs.princeton.edu/capsules/{cid}.tar.gz",
            capsule_sha256=hashlib.sha256(item["body"]).hexdigest(),
            prepared_sha256=hashlib.sha256(safe).hexdigest(),
            image=info["RepoDigests"][0],
            platform="linux/amd64",
            prepared_path=f"data/{cid}/prepared.tar",
            answers_path=f"private/{cid}.answers.json",
            input_inventory=inventory,
            mode="Prepared author environment, not unchanged CORE-Bench Medium",
        )
        write_json(ROOT / f"manifests/{cid}.json", manifest)
        write_json(ROOT / f"private/{cid}.answers.json", record["results"])
        return {
            "task_id": cid,
            "split": manifest["split"],
            "status": "ready",
            "seconds": time.monotonic() - start,
            "image": manifest["image"],
            "image_size_bytes": info["Size"],
        }

    outcomes = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        for outcome in pool.map(provision, selected):
            outcomes.append(outcome)
            print(json.dumps(outcome), flush=True)
            write_json(ROOT / "manifests/provisioning.json", outcomes)
    ready = [x for x in outcomes if x["status"] == "ready"]
    write_json(
        ROOT / "manifests/cohort.json",
        {
            "development": [x["task_id"] for x in ready if x["split"] == "official_train"],
            "heldout": [x["task_id"] for x in ready if x["split"] == "official_test"],
        },
    )


if __name__ == "__main__":
    main()
