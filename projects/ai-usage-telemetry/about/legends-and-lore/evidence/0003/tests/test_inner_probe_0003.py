"""Tests for the in-namespace structural inspector used by candidate 0003."""

from __future__ import annotations

import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


EVIDENCE_DIR = Path(__file__).resolve().parents[1]
INNER_PROBE_PATH = EVIDENCE_DIR / "runtime" / "inner_probe_0003.py"


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def assistant_record(*, session: str, request: str, stamp: str, count: int, content: str) -> bytes:
    return (
        "{"
        f'"type":"assistant","sessionId":"{session}","requestId":"{request}",'
        f'"timestamp":"{stamp}",'
        '"message":{'
        '"id":"synthetic-message","model":"synthetic-model",'
        f'"content":"{content}",'
        '"usage":{'
        f'"input_tokens":{count},"cache_creation_input_tokens":0,'
        f'"cache_read_input_tokens":0,"output_tokens":{count}'
        "}}}\n"
    ).encode("utf-8")


def assistant_record_with_unprojected_value(*, stamp: str, count: int, value: bytes) -> bytes:
    return (
        b'{"type":"assistant","sessionId":"s","requestId":"r","timestamp":"'
        + stamp.encode("ascii")
        + b'","message":{"id":"synthetic-message","model":"synthetic-model","content":'
        + value
        + b',"usage":{"input_tokens":'
        + str(count).encode("ascii")
        + b',"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":'
        + str(count).encode("ascii")
        + b"}}}\n"
    )


def assistant_record_with_duplicate_projected_key(*, stamp: str, count: int) -> bytes:
    return (
        b'{"type":"assistant","sessionId":"s","requestId":"r","timestamp":"'
        + stamp.encode("ascii")
        + b'","message":{"id":"synthetic-message","id":"synthetic-shadow","model":"synthetic-model",'
        b'"content":"","usage":{"input_tokens":'
        + str(count).encode("ascii")
        + b',"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":'
        + str(count).encode("ascii")
        + b"}}}\n"
    )


def assistant_record_with_escaped_semantic_duplicate(
    *, stamp: str, count: int, duplicate: str, escaped_first: bool
) -> bytes:
    header = (
        b'{"type":"assistant","sessionId":"s","requestId":"r","timestamp":"'
        + stamp.encode("ascii")
        + b'",'
    )
    usage = (
        b'"usage":{"input_tokens":'
        + str(count).encode("ascii")
        + b',"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":'
        + str(count).encode("ascii")
        + b"}"
    )
    if duplicate == "message-id":
        literal_key = b'"id"'
        escaped_key = b'"\\u0069\\u0064"'
        literal_value = b'"synthetic-message"'
        escaped_value = b'"synthetic-shadow"'
        first_key, first_value, second_key, second_value = (
            (escaped_key, escaped_value, literal_key, literal_value)
            if escaped_first
            else (literal_key, literal_value, escaped_key, escaped_value)
        )
        return (
            header
            + b'"message":{'
            + first_key
            + b":"
            + first_value
            + b","
            + second_key
            + b":"
            + second_value
            + b',"model":"synthetic-model","content":"",'
            + usage
            + b"}}\n"
        )
    if duplicate == "message-prefix":
        literal_key = b'"message"'
        escaped_key = b'"m\\u0065ssage"'

        def message_value(message_id: bytes) -> bytes:
            return b'{"id":' + message_id + b',"model":"synthetic-model","content":"",' + usage + b"}"

        first_key, first_value, second_key, second_value = (
            (escaped_key, message_value(b'"synthetic-shadow"'), literal_key, message_value(b'"synthetic-message"'))
            if escaped_first
            else (literal_key, message_value(b'"synthetic-message"'), escaped_key, message_value(b'"synthetic-shadow"'))
        )
        return (
            header
            + first_key
            + b":"
            + first_value
            + b","
            + second_key
            + b":"
            + second_value
            + b"}\n"
        )
    raise ValueError(f"unknown duplicate fixture: {duplicate}")


def assistant_record_with_escaped_unprojected_key(*, stamp: str, count: int) -> bytes:
    return (
        b'{"type":"assistant","sessionId":"s","requestId":"r","timestamp":"'
        + stamp.encode("ascii")
        + b'","message":{"id":"synthetic-message","model":"synthetic-model",'
        b'"m\\u0065tadata":"synthetic-unprojected","content":"","usage":{"input_tokens":'
        + str(count).encode("ascii")
        + b',"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":'
        + str(count).encode("ascii")
        + b"}}}\n"
    )


class InnerProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inner = load_module("inner_probe_0003", INNER_PROBE_PATH)

    def test_persisted_same_pair_monotone_records_become_contract_gap_without_values(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            session_dir = root / ".claude" / "projects" / "opaque"
            session_dir.mkdir(parents=True)
            content_sentinel = "synthetic-content-not-to-export"
            (session_dir / "session.jsonl").write_bytes(
                assistant_record(session="s", request="r", stamp="one", count=1, content=content_sentinel)
                + assistant_record(session="s", request="r", stamp="two", count=2, content=content_sentinel)
            )

            analysis = self.inner.inspect_virtual_home(root)
            safe_summary = self.inner.make_safe_summary(analysis, canary_connections=2)

        self.assertEqual(analysis.complete_usage_observation_count, 2)
        self.assertEqual(analysis.progressive_same_pair_group_count, 1)
        self.assertEqual(safe_summary["disposition"], "confirmed-contract-gap")
        self.assertNotIn(content_sentinel, repr(safe_summary))
        self.assertNotIn("session", safe_summary["counts"])
        self.assertEqual(safe_summary["direction_assertions"]["monotone-increase-groups"], 1)

    def test_reachable_unique_key_o4_aggregate_retains_contract_gap_disposition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            session_dir = root / ".claude" / "projects" / "opaque"
            session_dir.mkdir(parents=True)
            session_dir.joinpath("session.jsonl").write_bytes(
                assistant_record(
                    session="s", request="progressive", stamp="one", count=1, content="synthetic"
                )
                + assistant_record(
                    session="s", request="progressive", stamp="two", count=2, content="synthetic"
                )
                + assistant_record(
                    session="s", request="same-stamp", stamp="fixed", count=3, content="synthetic"
                )
                + assistant_record(
                    session="s", request="same-stamp", stamp="fixed", count=4, content="synthetic"
                )
            )

            analysis = self.inner.inspect_virtual_home(root)
            safe_summary = self.inner.make_safe_summary(analysis, canary_connections=1)

        self.assertEqual(analysis.complete_usage_observation_count, 4)
        self.assertEqual(analysis.same_native_pair_group_count, 2)
        self.assertEqual(analysis.progressive_same_pair_group_count, 1)
        self.assertEqual(analysis.exact_replay_group_count, 0)
        self.assertEqual(analysis.changed_timestamp_group_count, 1)
        self.assertEqual(analysis.decreasing_group_count, 0)
        self.assertEqual(analysis.nonconforming_reuse_group_count, 0)
        self.assertEqual(safe_summary["disposition"], "confirmed-contract-gap")

    def test_malformed_or_incomplete_records_cannot_confirm_a_negative(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            session_dir = root / ".claude" / "projects" / "opaque"
            session_dir.mkdir(parents=True)
            (session_dir / "session.jsonl").write_bytes(b"{\n" + b'{"type":"assistant"}')

            analysis = self.inner.inspect_virtual_home(root)
            safe_summary = self.inner.make_safe_summary(analysis, canary_connections=2)

        self.assertGreaterEqual(analysis.malformed_record_count, 1)
        self.assertGreaterEqual(analysis.incomplete_tail_count, 1)
        self.assertEqual(safe_summary["disposition"], "unresolved")

    def test_incomplete_tail_is_not_relabelled_as_malformed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            session_dir = root / ".claude" / "projects" / "opaque"
            session_dir.mkdir(parents=True)
            (session_dir / "session.jsonl").write_bytes(
                assistant_record(session="s", request="r", stamp="one", count=1, content="synthetic")[:-1]
            )

            analysis = self.inner.inspect_virtual_home(root)

        self.assertEqual(analysis.malformed_record_count, 0)
        self.assertEqual(analysis.incomplete_tail_count, 1)

    def test_unknown_content_subtree_cannot_override_a_safe_observation_field(self) -> None:
        raw_record = (
            b'{"type":"assistant","sessionId":"s","requestId":"r","timestamp":"t",'
            b'"message":{"id":"outer","model":"model",'
            b'"content":{"message":{"id":"decoy","model":"decoy",'
            b'"usage":{"input_tokens":99,"cache_creation_input_tokens":99,'
            b'"cache_read_input_tokens":99,"output_tokens":99}}},'
            b'"usage":{"input_tokens":1,"cache_creation_input_tokens":0,'
            b'"cache_read_input_tokens":0,"output_tokens":2}}}'
        )

        values = self.inner.StructuralJsonScanner(raw_record).parse()

        self.assertEqual(values[("message", "id")], "outer")
        self.assertEqual(values[("message", "usage", "input_tokens")], 1)

    def test_invalid_skip_only_escape_utf8_and_number_cannot_confirm(self) -> None:
        invalid_unprojected_values = {
            "invalid-escape": b'"\\q"',
            "invalid-utf8": b'"\xc0\x80"',
            "leading-zero-number": b"01",
        }
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            session_dir = root / ".claude" / "projects" / "opaque"
            session_dir.mkdir(parents=True)
            for name, invalid_value in invalid_unprojected_values.items():
                with self.subTest(name=name):
                    (session_dir / "session.jsonl").write_bytes(
                        assistant_record_with_unprojected_value(stamp="one", count=1, value=invalid_value)
                        + assistant_record_with_unprojected_value(stamp="two", count=2, value=invalid_value)
                    )

                    analysis = self.inner.inspect_virtual_home(root)
                    safe_summary = self.inner.make_safe_summary(analysis, canary_connections=1)

                    self.assertEqual(analysis.complete_usage_observation_count, 0)
                    self.assertEqual(analysis.malformed_record_count, 2)
                    self.assertEqual(analysis.progressive_same_pair_group_count, 0)
                    self.assertEqual(safe_summary["disposition"], "unresolved")

    def test_duplicate_projected_keys_are_malformed_and_cannot_confirm(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            session_dir = root / ".claude" / "projects" / "opaque"
            session_dir.mkdir(parents=True)
            (session_dir / "session.jsonl").write_bytes(
                assistant_record_with_duplicate_projected_key(stamp="one", count=1)
                + assistant_record_with_duplicate_projected_key(stamp="two", count=2)
            )

            analysis = self.inner.inspect_virtual_home(root)
            safe_summary = self.inner.make_safe_summary(analysis, canary_connections=1)

        self.assertEqual(analysis.complete_usage_observation_count, 0)
        self.assertEqual(analysis.malformed_record_count, 2)
        self.assertEqual(analysis.progressive_same_pair_group_count, 0)
        self.assertEqual(safe_summary["disposition"], "unresolved")

    def test_escaped_semantic_projected_duplicates_are_malformed_and_cannot_confirm(self) -> None:
        cases = (
            ("literal-then-escaped-projected-leaf", "message-id", False),
            ("escaped-then-literal-projected-leaf", "message-id", True),
            ("literal-then-escaped-projected-prefix", "message-prefix", False),
            ("escaped-then-literal-projected-prefix", "message-prefix", True),
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            session_dir = root / ".claude" / "projects" / "opaque"
            session_dir.mkdir(parents=True)
            session_path = session_dir / "session.jsonl"
            for name, duplicate, escaped_first in cases:
                with self.subTest(name=name):
                    session_path.write_bytes(
                        assistant_record_with_escaped_semantic_duplicate(
                            stamp="one", count=1, duplicate=duplicate, escaped_first=escaped_first
                        )
                        + assistant_record_with_escaped_semantic_duplicate(
                            stamp="two", count=2, duplicate=duplicate, escaped_first=escaped_first
                        )
                    )

                    analysis = self.inner.inspect_virtual_home(root)
                    safe_summary = self.inner.make_safe_summary(analysis, canary_connections=1)

                    self.assertEqual(analysis.complete_usage_observation_count, 0)
                    self.assertEqual(analysis.malformed_record_count, 2)
                    self.assertEqual(analysis.progressive_same_pair_group_count, 0)
                    self.assertEqual(safe_summary["disposition"], "unresolved")

    def test_escaped_projected_duplicate_rejects_before_second_value_decode(self) -> None:
        sentinel = b"escaped-duplicate-value-must-not-decode"

        class SecondValueSliceTrap(bytes):
            def __getitem__(self, item):
                value = super().__getitem__(item)
                if isinstance(item, slice) and sentinel in value:
                    raise AssertionError("escaped-duplicate-value-sliced")
                return value

        raw_record = SecondValueSliceTrap(
            assistant_record_with_escaped_semantic_duplicate(
                stamp="one", count=1, duplicate="message-id", escaped_first=False
            ).rstrip(b"\n").replace(b"synthetic-shadow", sentinel)
        )

        with self.assertRaisesRegex(self.inner.SafeParseError, "duplicate-projected-key"):
            self.inner.StructuralJsonScanner(raw_record).parse()

    def test_escaped_unprojected_key_remains_skip_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            session_dir = root / ".claude" / "projects" / "opaque"
            session_dir.mkdir(parents=True)
            (session_dir / "session.jsonl").write_bytes(
                assistant_record_with_escaped_unprojected_key(stamp="one", count=1)
            )

            analysis = self.inner.inspect_virtual_home(root)

        self.assertEqual(analysis.complete_usage_observation_count, 1)
        self.assertEqual(analysis.malformed_record_count, 0)

    def test_source_counter_above_signed_64_cannot_progress_or_confirm(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            session_dir = root / ".claude" / "projects" / "opaque"
            session_dir.mkdir(parents=True)
            session_dir.joinpath("session.jsonl").write_bytes(
                assistant_record(
                    session="s",
                    request="r",
                    stamp="one",
                    count=1 << 63,
                    content="synthetic",
                )
                + assistant_record(
                    session="s",
                    request="r",
                    stamp="two",
                    count=(1 << 63) + 1,
                    content="synthetic",
                )
            )

            analysis = self.inner.inspect_virtual_home(root)
            safe_summary = self.inner.make_safe_summary(analysis, canary_connections=1)

        self.assertEqual(analysis.complete_usage_observation_count, 0)
        self.assertEqual(analysis.malformed_record_count, 2)
        self.assertEqual(analysis.progressive_same_pair_group_count, 0)
        self.assertNotIn(
            safe_summary["disposition"],
            {"confirmed-contract-gap", "confirmed-current-contract"},
        )
        self.assertEqual(safe_summary["disposition"], "unresolved")

    def test_signed_64_source_counter_maximum_is_admitted(self) -> None:
        values = self.inner.StructuralJsonScanner(
            assistant_record(
                session="s",
                request="r",
                stamp="one",
                count=(1 << 63) - 1,
                content="synthetic",
            ).rstrip(b"\n")
        ).parse()

        self.assertEqual(values[("message", "usage", "input_tokens")], (1 << 63) - 1)
        self.assertEqual(values[("message", "usage", "output_tokens")], (1 << 63) - 1)

    def test_loopback_mock_positive_control_accepts_without_reading_request_values(self) -> None:
        mock = self.inner.LoopbackOnlyMock()
        try:
            mock.start()
            self.inner.run_loopback_canary(mock.port)
            self.assertTrue(mock.wait_for_connections(1))
            self.assertEqual(mock.nonloopback_connection_count, 0)
        finally:
            mock.close()

    def test_network_state_requires_only_loopback_and_no_default_route(self) -> None:
        self.assertTrue(self.inner.network_state_is_safe(("lo",), 0))
        self.assertFalse(self.inner.network_state_is_safe(("lo", "eth0"), 0))
        self.assertFalse(self.inner.network_state_is_safe(("lo",), 1))

    def test_target_command_uses_an_empty_content_free_argument(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            output = root / "output"
            work = root / "work"
            output.mkdir()
            work.mkdir()
            process = mock.Mock()
            with (
                mock.patch.object(self.inner, "SYNTHETIC_OUTPUT", output),
                mock.patch.object(self.inner, "SYNTHETIC_WORK", work),
                mock.patch.object(self.inner.subprocess, "Popen", return_value=process) as popen,
            ):
                self.inner._run_target()

        argv = popen.call_args.args[0]
        self.assertEqual(
            argv[argv.index("--") + 1 :],
            [
                self.inner.SYNTHETIC_TARGET,
                "-p",
                "",
                "--output-format",
                "json",
                "--permission-mode",
                "plan",
            ],
        )
        self.assertEqual(popen.call_args.kwargs["cwd"], work)
        self.assertEqual(popen.call_args.kwargs["env"], self.inner.SAFE_TARGET_ENVIRONMENT)
        self.assertIs(popen.call_args.kwargs["stdin"], self.inner.subprocess.DEVNULL)
        self.assertTrue(popen.call_args.kwargs["start_new_session"])
        self.assertIs(popen.call_args.kwargs["stdout"], self.inner.subprocess.DEVNULL)
        self.assertIs(popen.call_args.kwargs["stderr"], self.inner.subprocess.DEVNULL)

    def test_target_runs_as_nested_pid_namespace_init_without_reporter_descriptor_access(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            output = root / "output"
            work = root / "work"
            output.mkdir()
            work.mkdir()
            process = mock.Mock()
            with (
                mock.patch.object(self.inner, "SYNTHETIC_OUTPUT", output),
                mock.patch.object(self.inner, "SYNTHETIC_WORK", work),
                mock.patch.object(self.inner.subprocess, "Popen", return_value=process) as popen,
            ):
                self.inner._run_target()

        argv = popen.call_args.args[0]
        self.assertEqual(argv[0], self.inner.TRUSTED_BWRAP_PATH)
        self.assertIn("--unshare-pid", argv)
        self.assertIn("--proc", argv)
        self.assertIn("--new-session", argv)
        self.assertEqual(argv[argv.index("--") + 1], self.inner.SYNTHETIC_TARGET)
        self.assertTrue(popen.call_args.kwargs["close_fds"])

    def test_target_discards_raw_standard_streams_instead_of_materializing_them(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            output = root / "output"
            work = root / "work"
            output.mkdir()
            work.mkdir()
            process = mock.Mock()
            with (
                mock.patch.object(self.inner, "SYNTHETIC_OUTPUT", output),
                mock.patch.object(self.inner, "SYNTHETIC_WORK", work),
                mock.patch.object(self.inner.subprocess, "Popen", return_value=process) as popen,
            ):
                self.inner._run_target()

        self.assertIs(popen.call_args.kwargs["stdout"], self.inner.subprocess.DEVNULL)
        self.assertIs(popen.call_args.kwargs["stderr"], self.inner.subprocess.DEVNULL)

    def test_nested_target_nonzero_exit_is_not_completed(self) -> None:
        process = mock.Mock()
        process.wait.return_value = 2
        with (
            mock.patch.object(self.inner.subprocess, "Popen", return_value=process),
        ):
            outcome = self.inner._run_target()

        self.assertEqual(outcome, (1, 0))

    def test_nested_target_timeout_after_kill_is_not_completed(self) -> None:
        process = mock.Mock()
        process.pid = 4242
        process.wait.side_effect = [subprocess.TimeoutExpired("synthetic-target", 60), -9]
        with (
            mock.patch.object(self.inner.subprocess, "Popen", return_value=process),
            mock.patch.object(self.inner.os, "killpg") as killpg,
        ):
            outcome = self.inner._run_target()

        self.assertEqual(outcome, (1, 0))
        killpg.assert_called_once_with(process.pid, self.inner.signal.SIGKILL)
        self.assertEqual(process.wait.call_args_list, [mock.call(timeout=60), mock.call(timeout=10)])

    def test_incomplete_target_outcome_stops_before_home_inspection(self) -> None:
        safe_mock = mock.Mock()
        safe_mock.connection_count = 1
        safe_mock.nonloopback_connection_count = 0
        safe_mock.wait_for_connections.return_value = True
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            with (
                mock.patch.object(self.inner, "SYNTHETIC_HOME", root / "home"),
                mock.patch.object(self.inner, "SYNTHETIC_WORK", root / "work"),
                mock.patch.object(self.inner, "SYNTHETIC_OUTPUT", root / "output"),
                mock.patch.object(self.inner, "LoopbackOnlyMock", return_value=safe_mock),
                mock.patch.object(self.inner, "_prepare_loopback_network", return_value=(("lo",), 0)),
                mock.patch.object(self.inner, "run_loopback_canary"),
                mock.patch.object(self.inner, "_run_target", return_value=(1, 0)),
                mock.patch.object(
                    self.inner,
                    "inspect_virtual_home",
                    side_effect=AssertionError("incomplete target must not be inspected"),
                ) as inspect_virtual_home,
            ):
                safe_summary = self.inner.run_probe()

        inspect_virtual_home.assert_not_called()
        self.assertEqual(safe_summary["disposition"], "unresolved")
        self.assertEqual(safe_summary["counts"]["target_started"], 1)
        self.assertEqual(safe_summary["counts"]["target_completed"], 0)

    def test_malformed_analysis_cannot_confirm_a_contract_gap(self) -> None:
        analysis = self.inner.InspectionAnalysis(2, 1, 0, 1, 1, 1, 0, 1, 0, 0)

        safe_summary = self.inner.make_safe_summary(analysis, canary_connections=1)

        self.assertEqual(safe_summary["disposition"], "unresolved")

    def test_incomplete_analysis_cannot_confirm_a_contract_gap(self) -> None:
        analysis = self.inner.InspectionAnalysis(2, 0, 1, 1, 1, 1, 0, 1, 0, 0)

        safe_summary = self.inner.make_safe_summary(analysis, canary_connections=1)

        self.assertEqual(safe_summary["disposition"], "unresolved")


if __name__ == "__main__":
    unittest.main()
