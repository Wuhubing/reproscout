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
    if experiment_id and experiment_id.endswith("v6"):
        config["controlled_execution"] = condition == "B"
        config["answer_types"] = json.loads((root / "configs/answer-types-v6.json").read_text())[
            "tasks"
        ][manifest["task_id"]]
    write_json(run / "config.json", config)
    budget = Budget(
        limit=config["model_budget_usd"],
        max_output=config["max_output_tokens"],
        max_input_tokens=config.get("max_input_tokens", 60000),
        framing_allowance=config.get("token_count_margin", 2048),
    )
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
    # Retries share the original cell budgets; failed attempts are never erased.
    prior = []
    if mode == "run" and experiment_id and experiment_id.endswith(("v4", "v5", "v6")):
        for previous in sorted((root / "runs").glob("*/summary.json")):
            old = json.loads(previous.read_text())
            if (old.get("experiment_id"), old.get("condition"), old.get("repeat")) != (
                experiment_id,
                condition,
                repeat,
            ):
                continue
            old_manifest = json.loads((previous.parent / "manifest.json").read_text())
            if old_manifest["task_id"] == manifest["task_id"]:
                prior.append(old)
        if any(not old.get("infrastructure_failure", False) for old in prior):
            raise ValueError("A scientific outcome already exists for this cell")
        budget.limit -= sum(old["cost_uncached_upper_usd"] for old in prior)
        config["max_model_calls"] -= sum(
            old["model_calls"] + old.get("unsettled_model_requests", 0) for old in prior
        )
        config["wall_time_seconds"] = int(
            config["wall_time_seconds"] - sum(old["seconds"] for old in prior)
        )
        if min(budget.limit, config["max_model_calls"], config["wall_time_seconds"]) <= 0:
            raise ValueError("Cell budget exhausted by retained infrastructure attempts")
        write_json(
            run / "retry-context.json",
            {
                "prior_attempts": [old["run_id"] for old in prior],
                "remaining_cost_upper_usd": budget.limit,
                "remaining_model_calls": config["max_model_calls"],
                "remaining_wall_seconds": config["wall_time_seconds"],
            },
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
        "unsettled_model_requests": int(budget.reserved > 0),
        "evaluation": {},
        "framework": importlib.metadata.version("inspect-ai"),
        "limitations": [
            "Pre-provisioned environment, not unchanged Medium",
            "Single-run report; see the frozen experiment for cohort comparisons",
            "Artifact validity is not semantic evidence verification",
        ],
    }
    network_path = run / "network-events.jsonl"
    events = (
        [json.loads(line) for line in network_path.read_text().splitlines()]
        if network_path.exists()
        else []
    )
    terminal_network = bool(events and events[-1]["status"] == "failed")
    startup_failure = (
        summary["status"] == "error"
        and not budget.calls
        and not (run / "source-audit.json").exists()
    )
    summary["infrastructure_failure"] = terminal_network or startup_failure
    summary["infrastructure_reason"] = (
        "terminal_network_failure"
        if terminal_network
        else "sandbox_startup_failure"
        if startup_failure
        else None
    )
    summary["attempt_number"] = len(prior) + 1
    summary["network_attempt_failures"] = sum(e["status"] == "failed" for e in events)
    if (run / "submission.json").exists():
        answers = json.loads((run / "submission.json").read_text())
        references = json.loads(
            (root / manifest.get("answers_path", "private/pilot_answers.json")).read_text()
        )
        summary["evaluation"] = score_answers(answers, references, manifest["questions"])
    if experiment_id and experiment_id.endswith("v6"):
        from .controlled import evaluate_run

        assessment = evaluate_run(run, config["answer_types"], config["controlled_execution"])
        assessment["answer_solved"] = bool(summary["evaluation"].get("solved"))
        assessment["answer_solved_with_verified_execution"] = (
            assessment["answer_solved"]
            and assessment["execution_fidelity"] == "verified_original_execution"
        )
        write_json(run / "fidelity-assessment.json", assessment)
        summary["fidelity"] = assessment
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
