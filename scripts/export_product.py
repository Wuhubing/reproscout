"""Export only explicitly selected product runs; preserve historical reports byte for byte."""

import json
import shutil
from pathlib import Path

from export_delivery import check_public_export, public_messages
from inspect_ai.log import read_eval_log

from reproscout.reporting import document, escape, report
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    reports = ROOT / "reports"
    selected = json.loads((reports / "product-development-runs.json").read_text())
    rows = []
    for name in selected:
        run = ROOT / name
        target = reports / "product-runs" / run.name
        target.mkdir(parents=True, exist_ok=True)
        for path in run.iterdir():
            if path.suffix in (".json", ".jsonl", ".md"):
                encoded = path.read_text()
                check_public_export(encoded)
                (target / path.name).write_text(encoded)
        if (run / "artifacts").exists():
            for path in (run / "artifacts").iterdir():
                if path.suffix in (".txt", ".json", ".html"):
                    check_public_export(path.read_text())
            shutil.copytree(run / "artifacts", target / "artifacts", dirs_exist_ok=True)
        logs = list((run / "logs").glob("*.eval"))
        if logs:
            log = read_eval_log(str(logs[0]))
            if log.samples:
                sample = log.samples[0]
                value = {
                    "messages": public_messages(
                        [m.model_dump(mode="json") for m in sample.messages]
                    ),
                    "model_usage": {k: v.model_dump() for k, v in sample.model_usage.items()},
                    "export_policy": "Visible messages retained. Encrypted reasoning omitted. Raw logs remain local.",
                }
                encoded = json.dumps(value, indent=2)
                check_public_export(encoded)
                (target / "trajectory.json").write_text(encoded)
        report(target)
        assessment = json.loads((target / "review-assessment.json").read_text())
        manifest = json.loads((target / "manifest.json").read_text())
        summary = json.loads((target / "summary.json").read_text())
        rows.append(
            {
                "run_id": run.name,
                "task_id": manifest["task_id"],
                "title": manifest["title"],
                "outcome": assessment["outcome"],
                "scoring": assessment["scoring"],
                "seconds": summary["seconds"],
                "cost_estimated_usd": summary["cost_estimated_usd"],
                "report": f"product-runs/{run.name}/report.html",
            }
        )
    write_json(reports / "product-index.json", rows)
    old = reports / "experiments-v6.html"
    if not old.exists():
        shutil.copyfile(reports / "index.html", old)
    table = "".join(
        f'<tr><td>{escape(r["title"])}</td><td>{escape(r["outcome"])}</td><td>{r["scoring"]}</td><td><a href="{r["report"]}">Open review</a></td></tr>'
        for r in rows
    )
    body = f"""<h1>ReproScout</h1><p>Review scientific reproduction through original author execution and inspectable evidence.</p>
<h2>Recent development runs</h2><p>Three prepared tasks, no reference answers. These are product acceptance runs, not a new A/B experiment.</p>
<table><tr><th>Task</th><th>Outcome</th><th>Scoring</th><th>Report</th></tr>{table}</table>
<h2>Start a review</h2><p>Supply a prepared capsule manifest, explicit question types, and a pinned author environment. Run the CLI, inspect candidate evidence, then import an attributed review.</p><p><a href="../docs/product-guide.md">Workflow and commands</a> · <a href="../docs/product-release-v7.md">Validation and limitations</a></p>
<h2>Historical experiments</h2><p>The research record remains available separately. Product completion is not evidence that lessons improve scientific success.</p><p><a href="experiments-v6.html">Open preserved experiment dashboard</a></p>"""
    (reports / "index.html").write_text(document("ReproScout", body))


if __name__ == "__main__":
    main()
