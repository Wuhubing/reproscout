"""Loopback-only research workspace over the existing controller and review modules."""

from __future__ import annotations

import io
import json
import mimetypes
import os
import re
import secrets
import shutil
import subprocess
import sys
import threading
import time
import uuid
import zipfile
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from .lessons import change, content_hash, edit, lesson_path, propose
from .review import import_review, read
from .tasks import digest


def atomic(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name(path.name + "." + uuid.uuid4().hex + ".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n")
    temp.replace(path)


def process_alive(pid):
    if not isinstance(pid, int):
        return False
    try:
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,180}", value):
        raise ValueError("Invalid identifier")
    return value


class Workspace:
    def __init__(self, root: Path):
        self.root = root.resolve()
        self.state = self.root / ".reproscout"
        self.registry = self.root / "lessons/registry"
        self.lock = threading.RLock()
        self.processes = {}
        self.token = secrets.token_urlsafe(32)
        # A restart must not pretend an interrupted worker is still under supervision.
        for path in (self.state / "jobs").glob("*/job.json"):
            job = read(path.parent, path.name, {})
            if job.get("status") in ("running", "starting", "cancelling"):
                job.update(
                    status="interrupted",
                    error="Workspace restarted. Previous attempt retained; verify it before starting another.",
                )
                atomic(path, job)

    def projects(self):
        results = []
        for base in (self.root / "manifests/product", self.state / "projects"):
            for path in sorted(base.glob("*.json")):
                m = read(path.parent, path.name)
                p = (self.root / m.get("prepared_path", "")).resolve()
                results.append(
                    {
                        "id": path.stem,
                        "title": m["title"],
                        "task_id": m["task_id"],
                        "language": m.get("language", "Python / R"),
                        "questions": m["questions"],
                        "answer_types": m.get("answer_types", {}),
                        "split": m.get("split"),
                        "prepared": p.is_file() and p.is_relative_to(self.root / "data"),
                        "description": m.get("task_prompt", ""),
                        "path": str(path.relative_to(self.root)),
                    }
                )
        return results

    def project(self, key):
        identifier(key)
        for p in self.projects():
            if p["id"] == key:
                return read(self.root, p["path"])
        raise ValueError("Unknown prepared project")

    def register_project(self, manifest):
        required = (
            "task_id",
            "title",
            "questions",
            "answer_types",
            "prepared_path",
            "prepared_sha256",
            "image",
            "input_inventory",
            "task_prompt",
        )
        if not isinstance(manifest, dict) or any(k not in manifest for k in required):
            raise ValueError(
                "Manifest requires title, task_id, questions, answer_types, prepared archive/hash, image, inventory, and task_prompt"
            )
        key = identifier(manifest["task_id"])
        if any(p["id"] == key for p in self.projects()):
            raise ValueError("A project with that ID already exists")
        if manifest.get("split") not in ("user_project", "development", "official_train"):
            raise ValueError(
                "The workspace accepts user_project, development, or official_train projects"
            )
        self.validate_manifest(manifest)
        atomic(self.state / "projects" / f"{key}.json", manifest)
        return {"id": key}

    def validate_manifest(self, manifest):
        prepared = (self.root / manifest["prepared_path"]).resolve()
        if not prepared.is_relative_to(self.root / "data") or not prepared.is_file():
            raise ValueError(
                "Prepared archive must be a local file under this repository data/ directory"
            )
        if digest(prepared.read_bytes()) != manifest["prepared_sha256"]:
            raise ValueError("Prepared input checksum does not match")
        if "@sha256:" not in manifest["image"]:
            raise ValueError("Use an image pinned by SHA-256 digest")
        if not isinstance(manifest["questions"], dict) or not 1 <= len(manifest["questions"]) <= 30:
            raise ValueError("Supply 1–30 questions")
        if set(manifest["questions"]) != set(manifest["answer_types"]):
            raise ValueError("Every question requires an answer type")
        if any(
            t not in ("number", "string", "number_list") for t in manifest["answer_types"].values()
        ):
            raise ValueError("Unsupported answer type")
        if any(
            not isinstance(q, str) or not q.strip() or len(q) > 4000
            for q in manifest["questions"].values()
        ):
            raise ValueError("Questions must contain 1–4,000 characters")

    def lessons(self):
        result = []
        for p in sorted(self.registry.glob("*.json")):
            r = read(p.parent, p.name)
            md = p.with_suffix(".md")
            effective = r["status"]
            if effective == "approved" and (
                not md.exists() or r["approved_sha256"] != content_hash(md)
            ):
                effective = "needs_reapproval"
            result.append(
                {
                    **r,
                    "history": [
                        read(h.parent, h.name)
                        for h in sorted((self.registry / "history" / r["id"]).glob("*.json"))
                    ],
                    "effective_status": effective,
                    "content": md.read_text() if md.exists() else "",
                }
            )
        return result

    def job(self, key):
        return read(self.state / "jobs" / identifier(key), "job.json")

    def sources(self):
        result = {}
        for directory in (self.root / "reports/product-runs", self.root / "reports/workspace-runs"):
            if directory.exists():
                result.update({p.name: p for p in directory.iterdir() if p.is_dir()})
        for p in (self.state / "jobs").glob("*/job.json"):
            job = read(p.parent, p.name)
            if job.get("run_id"):
                run = self.root / "runs" / identifier(job["run_id"])
                if run.is_dir():
                    result[run.name] = run
        return result

    def source(self, key):
        run = self.sources().get(identifier(key))
        if not run:
            raise ValueError("Unknown workspace run")
        return run

    def reviewed_source(self, key):
        source = self.source(key)
        versions = sorted((self.state / "reviews" / key).glob("*/manual-review.json"))
        return versions[-1].parent if versions else source

    def jobs(self):
        return [read(p.parent, p.name) for p in sorted((self.state / "jobs").glob("*/job.json"))]

    def runs(self):
        result = []
        jobs = {j.get("run_id"): j for j in self.jobs()}
        for key, source in self.sources().items():
            m = read(source, "manifest.json", {})
            s = read(source, "summary.json", {})
            review = read(self.reviewed_source(key), "review-assessment.json", {})
            job = jobs.get(key, {})
            status = job.get("status", "finished")
            budget = read(source, "budget.json", {})
            records = review.get("review_history", []) + [review.get("manual_review") or {}]
            reviewed_questions = set(q for record in records for q in record.get("questions", {}))
            result.append(
                {
                    "id": key,
                    "title": m.get("title", key),
                    "task_id": m.get("task_id"),
                    "language": m.get("language", ""),
                    "status": status,
                    "outcome": review.get("outcome", "pending"),
                    "questions": len(m.get("questions", {})),
                    "reviewed": len(reviewed_questions),
                    "seconds": s.get(
                        "seconds", round(time.time() - job.get("started", time.time()), 1)
                    ),
                    "cost": s.get(
                        "cost_estimated_usd",
                        budget.get("estimated_billed", budget.get("spent_upper", 0)),
                    ),
                    "model_calls": s.get("model_calls", len(budget.get("calls", []))),
                    "scoring": review.get("scoring", "Not scored"),
                    "job_id": job.get("id"),
                    "historical": key not in jobs,
                }
            )
        return sorted(result, key=lambda x: x["id"], reverse=True)

    def details(self, key):
        source = self.source(key)
        reviewed = self.reviewed_source(key)
        m = read(source, "manifest.json", {})
        assessment = read(reviewed, "review-assessment.json", {})
        return {
            "reviews": assessment.get("review_history", [])
            + [assessment.get("manual_review") or {}],
            "run": next(r for r in self.runs() if r["id"] == key),
            "manifest": {
                k: m.get(k)
                for k in (
                    "title",
                    "task_id",
                    "questions",
                    "answer_types",
                    "split",
                    "language",
                    "task_prompt",
                )
            },
            "summary": read(source, "summary.json", {}),
            "assessment": read(reviewed, "review-assessment.json", {}),
            "diagnosis": read(source, "diagnosis.json", {}),
            "ledger": read(source, "execution-ledger.json", []),
            "budget": read(source, "budget.json", {}),
            "artifacts": read(source, "artifact-index.json", {}),
            "lessons": read(source, "lessons-snapshot.json", []),
            "blocker": read(source, "blocker.json"),
            "source_audit": read(source, "source-audit.json", {}),
            "steps": [read(source, p.name) for p in sorted(source.glob("step-*.json"))],
        }

    def start(self, data):
        with self.lock:
            if any(p.poll() is None for p in self.processes.values()) or any(
                j.get("status") == "interrupted" and process_alive(j.get("worker_pid"))
                for j in self.jobs()
            ):
                raise ValueError("A run is active. Finish or cancel it before starting another.")
            if not os.environ.get("OPENAI_API_KEY"):
                raise ValueError(
                    "API credential is not configured. Restart serve with --key-file or OPENAI_API_KEY."
                )
            manifest = self.project(data.get("project_id"))
            manifest = {
                **manifest,
                "questions": data.get("questions", manifest["questions"]),
                "answer_types": data.get("answer_types", manifest["answer_types"]),
            }
            manifest.pop("answers_path", None)
            self.validate_manifest(manifest)
            # No silent pulls or provisioning through the UI.
            image = subprocess.run(
                ["docker", "image", "inspect", manifest["image"]], capture_output=True, timeout=20
            )
            if image.returncode:
                raise ValueError(
                    "Author image is not available locally. Prepare it before launching."
                )
            calls = data.get("max_model_calls", 20)
            seconds = data.get("wall_time_seconds", 1800)
            cost = data.get("model_budget_usd", 1)
            if (
                type(calls) is not int
                or not 3 <= calls <= 20
                or type(seconds) is not int
                or not 60 <= seconds <= 1800
                or type(cost) not in (int, float)
                or not 0.01 <= cost <= 1
            ):
                raise ValueError("Budgets must be 3–20 calls, 60–1,800 seconds, and $0.01–$1.")
            ids = data.get("lesson_ids", [])
            if not isinstance(ids, list) or len(ids) > 20:
                raise ValueError("Invalid lesson selection")
            available = {r["id"]: r for r in self.lessons()}
            if any(
                key not in available or available[key]["effective_status"] != "approved"
                for key in ids
            ):
                raise ValueError("Only unchanged, approved lessons can be selected")
            key = uuid.uuid4().hex
            folder = self.state / "jobs" / key
            job = {
                "id": key,
                "project_id": data["project_id"],
                "title": manifest["title"],
                "status": "starting",
                "started": time.time(),
                "run_id": None,
                "lesson_ids": ids,
            }
            atomic(folder / "manifest.json", manifest)
            atomic(
                folder / "config.json",
                {
                    "execution_policy": "author_only",
                    "stop_on_offline_blocker": True,
                    "max_model_calls": calls,
                    "wall_time_seconds": seconds,
                    "model_budget_usd": cost,
                    "web_job_id": key,
                },
            )
            atomic(folder / "job.json", job)
            with (folder / "worker.log").open("w") as log:
                proc = subprocess.Popen(
                    [sys.executable, "-m", "reproscout.web_worker", str(self.root), key],
                    stdout=log,
                    stderr=log,
                    cwd=self.root,
                )
            self.processes[key] = proc
            threading.Thread(target=self.monitor, args=(key, proc), daemon=True).start()
            return job

    def monitor(self, key, proc):
        proc.wait()
        with self.lock:
            folder = self.state / "jobs" / key
            job = read(folder, "job.json", {})
            if job.get("status") in ("running", "starting", "cancelling"):
                job.update(
                    status="failed",
                    error="Worker exited before finalization. Partial files are retained.",
                )
                atomic(folder / "job.json", job)

    def cancel(self, key):
        with self.lock:
            job = self.job(key)
            if not job or job["status"] not in ("starting", "running", "cancelling"):
                raise ValueError("This job is not active")
            folder = self.state / "jobs" / key
            (folder / "cancel.requested").touch()
            if job.get("run_id"):
                (self.source(job["run_id"]) / "cancel.requested").touch()
            job["status"] = "cancelling"
            atomic(folder / "job.json", job)
            return job

    def review(self, key, record):
        with self.lock:
            source = self.source(key)
            if not (source / "summary.json").exists():
                raise ValueError("Wait for the run to finish before reviewing")
            version = f"{time.time_ns()}-{uuid.uuid4().hex[:8]}"
            target = self.state / "reviews" / identifier(key) / version
            shutil.copytree(
                source,
                target,
                ignore=shutil.ignore_patterns(
                    "logs", "*.eval", "manual-review.json", "review-assessment.json", "compose.yaml"
                ),
            )
            # Existing validator uses the actual run directory name; validate in a named child.
            named = target / key
            named.mkdir()
            for p in list(target.iterdir()):
                if p != named:
                    shutil.move(str(p), named / p.name)
            record = {
                **record,
                "run_id": key,
                "review_version": version,
                "recorded_at_unix": time.time(),
            }
            previous = read(self.reviewed_source(key), "review-assessment.json", {})
            records = previous.get("review_history", []) + (
                [previous["manual_review"]] if previous.get("manual_review") else []
            )
            atomic(named / "review-history.json", records)
            atomic(named / "review-import.json", record)
            try:
                import_review(named, named / "review-import.json")
                from .reporting import report

                report(named)
                for p in list(named.iterdir()):
                    shutil.move(str(p), target / p.name)
                named.rmdir()
            except Exception:
                shutil.rmtree(target)
                raise
            return {"saved": True, "version": version}

    def evidence(self, key, name):
        source = self.source(key)
        artifacts = read(source, "artifact-index.json", {})
        if name not in artifacts:
            raise ValueError("Unknown retained artifact")
        path = (source / name).resolve()
        if not path.is_relative_to((source / "artifacts").resolve()) or not path.is_file():
            raise ValueError("Unavailable artifact")
        if path.stat().st_size > 5_000_000:
            raise ValueError("Evidence is too large for inline preview; download the report")
        return path, artifacts[name]

    def export(self, key):
        source = self.reviewed_source(key)
        if not (source / "report.html").exists():
            raise ValueError("Report is not ready")
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as z:
            for p in source.rglob("*"):
                if (
                    p.is_file()
                    and not p.is_symlink()
                    and "logs" not in p.relative_to(source).parts
                    and p.suffix
                    in (".json", ".jsonl", ".html", ".md", ".txt", ".png", ".jpg", ".jpeg")
                ):
                    z.write(p, str(Path(key) / p.relative_to(source)))
        return buffer.getvalue()


