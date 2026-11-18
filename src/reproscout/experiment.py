"""Freeze a small experiment and verify it before every held-out run."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from .tasks import write_json


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def freeze(root: Path, lessons: Path, development_runs: list[str], experiment_id: str) -> Path:
    cohort = json.loads((root / "manifests/cohort.json").read_text())
    if set(cohort["development"]) & set(cohort["heldout"]):
        raise ValueError("Development and held-out task IDs overlap")
    for run_id in development_runs:
        summary = json.loads((root / "runs" / run_id / "summary.json").read_text())
        if summary["split"] != "official_train":
            raise ValueError("Lessons sources must be official training runs")
    target = root / "experiments" / experiment_id
    target.mkdir(parents=True, exist_ok=False)
    (target / "lessons.md").write_text(lessons.read_text(), encoding="utf-8")
    paths = list((root / "src").rglob("*.py")) + list((root / "configs").glob("*.json"))
    paths += list((root / "scripts").glob("*.py"))
    paths += [root / "uv.lock", root / "pyproject.toml", root / "manifests/cohort.json"]
    paths += [
        root / "manifests" / f"{cid}.json" for cid in cohort["development"] + cohort["heldout"]
    ]
    payload = {
        "experiment_id": experiment_id,
        "cohort": cohort,
        "development_runs": development_runs,
        "lessons_sha256": file_hash(target / "lessons.md"),
        "files": {str(p.relative_to(root)): file_hash(p) for p in sorted(paths)},
        "repeats": 2,
        "conditions": ["A", "B"],
        "protocol": "Prepared author environments; fixed small size-ranked CPU subset; no held-out updates.",
    }
    write_json(target / "freeze.json", payload)
    return target


def verify_freeze(root: Path, experiment: Path) -> dict:
    payload = json.loads((experiment / "freeze.json").read_text())
    changed = [
        name
        for name, expected in payload["files"].items()
        if not (root / name).is_file() or file_hash(root / name) != expected
    ]
    if file_hash(experiment / "lessons.md") != payload["lessons_sha256"]:
        changed.append("lessons.md")
    if changed:
        raise ValueError("Frozen inputs changed: " + ", ".join(changed))
    return payload


def aggregate(root: Path, experiment: Path) -> dict:
    payload = verify_freeze(root, experiment)
    results = []
    for p in sorted((root / "runs").glob("*/summary.json")):
        s = json.loads(p.read_text())
        if s.get("experiment_id") == payload["experiment_id"]:
            s["task_id"] = json.loads((p.parent / "manifest.json").read_text())["task_id"]
            results.append(s)
    retry_policy = payload.get("infrastructure_retry_policy")
    all_attempts = results
    by_key = {}
    for result in results:
        key = (result["task_id"], result["condition"], result["repeat"])
        if retry_policy and result.get("infrastructure_failure"):
            continue
        if key in by_key:
            raise ValueError(
                "Duplicate formal run; apply an explicit retry policy before aggregation"
            )
        by_key[key] = result
    results = list(by_key.values())
    expected = [
        (cid, condition, repeat)
        for cid in payload["cohort"]["heldout"]
        for repeat in [1, 2]
        for condition in ["A", "B"]
    ]
    totals = {}
    for repeat in [1, 2]:
        for condition in ["A", "B"]:
            group = [r for r in results if r["condition"] == condition and r["repeat"] == repeat]
            totals[f"{condition}{repeat}"] = {
                "solved": sum(bool(r.get("evaluation", {}).get("solved")) for r in group),
                "completed_records": len(group),
                "planned": len(payload["cohort"]["heldout"]),
                "cost_estimated_usd": sum(r["cost_estimated_usd"] for r in group),
                "seconds": sum(r["seconds"] for r in group),
            }
    out = {
        "experiment_id": payload["experiment_id"],
        "totals": totals,
        "missing": [list(key) for key in expected if key not in by_key],
        "runs": results,
        **(
            {
                "all_attempts": all_attempts,
                "infrastructure_attempts": [
                    r for r in all_attempts if r.get("infrastructure_failure")
                ],
                "scientific_matrix_complete": set(by_key) == set(expected),
                "all_attempt_cost_estimated_usd": sum(
                    r["cost_estimated_usd"] for r in all_attempts
                ),
                "all_attempt_seconds": sum(r["seconds"] for r in all_attempts),
            }
            if retry_policy
            else {}
        ),
        "average_solved_difference_B_minus_A": sum(
            totals[f"B{i}"]["solved"] - totals[f"A{i}"]["solved"] for i in [1, 2]
        )
        / 2,
        "diagnostic_agreement": "Not measured: no independent human annotations.",
    }
    write_json(experiment / "results.json", out)
    return out
