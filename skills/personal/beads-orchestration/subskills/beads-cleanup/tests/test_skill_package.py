# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = SKILL_ROOT / "SKILL.md"
OPENAI_YAML = SKILL_ROOT / "agents" / "openai.yaml"
LOCAL_STATE = SKILL_ROOT / "references" / "local-state-reconciliation.md"
PR_RECON = SKILL_ROOT / "references" / "pr-review-reconciliation.md"
REPORTING = SKILL_ROOT / "references" / "reporting.md"


class BeadsCleanupPackageTests(unittest.TestCase):
    def test_skill_is_slimmer_than_two_hundred_lines(self) -> None:
        line_count = len(SKILL_MD.read_text(encoding="utf-8").splitlines())
        self.assertLessEqual(line_count, 200)

    def test_skill_frontmatter_has_trigger_metadata_and_compatibility(self) -> None:
        frontmatter = SKILL_MD.read_text(encoding="utf-8").split("---", 2)[1]
        self.assertIn("name: beads-cleanup", frontmatter)
        self.assertIn(
            "description: Use when a Beads coordinator needs to reconcile",
            frontmatter,
        )
        self.assertIn("metadata:", frontmatter)
        self.assertIn("owner: tze", frontmatter)
        self.assertIn("authors:", frontmatter)
        self.assertIn('last_reviewed: "2026-04-12"', frontmatter)
        self.assertIn("compatibility:", frontmatter)
        self.assertIn("bd", frontmatter)
        self.assertIn("gh", frontmatter)

    def test_skill_routes_to_references_and_companion_docs(self) -> None:
        contents = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("references/local-state-reconciliation.md", contents)
        self.assertIn("references/pr-review-reconciliation.md", contents)
        self.assertIn("references/reporting.md", contents)
        self.assertIn("../beads-coordinator/references/runtime-and-safety.md", contents)
        self.assertIn("../beads-coordinator/references/coordinator-loop.md", contents)
        self.assertIn("../beads-pr-reviewer-worker/SKILL.md", contents)

    def test_skill_documents_operational_boundaries(self) -> None:
        contents = SKILL_MD.read_text(encoding="utf-8")
        self.assertRegex(contents, re.compile(r"Never implement code", re.IGNORECASE))
        self.assertRegex(
            contents,
            re.compile(r"Never create new beads from cleanup", re.IGNORECASE),
        )
        self.assertIn("Never touch `.beads/dolt/` manually.", contents)

    def test_openai_metadata_exists_and_mentions_skill(self) -> None:
        self.assertTrue(OPENAI_YAML.exists(), OPENAI_YAML)
        contents = OPENAI_YAML.read_text(encoding="utf-8")
        self.assertIn('display_name: "Beads Cleanup"', contents)
        self.assertIn("short_description:", contents)
        self.assertIn("$beads-cleanup", contents)

    def test_expected_reference_files_exist(self) -> None:
        for path in (LOCAL_STATE, PR_RECON, REPORTING):
            self.assertTrue(path.exists(), path)

    def test_references_cover_cleanup_passes_and_report(self) -> None:
        local_state = LOCAL_STATE.read_text(encoding="utf-8")
        pr_recon = PR_RECON.read_text(encoding="utf-8")
        reporting = REPORTING.read_text(encoding="utf-8")
        self.assertIn("Pass 1: Stale `in_progress` Beads", local_state)
        self.assertIn("Pass 4: Blocked Beads Whose Blockers Are Closed", local_state)
        self.assertIn("Pass 5a: Dolt Health", local_state)
        self.assertIn("Pass 6: Stale `review-running` Labels", local_state)
        self.assertIn("Pass 2: Blocked Original Beads With `pr-review`", pr_recon)
        self.assertIn("Pass 3: Blocked `pr-review-task` Review Beads", pr_recon)
        self.assertIn("## Beads Cleanup Report", reporting)
        self.assertIn("| Metric | Count |", reporting)


if __name__ == "__main__":
    unittest.main()
