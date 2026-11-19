"""Download pinned upstream code and package it unchanged; contains no reference answers."""

import argparse
import hashlib
import io
import json
import tarfile
import zipfile
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]

parser = argparse.ArgumentParser(
    description="Package unchanged scikit-learn scientific example for ReproScout import."
)
parser.add_argument("--output", type=Path, required=True)
OUT = parser.parse_args().output
OUT.mkdir(parents=True, exist_ok=True)
commit = "7e1e6d09bcc2eaeba98f7e737aac2ac782f0e5f1"
base = f"https://raw.githubusercontent.com/scikit-learn/scikit-learn/{commit}"
files = {}
for src, target in [
    ("examples/linear_model/plot_ols.py", "code/plot_ols.py"),
    ("COPYING", "code/LICENSE"),
]:
    r = httpx.get(base + "/" + src, follow_redirects=True, timeout=30)
    r.raise_for_status()
    files[target] = r.content
files["code/README.md"] = (
    """# Diabetes regression — scikit-learn 1.0.2

This is a prepared, unchanged upstream scientific example, not a CORE-Bench task.
Original source: scikit-learn/scikit-learn at commit """
    + commit
    + """.
The source file is authored by Jaques Grobler and distributed under BSD-3-Clause.
Run `/code/plot_ols.py` natively. It loads the diabetes dataset packaged with
scikit-learn, fits the author's one-feature ordinary least squares model,
and prints the coefficient, test mean squared error, and test R-squared.
Report the values actually printed, at the displayed precision.
The source calls plt.show(); this headless environment does not promise a saved figure.
No expected answer or reference score is supplied.

This README is ReproScout preparation metadata, not upstream scientific code.
"""
).encode()
files["REPRODUCING.md"] = b"""# Prepared runtime

Execute the unchanged /code/plot_ols.py using Python in /code.
The image contains scikit-learn 1.0.2, numpy 1.21.5, scipy 1.7.3, and matplotlib 3.5.1.
The diabetes data is the original packaged scikit-learn dataset inside the pinned image.
This compatible cached runtime is reused; it is not claimed to be an image published by the scikit-learn authors.
The controller empties /code, /data and /results before extracting these inputs.
Network access is disabled. Do not substitute data or rewrite the computation.
"""
inventory = []
buffer = io.BytesIO()
for name, body in files.items():
    inventory.append(
        {
            "path": name,
            "sha256": hashlib.sha256(body).hexdigest(),
            "bytes": len(body),
            "role": "upstream_source"
            if name == "code/plot_ols.py"
            else "license"
            if name == "code/LICENSE"
            else "preparation_metadata",
        }
    )
with tarfile.open(fileobj=buffer, mode="w") as tf:
    for name, body in files.items():
        info = tarfile.TarInfo(name)
        info.size = len(body)
        info.mode = 0o644
        tf.addfile(info, io.BytesIO(body))
archive = buffer.getvalue()
(OUT / "prepared.tar").write_bytes(archive)
m = {
    "task_id": "sklearn-diabetes-ols-102",
    "title": "Diabetes regression — scikit-learn",
    "language": "Python",
    "split": "user_project",
    "task_prompt": "Run the unchanged original /code/plot_ols.py and report the printed regression outputs at their displayed precision. Do not modify scientific code or replace data.",
    "questions": {
        "q1": "What regression coefficient does the original example print?",
        "q2": "What test mean squared error does the original example print?",
        "q3": "What test coefficient of determination (R-squared) does the original example print?",
    },
    "answer_types": {"q1": "number", "q2": "number", "q3": "number"},
    "prepared_path": "prepared.tar",
    "prepared_sha256": hashlib.sha256(archive).hexdigest(),
    "image": "registry.codeocean.com/published/9765eb0c-6e64-461f-9572-d83aa926b865@sha256:d9941a888badf522e9e605c0afdab854eddbcfe74e8f76b150682541a135f2c4",
    "input_inventory": inventory,
    "source_repository": "https://github.com/scikit-learn/scikit-learn",
    "source_commit": commit,
    "source_path": "examples/linear_model/plot_ols.py",
    "source_license": "BSD-3-Clause",
    "preparation_note": "Upstream scientific source unchanged. Compatible cached runtime with matching scikit-learn version; not the upstream authors image. Library-packaged data is fixed by image digest.",
}
(OUT / "manifest.json").write_text(json.dumps(m, indent=2) + "\n")
with zipfile.ZipFile(OUT / "sklearn-diabetes-ols-102.zip", "w", zipfile.ZIP_DEFLATED) as z:
    z.write(OUT / "manifest.json", "manifest.json")
    z.write(OUT / "prepared.tar", "prepared.tar")
expected = json.loads(
    (ROOT / "manifests/import-examples/sklearn-diabetes-ols-102.json").read_text()
)
if m != expected:
    raise ValueError("Prepared project differs from the frozen import example")
print(
    json.dumps(
        {
            "bundle": str(OUT / "sklearn-diabetes-ols-102.zip"),
            "prepared_sha256": m["prepared_sha256"],
            "source_sha256": inventory[0]["sha256"],
            "source_commit": commit,
        }
    )
)
