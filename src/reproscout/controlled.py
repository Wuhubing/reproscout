"""V6 capability boundary: model-selected original files, never model-written code."""

from __future__ import annotations

import json
import math
import shlex
from pathlib import Path, PurePosixPath

from inspect_ai.tool import ToolError, tool
from inspect_ai.util import sandbox

from .tasks import write_json

NOTEBOOK = """import nbformat, base64, json
from pathlib import Path
from nbconvert.preprocessors import ExecutePreprocessor
from nbconvert import HTMLExporter
nb = nbformat.read(PATH, as_version=4)
ExecutePreprocessor(timeout=None, kernel_name=nb.metadata.get('kernelspec', {}).get('name', 'python3')).preprocess(nb, {'metadata': {'path': '/code'}})
out=Path('/results/reproscout-notebook');out.mkdir(exist_ok=True)
nbformat.write(nb, out/'executed.ipynb')
body,_=HTMLExporter().from_notebook_node(nb)
(out/'executed.html').write_text(body)
lines=[]
for i,c in enumerate(nb.cells):
 for j,o in enumerate(c.get('outputs', [])):
  lines.append('CELL %s OUTPUT %s' % (i,j))
  if 'text' in o: lines.append(o.text)
  data=o.get('data', {})
  if 'text/plain' in data: lines.append(data['text/plain'])
  if 'image/png' in data:
   p=out/('cell-%s-output-%s.png' % (i,j));p.write_bytes(base64.b64decode(data['image/png']));lines.append(str(p))
text='\\n'.join(lines)
(out/'outputs.txt').write_text(text)
print(text)
"""


def valid_path(path: str) -> str:
    p = PurePosixPath(path)
    if not path.startswith(("/code/", "/data/", "/results/")) and path not in {
        "/code",
        "/data",
        "/results",
        "/REPRODUCING.md",
    }:
        raise ValueError("Path outside task scope")
    if ".." in p.parts or "\x00" in path or "\n" in path:
        raise ValueError("Invalid task path")
    return str(p)


def author_command(path: str, mode: str, inventory: dict) -> str:
    path = valid_path(path)
    if path not in inventory or not path.startswith("/code/"):
        raise ValueError("Only inventoried original author files can execute")
    q = shlex.quote(path)
    if mode not in {"native", "r_chunks"}:
        raise ValueError("Unsupported execution mode")
    suffix = PurePosixPath(path).suffix.lower()
    if suffix == ".rmd":
        # JSON string syntax is valid for these absolute POSIX paths in R.
        literal = json.dumps(path)
        code = (
            f"knitr::purl({literal}, output='/results/reproscout-author.R', documentation=0); "
            "source('/results/reproscout-author.R', echo=TRUE)"
            if mode == "r_chunks"
            else f"rmarkdown::render({literal}, output_dir='/results', clean=TRUE)"
        )
        return "Rscript -e " + shlex.quote(code)
    if mode != "native":
        raise ValueError("Chunk extraction requires an original R Markdown file")
    if suffix == ".ipynb":
        return "python -c " + shlex.quote("PATH=" + repr(path) + "\n" + NOTEBOOK)
    if suffix == ".py":
        return "python " + q
    if suffix == ".r":
        return "Rscript " + q
    if suffix == ".sh" or PurePosixPath(path).name == "run":
        return "bash " + q
    raise ValueError("Unsupported author file; no arbitrary interpreter arguments allowed")


def validate_types(answers: dict, contracts: dict) -> None:
    def numeric(x):
        return type(x) in (int, float) and math.isfinite(x)

    for qid, kind in contracts.items():
        value = answers[qid]["value"]
        if value is None:
            continue
        good = (
            numeric(value)
            if kind == "number"
            else isinstance(value, str)
            if kind == "string"
            else isinstance(value, list) and bool(value) and all(numeric(x) for x in value)
        )
        if not good:
            raise ValueError(f"{qid}: requires {kind}, or null with blocker evidence; no coercion")


def validate_provenance(answers: dict, artifacts: dict) -> None:
    for qid, answer in answers.items():
        if answer["value"] is not None and not all(
            artifacts[ref["artifact"]].get("verified_execution") for ref in answer["evidence"]
        ):
            raise ValueError(
                f"{qid}: non-null values must cite successful original execution outputs"
            )


