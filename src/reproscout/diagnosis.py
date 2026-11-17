"""Conservative operational failure labels with explicit uncertainty."""

import json
from pathlib import Path

from .tasks import write_json


def diagnose(run: Path) -> dict:
    summary = json.loads((run / "summary.json").read_text())
    if summary.get("evaluation", {}).get("solved"):
        result = {
            "label": None,
            "status": "solved",
            "evidence": ["summary.json"],
            "human_confirmed": False,
            "note": "No failed reproduction to classify.",
        }
    else:
        files = sorted((run / "artifacts").glob("*.txt"))
        labels = [
            (
                "environment",
                [
                    "Temporary failure in name resolution",
                    "Network is unreachable",
                    "ModuleNotFoundError",
                    "ImportError",
                    "there is no package called",
                    "command not found",
                    "cannot open shared object",
                ],
            ),
            ("code_error", ["Traceback (most recent call last)", "Error in ", "Execution halted"]),
        ]
        result = {
            "label": "output_error",
            "status": "provisional",
            "evidence": ["summary.json"],
            "human_confirmed": False,
            "note": "No fully correct submitted output. This is a symptom, not proof of root cause.",
        }
        for label, markers in labels:
            matched = [
                str(p.relative_to(run))
                for p in files
                if any(m in p.read_text(errors="replace") for m in markers)
            ]
            if matched:
                result.update(
                    label=label,
                    evidence=matched,
                    note="Trace signature suggests this category; independent review is required.",
                )
                break
        timed_out = []
        for p in run.glob("step-*.json"):
            if json.loads(p.read_text()).get("status") == "timeout":
                timed_out.append(p.name)
        if (
            summary.get("limit")
            or timed_out
            or "limit" in str(summary.get("sample_error", "")).lower()
        ):
            result.update(
                label="budget_exhausted",
                evidence=timed_out or ["summary.json"],
                note="A configured execution limit was reached; earlier contributing failures may exist.",
            )
    write_json(run / "diagnosis.json", result)
    return result
