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
    def setUp(self) -> None:
        self.gate = load_gate_module()

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

    def assert_denial(self, decision, code: str) -> None:
        self.assertIsInstance(decision, self.gate.CandidateReviewDecision)
        self.assertEqual(decision.status, "candidate-denied")
        self.assertEqual(decision.execution_authority, "none")
        self.assertEqual(decision.required_next_gate, self.gate.REQUIRED_NEXT_GATE)
        self.assertEqual(decision.denial_code, code)

    def test_rejects_a_reset_of_the_consumed_predecessor_attempt(self) -> None:
        reset_predecessor = replace(self.gate.PREDECESSOR_GATE, attempt_consumed=False)
        request = replace(self.valid_request(), predecessor=reset_predecessor)

        self.assert_denial(
            self.gate.bind_successor_attempt_gate(request),
            "predecessor-binding",
        )

    def test_rejects_a_different_predecessor_head_or_gate_identifier(self) -> None:
        different_head = replace(
            self.gate.PREDECESSOR_GATE,
            exact_head="0" * 40,
        )
        self.assert_denial(
            self.gate.bind_successor_attempt_gate(
                replace(self.valid_request(), predecessor=different_head)
            ),
            "predecessor-binding",
        )

        different_gate_protocol = self.gate.SuccessorAttemptGateProtocol()
        self.assert_denial(
            different_gate_protocol.bind(
                replace(self.valid_request(), successor_gate_id="aib-alo-attempt-0003")
            ),
            "successor-gate-id",
        )

    def test_duplicate_valid_request_is_denied_after_the_one_shot_binding(self) -> None:
        request = self.valid_request()

        accepted = self.gate.bind_successor_attempt_gate(request)
        duplicate = self.gate.bind_successor_attempt_gate(request)

        self.assertEqual(accepted.status, "candidate-review-required")
        self.assertEqual(accepted.execution_authority, "none")
        self.assert_denial(duplicate, "attempt-already-consumed")

    def test_none_and_malformed_requests_return_schema_valid_denials(self) -> None:
        protocol = self.gate.SuccessorAttemptGateProtocol()

        self.assert_denial(protocol.bind(None), "request-schema")
        self.assert_denial(protocol.bind(self.valid_request()), "attempt-already-consumed")

        malformed_request_protocol = self.gate.SuccessorAttemptGateProtocol()
        self.assert_denial(malformed_request_protocol.bind(object()), "request-schema")

        malformed_protocol = self.gate.SuccessorAttemptGateProtocol()
        malformed_request = self.gate.SuccessorAttemptGateRequest(
            successor_gate_id=self.gate.SUCCESSOR_GATE_ID,
            predecessor=object(),
        )
        self.assert_denial(malformed_protocol.bind(malformed_request), "predecessor-schema")

    def test_malformed_gate_identifier_is_a_denial_not_an_exception(self) -> None:
        request = self.gate.SuccessorAttemptGateRequest(
            successor_gate_id=None,
            predecessor=self.gate.PREDECESSOR_GATE,
        )

        self.assert_denial(self.gate.bind_successor_attempt_gate(request), "successor-gate-id")

    def test_module_offers_no_target_or_execution_surface(self) -> None:
        source = GATE_PATH.read_text(encoding="utf-8")

        for forbidden_token in ("subprocess", "socket", "bwrap", "--execute", "claude"):
            self.assertNotIn(forbidden_token, source.lower())
        self.assertFalse(hasattr(self.gate, "execute"))
        self.assertFalse(hasattr(self.gate, "launch"))


if __name__ == "__main__":
    unittest.main()
