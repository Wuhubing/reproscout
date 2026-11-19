"""Behavior checks for local workspace boundaries, review versions, and blocker stops."""

import json
import threading
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer

import pytest

from reproscout.blockers import before_generation, detect_offline_blocker
from reproscout.review import assess
from reproscout.tasks import write_json
from reproscout.web import Workspace, handler


def workspace_fixture(tmp_path):
    root = tmp_path
    source = root / "reports/product-runs/dev-run"
    (source / "artifacts").mkdir(parents=True)
    (source / "artifacts/output.txt").write_text("Accuracy: 95%\n")
    write_json(
        source / "manifest.json",
        {
            "task_id": "fixture",
            "title": "Fixture",
            "questions": {"q1": "Accuracy?"},
            "split": "official_train",
        },
    )
    write_json(source / "summary.json", {"seconds": 1, "evaluation": {}})
    write_json(
        source / "submission.json",
        {
            "q1": {
                "value": 95,
                "evidence": [{"artifact": "artifacts/output.txt", "line_start": 1, "line_end": 1}],
            }
        },
    )
    write_json(source / "execution-ledger.json", [{"status": "succeeded", "execution_id": 1}])
    write_json(
        source / "artifact-index.json",
        {
            "artifacts/output.txt": {
                "kind": "command_stdout",
                "verified_execution": True,
                "execution_id": 1,
            }
        },
    )
    assess(source)
    return Workspace(root), source


def test_blocker_requires_actual_stderr_signature_and_preserves_evidence(tmp_path):
    (tmp_path / "artifacts").mkdir()
    path = tmp_path / "artifacts/error.txt"
    path.write_text("URLError: <urlopen error [Errno -3] Temporary failure in name resolution>\n")
    artifacts = {"artifacts/error.txt": {"kind": "file_snapshot", "execution_id": 1}}
    assert detect_offline_blocker(tmp_path, artifacts, 1) is None
    artifacts["artifacts/error.txt"]["kind"] = "command_stderr"
    result = detect_offline_blocker(tmp_path, artifacts, 1)
    assert result["evidence"][0]["line_start"] == 1
    before_generation(tmp_path)
    before_generation(tmp_path)
    with pytest.raises(ValueError, match="Known offline blocker"):
        before_generation(tmp_path)
    assert not (tmp_path / "submission.json").exists()


def test_generic_error_and_success_do_not_trigger_network_stop(tmp_path):
    path = tmp_path / "error.txt"
    path.write_text("ValueError: shapes not aligned\n")
    assert (
        detect_offline_blocker(
            tmp_path, {"error.txt": {"kind": "command_stderr", "execution_id": 1}}, 1
        )
        is None
    )
    path.write_text("URLError: Network is unreachable\n")
    assert (
        detect_offline_blocker(
            tmp_path, {"error.txt": {"kind": "command_stdout", "execution_id": 1}}, 1
        )
        is None
    )
    (tmp_path / "cancel.requested").touch()
    with pytest.raises(ValueError, match="cancelled"):
        before_generation(tmp_path)


def test_review_versions_preserve_identity_and_original_bytes(tmp_path):
    workspace, source = workspace_fixture(tmp_path)
    original = {
        str(p.relative_to(source)): p.read_bytes() for p in source.rglob("*") if p.is_file()
    }

    def record(name, support):
        return {
            "reviewer": name,
            "reviewer_kind": "assistant",
            "questions": {
                "q1": {
                    "support": support,
                    "rationale": "The accuracy is reported on a percentage scale.",
                    "evidence": [
                        {"artifact": "artifacts/output.txt", "line_start": 1, "line_end": 1}
                    ],
                }
            },
        }

    workspace.review("dev-run", record("assistant:first", "uncertain"))
    workspace.review("dev-run", record("assistant:second", "supported"))
    details = workspace.details("dev-run")
    assert [r["reviewer"] for r in details["reviews"]] == ["assistant:first", "assistant:second"]
    assert workspace.runs()[0]["reviewed"] == 1
    assert workspace.export("dev-run").startswith(b"PK")
    for name, contents in original.items():
        assert (source / name).read_bytes() == contents


def test_artifact_escape_and_unregistered_files_rejected(tmp_path):
    workspace, _ = workspace_fixture(tmp_path)
    with pytest.raises(ValueError, match="Unknown retained artifact"):
        workspace.evidence("dev-run", "../../private/secret")
    with pytest.raises(ValueError, match="Invalid identifier"):
        workspace.source("../dev-run")


def test_same_origin_write_protection_and_host_validation(tmp_path):
    workspace, _ = workspace_fixture(tmp_path)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler(workspace))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"
    try:
        boot = json.load(urllib.request.urlopen(base + "/api/bootstrap"))
        assert boot["csrf"] == workspace.token
        request = urllib.request.Request(
            base + "/api/runs", data=b"{}", headers={"Content-Type": "application/json"}
        )
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request)
        assert error.value.code == 403
        request = urllib.request.Request(
            base + "/api/bootstrap", headers={"Host": "attacker.invalid"}
        )
        with pytest.raises(urllib.error.HTTPError) as error:
            urllib.request.urlopen(request)
        assert error.value.code == 403
    finally:
        server.shutdown()
        server.server_close()


def test_cancel_is_explicit_and_keeps_run_files(tmp_path):
    workspace, source = workspace_fixture(tmp_path)
    local = tmp_path / "runs/dev-run"
    local.parent.mkdir()
    import shutil

    shutil.copytree(source, local)
    job = workspace.state / "jobs/job1"
    write_json(job / "job.json", {"id": "job1", "run_id": "dev-run", "status": "running"})
    result = workspace.cancel("job1")
    assert result["status"] == "cancelling"
    assert (local / "cancel.requested").exists()
    assert (local / "submission.json").exists()


def test_bad_review_does_not_replace_existing_view(tmp_path):
    workspace, source = workspace_fixture(tmp_path)
    with pytest.raises(ValueError):
        workspace.review(
            "dev-run",
            {
                "reviewer": "x",
                "reviewer_kind": "human",
                "questions": {
                    "q1": {
                        "support": "supported",
                        "rationale": "x",
                        "evidence": [{"artifact": "not-real"}],
                    }
                },
            },
        )
    assert workspace.reviewed_source("dev-run") == source


def test_quoted_exception_text_does_not_trigger_stop(tmp_path):
    (tmp_path / "error.txt").write_text("    print('URLError: Network is unreachable')\n")
    assert (
        detect_offline_blocker(
            tmp_path, {"error.txt": {"kind": "command_stderr", "execution_id": 1}}, 1
        )
        is None
    )


def test_lesson_transition_history_is_append_only(tmp_path):
    from reproscout.lessons import change, edit, propose

    workspace, source = workspace_fixture(tmp_path)
    registry = workspace.registry
    propose(
        registry,
        source,
        "history",
        "Inspect the metric.",
        "Printed outputs",
        "artifacts/output.txt",
    )
    change(registry, "history", "approved", "assistant:first")
    first = {p: p.read_bytes() for p in (registry / "history/history").glob("*.json")}
    edit(registry, "history", "Changed guidance")
    change(registry, "history", "disabled", "assistant:second")
    events = [
        json.loads(p.read_text()) for p in sorted((registry / "history/history").glob("*.json"))
    ]
    assert [e["action"] for e in events] == ["propose", "approved", "edit", "disabled"]
    assert events[1]["record"]["reviewer"] == "assistant:first"
    for path, contents in first.items():
        assert path.read_bytes() == contents
