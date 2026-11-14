# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""HTTP transport and background telemetry for one progress workspace."""
from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import signal
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit

import progress_dashboard as model
from loop_telemetry import UsageCollector

ASSETS = Path(__file__).resolve().parent.parent / "assets/web"
MAX_BODY = 16 * 1024


class DashboardServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, folder: Path, bind: str, port: int, instance: str):
        super().__init__((bind, port), Handler)
        self.folder = folder
        self.instance = instance
        self.prefix = "/" + instance + "/"
        self.telemetry_lock = threading.Lock()
        self.stopping = threading.Event()
        self.collector = UsageCollector(folder)
        with model.lock(folder):
            sources = model.load(folder / "sources.json", [])
        self.telemetry = self.collector.poll(sources)
        self.allowed_hosts = {f"{bind}:{self.server_port}"}
        if bind == "127.0.0.1":
            self.allowed_hosts.add(f"localhost:{self.server_port}")

    def collect(self):
        while not self.stopping.is_set():
            try:
                with model.lock(self.folder):
                    sources = model.load(self.folder / "sources.json", [])
                telemetry = self.collector.poll(sources)
                with self.telemetry_lock:
                    self.telemetry = telemetry
            except (ValueError, OSError) as error:
                # Metadata/counter failures must be visible without logging transcript content.
                with self.telemetry_lock:
                    self.telemetry = {"agents": [], "totals": None,
                        "coverage": {"attached": 0, "measured": 0}, "sampled_at": model.now(),
                        "error": type(error).__name__}
            self.stopping.wait(3)

    def view(self) -> dict:
        with model.lock(self.folder):
            state = model.load(self.folder / "state.json")
            documents = model.documents(state)
            handover = self.folder / "handover.md"
            if handover.is_symlink():
                raise ValueError("handover must not be a symlink")
            documents["handover.md"] = handover.read_text(encoding="utf-8")
            feedback = model.load(self.folder / "feedback.json", [])
        with self.telemetry_lock:
            telemetry = {**self.telemetry, "agents": list(self.telemetry["agents"]),
                         "coverage": dict(self.telemetry["coverage"])}
        expected = {state["actor"], *[agent["id"] for agent in state["agents"]]}
        observed = {row["id"] for row in telemetry["agents"]}
        for agent_id in sorted(expected - observed):
            telemetry["agents"].append({"id": agent_id, "provider": None, "status": "unknown",
                "input_tokens": None, "cached_input_tokens": None, "output_tokens": None,
                "total_tokens": None, "context_tokens": None, "observed_at": None,
                "reason": "not-attached"})
        telemetry["coverage"]["expected"] = len(expected | observed)
        # Local transcript locators and feedback idempotency keys are not browser data.
        return {"state": state, "documents": documents, "telemetry": telemetry,
                "feedback": [{k: v for k, v in row.items() if k != "client_id"} for row in feedback],
                "feedback_enabled": state["feedback_enabled"]}


class Handler(BaseHTTPRequestHandler):
    server: DashboardServer

    def log_message(self, *_args):
        pass  # Access logs would persist capability URLs and feedback details.

    def respond(self, status: int, body=b"", mime="application/json", *, etag=None, attachment=False):
        self.send_response(status)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Content-Security-Policy", "default-src 'none'; script-src 'self'; style-src 'self'; "
                         "img-src 'self'; connect-src 'self'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'")
        if etag:
            self.send_header("ETag", etag)
        if attachment:
            self.send_header("Content-Disposition", "attachment")
        self.end_headers()
        if body:
            self.wfile.write(body)

    def json(self, status, value):
        self.respond(status, json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode())

    def route(self) -> str | None:
        if self.headers.get("Host") not in self.server.allowed_hosts:
            self.json(403, {"error": "unrecognized host"})
            return None
        path = urlsplit(self.path).path
        if not path.startswith(self.server.prefix):
            self.json(404, {"error": "not found"})
            return None
        return unquote(path[len(self.server.prefix):])

    def do_GET(self):
        route = self.route()
        if route is None:
            return
        try:
            if route == "api/health":
                self.json(200, {"instance": self.server.instance, "pid": os.getpid()})
            elif route == "api/state":
                body = json.dumps(self.server.view(), ensure_ascii=False, sort_keys=True).encode()
                etag = '"' + hashlib.sha256(body).hexdigest() + '"'
                if self.headers.get("If-None-Match") == etag:
                    self.respond(304, etag=etag)
                else:
                    self.respond(200, body, etag=etag)
            elif route in ("", "index.html", "style.css", "app.js"):
                path = ASSETS / (route or "index.html")
                self.respond(200, path.read_bytes(), mimetypes.guess_type(path)[0] or "text/plain")
            elif route.startswith("artifacts/"):
                relative = route[len("artifacts/"):]
                with model.lock(self.server.folder):
                    state = model.load(self.server.folder / "state.json")
                    if relative not in {r["path"] for r in state["artifacts"]}:
                        self.json(404, {"error": "artifact is not published"})
                        return
                    path = model.artifact_path(self.server.folder, relative)
                    if path.stat().st_size > 20 * 1024 * 1024:
                        raise ValueError("artifact exceeds 20MiB")
                    body = path.read_bytes()
                mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
                self.respond(200, body, mime, attachment=path.suffix in (".pdf", ".excalidraw"))
            else:
                self.json(404, {"error": "not found"})
        except (ValueError, OSError, KeyError):
            self.json(409, {"error": "workspace content unavailable; inspect the local state"})

    def do_POST(self):
        route = self.route()
        if route is None:
            return
        if route != "api/feedback":
            self.json(404, {"error": "not found"})
            return
        expected_origin = "http://" + self.headers.get("Host", "")
        if (self.headers.get("Origin") != expected_origin or self.headers.get("X-Loop-Feedback") != "1"
                or self.headers.get("Content-Type", "").split(";")[0] != "application/json"):
            self.json(403, {"error": "feedback requires the same-origin dashboard form"})
            return
        try:
            length = int(self.headers.get("Content-Length", "-1"))
            if not 0 < length <= MAX_BODY:
                self.json(413, {"error": "feedback body is empty or too large"})
                return
            self.connection.settimeout(5)
            body = json.loads(self.rfile.read(length))
            row = model.record_feedback(self.server.folder, body)
            self.json(200, {"feedback": {k: v for k, v in row.items() if k != "client_id"}})
        except (ValueError, UnicodeError, TypeError) as error:
            self.json(400, {"error": str(error)})
        except OSError:
            self.json(503, {"error": "feedback could not be persisted; retry with the same request"})


def run(folder: Path, bind: str, port: int, instance: str):
    server = DashboardServer(folder, bind, port, instance)
    info = {"pid": os.getpid(), "instance": instance, "bind": bind, "port": server.server_port,
            "url": f"http://{bind}:{server.server_port}/{instance}/"}
    model.save(folder / "server.json", info)
    collector = threading.Thread(target=server.collect, daemon=True)
    collector.start()

    def shutdown(_signum, _frame):
        server.stopping.set()
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    try:
        server.serve_forever(poll_interval=0.1)
    finally:
        server.stopping.set()
        server.server_close()
        collector.join(timeout=5)
