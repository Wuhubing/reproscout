"""Invite-only, persistent, per-account workspaces behind a same-origin HTTPS proxy.

One host-wide controller at a time. This is a trusted research pilot, not an
anonymous arbitrary-code hosting service. No credentials are sent to author code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import secrets
import shutil
import sqlite3
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from http.cookies import SimpleCookie
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

from .web import Workspace, handler, identifier, process_alive


def hashed(value):
    return hashlib.sha256(value.encode()).hexdigest()


class OnlineStore:
    def __init__(self, state, template, origin, images, monthly_budget=1.0, recover=True):
        self.state = Path(state).resolve()
        self.template = Path(template).resolve()
        self.origin = origin.rstrip("/")
        url = urlsplit(self.origin)
        if url.scheme not in ("http", "https") or url.path or not url.netloc:
            raise ValueError("Origin must be a scheme and host without a path")
        if url.scheme != "https" and url.hostname not in ("127.0.0.1", "localhost"):
            raise ValueError("Public online mode requires HTTPS")
        self.images = set(images)
        if not self.images or any("@sha256:" not in image for image in self.images):
            raise ValueError("An administrator-approved digest-pinned image allowlist is required")
        if not 0 < monthly_budget <= 5:
            raise ValueError(
                "Monthly model reservation ceiling must be greater than zero and <= $5"
            )
        self.monthly_budget = monthly_budget
        self.state.mkdir(parents=True, exist_ok=True, mode=0o700)
        self.lock = threading.RLock()
        self.workspaces = {}
        self.db_path = self.state / "accounts.sqlite3"
        with self.db() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS accounts (id TEXT PRIMARY KEY, secret_hash TEXT UNIQUE);
                CREATE TABLE IF NOT EXISTS sessions (hash TEXT PRIMARY KEY, account TEXT, expires REAL);
                CREATE TABLE IF NOT EXISTS reservations (id TEXT PRIMARY KEY, account TEXT,
                    month TEXT, amount REAL, job TEXT);
            """)
        self.db_path.chmod(0o600)
        self.failures = []
        # Load all accounts so restart recovery also covers other tenants' workers.
        with self.db() as db:
            accounts = [row[0] for row in db.execute("SELECT id FROM accounts")]
        if recover:
            for account in accounts:
                self.workspace(account)

    @contextmanager
    def db(self):
        connection = sqlite3.connect(self.db_path, timeout=30)
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def invite(self, account, destination):
        identifier(account)
        code = secrets.token_urlsafe(32)
        destination = Path(destination)
        with self.lock, self.db() as db:
            if db.execute("SELECT 1 FROM accounts WHERE id=?", (account,)).fetchone():
                raise ValueError("Account already exists")
            # Exclusive creation, private mode; never print the access code.
            fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                with os.fdopen(fd, "w") as stream:
                    stream.write(code + "\n")
                db.execute("INSERT INTO accounts VALUES (?, ?)", (account, hashed(code)))
            except Exception:
                destination.unlink(missing_ok=True)
                raise
        return account

    def revoke(self, account):
        with self.lock, self.db() as db:
            if not db.execute("SELECT 1 FROM accounts WHERE id=?", (account,)).fetchone():
                raise ValueError("Unknown account")
            db.execute("DELETE FROM sessions WHERE account=?", (account,))
            db.execute("UPDATE accounts SET secret_hash=NULL WHERE id=?", (account,))

    def login(self, code):
        with self.lock, self.db() as db:
            now = time.time()
            self.failures = [stamp for stamp in self.failures if stamp > now - 60]
            if len(self.failures) >= 20:
                raise ValueError("Too many login attempts. Wait one minute.")
            self.failures.append(now)
            row = db.execute(
                "SELECT id FROM accounts WHERE secret_hash=?", (hashed(code),)
            ).fetchone()
            if not row:
                raise ValueError("Invalid access code")
            token = secrets.token_urlsafe(32)
            db.execute("DELETE FROM sessions WHERE expires < ?", (now,))
            db.execute(
                "INSERT INTO sessions VALUES (?, ?, ?)", (hashed(token), row[0], now + 43200)
            )
            return token

    def account(self, token):
        with self.db() as db:
            row = db.execute(
                "SELECT account FROM sessions WHERE hash=? AND expires>?",
                (hashed(token), time.time()),
            ).fetchone()
        return row[0] if row else None

    def logout(self, token):
        with self.db() as db:
            db.execute("DELETE FROM sessions WHERE hash=?", (hashed(token),))

    def workspace(self, account):
        with self.lock:
            if account not in self.workspaces:
                root = self.state / "users" / identifier(account)
                (root / "configs").mkdir(parents=True, exist_ok=True)
                shutil.copyfile(self.template / "configs/pilot.json", root / "configs/pilot.json")
                self.workspaces[account] = OnlineWorkspace(root, self, account)
            return self.workspaces[account]

    def usage(self):
        month = datetime.now(timezone.utc).strftime("%Y-%m")
        with self.db() as db:
            used = db.execute(
                "SELECT COALESCE(SUM(amount),0) FROM reservations WHERE month=?", (month,)
            ).fetchone()[0]
        return month, used


