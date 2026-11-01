#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Behavioral tests for the registry CLI's failure reporting and retries."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
spec = importlib.util.spec_from_file_location("coordinator_registry", SCRIPTS / "coordinator_registry.py")
assert spec is not None and spec.loader is not None
registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(registry)

TIMEOUT = "Error: failed to open database: dial tcp dolt.example.invalid:3307: i/o timeout\n"
REFUSED = "Error: dial tcp dolt.example.invalid:3307: connect: connection refused\n"
ID = "coordinator:claude-20261101-deadbeef"


def done(returncode: int = 0, stdout: str = "", stderr: str = "") -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess(args=["bd"], returncode=returncode, stdout=stdout, stderr=stderr)


class FakeBd:
    """Replay one scripted result per `bd` call and record each call's argv."""

    def __init__(self, *results: subprocess.CompletedProcess[str]) -> None:
        self.results = list(results)
        self.calls: list[list[str]] = []

    def __call__(self, argv: list[str], **_: object) -> subprocess.CompletedProcess[str]:
        self.calls.append(argv)
        return self.results.pop(0)


class ClassifyFailureTests(unittest.TestCase):
    def test_codes(self) -> None:
        table = {
            TIMEOUT: "server-timeout",
            "Error: context deadline exceeded": "server-timeout",
            "read tcp: connection reset by peer": "server-timeout",
            "write: broken pipe": "server-timeout",
            "[mysql] packets.go: unexpected EOF": "server-timeout",
            "driver: bad connection": "server-timeout",
            "operation TIMED OUT": "server-timeout",
            REFUSED: "connection-refused",
            "Error: issue not found": "command-failed",
            "": "command-failed",
        }
        for stderr, code in table.items():
            with self.subTest(stderr=stderr):
                self.assertEqual(registry.classify_failure(1, stderr), code)

    def test_a_command_that_never_started_is_a_plain_failure(self) -> None:
        self.assertEqual(registry.classify_failure(None, TIMEOUT), "command-failed")

    def test_detail_is_the_last_line_truncated(self) -> None:
        self.assertEqual(registry.last_line("first\n\n  last line  \n\n"), "last line")
        self.assertEqual(len(registry.last_line("x" * 500)), registry.DETAIL_LIMIT)
        self.assertEqual(registry.last_line(None), "")


class RetryTests(unittest.TestCase):
    def run_bd(self, fake: FakeBd) -> tuple[subprocess.CompletedProcess[str], int, mock.MagicMock]:
        with mock.patch.object(registry.subprocess, "run", fake), mock.patch.object(registry, "sleep") as sleep:
            result, attempts = registry.bd(["kv", "list", "--json"], Path("/repo"), ID)
        return result, attempts, sleep

    def test_a_transient_timeout_is_retried_until_it_succeeds(self) -> None:
        fake = FakeBd(done(1, stderr=TIMEOUT), done(0, stdout="{}"))
        result, attempts, sleep = self.run_bd(fake)
        self.assertEqual((result.returncode, attempts), (0, 2))
        self.assertEqual([call.args for call in sleep.call_args_list], [(1.0,)])

    def test_retries_stop_after_three_attempts(self) -> None:
        fake = FakeBd(*(done(1, stderr=TIMEOUT) for _ in range(3)))
        result, attempts, sleep = self.run_bd(fake)
        self.assertEqual((result.returncode, attempts), (1, 3))
        self.assertEqual([call.args for call in sleep.call_args_list], [(1.0,), (2.0,)])
        self.assertEqual(fake.results, [])

    def test_connection_refused_and_plain_failures_are_never_retried(self) -> None:
        for stderr in (REFUSED, "Error: unknown key"):
            with self.subTest(stderr=stderr):
                fake = FakeBd(done(1, stderr=stderr), done(0))
                result, attempts, sleep = self.run_bd(fake)
                self.assertEqual((result.returncode, attempts), (1, 1))
                sleep.assert_not_called()


class CliFailureReportTests(unittest.TestCase):
    def run_cli(self, argv: list[str], fake: FakeBd) -> tuple[int, dict[str, object]]:
        out = io.StringIO()
        with (
            mock.patch.object(registry.subprocess, "run", fake),
            mock.patch.object(registry, "sleep"),
            mock.patch.object(sys, "argv", ["coordinator_registry.py", *argv]),
            contextlib.redirect_stdout(out),
        ):
            code = registry.main()
        return code, json.loads(out.getvalue())

    def test_deregister_failure_names_cause_detail_and_attempts(self) -> None:
        fake = FakeBd(*(done(1, stderr="warning: slow\n" + TIMEOUT) for _ in range(3)))
        code, payload = self.run_cli(["deregister", "--repo-root", "/repo", "--id", ID], fake)
        self.assertEqual(code, 1)
        self.assertEqual(
            payload,
            {
                "action": "failed",
                "attempts": 3,
                "detail": TIMEOUT.strip(),
                "error": "server-timeout",
                "id": ID,
                "step": "kv-clear",
            },
        )

    def test_deregister_success_output_is_unchanged(self) -> None:
        code, payload = self.run_cli(["deregister", "--repo-root", "/repo", "--id", ID], FakeBd(done(0)))
        self.assertEqual((code, payload), (0, {"action": "cleared", "id": ID}))

    def test_register_reports_a_refused_listing_without_retrying(self) -> None:
        fake = FakeBd(done(1, stderr=REFUSED))
        code, payload = self.run_cli(["register", "--repo-root", "/repo", "--id", ID, "--wake-minutes", "20"], fake)
        self.assertEqual(code, 1)
        self.assertEqual(len(fake.calls), 1)
        self.assertEqual(
            {key: payload[key] for key in ("action", "attempts", "error", "step")},
            {"action": "failed", "attempts": 1, "error": "connection-refused", "step": "kv-list"},
        )
        self.assertEqual(payload["detail"], REFUSED.strip())

    def test_register_reports_a_failed_write_with_the_value_it_tried(self) -> None:
        fake = FakeBd(done(0, stdout="{}"), done(1, stdout="Error: permission denied\n"))
        code, payload = self.run_cli(["register", "--repo-root", "/repo", "--id", ID, "--wake-minutes", "20"], fake)
        self.assertEqual(code, 1)
        self.assertEqual(payload["step"], "kv-set")
        self.assertEqual(payload["error"], "command-failed")
        # bd sometimes reports on stdout only; the detail falls back to it.
        self.assertEqual(payload["detail"], "Error: permission denied")
        self.assertIn("expires_at", payload)

    def test_register_reports_unparseable_listing_as_invalid_json(self) -> None:
        fake = FakeBd(done(0, stdout="not json"))
        code, payload = self.run_cli(["register", "--repo-root", "/repo", "--id", ID, "--wake-minutes", "20"], fake)
        self.assertEqual(code, 1)
        self.assertEqual((payload["error"], payload["step"]), ("invalid-json", "kv-list"))


if __name__ == "__main__":
    unittest.main()
