"""Retry rate-limited image preparation without changing task selection."""

import hashlib
import io
import json
import re
import subprocess
import tarfile
import time
from pathlib import Path

from reproscout.tasks import UPSTREAM_COMMIT, sanitized_archive, write_json

ROOT = Path(__file__).resolve().parents[1]
selection = json.loads((ROOT / "manifests/selection.json").read_text())["records"]
outcomes = json.loads((ROOT / "manifests/provisioning.json").read_text())
write_json(ROOT / "manifests/provisioning-first-attempt.json", outcomes)
ready = {r["task_id"] for r in outcomes if r["status"] == "ready"}
for item in selection:
    cid = item["task_id"]
    if item["decision"] != "selected" or cid in ready:
        continue
    records = json.loads((ROOT / f"private/core_{item['split']}.json").read_text())
    record = next(r for r in records if r["capsule_id"] == cid)
    body = (ROOT / f"data/{cid}.tar.gz").read_bytes()
    folder = ROOT / "data" / cid
    with tarfile.open(fileobj=io.BytesIO(body), mode="r:gz") as tf:
        member = next(m for m in tf.getmembers() if m.name.endswith("/REPRODUCING.md"))
        instructions = tf.extractfile(member).read().decode()
    image = re.findall(r"registry\.codeocean\.com/published/[A-Za-z0-9:-]+", instructions)[0]
    started = time.monotonic()
    success = False
    for attempt in range(1, 4):
        try:
            process = subprocess.run(
                ["docker", "pull", "--platform", "linux/amd64", image],
                capture_output=True,
                text=True,
                timeout=600,
                check=False,
            )
            (folder / f"image-retry-{attempt}.log").write_text(process.stdout + process.stderr)
            success = process.returncode == 0
            print(f"{cid} attempt {attempt}: {'ready' if success else 'failed'}", flush=True)
            if success:
                break
            if "429" not in process.stderr:
                break
        except subprocess.TimeoutExpired:
            print(f"{cid} attempt {attempt}: provisioning timeout", flush=True)
        if attempt < 3:
            time.sleep(30)
    if not success:
        continue
    info = json.loads(subprocess.check_output(["docker", "image", "inspect", image]))[0]
    safe, inventory = sanitized_archive(body)
    (folder / "prepared.tar").write_bytes(safe)
    manifest = {
        "task_id": cid,
        "split": "official_" + item["split"],
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
        "image": info["RepoDigests"][0],
        "platform": "linux/amd64",
        "prepared_path": f"data/{cid}/prepared.tar",
        "answers_path": f"private/{cid}.answers.json",
        "input_inventory": inventory,
        "mode": "Prepared author environment, not unchanged Medium",
    }
    write_json(ROOT / f"manifests/{cid}.json", manifest)
    write_json(ROOT / f"private/{cid}.answers.json", record["results"])
    outcomes = [r for r in outcomes if r["task_id"] != cid] + [
        {
            "task_id": cid,
            "split": manifest["split"],
            "status": "ready",
            "seconds": time.monotonic() - started,
            "image": manifest["image"],
            "retry": True,
        }
    ]
    write_json(ROOT / "manifests/provisioning.json", outcomes)
    ready.add(cid)
write_json(
    ROOT / "manifests/cohort.json",
    {
        "development": [
            i["task_id"] for i in selection if i["task_id"] in ready and i["split"] == "train"
        ],
        "heldout": [
            i["task_id"] for i in selection if i["task_id"] in ready and i["split"] == "test"
        ],
    },
)
