"""Compare fixed experiments without pooling denominators or altering outcomes."""

import argparse
import json
from collections import Counter
from pathlib import Path

from reproscout.experiment import verify_freeze
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", type=Path)
    parser.add_argument("--previous", type=Path, default=ROOT / "experiments/prepared-v2")
    args = parser.parse_args()
    verify_freeze(ROOT, args.experiment)
    current = json.loads((args.experiment / "results.json").read_text())
    previous = json.loads((args.previous / "results.json").read_text())
    assert not current["missing"] and len(current["runs"]) == 60
    calls = []
    checks = []
    rows = []
    for run in current["runs"]:
        directory = ROOT / "runs" / run["run_id"]
        budget = json.loads((directory / "budget.json").read_text())
        calls.extend(budget["calls"])
        checks.extend(budget.get("request_checks", []))
        p = directory / "source-audit.json"
        audit = json.loads(p.read_text()) if p.exists() else {}
        rows.append(
            {
                "run_id": run["run_id"],
                "task_id": run["task_id"],
                "cell": run["condition"] + str(run["repeat"]),
                "answer_solved": bool(run.get("evaluation", {}).get("solved")),
                "source_unchanged": audit.get("unchanged"),
                "answer_solved_and_source_unchanged": bool(run.get("evaluation", {}).get("solved"))
                and audit.get("unchanged") is True,
                "sample_error": run["sample_error"],
                "limit": run["limit"],
            }
        )
    by_cell = {}
    for cell in ["A1", "B1", "A2", "B2"]:
        group = [r for r in rows if r["cell"] == cell]
        by_cell[cell] = {
            "answer_solved": sum(r["answer_solved"] for r in group),
            "answer_solved_and_source_unchanged": sum(
                r["answer_solved_and_source_unchanged"] for r in group
            ),
            "attempts": len(group),
        }
    old_stops = sum(
        "Pilot context limit reached" in (r.get("sample_error") or "") for r in previous["runs"]
    )
    payload = {
        "experiment_id": current["experiment_id"],
        "previous_experiment_id": previous["experiment_id"],
        "previous_totals": previous["totals"],
        "current_totals": current["totals"],
        "previous_controller_stops": old_stops,
        "counted_context_stops": sum(c["status"] == "context_denied" for c in checks),
        "count_service_failures": sum(c["status"] == "count_failed" for c in checks),
        "cost_admission_denials": sum(c["status"] == "cost_denied" for c in checks),
        "model_calls": len(calls),
        "native_input_max": max((c["native_input_tokens"] for c in calls), default=0),
        "legacy_bound_crossings_admitted": sum(
            c.get("legacy_input_bound", 0) > 60000 for c in calls
        ),
        "calls_with_exact_native_input_usage_match": sum(
            c["native_input_tokens"]
            == c["usage"]["input_tokens"]
            + (c["usage"].get("input_tokens_cache_read") or 0)
            + (c["usage"].get("input_tokens_cache_write") or 0)
            for c in calls
        ),
        "all_calls_inside_counted_input_bound": all(
            c["usage"]["input_tokens"]
            + (c["usage"].get("input_tokens_cache_read") or 0)
            + (c["usage"].get("input_tokens_cache_write") or 0)
            <= c["input_token_bound"]
            for c in calls
        ),
        "zero_model_call_attempts": sum(r["model_calls"] == 0 for r in current["runs"]),
        "sample_errors": dict(Counter(r["sample_error"] for r in rows if r["sample_error"])),
        "cell_source_integrity": by_cell,
        "rows": rows,
        "interpretation": "Within-version B minus A compares frozen lessons. Across-version differences are descriptive before/after measurements on fifteen previously evaluated test tasks, not a randomized controller effect or unseen generalization claim.",
    }
    write_json(ROOT / "reports/controller-comparison.json", payload)
    lines = [
        "# Repaired controller comparison",
        "",
        payload["interpretation"],
        "",
        "| Cell | Previous answer-solved | Repaired answer-solved | Repaired solved with unchanged inputs |",
        "|---|---:|---:|---:|",
    ]
    for cell, value in by_cell.items():
        lines.append(
            f"| {cell} | {previous['totals'][cell]['solved']}/15 | {value['answer_solved']}/15 | {value['answer_solved_and_source_unchanged']}/15 |"
        )
    lines += [
        "",
        f"Historical controller stops: {old_stops}; repaired counted-context stops: {payload['counted_context_stops']}; native counting-service failures: {payload['count_service_failures']}.",
        f"Model generations: {len(calls)}; admitted requests above the historical byte bound: {payload['legacy_bound_crossings_admitted']}; maximum counted native input: {payload['native_input_max']} tokens.",
        f"Exact count/returned-input matches: {payload['calls_with_exact_native_input_usage_match']}/{len(calls)}. Every returned input stayed inside its counted bound: {payload['all_calls_inside_counted_input_bound']}.",
        "",
        "Answer correctness and unchanged-input audits are separate checks. Even their conjunction does not prove semantic fidelity. Source changes and failed startup attempts remain visible in the per-run report.",
        "",
        "See reports/controller-comparison.json for all per-run audit flags, failure messages, costs and wall times.",
    ]
    (ROOT / "docs/controller-comparison.md").write_text("\n".join(lines) + "\n")
    print(
        json.dumps(
            {
                k: v
                for k, v in payload.items()
                if k not in ["rows", "previous_totals", "current_totals"]
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
