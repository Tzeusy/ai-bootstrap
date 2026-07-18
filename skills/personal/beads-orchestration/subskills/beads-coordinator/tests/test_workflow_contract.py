# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
LOOP = SKILL_ROOT / "references" / "coordinator-loop.md"
SAFETY = SKILL_ROOT / "references" / "runtime-and-safety.md"


class BeadsCoordinatorWorkflowContractTests(unittest.TestCase):
    def test_dispatch_requires_structured_acceptance_and_cohesion_check(self) -> None:
        contents = LOOP.read_text(encoding="utf-8").lower()
        self.assertIn("dispatch readiness", contents)
        self.assertIn("cohesion", contents)
        self.assertIn("acceptance criteria", contents)

    def test_discoveries_are_classified_before_bead_creation(self) -> None:
        contents = LOOP.read_text(encoding="utf-8").lower()
        for phrase in (
            "current-pr correctness",
            "prerequisite blocker",
            "new behavior",
            "duplicate",
        ):
            self.assertIn(phrase, contents)

    def test_review_risk_tiers_and_exact_head_are_explicit(self) -> None:
        contents = SAFETY.read_text(encoding="utf-8").lower()
        self.assertIn("review risk tiers", contents)
        self.assertIn("exact head sha", contents)
        self.assertIn("auth", contents)
        self.assertIn("data loss", contents)

    def test_refresh_is_event_driven_with_safety_sweep(self) -> None:
        contents = LOOP.read_text(encoding="utf-8").lower()
        self.assertIn("event-driven", contents)
        self.assertIn("30-minute safety sweep", contents)

    def test_dispatch_preserves_context_affinity_when_safe(self) -> None:
        contents = LOOP.read_text(encoding="utf-8").lower()
        self.assertIn("context affinity", contents)

    def test_review_cycle_state_has_a_canonical_note(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn("[review-cycle]", contents)
        self.assertIn("substantive_reopenings=", contents)
        self.assertIn("reviewed_head_sha=", contents)

    def test_correction_lane_temporarily_detaches_and_restores_review_gate(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn("bd dep remove <original-id> <review-id>", contents)
        self.assertIn("REVIEW_CORRECTION_MODE=yes", contents)
        self.assertIn("bd dep add <original-id> <review-id>", contents)

    def test_review_bead_template_is_packet_complete(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn('--acceptance="1. Record reviewer identity', contents)
        self.assertIn('--design="Independent exact-head review', contents)

    def test_correction_worktree_has_an_explicit_re_review_hand_back(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn("Correction-to-re-review hand-back", contents)
        self.assertIn(
            "git -C <review-worktree> checkout -B agent/<original-id> origin/agent/<original-id>",
            contents,
        )
        self.assertIn("expected reviewer branch is `agent/<original-id>`", contents)

    def test_initial_review_bootstrap_uses_two_stage_branch_attestation(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn("Stage 1 — dispatch bootstrap", contents)
        self.assertIn("`agent/<review-id>`", contents)
        self.assertIn("Stage 2 — prepared-head attestation", contents)
        self.assertIn("`agent/<original-id>`", contents)
        self.assertIn("Re-review hand-back starts at Stage 2", contents)


if __name__ == "__main__":
    unittest.main()
