"""Exercise the capability boundary and strict submissions, including stale evidence."""

import asyncio
import json
from types import SimpleNamespace

import pytest
from inspect_ai.tool import ToolError

from reproscout import agent, controlled
from reproscout.budget import Budget
from reproscout.controlled import author_command, validate_provenance, validate_types


@pytest.mark.parametrize("value", ["1000", "1000 ms", True, float("nan"), float("inf")])
def test_reject_numeric_coercion(value):
    with pytest.raises(ValueError):
        validate_types({"q": {"value": value}}, {"q": "number"})


def test_explicit_types_and_nulls():
    for value in [1, 0.25, None]:
        validate_types({"q": {"value": value}}, {"q": "number"})
    validate_types({"q": {"value": [0.1, 0.01]}}, {"q": "number_list"})
    with pytest.raises(ValueError):
        validate_types({"q": {"value": [0.1, "0.01"]}}, {"q": "number_list"})


@pytest.mark.parametrize(
    "path", ["/tmp/copy.py", "/code/../data/code.py", "/code/a.py; echo 90", "/code/new.py"]
)
def test_refuse_uninventoried_execution(path):
    with pytest.raises(ValueError):
        author_command(path, "native", {"/code/a.py": "hash"})


def test_no_model_code_arguments_or_selected_chunks():
    inventory = {"/code/a.Rmd": "x", "/code/a.ipynb": "y"}
    with pytest.raises(ValueError):
        author_command("/code/a.Rmd", "eval arbitrary code", inventory)
    code = author_command("/code/a.Rmd", "r_chunks", inventory)
    assert "knitr::purl" in code and "source(" in code
    notebook = author_command("/code/a.ipynb", "native", inventory)
    assert "ExecutePreprocessor" in notebook and "allow_errors" not in notebook
    assert ".source =" not in notebook


def test_source_and_failed_output_cannot_support_non_null():
    answer = {"q": {"value": 90, "evidence": [{"artifact": "a"}]}}
    for metadata in [{"kind": "file_snapshot"}, {"verified_execution": False}]:
        with pytest.raises(ValueError):
            validate_provenance(answer, {"a": metadata})
    validate_provenance(answer, {"a": {"verified_execution": True}})
    answer["q"]["value"] = None
    validate_provenance(answer, {"a": {}})


def test_lineage_requires_current_output_hash(tmp_path):
    c = controlled.ControlledExecution(tmp_path, {"input_inventory": []}, {}, None)
    c.generated["/results/a.csv"] = {"source_sha256": "old", "verified_execution": True}
    assert not c.lineage("/results/a.csv", "new")
    assert c.lineage("/results/a.csv", "old")["verified_execution"]


def test_modified_input_refuses_before_dispatch(monkeypatch, tmp_path):
    class Fake:
        async def exec(self, args, **kwargs):
            return SimpleNamespace(
                returncode=0, stdout="/code/a.py" if args[0] == "readlink" else "wrong  /code/a.py"
            )

    monkeypatch.setattr(controlled, "sandbox", lambda: Fake())
    calls = []

    async def dispatch(**kwargs):
        calls.append(kwargs)

    c = controlled.ControlledExecution(
        tmp_path, {"input_inventory": [{"path": "code/a.py", "sha256": "expected"}]}, {}, dispatch
    )
    with pytest.raises(ToolError, match="changed"):
        asyncio.run(c.tools()[1]("/code/a.py"))
    assert not calls
    assert json.loads((tmp_path / "execution-ledger.json").read_text())[-1]["status"] == "refused"


def test_no_shell_in_b_and_baseline_retained(monkeypatch, tmp_path):
    monkeypatch.setattr(agent, "react", lambda **kwargs: kwargs)
    manifest = {"questions": {}, "input_inventory": []}
    a = agent.build_agent(tmp_path, manifest, {"max_model_calls": 20}, Budget())
    b = agent.build_agent(
        tmp_path,
        manifest,
        {"max_model_calls": 20, "controlled_execution": True, "answer_types": {}},
        Budget(),
    )
    assert len(a["tools"]) == 3 and len(b["tools"]) == 5
    assert "command" in a["tools"][0].__annotations__
    assert all("command" not in t.__annotations__ for t in b["tools"])
