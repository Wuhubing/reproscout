"""Apply the prospectively declared v6 development gate without score-floor changes."""

import json
from pathlib import Path

from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    cohort = json.loads((ROOT / "manifests/cohort.json").read_text())["development"]
    rows = []
    for p in sorted((ROOT / "runs").glob("*/summary.json")):
        x = json.loads(p.read_text())
        if x.get("experiment_id") == "development-v6":
            x["task_id"] = json.loads((p.parent / "manifest.json").read_text())["task_id"]
            rows.append(x)
    science = [x for x in rows if not x["infrastructure_failure"]]
    b = [x for x in science if x["condition"] == "B"]
    checks = {
        "ten_distinct_scientific_cells": len(science) == 10
        and {(x["task_id"], x["condition"]) for x in science}
        == {(t, c) for t in cohort for c in ["A", "B"]},
        "all_five_B_submissions": len(b) == 5
        and all((ROOT / "runs" / x["run_id"] / "submission.json").exists() for x in b),
        "B_strict_types": len(b) == 5
        and all(x["fidelity"]["answer_types_compliant"] is True for x in b),
        "B_verified_non_null_provenance": len(b) == 5
        and all(x["fidelity"]["non_null_output_provenance_verified"] is True for x in b),
        "B_original_hashes_unchanged": len(b) == 5
        and all(
            json.loads((ROOT / "runs" / x["run_id"] / "source-audit.json").read_text())["unchanged"]
            for x in b
        ),
        "two_B_verified_answer_successes": sum(
            x["fidelity"]["answer_solved_with_verified_execution"] for x in b
        )
        >= 2,
    }
    out = {
        "passed": all(checks.values()),
        "checks": checks,
        "all_attempts": rows,
        "protocol": "docs/fidelity-protocol-v6.md",
        "gate_changed_after_results": False,
    }
    write_json(ROOT / "reports/development-v6-validation.json", out)
    print(
        json.dumps(
            {
                "passed": out["passed"],
                "checks": checks,
                "A_solved": sum(
                    x["condition"] == "A" and bool(x["evaluation"].get("solved")) for x in science
                ),
                "B_solved": sum(bool(x["evaluation"].get("solved")) for x in b),
            },
            indent=2,
        )
    )
    if not out["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
