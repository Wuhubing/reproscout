"""Verify visual evidence decoding and sandbox path boundaries without a model."""

import asyncio
import io
import json
from types import SimpleNamespace

import pymupdf
import pytest
from inspect_ai.tool import ToolError
from PIL import Image

from reproscout import agent
from reproscout.budget import Budget


class FileSandbox:
    def __init__(self, content, resolved="/results/plot.png"):
        self.content = content
        self.resolved = resolved

    async def exec(self, args, **kwargs):
        value = self.resolved if args[0] == "readlink" else str(len(self.content))
        return SimpleNamespace(returncode=0, stdout=value)

    async def read_file(self, path, text=True):
        return self.content


def image_tool(monkeypatch, tmp_path, sandbox):
    monkeypatch.setattr(agent, "sandbox", lambda: sandbox)
    monkeypatch.setattr(agent, "react", lambda **kwargs: kwargs)
    built = agent.build_agent(tmp_path, {"questions": {}}, {"max_model_calls": 2}, Budget())
    return built["tools"][2]


def test_large_image_is_bounded_and_retained(monkeypatch, tmp_path):
    content = io.BytesIO()
    Image.new("RGB", (2000, 1000), "white").save(content, format="PNG")
    tool = image_tool(monkeypatch, tmp_path, FileSandbox(content.getvalue()))
    result = asyncio.run(tool("/results/plot.png"))
    index = json.loads((tmp_path / "artifact-index.json").read_text())
    record = index["artifacts/step-001.png"]
    assert record["dimensions"] == [1024, 512]
    assert result[1].image.startswith("data:image/png;base64,")
    assert (tmp_path / "artifacts/step-001.png").exists()


def test_pdf_page_is_rendered_and_invalid_page_rejected(monkeypatch, tmp_path):
    with pymupdf.open() as document:
        page = document.new_page()
        page.insert_text((72, 72), "Evidence from a generated PDF")
        data = document.tobytes()
    tool = image_tool(monkeypatch, tmp_path, FileSandbox(data, "/results/plot.pdf"))
    asyncio.run(tool("/results/plot.pdf", page=1))
    with pytest.raises(ToolError, match="PDF page out of range"):
        asyncio.run(tool("/results/plot.pdf", page=2))


def test_resolved_image_escape_is_rejected(monkeypatch, tmp_path):
    tool = image_tool(monkeypatch, tmp_path, FileSandbox(b"", "/private/answer.png"))
    with pytest.raises(ToolError, match="outside"):
        asyncio.run(tool("/results/plot.png"))
    assert not (tmp_path / "artifact-index.json").exists()
