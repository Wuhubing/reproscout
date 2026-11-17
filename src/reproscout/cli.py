"""ReproScout command line entry point."""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

from .tasks import digest, prepare, write_json


def load_key(path: Path | None) -> None:
    if path:
        matches = re.findall(r"sk-[A-Za-z0-9_-]+", path.read_text(encoding="utf-8"))
        if len(matches) != 1:
            raise ValueError("Credential file must contain exactly one API key")
        os.environ["OPENAI_API_KEY"] = matches[0]
    if not os.environ.get("OPENAI_API_KEY"):
        raise ValueError("Supply --key-file or set OPENAI_API_KEY")


def execute(
    root: Path,
    mode: str,
    key_file: Path | None,
    manifest_path: Path | None = None,
    condition: str = "A",
    lessons_path: Path | None = None,
    repeat: int = 1,
    experiment_id: str | None = None,
) -> Path:
    from inspect_ai import Task, eval
    from inspect_ai.dataset import Sample
    from inspect_ai.model import GenerateConfig, ModelCost, set_model_cost

    from .agent import build_agent
    from .budget import Budget
    from .diagnosis import diagnose
    from .reporting import report
    from .sandbox import SETUP, compose_file
    from .scoring import score_answers
    from .validation import environment_checks, source_audit

    manifest = json.loads((manifest_path or root / "manifests/pilot.json").read_text())
    config = json.loads((root / "configs/pilot.json").read_text())
    prepared = root / manifest.get("prepared_path", "data/prepared.tar")
    if digest(prepared.read_bytes()) != manifest["prepared_sha256"]:
        raise ValueError("Prepared input checksum changed; refusing to run")
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    run = root / "runs" / f"{stamp}-{manifest['task_id']}-{mode}-{condition}{repeat}"
    run.mkdir(parents=True)
    write_json(run / "manifest.json", manifest)
    write_json(run / "config.json", config)
    config.update(condition=condition, repeat=repeat, experiment_id=experiment_id)
    write_json(run / "config.json", config)
    budget = Budget(limit=config["model_budget_usd"], max_output=config["max_output_tokens"])
    question_text = json.dumps(manifest["questions"], indent=2)
    sample = Sample(
        id=manifest["task_id"],
        input=manifest["task_prompt"] + "\nQuestions:\n" + question_text,
        files={
            "/tmp/reproscout-input.tar": str(
                root / manifest.get("prepared_path", "data/prepared.tar")
            )
        },
        setup=SETUP,
    )
    started = time.monotonic()
    if mode == "run":
        load_key(key_file)
        lessons = ""
        if condition == "B":
            if lessons_path is None:
                raise ValueError("Condition B requires a frozen lessons file")
            lessons = "\nFrozen development lessons:\n" + lessons_path.read_text()
            (run / "lessons.md").write_text(lessons_path.read_text(), encoding="utf-8")
        solver = build_agent(run, manifest, config, budget, lessons)
        model = config["model"]
        set_model_cost(
            model, ModelCost(input=0.75, output=4.5, input_cache_read=0.075, input_cache_write=0.75)
        )
    else:
        solver = environment_checks(run, manual=True)
        model = "mockllm/model"
    task = Task(
        name="reproscout_pilot",
        dataset=[sample],
        solver=solver,
        cleanup=source_audit(run, manifest),
        sandbox=("docker", str(compose_file(run, manifest["image"]))),
        time_limit=config["wall_time_seconds"],
        message_limit=80,
        cost_limit=config["model_budget_usd"] if mode == "run" else None,
        config=GenerateConfig(
            max_tokens=config["max_output_tokens"],
            max_retries=0,
            parallel_tool_calls=False,
            reasoning_effort=config["reasoning_effort"],
        ),
    )
    logs = eval(
        task,
        model=model,
        log_dir=str(run / "logs"),
        display="plain",
        max_samples=1,
        max_tasks=1,
        fail_on_error=False,
    )
    summary = {
        "run_id": run.name,
        "mode": mode,
        "split": manifest["split"],
        "condition": condition,
        "repeat": repeat,
        "experiment_id": experiment_id,
        "status": ("error" if logs[0].samples and logs[0].samples[0].error else logs[0].status),
        "sample_error": (
            logs[0].samples[0].error.message
            if logs[0].samples and logs[0].samples[0].error
            else None
        ),
        "limit": (
            logs[0].samples[0].limit.model_dump()
            if logs[0].samples and logs[0].samples[0].limit
            else None
        ),
        "seconds": time.monotonic() - started,
        "model": model,
        "cost_estimated_usd": budget.estimated_billed,
        "cost_uncached_upper_usd": budget.spent_upper,
        "model_calls": len(budget.calls),
        "evaluation": {},
        "framework": importlib.metadata.version("inspect-ai"),
        "limitations": [
            "Pre-provisioned environment, not unchanged Medium",
            "No held-out comparison yet",
            "Artifact validity is not semantic evidence verification",
        ],
    }
    if (run / "submission.json").exists():
        answers = json.loads((run / "submission.json").read_text())
        references = json.loads(
            (root / manifest.get("answers_path", "private/pilot_answers.json")).read_text()
        )
        summary["evaluation"] = score_answers(answers, references, manifest["questions"])
    write_json(run / "budget.json", budget.__dict__)
    write_json(run / "summary.json", summary)
    diagnose(run)
    report(run)
    print(json.dumps(summary, indent=2))
    print(f"Report: {run / 'report.html'}")
    return run


def main() -> None:
    parser = argparse.ArgumentParser(description="Evidence-linked scientific reproduction")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("doctor")
    sub.add_parser("prepare")
    sub.add_parser("validate")
    run = sub.add_parser("run")
    run.add_argument("--key-file", type=Path)
    run.add_argument("--manifest", type=Path)
    run.add_argument("--condition", choices=["A", "B"], default="A")
    run.add_argument("--lessons", type=Path)
    run.add_argument("--repeat", type=int, default=1)
    run.add_argument("--experiment-id")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.command == "doctor":
        data = {
            "python": platform.python_version(),
            "host_arch": platform.machine(),
            "inspect_ai": importlib.metadata.version("inspect-ai"),
        }
        for name, command in {
            "docker": ["docker", "info", "--format", "{{.ServerVersion}} {{.Architecture}}"],
            "compose": ["docker", "compose", "version"],
        }.items():
            p = subprocess.run(command, capture_output=True, text=True, check=False)
            data[name] = {"ok": p.returncode == 0, "stdout": p.stdout.strip()}
        print(json.dumps(data, indent=2))
    elif args.command == "prepare":
        print(f"Prepared {prepare(root)['task_id']} from official training data.")
    else:
        execute(
            root,
            "run" if args.command == "run" else "validate",
            getattr(args, "key_file", None),
            getattr(args, "manifest", None),
            getattr(args, "condition", "A"),
            getattr(args, "lessons", None),
            getattr(args, "repeat", 1),
            getattr(args, "experiment_id", None),
        )
