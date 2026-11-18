"""Compare all controller versions, keeping infrastructure attempts visible."""

import json
from collections import Counter
from datetime import datetime
from pathlib import Path

from inspect_ai.log import read_eval_log

from reproscout.experiment import verify_freeze
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def metrics(experiment):
    result = json.loads((ROOT / "experiments" / experiment / "results.json").read_text())
    outcomes = result["runs"]
    attempts = result.get("all_attempts", outcomes)
    audits = Counter()
    context = 0
    count_failures = 0
    matched = 0
    crossings = 0
    network_failures = []
    starts, ends = [], []
    faithful = 0
    for r in attempts:
        folder = ROOT / "runs" / r["run_id"]
        p = folder / "source-audit.json"
        audit = json.loads(p.read_text()) if p.exists() else {}
        audits[
            "unchanged"
            if audit.get("unchanged") is True
            else "changed"
            if audit.get("unchanged") is False
            else "missing"
        ] += 1
        faithful += bool(r.get("evaluation", {}).get("solved")) and audit.get("unchanged") is True
        budget = json.loads((folder / "budget.json").read_text())
        context += sum(c["status"] == "context_denied" for c in budget.get("request_checks", []))
        count_failures += sum(
            c["status"] == "count_failed" for c in budget.get("request_checks", [])
        )
        for c in budget["calls"]:
            if "native_input_tokens" in c:
                usage = c["usage"]
                matched += c["native_input_tokens"] == usage["input_tokens"] + (
                    usage.get("input_tokens_cache_read") or 0
                ) + (usage.get("input_tokens_cache_write") or 0)
                crossings += c.get("legacy_input_bound", 0) > 60000
        events = folder / "network-events.jsonl"
        if events.exists():
            network_failures.extend(
                {"run_id": r["run_id"], **json.loads(line)}
                for line in events.read_text().splitlines()
                if json.loads(line)["status"] == "failed"
            )
        for log in (folder / "logs").glob("*.eval"):
            stats = read_eval_log(str(log), header_only=True).stats
            if stats.started_at:
                starts.append(datetime.fromisoformat(stats.started_at))
            if stats.completed_at:
                ends.append(datetime.fromisoformat(stats.completed_at))
    return {
        "experiment_id": experiment,
        "attempts": len(attempts),
        "selected_outcomes": len(outcomes),
        "scientific_matrix_complete": result.get("scientific_matrix_complete", False),
        "answer_solved": sum(bool(r.get("evaluation", {}).get("solved")) for r in outcomes),
        "all_attempt_answer_solved": sum(
            bool(r.get("evaluation", {}).get("solved")) for r in attempts
        ),
        "answer_solved_and_source_unchanged": faithful,
        "source_audits": dict(audits),
        "legacy_context_stops": sum(
            "Pilot context limit reached" in (r.get("sample_error") or "") for r in attempts
        ),
        "native_context_stops": context,
        "terminal_count_failures": count_failures,
        "infrastructure_attempts": len(result.get("infrastructure_attempts", []))
        if experiment == "prepared-v4"
        else (59 if experiment == "prepared-v3" else 1),
        "historical_dns_failures": 59 if experiment == "prepared-v3" else 0,
        "request_retry_failures": network_failures,
        "zero_model_call_attempts": sum(r["model_calls"] == 0 for r in attempts),
        "model_calls": sum(r["model_calls"] for r in attempts),
        "native_counts_matching_usage": matched,
        "old_byte_bound_crossings": crossings,
        "estimated_model_cost_usd": sum(r["cost_estimated_usd"] for r in attempts),
        "uncached_cost_upper_usd": sum(r["cost_uncached_upper_usd"] for r in attempts),
        "recorded_sample_seconds_sum": sum(r["seconds"] for r in attempts),
        "calendar_interval_seconds": (max(ends) - min(starts)).total_seconds(),
        "first_inspect_started_at": min(starts).isoformat(),
        "last_inspect_completed_at": max(ends).isoformat(),
        "totals": result["totals"],
        "missing": result["missing"],
    }


