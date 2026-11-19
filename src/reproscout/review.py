"""Conservative, score-independent review records and attributed review imports."""

import json
from pathlib import Path

from .evidence import validate_submission
from .tasks import write_json


def read(run, name, default=None):
    path = run / name
    return json.loads(path.read_text()) if path.exists() else default


def assess(run: Path) -> dict:
    summary = read(run, "summary.json", {})
    manifest = read(run, "manifest.json", {})
    answers = read(run, "submission.json", {})
    artifacts = read(run, "artifact-index.json", {})
    ledger = read(run, "execution-ledger.json", [])
    terminal = [
        e for e in ledger if e.get("status") in ("succeeded", "failed", "failed_or_timeout")
    ]
    succeeded = sum(e["status"] == "succeeded" for e in terminal)
    failed = len(terminal) - succeeded
    rejected = [
        e for e in ledger if e.get("operation") == "submit_report" and e.get("status") == "refused"
    ]
    questions = {}
    for qid, question in manifest.get("questions", {}).items():
        answer = answers.get(qid)
        valid = False
        error = None
        if answer:
            try:
                validate_submission(json.dumps({qid: answer}), {qid: question}, artifacts, run)
                valid = True
            except (ValueError, OSError, TypeError) as exc:
                error = str(exc)
        provenance = bool(
            valid
            and all(
                artifacts[e["artifact"]].get("verified_execution") is True
                for e in answer["evidence"]
            )
        )
        questions[qid] = {
            "question": question,
            "candidate": answer,
            "citation_valid": valid,
            "citation_error": error,
            "successful_execution_provenance": provenance,
            "semantic_support": "needs_review",
            "correct": summary.get("evaluation", {}).get("question_correct", {}).get(qid),
        }
    complete = bool(
        terminal
        and not failed
        and answers
        and all(
            q["citation_valid"]
            and q["successful_execution_provenance"]
            and q["candidate"]["value"] is not None
            for q in questions.values()
        )
    )
    result = {
        "schema_version": "1.0",
        "run_id": run.name,
        "outcome": "cancelled"
        if (run / "cancel.requested").exists()
        else "completed"
        if complete
        else "partial"
        if succeeded
        else "blocked"
        if failed or summary.get("infrastructure_failure")
        else "failed",
        "execution": {"succeeded": succeeded, "failed": failed, "events": ledger},
        "questions": questions,
        "scoring": "scored" if summary.get("evaluation") else "Not scored",
        "source_changes": read(run, "source-audit.json", {}),
        "source_change_interpretation": "Changes require review of file role and execution provenance; a change alone does not establish agent tampering.",
        "rejected_submissions": rejected,
        "partial_artifacts": [
            k
            for k, v in artifacts.items()
            if v.get("execution_id") and v.get("verified_execution") is not True
        ],
        "limitations": [
            "Execution provenance does not establish metric, object, or unit agreement.",
            "All-chunk R Markdown execution may differ from native rendering context.",
            "Completed means execution and submission completed; semantic review is separate.",
        ],
        "manual_review": read(run, "manual-review.json", None),
        "review_history": read(run, "review-history.json", []),
        "blocker": read(run, "blocker.json", None),
    }
    write_json(run / "review-assessment.json", result)
    return result


def import_review(run: Path, path: Path):
    record = json.loads(path.read_text())
    if record.get("run_id") != run.name or not record.get("reviewer"):
        raise ValueError("Matching run_id and reviewer identity are required")
    if record.get("reviewer_kind") not in ("assistant", "human"):
        raise ValueError("reviewer_kind must be assistant or human")
    manifest = read(run, "manifest.json", {})
    artifacts = read(run, "artifact-index.json", {})
    for qid, item in record.get("questions", {}).items():
        if qid not in manifest["questions"] or item.get("support") not in (
            "supported",
            "unsupported",
            "uncertain",
        ):
            raise ValueError("Invalid question or support decision")
        if not item.get("rationale"):
            raise ValueError("A metric, object, and unit rationale is required")
        validate_submission(
            json.dumps({qid: {"value": None, "evidence": item.get("evidence")}}),
            {qid: manifest["questions"][qid]},
            artifacts,
            run,
        )
    if not record.get("questions"):
        raise ValueError("At least one reviewed question is required")
    target = run / "manual-review.json"
    if target.exists():
        raise ValueError("Review already imported; preserve it rather than overwrite attribution")
    write_json(target, record)
    return assess(run)