class OnlineWorkspace(Workspace):
    def __init__(self, root, store, account):
        super().__init__(root)
        self.store, self.account = store, account

    def validate_manifest(self, manifest):
        if manifest.get("image") not in self.store.images:
            raise ValueError(
                "Runtime is not approved on this server. Ask the operator to provision it."
            )
        super().validate_manifest(manifest)

    def storage_gate(self):
        used = sum(p.stat().st_size for p in self.root.rglob("*") if p.is_file())
        if used > 500 * 1024 * 1024:
            raise ValueError("Workspace storage admission limit reached. Contact the operator.")

    def import_bundle(self, body):
        with self.lock:
            self.storage_gate()
            if len(self.projects()) >= 10:
                raise ValueError("This pilot allows ten projects per account")
            return super().import_bundle(body)

    def start(self, data):
        with self.store.lock:
            self.storage_gate()
            for workspace in self.store.workspaces.values():
                if any(proc.poll() is None for proc in workspace.processes.values()) or any(
                    j.get("status") in ("starting", "running", "cancelling")
                    or (j.get("status") == "interrupted" and process_alive(j.get("worker_pid")))
                    for j in workspace.jobs()
                ):
                    raise ValueError("Server is busy with another run. Retry after it finishes.")
            amount = data.get("model_budget_usd", 0.1)
            if type(amount) not in (int, float) or not 0.01 <= amount <= 0.1:
                raise ValueError("Online runs require a model budget between $0.01 and $0.10")
            month, used = self.store.usage()
            if used + amount > self.store.monthly_budget + 1e-9:
                raise ValueError("Monthly model reservation limit reached. No run was started.")
            reservation = secrets.token_hex(16)
            with self.store.db() as db:
                db.execute(
                    "INSERT INTO reservations VALUES (?, ?, ?, ?, NULL)",
                    (reservation, self.account, month, amount),
                )
            # Conservative: a failed launch retains its reservation for operator audit.
            job = super().start({**data, "model_budget_usd": amount})
            with self.store.db() as db:
                db.execute("UPDATE reservations SET job=? WHERE id=?", (job["id"], reservation))
            return job

    def review(self, key, record):
        self.storage_gate()
        return super().review(key, {**record, "reviewer": self.account})


