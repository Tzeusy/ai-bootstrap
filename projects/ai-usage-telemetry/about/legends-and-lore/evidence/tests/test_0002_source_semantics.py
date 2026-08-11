"""Regression tests for the non-normative source-semantics evidence record."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import unittest


EVIDENCE_DIR = Path(__file__).resolve().parents[1]
FIXTURE_PATH = EVIDENCE_DIR / "0002-source-semantics-fixtures.json"
VERIFIER_PATH = EVIDENCE_DIR / "verify_0002_source_semantics.py"
CAPTURE_HARNESS_PATH = EVIDENCE_DIR / "exercise_0002_capture_controls.py"
CANDIDATE_PATH = EVIDENCE_DIR / "0002-source-semantics-candidate.md"

EXPECTED_CODEX_SOURCE_REFS = (
    "https://github.com/openai/codex/blob/be6e8eac029b183056b7e4402879f15d2c85f61b/codex-rs/core/src/thread_manager.rs#L1027-L1097",
    "https://github.com/openai/codex/blob/be6e8eac029b183056b7e4402879f15d2c85f61b/codex-rs/core/src/session/mod.rs#L1359-L1396",
    "https://github.com/openai/codex/blob/be6e8eac029b183056b7e4402879f15d2c85f61b/codex-rs/rollout/src/recorder.rs#L832-L871",
    "https://github.com/openai/codex/blob/be6e8eac029b183056b7e4402879f15d2c85f61b/codex-rs/rollout/src/recorder.rs#L1715-L1734",
)
EXACT_IMPACT_REQUIREMENTS = (
    "REQ-source-adapter-profiles-008",
    "REQ-source-adapter-profiles-009",
    "REQ-source-adapter-profiles-010",
    "REQ-event-identity-and-normalization-002",
    "REQ-event-identity-and-normalization-003",
    "REQ-event-identity-and-normalization-004",
    "REQ-event-identity-and-normalization-005",
    "REQ-durable-local-ledger-003",
    "REQ-durable-local-ledger-004",
    "REQ-synthetic-usage-spine-001",
    "REQ-synthetic-usage-spine-002",
    "REQ-synthetic-usage-spine-003",
    "REQ-synthetic-usage-spine-004",
    "REQ-synthetic-usage-spine-005",
    "REQ-synthetic-usage-spine-006",
    "REQ-stream-reconciliation-and-health-001",
    "REQ-stream-reconciliation-and-health-002",
    "REQ-stream-reconciliation-and-health-003",
    "REQ-stream-reconciliation-and-health-004",
    "REQ-stream-reconciliation-and-health-005",
    "REQ-stream-reconciliation-and-health-006",
    "REQ-stream-reconciliation-and-health-007",
    "REQ-stream-reconciliation-and-health-008",
    "REQ-stream-reconciliation-and-health-009",
    "REQ-stream-reconciliation-and-health-010",
    "REQ-release-profile-governance-002",
    "REQ-release-profile-governance-004",
    "REQ-release-profile-governance-006",
    "REQ-release-profile-governance-007",
)


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def load_fixture_value() -> dict[str, object]:
    return json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))


class SourceSemanticsEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.verifier = load_module("source_semantics_verifier", VERIFIER_PATH)

    def test_fixture_uses_exact_pinned_codex_source_ranges(self) -> None:
        data = load_fixture_value()

        self.assertEqual(
            tuple(data["pins"]["codex"]["public_source_refs"]),
            EXPECTED_CODEX_SOURCE_REFS,
        )

    def test_verifier_rejects_unregistered_fixture_scalar(self) -> None:
        data = load_fixture_value()
        data["unregistered_scalar"] = "synthetic-only"

        with self.assertRaisesRegex(AssertionError, "fixture-top-level-keys"):
            self.verifier.verify_structure(data)

    def test_capture_harness_executes_declared_controls_without_touching_values(self) -> None:
        harness = load_module("source_semantics_capture_harness", CAPTURE_HARNESS_PATH)

        result = harness.run_capture_controls()

        data = load_fixture_value()
        self.assertEqual(result.positive_canary_lanes, tuple(data["safety"]["canary_lanes"]))
        self.assertEqual(result.rejected_controls, tuple(data["safety"]["negative_mutations"]))
        self.assertEqual(result.synthetic_value_touches, 0)

    def test_candidate_handoff_names_every_exact_impact_surface(self) -> None:
        candidate = CANDIDATE_PATH.read_text(encoding="utf-8")

        self.assertNotIn("REQ-synthetic-usage-spine-*", candidate)
        self.assertNotIn("REQ-stream-reconciliation-and-health-*", candidate)
        for requirement in EXACT_IMPACT_REQUIREMENTS:
            self.assertIn(requirement, candidate)
        for path in (
            "tests/spec/test_event_identity_and_normalization.py",
            "tests/spec/test_source_adapter_profiles.py",
            "tests/spec/test_stream_reconciliation_and_health.py",
            "tests/fixtures/codex/rollout-copied-prefix.jsonl",
            "tests/oracles/codex_copied_prefix_oracle.py",
        ):
            self.assertIn(path, candidate)


if __name__ == "__main__":
    unittest.main()
