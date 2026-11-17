"""The recovery path verifies public manifest bytes before trusting a digest."""

import hashlib
import importlib
import json
from pathlib import Path

import httpx
import pytest


@pytest.mark.parametrize("tampered", [False, True])
def test_registry_resolution_checks_digest_and_uses_standard_auth(monkeypatch, tampered):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "scripts"))
    recovery = importlib.import_module("recover_cohort")
    body = json.dumps({"schemaVersion": 2, "layers": [{"size": 12}]}).encode()
    digest = "sha256:" + hashlib.sha256(body).hexdigest()
    calls = []

    def handler(request):
        calls.append(request)
        if request.url.host == "codeocean.com":
            assert request.url.params["scope"] == "repository:published/example:pull"
            return httpx.Response(200, json={"token": "public-test-token"})
        assert request.headers["authorization"] == "Bearer public-test-token"
        return httpx.Response(
            200,
            content=body,
            headers={"docker-content-digest": "sha256:invalid" if tampered else digest},
        )

    original = httpx.Client
    monkeypatch.setattr(
        recovery.httpx,
        "Client",
        lambda **kwargs: original(transport=httpx.MockTransport(handler), **kwargs),
    )
    if tampered:
        with pytest.raises(ValueError, match="digest mismatch"):
            recovery.resolve("registry.codeocean.com/published/example:v1")
    else:
        image, manifest = recovery.resolve("registry.codeocean.com/published/example:v1")
        assert image == "registry.codeocean.com/published/example@" + digest
        assert manifest["layers"][0]["size"] == 12
    assert len(calls) == 2
