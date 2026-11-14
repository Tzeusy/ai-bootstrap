# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Usage totals stay honest across streaming events, restarts and damaged logs."""

from __future__ import annotations

import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

SCRIPT = Path(__file__).resolve().parents[1] / "scripts/loop_telemetry.py"
SPEC = importlib.util.spec_from_file_location("loop_telemetry", SCRIPT)
telemetry = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(telemetry)


def codex(input_tokens=100, cached=20, output_tokens=5, timestamp="2026-11-14T10:00:00Z"):
    return {"type": "event_msg", "timestamp": timestamp, "payload": {
        "type": "token_count", "info": {
            "total_token_usage": {"input_tokens": input_tokens, "cached_input_tokens": cached,
                                  "output_tokens": output_tokens, "total_tokens": input_tokens + output_tokens},
            "last_token_usage": {"total_tokens": 33},
        }
    }}


def claude(message_id="message-a", input_tokens=30, read=40, write=50, output_tokens=10):
    return {"type": "assistant", "timestamp": "2026-11-14T10:01:00Z", "message": {
        "id": message_id, "content": [{"type": "text", "text": "private-message-never-cached"}],
        "usage": {"input_tokens": input_tokens, "cache_read_input_tokens": read,
                  "cache_creation_input_tokens": write, "output_tokens": output_tokens},
    }}


class UsageCollectorTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.workspace = self.root / "workspace"
        self.log = self.root / "session.jsonl"
        self.source = {"id": "parent", "provider": "codex", "path": str(self.log)}
        self.collector = telemetry.UsageCollector(self.workspace)

    def write(self, *records, path=None, mode="w"):
        with (path or self.log).open(mode, encoding="utf-8") as stream:
            for record in records:
                stream.write(json.dumps(record, separators=(",", ":")) + "\n")

    def poll(self, *sources):
        return self.collector.poll(list(sources or (self.source,)))

    def test_codex_uses_latest_cumulative_sample_instead_of_summing_duplicates(self):
        """Spec: REQ-progress-dashboard-004."""
        self.write(codex(), codex(), {"type": "event_msg", "payload": {"type": "token_count", "info": None}})
        result = self.poll()
        self.assertEqual(result["totals"]["total_tokens"], 105)
        self.assertEqual(result["agents"][0]["context_tokens"], 33)
        self.write(codex(150, 60, 15), mode="a")
        result = self.poll()
        self.assertEqual(result["totals"], {"input_tokens": 150, "cached_input_tokens": 60,
                                            "output_tokens": 15, "total_tokens": 165})
        self.assertEqual(result["agents"][0]["status"], "measured")
        self.assertEqual(result["agents"][0]["observed_at"], "2026-11-14T10:00:00+00:00")

    def test_claude_deduplicates_messages_and_counts_cache_reads_and_writes_once(self):
        self.source["provider"] = "claude"
        self.write(claude(), claude(output_tokens=15), claude(output_tokens=12))
        result = self.poll()
        self.assertEqual(result["totals"], {"input_tokens": 120, "cached_input_tokens": 40,
                                            "output_tokens": 15, "total_tokens": 135})
        self.write(claude(message_id="message-b", input_tokens=5, read=7, write=3, output_tokens=2), mode="a")
        result = self.poll()
        self.assertEqual(result["totals"]["total_tokens"], 152)
        self.assertEqual(result["totals"]["cached_input_tokens"], 47)
        cache = self.collector.cache_path.read_text()
        self.assertNotIn("private-message-never-cached", cache)
        self.assertNotIn("message-a", cache)

    def test_codex_native_thread_records_exclude_fork_history_and_outlive_lagging_events(self):
        """Spec: REQ-progress-dashboard-004."""
        own = "00000000-0000-4000-8000-000000000001"
        foreign = "00000000-0000-4000-8000-000000000002"
        self.source["thread_id"] = own

        def native(thread, total, stamp="2026-11-14T10:10:00Z", ordinal=30):
            return {"type": "token_usage_record", "timestamp": stamp, "ordinal": ordinal, "payload": {
                "thread_id": thread, "thread_token_usage": {"input_tokens": total - 5,
                "cached_input_tokens": 20, "output_tokens": 5, "total_tokens": total},
                "usage": {"total_tokens": 33}}}

        self.write({"type": "session_meta", "payload": {"id": own, "subagent_history_start_ordinal": 20}},
                   {**codex(9999), "ordinal": 10}, native(foreign, 99999, ordinal=11))
        self.assertIsNone(self.poll()["totals"]["total_tokens"])
        self.write(native(own, 105), native(foreign, 99999), {**codex(50), "ordinal": 31}, mode="a")
        measured = self.poll()
        self.assertEqual(measured["totals"]["total_tokens"], 105)
        self.assertEqual(measured["agents"][0]["observed_at"], "2026-11-14T10:10:00+00:00")
        self.collector = telemetry.UsageCollector(self.workspace)
        self.write({**codex(9999), "ordinal": 32},
                   native(own, 205, "2026-11-14T10:11:00Z", ordinal=33), mode="a")
        self.assertEqual(self.poll()["totals"]["total_tokens"], 205)

    def test_restart_reuses_offsets_and_unchanged_polls_do_not_rewrite_cache(self):
        """Spec: REQ-progress-dashboard-003."""
        self.write(codex())
        empty = telemetry._empty

        def append_after_stat(source, identity):
            self.write(codex(150, 60, 15), mode="a")
            return empty(source, identity)

        with mock.patch.object(telemetry, "_empty", side_effect=append_after_stat):
            self.assertEqual(self.poll()["totals"]["total_tokens"], 105)
        cache = json.loads(self.collector.cache_path.read_text())
        entry = cache["sources"]["parent"]
        self.assertEqual(entry["offset"], entry["size_seen"])
        self.assertLess(entry["offset"], self.log.stat().st_size)
        self.assertEqual(self.poll()["totals"]["total_tokens"], 165)
        # Older collectors could consume an append after fstat and persist
        # offset > size_seen. That valid legacy cache must resume without replay.
        cache = json.loads(self.collector.cache_path.read_text())
        cache["sources"]["parent"]["size_seen"] -= 1
        self.collector.cache_path.write_text(json.dumps(cache))
        with mock.patch.object(telemetry, "_consume", wraps=telemetry._consume) as consume:
            self.assertEqual(self.poll()["totals"]["total_tokens"], 165)
        self.assertEqual(consume.call_args.args[1], b"")
        collector = telemetry.UsageCollector(self.workspace)
        with mock.patch.object(telemetry, "_consume", wraps=telemetry._consume) as consume, \
                mock.patch.object(collector, "_save", wraps=collector._save) as save:
            result = collector.poll([self.source])
        self.assertEqual(result["totals"]["total_tokens"], 165)
        self.assertEqual(consume.call_args.args[1], b"")
        save.assert_not_called()
        self.assertEqual(json.loads(collector.cache_path.read_text())["sources"]["parent"]["offset"],
                         self.log.stat().st_size)
        self.assertEqual(collector.cache_path.stat().st_mode & 0o777, 0o600)

    def test_incomplete_line_recovers_on_append_without_caching_text(self):
        raw = json.dumps(codex()).encode()
        self.log.write_bytes(raw[:len(raw) // 2])
        first = self.poll()
        self.assertEqual(first["agents"][0]["status"], "catching-up")
        self.assertIsNone(first["totals"]["total_tokens"])
        cache = json.loads(self.collector.cache_path.read_text())
        self.assertEqual(cache["sources"]["parent"]["offset"], 0)
        with self.log.open("ab") as stream:
            stream.write(raw[len(raw) // 2:] + b"\n")
        self.assertEqual(self.poll()["totals"]["total_tokens"], 105)

    def test_missing_log_does_not_present_previously_recorded_usage_as_current(self):
        self.write(codex())
        self.poll()
        self.log.rename(self.root / "away.jsonl")
        result = self.poll()
        self.assertEqual(result["agents"][0]["status"], "error")
        self.assertEqual(result["agents"][0]["reason"], "unreadable-source")
        self.assertIsNone(result["totals"]["total_tokens"])
        (self.root / "away.jsonl").rename(self.log)
        self.assertEqual(self.poll()["totals"]["total_tokens"], 105)

    def test_rotation_truncation_and_same_size_replacement_reset_old_counters(self):
        self.write(codex())
        self.poll()
        self.log.rename(self.root / "old.jsonl")
        self.write(codex(10, 2, 1))
        self.assertEqual(self.poll()["totals"]["total_tokens"], 11)
        self.log.write_text("")
        result = self.poll()
        self.assertEqual(result["agents"][0]["status"], "unknown")
        self.assertIsNone(result["totals"]["total_tokens"])
        self.write(codex())
        self.poll()
        # Same inode and byte length, but the checked tail no longer matches.
        self.write(codex(101, 20, 5))
        self.assertEqual(self.poll()["totals"]["total_tokens"], 106)

    def test_per_poll_read_budget_advances_gradually_and_exposes_partial_coverage(self):
        self.write(codex(), *[{"type": "ignored", "data": "x" * 30}] * 20, codex(150, 60, 15))
        with mock.patch.object(telemetry, "MAX_BYTES_PER_POLL", 512):
            first = self.poll()
            cache = json.loads(self.collector.cache_path.read_text())
            self.assertLessEqual(cache["sources"]["parent"]["offset"], 512)
            self.assertEqual(first["agents"][0]["status"], "catching-up")
            self.assertEqual(first["agents"][0]["total_tokens"], 105)
            self.assertIsNone(first["totals"]["total_tokens"])
            self.assertEqual(first["coverage"], {"attached": 1, "measured": 0})
            for _ in range(10):
                final = self.poll()
                if final["agents"][0]["status"] == "measured":
                    break
        self.assertEqual(final["totals"]["total_tokens"], 165)

    def test_only_later_cumulative_samples_recover_uncertainty_after_bounded_line_skips(self):
        for provider in ("codex", "claude"):
            with self.subTest(provider=provider), \
                    mock.patch.object(telemetry, "MAX_BYTES_PER_POLL", 1024), \
                    mock.patch.object(telemetry, "MAX_LINE_BYTES", 512):
                self.source["provider"] = provider
                self.write(codex() if provider == "codex" else claude())
                self.assertEqual(self.poll()["agents"][0]["status"], "measured")
                self.write({"type": "response_item", "content": "x" * 1800}, mode="a")
                start = json.loads(self.collector.cache_path.read_text())["sources"]["parent"]["offset"]
                for _ in range(10):
                    result = self.poll()
                    offset = json.loads(self.collector.cache_path.read_text())["sources"]["parent"]["offset"]
                    self.assertLessEqual(offset - start, 1024)
                    start = offset
                    if offset == self.log.stat().st_size:
                        break
                self.assertEqual(result["agents"][0]["reason"], "oversized-log-line")
                self.assertIsNone(result["totals"]["total_tokens"])
                self.assertNotIn("xxx", self.collector.cache_path.read_text())
                self.collector = telemetry.UsageCollector(self.workspace)
                self.assertEqual(self.poll()["agents"][0]["status"], "error")
                self.write(codex(150, 60, 15) if provider == "codex" else claude(message_id="message-b"),
                           mode="a")
                recovered = self.poll()
                if provider == "claude":
                    self.assertEqual(recovered["agents"][0]["status"], "error")
                    self.assertIsNone(recovered["totals"]["total_tokens"])
                    continue
                self.assertEqual(recovered["agents"][0]["status"], "measured")
                self.assertEqual(recovered["totals"]["total_tokens"], 165)
                with self.log.open("a") as stream:
                    stream.write("malformed JSON record\n")
                self.assertEqual(self.poll()["agents"][0]["reason"], "malformed-usage-log")
                self.write(codex(150, 60, 15), mode="a")
                self.assertEqual(self.poll()["totals"]["total_tokens"], 165)
                self.collector = telemetry.UsageCollector(self.workspace)
                with mock.patch.object(telemetry, "_consume", wraps=telemetry._consume) as consume:
                    self.assertEqual(self.poll()["totals"]["total_tokens"], 165)
                self.assertEqual(consume.call_args.args[1], b"")

    def test_malformed_counters_fail_honestly_instead_of_reusing_or_fabricating_totals(self):
        self.write(codex(), codex(10, 2, 1))
        result = self.poll()
        self.assertEqual(result["agents"][0]["status"], "error")
        self.assertIsNone(result["totals"]["total_tokens"])
        self.log.write_text('{"message":"do not echo this payload"\n')
        result = self.poll()
        self.assertEqual(result["agents"][0]["reason"], "malformed-usage-log")
        self.assertNotIn("do not echo", json.dumps(result))
        self.assertNotIn("do not echo", self.collector.cache_path.read_text())
        self.write(codex(input_tokens=True))
        self.assertEqual(self.poll()["agents"][0]["status"], "error")

    def test_unknown_and_missing_rows_are_excluded_from_totals_with_explicit_coverage(self):
        self.write(codex())
        empty = self.root / "empty.jsonl"
        empty.write_text("")
        result = self.poll(self.source, {"id": "child", "provider": "claude", "path": str(empty)})
        self.assertEqual(result["coverage"], {"attached": 2, "measured": 1})
        self.assertEqual(result["totals"]["total_tokens"], 105)
        self.assertIsNone(result["agents"][1]["total_tokens"])
        self.assertEqual(result["agents"][1]["status"], "unknown")
        self.assertTrue(all(value is None for value in self.collector.poll([])["totals"].values()))

    def test_invalid_sources_are_rejected_before_content_is_read(self):
        for path in ["relative.jsonl", str(self.root / "secrets" / "data.jsonl"),
                     str(self.root / "credentials.jsonl"), str(self.root / ".env.jsonl")]:
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.poll({**self.source, "path": path})
        forbidden = self.root / "secrets" / "data.jsonl"
        forbidden.parent.mkdir()
        forbidden.write_text("never read this")
        alias = self.root / "alias"
        alias.symlink_to(forbidden.parent, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "non-secret JSONL"):
            self.poll({**self.source, "path": str(alias / "data.jsonl")})
        self.log.symlink_to(forbidden)
        with self.assertRaises(ValueError):
            self.poll()
        with self.assertRaises(ValueError):
            self.poll({**self.source, "provider": "unsupported"})
        self.log.unlink()
        self.write(codex())
        with self.assertRaises(ValueError):
            self.poll(self.source, self.source)
        with self.assertRaisesRegex(ValueError, "log paths must be unique"):
            self.poll(self.source, {**self.source, "id": "child"})
        benign = self.root / "benign.jsonl"
        self.write(codex(), path=benign)
        self.log.unlink()
        self.log.symlink_to(benign)
        with self.assertRaisesRegex(ValueError, "must not be a symlink"):
            self.poll()
        self.log.unlink()
        self.write(codex())
        validate = telemetry.validate_source

        def swap_after_validation(source):
            result = validate(source)
            self.log.unlink()
            self.log.symlink_to(forbidden)
            return result

        with mock.patch.object(telemetry, "validate_source", side_effect=swap_after_validation):
            result = self.poll()
        self.assertEqual(result["agents"][0]["reason"], "unreadable-source")
        self.assertIsNone(result["totals"]["total_tokens"])

    def test_damaged_cache_is_an_explicit_failure_not_an_automatic_full_log_rescan(self):
        self.write(codex())
        self.poll()
        valid_entry = json.loads(self.collector.cache_path.read_text())["sources"]["parent"]
        corrupt_entries = ["damaged entry", {}, *(
            {**valid_entry, key: value} for key, value in (
                ("offset", "offset"), ("identity", [1]), ("discard_partial", 1),
                ("usage", {"input_tokens": 1}), ("context_tokens", -1),
                ("observed_at", []), ("messages", {"a" * 64: [1, 2]}),
            )
        )]
        damaged_caches = ["not valid JSON", *(
            json.dumps({"schema": 1, "sources": {"parent": entry}}) for entry in corrupt_entries
        )]
        for damaged in damaged_caches:
            with self.subTest(cache=damaged):
                self.collector.cache_path.write_text(damaged)
                with self.assertRaisesRegex(ValueError, "telemetry cache is invalid"), \
                        mock.patch.object(telemetry, "_consume") as consume:
                    self.poll()
                consume.assert_not_called()
                self.assertEqual(self.collector.cache_path.read_text(), damaged)
        self.collector.cache_path.unlink()
        target = self.root / "unrelated.json"
        original = '{"schema":1,"sources":{}}'
        target.write_text(original)
        for path in (self.collector.cache_path, self.workspace / "telemetry-cache.lock"):
            with self.subTest(path=path.name):
                path.unlink(missing_ok=True)
                path.symlink_to(target)
                with self.assertRaisesRegex(ValueError, "regular non-symlink"):
                    self.poll()
                self.assertEqual(target.read_text(), original)
                path.unlink()

    def test_named_pipe_cannot_block_the_background_collector(self):
        os.mkfifo(self.log)
        result = self.poll()
        self.assertEqual(result["agents"][0]["status"], "error")
        self.assertEqual(result["agents"][0]["reason"], "unreadable-source")
        self.assertIsNone(result["totals"]["total_tokens"])


if __name__ == "__main__":
    unittest.main()
