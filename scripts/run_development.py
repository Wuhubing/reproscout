"""Run a fixed five-task A/B development validation matrix before freezing v3."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--key-file", required=True)
    args = parser.parse_args()
    cohort = json.loads((ROOT / "manifests/cohort.json").read_text())
    completed = set()
    for path in (ROOT / "runs").glob("*/summary.json"):
        record = json.loads(path.read_text())
        if record.get("experiment_id") == "development-v3" and record.get("repeat") == 2:
            manifest = json.loads((path.parent / "manifest.json").read_text())
            completed.add((manifest["task_id"], record["condition"]))
    for task in cohort["development"]:
        for condition in ["A", "B"]:
            if (task, condition) in completed:
                continue
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
                "2",
                "--experiment-id",
                "development-v3",
                "--key-file",
                args.key_file,
            ]
            if condition == "B":
                command += ["--lessons", "lessons/development-v1.md"]
            print(f"Development {task} {condition}2", flush=True)
            subprocess.run(command, cwd=ROOT, check=True)
