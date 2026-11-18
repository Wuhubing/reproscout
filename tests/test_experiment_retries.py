"""Infrastructure records never fill scientific cells or disappear on retry."""

import pytest

from reproscout.experiment import aggregate
from reproscout.tasks import digest, write_json


def setup(tmp_path):
    experiment = tmp_path / "experiments/test"
    experiment.mkdir(parents=True)
    (experiment / "lessons.md").write_text("unchanged")
    write_json(
        experiment / "freeze.json",
        {
            "experiment_id": "test",
            "cohort": {"heldout": ["capsule"]},
            "files": {},
            "lessons_sha256": digest(b"unchanged"),
            "infrastructure_retry_policy": {"max_cell_attempts": 3},
        },
    )
    return experiment


def record(root, name, infrastructure):
    folder = root / "runs" / name
    folder.mkdir(parents=True)
    write_json(folder / "manifest.json", {"task_id": "capsule"})
    write_json(
        folder / "summary.json",
        {
            "run_id": name,
            "experiment_id": "test",
            "condition": "A",
            "repeat": 1,
            "infrastructure_failure": infrastructure,
            "cost_estimated_usd": 0.01,
            "seconds": 10,
            "evaluation": {"solved": False},
        },
    )


def test_failed_infrastructure_is_missing_and_retained(tmp_path):
    experiment = setup(tmp_path)
    record(tmp_path, "01-failed", True)
    result = aggregate(tmp_path, experiment)
    assert ["capsule", "A", 1] in result["missing"]
    assert not result["scientific_matrix_complete"]
    assert result["runs"] == [] and len(result["all_attempts"]) == 1
    record(tmp_path, "02-scientific", False)
    result = aggregate(tmp_path, experiment)
    assert ["capsule", "A", 1] not in result["missing"]
    assert len(result["runs"]) == 1 and len(result["infrastructure_attempts"]) == 1
    assert result["all_attempt_cost_estimated_usd"] == 0.02
    assert result["totals"]["A1"]["solved"] == 0  # An unsolved outcome is final.


def test_duplicate_scientific_outcomes_rejected(tmp_path):
    experiment = setup(tmp_path)
    record(tmp_path, "01-scientific", False)
    record(tmp_path, "02-scientific", False)
    with pytest.raises(ValueError, match="Duplicate formal run"):
        aggregate(tmp_path, experiment)