def handler(workspace):
    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *_):
            pass

        def send(self, data, status=200, kind="application/json", attachment=None):
            encoded = json.dumps(data).encode() if kind == "application/json" else data
            self.send_response(status)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(encoded)))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Referrer-Policy", "no-referrer")
            self.send_header(
                "Content-Security-Policy",
                "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; frame-ancestors 'none'",
            )
            if attachment:
                self.send_header("Content-Disposition", f'attachment; filename="{attachment}"')
            self.end_headers()
            self.wfile.write(encoded)

        def allowed(self):
            port = self.server.server_port
            return self.headers.get("Host") in (f"127.0.0.1:{port}", f"localhost:{port}")

        def do_GET(self):
            if not self.allowed():
                return self.send({"error": "Loopback Host required"}, 403)
            try:
                url = urlsplit(self.path)
                parts = unquote(url.path).strip("/").split("/")
                if parts == ["api", "bootstrap"]:
                    return self.send(
                        {
                            "csrf": workspace.token,
                            "version": "0.8.0",
                            "credential_ready": bool(os.environ.get("OPENAI_API_KEY")),
                            "projects": workspace.projects(),
                            "runs": workspace.runs(),
                            "lessons": workspace.lessons(),
                            "jobs": workspace.jobs(),
                        }
                    )
                if parts == ["api", "runs"]:
                    return self.send({"runs": workspace.runs(), "jobs": workspace.jobs()})
                if len(parts) >= 3 and parts[:2] == ["api", "runs"]:
                    key = parts[2]
                    if len(parts) == 3:
                        return self.send(workspace.details(key))
                    if parts[3] == "evidence":
                        path, meta = workspace.evidence(
                            key, parse_qs(url.query).get("artifact", [""])[0]
                        )
                        if meta.get("kind") == "image":
                            return self.send(
                                path.read_bytes(),
                                kind=mimetypes.guess_type(path.name)[0]
                                or "application/octet-stream",
                            )
                        return self.send(
                            {
                                "name": path.name,
                                "text": path.read_text(errors="replace"),
                                "metadata": meta,
                            }
                        )
                    if parts[3] == "export":
                        return self.send(
                            workspace.export(key),
                            kind="application/zip",
                            attachment=f"{identifier(key)}.zip",
                        )
                    if parts[3] == "trace":
                        return self.send(
                            read(
                                workspace.source(key),
                                "trajectory.json",
                                {
                                    "messages": [],
                                    "note": "Trace export becomes available after finalization.",
                                },
                            )
                        )
                if parts[:1] == ["archive"]:
                    base = workspace.root / "reports"
                    path = (base / "/".join(parts[1:])).resolve()
                    if not path.is_relative_to(base) or not path.is_file():
                        return self.send({"error": "Not found"}, 404)
                    return self.send(
                        path.read_bytes(),
                        kind=mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                    )
                static = Path(__file__).parent / "static"
                path = (static / url.path.lstrip("/")).resolve()
                if not path.is_relative_to(static.resolve()):
                    return self.send({"error": "Not found"}, 404)
                if not path.is_file():
                    path = static / "index.html"
                return self.send(
                    path.read_bytes(),
                    kind=mimetypes.guess_type(path.name)[0] or "application/octet-stream",
                )
            except (ValueError, FileNotFoundError, KeyError) as exc:
                self.send({"error": str(exc)}, 400)

        def do_POST(self):
            port = self.server.server_port
            if (
                not self.allowed()
                or self.headers.get("X-ReproScout-CSRF") != workspace.token
                or self.headers.get("Origin")
                not in (f"http://127.0.0.1:{port}", f"http://localhost:{port}")
            ):
                return self.send({"error": "Same-origin workspace request required"}, 403)
            try:
                size = int(self.headers.get("Content-Length", 0))
                if not 0 < size <= 500_000:
                    raise ValueError("Invalid request size")
                data = json.loads(self.rfile.read(size))
                parts = unquote(urlsplit(self.path).path).strip("/").split("/")
                if parts == ["api", "runs"]:
                    return self.send(workspace.start(data), 201)
                if parts == ["api", "projects"]:
                    return self.send(workspace.register_project(data), 201)
                if len(parts) == 4 and parts[:2] == ["api", "jobs"] and parts[3] == "cancel":
                    return self.send(workspace.cancel(parts[2]))
                if len(parts) == 4 and parts[:2] == ["api", "runs"] and parts[3] == "review":
                    return self.send(workspace.review(parts[2], data), 201)
                if parts == ["api", "lessons"]:
                    source = workspace.source(data["source_run"])
                    result = propose(
                        workspace.registry,
                        source,
                        data["id"],
                        data["action"],
                        data["applicability"],
                        data["evidence"],
                    )
                    return self.send(result, 201)
                if len(parts) == 4 and parts[:2] == ["api", "lessons"]:
                    with workspace.lock:
                        key, action = parts[2:]
                        path = lesson_path(workspace.registry, key)
                        if not path.exists():
                            raise ValueError("Unknown lesson")
                        if action == "edit":
                            if (
                                not isinstance(data.get("content"), str)
                                or not 1 <= len(data["content"]) <= 20_000
                            ):
                                raise ValueError("Lesson must contain 1–20,000 characters")
                            edit(workspace.registry, key, data["content"])
                            return self.send(
                                {"saved": True, "note": "Changed content requires approval again."}
                            )
                        if (
                            action not in ("approve", "disable")
                            or not data.get("reviewer", "").strip()
                        ):
                            raise ValueError("Valid action and reviewer identity are required")
                        return self.send(
                            change(
                                workspace.registry,
                                key,
                                "approved" if action == "approve" else "disabled",
                                data["reviewer"],
                            )
                        )
                self.send({"error": "Unknown endpoint"}, 404)
            except (ValueError, KeyError, TypeError, OSError, subprocess.SubprocessError) as exc:
                self.send({"error": str(exc)}, 400)

    return Handler


def serve(root, port=8765, key_file=None):
    if key_file:
        from .cli import load_key

        load_key(key_file)
    import fcntl

    (root / ".reproscout").mkdir(exist_ok=True)
    lock = (root / ".reproscout/server.lock").open("w")
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        raise ValueError(
            "Another workspace server is already running for this repository"
        ) from None
    workspace = Workspace(root)
    server = ThreadingHTTPServer(("127.0.0.1", port), handler(workspace))
    print(f"ReproScout workspace: http://127.0.0.1:{server.server_port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        for job in workspace.jobs():
            if job.get("status") in ("starting", "running", "cancelling"):
                workspace.cancel(job["id"])
    finally:
        server.server_close()
