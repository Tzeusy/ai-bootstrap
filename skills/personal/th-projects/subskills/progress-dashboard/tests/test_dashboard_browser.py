# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.61.0"]
# ///
"""Browser journeys against the real progress server, without model calls.

Run with ``uv run --script tests/test_dashboard_browser.py``. Missing Chromium
is an explicit skip; PLAYWRIGHT_CHROMIUM may name a local Chrome executable.
"""
from __future__ import annotations

import glob
import json
import os
import shutil
import sys
import tempfile
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import patch

try:
    from playwright.sync_api import Error as PlaywrightError
    from playwright.sync_api import expect, sync_playwright
except ImportError:
    sync_playwright = None

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
import progress_dashboard as model
from dashboard_server import DashboardServer


@unittest.skipIf(sync_playwright is None, "Playwright is not installed")
class DashboardBrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        candidates = [os.environ.get("PLAYWRIGHT_CHROMIUM"), None,
                      shutil.which("google-chrome"), shutil.which("chromium"),
                      *sorted(glob.glob(os.path.expanduser("~/.cache/ms-playwright/chromium-*/chrome-linux*/chrome")), reverse=True)]
        launch_errors = []
        for executable in dict.fromkeys(candidates):
            try:
                cls.browser = cls.playwright.chromium.launch(executable_path=executable) if executable else cls.playwright.chromium.launch()
                return
            except PlaywrightError as error:
                launch_errors.append(str(error).splitlines()[0])
        cls.playwright.stop()
        raise unittest.SkipTest("no launchable Chromium for Playwright: " + "; ".join(dict.fromkeys(launch_errors)))

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.folder = model.workspace("browser-session", self.root)
        model.initialize(self.folder, title="A useful progress workspace", actor="parent", repo_root=str(self.root))
        self.snapshot = {
            "summary": "The parent owns the outcome; this page owns its readable projection.",
            "phase": "Implementation",
            "tasks": [{"id": "work", "title": "Implement the workspace", "status": "in-progress", "detail": "Persist progress and feedback.", "evidence": "Focused checks"},
                      {"id": "review", "title": "Independently verify", "status": "todo", "detail": "Review the complete behavior.", "evidence": ""}],
            "findings": ["Unknown counters stay unknown."],
            "agents": [{"id": "reviewer", "name": "Independent reviewer", "role": "Verifier", "status": "waiting", "task": "Review the workspace", "summary": "Waiting for a reviewable checkpoint.", "model": "example", "updated_at": model.now()}],
        }
        model.checkpoint(self.folder, self.snapshot, 0)
        self.server = DashboardServer(self.folder, "127.0.0.1", 0, "browser-fixture")
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.addCleanup(self.stop_server)
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 900}, reduced_motion="reduce")
        self.addCleanup(self.context.close)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on("pageerror", lambda error: self.errors.append(str(error)))
        self.page.goto(f"http://127.0.0.1:{self.server.server_port}/{self.server.instance}/")
        self.page.get_by_role("heading", name="A useful progress workspace", exact=True).wait_for()

    def stop_server(self):
        self.server.stopping.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=3)

    def tearDown(self):
        self.assertEqual(self.errors, [])

    def saved(self):
        return model.load(self.folder / "feedback.json")

    def refresh(self):
        self.page.get_by_role("button", name="Refresh", exact=True).click()

    def saved_result(self):
        expect(self.page.locator("#feedback-result")).to_contain_text("Saved.")

    def test_progress_feedback_acknowledgement_and_safe_content(self):
        page = self.page
        self.assertEqual(page.locator("#token-total").inner_text(), "Unknown")
        page.locator("#feedback-text").fill("Keep this bounded and token efficient.")
        model.checkpoint(self.folder, {"findings": ["<img src=x onerror=window.unsafe=true>"]}, 1)
        self.refresh()
        page.locator("#findings").get_by_text("<img src=x onerror=window.unsafe=true>", exact=True).wait_for()
        self.assertEqual(page.locator("#feedback-text").input_value(), "Keep this bounded and token efficient.")
        self.assertIsNone(page.evaluate("window.unsafe"))
        self.assertEqual(page.locator("#findings img").count(), 0)
        page.reload()
        page.get_by_role("heading", name="A useful progress workspace", exact=True).wait_for()
        self.assertEqual(page.locator("#feedback-text").input_value(), "Keep this bounded and token efficient.")
        page.locator("#feedback-target").select_option("reviewer")
        page.get_by_role("button", name="Send feedback", exact=True).click()
        self.saved_result()
        rows = self.saved()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["target"], "reviewer")
        model.acknowledge(self.folder, rows[0]["id"], "Kept the scope bounded; background refresh does not wake the model.")
        self.refresh()
        page.get_by_text("Kept the scope bounded; background refresh does not wake the model.", exact=True).wait_for()
        self.assertEqual(page.locator("#feedback-text").input_value(), "")
        self.assertEqual((self.folder / "handover.md").read_text(), "# Handover\n\nNo handover has been requested.\n")

    def test_ambiguous_save_retry_is_idempotent_and_a_slow_save_preserves_new_input(self):
        page = self.page
        first = True

        def interrupt_confirmation(route):
            nonlocal first
            if first:
                first = False
                route.fetch()  # The real backend saves the message; its confirmation is lost.
                route.fulfill(status=503, json={"error": "Confirmation interrupted"})
            else:
                route.continue_()

        page.route("**/api/feedback", interrupt_confirmation)
        page.locator("#feedback-text").fill("One message even if confirmation is interrupted.")
        page.get_by_role("button", name="Send feedback", exact=True).click()
        expect(page.locator("#feedback-result")).to_contain_text("Your draft is kept")
        self.assertEqual(len(self.saved()), 1)
        page.get_by_role("button", name="Send feedback", exact=True).click()
        self.saved_result()
        self.assertEqual(len(self.saved()), 1)
        original = model.record_feedback

        def slow_record(*args, **kwargs):
            row = original(*args, **kwargs)
            time.sleep(0.8)
            return row

        with patch.object(model, "record_feedback", slow_record):
            page.locator("#feedback-text").fill("The message being saved.")
            page.get_by_role("button", name="Send feedback", exact=True).click()
            self.assertFalse(page.locator("#feedback-text").is_disabled())
            page.locator("#feedback-text").fill("A new thought while saving.")
            self.saved_result()
        self.assertEqual(page.locator("#feedback-text").input_value(), "A new thought while saving.")
        self.assertEqual(len(self.saved()), 2)

    def test_partial_usage_stays_visible_and_small_screens_fit(self):
        source = self.root / "usage.jsonl"
        source.write_text(json.dumps({"type": "event_msg", "timestamp": model.now(), "payload": {"type": "token_count", "info": {"total_token_usage": {"input_tokens": 100, "cached_input_tokens": 80, "output_tokens": 23, "total_tokens": 123}}}}) + "\n")
        model.attach(self.folder, "parent", "codex", str(source))
        model.attach(self.folder, "reviewer", "codex", str(self.root / "waiting.jsonl"))
        self.server.telemetry = self.server.collector.poll(model.load(self.folder / "sources.json"))
        self.refresh()
        expect(self.page.locator("#token-total")).to_have_text("123")
        self.assertIn("1 of 2", self.page.locator("#token-caption").inner_text())
        self.assertIn("Token usage unknown", self.page.locator("#agent-list").inner_text())
        self.page.emulate_media(color_scheme="dark")
        for width in (320, 390, 650, 768, 970, 1280):
            self.page.set_viewport_size({"width": width, "height": 900})
            self.assertTrue(self.page.evaluate("document.documentElement.scrollWidth <= innerWidth"), f"horizontal page overflow at {width}px")


if __name__ == "__main__":
    unittest.main()
