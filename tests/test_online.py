import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import httpx
import pytest

from reproscout.online import OnlineStore, online_handler
from reproscout.web import Workspace

ROOT = Path(__file__).resolve().parents[1]
IMAGES = json.loads((ROOT / "deploy/images.example.json").read_text())


@pytest.fixture
def online(tmp_path):
    store = OnlineStore(tmp_path / "state", ROOT, "http://127.0.0.1:8789", IMAGES, 0.1)
    store.invite("alice", tmp_path / "alice.code")
    store.invite("bob", tmp_path / "bob.code")
    server = ThreadingHTTPServer(("127.0.0.1", 0), online_handler(store))
    store.origin = f"http://127.0.0.1:{server.server_port}"
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    with httpx.Client(base_url=store.origin, headers={"Origin": store.origin}) as client:
        yield store, client, tmp_path
    server.shutdown()
    server.server_close()


def login(client, path):
    result = client.post("/api/login", json={"code": path.read_text().strip()})
    assert result.status_code == 200
    assert "HttpOnly" in result.headers["set-cookie"]
    boot = client.get("/api/bootstrap").json()
    client.headers["X-ReproScout-CSRF"] = boot["csrf"]
    return boot


def test_accounts_cannot_read_or_mutate_each_other(online, monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder-never-sent")
    store, client, tmp = online
    assert client.get("/api/bootstrap").status_code == 401
    assert client.get("/%61pi/bootstrap").status_code == 401
    assert client.post("/api/login", json={"code": "wrong"}).status_code == 401
    boot = login(client, tmp / "alice.code")
    assert boot["account"] == "alice" and boot["online"]
    bundle = (ROOT / "deliverables/sklearn-diabetes-ols-102.zip").read_bytes()
    assert client.post("/api/projects/import", content=bundle).status_code == 201
    assert len(client.get("/api/bootstrap").json()["projects"]) == 1
    assert client.post("/api/logout", json={}).status_code == 200
    assert client.get("/api/bootstrap").status_code == 401
    boot = login(client, tmp / "bob.code")
    assert boot["projects"] == [] and boot["runs"] == []
    denied = client.post("/api/runs", json={"project_id": "sklearn-diabetes-ols-102"})
    assert denied.status_code == 400
    assert "Unknown prepared project" in denied.text
    assert not store.workspace("bob").jobs()


def test_csrf_origin_host_and_session_expiry(online):
    store, client, tmp = online
    login(client, tmp / "alice.code")
    assert (
        client.post("/api/logout", json={}, headers={"Origin": "https://evil.test"}).status_code
        == 403
    )
    assert (
        client.post("/api/logout", json={}, headers={"X-ReproScout-CSRF": "wrong"}).status_code
        == 403
    )
    assert client.get("/api/bootstrap", headers={"Host": "evil.test"}).status_code == 403
    with store.db() as db:
        db.execute("UPDATE sessions SET expires=0")
    assert client.get("/api/bootstrap").status_code == 401


def test_global_budget_is_persistent_and_not_bypassed_by_new_account(online, monkeypatch):
    store, client, tmp = online
    monkeypatch.setattr(Workspace, "start", lambda self, data: {"id": "retained-job"})
    a = store.workspace("alice")
    assert a.start({"model_budget_usd": 0.1})["id"] == "retained-job"
    with pytest.raises(ValueError, match="Monthly"):
        store.workspace("bob").start({"model_budget_usd": 0.01})
    restarted = OnlineStore(store.state, ROOT, store.origin, IMAGES, 0.1)
    with pytest.raises(ValueError, match="Monthly"):
        restarted.workspace("alice").start({"model_budget_usd": 0.01})
    with pytest.raises(ValueError, match="between"):
        a.start({"model_budget_usd": float("nan")})


def test_runtime_allowlist_and_server_wide_concurrency(online, monkeypatch):
    store, client, tmp = online
    a = store.workspace("alice")
    with pytest.raises(ValueError, match="not approved"):
        a.validate_manifest({"image": "evil@sha256:" + "0" * 64})
    monkeypatch.setattr(a, "jobs", lambda: [{"status": "running"}])
    with pytest.raises(ValueError, match="Server is busy"):
        store.workspace("bob").start({"model_budget_usd": 0.1})


def test_public_origin_requires_https(tmp_path):
    with pytest.raises(ValueError, match="HTTPS"):
        OnlineStore(tmp_path, ROOT, "http://public.example", IMAGES)


def test_revocation_blocks_existing_sessions_and_access_code(online):
    store, client, tmp = online
    login(client, tmp / "alice.code")
    store.revoke("alice")
    assert client.get("/api/bootstrap").status_code == 401
    assert (
        client.post(
            "/api/login", json={"code": (tmp / "alice.code").read_text().strip()}
        ).status_code
        == 401
    )


def test_secure_cookie_and_review_identity(online, monkeypatch):
    store, client, tmp = online
    store.origin = "https://research.example"
    response = client.post(
        "/api/login",
        headers={"Host": "research.example", "Origin": store.origin},
        json={"code": (tmp / "alice.code").read_text().strip()},
    )
    assert response.status_code == 200
    assert "; Secure" in response.headers["set-cookie"]
    monkeypatch.setattr(Workspace, "review", lambda self, key, record: record)
    record = store.workspace("alice").review(
        "run", {"reviewer": "bob", "reviewer_kind": "assistant"}
    )
    assert record["reviewer"] == "alice" and record["reviewer_kind"] == "assistant"