def online_handler(store):
    class Handler(handler(None)):
        def setup(self):
            super().setup()
            self.connection.settimeout(30)

        def cookie(self):
            try:
                cookies = SimpleCookie(self.headers.get("Cookie", ""))
                return (
                    cookies["reproscout_session"].value if "reproscout_session" in cookies else ""
                )
            except Exception:
                return ""

        def allowed(self):
            return self.headers.get("Host") == urlsplit(store.origin).netloc

        def valid_mutation(self):
            return (
                self.allowed()
                and self.headers.get("Origin") == store.origin
                and self.headers.get("X-ReproScout-CSRF") == self.workspace.token
            )

        def session_response(self, value, token="", status=200):
            body = json.dumps(value).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            secure = "; Secure" if store.origin.startswith("https:") else ""
            self.send_header(
                "Set-Cookie",
                "reproscout_session="
                + token
                + "; Path=/; HttpOnly; SameSite=Strict; Max-Age="
                + ("43200" if token else "0")
                + secure,
            )
            self.end_headers()
            self.wfile.write(body)

        def authenticate(self):
            account = store.account(self.cookie())
            if not account:
                self.send(
                    {"error": "Sign in to your research workspace", "login_required": True}, 401
                )
                return False
            self.workspace = store.workspace(account)
            return True

        def do_GET(self):
            if not self.allowed():
                return self.send({"error": "Invalid host"}, 403)
            path = unquote(urlsplit(self.path).path)
            if path == "/api/session":
                account = store.account(self.cookie())
                return self.send({"online": True, "account": account})
            if path.startswith("/api/") or path.startswith("/archive"):
                if not self.authenticate():
                    return
            if path == "/api/bootstrap":
                month, used = store.usage()
                return self.send(
                    {
                        "online": True,
                        "account": self.workspace.account,
                        "version": "0.10.0",
                        "csrf": self.workspace.token,
                        "credential_ready": bool(os.environ.get("OPENAI_API_KEY")),
                        "projects": self.workspace.projects(),
                        "runs": self.workspace.runs(),
                        "lessons": self.workspace.lessons(),
                        "jobs": self.workspace.jobs(),
                        "runtime_images": sorted(store.images),
                        "max_run_budget_usd": 0.1,
                        "monthly_reserved_usd": used,
                        "monthly_limit_usd": store.monthly_budget,
                        "budget_month_utc": month,
                    }
                )
            return super().do_GET()

        def do_POST(self):
            if not self.allowed() or self.headers.get("Origin") != store.origin:
                return self.send({"error": "Same-origin request required"}, 403)
            path = unquote(urlsplit(self.path).path)
            if path == "/api/login":
                try:
                    size = int(self.headers.get("Content-Length", 0))
                    if not 0 < size <= 4096:
                        raise ValueError("Invalid login request")
                    data = json.loads(self.rfile.read(size))
                    code = data.get("code", "")
                    if not isinstance(code, str) or len(code) > 256:
                        raise ValueError("Invalid access code")
                    token = store.login(code)
                    return self.session_response({"signed_in": True}, token)
                except (ValueError, TypeError, AttributeError):
                    return self.send(
                        {"error": "Sign-in failed. Check your code or retry in one minute."}, 401
                    )
            if not self.authenticate():
                return
            if path == "/api/logout":
                if not self.valid_mutation():
                    return self.send({"error": "Invalid session request"}, 403)
                store.logout(self.cookie())
                return self.session_response({"signed_out": True})
            if path == "/api/projects":
                return self.send({"error": "Online projects must be uploaded as ZIP bundles"}, 400)
            return super().do_POST()

    return Handler


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", type=Path, required=True)
    parser.add_argument("--template", type=Path, default=Path.cwd())
    parser.add_argument("--origin", required=True)
    parser.add_argument(
        "--images", type=Path, required=True, help="JSON array of approved image digests"
    )
    parser.add_argument("--monthly-model-budget", type=float, default=1.0)
    parser.add_argument("--port", type=int, default=8780)
    parser.add_argument("--key-file", type=Path)
    parser.add_argument("--revoke", help="Revoke an account access code and all sessions")
    parser.add_argument("--invite", help="Create one account; no server is started")
    parser.add_argument("--code-file", type=Path)
    args = parser.parse_args()
    if args.key_file:
        from .cli import load_key

        load_key(args.key_file)
    import fcntl

    args.state.mkdir(parents=True, exist_ok=True, mode=0o700)
    lock = (args.state / "online.lock").open("w")
    # Account creation is a SQLite transaction and can run while the server is up.
    if args.invite and args.revoke:
        parser.error("Choose --invite or --revoke")
    if not (args.invite or args.revoke):
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    store = OnlineStore(
        args.state,
        args.template,
        args.origin,
        json.loads(args.images.read_text()),
        args.monthly_model_budget,
        recover=not (args.invite or args.revoke),
    )
    if args.revoke:
        store.revoke(args.revoke)
        print("Access revoked; retained projects and run records were not deleted.")
        return
    if args.invite:
        if not args.code_file:
            parser.error("--invite requires --code-file; the code is never printed")
        store.invite(args.invite, args.code_file)
        print("Account created; access code saved to the requested private file.")
        return
    server = ThreadingHTTPServer(("127.0.0.1", args.port), online_handler(store))
    print(f"Online workspace backend listening on 127.0.0.1:{args.port}", flush=True)
    try:
        server.serve_forever()
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
