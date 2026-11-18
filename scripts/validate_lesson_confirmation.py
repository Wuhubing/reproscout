"""Accept or reject the second candidate without deleting the first candidate."""

import json
from pathlib import Path

from reproscout.experiment import file_hash
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    prior = json.loads((ROOT / "reports/development-v5-candidate1-validation.json").read_text())
    cohort = json.loads((ROOT / "manifests/cohort.json").read_text())
    rows = []
    for p in sorted((ROOT / "runs").glob("*/summary.json")):
        s = json.loads(p.read_text())
        if s.get("experiment_id") != "development-confirmation-v5":
            continue
        m = json.loads((p.parent / "manifest.json").read_text())
        b = json.loads((p.parent / "budget.json").read_text())
        a = p.parent / "source-audit.json"
        q = p.parent / "submission.json"
        answers = json.loads(q.read_text()) if q.exists() else {}
        ref = json.loads((ROOT / m["answers_path"]).read_text())
        errors = [
            qid
            for qid, question in m["questions"].items()
            if isinstance(ref[0][question], (int, float))
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
                "submission_present": q.exists(),
                "numeric_format_errors": errors,
                "native_counts_match": all(
                    c["native_input_tokens"]
                    == c["usage"]["input_tokens"]
                    + (c["usage"].get("input_tokens_cache_read") or 0)
                    + (c["usage"].get("input_tokens_cache_write") or 0)
                    for c in b["calls"]
                ),
            }
        )
    selected = [x for x in rows if not x["infrastructure_failure"]]
    solved = sum(bool(x.get("evaluation", {}).get("solved")) for x in selected)
    snapshot = json.loads(
        (ROOT / "reports/lesson-confirmation-v5/candidate-freeze.json").read_text()
    )
    review_path = ROOT / "reports/development-confirmation-review-v5.json"
    review = json.loads(review_path.read_text()) if review_path.exists() else {}
    legacy = [
        x
        for x in prior["rows"]
        if x["experiment_id"] == "development-legacy-v5" and not x["infrastructure_failure"]
    ]
    legacy_qualified = sum(
        bool(x.get("evaluation", {}).get("solved"))
        and x["source_unchanged"] is True
        and x["run_id"] not in review.get("legacy_scientific_change_runs", [])
        for x in legacy
    )
    checks = {
        "original_fifteen_outcomes_retained": prior["checks"]["fifteen_scientific_outcomes"],
        "candidate1_rejected": prior["passed"] is False,
        "five_confirmation_outcomes": len(selected) == 5
        and {x["task_id"] for x in selected} == set(cohort["development"]),
        "candidate_unchanged": all(file_hash(ROOT / p) == h for p, h in snapshot["files"].items()),
        "count_accounting": all(
            x["model_calls"] > 0 and x["native_counts_match"] for x in selected
        ),
        "candidate_submissions": all(x["submission_present"] for x in selected),
        "candidate_numeric_types": all(not x["numeric_format_errors"] for x in selected),
        "amended_fidelity_aware_success_floor": solved >= max(3, legacy_qualified),
        "legacy_review_complete": set(review.get("legacy_reviewed_run_ids", []))
        == {x["run_id"] for x in legacy},
        "candidate_input_hashes": all(x["source_unchanged"] is True for x in selected),
        "manual_candidate_fidelity_review": review.get("passed") is True
        and set(review.get("run_ids", [])) == {x["run_id"] for x in selected},
    }
    out = {
        "passed": all(checks.values()),
        "checks": checks,
        "rows": prior["rows"] + rows,
        "all_development_run_ids": prior["all_development_run_ids"] + [x["run_id"] for x in rows],
        "candidate_solved": solved,
        "legacy_solved": prior["legacy_solved"],
        "legacy_fidelity_qualified_solved": legacy_qualified,
        "original_raw_success_floor_passed": solved >= max(3, prior["legacy_solved"]),
        "acceptance_amended_before_confirmation": True,
        "baseline_solved": prior["baseline_solved"],
        "candidate_experiment": "development-confirmation-v5",
        "candidate_lessons": "lessons/development-v2b.md",
        "candidate1_solved": prior["candidate_solved"],
        "candidate1_rejected": True,
        "scope": "Fifteen first-stage outcomes plus five second-candidate confirmations. Candidate 2 is later in time; not proof of statistical superiority or fresh generalization.",
    }
    write_json(ROOT / "reports/development-v5-validation.json", out)
    print(
        json.dumps(
            {k: v for k, v in out.items() if k not in {"rows", "all_development_run_ids"}}, indent=2
        )
    )
    if not out["passed"]:
        raise SystemExit("Final development candidate not accepted.")


if __name__ == "__main__":
    main()
