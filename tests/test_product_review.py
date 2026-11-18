import json

import pytest

from reproscout.diagnosis import diagnose
from reproscout.lessons import change, propose, snapshot
from reproscout.reporting import report
from reproscout.review import assess, import_review
from reproscout.tasks import write_json


def fixture_run(tmp_path, success=True):
    run = tmp_path / "run"
    (run / "artifacts").mkdir(parents=True)
    (run / "artifacts/output.txt").write_text("Mean: 0.5\nMedian: 0.4\n")
    write_json(
        run / "manifest.json",
        {"title": "Study", "split": "official_train", "questions": {"q1": "Median?"}},
    )
    write_json(
        run / "summary.json", {"evaluation": {"question_correct": {"q1": True}}, "seconds": 1}
    )
    write_json(
        run / "artifact-index.json",
        {
            "artifacts/output.txt": {
                "kind": "text",
                "execution_id": 1,
                "verified_execution": success,
            }
        },
    )
    write_json(
        run / "execution-ledger.json",
        [{"execution_id": 1, "status": "succeeded" if success else "failed"}],
    )
    write_json(
        run / "submission.json",
        {
            "q1": {
                "value": 0.4,
                "evidence": [{"artifact": "artifacts/output.txt", "line_start": 1, "line_end": 1}],
            }
        },
    )
    return run


def test_correct_answer_is_not_semantic_support(tmp_path):
    run = fixture_run(tmp_path)
    result = assess(run)
    assert result["outcome"] == "completed"
    assert result["questions"]["q1"]["correct"] is True
    assert result["questions"]["q1"]["semantic_support"] == "needs_review"
    html = report(run).read_text()
    assert "output.txt.html#L1" in html
    assert 'id="L1"' in (run / "artifacts/output.txt.html").read_text()


def test_partial_output_never_promoted(tmp_path):
    run = fixture_run(tmp_path, False)
    result = assess(run)
    assert result["outcome"] == "blocked"
    assert result["partial_artifacts"] == ["artifacts/output.txt"]
    assert not result["questions"]["q1"]["successful_execution_provenance"]


def test_no_key_no_submission_broken_citation(tmp_path):
    run = fixture_run(tmp_path)
    write_json(run / "summary.json", {})
    (run / "submission.json").unlink()
    assert assess(run)["scoring"] == "Not scored"
    assert assess(run)["outcome"] == "partial"
    write_json(
        run / "submission.json",
        {
            "q1": {
                "value": 1,
                "evidence": [
                    {"artifact": "artifacts/output.txt", "line_start": 999, "line_end": 999}
                ],
            }
        },
    )
    assert not assess(run)["questions"]["q1"]["citation_valid"]


def test_diagnosis_not_short_circuited_by_score(tmp_path):
    run = fixture_run(tmp_path)
    write_json(run / "summary.json", {"evaluation": {"solved": True}, "limit": {"type": "model"}})
    (run / "artifacts/error.txt").write_text("URLError: Network is unreachable\n")
    result = diagnose(run)
    assert [x["label"] for x in result["contributors"]] == ["environment", "budget_exhausted"]


def test_lesson_lifecycle_and_eval_refusal(tmp_path):
    run = fixture_run(tmp_path)
    directory = tmp_path / "registry"
    propose(
        directory, run, "inspect", "Inspect outputs.", "Original scripts", "artifacts/output.txt"
    )
    with pytest.raises(ValueError, match="not approved"):
        snapshot(directory, ["inspect"], run)
    change(directory, "inspect", "approved", "assistant:development-review")
    assert "Inspect outputs" in snapshot(directory, ["inspect"], run)
    frozen = (run / "lessons-snapshot.json").read_text()
    (directory / "inspect.md").write_text("Changed instruction")
    with pytest.raises(ValueError, match="changed after approval"):
        snapshot(directory, ["inspect"], run)
    assert (run / "lessons-snapshot.json").read_text() == frozen
    change(directory, "inspect", "disabled", "assistant:development-review")
    with pytest.raises(ValueError, match="not approved"):
        snapshot(directory, ["inspect"], run)
    write_json(run / "manifest.json", {"split": "official_test"})
    with pytest.raises(ValueError, match="only originate"):
        propose(directory, run, "eval", "x", "y", "artifacts/output.txt")


def test_attributed_review_requires_evidence(tmp_path):
    run = fixture_run(tmp_path)
    path = tmp_path / "review.json"
    data = {
        "run_id": run.name,
        "reviewer": "assistant:qa",
        "reviewer_kind": "assistant",
        "questions": {
            "q1": {
                "support": "unsupported",
                "rationale": "Mean does not answer median.",
                "evidence": [{"artifact": "artifacts/output.txt", "line_start": 1, "line_end": 1}],
            }
        },
    }
    write_json(path, data)
    result = import_review(run, path)
    assert result["manual_review"]["reviewer_kind"] == "assistant"
    with pytest.raises(ValueError, match="already imported"):
        import_review(run, path)


def test_historical_render_failure_retains_changed_inputs_and_candidates(tmp_path):
    import shutil
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[1]
        / "reports/runs/20261118T190037740789Z-capsule-3262218-run-B2"
    )
    run = tmp_path / "historical-regression-copy"
    run.mkdir()
    for name in (
        "manifest.json",
        "summary.json",
        "submission.json",
        "artifact-index.json",
        "execution-ledger.json",
        "source-audit.json",
    ):
        shutil.copyfile(source / name, run / name)
    shutil.copytree(source / "artifacts", run / "artifacts")
    result = assess(run)
    assert result["source_changes"]["unchanged"] is False
    assert len(result["source_changes"]["changed_or_missing"]) == 6
    assert result["partial_artifacts"]
    assert result["rejected_submissions"]
    assert all(q["semantic_support"] == "needs_review" for q in result["questions"].values())


def test_runtime_exception_still_emits_report_and_missing_key_is_config_error(
    tmp_path, monkeypatch
):
    from pathlib import Path

    import inspect_ai

    from reproscout.cli import execute
    from reproscout.tasks import digest

    root = Path(__file__).resolve().parents[1]
    (tmp_path / "configs").mkdir()
    (tmp_path / "configs/pilot.json").write_text((root / "configs/pilot.json").read_text())
    prepared = tmp_path / "input.tar"
    prepared.write_bytes(b"fixture-input")
    manifest = {
        "task_id": "fixture",
        "title": "Fixture",
        "task_prompt": "Run original code",
        "split": "development",
        "questions": {"q1": "Count?"},
        "answer_types": {"q1": "number"},
        "prepared_path": "input.tar",
        "prepared_sha256": digest(prepared.read_bytes()),
        "image": "unused-fixture",
        "input_inventory": [],
    }
    path = tmp_path / "manifest.json"
    write_json(path, manifest)
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder")

    def fail(*args, **kwargs):
        raise RuntimeError("simulated framework startup failure")

    monkeypatch.setattr(inspect_ai, "eval", fail)
    run = execute(tmp_path, "run", None, path)
    assert (run / "report.html").is_file()
    assert json.loads((run / "summary.json").read_text())["infrastructure_failure"] is True
    assert assess(run)["scoring"] == "Not scored"
    manifest["answers_path"] = "missing-reference.json"
    write_json(path, manifest)
    with pytest.raises(FileNotFoundError):
        execute(tmp_path, "run", None, path)
