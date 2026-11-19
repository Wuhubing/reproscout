"""Run the fixed public example as a repository integration test, never a job service."""

import json
import os
import subprocess
import time
from pathlib import Path

from reproscout.cli import execute
from reproscout.project_import import decode_bundle
from reproscout.web import Workspace, atomic

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "actions-evidence"
IMAGE = json.loads((ROOT / "deploy/images.example.json").read_text())[0]


def main():
    OUT.mkdir(exist_ok=True)
    record = {
        "purpose": "Fixed-example repository integration acceptance",
        "github_run_id": os.environ.get("GITHUB_RUN_ID"),
        "github_run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT"),
        "commit": os.environ.get("GITHUB_SHA"),
        "image": IMAGE,
        "status": "started",
    }
    started = time.monotonic()
    try:
        # One bounded pull; retain registry/DNS errors instead of disguising a setup failure.
        for name, command in [
            ("docker-version", ["docker", "version"]),
            ("compose-version", ["docker", "compose", "version"]),
            ("image-pull", ["docker", "pull", "--platform", "linux/amd64", IMAGE]),
        ]:
            phase = time.monotonic()
            result = subprocess.run(command, capture_output=True, text=True, timeout=420)
            (OUT / f"{name}.stdout.txt").write_text(result.stdout)
            (OUT / f"{name}.stderr.txt").write_text(result.stderr)
            record[name] = {"exit_code": result.returncode, "seconds": time.monotonic() - phase}
            if result.returncode:
                raise RuntimeError(f"{name} failed; inspect retained logs")
        bundle = (ROOT / "deliverables/sklearn-diabetes-ols-102.zip").read_bytes()
        manifest, _, _ = decode_bundle(bundle)
        workspace = Workspace(ROOT)
        imported = workspace.import_bundle(bundle)
        manifest_path = workspace.state / "projects" / (imported["id"] + ".json")
        config_path = OUT / "config.json"
        atomic(
            config_path,
            {
                "execution_policy": "author_only",
                "stop_on_offline_blocker": True,
                "max_model_calls": 10,
                "wall_time_seconds": 300,
                "model_budget_usd": 0.10,
            },
        )
        run = execute(ROOT, "run", None, manifest_path, config_path=config_path)
        record["run_id"] = run.name
        summary = json.loads((run / "summary.json").read_text())
        audit = json.loads((run / "source-audit.json").read_text())
        assessment = json.loads((run / "review-assessment.json").read_text())
        record.update(summary=summary, source_audit=audit, outcome=assessment["outcome"])
        # Use the already exported portable report whitelist; do not publish raw provider logs.
        workspace.sources = lambda: {run.name: run}
        (OUT / "report.zip").write_bytes(workspace.export(run.name))
        if summary.get("infrastructure_failure") or not audit.get("unchanged"):
            raise RuntimeError("Infrastructure or source-integrity gate failed")
        if assessment["outcome"] != "completed":
            raise RuntimeError("Execution did not complete")
        submission = json.loads((run / "submission.json").read_text())
        record["submission"] = submission
        record["status"] = "passed"
    except Exception as exc:
        record.update(status="failed", error=f"{type(exc).__name__}: {exc}")
        raise
    finally:
        record["total_seconds"] = time.monotonic() - started
        atomic(OUT / "acceptance.json", record)


if __name__ == "__main__":
    main()
