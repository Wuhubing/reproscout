"""Explain the four v4 adverse pairs using public observable traces only."""

import json
from pathlib import Path

from reproscout.experiment import file_hash
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    pairs = json.loads((ROOT / "reports/paired-outcomes-v4.json").read_text())["pairs"]
    adverse = [p for p in pairs if p["A_solved"] and not p["B_solved"]]
    assert len(adverse) == 4
    cases = []
    for pair in adverse:
        case = dict(pair)
        case["runs"] = {}
        for condition in ["A", "B"]:
            run = ROOT / "reports/runs" / pair[f"{condition}_run_id"]
            summary = json.loads((run / "summary.json").read_text())
            trajectory = json.loads((run / "trajectory.json").read_text())
            submission = run / "submission.json"
            calls = [t for m in trajectory["messages"] for t in m.get("tool_calls") or []]
            case["runs"][condition] = {
                "run_id": run.name,
                "model_calls": summary["model_calls"],
                "seconds": summary["seconds"],
                "cost_estimated_usd": summary["cost_estimated_usd"],
                "sample_error": summary.get("sample_error"),
                "source_audit": json.loads((run / "source-audit.json").read_text()),
                "submission": json.loads(submission.read_text()) if submission.exists() else None,
                "unsupported_timeout_calls": sum("timeout" in t["arguments"] for t in calls),
                "tool_calls": calls,
                "trajectory_sha256": file_hash(run / "trajectory.json"),
            }
        cases.append(case)
    write_json(
        ROOT / "reports/lesson-pair-analysis-v4.json",
        {
            "scope": "Four paired observations on three exposed test tasks; observable behavior, not hidden reasoning or causal proof.",
            "cases": cases,
        },
    )
    table = []
    for p in cases:
        a, b = p["runs"]["A"], p["runs"]["B"]
        table.append(
            f"| {p['task_id']} | {p['repeat']} | {a['model_calls']} / {b['model_calls']} | {a['seconds']:.1f} / {b['seconds']:.1f} | ${a['cost_estimated_usd']:.5f} / ${b['cost_estimated_usd']:.5f} |"
        )
    text = (
        """# Why four v4 pairs favored A

The v4 score gap was A 25/30 versus B 21/30. Four task/repetition pairs favored A,
none favored B. These are **four observations on three capsules**, not four
independent tasks. The analysis uses saved tool calls, outputs, submissions and the
unchanged scorer; encrypted provider reasoning is not available for interpretation.
No old outcome is rescored or replaced.

| Capsule | Repeat | Model calls A / B | Seconds A / B | Estimated cost A / B |
|---|---:|---:|---:|---:|
"""
        + "\n".join(table)
        + """

## 1. capsule-0504157, repeat 2: units, with a fidelity caveat

[A2](../reports/runs/20261118T063706044862Z-capsule-0504157-run-A2/report.html)
submitted numeric `1000`. [B2](../reports/runs/20261118T063546423955Z-capsule-0504157-run-B2/report.html)
submitted `"1000 ms"`, although the question says to ignore units. The scorer calls
`float(str(value).replace("%", ""))`; the latter raises a conversion error. Removing
units would produce A's accepted scalar, but that is a **formatting counterfactual**,
not a corrected formal outcome or proof that every computation was faithful.

Both runs hit the manuscript's offline GitHub dependency, inspected bundled data,
and computed EC summaries. B did not immediately abandon the task under old L1:
it continued through twenty model calls and submitted. Its step-018 output shows
coded time groups; step-008 includes the author's mapping from those groups to the
displayed presentation times. Its hand-built calculation also omits parts of the
author's filtering path. The numerical scalar alone does not validate that path.

More seriously, A copied the manuscript to `manuscript.Rmd`, replaced the network
logic, and rendered the edited copy (shell step-008). Its original-file hash audit
still passed because it checks original files, not newly created scientific copies.
A's answer score must therefore not be treated as an unqualified faithful-reproduction
win. This refines the v4 interpretation without changing its original metrics.
Revision 2 explicitly prohibits scientific changes in copies as well as originals.

## 2. capsule-2708693, repeat 1: search and presentation consumed the submission budget

[A1](../reports/runs/20261118T055452132871Z-capsule-2708693-run-A1/report.html)
read the task data, corrected shell quoting, printed the requested counts and
submitted them. [B1](../reports/runs/20261118T055556608693Z-capsule-2708693-run-B1/report.html)
reached twenty generations with no submission. Both encountered missing rendering
support and had access to the data. B spent calls locating and testing an alternate
pandoc, then repeatedly inspected manuscript sections and searched output variables.
Its final call still searched `ndisclosed`, `CIdisclosed`, and `PIdisclosed`.

Both trajectories also contain unsupported `timeout` tool arguments and shell
expansion of R `$` expressions. These consume budget or produce irrelevant errors.
Old L3 did not reliably prevent B's first missing-README chain. Old L2 advises
notebook execution once; this R Markdown trajectory does **not** establish that L2
caused the pandoc detour. The observed mechanism is lost submission opportunity,
not a native-count/DNS failure. Revision 2 gives schema/quoting reminders, separates
presentation from computation, and reserves calls for a final evidence-backed report.

## 3. capsule-9054015, repeat 1: wrong output family, not just formatting

[A1](../reports/runs/20261118T052421157449Z-capsule-9054015-run-A1/report.html)
queried the author function for the requested prevalence/figure conditions and
submitted `90`. [B1](../reports/runs/20261118T052632424013Z-capsule-9054015-run-B1/report.html)
finished in seven calls but sorted `supplemental_table1` and submitted `"80%"`.
Its step-006 rows describe a different output grid. The question asks about the
figure's hypothetical test; matching a similarly named sensitivity column in a
supplemental table does not establish the same quantity. B's second answer passed.

The percent sign itself is accepted by the scorer. Removing it would still leave
the wrong first answer. This is an evidence-selection failure. It is consistent
with premature satisfaction after finding plausible output, but the traces cannot
prove the old avoid-reexecution advice caused that choice. Revision 2 asks for an
explicit question-to-output mapping and permits targeted inspection of objects
created by unchanged author code.

## 4. capsule-9054015, repeat 2: correct computed quantity, unparsable value

[A2](../reports/runs/20261118T063058891718Z-capsule-9054015-run-A2/report.html)
submitted `"90%"`, which the unchanged numeric scorer accepts.
[B2](../reports/runs/20261118T062744402986Z-capsule-9054015-run-B2/report.html)
computed the relevant maximum (step-011 stdout, lines 1–4) but submitted
`"90% sensitivity for both cancers A and B"`. Stripping only `%` still leaves prose,
so numeric conversion fails. The second answer passed. A numeric scalar matching
the computed percentage would remove this parsing failure; the formal record stays
failed. This case provides stronger evidence for a serialization problem than for
a scientific reasoning failure.

## What changes, and what the evidence does not establish

Two of four score deficits have immediate numeric-serialization explanations; one
uses the wrong result family; one never submits. None is an observed API or native
request-size failure. The old lessons focus on avoiding search, repeated notebook
execution, and README assumptions. They omit answer typing, question-output mapping,
and explicit submission budgeting. They also are not always followed.

Adding instructions can change trajectories, token use and attention, but the runs
do not isolate causal effects of individual lessons. No significance claim is made.
The exposed pairs motivate generic revisions; all candidate selection and live
validation occur on the five official training tasks. This remains test-informed
method development and the next sixty-cell rerun is a regression study on an exposed
cohort. It cannot be called a fresh held-out generalization test.

The scorer, base prompt, model and budgets remain unchanged. Do not repair apparent
performance by accepting arbitrary prose numerals, changing reference answers,
patching scientific code, or selectively retrying failures. Original-hash integrity
is reported separately from semantic fidelity and copied-code review.

[Machine-readable calls and metrics](../reports/lesson-pair-analysis-v4.json) ·
[Revision protocol](lesson-revision-protocol.md) · [Rejected first candidate](../lessons/development-v2.md) · [Second candidate](../lessons/development-v2b.md) · [Confirmation amendment](lesson-confirmation-protocol.md)
"""
    )
    (ROOT / "docs/lesson-pair-analysis-v4.md").write_text(text)
    print("Analyzed four adverse pairs on three tasks; historical outcomes unchanged.")


if __name__ == "__main__":
    main()
