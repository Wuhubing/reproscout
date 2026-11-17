import io
import json
import tarfile

import pytest

from reproscout.budget import Budget
from reproscout.evidence import validate_submission
from reproscout.scoring import score_answers
from reproscout.tasks import sanitized_archive


def archive(entries):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as tf:
        for name, content, kind in entries:
            info = tarfile.TarInfo(name)
            info.type = kind
            body = content.encode()
            info.size = len(body) if kind == tarfile.REGTYPE else 0
            if kind == tarfile.SYMTYPE:
                info.linkname = "/private/answers"
            tf.addfile(info, io.BytesIO(body) if info.size else None)
    return output.getvalue()


def test_preparation_excludes_supplied_results():
    safe, inventory = sanitized_archive(
        archive(
            [
                ("capsule/code/main.py", "print(1)", tarfile.REGTYPE),
                ("capsule/results/Output", "answer", tarfile.REGTYPE),
                ("capsule/metadata/metadata.yml", "metadata", tarfile.REGTYPE),
            ]
        )
    )
    assert [x["path"] for x in inventory] == ["code/main.py"]
    with tarfile.open(fileobj=io.BytesIO(safe)) as tf:
        assert tf.getnames() == ["code/main.py"]


@pytest.mark.parametrize(
    "name,kind",
    [
        ("capsule/../answers", tarfile.REGTYPE),
        ("/etc/passwd", tarfile.REGTYPE),
        ("capsule/code/link", tarfile.SYMTYPE),
    ],
)
def test_rejects_unsafe_archives(name, kind):
    with pytest.raises(ValueError):
        sanitized_archive(archive([(name, "x", kind)]))


def test_score_original_numeric_and_text_rules():
    references = [{"Accuracy.": 90, "Name": "Model A"}] * 3
    questions = {"q1": "Accuracy.", "q2": "Name"}
    assert score_answers(
        {"q1": {"value": "90%"}, "q2": {"value": "model a"}}, references, questions
    )["solved"]
    assert not score_answers(
        {"q1": {"value": 90.001}, "q2": {"value": "Model A."}}, references, questions
    )["solved"]
    assert not score_answers({}, references, questions)["solved"]
    assert not score_answers({"q1": {"value": "nan"}}, references, questions)["solved"]


def test_prediction_interval_not_just_reference_mean():
    references = [{"value": value} for value in [9, 10, 11]]
    questions = {"q1": "value"}
    assert score_answers({"q1": {"value": 14}}, references, questions)["solved"]
    assert not score_answers({"q1": {"value": 16}}, references, questions)["solved"]


def test_evidence_rejects_forged_and_out_of_range_references(tmp_path):
    (tmp_path / "output.txt").write_text("line 1\nline 2\n")
    payload = {
        "q1": {"value": 1, "evidence": [{"artifact": "output.txt", "line_start": 1, "line_end": 2}]}
    }
    assert validate_submission(
        json.dumps(payload), {"q1": "question"}, {"output.txt": {}}, tmp_path
    )
    payload["q1"]["evidence"][0]["line_end"] = 3
    with pytest.raises(ValueError):
        validate_submission(json.dumps(payload), {"q1": "question"}, {"output.txt": {}}, tmp_path)
    payload["q1"]["evidence"][0]["artifact"] = "../answers"
    with pytest.raises(ValueError):
        validate_submission(json.dumps(payload), {"q1": "question"}, {"output.txt": {}}, tmp_path)


def test_budget_denies_before_dispatch_and_retains_failed_reservation():
    b = Budget(limit=0.03)
    reservation = b.reserve(10)
    assert b.spent_upper == reservation
    with pytest.raises(ValueError):
        b.reserve(10)
    b.settle({"input_tokens": 100, "output_tokens": 20}, "test-model")
    assert b.spent_upper == pytest.approx((100 * 0.75 + 20 * 4.5) / 1e6)


def test_inspect_usage_reports_cached_tokens_separately():
    budget = Budget()
    budget.reserve(4000)
    budget.settle(
        {"input_tokens": 221, "input_tokens_cache_read": 1152, "output_tokens": 37}, "test-model"
    )
    assert budget.estimated_billed == pytest.approx(0.00041865)
    assert budget.spent_upper == pytest.approx(((221 + 1152) * 0.75 + 37 * 4.5) / 1e6)


def test_frozen_inputs_reject_edits_and_test_sources(tmp_path):
    from reproscout.experiment import freeze, verify_freeze
    from reproscout.tasks import write_json

    for d in ["src", "configs", "manifests", "runs/dev"]:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    (tmp_path / "src/agent.py").write_text("version = 1")
    (tmp_path / "uv.lock").write_text("locked")
    (tmp_path / "pyproject.toml").write_text("project")
    write_json(tmp_path / "manifests/cohort.json", {"development": ["dev"], "heldout": ["test"]})
    for task in ["dev", "test"]:
        write_json(tmp_path / f"manifests/{task}.json", {"task_id": task})
    write_json(tmp_path / "runs/dev/summary.json", {"split": "official_train"})
    lessons = tmp_path / "lessons.md"
    lessons.write_text("Read the entry point.")
    target = freeze(tmp_path, lessons, ["dev"], "test-freeze")
    assert verify_freeze(tmp_path, target)["repeats"] == 2
    (tmp_path / "src/agent.py").write_text("version = 2")
    with pytest.raises(ValueError, match="Frozen inputs changed"):
        verify_freeze(tmp_path, target)
    write_json(tmp_path / "runs/dev/summary.json", {"split": "official_test"})
    with pytest.raises(ValueError, match="training"):
        freeze(tmp_path, lessons, ["dev"], "invalid-freeze")
