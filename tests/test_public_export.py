"""Keep encrypted provider blobs private without dropping visible evidence."""

import importlib
import json
from pathlib import Path

import pytest


def exporter(monkeypatch):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    return importlib.import_module("export_delivery")


def test_opaque_payload_omission_preserves_visible_evidence(monkeypatch):
    module = exporter(monkeypatch)
    opaque = "encrypted-" + "sk-" + "x" * 40
    original = [
        {
            "content": [
                {
                    "type": "reasoning",
                    "redacted": True,
                    "reasoning": opaque,
                    "signature": "opaque-id",
                },
                {"type": "text", "text": "The computed accuracy is 97.22."},
            ],
            "tool_calls": [{"function": "shell", "arguments": {"command": "python run.py"}}],
        }
    ]
    result = module.public_messages(original)
    assert original[0]["content"][0]["reasoning"] == opaque
    assert opaque not in json.dumps(result)
    assert result[0]["content"][1] == original[0]["content"][1]
    assert result[0]["tool_calls"] == original[0]["tool_calls"]
    module.check_public_export(json.dumps(result))


def test_visible_credentials_still_block_export(monkeypatch):
    module = exporter(monkeypatch)
    text = json.dumps({"content": "sk-proj-" + "x" * 40})
    with pytest.raises(ValueError, match="Potential secret"):
        module.check_public_export(text)
