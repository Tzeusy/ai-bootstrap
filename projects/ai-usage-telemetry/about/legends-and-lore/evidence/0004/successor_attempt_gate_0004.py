"""Pure, candidate-only binding for the consumed predecessor evidence gate."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PredecessorGate:
    issue_id: str
    pull_request_number: int
    exact_head: str
    candidate_record_sha256: str
    artifact_sha256: tuple[str, ...]
    attempt_consumed: bool
    disposition: str
    starts: int
    completions: int


PREDECESSOR_GATE = PredecessorGate(
    issue_id="aib-alo",
    pull_request_number=22,
    exact_head="62829a9f65f4527a1a07e29b673666d8bb224935",
    candidate_record_sha256="6126f3e18d7bf8ded6d788143b5857fcb628442759f701f04e1a68ff8a51b9c0",
    artifact_sha256=(
        "11bc385d4dbb5fb59aea2e53bd3134b42a6aea351ab39146388de3bf6d531b4e",
        "2585565d1853e9489664eb5e22fa172f0fe0178447f2bebcd7a946d972860caa",
        "3aeff02535c00704d561b7c28f92f12a3e5eff2aa1a4f141e1a2ff253746f491",
        "128e0d800bcdba78c13efe6d02eddec50980b1656b520c4737103d02eec089fc",
        "468d099363596a22708a4f4657d866bd4c87c3e83832663ca588bc27a0c8bc41",
    ),
    attempt_consumed=True,
    disposition="unresolved",
    starts=0,
    completions=0,
)
SUCCESSOR_GATE_ID = "aib-g0k-successor-attempt-gate-0004"
REQUIRED_NEXT_GATE = "fresh-independent-high-risk-privacy-accounting-review"


@dataclass(frozen=True)
class SuccessorAttemptGateRequest:
    successor_gate_id: str
    predecessor: PredecessorGate


@dataclass(frozen=True)
class CandidateAttemptState:
    """Candidate-only terminal state bound to one predecessor/successor pair."""

    predecessor: PredecessorGate
    successor_gate_id: str
    candidate_attempt_consumed: bool
    disposition: str


CANDIDATE_ATTEMPT_STATE = CandidateAttemptState(
    predecessor=PREDECESSOR_GATE,
    successor_gate_id=SUCCESSOR_GATE_ID,
    candidate_attempt_consumed=True,
    disposition="consumed-without-launch",
)


@dataclass(frozen=True)
class CandidateReviewDecision:
    predecessor_commit: str
    predecessor_attempt_consumed: bool
    predecessor_disposition: str
    status: str
    execution_authority: str
    required_next_gate: str
    denial_code: str


def _decision(status: str, denial_code: str) -> CandidateReviewDecision:
    return CandidateReviewDecision(
        predecessor_commit=PREDECESSOR_GATE.exact_head,
        predecessor_attempt_consumed=PREDECESSOR_GATE.attempt_consumed,
        predecessor_disposition=PREDECESSOR_GATE.disposition,
        status=status,
        execution_authority="none",
        required_next_gate=REQUIRED_NEXT_GATE,
        denial_code=denial_code,
    )


def _rejection_code(request: object) -> str | None:
    if not isinstance(request, SuccessorAttemptGateRequest):
        return "request-schema"
    if not isinstance(request.successor_gate_id, str) or request.successor_gate_id != SUCCESSOR_GATE_ID:
        return "successor-gate-id"
    if not isinstance(request.predecessor, PredecessorGate):
        return "predecessor-schema"
    if request.predecessor != PREDECESSOR_GATE:
        return "predecessor-binding"
    if not PREDECESSOR_GATE.attempt_consumed:
        return "predecessor-not-consumed"
    if PREDECESSOR_GATE.disposition != "unresolved":
        return "predecessor-disposition"
    if PREDECESSOR_GATE.starts != 0:
        return "predecessor-start-count"
    if PREDECESSOR_GATE.completions != 0:
        return "predecessor-completion-count"
    return None


def _candidate_state_rejection_code(state: object) -> str | None:
    if not isinstance(state, CandidateAttemptState):
        return "candidate-state-schema"
    if state != CANDIDATE_ATTEMPT_STATE:
        return "candidate-state-binding"
    return None


def bind_successor_attempt_gate(
    request: object,
    state: object = CANDIDATE_ATTEMPT_STATE,
) -> CandidateReviewDecision:
    """Deny every retry against the fixed, already consumed candidate state."""

    rejection_code = _rejection_code(request)
    if rejection_code is not None:
        return _decision("candidate-denied", rejection_code)

    state_rejection_code = _candidate_state_rejection_code(state)
    if state_rejection_code is not None:
        return _decision("candidate-denied", state_rejection_code)

    return _decision("candidate-denied", "attempt-already-consumed")
