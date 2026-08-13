"""Regression tests for candidate evidence 0003's independent fixture oracle."""

from __future__ import annotations

import importlib.util
import hashlib
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock


EVIDENCE_DIR = Path(__file__).resolve().parents[1]
FIXTURE_PATH = EVIDENCE_DIR / "fixture_0003.json"
ORACLE_PATH = EVIDENCE_DIR / "verify_0003_structural_oracle.py"
CANDIDATE_PATH = EVIDENCE_DIR.parent / "0003-claude-progressive-probe-candidate.md"


def load_module(module_name: str, path: Path):
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"could not load {path.name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


class StructuralOracleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.oracle = load_module("structural_oracle_0003", ORACLE_PATH)

    def test_oracle_accepts_the_complete_predeclared_fixture_matrix(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))

        result = self.oracle.verify_fixture(fixture)

        self.assertEqual(result.case_count, 8)
        self.assertEqual(result.deliberate_mutation_rejections, 4)

    def test_oracle_rejects_a_nonconforming_reuse_case_relabelled_as_progressive(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        case = next(item for item in fixture["cases"] if item["case_id"] == "nonconforming-identity-reuse")
        case["expected_disposition"] = "confirmed-contract-gap"

        with self.assertRaisesRegex(AssertionError, "case-disposition"):
            self.oracle.verify_fixture(fixture)

    def test_oracle_rejects_missing_predeclared_case(self) -> None:
        fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        fixture["cases"] = fixture["cases"][:-1]

        with self.assertRaisesRegex(AssertionError, "case-coverage"):
            self.oracle.verify_fixture(fixture)

    def test_oracle_rejects_a_fixture_with_the_wrong_exact_digest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            wrong_fixture = Path(temporary_directory) / "fixture.json"
            wrong_fixture.write_text('{"synthetic":"wrong"}', encoding="utf-8")

            with mock.patch.object(self.oracle, "FIXTURE_PATH", wrong_fixture):
                with self.assertRaisesRegex(AssertionError, "fixture-digest"):
                    self.oracle.load_fixture()

    def test_candidate_record_is_explicitly_unresolved_and_has_final_artifact_digests(self) -> None:
        candidate = CANDIDATE_PATH.read_text(encoding="utf-8")

        self.assertIn("**Unresolved.**", candidate)
        self.assertIn("target_started=0", candidate)
        self.assertIn("fresh **different** independent high-risk privacy/accounting review", candidate)
        self.assertIn("nested PID namespace", candidate)
        self.assertIn("16,385-byte", candidate)
        self.assertNotIn("PENDING-FINAL-DIGEST", candidate)
        self.assertNotIn("/home/", candidate)

        for relative_path in (
            "fixture_0003.json",
            "verify_0003_structural_oracle.py",
            "claude_progressive_probe_0003.py",
            "runtime/inner_probe_0003.py",
            "runtime/attempt_gate_0003.json",
            "exercise_capture_controls_0003.py",
        ):
            digest = hashlib.sha256((EVIDENCE_DIR / relative_path).read_bytes()).hexdigest()
            self.assertIn(f"`0003/{relative_path}` | `{digest}`", candidate)


if __name__ == "__main__":
    unittest.main()