def main():
    verify_freeze(ROOT, ROOT / "experiments/prepared-v4")
    versions = {v: metrics(v) for v in ["prepared-v2", "prepared-v3", "prepared-v4"]}
    current = versions["prepared-v4"]
    assert (
        current["scientific_matrix_complete"]
        and current["selected_outcomes"] == 60
        and not current["missing"]
    )
    write_json(
        ROOT / "reports/controller-comparison.json",
        {
            "version_totals": versions,
            "interpretation": "Descriptive repair study on fifteen previously evaluated tasks. v3 is infrastructure-invalid, not a completed scientific comparison.",
        },
    )

    def line(label, fn):
        return "| " + label + " | " + " | ".join(str(fn(v)) for v in versions.values()) + " |"

    table = ["| Metric | v2 | v3 | v4 |", "|---|---:|---:|---:|"]
    table += [
        line("Retained attempts", lambda v: v["attempts"]),
        line(
            "Answer-solved / 60 planned cells",
            lambda v: f"{v['answer_solved']}/60 ({v['answer_solved'] / 60:.1%})",
        ),
        line(
            "A solved / 30",
            lambda v: f"{v['totals']['A1']['solved'] + v['totals']['A2']['solved']}/30",
        ),
        line(
            "B solved / 30",
            lambda v: f"{v['totals']['B1']['solved'] + v['totals']['B2']['solved']}/30",
        ),
        line(
            "Solved with unchanged prepared inputs",
            lambda v: v["answer_solved_and_source_unchanged"],
        ),
        line("Legacy byte-bound stops", lambda v: v["legacy_context_stops"]),
        line("Native-token context stops", lambda v: v["native_context_stops"]),
        line("Terminal counting failures", lambda v: v["terminal_count_failures"]),
        line("Infrastructure attempts", lambda v: v["infrastructure_attempts"]),
        line("Zero-generation attempts", lambda v: v["zero_model_call_attempts"]),
        line(
            "Source unchanged / changed / missing",
            lambda v: " / ".join(
                str(v["source_audits"].get(k, 0)) for k in ["unchanged", "changed", "missing"]
            ),
        ),
        line("Model generations", lambda v: v["model_calls"]),
        line(
            "Sum of recorded sample time (minutes)",
            lambda v: f"{v['recorded_sample_seconds_sum'] / 60:.2f}",
        ),
        line(
            "First-start to last-completion interval (minutes)",
            lambda v: f"{v['calendar_interval_seconds'] / 60:.2f}",
        ),
        line(
            "Estimated returned model-usage cost", lambda v: f"${v['estimated_model_cost_usd']:.5f}"
        ),
        line(
            "Uncached cost upper bound (including reservations)",
            lambda v: f"${v['uncached_cost_upper_usd']:.5f}",
        ),
    ]
    text = "# Controller and network recovery comparison\n\n"
    text += "Prepared-v4 completed all sixty scientific cells under one unchanged freeze. Infrastructure attempts are retained separately and never satisfy a cell. An unsolved scientific outcome remains final.\n\n"
    text += "\n".join(table) + "\n\n"
    text += "## Interpretation\n\nPrepared-v3 was infrastructure-invalid: 59 DNS failures, 55 zero-generation attempts, and only one answer-solved attempt. Its low cost and time reflect early aborts, not efficiency. v2 had 39 premature byte-bound stops and one startup failure. Neither problem should be interpreted as evidence against lessons.\n\n"
    totals = current["totals"]
    delta = sum(totals[f"B{i}"]["solved"] - totals[f"A{i}"]["solved"] for i in [1, 2]) / 2
    text += f"Under v4, A solved {totals['A1']['solved']}/15 and {totals['A2']['solved']}/15; B solved {totals['B1']['solved']}/15 and {totals['B2']['solved']}/15. Average B-minus-A solved count is {delta:+.1f}. This is a descriptive observation on fifteen reused tasks, not a statistical-significance or unseen-generalization claim. Cross-version differences also include temporal and model-sampling variation.\n\n"
    text += f"Native counts matched returned input usage on {current['native_counts_matching_usage']} of {current['model_calls']} generations. {current['old_byte_bound_crossings']} generated requests crossed the former byte guard. Retained request-level failures: {len(current['request_retry_failures'])}; retained infrastructure attempts: {current['infrastructure_attempts']}. All-attempt answer success: {current['all_attempt_answer_solved']}/{current['attempts']}.\n\n"
    text += "Sample timers include in-task retries and scientific execution. The calendar interval also includes between-cell preflights, cooldowns and scheduling gaps; neither is CPU time. Costs use returned token usage, exclude host/image/development costs, and are not an invoice. Unknown usage remains represented by conservative reservations. All infrastructure attempt time and cost are included.\n\n"
    text += "Source integrity is a separate criterion: correct answers produced after changing scientific inputs are not faithful unchanged-input reproductions. Audit absence is never treated as unchanged. See every run, including failed attempts, for evidence.\n\n"
    text += "## Verification and retained evidence\n\n- [Frozen recovery protocol](network-recovery-protocol.md)\n- [Development validation](../reports/development-v4-validation.json)\n- [Live network and injected recovery validation](../reports/network-development-v4/validation.json)\n- [Full comparison data](../reports/controller-comparison.json)\n- [Per-task results](results.md)\n- [Portable evidence browser](../reports/index.html)\n- [All 59 historical DNS failures](../reports/transport-failures-v3.json)\n- [Archived v3 interpretation](../reports/archive-v3/controller-comparison.md)\n\nThe release retains v1, v2 and v3 experiments and their original public releases. The exact historical DNS root cause remains unknown; successful current requests and retry validation do not retroactively diagnose it.\n"
    (ROOT / "docs/controller-comparison.md").write_text(text)
    print(json.dumps(current, indent=2))


if __name__ == "__main__":
    main()