class ControlledExecution:
    def __init__(self, run: Path, manifest: dict, artifacts: dict, execute):
        self.run, self.artifacts, self.execute = run, artifacts, execute
        self.inventory = {"/" + x["path"]: x["sha256"] for x in manifest["input_inventory"]}
        self.generated = {}
        self.events = []

    def record(self, **event):
        self.events.append(event)
        write_json(self.run / "execution-ledger.json", self.events)

    async def resolve(self, path):
        path = valid_path(path)
        result = await sandbox().exec(["readlink", "-f", path], timeout=10)
        if result.returncode:
            raise ValueError("File unavailable")
        return valid_path(result.stdout.strip())

    async def outputs(self):
        result = await sandbox().exec(
            ["find", "/code", "/results", "-type", "f", "-exec", "sha256sum", "{}", "+"], timeout=30
        )
        return {
            line.split(maxsplit=1)[1]: line.split(maxsplit=1)[0]
            for line in result.stdout.splitlines()
            if len(line.split(maxsplit=1)) == 2
        }

    async def verify(self):
        result = await sandbox().exec(["sha256sum", *self.inventory], timeout=30)
        actual = {
            line.split(maxsplit=1)[1]: line.split(maxsplit=1)[0]
            for line in result.stdout.splitlines()
            if len(line.split(maxsplit=1)) == 2
        }
        if result.returncode or any(actual.get(p) != h for p, h in self.inventory.items()):
            raise ValueError("Original input changed or missing; execution refused")

    def lineage(self, source: str, content_sha256: str) -> dict:
        value = self.generated.get(source, {})
        return value if value.get("source_sha256") == content_sha256 else {}

    def tools(self):
        @tool
        def list_files():
            async def execute(path: str = "/code") -> str:
                """List task files without executing code.

                Args:
                    path: Directory under /code, /data or /results.
                """
                try:
                    real = await self.resolve(path)
                    result = await sandbox().exec(
                        ["find", real, "-maxdepth", "3", "-type", "f"], timeout=20
                    )
                    return result.stdout[:20000]
                except ValueError as exc:
                    raise ToolError(str(exc)) from None

            return execute

        @tool
        def execute_author():
            async def execute(path: str, mode: str = "native") -> str:
                """Execute a hash-verified original author file, with no editable code or arguments.

                Args:
                    path: Original file under /code: .py, .R, .sh, run, .ipynb or .Rmd.
                    mode: native, or r_chunks to extract and execute ALL original R Markdown chunks.
                """
                try:
                    real = await self.resolve(path)
                    if real != path:
                        raise ValueError("Use the exact inventoried original path")
                    command = author_command(path, mode, self.inventory)
                    await self.verify()
                    before = await self.outputs()
                except ValueError as exc:
                    self.record(
                        operation="execute_author",
                        path=path,
                        mode=mode,
                        status="refused",
                        reason=str(exc),
                    )
                    raise ToolError(str(exc)) from None
                old = set(self.artifacts)
                execution_id = len(self.events) + 1
                self.record(
                    operation="execute_author",
                    path=path,
                    mode=mode,
                    status="started",
                    execution_id=execution_id,
                    input_hashes_verified=len(self.inventory),
                    source_sha256=self.inventory[path],
                )
                try:
                    result = await self.execute(command=command)
                except Exception:
                    self.record(
                        operation="execute_author",
                        execution_id=execution_id,
                        status="failed_or_timeout",
                    )
                    raise
                success = result.startswith("Exit code: 0\n")
                for key in set(self.artifacts) - old:
                    self.artifacts[key].update(
                        execution_id=execution_id, verified_execution=success
                    )
                after = await self.outputs()
                for p, h in after.items():
                    if p not in self.inventory and before.get(p) != h:
                        self.generated[p] = {
                            "execution_id": execution_id,
                            "verified_execution": success,
                            "source_sha256": h,
                        }
                write_json(self.run / "artifact-index.json", self.artifacts)
                write_json(self.run / "generated-output-provenance.json", self.generated)
                self.record(
                    operation="execute_author",
                    execution_id=execution_id,
                    status="succeeded" if success else "failed",
                )
                return result

            return execute

        return [list_files(), execute_author()]


def evaluate_run(run: Path, contracts: dict, controlled: bool) -> dict:
    submission = run / "submission.json"
    answers = json.loads(submission.read_text()) if submission.exists() else None
    audit_path = run / "source-audit.json"
    audit = json.loads(audit_path.read_text()) if audit_path.exists() else {}
    artifacts = (
        json.loads((run / "artifact-index.json").read_text())
        if (run / "artifact-index.json").exists()
        else {}
    )
    types_ok, provenance = None, None
    if answers is not None:
        try:
            validate_types(answers, contracts)
            types_ok = True
        except ValueError:
            types_ok = False
        if controlled:
            try:
                validate_provenance(answers, artifacts)
                provenance = True
            except ValueError:
                provenance = False
    ledger = (
        json.loads((run / "execution-ledger.json").read_text())
        if (run / "execution-ledger.json").exists()
        else []
    )
    success = sum(e["status"] == "succeeded" for e in ledger)
    status = (
        "violated"
        if audit.get("unchanged") is False
        else "verified_original_execution"
        if controlled and success and audit.get("unchanged") is True and provenance is True
        else "unverified"
    )
    return {
        "answer_types_compliant": types_ok,
        "execution_fidelity": status,
        "non_null_output_provenance_verified": provenance,
        "successful_original_executions": success,
        "null_answers": sum(a["value"] is None for a in answers.values()) if answers else None,
        "semantic_evidence_support": "not_automatically_established",
        "scope": "Execution boundary and output provenance, not proof of complete scientific or semantic reproduction. A unrestricted trajectories require separate manual review.",
    }
