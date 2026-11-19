"""Build read-only Pages data exclusively from public report directories.

Never reads local jobs, credentials, imported projects, or review drafts.
"""

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from export_delivery import check_public_export

from reproscout.web import Workspace

ROOT = Path(__file__).resolve().parents[1]


def write(path, value):
    body = json.dumps(value, indent=2) + "\n"
    check_public_export(body)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(body)


def export(root, output):
    output.mkdir(parents=True, exist_ok=True)
    # Isolated state prevents local jobs or unpublished reviews entering the site.
    with tempfile.TemporaryDirectory() as temporary:
        staging = Path(temporary)
        for name in ("product-runs", "workspace-runs"):
            source = root / "reports" / name
            if source.exists():
                shutil.copytree(source, staging / "reports" / name)
        if (root / "lessons/registry").exists():
            shutil.copytree(root / "lessons/registry", staging / "lessons/registry")
        workspace = Workspace(staging)
        runs = workspace.runs()
        projects = {}
        for run in runs:
            key = run["id"]
            detail = workspace.details(key)
            manifest = detail["manifest"]
            projects.setdefault(
                manifest["task_id"],
                {
                    **manifest,
                    "id": manifest["task_id"],
                    "description": manifest.get("task_prompt", ""),
                    "prepared": False,
                },
            )
            target = output / "snapshot/runs" / key
            write(target / "details.json", detail)
            source = workspace.source(key)
            trace = source / "trajectory.json"
            write(target / "trace.json", json.loads(trace.read_text()) if trace.exists() else {})
            for name, meta in detail["artifacts"].items():
                artifact, _ = workspace.evidence(key, name)
                destination = target / name
                destination.parent.mkdir(parents=True, exist_ok=True)
                if meta.get("kind") == "image":
                    shutil.copyfile(artifact, destination)
                else:
                    write(
                        Path(str(destination) + ".json"),
                        {
                            "name": artifact.name,
                            "text": artifact.read_text(errors="replace"),
                            "metadata": meta,
                        },
                    )
            download = output / "downloads" / (key + ".zip")
            download.parent.mkdir(parents=True, exist_ok=True)
            download.write_bytes(workspace.export(key))
        write(
            output / "snapshot/bootstrap.json",
            {
                "version": "0.9.0",
                "read_only": True,
                "credential_ready": False,
                "projects": list(projects.values()),
                "runs": runs,
                "lessons": workspace.lessons(),
                "jobs": [],
            },
        )
        write(output / "snapshot/runs.json", {"runs": runs, "jobs": []})
    shutil.copytree(root / "reports", output / "archive", dirs_exist_ok=True)
    shutil.copytree(root / "docs", output / "docs", dirs_exist_ok=True)
    for path in output.rglob("*"):
        if path.is_file() and path.suffix in (".json", ".jsonl", ".txt", ".md", ".html"):
            check_public_export(path.read_text(errors="replace"))
    shutil.copyfile(
        root / "deliverables/sklearn-diabetes-ols-102.zip",
        output / "downloads/sklearn-diabetes-ols-102.zip",
    )
    (output / ".nojekyll").touch()
    print(f"Published snapshot: {len(runs)} runs, {len(projects)} projects")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "frontend/dist-pages")
    args = parser.parse_args()
    export(ROOT, args.output)
