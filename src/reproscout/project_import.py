"""Validate portable prepared projects without extracting untrusted archive paths."""

import io
import json
import re
import tarfile
import zipfile
from pathlib import PurePosixPath

from .tasks import digest

MAX_UPLOAD = 50 * 1024 * 1024
MAX_PREPARED = 128 * 1024 * 1024


def validate_prepared(body: bytes, inventory):
    if len(body) > MAX_PREPARED:
        raise ValueError("Prepared archive exceeds the 128 MiB limit")
    if not isinstance(inventory, list) or not inventory:
        raise ValueError("A nonempty input inventory is required")
    expected = {}
    for entry in inventory:
        if (
            not isinstance(entry, dict)
            or not isinstance(entry.get("path"), str)
            or not re.fullmatch(r"[a-f0-9]{64}", str(entry.get("sha256", "")))
        ):
            raise ValueError("Every inventory entry needs a path and SHA-256")
        if entry["path"] in expected:
            raise ValueError("Duplicate inventory path")
        expected[entry["path"]] = entry["sha256"]
    seen = set()
    total = 0
    try:
        with tarfile.open(fileobj=io.BytesIO(body), mode="r:") as archive:
            for member in archive:
                name = member.name
                path = PurePosixPath(name)
                if (
                    path.is_absolute()
                    or ".." in path.parts
                    or "\\" in name
                    or not path.parts
                    or name.rstrip("/") != path.as_posix()
                ):
                    raise ValueError("Unsafe path in prepared archive")
                allowed = (
                    path.parts[0] in ("code", "data", "environment") or name == "REPRODUCING.md"
                )
                if not allowed:
                    raise ValueError(
                        "Prepared inputs must stay in code/, data/, environment/, or REPRODUCING.md"
                    )
                if member.isdir():
                    continue
                if not member.isfile() or member.issym() or member.islnk():
                    raise ValueError(
                        "Only regular files and directories are accepted; archive links are rejected"
                    )
                if name in seen or name not in expected:
                    raise ValueError(
                        "Archive files must match the inventory exactly, without duplicates"
                    )
                seen.add(name)
                total += member.size
                if total > MAX_PREPARED or len(seen) > 10000:
                    raise ValueError("Expanded input limits exceeded")
                stream = archive.extractfile(member)
                if digest(stream.read()) != expected[name]:
                    raise ValueError(f"Input checksum mismatch: {name}")
    except tarfile.TarError as exc:
        raise ValueError("prepared.tar must be a valid uncompressed tar archive") from exc
    if seen != set(expected):
        raise ValueError("Inventory includes files missing from the archive")


def decode_bundle(body: bytes):
    if len(body) > MAX_UPLOAD:
        raise ValueError("Project ZIP exceeds the 50 MiB upload limit")
    try:
        with zipfile.ZipFile(io.BytesIO(body)) as archive:
            entries = archive.infolist()
            if len(entries) != 2 or {e.filename for e in entries} != {
                "manifest.json",
                "prepared.tar",
            }:
                raise ValueError(
                    "ZIP must contain exactly manifest.json and prepared.tar at its root"
                )
            if (
                archive.getinfo("manifest.json").file_size > 500_000
                or archive.getinfo("prepared.tar").file_size > MAX_PREPARED
            ):
                raise ValueError("Project manifest or prepared archive exceeds its size limit")
            raw_manifest = archive.read("manifest.json")
            manifest = json.loads(raw_manifest)
            if not isinstance(manifest, dict):
                raise ValueError("Manifest must be a JSON object")
            prepared = archive.read("prepared.tar")
    except (zipfile.BadZipFile, RuntimeError, UnicodeError) as exc:
        raise ValueError("Cannot read project ZIP; use an unencrypted ZIP bundle") from exc
    if digest(prepared) != manifest.get("prepared_sha256"):
        raise ValueError("Prepared archive checksum does not match the manifest")
    validate_prepared(prepared, manifest.get("input_inventory"))
    return manifest, prepared, raw_manifest
