"""Pure, candidate-only binding for the consumed predecessor evidence gate."""

from __future__ import annotations

from dataclasses import dataclass


class PredecessorBindingRejected(ValueError):
    """Raised when a candidate tries to replace or weaken the predecessor gate."""


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
class CandidateReviewDecision:
    predecessor_commit: str
    predecessor_attempt_consumed: bool
    predecessor_disposition: str
    status: str
    execution_authority: str
    required_next_gate: str


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise PredecessorBindingRejected(code)


def bind_successor_attempt_gate(request: SuccessorAttemptGateRequest) -> CandidateReviewDecision:
    """Bind a successor review request to the one fixed consumed predecessor."""

    _require(request.successor_gate_id == SUCCESSOR_GATE_ID, "successor-gate-id")
    _require(request.predecessor == PREDECESSOR_GATE, "predecessor-binding")
    _require(PREDECESSOR_GATE.attempt_consumed, "predecessor-not-consumed")
    _require(PREDECESSOR_GATE.disposition == "unresolved", "predecessor-disposition")
    _require(PREDECESSOR_GATE.starts == 0, "predecessor-start-count")
    _require(PREDECESSOR_GATE.completions == 0, "predecessor-completion-count")

    return CandidateReviewDecision(
        predecessor_commit=PREDECESSOR_GATE.exact_head,
        predecessor_attempt_consumed=PREDECESSOR_GATE.attempt_consumed,
        predecessor_disposition=PREDECESSOR_GATE.disposition,
        status="candidate-review-required",
        execution_authority="none",
        required_next_gate=REQUIRED_NEXT_GATE,
    )
