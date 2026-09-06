# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
LOOP = SKILL_ROOT / "references" / "coordinator-loop.md"
SAFETY = SKILL_ROOT / "references" / "runtime-and-safety.md"
WRITER = SKILL_ROOT.parent / "beads-writer" / "SKILL.md"
TOKEN_EFFICIENCY = SKILL_ROOT.parents[1] / "references" / "token-efficiency.md"
NORMALIZER = SKILL_ROOT / "scripts" / "normalize_pr_review_state.py"
SKILL_AUDIT_WORKFLOW = SKILL_ROOT.parents[4] / ".github" / "workflows" / "skill-audit.yml"


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

    def test_codex_model_selection_matches_complexity_and_design_policy(self) -> None:
        contents = SAFETY.read_text(encoding="utf-8")
        self.assertIn("| Strategy | Claude | Codex / ChatGPT | Gemini |", contents)
        for row in (
            "| `EPIC_COMPLEXITY_MODEL` | Opus 4.8 | 5.6 Sol Medium | gemini-3-pro |",
            "| `HIGH_COMPLEXITY_MODEL` | Sonnet 5 | 5.6 Sol Medium | gemini-3-pro |",
            "| `MEDIUM_COMPLEXITY_MODEL` | Sonnet 5 | 5.6 Luna Max | gemini-3-pro |",
            "| `LOW_COMPLEXITY_MODEL` | 4.5 Haiku | 5.6 Luna Max | gemini-3-flash-preview |",
            "| `DESIGN_AND_SPECIFICATION_MODEL` | Sonnet 5 | 5.6 Sol High | gemini-3-pro |",
        ):
            self.assertIn(row, contents)
        for binding in (
            "| 5.6 Luna Max | `gpt-5.6-luna` | `max` |",
            "| 5.6 Sol Medium | `gpt-5.6-sol` | `medium` |",
            "| 5.6 Sol High | `gpt-5.6-sol` | `high` |",
        ):
            self.assertIn(binding, contents)
        self.assertIn("Design/specification override", contents)
        self.assertIn("before the complexity-label fast path", contents)
        for path in (WRITER, TOKEN_EFFICIENCY):
            self.assertIn("design/specification override", path.read_text(encoding="utf-8"))

    def test_refresh_is_event_driven_with_cache_bounded_wakes(self) -> None:
        loop = LOOP.read_text(encoding="utf-8").lower()
        self.assertIn("event-driven", loop)
        self.assertIn("no-progress frontier", loop)
        self.assertIn("safety sweep", loop)
        # Numbers are canonical in runtime-and-safety.md; the loop only points.
        safety = SAFETY.read_text(encoding="utf-8").lower()
        self.assertIn("orchestrator wake cadence", safety)
        self.assertIn("4m50s", safety)
        self.assertIn("60 minutes", safety)
        self.assertIn("3 consecutive no-op wakes", safety)
        self.assertNotIn("30-minute safety sweep", loop)

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

    def test_queue_membership_uses_entry_and_never_infers_rebase_from_absence(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn("mergeQueueEntry{position enqueuedAt} labels(first:20)", contents)
        self.assertIn("`merge_queue_entry` is non-null", contents)
        self.assertIn("queue metadata alone", contents)
        self.assertNotIn("the queue ejected it", contents)

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

    def test_post_merge_cleanup_maps_original_and_review_ids(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        cleanup = contents.split(
            "### Post-closure branch and worktree cleanup (merged PRs)", 1
        )[1].split("Priority rule:", 1)[0]
        for command in (
            'git push origin --delete "agent/${ORIGINAL_ID}"',
            'bd worktree remove ".worktrees/parallel-agents/${REVIEW_ID}"',
            'git branch -D "agent/${ORIGINAL_ID}"',
            'git branch -D "agent/${REVIEW_ID}"',
        ):
            self.assertIn(command, cleanup)
        self.assertIn(
            "the transferred worktree path remains keyed by `REVIEW_ID`",
            cleanup,
        )
        self.assertNotIn("agent/<id>", cleanup)

    def test_step_zero_uses_the_report_only_normalizer_then_reverifies_before_mutation(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertTrue(NORMALIZER.exists(), NORMALIZER)
        self.assertIn("scripts/normalize_pr_review_state.py", contents)
        self.assertIn("beads-pr-review-normalization/v1", contents)
        self.assertIn("immediately before each actual mutation", contents)
        self.assertIn("sole PR-state mutator", contents)
        self.assertIn("manual-triage", contents)
        # The fail-closed contract is canonical in the script docstring, not the
        # loop doc, so the coordinator does not re-read it every cycle.
        self.assertIn("module docstring", contents)
        docstring = NORMALIZER.read_text(encoding="utf-8").split('"""', 2)[1]
        for phrase in (
            "Fail-closed contract",
            "manual-triage",
            "self-referential",
            "resolver `issue_id`",
            "required label, status, or uniqueness",
            "creation timestamp",
            "`gh-pr:<N>`",
            "skip-command-failure",
            "cyclic-review-relation",
            "duplicate review-ID",
            "same original",
        ):
            self.assertIn(phrase, docstring)

    def test_review_deduplication_uses_parsed_chronology_and_fails_closed(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn("parsed creation chronology", contents)
        self.assertIn("partial manual triage", contents)
        self.assertIn("never choose by raw timestamp text", contents)

    def test_pr_ci_runs_only_the_report_only_fake_command_suites(self) -> None:
        contents = SKILL_AUDIT_WORKFLOW.read_text(encoding="utf-8")
        marker = "      - name: Run report-only Beads safety suites"
        self.assertIn(marker, contents)
        step = contents.split(marker, 1)[1].split(
            "      - name:", 1
        )[0]
        for command in (
            "uv run skills/personal/beads-orchestration/subskills/beads-coordinator/tests/test_normalize_pr_review_state.py",
            "uv run skills/personal/beads-orchestration/subskills/beads-cleanup/tests/test_cleanup_scan.py",
            "uv run skills/personal/beads-orchestration/subskills/beads-pr-reviewer-worker/tests/test_scripts.py",
        ):
            self.assertIn(command, step)
        self.assertNotIn("bd ", step)
        self.assertNotIn("gh ", step)


if __name__ == "__main__":
    unittest.main()
