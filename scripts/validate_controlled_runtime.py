"""Offline integration probes for generic wrappers, separate from scientific tasks."""

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path

from reproscout.controlled import author_command
from reproscout.tasks import write_json

ROOT = Path(__file__).resolve().parents[1]


def main():
    records = []
    fixtures = [
        (
            "capsule-0940461",
            "fixture.ipynb",
            json.dumps(
                {
                    "nbformat": 4,
                    "nbformat_minor": 2,
                    "metadata": {
                        "kernelspec": {
                            "name": "python3",
                            "display_name": "Python 3",
                            "language": "python",
                        }
                    },
                    "cells": [
                        {
                            "cell_type": "code",
                            "metadata": {},
                            "execution_count": None,
                            "outputs": [],
                            "source": '%matplotlib inline\nimport matplotlib.pyplot as plt\nprint("WRAPPER_PROBE", 2*3)\nplt.plot([0,1],[0,1]); plt.show()',
                        }
                    ],
                }
            ),
            "native",
        ),
        (
            "capsule-9168639",
            "fixture.Rmd",
            '---\ntitle: "Wrapper probe"\noutput: html_document\n---\n\n```{r}\nvalue <- 2*3\nprint(value)\n```\n',
            "r_chunks",
        ),
    ]
    with tempfile.TemporaryDirectory() as folder:
        for task, name, content, mode in fixtures:
            image = json.loads((ROOT / "manifests" / f"{task}.json").read_text())["image"]
            p = Path(folder) / name
            p.write_text(content)
            sha = hashlib.sha256(p.read_bytes()).hexdigest()
            cid = subprocess.check_output(
                [
                    "docker",
                    "run",
                    "-d",
                    "--rm",
                    "--platform",
                    "linux/amd64",
                    "--network",
                    "none",
                    "--cap-drop",
                    "ALL",
                    "--security-opt",
                    "no-new-privileges:true",
                    image,
                    "bash",
                    "-c",
                    "sleep infinity",
                ],
                text=True,
            ).strip()
            try:
                subprocess.run(
                    ["docker", "exec", cid, "mkdir", "-p", "/code", "/results"],
                    check=True,
                    capture_output=True,
                )
                subprocess.run(
                    ["docker", "cp", str(p), cid + ":/code/" + name],
                    check=True,
                    capture_output=True,
                )
                command = author_command("/code/" + name, mode, {"/code/" + name: sha})
                result = subprocess.run(
                    ["docker", "exec", "-w", "/code", cid, "bash", "-c", command],
                    capture_output=True,
                    text=True,
                    timeout=180,
                )
                actual = subprocess.check_output(
                    ["docker", "exec", cid, "sha256sum", "/code/" + name], text=True
                ).split()[0]
                outputs = subprocess.check_output(
                    ["docker", "exec", cid, "find", "/results", "-type", "f"], text=True
                ).splitlines()
                passed = (
                    result.returncode == 0
                    and actual == sha
                    and (
                        "WRAPPER_PROBE 6" in result.stdout
                        if name.endswith("ipynb")
                        else "[1] 6" in result.stdout
                    )
                )
                if name.endswith("ipynb"):
                    passed = (
                        passed
                        and any(x.endswith(".png") for x in outputs)
                        and any(x.endswith("outputs.txt") for x in outputs)
                    )
                records.append(
                    {
                        "fixture": name,
                        "image": image,
                        "mode": mode,
                        "passed": passed,
                        "source_unchanged": actual == sha,
                        "source_sha256": sha,
                        "exit_code": result.returncode,
                        "outputs": outputs,
                        "stdout": result.stdout,
                        "stderr": result.stderr,
                    }
                )
            finally:
                subprocess.run(["docker", "rm", "-f", cid], capture_output=True)
    write_json(
        ROOT / "reports/controlled-runtime-validation-v6.json",
        {
            "scope": "Synthetic offline wrapper integration probes, not scientific benchmark outcomes or answer evidence. No model requests.",
            "passed": all(x["passed"] for x in records),
            "probes": records,
        },
    )
    print(
        json.dumps(
            [{k: v for k, v in x.items() if k not in ["stdout", "stderr"]} for x in records],
            indent=2,
        )
    )
    assert all(x["passed"] for x in records)


if __name__ == "__main__":
    main()
