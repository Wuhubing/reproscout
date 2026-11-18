"""Offline review reports with line-addressable, escaped evidence views."""

import html
import json
from pathlib import Path
from urllib.parse import quote

from .review import assess, read

STYLE = """body{font:16px system-ui;max-width:1200px;margin:36px auto;padding:0 24px;color:#172633;background:#fafbfc}h1{font-size:36px}table{border-collapse:collapse;width:100%;background:white}td,th{padding:12px;border:1px solid #ccd6dc;text-align:left;vertical-align:top}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#eef2f5;padding:18px}a{color:#1659a5}details{margin:18px 0}section{margin:32px 0}.line{display:block;white-space:pre-wrap}.line:target{background:#ffeb9c}small{color:#526372}"""


def escape(value):
    return html.escape(str(value), quote=True)


def document(title, body):
    return f'<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>{escape(title)}</title><style>{STYLE}</style><body>{body}</body></html>'


def evidence_link(run, item):
    name = item.get("artifact", "")
    path = (run / name).resolve()
    if not path.is_relative_to(run.resolve()) or not path.is_file():
        return "<strong>Unavailable evidence</strong>"
    if path.suffix.lower() in (".png", ".jpg", ".jpeg", ".gif"):
        return f'<a href="{quote(name)}">{escape(name)} (image)</a>'
    view = path.with_name(path.name + ".html")
    lines = path.read_text(errors="replace").splitlines()
    view.write_text(
        document(
            name,
            '<p><a href="'
            + "../" * len(Path(name).parent.parts)
            + 'report.html">Back to review</a></p><h1>'
            + escape(name)
            + "</h1><pre>"
            + "".join(
                f'<span class="line" id="L{i}"><a href="#L{i}">{i}</a> {escape(text)}</span>'
                for i, text in enumerate(lines, 1)
            )
            + "</pre>",
        )
    )
    if not lines:
        return f'<a href="{quote(name)}.html">{escape(name)} (empty output)</a>'
    line = item.get("line_start", 1)
    return f'<a href="{quote(name)}.html#L{line}">{escape(name)} lines {escape(line)}–{escape(item.get("line_end", line))}</a>'


def export_trace(run):
    """Export visible messages without provider encrypted reasoning or headers."""
    from inspect_ai.log import read_eval_log

    def public(value):
        if isinstance(value, list):
            return [public(x) for x in value]
        if isinstance(value, dict):
            result = {k: public(v) for k, v in value.items()}
            if result.get("type") == "reasoning" and result.get("redacted"):
                result["reasoning"] = (
                    "[Encrypted provider payload omitted; retained in local raw log.]"
                )
                result["signature"] = None
            return result
        return value

    logs = sorted((run / "logs").glob("*.eval"))
    if logs and not (run / "trajectory.json").exists():
        log = read_eval_log(str(logs[0]))
        if log.samples:
            encoded = json.dumps(
                {"messages": public([m.model_dump(mode="json") for m in log.samples[0].messages])},
                indent=2,
            )
            import re

            if re.search(r"sk-[A-Za-z0-9_-]{20,}", encoded):
                raise ValueError("Potential secret in visible trace; export refused")
            (run / "trajectory.json").write_text(encoded)


