"""Report scoring, fidelity instrumentation, abstention and costs independently."""

import json
from collections import Counter
from pathlib import Path

from summarize_recovery import metrics

from reproscout.experiment import verify_freeze
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    freeze = verify_freeze(ROOT, ROOT / "experiments/prepared-v6")
    result = json.loads((ROOT / "experiments/prepared-v6/results.json").read_text())
    assert result["scientific_matrix_complete"] and len(result["runs"]) == 60
    versions = {}
    for name in ["prepared-v2", "prepared-v3", "prepared-v4", "prepared-v5", "prepared-v6"]:
        v = metrics(name)
        r = json.loads((ROOT / "experiments" / name / "results.json").read_text())
        attempts = r.get("all_attempts", r["runs"])
        if "infrastructure_attempts" in r:
            v["infrastructure_attempts"] = len(r["infrastructure_attempts"])
        v["max_model_call_stops"] = sum(
            "Maximum model calls reached" in (x.get("sample_error") or "") for x in attempts
        )
        versions[name] = v
    write_json(ROOT / "reports/controller-comparison.json", {"version_totals": versions})
    groups = {}
    events = []
    rejections = []
    for x in result["all_attempts"]:
        d = ROOT / "runs" / x["run_id"]
        p = d / "network-events.jsonl"
        if p.exists():
            events.extend(
                {"scope": "attempt", "run_id": x["run_id"], **json.loads(line)}
                for line in p.read_text().splitlines()
            )
        p = d / "execution-ledger.json"
        if p.exists():
            rejections.extend(
                {"run_id": x["run_id"], **e}
                for e in json.loads(p.read_text())
                if e["status"] == "refused"
            )
    for p in (ROOT / "experiments/prepared-v6/preflights").glob("*/network-events.jsonl"):
        events.extend(
            {"scope": "preflight", "id": p.parent.name, **json.loads(line)}
            for line in p.read_text().splitlines()
        )
    for c in ["A", "B"]:
        rows = [x for x in result["runs"] if x["condition"] == c]
        f = [x["fidelity"] for x in rows]
        groups[c] = {
            "runs": 30,
            "answer_solved": sum(bool(x["evaluation"].get("solved")) for x in rows),
            "execution_fidelity": dict(Counter(x["execution_fidelity"] for x in f)),
            "typed_submissions": sum(x["answer_types_compliant"] is True for x in f),
            "type_noncompliant_submissions": sum(x["answer_types_compliant"] is False for x in f),
            "missing_submissions": sum(x["answer_types_compliant"] is None for x in f),
            "null_answers": sum(x["null_answers"] or 0 for x in f),
            "runs_with_nulls": sum(bool(x["null_answers"]) for x in f),
            "solved_and_verified_execution": sum(
                x["answer_solved_with_verified_execution"] for x in f
            ),
            "call_cap_failures": sum(
                "Maximum model calls reached" in (x.get("sample_error") or "") for x in rows
            ),
            "model_calls": sum(x["model_calls"] for x in rows),
            "sample_seconds": sum(x["seconds"] for x in rows),
            "estimated_cost_usd": sum(x["cost_estimated_usd"] for x in rows),
        }
    write_json(
        ROOT / "reports/fidelity-outcomes-v6.json",
        {
            "groups": groups,
            "runs": result["runs"],
            "scope": "Mechanical execution boundary and provenance only; A unverified is not measured zero fidelity. Semantic support requires separate review.",
            "rejected_operations": rejections,
        },
    )
    write_json(
        ROOT / "reports/network-audit-v6.json",
        {
            "operations": len(events),
            "failed_operations": [e for e in events if e["status"] == "failed"],
            "all_events": events,
        },
    )
    pairs = []
    for task in freeze["cohort"]["heldout"]:
        for repeat in [1, 2]:
            pair = {"task_id": task, "repeat": repeat}
            for c in ["A", "B"]:
                row = next(
                    x
                    for x in result["runs"]
                    if (x["task_id"], x["repeat"], x["condition"]) == (task, repeat, c)
                )
                pair[c + "_solved"] = bool(row["evaluation"].get("solved"))
                pair[c + "_run_id"] = row["run_id"]
            pairs.append(pair)
    write_json(
        ROOT / "reports/paired-outcomes-v6.json",
        {
            "pairs": pairs,
            "A_only": sum(p["A_solved"] and not p["B_solved"] for p in pairs),
            "B_only": sum(p["B_solved"] and not p["A_solved"] for p in pairs),
        },
    )

    def line(label, fn):
        return "| " + label + " | " + " | ".join(str(fn(v)) for v in versions.values()) + " |"

    table = [
        "| Metric | v2 | v3 | v4 | v5 | v6 |",
        "|---|---:|---:|---:|---:|---:|",
        line("Answer solved / 60", lambda v: v["answer_solved"]),
        line("A solved / 30", lambda v: v["totals"]["A1"]["solved"] + v["totals"]["A2"]["solved"]),
        line("B solved / 30", lambda v: v["totals"]["B1"]["solved"] + v["totals"]["B2"]["solved"]),
        line("Retained attempts", lambda v: v["attempts"]),
        line("Infrastructure failures", lambda v: v["infrastructure_attempts"]),
        line(
            "Original hashes unchanged / changed / missing",
            lambda v: " / ".join(
                str(v["source_audits"].get(k, 0)) for k in ["unchanged", "changed", "missing"]
            ),
        ),
        line("Old byte-bound stops", lambda v: v["legacy_context_stops"]),
        line("Native-count failures", lambda v: v["terminal_count_failures"]),
        line("20-call stops", lambda v: v["max_model_call_stops"]),
        line("Generations", lambda v: v["model_calls"]),
        line("Sample minutes", lambda v: round(v["recorded_sample_seconds_sum"] / 60, 2)),
        line("Calendar minutes", lambda v: round(v["calendar_interval_seconds"] / 60, 2)),
        line("Estimated model cost USD", lambda v: round(v["estimated_model_cost_usd"], 5)),
    ]
    text = (
        "# V6: scoring and controlled scientific execution\n\nAll sixty scientific cells completed under one unchanged freeze. V3 remains infrastructure-invalid; its score/time are not scientific or efficiency evidence. V6 changes B tools and submission enforcement, not only lesson text. A retains the original unrestricted baseline.\n\n"
        + "\n".join(table)
        + "\n\n"
    )
    text += "## Separate outcomes\n\n| Outcome | A | B |\n|---|---:|---:|\n"
    for field in [
        "answer_solved",
        "typed_submissions",
        "type_noncompliant_submissions",
        "missing_submissions",
        "null_answers",
        "runs_with_nulls",
        "solved_and_verified_execution",
        "call_cap_failures",
        "model_calls",
        "sample_seconds",
        "estimated_cost_usd",
    ]:
        text += f"| {field} | {groups['A'][field]} | {groups['B'][field]} |\n"
    text += (
        "\nExecution fidelity statuses: A `"
        + str(groups["A"]["execution_fidelity"])
        + "`; B `"
        + str(groups["B"]["execution_fidelity"])
        + "`.\n\n"
    )
    text += "**Do not interpret A unverified as a zero faithful-reproduction rate.** A has unrestricted commands and lacks B's execution ledger. Verified execution means original-file dispatch, input integrity and current-output provenance; it does not prove complete experimental coverage or semantic support. A correct answer, a typed answer, an intact source file and a faithful explanation are distinct properties. Nulls are retained failures, not improved accuracy.\n\n"
    text += f"All {len(result['all_attempts'])} attempts remain available. Application operations including preflights: {len(events)}, failed: {sum(e['status'] == 'failed' for e in events)}. Native input counts match on {versions['prepared-v6']['native_counts_matching_usage']}/{versions['prepared-v6']['model_calls']} generations. Rejected controlled operations/submissions: {len(rejections)}. Costs exclude host, image and development work and are usage estimates, not invoices.\n\n"
    text += "## Interpretation and evidence\n\nThis is a test-informed regression study on fifteen exposed tasks, each repeated twice. No fresh held-out generalization or significance claim applies. Cross-version A movement reflects different trajectories and sampling/time effects, not a treatment delivered to A. See the six-regression/one-gain analysis. Scientific failures are final; infrastructure attempts never satisfy a cell.\n\n- [A decline analysis](baseline-decline-v5.md)\n- [Frozen fidelity protocol](fidelity-protocol-v6.md)\n- [Development gate](../reports/development-v6-validation.json)\n- [All fidelity outcomes](../reports/fidelity-outcomes-v6.json)\n- [Complete results](results.md)\n- [Evidence app](../reports/index.html)\n- [Previous v5 report](../reports/archive-v5/controller-comparison.md)\n"
    (ROOT / "docs/controller-comparison.md").write_text(text)
    print(json.dumps(groups, indent=2))


if __name__ == "__main__":
    main()
