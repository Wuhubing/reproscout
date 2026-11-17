"""Generate portable English reports and a rebuildable SQLite event index."""

from __future__ import annotations

import html
import json
import sqlite3
from pathlib import Path

from inspect_ai.log import read_eval_log


def report(run: Path) -> Path:
    summary = json.loads((run / "summary.json").read_text())
    submission_path = run / "submission.json"
    answers = json.loads(submission_path.read_text()) if submission_path.exists() else {}
    manifest = json.loads((run / "manifest.json").read_text())
    rows = []
    for qid, question in manifest["questions"].items():
        answer = answers.get(qid, {})
        citations = []
        for ev in answer.get("evidence", []):
            name = ev["artifact"]
            citations.append(
                f'<a href="{html.escape(name, quote=True)}">{html.escape(name)} {("lines " + str(ev["line_start"]) + "-" + str(ev["line_end"])) if "line_start" in ev else "image"}</a>'
            )
        correct = summary.get("evaluation", {}).get("question_correct", {}).get(qid, "unscored")
        rows.append(
            f"<tr><td>{html.escape(question)}</td><td>{html.escape(str(answer.get('value', 'not submitted')))}</td><td>{correct}</td><td>{'<br>'.join(citations)}</td></tr>"
        )
    body = f"""<!doctype html><html lang="en"><meta charset="utf-8"><title>ReproScout evidence report</title>
<style>body{{font:16px system-ui;max-width:1150px;margin:40px auto;padding:0 24px;color:#172633}}table{{border-collapse:collapse;width:100%}}td,th{{padding:12px;border:1px solid #ccd6dc;text-align:left}}pre{{white-space:pre-wrap;background:#f2f5f7;padding:18px}}a{{color:#1659a5}}</style>
<h1>ReproScout: evidence report</h1><p>{html.escape(manifest["title"])}</p>
<p><strong>Prepared author environment. Not an unchanged CORE-Bench Medium result.</strong></p>
<p>Evidence links prove artifact availability, not semantic support. Semantic support requires a separate review.</p>
<table><tr><th>Question</th><th>Submitted answer</th><th>Correct</th><th>Evidence</th></tr>{"".join(rows)}</table>
<p><a href="diagnosis.json">Provisional failure diagnosis</a> | <a href="source-audit.json">Source integrity audit</a> | <a href="trajectory.json">Exported trajectory (delivery reports)</a></p><h2>Run summary</h2><pre>{html.escape(json.dumps(summary, indent=2))}</pre>
<p><a href="manifest.json">Task manifest</a> | <a href="budget.json">Model usage</a> | <a href="artifact-index.json">Artifact index</a></p></html>"""
    destination = run / "report.html"
    destination.write_text(body, encoding="utf-8")
    with sqlite3.connect(run / "index.sqlite") as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS events (id TEXT PRIMARY KEY, type TEXT, record TEXT)"
        )
        db.execute("DELETE FROM events")
        for path in (run / "logs").glob("*.eval"):
            log = read_eval_log(str(path))
            for sample in log.samples or []:
                for index, event in enumerate(sample.events):
                    db.execute(
                        "INSERT INTO events VALUES (?,?,?)",
                        (f"{path.name}:{sample.id}:{index}", event.event, event.model_dump_json()),
                    )
        db.commit()
    return destination
