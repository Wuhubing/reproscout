"""Static publishing must never expose local job state or unexported reviews."""

import importlib.util
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
spec = importlib.util.spec_from_file_location("export_pages", ROOT / "scripts/export_pages.py")
pages = importlib.util.module_from_spec(spec)
spec.loader.exec_module(pages)


def test_pages_export_uses_public_records_and_retains_downloadable_evidence(tmp_path):
    root = tmp_path / "repository"
    name = "20261119T035641056702Z-sklearn-diabetes-ols-102-run-A1"
    source = ROOT / "reports/workspace-runs" / name
    shutil.copytree(source, root / "reports/workspace-runs" / name)
    (root / "docs").mkdir()
    (root / "deliverables").mkdir()
    shutil.copyfile(
        ROOT / "deliverables/sklearn-diabetes-ols-102.zip",
        root / "deliverables/sklearn-diabetes-ols-102.zip",
    )
    # A local interrupted job would be mutated by a Workspace on the real root.
    jobs = root / ".reproscout/jobs/private"
    jobs.mkdir(parents=True)
    job = {"status": "running", "private_marker": "LOCAL_ONLY"}
    (jobs / "job.json").write_text(json.dumps(job))
    output = tmp_path / "site"
    pages.export(root, output)
    boot = json.loads((output / "snapshot/bootstrap.json").read_text())
    assert boot["read_only"] and not boot["credential_ready"]
    assert "csrf" not in boot and boot["jobs"] == []
    assert len(boot["runs"]) == 1
    assert boot["runs"][0]["reviewed"] == 3
    assert json.loads((jobs / "job.json").read_text()) == job
    evidence = output / "snapshot/runs" / name / "artifacts/step-003.stdout.txt.json"
    assert "2548.07" in json.loads(evidence.read_text())["text"]
    assert (output / "downloads" / (name + ".zip")).is_file()
    assert not (output / ".reproscout").exists()
    for path in (output / "snapshot").rglob("*.json"):
        assert "LOCAL_ONLY" not in path.read_text()
