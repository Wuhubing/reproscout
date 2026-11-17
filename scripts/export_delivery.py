"""Export a portable, credential-free evidence site from actual run records."""

from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from pathlib import Path

from inspect_ai.log import read_eval_log

from reproscout.diagnosis import diagnose
from reproscout.reporting import report
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--experiment", type=Path)
    args = parser.parse_args()
    destination = ROOT / "reports"
    destination.mkdir(exist_ok=True)
    rows = []
    run_records = []
    for run in sorted((ROOT / "runs").iterdir()):
        if not (run / "summary.json").exists():
            continue
        summary = json.loads((run / "summary.json").read_text())
        if summary["mode"] != "run":
            continue
        diagnose(run)
        report(run)
        target = destination / "runs" / run.name
        target.mkdir(parents=True, exist_ok=True)
        for p in run.iterdir():
            if p.suffix in {".json", ".html", ".md"} and "before-accounting-fix" not in p.name:
                shutil.copyfile(p, target / p.name)
        if (run / "artifacts").exists():
            shutil.copytree(run / "artifacts", target / "artifacts", dirs_exist_ok=True)
        # Export model/tool messages rather than provider headers, environment or raw answers.
        logs = list((run / "logs").glob("*.eval"))
        if logs:
            sample = read_eval_log(str(logs[0])).samples[0]
            trajectory = {
                "messages": [m.model_dump(mode="json") for m in sample.messages],
                "model_usage": {k: v.model_dump() for k, v in sample.model_usage.items()},
                "sample_error": sample.error.message if sample.error else None,
            }
            encoded = json.dumps(trajectory, indent=2, ensure_ascii=True)
            if re.search(r"sk-[A-Za-z0-9_-]{20,}", encoded):
                raise ValueError("Potential secret in trajectory; export refused")
            (target / "trajectory.json").write_text(encoded, encoding="utf-8")
        manifest = json.loads((run / "manifest.json").read_text())
        score = summary.get("evaluation", {})
        group = "held-out" if summary.get("experiment_id") else "development"
        result = f"{score.get('correct_questions', 0)}/{len(manifest['questions'])}"
        link = f"runs/{run.name}/report.html"
        rows.append(
            f"<tr><td>{group}</td><td>{manifest['task_id']}</td><td>{manifest['language']}</td>"
            f"<td>{summary.get('condition', 'A')}{summary.get('repeat', 1)}</td><td>{result}</td>"
            f"<td>${summary['cost_estimated_usd']:.5f}</td><td>{summary['seconds']:.1f}s</td>"
            f'<td><a href="{link}">Evidence report</a></td></tr>'
        )
        run_records.append(
            {"run_id": run.name, "task_id": manifest["task_id"], "group": group, **summary}
        )
    write_json(destination / "run-index.json", run_records)
    comparison = "No frozen held-out comparison has completed."
    groups = ""
    lessons_panel = ""
    if args.experiment:
        results = json.loads((args.experiment / "results.json").read_text())
        shutil.copytree(args.experiment, destination / "experiment", dirs_exist_ok=True)
        comparison = "<table><tr><th>Condition / repeat</th><th>Solved capsules</th><th>Model cost</th><th>Total time</th></tr>"
        for label, value in results["totals"].items():
            comparison += f"<tr><td>{label}</td><td>{value['solved']}/{value['planned']}</td><td>${value['cost_estimated_usd']:.5f}</td><td>{value['seconds']:.1f}s</td></tr>"
        comparison += f"</table><p>Average B minus A solved count: <strong>{results['average_solved_difference_B_minus_A']:+.1f}</strong>. Missing planned runs: {len(results['missing'])}.</p>"
        comparison += '<p>A: baseline. B: frozen development lessons. <a href="experiment/freeze.json">Freeze manifest</a> | <a href="experiment/results.json">Full comparison data</a></p>'
        formal = [r for r in run_records if r.get("experiment_id") == results["experiment_id"]]
        groups = "<h2>Language and modality</h2><table><tr><th>Group</th><th>A solved / runs</th><th>B solved / runs</th></tr>"
        for field, value in [
            ("language", "Python"),
            ("language", "R"),
            ("vision", False),
            ("vision", True),
        ]:
            cells = []
            for condition in ["A", "B"]:
                subset = [
                    r
                    for r in formal
                    if r["condition"] == condition
                    and json.loads((ROOT / "manifests" / (r["task_id"] + ".json")).read_text()).get(
                        field
                    )
                    == value
                ]
                cells.append(
                    f"{sum(bool(r.get('evaluation', {}).get('solved')) for r in subset)}/{len(subset)}"
                )
            label = (
                value
                if field == "language"
                else ("Vision-labelled tasks" if value else "Text tasks")
            )
            groups += f"<tr><td>{label}</td><td>{cells[0]}</td><td>{cells[1]}</td></tr>"
        groups += "</table><p>Counts include both repetitions; repetitions are not independent tasks. Task modality labels do not prove the image tool was used.</p>"
        lessons_panel = (
            "<h2>Frozen development lessons</h2><details><summary>Read the rules and source cases</summary><pre>"
            + html.escape((args.experiment / "lessons.md").read_text())
            + "</pre></details>"
        )
    failures = {}
    for r in run_records:
        diagnosis = json.loads((destination / "runs" / r["run_id"] / "diagnosis.json").read_text())
        label = diagnosis.get("category", "unknown")
        failures[label] = failures.get(label, 0) + 1
    failure_panel = (
        "<h2>Provisional diagnoses (all recorded runs)</h2><pre>"
        + html.escape(json.dumps(failures, indent=2))
        + "</pre><p>Independent human agreement: not measured. These are operational labels, not causal ground truth.</p>"
    )
    for path in sorted((ROOT / "runs").glob("*/environment-checks.json")):
        shutil.copyfile(path, destination / "environment-checks.json")
    page = f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>ReproScout results</title>
<style>body{{font:16px system-ui;max-width:1200px;margin:40px auto;padding:0 24px;color:#172633}}h1{{font-size:38px}}table{{border-collapse:collapse;width:100%}}td,th{{padding:10px;border-bottom:1px solid #ccd6dc;text-align:left}}pre{{background:#f0f4f7;padding:20px;white-space:pre-wrap}}a{{color:#1659a5}}.note{{padding:18px;background:#fff1d6;border-left:4px solid #ba7900}}</style>
<h1>ReproScout</h1><p>Evidence-linked scientific reproduction with frozen development lessons.</p>
<p class="note">Prepared author environments, offline execution, small selected subset.
This is not an unchanged CORE-Bench Medium result. Registry availability constrained cohort size.
Results are empirical observations, not proof of general reproducibility or statistical significance.</p>
<h2>Frozen comparison</h2>{comparison}
{groups}{lessons_panel}<h2>Recorded runs</h2><table><tr><th>Split</th><th>Task</th><th>Language</th><th>Condition</th><th>Questions correct</th><th>Model cost</th><th>Time</th><th>Details</th></tr>{"".join(rows)}</table>
{failure_panel}<h2>Inspect the evidence</h2><p>Each task report links to controller-owned output snapshots.
A trajectory.json file alongside each report preserves the actual model/tool conversation.
Costs are usage-based estimates. Failure diagnoses are provisional, not independent human labels.</p>
<p><a href="run-index.json">Run index</a> | <a href="environment-checks.json">Environment checks</a> |
<a href="https://github.com/Wuhubing/reproscout">Source and reproduction instructions</a></p></html>"""
    (destination / "index.html").write_text(page, encoding="utf-8")
    print(f"Exported {len(rows)} runs to {destination / 'index.html'}")


if __name__ == "__main__":
    main()
