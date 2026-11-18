"""Run the predeclared three-arm training comparison without scientific reruns."""

import argparse
import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

from validate_network import probe

from reproscout.cli import load_key
from reproscout.experiment import file_hash
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def records(task, condition, experiment):
    found = []
    for path in sorted((ROOT / "runs").glob("*/summary.json")):
        row = json.loads(path.read_text())
        if (row.get("experiment_id"), row.get("condition"), row.get("repeat")) != (
            experiment,
            condition,
            1,
        ):
            continue
        if json.loads((path.parent / "manifest.json").read_text())["task_id"] == task:
            found.append(row)
    return found


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--key-file", type=Path, required=True)
    args = parser.parse_args()
    folder = ROOT / "reports/lesson-development-v5"
    folder.mkdir(exist_ok=True)
    snapshot = folder / "candidate-freeze.json"
    if not snapshot.exists():
        paths = list((ROOT / "src").rglob("*.py"))
        paths += list((ROOT / "configs").glob("*.json"))
        paths += list((ROOT / "manifests").glob("*.json"))
        paths += [
            ROOT / p
            for p in [
                "uv.lock",
                "pyproject.toml",
                "lessons/development-v1.md",
                "lessons/development-v2.md",
                "docs/lesson-revision-protocol.md",
                "scripts/run_lesson_development.py",
                "scripts/validate_network.py",
            ]
        ]
        write_json(snapshot, {"files": {str(p.relative_to(ROOT)): file_hash(p) for p in paths}})
    frozen = json.loads(snapshot.read_text())["files"]
    cohort = json.loads((ROOT / "manifests/cohort.json").read_text())
    arms = [
        ("A", "development-v5", None),
        ("B", "development-legacy-v5", "lessons/development-v1.md"),
        ("B", "development-v5", "lessons/development-v2.md"),
    ]
    for index, task in enumerate(cohort["development"]):
        for condition, experiment, lesson in arms if index % 2 == 0 else reversed(arms):
            while True:
                assert all(file_hash(ROOT / p) == h for p, h in frozen.items()), "Candidate changed"
                old = records(task, condition, experiment)
                scientific = [x for x in old if not x["infrastructure_failure"]]
                assert len(scientific) <= 1, "Duplicate scientific outcome"
                if scientific:
                    break
                if len(old) >= 3:
                    raise RuntimeError("Infrastructure retries exhausted; development incomplete")
                load_key(args.key_file)
                asyncio.run(probe(2, folder / "preflights" / str(time.time_ns())))
                command = [
                    sys.executable,
                    "-m",
                    "reproscout",
                    "run",
                    "--manifest",
                    f"manifests/{task}.json",
                    "--condition",
                    condition,
                    "--repeat",
                    "1",
                    "--experiment-id",
                    experiment,
                    "--key-file",
                    str(args.key_file),
                ]
                if lesson:
                    command += ["--lessons", lesson]
                print(f"Development {task} {condition} {experiment}", flush=True)
                subprocess.run(command, cwd=ROOT, check=True)
                if records(task, condition, experiment)[-1]["infrastructure_failure"]:
                    time.sleep(30)
    print("All fifteen scientific development outcomes retained.", flush=True)


if __name__ == "__main__":
    main()
