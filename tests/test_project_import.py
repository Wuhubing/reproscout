import io
import json
import tarfile
import zipfile

import pytest

from reproscout.project_import import decode_bundle
from reproscout.tasks import digest
from reproscout.web import Workspace


def bundle(task="new-project", name="code/main.py", payload=b"print(42)\n", inventory=None):
    out = io.BytesIO()
    with tarfile.open(fileobj=out, mode="w") as archive:
        entry = tarfile.TarInfo(name)
        entry.size = len(payload)
        archive.addfile(entry, io.BytesIO(payload))
    prepared = out.getvalue()
    manifest = {
        "task_id": task,
        "title": "New upstream project",
        "split": "user_project",
        "questions": {"q1": "Printed value?"},
        "answer_types": {"q1": "number"},
        "task_prompt": "Run the original code.",
        "prepared_path": "prepared.tar",
        "prepared_sha256": digest(prepared),
        "image": "example@sha256:" + "a" * 64,
        "input_inventory": inventory
        if inventory is not None
        else [{"path": name, "sha256": digest(payload)}],
    }
    output = io.BytesIO()
    with zipfile.ZipFile(output, "w") as z:
        z.writestr("manifest.json", json.dumps(manifest))
        z.writestr("prepared.tar", prepared)
    return output.getvalue()


def test_bundle_import_copies_inputs_without_rewriting_science(tmp_path):
    workspace = Workspace(tmp_path)
    body = bundle()
    original, prepared, _ = decode_bundle(body)
    result = workspace.import_bundle(body)
    stored = workspace.project(result["id"])
    assert stored["prepared_path"] == "data/imports/new-project/prepared.tar"
    assert (tmp_path / stored["prepared_path"]).read_bytes() == prepared
    assert stored["input_inventory"] == original["input_inventory"]
    assert stored["import_provenance"]["bundle_sha256"] == digest(body)
    with pytest.raises(ValueError, match="already exists"):
        workspace.import_bundle(body)
    assert (tmp_path / stored["prepared_path"]).read_bytes() == prepared


@pytest.mark.parametrize(
    "name",
    [
        "../code/main.py",
        "/code/main.py",
        "results/precomputed.txt",
        "code/../../outside",
        "code\\main.py",
        "code/./main.py",
        "code//main.py",
    ],
)
def test_unsafe_archive_paths_are_rejected(name):
    with pytest.raises(ValueError):
        decode_bundle(bundle(name=name))


def test_inventory_mismatch_and_invalid_manifest_leave_no_partial_project(tmp_path):
    with pytest.raises(ValueError, match="checksum"):
        decode_bundle(bundle(inventory=[{"path": "code/main.py", "sha256": "0" * 64}]))
    workspace = Workspace(tmp_path)
    body = bundle()
    raw = io.BytesIO()
    with zipfile.ZipFile(io.BytesIO(body)) as old, zipfile.ZipFile(raw, "w") as new:
        manifest = json.loads(old.read("manifest.json"))
        manifest["split"] = "official_test"
        new.writestr("manifest.json", json.dumps(manifest))
        new.writestr("prepared.tar", old.read("prepared.tar"))
    with pytest.raises(ValueError, match="accepts"):
        workspace.import_bundle(raw.getvalue())
    assert not workspace.projects()
    assert not (tmp_path / "data/imports/new-project").exists()


def test_bundle_does_not_accept_extra_zip_entries():
    body = io.BytesIO(bundle())
    with zipfile.ZipFile(body, "a") as z:
        z.writestr("../extra", "x")
    with pytest.raises(ValueError, match="exactly"):
        decode_bundle(body.getvalue())
