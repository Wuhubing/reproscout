"""Compare frozen revisions and retain every outcome, request, and source exception."""

import json
from collections import Counter
from pathlib import Path

from summarize_recovery import metrics

from reproscout.experiment import verify_freeze
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    freeze = verify_freeze(ROOT, ROOT / "experiments/prepared-v5")
    r = json.loads((ROOT / "experiments/prepared-v5/results.json").read_text())
    assert r["scientific_matrix_complete"] and len(r["runs"]) == 60 and not r["missing"]
    versions = {}
    for name in ["prepared-v2", "prepared-v3", "prepared-v4", "prepared-v5"]:
        v = metrics(name)
        result = json.loads((ROOT / "experiments" / name / "results.json").read_text())
        attempts = result.get("all_attempts", result["runs"])
        if name == "prepared-v5":
            v["infrastructure_attempts"] = len(result["infrastructure_attempts"])
        v["max_model_call_stops"] = sum(
            "Maximum model calls reached" in (x.get("sample_error") or "") for x in attempts
        )
        versions[name] = v
    write_json(ROOT / "reports/controller-comparison.json", {"version_totals": versions})
    v = versions["prepared-v5"]
    groups = {}
    for c in ["A", "B"]:
        group = [x for x in r["runs"] if x["condition"] == c]
        categories = Counter()
        for x in group:
            if x.get("evaluation", {}).get("solved"):
                categories["answer_solved"] += 1
            elif "Maximum model calls reached" in (x.get("sample_error") or ""):
                categories["model_call_cap"] += 1
            elif x.get("sample_error"):
                categories["other_sample_error"] += 1
            else:
                categories["completed_without_passing_score"] += 1
        groups[c] = {
            "outcomes": dict(categories),
            "model_calls": sum(x["model_calls"] for x in group),
            "seconds": sum(x["seconds"] for x in group),
            "estimated_cost_usd": sum(x["cost_estimated_usd"] for x in group),
        }
    write_json(ROOT / "reports/lessons-breakdown-v5.json", groups)
    keyed = {(x["task_id"], x["condition"], x["repeat"]): x for x in r["runs"]}
    pairs = []
    for task in freeze["cohort"]["heldout"]:
        for repeat in [1, 2]:
            a, b = keyed[task, "A", repeat], keyed[task, "B", repeat]
            pairs.append(
                {
                    "task_id": task,
                    "repeat": repeat,
                    "A_solved": bool(a.get("evaluation", {}).get("solved")),
                    "B_solved": bool(b.get("evaluation", {}).get("solved")),
                    "A_run_id": a["run_id"],
                    "B_run_id": b["run_id"],
                }
            )
    paired = {
        "A_only": sum(p["A_solved"] and not p["B_solved"] for p in pairs),
        "B_only": sum(p["B_solved"] and not p["A_solved"] for p in pairs),
        "both_solved": sum(p["A_solved"] and p["B_solved"] for p in pairs),
        "neither_solved": sum(not p["A_solved"] and not p["B_solved"] for p in pairs),
        "pairs": pairs,
    }
    write_json(ROOT / "reports/paired-outcomes-v5.json", paired)
    old = json.loads((ROOT / "reports/paired-outcomes-v4.json").read_text())["pairs"]
    transitions = [
        {
            "v4": p,
            "v5": next(
                q for q in pairs if (q["task_id"], q["repeat"]) == (p["task_id"], p["repeat"])
            ),
        }
        for p in old
        if p["A_solved"] and not p["B_solved"]
    ]
    write_json(ROOT / "reports/adverse-pair-transitions-v5.json", transitions)
    exceptions, events = [], []
    for x in r["all_attempts"]:
        folder = ROOT / "runs" / x["run_id"]
        p = folder / "source-audit.json"
        audit = json.loads(p.read_text()) if p.exists() else {}
        if audit.get("unchanged") is not True:
            exceptions.append(
                {
                    "run_id": x["run_id"],
                    "audit": audit,
                    "infrastructure_failure": x["infrastructure_failure"],
                }
            )
        p = folder / "network-events.jsonl"
        if p.exists():
            events += [
                {"scope": "attempt", "run_id": x["run_id"], **json.loads(line)}
                for line in p.read_text().splitlines()
            ]
    for p in sorted((ROOT / "experiments/prepared-v5/preflights").glob("*/network-events.jsonl")):
        events += [
            {"scope": "preflight", "id": p.parent.name, **json.loads(line)}
            for line in p.read_text().splitlines()
        ]
    write_json(ROOT / "reports/source-integrity-v5.json", {"non_unchanged_audits": exceptions})
    write_json(
        ROOT / "reports/network-audit-v5.json",
        {
            "operations": len(events),
            "failed_operations": [e for e in events if e["status"] == "failed"],
            "scope": "Application requests, not individual TCP connection attempts.",
            "all_events": events,
        },
    )

    def line(label, fn):
        return "| " + label + " | " + " | ".join(str(fn(x)) for x in versions.values()) + " |"

    rows = ["| Metric | v2 | v3 | v4 | v5 |", "|---|---:|---:|---:|---:|"]
    rows += [
        line("Retained attempts", lambda x: x["attempts"]),
        line(
            "Answer-solved / 60",
            lambda x: f"{x['answer_solved']}/60 ({x['answer_solved'] / 60:.1%})",
        ),
        line(
            "A solved / 30",
            lambda x: f"{x['totals']['A1']['solved'] + x['totals']['A2']['solved']}/30",
        ),
        line(
            "B solved / 30",
            lambda x: f"{x['totals']['B1']['solved'] + x['totals']['B2']['solved']}/30",
        ),
        line(
            "Original-input hashes unchanged / changed / missing",
            lambda x: " / ".join(
                str(x["source_audits"].get(k, 0)) for k in ["unchanged", "changed", "missing"]
            ),
        ),
        line(
            "Answer solved with original hashes unchanged",
            lambda x: x["answer_solved_and_source_unchanged"],
        ),
        line("Old byte-bound stops", lambda x: x["legacy_context_stops"]),
        line("Native context stops", lambda x: x["native_context_stops"]),
        line("20-call stops", lambda x: x["max_model_call_stops"]),
        line("Terminal count failures", lambda x: x["terminal_count_failures"]),
        line("Infrastructure attempts", lambda x: x["infrastructure_attempts"]),
        line("Model generations", lambda x: x["model_calls"]),
        line(
            "Sample time, minutes (all attempts)",
            lambda x: f"{x['recorded_sample_seconds_sum'] / 60:.2f}",
        ),
        line("Calendar interval, minutes", lambda x: f"{x['calendar_interval_seconds'] / 60:.2f}"),
        line(
            "Estimated model cost (all attempts)", lambda x: f"${x['estimated_model_cost_usd']:.5f}"
        ),
        line("Uncached cost upper bound", lambda x: f"${x['uncached_cost_upper_usd']:.5f}"),
    ]
    text = "# Controller, network, and lesson revision comparison\n\n"
    text += "V5 completed sixty scientific cells under one unchanged freeze. Infrastructure attempts are separately retained and cannot satisfy a cell. Scientific failures are final.\n\n"
    text += "\n".join(rows) + "\n\n"
    text += "V3 is infrastructure-invalid: its low cost and success rate reflect DNS aborts, not an informative scientific comparison. V4 repaired transport and request accounting; v5 revises only the B lesson treatment, with the same base prompt, scientific tools, model, scorer, inputs and limits. The shared retry guard now recognizes v5 IDs. Cross-version results also include sampling and time effects.\n\n"
    text += f"V5 A solved {groups['A']['outcomes'].get('answer_solved', 0)}/30 and B {groups['B']['outcomes'].get('answer_solved', 0)}/30. Within v5, A-only pairs: {paired['A_only']}; B-only: {paired['B_only']}; both solved: {paired['both_solved']}; neither: {paired['neither_solved']}. Thirty paired observations reuse fifteen tasks. No significance claim applies.\n\n"
    text += f"All {v['model_calls']} generations are retained; native counts matched usage on {v['native_counts_matching_usage']}. Application operations including preflights: {len(events)}; failed operations: {sum(e['status'] == 'failed' for e in events)}. These are application logs, not TCP packet traces.\n\n"
    text += "## Four previously adverse pairs\n\n| Task | Repeat | v4 A / B | v5 A / B | v5 B evidence |\n|---|---:|---|---|---|\n"
    for p in transitions:
        a, b = p["v4"], p["v5"]
        text += f"| {a['task_id']} | {a['repeat']} | {a['A_solved']} / {a['B_solved']} | {b['A_solved']} / {b['B_solved']} | [Run](../reports/runs/{b['B_run_id']}/report.html) |\n"
    text += "\n## Fidelity and interpretation\n\nThe original-input hash audit does not detect modifications to newly created scientific copies, nor prove semantic support. The v4 adverse-pair analysis identifies such a case even among answer-solved runs. Do not label the hash-and-answer intersection as fully faithful reproduction. Source exceptions and supplemental trajectory review remain separate from the unchanged scorer.\n\n"
    text += "This revision was informed by exposed test trajectories and validated on five training tasks. It is a test-informed regression study, not a new held-out generalization test. Formatting counterfactuals in the old analysis do not alter historical scores. All failures remain visible.\n\n"
    text += "Costs use returned token usage and conservative reservations, exclude development/host/image costs, and are not invoices. Sample time includes in-task execution; calendar time also includes preflights, cooldowns and scheduling.\n\n"
    text += "## Evidence\n\n- [Four-pair diagnosis](lesson-pair-analysis-v4.md)\n- [Revision protocol](lesson-revision-protocol.md)\n- [Development validation](../reports/development-v5-validation.json)\n- [Full metrics](../reports/controller-comparison.json)\n- [All outcomes](results.md)\n- [Portable app](../reports/index.html)\n- [Source exceptions](../reports/source-integrity-v5.json)\n- [Application request ledger](../reports/network-audit-v5.json)\n- [Archived v4 interpretation](../reports/archive-v4/controller-comparison.md)\n"
    (ROOT / "docs/controller-comparison.md").write_text(text)
    print(
        json.dumps(
            {
                "groups": groups,
                "paired": {k: v for k, v in paired.items() if k != "pairs"},
                "attempts": len(r["all_attempts"]),
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
