"""Run missing planned cells with freeze verification and no silent reruns."""

import argparse
import asyncio
import json
import subprocess
import sys
import time
from pathlib import Path

from validate_network import probe

from reproscout.cli import load_key
from reproscout.experiment import aggregate, verify_freeze

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", type=Path)
    parser.add_argument("--key-file", type=Path, required=True)
    args = parser.parse_args()
    payload = verify_freeze(ROOT, args.experiment)
    completed = set()
    for path in (ROOT / "runs").glob("*/summary.json"):
        record = json.loads(path.read_text())
        if record.get("experiment_id") == payload["experiment_id"]:
            task = json.loads((path.parent / "manifest.json").read_text())["task_id"]
            if not payload.get("infrastructure_retry_policy") or not record.get(
                "infrastructure_failure"
            ):
                completed.add((task, record["condition"], record["repeat"]))
    # Reverse A/B order across repetitions; serial execution avoids resource interference.
    for repeat in [1, 2]:
        for task in payload["cohort"]["heldout"]:
            for condition in ["A", "B"] if repeat == 1 else ["B", "A"]:
                verify_freeze(ROOT, args.experiment)
                if (task, condition, repeat) in completed:
                    continue
                command = [
                    sys.executable,
                    "-m",
                    "reproscout",
                    "run",
                    "--manifest",
                    str(ROOT / "manifests" / f"{task}.json"),
                    "--condition",
                    condition,
                    "--repeat",
                    str(repeat),
                    "--experiment-id",
                    payload["experiment_id"],
                    "--key-file",
                    str(args.key_file),
                ]
                if condition == "B":
                    command.extend(["--lessons", str(args.experiment / "lessons.md")])
                policy = payload.get("infrastructure_retry_policy")
                while True:
                    if policy:
                        current = aggregate(ROOT, args.experiment)
                        attempts = [
                            r
                            for r in current["all_attempts"]
                            if (r["task_id"], r["condition"], r["repeat"])
                            == (task, condition, repeat)
                        ]
                        if len(attempts) >= policy["max_cell_attempts"]:
                            raise RuntimeError(
                                "Infrastructure retry limit reached; matrix remains incomplete"
                            )
                        load_key(args.key_file)
                        # The exact counting path must work before launching a scientific cell.
                        asyncio.run(probe(2, args.experiment / "preflights" / str(time.time_ns())))
                    print(f"Running {task} {condition}{repeat}", flush=True)
                    result = subprocess.run(command, cwd=ROOT, check=False)
                    if result.returncode:
                        raise RuntimeError(
                            "Runner process failed; retain evidence and inspect before resuming"
                        )
                    current = aggregate(ROOT, args.experiment)
                    if [task, condition, repeat] not in current["missing"]:
                        break
                    if not policy:
                        break
                    print(
                        "Infrastructure failure retained; cooling down before bounded cell retry",
                        flush=True,
                    )
                    time.sleep(policy["cell_retry_delay_seconds"])
    result = aggregate(ROOT, args.experiment)
    print(json.dumps(result["totals"], indent=2))


if __name__ == "__main__":
    main()
