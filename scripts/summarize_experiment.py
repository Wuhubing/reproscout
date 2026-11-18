"""Write measured results and verify evidence without altering any run outcome."""

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

from reproscout.experiment import verify_freeze
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("experiment", type=Path)
    args = parser.parse_args()
    freeze = verify_freeze(ROOT, args.experiment)
    result = json.loads((args.experiment / "results.json").read_text())
    if result["missing"]:
        raise ValueError("Do not publish a completed-study summary with missing cells")
    runs = result["runs"]
    cohort = freeze["cohort"]
    prior = freeze.get("previously_evaluated_task_ids", [])
    rows = []
    unchanged = 0
    source_missing = 0
    images = 0
    labels = Counter()
    records = []
    for run in runs:
        folder = ROOT / "runs" / run["run_id"]
        manifest = json.loads((folder / "manifest.json").read_text())
        audit_path = folder / "source-audit.json"
        audit = json.loads(audit_path.read_text()) if audit_path.exists() else {}
        unchanged += audit.get("unchanged") is True
        source_missing += not audit_path.exists()
        artifact_path = folder / "artifact-index.json"
        artifacts = json.loads(artifact_path.read_text()) if artifact_path.exists() else {}
        for name, artifact in artifacts.items():
            if hashlib.sha256((folder / name).read_bytes()).hexdigest() != artifact["sha256"]:
                raise ValueError(f"Artifact digest mismatch: {run['run_id']}/{name}")
            images += artifact["kind"] == "image"
        diagnosis = json.loads((folder / "diagnosis.json").read_text())
        labels[diagnosis.get("label") or "solved"] += 1
        score = run.get("evaluation", {})
        rows.append(
            f"| {run['task_id']} | {run['condition']}{run['repeat']} | {score.get('correct_questions', 0)}/{len(manifest['questions'])} | {bool(score.get('solved'))} | ${run['cost_estimated_usd']:.5f} | {run['seconds']:.1f} | {audit.get('unchanged', 'not recorded')} |"
        )
        records.append(
            {
                **run,
                "language": manifest["language"],
                "vision": manifest.get("vision", False),
                "prior": run["task_id"] in prior,
            }
        )
    totals = "\n".join(
        f"| {key} | {value['solved']}/{value['planned']} | ${value['cost_estimated_usd']:.5f} | {value['seconds']:.1f} |"
        for key, value in result["totals"].items()
    )
    groups = []
    for field, value, name in [
        ("language", "Python", "Python"),
        ("language", "R", "R"),
        ("vision", False, "Text-labelled"),
        ("vision", True, "Vision-labelled"),
        ("prior", False, "Newly evaluated"),
        ("prior", True, "Previously evaluated"),
    ]:
        cells = []
        for condition in ["A", "B"]:
            subset = [r for r in records if r[field] == value and r["condition"] == condition]
            cells.append(
                f"{sum(bool(r.get('evaluation', {}).get('solved')) for r in subset)}/{len(subset)}"
            )
        groups.append(f"| {name} | {cells[0]} | {cells[1]} |")
    cost = sum(r["cost_estimated_usd"] for r in runs)
    text = f"""# Measured results: {result["experiment_id"]}

This is a prepared-author-environment experiment on {len(cohort["heldout"])} official test
capsules. Author images are pre-provisioned and execution is offline. This is not
an unchanged CORE-Bench Medium score. Model and limits are recorded in the freeze.

## Complete paired comparison

| Cell | Solved capsules | Estimated model cost | Total seconds |
|---|---:|---:|---:|
{totals}

Average B-minus-A solved count: **{result["average_solved_difference_B_minus_A"]:+.1f}**.
All **{len(runs)}** planned scientific outcomes are present; no missing cells.
Retained infrastructure attempts: **{len(result.get("infrastructure_attempts", []))}**; these do not fill scientific cells.
Total selected-outcome model cost: **${cost:.5f}**. A receives no lessons; B receives the rules saved in this experiment's freeze.
All-attempt cost, including infrastructure retries: **${result.get("all_attempt_cost_estimated_usd", cost):.5f}**.
No earlier experiment run is counted in these totals. Costs exclude image
preparation, host compute, and development assistance.

## Group breakdown

| Group | A solved / attempts | B solved / attempts |
|---|---:|---:|
{chr(10).join(groups)}

Counts combine two repetitions; repeats are not independent scientific tasks.
Previously evaluated capsules: {len(prior)}; newly evaluated capsules: {len(cohort["heldout"]) - len(prior)}.
Prior exposure is disclosed rather than treating repeated evaluation as new data. Any method revision and its development validation are documented in this experiment's protocol. Task modality labels do not establish image-tool use.

## Per-task records

| Capsule | Cell | Correct questions | Solved | Model cost | Seconds | Inputs unchanged |
|---|---|---:|---|---:|---:|---|
{chr(10).join(rows)}

A missing submission or scientific execution/context/budget failure counts as unsolved, rather than
being excluded. Source integrity and answer correctness are separate properties.
Where inputs changed, the audit must be inspected before claiming faithful reproduction.

## Recovery and selection

The original eight unavailable selected images were revisited using the public
Registry authentication protocol, manifest digest verification, cached layers,
and serial pulls with bounded backoff. The original tag also worked in a control
recheck after the first recovery. The exact upstream rate-limit policy remains
unknown; do not attribute recovery conclusively to digest addressing alone.

The original size-ranked selection was extended to the proposal target of fifteen
held-out tasks before v2 execution. The five development tasks remain fixed;
the version-specific frozen lesson text records any subsequent revision. See selection-v2.json, recovery-v2.json, and the expanded
experiment protocol. No held-out score determined task replacement.

## Evidence and limitations

- Prepared original inputs unchanged: **{unchanged}/{len(runs)}**; missing audits: {source_missing}.
- All referenced evidence artifact hashes match their recorded SHA-256 values.
- Formal image artifacts: **{images}**.
- Provisional diagnoses: `{dict(labels)}`.
- Software checks, environment checks, report navigation, and release validation
  are recorded separately in reports/delivery-validation.json.
- Independent human diagnosis agreement and ten adversarial model-prompt trials
  remain unmeasured. Deterministic isolation checks are not substitutes for them.
- Two repetitions, a selected small-archive cohort, and amd64 emulation limit
  interpretation. No statistical-significance or general reproducibility claim is made.

The v0.1.0 release preserves the earlier two-task experiment. The expanded release
contains fresh runs and frozen lessons, with real failures retained. See the
portable evidence reports and exported trajectories for the underlying observations.
"""
    (ROOT / "docs/results.md").write_text(text, encoding="utf-8")
    write_json(
        ROOT / "reports/integrity-audit.json",
        {
            "experiment_id": result["experiment_id"],
            "formal_runs": len(runs),
            "source_unchanged": unchanged,
            "source_audits_missing": source_missing,
            "all_artifact_hashes_match": True,
            "image_artifacts": images,
            "diagnoses": dict(labels),
        },
    )
    print(f"Summarized {len(runs)} formal records; ${cost:.5f}")


if __name__ == "__main__":
    main()
