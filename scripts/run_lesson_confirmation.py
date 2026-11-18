"""Validate the one permitted second candidate on all five training tasks."""

import argparse
import asyncio
import json
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from run_lesson_development import records
from validate_network import probe

from reproscout.cli import load_key
from reproscout.experiment import file_hash
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key-file", type=Path, required=True)
    args = parser.parse_args()
    prior = json.loads((ROOT / "reports/development-v5-candidate1-validation.json").read_text())
    assert not prior["passed"] and prior["checks"]["fifteen_scientific_outcomes"]
    folder = ROOT / "reports/lesson-confirmation-v5"
    folder.mkdir(exist_ok=True)
    snapshot = folder / "candidate-freeze.json"
    if not snapshot.exists():
        paths = list((ROOT / "src").rglob("*.py")) + list((ROOT / "configs").glob("*.json"))
        paths += list((ROOT / "manifests").glob("*.json"))
        paths += [
            ROOT / p
            for p in [
                "uv.lock",
                "pyproject.toml",
                "lessons/development-v2b.md",
                "docs/lesson-confirmation-protocol.md",
                "scripts/run_lesson_confirmation.py",
                "scripts/run_lesson_development.py",
                "scripts/validate_network.py",
            ]
        ]
        write_json(
            snapshot,
            {
                "created_at": datetime.now(timezone.utc).isoformat(),
                "files": {str(p.relative_to(ROOT)): file_hash(p) for p in paths},
            },
        )
    frozen = json.loads(snapshot.read_text())["files"]
    cohort = json.loads((ROOT / "manifests/cohort.json").read_text())
    for task in cohort["development"]:
        while True:
            assert all(file_hash(ROOT / p) == h for p, h in frozen.items()), "Candidate changed"
            old = records(task, "B", "development-confirmation-v5")
            scientific = [x for x in old if not x["infrastructure_failure"]]
            assert len(scientific) <= 1
            if scientific:
                break
            if len(old) >= 3:
                raise RuntimeError("Confirmation infrastructure retries exhausted; incomplete")
            load_key(args.key_file)
            asyncio.run(probe(2, folder / "preflights" / str(time.time_ns())))
            print(f"Confirmation {task} B", flush=True)
            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "reproscout",
                    "run",
                    "--manifest",
                    f"manifests/{task}.json",
                    "--condition",
                    "B",
                    "--repeat",
                    "1",
                    "--experiment-id",
                    "development-confirmation-v5",
                    "--lessons",
                    "lessons/development-v2b.md",
                    "--key-file",
                    str(args.key_file),
                ],
                cwd=ROOT,
                check=True,
            )
            if records(task, "B", "development-confirmation-v5")[-1]["infrastructure_failure"]:
                time.sleep(30)
    print("All five confirmation scientific outcomes retained.", flush=True)


if __name__ == "__main__":
    main()
