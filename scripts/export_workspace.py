"""Export only the v0.8 acceptance attempts, preserving previous delivery reports."""

import json
import shutil
from pathlib import Path

from export_delivery import check_public_export

from reproscout.reporting import document, escape, report
from reproscout.web import Workspace

ROOT = Path(__file__).resolve().parents[1]


def main():
    workspace = Workspace(ROOT)
    records = json.loads((ROOT / "reports/workspace-acceptance-v8.json").read_text())
    rows = []
    for record in records["runs"]:
        key = record["run_id"]
        source = workspace.reviewed_source(key)
        target = ROOT / "reports/workspace-runs" / key
        target.mkdir(parents=True, exist_ok=True)
        for p in source.iterdir():
            if p.suffix in (".json", ".jsonl", ".md") or p.name == "cancel.requested":
                check_public_export(p.read_text())
                shutil.copyfile(p, target / p.name)
        if (source / "artifacts").exists():
            for p in (source / "artifacts").iterdir():
                if p.suffix in (".txt", ".json", ".html"):
                    check_public_export(p.read_text())
            shutil.copytree(source / "artifacts", target / "artifacts", dirs_exist_ok=True)
        report(target)
        assessment = json.loads((target / "review-assessment.json").read_text())
        summary = json.loads((target / "summary.json").read_text())
        record["outcome"] = assessment["outcome"]
        rows.append(
            f'<tr><td>{escape(record["task_id"])}</td><td>{escape(assessment["outcome"])}</td><td>{summary["model_calls"]}</td><td>{summary["seconds"]:.2f}s</td><td>${summary["cost_estimated_usd"]:.6f}</td><td><a href="workspace-runs/{key}/report.html">Evidence report</a></td></tr>'
        )
    (ROOT / "reports/workspace-v8.html").write_text(
        document(
            "ReproScout workspace acceptance",
            "<h1>v0.8 local workspace acceptance</h1><p>Browser-launched development attempts. No reference scoring or new A/B experiment. A cancelled attempt is retained separately.</p><table><tr><th>Task</th><th>Outcome</th><th>Model calls</th><th>Time</th><th>Estimated cost</th><th>Evidence</th></tr>"
            + "".join(rows)
            + '</table><p><a href="index.html">Preserved v0.7 dashboard</a> · <a href="experiments-v6.html">Historical experiments</a></p>',
        )
    )
    (ROOT / "reports/workspace-acceptance-v8.json").write_text(json.dumps(records, indent=2) + "\n")


if __name__ == "__main__":
    main()