def report(run: Path) -> Path:
    export_trace(run)
    review = assess(run)
    manifest = read(run, "manifest.json", {})
    summary = read(run, "summary.json", {})
    diagnosis = read(run, "diagnosis.json", {})
    manual = review.get("manual_review") or {}
    rows = []
    for qid, item in review["questions"].items():
        candidate = item["candidate"] or {}
        decision = manual.get("questions", {}).get(qid, {})
        support = decision.get("support", "Needs review")
        if decision:
            support += (
                f" ({manual['reviewer_kind']}: {manual['reviewer']}) — {decision['rationale']}"
            )
        links = "<br>".join(evidence_link(run, ev) for ev in candidate.get("evidence", []))
        rows.append(
            f"<tr><td>{escape(qid)}: {escape(item['question'])}</td><td>{escape(candidate.get('value', 'No candidate'))}</td><td>{escape(support)}<br><small>Citation valid: {item['citation_valid']}; successful execution provenance: {item['successful_execution_provenance']}</small></td><td>{escape(item['correct'] if item['correct'] is not None else 'Not scored')}</td><td>{links}</td></tr>"
        )
    steps = "".join(
        f"<tr><td>{escape(e.get('execution_id', ''))}</td><td>{escape(e.get('path', ''))} {escape(e.get('mode', ''))}</td><td>{escape(e.get('status'))}</td></tr>"
        for e in review["execution"]["events"]
    )
    partial = (
        "<br>".join(evidence_link(run, {"artifact": name}) for name in review["partial_artifacts"])
        or "None recorded."
    )
    findings = "".join(
        "<li>"
        + escape(c["label"] + " / " + c["stage"])
        + ": "
        + " ".join(
            evidence_link(run, e) if isinstance(e, dict) else escape(e) for e in c["evidence"]
        )
        + "</li>"
        for c in diagnosis.get("contributors", [])
    )
    lessons = read(run, "lessons-snapshot.json", [])
    lesson_text = (
        "".join(
            f"<details><summary>{escape(r['id'])} — approved by {escape(r.get('reviewer'))}</summary><p>Source: {escape(r['source_run'])}; evidence: {escape(r['evidence'])}; content SHA-256: {escape(r['approved_sha256'])}</p><pre>{escape(r['content'])}</pre></details>"
            for r in lessons
        )
        or "<p>No lessons loaded.</p>"
    )
    raw = "".join(
        f"<details><summary>{escape(name)}</summary><pre>{escape(json.dumps(value, indent=2))}</pre></details>"
        for name, value in [
            ("Assessment", review),
            ("Diagnosis", diagnosis),
            ("Summary", summary),
            ("Source changes", review["source_changes"]),
        ]
    )
    body = f"""<h1>ReproScout · Reproduction review</h1><p>{escape(manifest.get("title", run.name))}</p>
<p><strong>{escape(review["outcome"].upper())}</strong> · {escape(review["scoring"])} · {summary.get("model_calls", 0)} model calls · {summary.get("seconds", 0):.1f} seconds · ${summary.get("cost_estimated_usd", 0):.4f} estimated</p>
<p>Prepared author environment. Execution completion, semantic support, source integrity, and answer correctness are separate assessments.</p>
<section><h2>Questions and candidate evidence</h2><table><tr><th>Question</th><th>Candidate</th><th>Review</th><th>Optional score</th><th>Evidence</th></tr>{"".join(rows)}</table></section>
<section><h2>Execution steps</h2><table><tr><th>Execution</th><th>Original file / mode</th><th>Status</th></tr>{steps}</table><h3>Partial output</h3><p>Output from failed executions remains candidate evidence; it is not verified as a completed computation.</p>{partial}</section>
<section><h2>Diagnosis and next actions</h2><p>{escape(diagnosis.get("primary_cause", "Unknown"))}</p><ul>{findings}</ul><p>{escape(diagnosis.get("note", ""))}</p><ol>{"".join("<li>" + escape(x) + "</li>" for x in diagnosis.get("next_actions", []))}</ol></section>
<section><h2>Input and source integrity</h2><p>{escape(review["source_change_interpretation"])}</p><pre>{escape(json.dumps(review["source_changes"], indent=2))}</pre></section>
<section><h2>Loaded lessons</h2>{lesson_text}<p>Loading a rule does not demonstrate compliance or benefit. Compare its action with the recorded execution steps and full trace.</p></section>
<section><h2>Review limitations</h2><ul>{"".join("<li>" + escape(x) + "</li>" for x in review["limitations"])}</ul></section>
<h2>Audit records</h2><p><a href="manifest.json">Manifest</a> · <a href="artifact-index.json">Artifact index</a> · <a href="review-assessment.json">Review JSON</a></p>{raw}"""
    if (run / "trajectory.json").exists():
        body += (
            "<details><summary>Full execution trace</summary><pre>"
            + escape((run / "trajectory.json").read_text())
            + "</pre></details>"
        )
    destination = run / "report.html"
    destination.write_text(document("ReproScout review", body))
    return destination
