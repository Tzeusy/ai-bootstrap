# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Exercise persistence, feedback transport and detached server lifecycle."""
import json
import os
import subprocess
import sys
import tempfile
import threading
import time
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import progress_dashboard as dashboard
from dashboard_server import DashboardServer


class WorkspaceFixture:
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.folder = dashboard.workspace("demo", self.tmp.name)
        dashboard.initialize(self.folder, title="A useful outcome", actor="owner", repo_root=self.tmp.name)

    def snapshot(self):
        return {"summary": "Implementing the accepted scope", "phase": "implementation",
                "tasks": [{"id": "task-1", "title": "Ship behavior", "status": "in-progress", "detail": "Current work"}],
                "agents": [{"id": "reviewer", "status": "running", "summary": "Reviewing the package"}],
                "findings": ["Focused verification passes"]}

    def feedback(self, key="request-1", **kwargs):
        return {"client_id": key, "kind": "steer", "target": "loop", "text": "Prioritize verification", "revision": 0, **kwargs}


class WorkspaceTests(WorkspaceFixture, unittest.TestCase):
    def test_publish_resume_idempotence_and_manual_handover(self):
        """Spec: REQ-progress-dashboard-001, REQ-progress-dashboard-002."""
        handover = self.folder / "handover.md"
        before = handover.stat().st_mtime_ns
        with patch.object(dashboard, "now", return_value="2026-11-14T09:00:00+00:00"):
            dashboard.checkpoint(self.folder, self.snapshot(), 0)
        self.assertIn("task-1", (self.folder / "in-progress.md").read_text())
        document_mtime = (self.folder / "in-progress.md").stat().st_mtime_ns
        with patch.object(dashboard, "now", return_value="2026-11-14T09:10:00+00:00"):
            self.assertEqual(dashboard.checkpoint(self.folder, self.snapshot(), 1)["revision"], 1)
        self.assertEqual(dashboard.load(self.folder / "state.json")["agents"][0]["updated_at"], "2026-11-14T09:00:00+00:00")
        self.assertEqual((self.folder / "in-progress.md").stat().st_mtime_ns, document_mtime)
        dashboard.initialize(self.folder, title="Ignored resume title", actor="owner", repo_root=self.tmp.name)
        self.assertEqual(handover.stat().st_mtime_ns, before)
        with self.assertRaises(ValueError):
            dashboard.handover(self.folder, "Please hand off", "")
        dashboard.handover(self.folder, "# Handover\nResume task-1", "Owner explicitly requested handover")
        dashboard.checkpoint(self.folder, {"phase": "waiting"}, 1)
        self.assertEqual(handover.read_text(), "# Handover\nResume task-1")

    def test_revision_and_identity_conflicts_preserve_state(self):
        dashboard.checkpoint(self.folder, self.snapshot(), 0)
        before = (self.folder / "state.json").read_bytes()
        with self.assertRaisesRegex(ValueError, "revision conflict"):
            dashboard.checkpoint(self.folder, {"summary": "Stale writer"}, 0)
        with self.assertRaisesRegex(ValueError, "different actor"):
            dashboard.initialize(self.folder, title="Other", actor="foreign", repo_root=self.tmp.name)
        self.assertEqual((self.folder / "state.json").read_bytes(), before)

    def test_unknown_fields_cannot_write_handover_or_fabricate_usage(self):
        for incoming in ({"handover": "automatic"}, {"tokens": 1234}, {"tasks": [{"id": "a", "status": "complete"}]}):
            with self.subTest(incoming=incoming), self.assertRaises(ValueError):
                dashboard.checkpoint(self.folder, incoming, 0)
        self.assertEqual(dashboard.load(self.folder / "state.json")["revision"], 0)

    def test_feedback_retries_concurrent_writes_and_ack_survive_restart(self):
        """Spec: REQ-progress-dashboard-005."""
        row = dashboard.record_feedback(self.folder, self.feedback())
        self.assertEqual(dashboard.record_feedback(self.folder, self.feedback())["id"], row["id"])
        with self.assertRaisesRegex(ValueError, "different feedback"):
            dashboard.record_feedback(self.folder, self.feedback(text="changed"))
        with ThreadPoolExecutor(max_workers=6) as pool:
            list(pool.map(lambda i: dashboard.record_feedback(self.folder, self.feedback(f"request-{i}")), range(2, 22)))
        self.assertEqual(dashboard.pending(self.folder)["pending_count"], 21)
        dashboard.acknowledge(self.folder, 1, "Accepted; verification now takes priority")
        resumed = subprocess.run([sys.executable, str(SCRIPTS / "progress_dashboard.py"),
            "--root", self.tmp.name, "--slug", "demo", "status", "--since", "0"],
            capture_output=True, text=True, check=True)
        status = json.loads(resumed.stdout)
        self.assertEqual(status["pending_count"], 20)
        self.assertFalse(status["changed"])
        self.assertLessEqual(len(status["feedback"]), 10)
        self.assertNotIn("tasks", status)

    def test_feedback_disabled_stale_targets_and_invalid_revisions(self):
        for body in (self.feedback(target="gone"), self.feedback(revision=1), self.feedback(revision=True), []):
            with self.subTest(body=body), self.assertRaises(ValueError):
                dashboard.record_feedback(self.folder, body)
        state = dashboard.load(self.folder / "state.json")
        state["feedback_enabled"] = False
        dashboard.save(self.folder / "state.json", state)
        with self.assertRaisesRegex(ValueError, "disabled"):
            dashboard.record_feedback(self.folder, self.feedback())

    def test_acknowledgement_limit_preserves_readable_history(self):
        rows = [{**self.feedback(f"request-{i:04}", text="x" * 7200), "id": i + 1,
                 "created_at": dashboard.now(), "status": "pending", "response": None} for i in range(400)]
        dashboard.save_feedback(self.folder, rows)
        acknowledged = 0
        for row in rows:
            before = (self.folder / "feedback.json").read_bytes()
            try:
                dashboard.acknowledge(self.folder, row["id"], "r" * 8000)
                acknowledged += 1
            except ValueError as error:
                self.assertIn("history is full", str(error))
                self.assertEqual((self.folder / "feedback.json").read_bytes(), before)
                break
        self.assertGreater(acknowledged, 0)
        self.assertLess(acknowledged, len(rows))
        self.assertLessEqual((self.folder / "feedback.json").stat().st_size, 3 * 1024 * 1024)
        self.assertEqual(dashboard.pending(self.folder)["pending_count"], 400 - acknowledged)
        dashboard.acknowledge(self.folder, acknowledged + 1, "Deferred")

    def test_artifact_allowlist_and_symlink_boundaries(self):
        image = self.folder / "artifacts/diagram.svg"
        image.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        dashboard.checkpoint(self.folder, {"artifacts": [{"path": "diagram.svg", "label": "Architecture"}]}, 0)
        self.assertEqual(dashboard.artifact_path(self.folder, "diagram.svg"), image)
        (self.folder / "artifacts/escape.png").symlink_to(self.folder / "state.json")
        for path in ("../state.json", ".env", "escape.png", "page.html"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                dashboard.artifact_path(self.folder, path)
        outside = Path(self.tmp.name) / "outside"
        outside.write_text("do not change")
        (self.folder / "todo.md").unlink()
        (self.folder / "todo.md").symlink_to(outside)
        with self.assertRaises(ValueError):
            dashboard.checkpoint(self.folder, {}, 1)
        self.assertEqual(outside.read_text(), "do not change")

    def test_source_attachment_identity_and_no_double_count(self):
        source = str(self.folder / "parent.jsonl")
        dashboard.attach(self.folder, "owner", "codex", source)
        dashboard.checkpoint(self.folder, {"agents": [{"id": "child", "status": "running"}]}, 0)
        with self.assertRaisesRegex(ValueError, "double-count"):
            dashboard.attach(self.folder, "child", "codex", source)
        with self.assertRaises(ValueError):
            dashboard.attach(self.folder, "foreign", "codex", source)

    def test_server_start_preserves_usage_offsets_and_reports_unattached_agents(self):
        from loop_telemetry import UsageCollector

        source = self.folder / "parent.jsonl"
        source.write_text(json.dumps({"type": "event_msg", "timestamp": "2026-11-14T09:00:00Z", "payload": {
            "type": "token_count", "info": {"total_token_usage": {"input_tokens": 10,
            "cached_input_tokens": 5, "output_tokens": 3, "total_tokens": 13}}}}) + "\n")
        dashboard.attach(self.folder, "owner", "codex", str(source))
        sources = dashboard.load(self.folder / "sources.json")
        UsageCollector(self.folder).poll(sources)
        cache = self.folder / "telemetry-cache.json"
        before = cache.stat().st_mtime_ns
        dashboard.checkpoint(self.folder, {"agents": [{"id": "child", "status": "running"}]}, 0)
        server = DashboardServer(self.folder, "127.0.0.1", 0, "usage-check")
        try:
            self.assertEqual(cache.stat().st_mtime_ns, before)
            view = server.view()
            self.assertEqual(view["telemetry"]["totals"]["total_tokens"], 13)
            self.assertEqual(view["telemetry"]["coverage"], {"attached": 1, "measured": 1, "expected": 2})
            child = next(row for row in view["telemetry"]["agents"] if row["id"] == "child")
            self.assertIsNone(child["total_tokens"])
        finally:
            server.server_close()


class HttpTests(WorkspaceFixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.server = DashboardServer(self.folder, "127.0.0.1", 0, "test-capability")
        self.thread = threading.Thread(target=self.server.serve_forever, kwargs={"poll_interval": .01}, daemon=True)
        self.thread.start()
        self.addCleanup(self.shutdown)
        self.url = f"http://127.0.0.1:{self.server.server_port}/test-capability/"

    def shutdown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def request(self, path, body=None, headers=None):
        headers = {"Origin": self.url.split("/test-capability")[0], "X-Loop-Feedback": "1",
                   "Content-Type": "application/json", **(headers or {})}
        return urlopen(Request(self.url + path, data=json.dumps(body).encode() if body is not None else None,
                               headers=headers), timeout=3)

    def test_real_http_feedback_state_etag_and_xss_text(self):
        content = '<img src=x onerror="alert(1)">'
        dashboard.checkpoint(self.folder, {"summary": content}, 0)
        with self.request("") as reply:
            self.assertIn("script-src 'self'", reply.headers["Content-Security-Policy"])
            self.assertNotIn(content.encode(), reply.read())
        with self.request("api/state") as reply:
            state = json.load(reply)
            etag = reply.headers["ETag"]
        self.assertEqual(state["state"]["summary"], content)
        self.assertIsNone(state["telemetry"]["totals"]["total_tokens"])
        with self.assertRaises(HTTPError) as error:
            self.request("api/state", headers={"If-None-Match": etag})
        self.assertEqual(error.exception.code, 304)
        with self.request("api/feedback", self.feedback()) as reply:
            self.assertEqual(json.load(reply)["feedback"]["status"], "pending")
        self.assertEqual(dashboard.pending(self.folder)["pending_count"], 1)
        self.assertEqual((self.folder / "handover.md").read_text(), "# Handover\n\nNo handover has been requested.\n")

    def test_wrong_capability_origin_host_and_traversal_are_denied(self):
        for url in (self.url.replace("test-capability/", "wrong/api/state"), self.url + "../state.json",
                    self.url + "artifacts/%2E%2E%2Fstate.json"):
            with self.subTest(url=url), self.assertRaises(HTTPError):
                urlopen(url, timeout=3)
        for headers in ({"Origin": "https://elsewhere.invalid"}, {"Host": "evil.invalid"}, {"X-Loop-Feedback": "0"}):
            with self.subTest(headers=headers), self.assertRaises(HTTPError) as error:
                self.request("api/feedback", self.feedback(), headers)
            self.assertEqual(error.exception.code, 403)
        forwarded = {"Host": "localhost:18080", "Origin": "http://localhost:18080"}
        with self.request("api/feedback", self.feedback(), forwarded) as response:
            self.assertEqual(json.load(response)["feedback"]["status"], "pending")
        for host in ("localhost:0", "localhost:70000", "evil.invalid:18080", "localhost.evil.invalid:18080"):
            with self.subTest(host=host), self.assertRaises(HTTPError) as error:
                self.request("api/state", headers={"Host": host})
            self.assertEqual(error.exception.code, 403)

    def test_only_explicitly_published_artifacts_are_served(self):
        image = self.folder / "artifacts/diagram.svg"
        image.write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        with self.assertRaises(HTTPError):
            self.request("artifacts/diagram.svg")
        dashboard.checkpoint(self.folder, {"artifacts": [{"path": "diagram.svg"}]}, 0)
        with self.request("artifacts/diagram.svg") as reply:
            self.assertEqual(reply.read(), image.read_bytes())


class LifecycleTests(unittest.TestCase):
    def test_detached_start_reuse_stop_and_stale_pid_safety(self):
        """Spec: REQ-progress-dashboard-006."""
        with tempfile.TemporaryDirectory() as temporary:
            folder = dashboard.workspace("lifecycle", temporary)
            dashboard.initialize(folder, title="Lifecycle", actor="owner", repo_root=temporary)
            server = dashboard.serve(folder, "127.0.0.1", 0)
            try:
                reused = dashboard.serve(folder, "127.0.0.1", 0)
                self.assertTrue(reused["reused"])
                self.assertEqual(reused["url"], server["url"])
                self.assertTrue(dashboard.stop(folder)["stopped"])
                deadline = time.monotonic() + 3
                while dashboard.health(dashboard.load(folder / "server.json")) and time.monotonic() < deadline:
                    time.sleep(.02)
                self.assertFalse(dashboard.health(dashboard.load(folder / "server.json")))
                # A stale PID, even our own, must never receive a signal.
                info = dashboard.load(folder / "server.json")
                info["pid"] = os.getpid()
                dashboard.save(folder / "server.json", info)
                self.assertFalse(dashboard.stop(folder)["stopped"])
            finally:
                dashboard.stop(folder)


if __name__ == "__main__":
    unittest.main()
