"""Accept the predeclared network gate without selecting on answer correctness."""

import argparse
import json
from pathlib import Path

from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--environment-run", type=Path, required=True)
    args = parser.parse_args()
    cohort = json.loads((ROOT / "manifests/cohort.json").read_text())
    expected = {(t, c) for t in cohort["development"] for c in ["A", "B"]}
    rows = []
    for path in sorted((ROOT / "runs").glob("*/summary.json")):
        s = json.loads(path.read_text())
        if s.get("experiment_id") != "development-v4":
            continue
        b = json.loads((path.parent / "budget.json").read_text())
        m = json.loads((path.parent / "manifest.json").read_text())
        audit = (
            json.loads((path.parent / "source-audit.json").read_text())
            if (path.parent / "source-audit.json").exists()
            else {}
        )
        rows.append(
            {
                **s,
                "task_id": m["task_id"],
                "source_unchanged": audit.get("unchanged"),
                "native_counts_match": all(
                    c["native_input_tokens"]
                    == c["usage"]["input_tokens"]
                    + (c["usage"].get("input_tokens_cache_read") or 0)
                    + (c["usage"].get("input_tokens_cache_write") or 0)
                    for c in b["calls"]
                ),
                "count_failures": sum(c["status"] == "count_failed" for c in b["request_checks"]),
            }
        )
    scientific = [r for r in rows if not r["infrastructure_failure"]]
    assert (
        len(scientific) == 10 and {(r["task_id"], r["condition"]) for r in scientific} == expected
    )
    assert all(
        r["model_calls"] > 0 and r["native_counts_match"] and r["count_failures"] == 0
        for r in scientific
    )
    network = json.loads((ROOT / "reports/network-development-v4/validation.json").read_text())
    assert network["passed"] and network["samples"] == 30 and network["injected_dns_failures"] == 2
    env = json.loads((args.environment_run / "environment-checks.json").read_text())
    assert len(env) == 13 and all(v["passed"] for v in env.values())
    write_json(
        ROOT / "reports/development-v4-validation.json",
        {
            "passed": True,
            "experiment_id": "development-v4",
            "rows": rows,
            "all_development_run_ids": [r["run_id"] for r in rows],
            "network": network,
            "environment_run": args.environment_run.name,
            "environment_checks": env,
            "scope": "Network and accounting gate; answer correctness and source integrity reported independently.",
            "source_integrity_violations": [
                r["run_id"] for r in rows if r["source_unchanged"] is False
            ],
        },
    )
    print(
        "Development network gate passed: 10 scientific A/B outcomes, 30 real counts, injected recovery, 13 environment checks."
    )


if __name__ == "__main__":
    main()
