"""Behavioral tests for candidate evidence 0003's isolated Claude probe."""

from __future__ import annotations

import hashlib
import io
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


EVIDENCE_DIR = Path(__file__).resolve().parents[1]
PROBE_PATH = EVIDENCE_DIR / "claude_progressive_probe_0003.py"
FIXTURE_PATH = EVIDENCE_DIR / "fixture_0003.json"
CAPTURE_CONTROLS_PATH = EVIDENCE_DIR / "exercise_capture_controls_0003.py"


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class RecordingLauncher:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, _plan: object) -> None:
        self.calls += 1


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


class CompletedSummaryProcess:
    """A no-target child process whose stdout is an untrusted summary payload."""

    def __init__(self, payload: bytes, *, returncode: int = 0) -> None:
        self.stdout = io.BytesIO(payload)
        self.returncode = returncode
        self.killed = False

    def poll(self) -> int:
        return self.returncode

    def wait(self, timeout: float | None = None) -> int:
        del timeout
        return self.returncode

    def kill(self) -> None:
        self.killed = True
        self.returncode = -9


class TimedOutSummaryProcess(CompletedSummaryProcess):
    def __init__(self) -> None:
        super().__init__(b"")
        self.returncode = None

    def poll(self):
        return self.returncode

    def wait(self, timeout: float | None = None):
        del timeout
        if self.returncode is None:
            raise subprocess.TimeoutExpired("synthetic-bwrap", 0)
        return self.returncode


class ClaudeProgressiveProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.probe = load_module("claude_progressive_probe_0003", PROBE_PATH)

    def safe_plan(self):
        return self.probe.make_safe_plan(
            target=Path("/exact-target/claude"),
            probe_code=Path("/candidate-only-probe"),
            runtime_roots=self.probe.DEFAULT_RUNTIME_MOUNT_SOURCES,
        )

    def full_safe_summary(self):
        return {
            "schema": "claude-progressive-probe-summary@1",
            "build_pin": {"version": self.probe.PINNED_VERSION, "sha256": self.probe.PINNED_SHA256},
            "path_classes": dict(self.probe.SUMMARY_STRING_SECTION_VALUES["path_classes"]),
            "type_assertions": dict(self.probe.SUMMARY_STRING_SECTION_VALUES["type_assertions"]),
            "counts": {key: 0 for key in self.probe.SUMMARY_SECTION_KEYS["counts"]},
            "equality_assertions": {
                key: 0 for key in self.probe.SUMMARY_SECTION_KEYS["equality_assertions"]
            },
            "direction_assertions": {
                key: 0 for key in self.probe.SUMMARY_SECTION_KEYS["direction_assertions"]
            },
            "control_totals": {key: 0 for key in self.probe.SUMMARY_SECTION_KEYS["control_totals"]},
            "disposition": "unresolved",
        }

    def confirmed_gap_summary(self):
        summary = self.full_safe_summary()
        summary["counts"].update(
            {
                "target_started": 1,
                "target_completed": 1,
                "loopback_mock_connections": 1,
                "complete_usage_observations": 2,
                "same_native_pair_groups": 1,
                "progressive_same_pair_groups": 1,
            }
        )
        summary["equality_assertions"].update(
            {
                "changed_timestamp_groups": 1,
            }
        )
        summary["direction_assertions"].update(
            {
                "monotone-increase-groups": 1,
            }
        )
        summary["control_totals"].update(
            {
                "loopback_canary_connections": 1,
            }
        )
        summary["disposition"] = "confirmed-contract-gap"
        return summary

    def assert_all_empty_unresolved(self, result):
        self.assertEqual(result, self.probe._safe_unresolved_result())
        self.probe.validate_safe_summary(result)

    def assert_rejected_before_launch(self, plan, *, pin_ok: bool = True) -> None:
        launcher = RecordingLauncher()
        with self.assertRaises(self.probe.ContainmentRejected):
            self.probe.launch_if_safe(plan, pin_checker=lambda _target: pin_ok, launcher=launcher)
        self.assertEqual(launcher.calls, 0)

    def execute_completed_summary(self, payload: bytes, *, returncode: int = 0):
        process = CompletedSummaryProcess(payload, returncode=returncode)
        with (
            mock.patch.object(self.probe, "assert_attempt_gate_allows_launch", create=True),
            mock.patch.object(self.probe, "resolve_claude_executable", return_value=Path("/synthetic-target/claude")),
            mock.patch.object(self.probe, "verify_pinned_build"),
            mock.patch.object(self.probe, "resolve_trusted_bwrap", return_value=Path("/synthetic-bwrap"), create=True),
            mock.patch.object(self.probe.subprocess, "Popen", return_value=process) as popen,
        ):
            try:
                result = self.probe.execute_isolated_probe()
            except self.probe.ContainmentRejected:
                result = {"disposition": "unsafe-exception"}
        return result, popen

    def test_missing_network_namespace_rejects_before_launch(self) -> None:
        plan = self.safe_plan().replace(namespaces=frozenset({"user", "pid"}))
        self.assert_rejected_before_launch(plan)

    def test_host_home_or_config_bind_rejects_before_launch(self) -> None:
        plan = self.safe_plan().with_mount(
            self.probe.MountRule("ro-bind", Path("/host-home/.config"), "/sandbox-home/.config", "forbidden")
        )
        self.assert_rejected_before_launch(plan)

    def test_broad_source_bind_rejects_before_launch(self) -> None:
        plan = self.safe_plan().with_mount(
            self.probe.MountRule("ro-bind", Path("/workspace"), "/source", "forbidden")
        )
        self.assert_rejected_before_launch(plan)

    def test_inherited_credential_or_proxy_rejects_before_launch(self) -> None:
        plan = self.safe_plan().replace(forwarded_environment={"HTTPS_PROXY": "synthetic-proxy"})
        self.assert_rejected_before_launch(plan)

    def test_non_loopback_route_rejects_before_launch(self) -> None:
        plan = self.safe_plan().replace(network_mode="non-loopback-route")
        self.assert_rejected_before_launch(plan)

    def test_raw_output_capture_rejects_before_launch(self) -> None:
        plan = self.safe_plan().replace(target_output="host-capture")
        self.assert_rejected_before_launch(plan)

    def test_pin_mismatch_rejects_before_launch(self) -> None:
        self.assert_rejected_before_launch(self.safe_plan(), pin_ok=False)

    def test_structural_oracle_covers_the_predeclared_matrix(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        outcomes = self.probe.verify_predeclared_oracle_matrix(fixture)

        self.assertEqual(
            outcomes,
            {
                "exact-replay": "duplicate",
                "one-request-progressive-stream": "confirmed-contract-gap",
                "changed-timestamp": "identity-collision",
                "monotone-counter": "confirmed-contract-gap",
                "decreasing-counter": "identity-collision",
                "malformed-record": "recognized-malformed",
                "incomplete-record": "incomplete-tail",
                "nonconforming-identity-reuse": "identity-collision",
            },
        )

    def test_structural_projector_skips_content_and_reports_only_safe_relationships(self) -> None:
        content_sentinel = "synthetic-content-that-must-not-be-decoded"
        raw_record = (
            '{"type":"assistant","sessionId":"s","requestId":"r","timestamp":"t",'
            '"message":{"id":"m","model":"model","content":"'
            + content_sentinel
            + '","usage":{"input_tokens":1,"cache_creation_input_tokens":0,'
            '"cache_read_input_tokens":0,"output_tokens":2}}}'
        ).encode("utf-8")

        summary = self.probe.inspect_jsonl_bytes(raw_record + b"\n")

        self.assertEqual(summary.complete_usage_observation_count, 1)
        self.assertEqual(summary.decoded_path_classes, self.probe.SAFE_PROJECTED_PATH_CLASSES)
        self.assertNotIn(content_sentinel, repr(summary))

    def test_structural_projector_never_slices_an_unknown_content_value(self) -> None:
        content_sentinel = b"synthetic-content-slice-trap"

        class ContentSliceTrap(bytes):
            def __getitem__(self, item):
                value = super().__getitem__(item)
                if isinstance(item, slice) and content_sentinel in value:
                    raise AssertionError("content-value-sliced")
                return value

        raw_record = ContentSliceTrap(
            b'{"type":"assistant","sessionId":"s","requestId":"r","timestamp":"t",'
            b'"message":{"id":"m","model":"model","content":"'
            + content_sentinel
            + b'","usage":{"input_tokens":1,"cache_creation_input_tokens":0,'
            b'"cache_read_input_tokens":0,"output_tokens":2}}}'
        )

        values = self.probe._SafeJsonLineScanner(raw_record).parse()

        self.assertEqual(values[("type",)], "assistant")

    def test_structural_projector_rejects_invalid_skip_only_json_grammar(self) -> None:
        invalid_unprojected_values = {
            "invalid-escape": b'"\\q"',
            "invalid-utf8": b'"\xc0\x80"',
            "leading-zero-number": b"01",
        }
        for name, invalid_value in invalid_unprojected_values.items():
            with self.subTest(name=name):
                summary = self.probe.inspect_jsonl_bytes(
                    assistant_record_with_unprojected_value(stamp="one", count=1, value=invalid_value)
                )

                self.assertEqual(summary.complete_usage_observation_count, 0)
                self.assertEqual(summary.malformed_record_count, 1)

    def test_source_counter_above_signed_64_cannot_be_a_complete_observation(self) -> None:
        for count in ((1 << 63), (1 << 63) + 1):
            with self.subTest(count=count):
                summary = self.probe.inspect_jsonl_bytes(
                    assistant_record_with_unprojected_value(stamp="one", count=count, value=b'""')
                )

                self.assertEqual(summary.complete_usage_observation_count, 0)
                self.assertEqual(summary.malformed_record_count, 1)

    def test_signed_64_source_counter_maximum_remains_a_complete_observation(self) -> None:
        summary = self.probe.inspect_jsonl_bytes(
            assistant_record_with_unprojected_value(stamp="one", count=(1 << 63) - 1, value=b'""')
        )

        self.assertEqual(summary.complete_usage_observation_count, 1)
        self.assertEqual(summary.malformed_record_count, 0)

    def test_unknown_subtree_cannot_reenter_the_safe_projection_paths(self) -> None:
        raw_record = (
            b'{"type":"assistant","sessionId":"s","requestId":"r","timestamp":"t",'
            b'"message":{"id":"outer","model":"model",'
            b'"content":{"message":{"id":"decoy","model":"decoy",'
            b'"usage":{"input_tokens":99,"cache_creation_input_tokens":99,'
            b'"cache_read_input_tokens":99,"output_tokens":99}}},'
            b'"usage":{"input_tokens":1,"cache_creation_input_tokens":0,'
            b'"cache_read_input_tokens":0,"output_tokens":2}}}'
        )

        values = self.probe._SafeJsonLineScanner(raw_record).parse()

        self.assertEqual(values[("message", "id")], "outer")
        self.assertEqual(values[("message", "usage", "input_tokens")], 1)

    def test_summary_schema_rejects_raw_output_like_fields(self) -> None:
        with self.assertRaisesRegex(self.probe.ContainmentRejected, "summary-key"):
            self.probe.validate_safe_summary({"target_stdout": "not-allowed"})

    def test_summary_schema_rejects_a_raw_like_nested_field(self) -> None:
        summary = self.probe._safe_unresolved_result()
        summary["counts"] = {"target_stdout": 1}

        with self.assertRaisesRegex(self.probe.ContainmentRejected, "summary-.*-keys"):
            self.probe.validate_safe_summary(summary)

    def test_summary_schema_rejects_opaque_values_in_allowed_string_sections(self) -> None:
        forbidden_output = "THESIS_FORBIDDEN_RAW_OUTPUT"
        summary = {
            "schema": "claude-progressive-probe-summary@1",
            "build_pin": {"version": self.probe.PINNED_VERSION, "sha256": self.probe.PINNED_SHA256},
            "path_classes": {
                "target": "synthetic-executable",
                "probe_code": "read-only-candidate-code",
                "home": "tmpfs-synthetic",
                "work": "tmpfs-synthetic",
                "output": "tmpfs-only",
                "network": "loopback-only",
            },
            "type_assertions": {
                "structural_projection": "explicit-safe-fields-only",
                "complete_usage_observation": "assistant-with-required-safe-types",
            },
            "counts": {key: 0 for key in self.probe.SUMMARY_SECTION_KEYS["counts"]},
            "equality_assertions": {
                key: 0 for key in self.probe.SUMMARY_SECTION_KEYS["equality_assertions"]
            },
            "direction_assertions": {
                key: 0 for key in self.probe.SUMMARY_SECTION_KEYS["direction_assertions"]
            },
            "control_totals": {key: 0 for key in self.probe.SUMMARY_SECTION_KEYS["control_totals"]},
            "disposition": "unresolved",
        }

        for section, key in (("path_classes", "target"), ("type_assertions", "structural_projection")):
            with self.subTest(section=section):
                hostile_summary = {**summary, section: dict(summary[section])}
                hostile_summary[section][key] = forbidden_output

                with self.assertRaisesRegex(self.probe.ContainmentRejected, f"summary-{section}-values"):
                    self.probe.validate_safe_summary(hostile_summary)

    def test_zero_evidence_summary_never_decodes_or_survives_admission(self) -> None:
        payload = json.dumps(self.full_safe_summary(), sort_keys=True, separators=(",", ":")).encode("ascii")

        with mock.patch.object(self.probe.json, "loads", side_effect=AssertionError("whole-summary-decoded")):
            admitted = self.probe._parse_summary_bytes(payload)

        self.assert_all_empty_unresolved(admitted)

    def test_all_empty_unresolved_summary_remains_admitted(self) -> None:
        unresolved = self.probe._safe_unresolved_result()

        admitted = self.probe._parse_summary_bytes(
            json.dumps(unresolved, sort_keys=True, separators=(",", ":")).encode("ascii")
        )

        self.assertEqual(admitted, unresolved)

    def test_summary_admission_rejects_hostile_allowed_value_without_materializing_it(self) -> None:
        sentinel = b"THESIS_FORBIDDEN_RAW_SUMMARY"

        class UnknownSummarySliceTrap(bytes):
            def __getitem__(self, item):
                value = super().__getitem__(item)
                if isinstance(item, slice) and sentinel in value:
                    raise AssertionError("unknown-summary-value-materialized")
                return value

        hostile_summary = self.full_safe_summary()
        hostile_summary["path_classes"]["target"] = sentinel.decode("ascii")
        payload = UnknownSummarySliceTrap(
            json.dumps(hostile_summary, sort_keys=True, separators=(",", ":")).encode("ascii")
        )

        with mock.patch.object(self.probe.json, "loads", side_effect=AssertionError("whole-summary-decoded")):
            with self.assertRaisesRegex(self.probe.ContainmentRejected, "summary-path_classes-values"):
                self.probe._parse_summary_bytes(payload)

    def test_summary_admission_rejects_leading_zero_counts_without_decoding(self) -> None:
        payload = json.dumps(self.full_safe_summary(), sort_keys=True, separators=(",", ":")).encode("ascii")
        malformed_payload = payload.replace(b'"target_started":0', b'"target_started":01')
        self.assertNotEqual(malformed_payload, payload)

        with mock.patch.object(self.probe.json, "loads", side_effect=AssertionError("whole-summary-decoded")):
            with self.assertRaisesRegex(self.probe.ContainmentRejected, "summary-counts"):
                self.probe._parse_summary_bytes(malformed_payload)

    def test_forged_confirmation_without_required_primitive_evidence_normalizes_to_unresolved(self) -> None:
        def erase_primitive_evidence(summary) -> None:
            summary["counts"].update(
                {
                    "target_started": 0,
                    "target_completed": 0,
                    "loopback_mock_connections": 0,
                    "complete_usage_observations": 0,
                    "same_native_pair_groups": 0,
                    "progressive_same_pair_groups": 0,
                }
            )
            summary["equality_assertions"].update({"changed_timestamp_groups": 0})
            summary["direction_assertions"].update({"monotone-increase-groups": 0})
            summary["control_totals"].update({"loopback_canary_connections": 0})

        mutations = {
            "confirmed-enum-with-zero-evidence": erase_primitive_evidence,
            "target-not-started": lambda summary: summary["counts"].update({"target_started": 0}),
            "target-not-completed": lambda summary: summary["counts"].update({"target_completed": 0}),
            "canary-not-observed": lambda summary: summary["counts"].update(
                {"loopback_mock_connections": 0}
            ),
            "canary-control-not-proven": lambda summary: summary["control_totals"].update(
                {"loopback_canary_connections": 0}
            ),
            "zero-observations": lambda summary: summary["counts"].update(
                {"complete_usage_observations": 0}
            ),
            "malformed-analysis": lambda summary: summary["counts"].update({"malformed_records": 1}),
            "incomplete-analysis": lambda summary: summary["counts"].update({"incomplete_tails": 1}),
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                forged = self.confirmed_gap_summary()
                mutate(forged)
                self.probe.validate_safe_summary(forged)

                result, popen = self.execute_completed_summary(
                    json.dumps(forged, sort_keys=True, separators=(",", ":")).encode("ascii")
                )

                self.assert_all_empty_unresolved(result)
                popen.assert_called_once()

    def test_inconsistent_or_unsupported_confirmation_normalizes_to_unresolved(self) -> None:
        for name, mutate in {
            "progressive-group-mismatch": lambda summary: summary["direction_assertions"].update(
                {"monotone-increase-groups": 0}
            ),
            "current-contract-has-no-negative-oracle-proof": lambda summary: summary.update(
                {"disposition": "confirmed-current-contract"}
            ),
        }.items():
            with self.subTest(name=name):
                forged = self.confirmed_gap_summary()
                mutate(forged)
                self.probe.validate_safe_summary(forged)

                result, popen = self.execute_completed_summary(
                    json.dumps(forged, sort_keys=True, separators=(",", ":")).encode("ascii")
                )

                self.assert_all_empty_unresolved(result)
                popen.assert_called_once()

    def test_inconsistent_primitive_relationships_normalize_to_unresolved(self) -> None:
        def progressive_groups_exceed_same_pair_groups(summary) -> None:
            summary["counts"].update(
                {"progressive_same_pair_groups": 2, "complete_usage_observations": 4}
            )
            summary["direction_assertions"].update({"monotone-increase-groups": 2})
            summary["equality_assertions"].update({"changed_timestamp_groups": 2})

        def insufficient_complete_observations(summary) -> None:
            summary["counts"].update(
                {
                    "same_native_pair_groups": 2,
                    "progressive_same_pair_groups": 2,
                    "complete_usage_observations": 3,
                }
            )
            summary["direction_assertions"].update({"monotone-increase-groups": 2})
            summary["equality_assertions"].update({"changed_timestamp_groups": 2})

        def insufficient_changed_timestamps(summary) -> None:
            summary["counts"].update(
                {
                    "same_native_pair_groups": 2,
                    "progressive_same_pair_groups": 2,
                    "complete_usage_observations": 4,
                }
            )
            summary["direction_assertions"].update({"monotone-increase-groups": 2})

        mutations = {
            "monotone-count-exceeds-progressive": lambda summary: summary["direction_assertions"].update(
                {"monotone-increase-groups": 2}
            ),
            "loopback-control-is-not-a-flag": lambda summary: summary["control_totals"].update(
                {"loopback_canary_connections": 2}
            ),
            "progressive-groups-exceed-same-pair-groups": progressive_groups_exceed_same_pair_groups,
            "complete-observations-cannot-cover-same-pair-groups": insufficient_complete_observations,
            "changed-timestamps-do-not-cover-progressive-groups": insufficient_changed_timestamps,
        }
        for name, mutate in mutations.items():
            with self.subTest(name=name):
                forged = self.confirmed_gap_summary()
                mutate(forged)
                self.probe.validate_safe_summary(forged)

                result, popen = self.execute_completed_summary(
                    json.dumps(forged, sort_keys=True, separators=(",", ":")).encode("ascii")
                )

                self.assert_all_empty_unresolved(result)
                popen.assert_called_once()

    def test_primitive_supported_contract_gap_remains_admitted(self) -> None:
        summary = self.confirmed_gap_summary()

        result, popen = self.execute_completed_summary(
            json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("ascii")
        )

        self.assertEqual(result, summary)
        popen.assert_called_once()

    def test_trusted_bwrap_identity_ignores_a_shadowed_path_entry(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            trusted = root / "trusted-bwrap"
            shadow_directory = root / "shadow"
            shadow_directory.mkdir()
            shadow = shadow_directory / "bwrap"
            trusted.write_bytes(b"trusted-bwrap-only")
            shadow.write_bytes(b"shadowed-bwrap")
            trusted.chmod(0o755)
            shadow.chmod(0o755)
            trusted_digest = hashlib.sha256(trusted.read_bytes()).hexdigest()
            with (
                mock.patch.object(self.probe, "TRUSTED_BWRAP_PATH", trusted, create=True),
                mock.patch.object(self.probe, "TRUSTED_BWRAP_SHA256", trusted_digest, create=True),
                mock.patch.dict(os.environ, {"PATH": str(shadow_directory)}, clear=True),
            ):
                resolved = self.probe.resolve_trusted_bwrap()

        self.assertEqual(resolved, trusted)

    def test_consumed_attempt_gate_denies_retry_before_target_or_bwrap(self) -> None:
        with (
            mock.patch.object(
                self.probe,
                "resolve_claude_executable",
                side_effect=AssertionError("target-resolution-after-consumption"),
            ),
            mock.patch.object(
                self.probe,
                "resolve_trusted_bwrap",
                side_effect=AssertionError("bwrap-resolution-after-consumption"),
                create=True,
            ),
            mock.patch.object(
                self.probe.subprocess,
                "Popen",
                side_effect=AssertionError("process-launch-after-consumption"),
            ) as popen,
        ):
            result = self.probe.execute_isolated_probe()

        self.assertEqual(result["disposition"], "unresolved")
        self.assertEqual(result["counts"], {})
        popen.assert_not_called()

    def test_tampered_consumed_attempt_gate_is_fail_closed_before_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            tampered_gate = Path(temporary_directory) / "attempt-gate.json"
            tampered_gate.write_text('{"schema":"candidate-0003-attempt-gate@1","state":"available"}', encoding="ascii")
            with (
                mock.patch.object(self.probe, "ATTEMPT_GATE_PATH", tampered_gate, create=True),
                mock.patch.object(
                    self.probe,
                    "resolve_claude_executable",
                    side_effect=AssertionError("target-resolution-after-tampered-gate"),
                ),
            ):
                result = self.probe.execute_isolated_probe()

        self.assertEqual(result["disposition"], "unresolved")
        self.assertEqual(result["counts"], {})

    def test_authorized_pin_or_environment_failure_returns_only_unresolved_safe_summary(self) -> None:
        with (
            mock.patch.object(self.probe, "assert_attempt_gate_allows_launch", create=True),
            mock.patch.object(
                self.probe,
                "resolve_claude_executable",
                side_effect=self.probe.ContainmentRejected("build-pin-executable-missing"),
            ),
        ):
            result = self.probe.execute_isolated_probe()

        self.assertEqual(result["disposition"], "unresolved")
        self.assertEqual(result["counts"], {})

    def test_authorized_unresolved_return_is_schema_valid_without_exception_text(self) -> None:
        forbidden_exception_text = "THESIS_FORBIDDEN_RAW_OUTPUT"
        with (
            mock.patch.object(self.probe, "assert_attempt_gate_allows_launch", create=True),
            mock.patch.object(
                self.probe,
                "resolve_claude_executable",
                side_effect=self.probe.ContainmentRejected(forbidden_exception_text),
            ),
        ):
            result = self.probe.execute_isolated_probe()

        self.assertNotIn(forbidden_exception_text, json.dumps(result, sort_keys=True))
        self.probe.validate_safe_summary(result)

    def test_successful_malformed_summary_returns_content_free_unresolved(self) -> None:
        result, popen = self.execute_completed_summary(b"{malformed-summary")

        self.assertEqual(result["disposition"], "unresolved")
        self.assertEqual(result["counts"], {})
        self.probe.validate_safe_summary(result)
        popen.assert_called_once()
        self.assertEqual(popen.call_args.kwargs.get("bufsize"), 0)

    def test_successful_oversized_summary_returns_content_free_unresolved(self) -> None:
        forbidden_raw_output = b"THESIS_FORBIDDEN_RAW_OUTPUT"
        payload = forbidden_raw_output * ((16_385 // len(forbidden_raw_output)) + 1)

        result, popen = self.execute_completed_summary(payload)

        self.assertEqual(result["disposition"], "unresolved")
        self.assertEqual(result["counts"], {})
        self.assertNotIn(forbidden_raw_output.decode("ascii"), json.dumps(result, sort_keys=True))
        self.probe.validate_safe_summary(result)
        popen.assert_called_once()

    def test_successful_schema_invalid_summary_returns_content_free_unresolved(self) -> None:
        result, popen = self.execute_completed_summary(b"{}")

        self.assertEqual(result["disposition"], "unresolved")
        self.assertEqual(result["counts"], {})
        self.probe.validate_safe_summary(result)
        popen.assert_called_once()

    def test_nonzero_summary_process_returns_content_free_unresolved(self) -> None:
        result, popen = self.execute_completed_summary(b"{}", returncode=2)

        self.assertEqual(result["disposition"], "unresolved")
        self.assertEqual(result["counts"], {})
        self.probe.validate_safe_summary(result)
        popen.assert_called_once()

    def test_timed_out_summary_process_returns_content_free_unresolved(self) -> None:
        process = TimedOutSummaryProcess()
        with (
            mock.patch.object(self.probe, "assert_attempt_gate_allows_launch", create=True),
            mock.patch.object(self.probe, "resolve_claude_executable", return_value=Path("/synthetic-target/claude")),
            mock.patch.object(self.probe, "verify_pinned_build"),
            mock.patch.object(self.probe, "resolve_trusted_bwrap", return_value=Path("/synthetic-bwrap"), create=True),
            mock.patch.object(self.probe.subprocess, "Popen", return_value=process) as popen,
            mock.patch.object(self.probe, "PROBE_TIMEOUT_SECONDS", 0),
        ):
            result = self.probe.execute_isolated_probe()

        self.assertEqual(result["disposition"], "unresolved")
        self.assertEqual(result["counts"], {})
        self.assertTrue(process.killed)
        self.probe.validate_safe_summary(result)
        popen.assert_called_once()

    def test_capture_controls_exercise_every_deliberate_mutation_without_launch(self) -> None:
        controls = load_module("capture_controls_0003", CAPTURE_CONTROLS_PATH)

        result = controls.run_capture_controls()

        self.assertEqual(result.rejected_mutations, 7)
        self.assertEqual(result.target_launches, 0)

    def test_patch_boundary_rejects_accepted_or_production_paths(self) -> None:
        with self.assertRaisesRegex(self.probe.ContainmentRejected, "patch-boundary"):
            self.probe.assert_candidate_only_paths(
                [
                    "projects/ai-usage-telemetry/about/legends-and-lore/rfcs/0001-adapter-ledger-and-sink-contract.md"
                ]
            )

    def test_hash_checker_rejects_a_nonmatching_regular_file(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            target = Path(temporary_directory) / "claude"
            target.write_bytes(b"synthetic-not-the-pinned-executable")

            with self.assertRaisesRegex(self.probe.ContainmentRejected, "build-pin"):
                self.probe.verify_pinned_build(target)


if __name__ == "__main__":
    unittest.main()
