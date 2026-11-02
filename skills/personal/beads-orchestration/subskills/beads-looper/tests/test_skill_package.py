# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = SKILL_ROOT / "SKILL.md"
OPENAI_YAML = SKILL_ROOT / "agents" / "openai.yaml"
IMPLEMENT = SKILL_ROOT / "references" / "implement-cycle.md"
REVIEW = SKILL_ROOT / "references" / "review-cycle.md"
VERIFIER = SKILL_ROOT / "references" / "adversarial-verifier.md"
ROUTER = SKILL_ROOT.parents[1] / "SKILL.md"
SAFETY = SKILL_ROOT.parent / "beads-coordinator" / "references" / "runtime-and-safety.md"

# A `bd` invocation that writes tracker state (mirrors the coordinator contract test).
BD_MUTATION = re.compile(
    r"\bbd((?:\s+-C\s+\S+|\s+--actor\s+\S+)*)\s+"
    r"(update|create|close|unclaim|dep add|dep remove|epic close-eligible)(?=\s)"
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class BeadsLooperPackageTests(unittest.TestCase):
    def test_router_routes_to_the_looper(self) -> None:
        router = read(ROUTER)
        self.assertIn("[subskills/beads-looper/SKILL.md](subskills/beads-looper/SKILL.md)", router)
        self.assertIn("Six subskills", router)

    def test_frontmatter_is_trigger_oriented_with_compatibility(self) -> None:
        frontmatter = yaml.safe_load(read(SKILL_MD).split("---", 2)[1])
        self.assertEqual(frontmatter["name"], "beads-looper")
        self.assertTrue(frontmatter["description"].startswith("Use when"))
        self.assertIn("/loop", frontmatter["description"])
        self.assertIn("--if-assignee", frontmatter["compatibility"])

    def test_openai_metadata_mentions_skill(self) -> None:
        interface = yaml.safe_load(read(OPENAI_YAML))["interface"]
        self.assertIn("$beads-looper", interface["default_prompt"])

    def test_looper_registers_as_a_coordinator(self) -> None:
        skill = read(SKILL_MD)
        self.assertIn("coordinator_registry.py new-id", skill)
        self.assertIn("`coordinator:` prefix", skill)
        self.assertIn("capacity.free > 0", skill)
        # The registry note in the coordinator's safety doc must know loopers exist.
        self.assertIn("**Loopers.**", read(SAFETY))

    def test_every_documented_mutation_carries_the_looper_actor(self) -> None:
        for path in (IMPLEMENT, REVIEW):
            for match in BD_MUTATION.finditer(read(path)):
                self.assertIn('--actor "$LOOPER_ID"', match.group(1), f"{path.name}: {match.group(0)}")

    def test_pr_hand_offs_are_compare_and_swap_guarded(self) -> None:
        implement, review = read(IMPLEMENT), read(REVIEW)
        # Implement lane releases the wired unit; it never assigns the review bead.
        create = re.search(r'REVIEW_ID=\$\(bd --actor "\$LOOPER_ID" create .*?--json', implement, re.S)
        self.assertIsNotNone(create)
        self.assertIn("-s blocked -l pr-review,pr-review-task", create.group(0))
        self.assertNotIn("--assignee", create.group(0))
        self.assertIn("always the iteration's last\nwrite", implement)
        self.assertRegex(implement, r'--if-assignee "\$LOOPER_ID" --status blocked[\s\\]+--external-ref')
        # Review lane takes the unit only while it is unassigned and blocked.
        self.assertIn("--if-assignee '' --if-status blocked", review)
        # `--claim` refuses blocked beads, so blocked review beads are taken by guarded update.
        self.assertNotRegex(review, r"update <review-id> --claim")
        # A closed-unmerged release must drop `pr-review` or the ranker never queues it.
        self.assertRegex(review, r"--status open \\\n\s+--assignee '' --remove-label pr-review --append-notes \"\[pr-closed\]")
        self.assertIn("exit 13", review)
        # Corrections go back to the implement lanes; the reviewer never fixes.
        self.assertIn("--add-label review-correction", review)
        self.assertIn("never\nauthors fixes", review)
        for document in (implement, review):
            self.assertIn("coordinator-loop.md#owner-merge-hold", document)
            self.assertIn("held-for-owner", document)
            self.assertIn("cycle", document)
            self.assertIn("frontier/final", document)
        self.assertIn("Merge-Performed: no", review)
        self.assertIn("PR-Closed: no", review)
        self.assertIn("same-head review solely to merge", review)
        self.assertIn("owner already MERGED/CLOSED", review)

    def test_worktrees_never_touch_repo_root_and_die_with_the_bead(self) -> None:
        skill, implement = read(SKILL_MD), read(IMPLEMENT)
        self.assertIn("never move its checkout", skill)
        self.assertIn("never inherit REPO_ROOT's HEAD", implement)
        self.assertIn('git push origin "HEAD:refs/heads/$BASE"', implement)
        self.assertIn('bd worktree remove ".worktrees/parallel-agents/$ID"', implement)
        self.assertIn('git branch -D "agent/$ID"', implement)
        # The review lane frees the PR branch before handing corrections back.
        self.assertIn("Tear down the review worktree **first**", read(REVIEW))

    def test_canary_gaps_stay_closed(self) -> None:
        skill, implement, review = read(SKILL_MD), read(IMPLEMENT), read(REVIEW)
        # REPO_ROOT resolves from any worktree or submodule, and survives compaction.
        self.assertIn('git -C "$COMMON" rev-parse --show-toplevel 2>/dev/null || dirname "$COMMON"', skill)
        self.assertIn("`LOOPER_ID` and\n  `REPO_ROOT` in every iteration report", skill)
        for path in (IMPLEMENT, REVIEW):
            self.assertIn('`../SKILL.md` → "Launch"', " ".join(read(path).split()), path.name)
        # The readiness stamp is the one write on an unheld bead, so it is CAS-guarded.
        self.assertIn("readiness-gate rejection stamp", skill)
        self.assertRegex(implement, r"update <id> --if-assignee '' --add-label needs-shaping")
        # Dead coordinators' blocked beads have an owner; what no lane owns is reported.
        self.assertIn("orphaned_blocked", implement)
        self.assertIn("`orphaned_blocked` rows of kind `pr`", review)
        self.assertIn('"Needs owner"', skill)
        # Local-state beads: owner-named only, moved aside, never deleted.
        self.assertIn("`scope:local-state`", skill)
        self.assertIn("Move, never delete", implement)
        # "Nothing claimable" is defined by claimable rows, not an empty queue.
        self.assertIn("no claimable row", " ".join(read(SAFETY).split()))

    def test_verifier_is_fresh_read_only_and_capped(self) -> None:
        verifier = read(VERIFIER)
        self.assertIn("Give it the work, not your conclusions", verifier)
        self.assertIn("read-only", verifier)
        self.assertIn('"verdict": "pass|fail"', verifier)
        self.assertIn("three verifier runs", verifier)
        self.assertIn("Verifier disputes", verifier)

    def test_numeric_policy_stays_canonical_in_runtime_and_safety(self) -> None:
        # Wake intervals, lane ceilings, and cooldowns are pointed to, never restated.
        for path in (SKILL_MD, IMPLEMENT, REVIEW, VERIFIER):
            contents = read(path)
            self.assertNotRegex(contents, r"\b\d+\s*(?:-\s*\d+\s*)?(?:minutes?|min)\b", path.name)
            self.assertNotRegex(contents, r"no-op wakes", path.name)


if __name__ == "__main__":
    unittest.main()
