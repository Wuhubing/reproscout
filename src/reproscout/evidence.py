"""Validate references to controller-owned, immutable tool output snapshots."""

from __future__ import annotations

import json
from pathlib import Path


def validate_submission(payload: str, questions: dict, artifacts: dict, root: Path) -> dict:
    result = json.loads(payload)
    if not isinstance(result, dict) or set(result) != set(questions):
        raise ValueError("Submit exactly the question IDs supplied in the task")
    for qid, answer in result.items():
        if not isinstance(answer, dict) or "value" not in answer or not answer.get("evidence"):
            raise ValueError(f"{qid}: value and nonempty evidence are required")
        for reference in answer["evidence"]:
            artifact = reference.get("artifact")
            if artifact not in artifacts:
                raise ValueError("Evidence must reference an artifact returned by a tool")
            if artifacts[artifact].get("kind") == "image":
                if not (root / artifact).is_file():
                    raise ValueError("Missing image evidence")
                continue
            lines = (root / artifact).read_text(encoding="utf-8").splitlines()
            start, end = reference.get("line_start"), reference.get("line_end")
            if (
                type(start) is not int
                or type(end) is not int
                or not 1 <= start <= end <= len(lines)
            ):
                raise ValueError("Invalid evidence line range")
    return result
