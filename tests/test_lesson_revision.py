"""V5 must retain the scientific-finality and shared-budget guarantees of v4."""

import json
from pathlib import Path

import pytest

from reproscout.cli import execute
from reproscout.tasks import digest, write_json


def prepare(tmp_path, infrastructure, spent):
    root = Path(__file__).resolve().parents[1]
    write_json(
        tmp_path / "configs/pilot.json", json.loads((root / "configs/pilot.json").read_text())
    )
    (tmp_path / "input.tar").write_bytes(b"test fixture, never dispatched")
    manifest = {
        "task_id": "training-fixture",
        "task_prompt": "Test fixture",
        "questions": {},
        "prepared_path": "input.tar",
        "prepared_sha256": digest((tmp_path / "input.tar").read_bytes()),
    }
    write_json(tmp_path / "manifest.json", manifest)
    write_json(tmp_path / "runs/prior/manifest.json", manifest)
    write_json(
        tmp_path / "runs/prior/summary.json",
        {
            "run_id": "prior",
            "experiment_id": "development-v5",
            "condition": "A",
            "repeat": 1,
            "infrastructure_failure": infrastructure,
            "cost_uncached_upper_usd": spent,
            "model_calls": 0,
            "seconds": 1,
        },
    )


def test_v5_scientific_failure_cannot_be_rerun(tmp_path):
    prepare(tmp_path, infrastructure=False, spent=0.01)
    with pytest.raises(ValueError, match="scientific outcome already exists"):
        execute(tmp_path, "run", None, tmp_path / "manifest.json", experiment_id="development-v5")


def test_v5_infrastructure_failure_consumes_shared_budget(tmp_path):
    prepare(tmp_path, infrastructure=True, spent=1.0)
    with pytest.raises(ValueError, match="Cell budget exhausted"):
        execute(tmp_path, "run", None, tmp_path / "manifest.json", experiment_id="development-v5")
