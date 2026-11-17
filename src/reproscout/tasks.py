"""Prepare an official development task without importing a benchmark package."""

from __future__ import annotations

import hashlib
import io
import json
import tarfile
from pathlib import Path, PurePosixPath

import httpx

UPSTREAM_COMMIT = "e32a2980e72fe6eb04ee04eb749458f570625663"
TRAIN_URL = (
    f"https://raw.githubusercontent.com/siegelz/core-bench/{UPSTREAM_COMMIT}"
    "/benchmark/dataset/core_train.json"
)
TRAIN_SHA = "3df47f1b3fa1cb60045018eb1a0f1ad4ecf6a53f72318c845a879ce0313b0730"
CAPSULE_ID = "capsule-6460826"
CAPSULE_URL = f"https://corebench.cs.princeton.edu/capsules/{CAPSULE_ID}.tar.gz"
CAPSULE_SHA = "36e6fe89a288dc66a167c055bd21965cdbd053f87217d6fc9e00642af0445664"
IMAGE = (
    "registry.codeocean.com/published/0609cc4f-8b95-4d94-8fd0-9456d262b3a5"
    "@sha256:8627797e74cc92c24dff1abec45d299f62b842f41630be4d0a87421df24c3a5e"
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")


def verified_download(url: str, expected: str, destination: Path) -> bytes:
    if destination.exists():
        data = destination.read_bytes()
    else:
        response = httpx.get(url, timeout=120, follow_redirects=True)
        response.raise_for_status()
        data = response.content
    if digest(data) != expected:
        raise ValueError(f"Checksum mismatch: {destination.name}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
    return data


def sanitized_archive(data: bytes) -> tuple[bytes, list[dict]]:
    """Allow regular code/data/environment files only; exclude supplied results."""
    output = io.BytesIO()
    inventory = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as source:
        with tarfile.open(fileobj=output, mode="w") as target:
            for member in source.getmembers():
                path = PurePosixPath(member.name)
                if path.is_absolute() or ".." in path.parts:
                    raise ValueError("Unsafe archive path")
                if member.issym() or member.islnk():
                    raise ValueError("Archive links are not allowed")
                if not member.isfile():
                    continue
                relative = PurePosixPath(*path.parts[1:])
                if not relative.parts or relative.parts[0] not in {
                    "code",
                    "data",
                    "environment",
                    "REPRODUCING.md",
                }:
                    continue
                if relative.name == ".DS_Store":
                    continue
                stream = source.extractfile(member)
                assert stream is not None
                body = stream.read()
                original_sha = digest(body)
                if relative.suffix == ".ipynb":
                    notebook = json.loads(body)
                    for cell in notebook.get("cells", []):
                        if cell.get("cell_type") == "code":
                            cell["outputs"] = []
                            cell["execution_count"] = None
                    body = json.dumps(notebook, ensure_ascii=True).encode()
                entry = tarfile.TarInfo(str(relative))
                entry.size = len(body)
                entry.mode = 0o755 if member.mode & 0o111 else 0o644
                target.addfile(entry, io.BytesIO(body))
                inventory.append(
                    {
                        "path": str(relative),
                        "sha256": digest(body),
                        "upstream_sha256": original_sha,
                        "bytes": len(body),
                    }
                )
    return output.getvalue(), inventory


def prepare(root: Path) -> dict:
    train = verified_download(TRAIN_URL, TRAIN_SHA, root / "private/core_train.json")
    records = json.loads(train)
    record = next(item for item in records if item["capsule_id"] == CAPSULE_ID)
    archive = verified_download(CAPSULE_URL, CAPSULE_SHA, root / f"data/{CAPSULE_ID}.tar.gz")
    safe, inventory = sanitized_archive(archive)
    (root / "data/prepared.tar").write_bytes(safe)
    questions = {f"q{i}": q for i, q in enumerate(record["results"][0], 1)}
    manifest = {
        "task_id": CAPSULE_ID,
        "split": "official_train",
        "language": "Python",
        "title": record["capsule_title"],
        "doi": record["capsule_doi"],
        "task_prompt": record["task_prompt"],
        "questions": questions,
        "source_commit": UPSTREAM_COMMIT,
        "dataset_url": TRAIN_URL,
        "dataset_sha256": TRAIN_SHA,
        "capsule_url": CAPSULE_URL,
        "capsule_sha256": CAPSULE_SHA,
        "prepared_sha256": digest(safe),
        "image": IMAGE,
        "platform": "linux/amd64",
        "mode": "prepared-environment development pilot; not unchanged CORE-Bench Medium",
        "selection_reason": "Small Python CPU classification example with text outputs and an archived author image.",
        "excluded_paths": ["results/", "metadata/", ".DS_Store", ".gitignore"],
        "input_inventory": inventory,
    }
    write_json(root / "manifests/pilot.json", manifest)
    write_json(root / "private/pilot_answers.json", record["results"])
    return manifest
