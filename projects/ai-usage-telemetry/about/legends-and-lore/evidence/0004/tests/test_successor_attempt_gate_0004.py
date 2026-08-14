"""No-target tests for candidate evidence 0004's successor attempt gate."""

from __future__ import annotations

from dataclasses import replace
import importlib.util
from pathlib import Path
import sys
import unittest


EVIDENCE_DIR = Path(__file__).resolve().parents[1]
GATE_PATH = EVIDENCE_DIR / "successor_attempt_gate_0004.py"


def load_gate_module():
    spec = importlib.util.spec_from_file_location("successor_attempt_gate_0004", GATE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("could not load successor_attempt_gate_0004.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SuccessorAttemptGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.gate = load_gate_module()

    def valid_request(self):
        return self.gate.SuccessorAttemptGateRequest(
            successor_gate_id=self.gate.SUCCESSOR_GATE_ID,
            predecessor=self.gate.PREDECESSOR_GATE,
        )

    def test_exact_consumed_predecessor_binds_to_candidate_review_only(self) -> None:
        decision = self.gate.bind_successor_attempt_gate(self.valid_request())

        self.assertEqual(decision.predecessor_commit, "62829a9f65f4527a1a07e29b673666d8bb224935")
        self.assertTrue(decision.predecessor_attempt_consumed)
        self.assertEqual(decision.predecessor_disposition, "unresolved")
        self.assertEqual(decision.status, "candidate-review-required")
        self.assertEqual(decision.execution_authority, "none")
        self.assertEqual(
            decision.required_next_gate,
            "fresh-independent-high-risk-privacy-accounting-review",
        )

    def test_rejects_a_reset_of_the_consumed_predecessor_attempt(self) -> None:
        reset_predecessor = replace(self.gate.PREDECESSOR_GATE, attempt_consumed=False)
        request = replace(self.valid_request(), predecessor=reset_predecessor)

        with self.assertRaisesRegex(self.gate.PredecessorBindingRejected, "predecessor-binding"):
            self.gate.bind_successor_attempt_gate(request)

    def test_rejects_a_different_predecessor_head_or_gate_identifier(self) -> None:
        different_head = replace(
            self.gate.PREDECESSOR_GATE,
            exact_head="0" * 40,
        )
        with self.assertRaisesRegex(self.gate.PredecessorBindingRejected, "predecessor-binding"):
            self.gate.bind_successor_attempt_gate(replace(self.valid_request(), predecessor=different_head))

        with self.assertRaisesRegex(self.gate.PredecessorBindingRejected, "successor-gate-id"):
            self.gate.bind_successor_attempt_gate(
                replace(self.valid_request(), successor_gate_id="aib-alo-attempt-0003")
            )

    def test_module_offers_no_target_or_execution_surface(self) -> None:
        source = GATE_PATH.read_text(encoding="utf-8")

        for forbidden_token in ("subprocess", "socket", "bwrap", "--execute", "claude"):
            self.assertNotIn(forbidden_token, source.lower())
        self.assertFalse(hasattr(self.gate, "execute"))
        self.assertFalse(hasattr(self.gate, "launch"))


if __name__ == "__main__":
    unittest.main()
