"""Explicit, hash-approved lessons; no evaluation-run learning."""

import hashlib
import json
import re
import time
from pathlib import Path

from .review import read
from .tasks import write_json


def content_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def lesson_path(directory, lesson_id):
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,79}", lesson_id):
        raise ValueError("Lesson ID must be a safe lowercase identifier")
    return directory / (lesson_id + ".json")


def transition(directory, record, action, previous=None, content=None):
    write_json(
        directory / "history" / record["id"] / f"{time.time_ns()}.json",
        {
            "action": action,
            "record": record,
            "previous": previous,
            "content": content,
            "recorded_at_unix_ns": time.time_ns(),
        },
    )


def edit(directory, lesson_id, content):
    path = lesson_path(directory, lesson_id)
    record = json.loads(path.read_text())
    previous = path.with_suffix(".md").read_text()
    path.with_suffix(".md").write_text(content)
    transition(directory, record, "edit", {"content": previous}, content)


def propose(
    directory: Path, source: Path, lesson_id: str, action: str, applicability: str, evidence: str
):
    manifest = read(source, "manifest.json", {})
    if manifest.get("split") not in ("official_train", "development", "train", "user_project"):
        raise ValueError("Lessons may only originate from development, training, or user projects")
    p = (source / evidence).resolve()
    if not p.is_relative_to((source / "artifacts").resolve()) or not p.is_file():
        raise ValueError("Evidence must be a retained artifact, never a private reference")
    path = lesson_path(directory, lesson_id)
    if path.exists():
        raise ValueError("Lesson ID already exists")
    directory.mkdir(parents=True, exist_ok=True)
    md = path.with_suffix(".md")
    md.write_text(f"# {lesson_id}\n\nApplicability: {applicability}\n\nAction: {action}\n")
    record = {
        "id": lesson_id,
        "source_run": source.name,
        "source_split": manifest["split"],
        "evidence": evidence,
        "evidence_sha256": content_hash(p),
        "status": "proposed",
        "approved_sha256": None,
    }
    write_json(path, record)
    transition(directory, record, "propose", content=md.read_text())
    return record


def change(directory, lesson_id, status, reviewer):
    path = lesson_path(directory, lesson_id)
    record = json.loads(path.read_text())
    previous = dict(record)
    record.update(
        status=status,
        reviewer=reviewer,
        approved_sha256=content_hash(path.with_suffix(".md")) if status == "approved" else None,
    )
    write_json(path, record)
    transition(directory, record, status, previous, path.with_suffix(".md").read_text())
    return record


def snapshot(directory, ids, run):
    records = []
    for lesson_id in ids:
        path = lesson_path(directory, lesson_id)
        record = json.loads(path.read_text())
        if record["status"] != "approved":
            raise ValueError(f"Lesson {lesson_id} is not approved")
        if record["approved_sha256"] != content_hash(path.with_suffix(".md")):
            raise ValueError(f"Lesson {lesson_id} changed after approval")
        records.append({**record, "content": path.with_suffix(".md").read_text()})
    if (run / "lessons-snapshot.json").exists():
        raise ValueError("Run lesson snapshot already exists and is immutable")
    write_json(run / "lessons-snapshot.json", records)
    return "\n\n".join(r["content"] for r in records)
