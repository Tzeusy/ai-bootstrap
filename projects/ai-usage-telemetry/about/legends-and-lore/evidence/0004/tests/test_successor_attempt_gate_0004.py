"""No-target tests for candidate evidence 0004's successor attempt gate."""

from __future__ import annotations

from dataclasses import fields, replace
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

    def test_exact_consumed_predecessor_is_already_terminal_without_launch(self) -> None:
        decision = self.gate.bind_successor_attempt_gate(self.valid_request())

        self.assertEqual(decision.predecessor_commit, "62829a9f65f4527a1a07e29b673666d8bb224935")
        self.assertTrue(decision.predecessor_attempt_consumed)
        self.assertEqual(decision.predecessor_disposition, "unresolved")
        self.assert_denial(decision, "attempt-already-consumed")

    def assert_denial(self, decision, code: str) -> None:
        self.assertEqual(decision.status, "candidate-denied")
        self.assertEqual(decision.execution_authority, "none")
        self.assertEqual(decision.required_next_gate, self.gate.REQUIRED_NEXT_GATE)
        self.assertEqual(decision.denial_code, code)

    def partial_instance(self, complete_instance, missing_field: str):
        partial = object.__new__(type(complete_instance))
        for field in fields(complete_instance):
            if field.name != missing_field:
                object.__setattr__(partial, field.name, getattr(complete_instance, field.name))
        return partial

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

        self.assert_denial(
            self.gate.bind_successor_attempt_gate(
                replace(self.valid_request(), successor_gate_id="aib-alo-attempt-0003")
            ),
            "successor-gate-id",
        )

    def test_fresh_module_load_and_restart_retry_are_terminal(self) -> None:
        request = self.valid_request()
        fresh_module = load_gate_module()
        restart_module = load_gate_module()
        fresh_request = fresh_module.SuccessorAttemptGateRequest(
            successor_gate_id=fresh_module.SUCCESSOR_GATE_ID,
            predecessor=fresh_module.PREDECESSOR_GATE,
        )
        restart_request = restart_module.SuccessorAttemptGateRequest(
            successor_gate_id=restart_module.SUCCESSOR_GATE_ID,
            predecessor=restart_module.PREDECESSOR_GATE,
        )

        initial = self.gate.bind_successor_attempt_gate(request)
        fresh_load = fresh_module.bind_successor_attempt_gate(fresh_request)
        restart_retry = restart_module.bind_successor_attempt_gate(restart_request)

        self.assertIsInstance(initial, self.gate.CandidateReviewDecision)
        self.assertIsInstance(fresh_load, fresh_module.CandidateReviewDecision)
        self.assertIsInstance(restart_retry, restart_module.CandidateReviewDecision)
        self.assert_denial(initial, "attempt-already-consumed")
        self.assert_denial(fresh_load, "attempt-already-consumed")
        self.assert_denial(restart_retry, "attempt-already-consumed")

    def test_none_and_malformed_requests_return_schema_valid_denials(self) -> None:
        self.assert_denial(self.gate.bind_successor_attempt_gate(None), "request-schema")
        self.assert_denial(self.gate.bind_successor_attempt_gate(object()), "request-schema")
        malformed_request = self.gate.SuccessorAttemptGateRequest(
            successor_gate_id=self.gate.SUCCESSOR_GATE_ID,
            predecessor=object(),
        )
        self.assert_denial(
            self.gate.bind_successor_attempt_gate(malformed_request),
            "predecessor-schema",
        )

    def test_malformed_gate_identifier_is_a_denial_not_an_exception(self) -> None:
        request = self.gate.SuccessorAttemptGateRequest(
            successor_gate_id=None,
            predecessor=self.gate.PREDECESSOR_GATE,
        )

        self.assert_denial(self.gate.bind_successor_attempt_gate(request), "successor-gate-id")

    def test_schema_valid_tampered_candidate_state_is_content_free_and_denied(self) -> None:
        reset_state = replace(
            self.gate.CANDIDATE_ATTEMPT_STATE,
            candidate_attempt_consumed=False,
        )
        tampered_predecessor_state = replace(
            self.gate.CANDIDATE_ATTEMPT_STATE,
            predecessor=replace(self.gate.PREDECESSOR_GATE, exact_head="0" * 40),
        )

        self.assert_denial(
            self.gate.bind_successor_attempt_gate(self.valid_request(), reset_state),
            "candidate-state-binding",
        )
        self.assert_denial(
            self.gate.bind_successor_attempt_gate(
                self.valid_request(), tampered_predecessor_state
            ),
            "candidate-state-binding",
        )

    def test_candidate_state_schema_mismatch_is_a_denial_not_an_exception(self) -> None:
        self.assert_denial(
            self.gate.bind_successor_attempt_gate(self.valid_request(), object()),
            "candidate-state-schema",
        )

    def test_partial_typed_inputs_are_terminal_content_free_denials(self) -> None:
        for field in fields(self.valid_request()):
            self.assert_denial(
                self.gate.bind_successor_attempt_gate(
                    self.partial_instance(self.valid_request(), field.name)
                ),
                "request-schema",
            )

        for field in fields(self.gate.PREDECESSOR_GATE):
            request = replace(
                self.valid_request(),
                predecessor=self.partial_instance(self.gate.PREDECESSOR_GATE, field.name),
            )
            self.assert_denial(
                self.gate.bind_successor_attempt_gate(request),
                "predecessor-schema",
            )

        for field in fields(self.gate.CANDIDATE_ATTEMPT_STATE):
            self.assert_denial(
                self.gate.bind_successor_attempt_gate(
                    self.valid_request(),
                    self.partial_instance(self.gate.CANDIDATE_ATTEMPT_STATE, field.name),
                ),
                "candidate-state-schema",
            )

        self.assert_denial(
            self.gate.bind_successor_attempt_gate(
                self.valid_request(),
                replace(
                    self.gate.CANDIDATE_ATTEMPT_STATE,
                    predecessor=self.partial_instance(
                        self.gate.PREDECESSOR_GATE,
                        "exact_head",
                    ),
                ),
            ),
            "candidate-state-binding",
        )

    def test_tampered_typed_inputs_are_terminal_content_free_denials(self) -> None:
        self.assert_denial(
            self.gate.bind_successor_attempt_gate(
                replace(self.valid_request(), successor_gate_id=object())
            ),
            "successor-gate-id",
        )
        self.assert_denial(
            self.gate.bind_successor_attempt_gate(
                replace(self.valid_request(), predecessor=replace(
                    self.gate.PREDECESSOR_GATE,
                    artifact_sha256=(object(),),
                ))
            ),
            "predecessor-binding",
        )
        self.assert_denial(
            self.gate.bind_successor_attempt_gate(
                self.valid_request(),
                replace(self.gate.CANDIDATE_ATTEMPT_STATE, disposition=object()),
            ),
            "candidate-state-binding",
        )

    def test_module_exposes_no_resettable_protocol_surface(self) -> None:
        self.assertFalse(hasattr(self.gate, "SuccessorAttemptGateProtocol"))
        self.assertTrue(self.gate.CANDIDATE_ATTEMPT_STATE.candidate_attempt_consumed)
        self.assertEqual(
            self.gate.CANDIDATE_ATTEMPT_STATE.predecessor,
            self.gate.PREDECESSOR_GATE,
        )
        self.assertEqual(
            self.gate.CANDIDATE_ATTEMPT_STATE.successor_gate_id,
            self.gate.SUCCESSOR_GATE_ID,
        )

    def test_module_offers_no_target_or_execution_surface(self) -> None:
        source = GATE_PATH.read_text(encoding="utf-8")

        for forbidden_token in ("subprocess", "socket", "bwrap", "--execute", "claude"):
            self.assertNotIn(forbidden_token, source.lower())
        self.assertFalse(hasattr(self.gate, "execute"))
        self.assertFalse(hasattr(self.gate, "launch"))


if __name__ == "__main__":
    unittest.main()
