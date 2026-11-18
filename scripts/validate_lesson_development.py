"""Evaluate the predeclared training gate, preserving adverse outcomes."""

import json
from pathlib import Path

from reproscout.experiment import file_hash
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    cohort = json.loads((ROOT / "manifests/cohort.json").read_text())
    rows = []
    for p in sorted((ROOT / "runs").glob("*/summary.json")):
        s = json.loads(p.read_text())
        if s.get("experiment_id") not in {"development-v5", "development-legacy-v5"}:
            continue
        m = json.loads((p.parent / "manifest.json").read_text())
        b = json.loads((p.parent / "budget.json").read_text())
        a = p.parent / "source-audit.json"
        submission = p.parent / "submission.json"
        answers = json.loads(submission.read_text()) if submission.exists() else {}
        references = json.loads((ROOT / m["answers_path"]).read_text())
        format_errors = [
            qid
            for qid, question in m["questions"].items()
            if isinstance(references[0][question], (int, float))
            and answers.get(qid, {}).get("value") is not None
            and (
                not isinstance(answers[qid]["value"], (int, float))
                or isinstance(answers[qid]["value"], bool)
            )
        ]
        rows.append(
            {
                **s,
                "task_id": m["task_id"],
                "source_unchanged": json.loads(a.read_text()).get("unchanged")
                if a.exists()
                else None,
                "submission_present": submission.exists(),
                "numeric_format_errors": format_errors,
                "native_counts_match": all(
                    c["native_input_tokens"]
                    == c["usage"]["input_tokens"]
                    + (c["usage"].get("input_tokens_cache_read") or 0)
                    + (c["usage"].get("input_tokens_cache_write") or 0)
                    for c in b["calls"]
                ),
            }
        )
    scientific = [x for x in rows if not x["infrastructure_failure"]]
    expected = {
        (t, e, c)
        for t in cohort["development"]
        for e, c in [
            ("development-v5", "A"),
            ("development-v5", "B"),
            ("development-legacy-v5", "B"),
        ]
    }
    candidate = [
        x for x in scientific if x["experiment_id"] == "development-v5" and x["condition"] == "B"
    ]
    legacy = [x for x in scientific if x["experiment_id"] == "development-legacy-v5"]

    def successes(group):
        return sum(bool(x.get("evaluation", {}).get("solved")) for x in group)

    snapshot = json.loads(
        (ROOT / "reports/lesson-development-v5/candidate-freeze.json").read_text()
    )
    manual = ROOT / "reports/development-trajectory-review-v5.json"
    review = json.loads(manual.read_text()) if manual.exists() else {}
    checks = {
        "fifteen_scientific_outcomes": len(scientific) == 15
        and {(x["task_id"], x["experiment_id"], x["condition"]) for x in scientific} == expected,
        "candidate_unchanged": all(file_hash(ROOT / p) == h for p, h in snapshot["files"].items()),
        "count_accounting": all(
            x["model_calls"] > 0 and x["native_counts_match"] for x in scientific
        ),
        "candidate_submissions": len(candidate) == 5
        and all(x["submission_present"] for x in candidate),
        "candidate_numeric_types": all(not x["numeric_format_errors"] for x in candidate),
        "candidate_success_floor": successes(candidate) >= max(3, successes(legacy)),
        "candidate_input_hashes": all(x["source_unchanged"] is True for x in candidate),
        "manual_candidate_fidelity_review": review.get("passed") is True
        and set(review.get("run_ids", [])) == {x["run_id"] for x in candidate},
    }
    out = {
        "passed": all(checks.values()),
        "checks": checks,
        "rows": rows,
        "all_development_run_ids": [x["run_id"] for x in rows],
        "candidate_solved": successes(candidate),
        "legacy_solved": successes(legacy),
        "baseline_solved": successes([x for x in scientific if x["condition"] == "A"]),
        "scope": "Single-repeat training mechanism check after test-informed revision; not proof of generalization or statistical superiority.",
    }
    write_json(ROOT / "reports/development-v5-validation.json", out)
    print(
        json.dumps(
            {k: v for k, v in out.items() if k not in {"rows", "all_development_run_ids"}}, indent=2
        )
    )
    if not out["passed"]:
        raise SystemExit("Development gate not accepted; retain outcomes and review failed checks.")


if __name__ == "__main__":
    main()
