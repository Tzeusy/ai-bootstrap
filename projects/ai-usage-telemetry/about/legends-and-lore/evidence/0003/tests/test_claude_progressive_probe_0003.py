"""Behavioral tests for candidate evidence 0003's isolated Claude probe."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
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

    def assert_rejected_before_launch(self, plan, *, pin_ok: bool = True) -> None:
        launcher = RecordingLauncher()
        with self.assertRaises(self.probe.ContainmentRejected):
            self.probe.launch_if_safe(plan, pin_checker=lambda _target: pin_ok, launcher=launcher)
        self.assertEqual(launcher.calls, 0)

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

    def test_pin_or_environment_failure_returns_only_unresolved_safe_summary(self) -> None:
        with mock.patch.object(
            self.probe,
            "resolve_claude_executable",
            side_effect=self.probe.ContainmentRejected("build-pin-executable-missing"),
        ):
            result = self.probe.execute_isolated_probe()

        self.assertEqual(result["disposition"], "unresolved")
        self.assertEqual(result["counts"], {})

    def test_unresolved_public_return_is_schema_valid_without_exception_text(self) -> None:
        forbidden_exception_text = "THESIS_FORBIDDEN_RAW_OUTPUT"
        with mock.patch.object(
            self.probe,
            "resolve_claude_executable",
            side_effect=self.probe.ContainmentRejected(forbidden_exception_text),
        ):
            result = self.probe.execute_isolated_probe()

        self.assertNotIn(forbidden_exception_text, json.dumps(result, sort_keys=True))
        self.probe.validate_safe_summary(result)

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
