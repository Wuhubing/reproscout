"""Apply the predefined development gate and write auditable validation evidence."""

import json
from pathlib import Path

from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    cohort = json.loads((ROOT / "manifests/cohort.json").read_text())
    expected = {(task, condition) for task in cohort["development"] for condition in ["A", "B"]}
    rows = []
    startup = []
    records = []
    for path in sorted((ROOT / "runs").glob("*/summary.json")):
        summary = json.loads(path.read_text())
        if summary.get("experiment_id") != "development-v3":
            continue
        records.append(summary["run_id"])
        if summary.get("repeat") != 2:
            startup.append(summary)
            continue
        manifest = json.loads((path.parent / "manifest.json").read_text())
        budget = json.loads((path.parent / "budget.json").read_text())
        checks = budget["request_checks"]
        calls = budget["calls"]
        audit_path = path.parent / "source-audit.json"
        audit = json.loads(audit_path.read_text()) if audit_path.exists() else {}
        rows.append(
            {
                "run_id": summary["run_id"],
                "task_id": manifest["task_id"],
                "condition": summary["condition"],
                "status": summary["status"],
                "sample_error": summary["sample_error"],
                "solved": bool(summary.get("evaluation", {}).get("solved")),
                "model_calls": len(calls),
                "cost_estimated_usd": summary["cost_estimated_usd"],
                "source_unchanged": audit.get("unchanged"),
                "counted_requests": len(checks),
                "failed_counts_or_context_denials": sum(
                    c["status"] in ["count_failed", "context_denied"] for c in checks
                ),
                "legacy_bound_crossings_admitted": sum(
                    c.get("legacy_input_bound", 0) > 60000 for c in calls
                ),
                "native_max_input_tokens": max(
                    (c["native_input_tokens"] for c in calls), default=0
                ),
                "all_actual_input_counts_match": all(
                    c["native_input_tokens"]
                    == c["usage"]["input_tokens"]
                    + (c["usage"].get("input_tokens_cache_read") or 0)
                    + (c["usage"].get("input_tokens_cache_write") or 0)
                    for c in calls
                ),
                "actual_usage_inside_reserved_bound": all(
                    c["usage"]["input_tokens"]
                    + (c["usage"].get("input_tokens_cache_read") or 0)
                    + (c["usage"].get("input_tokens_cache_write") or 0)
                    <= c["input_token_bound"]
                    for c in calls
                ),
            }
        )
    assert len(rows) == 10 and {(r["task_id"], r["condition"]) for r in rows} == expected, (
        "Complete the fixed development matrix first"
    )
    assert all(
        r["model_calls"] > 0
        and not r["failed_counts_or_context_denials"]
        and r["actual_usage_inside_reserved_bound"]
        for r in rows
    )
    assert sum(r["legacy_bound_crossings_admitted"] for r in rows) > 0
    env_run = ROOT / "runs/20261117T223433045169Z-capsule-6460826-validate-A1"
    env = json.loads((env_run / "environment-checks.json").read_text())
    assert len(env) == 13 and all(v["passed"] for v in env.values())
    write_json(
        ROOT / "reports/development-v3-validation.json",
        {
            "passed": True,
            "gate_scope": "Native request accounting only; answer correctness and source integrity are reported separately.",
            "source_integrity_failures": [
                r["run_id"] for r in rows if r["source_unchanged"] is not True
            ],
            "experiment_id": "development-v3",
            "matrix_records": len(rows),
            "all_development_run_ids": records,
            "retained_preflight_failures": startup,
            "environment_check_run": env_run.name,
            "environment_checks": env,
            "software_tests": 22,
            "rows": rows,
            "notes": "Development acceptance validates controller operation, not universal task success. All formal tasks remain unrun under the repaired controller until the new freeze.",
        },
    )
    print(
        "Development controller gate passed: ten A/B records, old-bound crossings, native usage checks, 13 environment checks"
    )


if __name__ == "__main__":
    main()
