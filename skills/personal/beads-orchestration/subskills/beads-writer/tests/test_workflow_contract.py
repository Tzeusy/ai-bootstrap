# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ROUTER = SKILL_ROOT.parents[1] / "SKILL.md"
WORKFLOW = SKILL_ROOT / "references" / "workflow.md"
CHECKLIST = SKILL_ROOT / "references" / "quality-checklist.md"
RECONCILIATION = SKILL_ROOT / "references" / "reconciliation-beads.md"


class BeadsWriterWorkflowContractTests(unittest.TestCase):
    def test_dedupe_scan_includes_recent_history_and_delivery_surfaces(self) -> None:
        contents = WORKFLOW.read_text(encoding="utf-8").lower()
        for phrase in ("recently closed", "open prs", "symbols", "files"):
            self.assertIn(phrase, contents)

    def test_dispatch_packet_is_structured(self) -> None:
        contents = WORKFLOW.read_text(encoding="utf-8").lower()
        for phrase in (
            "outcome",
            "non-goals",
            "governing spec",
            "trust boundaries",
            "failure",
            "concurrency",
            "idempotence",
            "documentation",
            "verification",
        ):
            self.assertIn(phrase, contents)

    def test_checklist_has_cohesion_and_dispatch_gates(self) -> None:
        contents = CHECKLIST.read_text(encoding="utf-8").lower()
        self.assertIn("cohesion", contents)
        self.assertIn("dispatch-ready", contents)

    def test_standalone_writer_is_an_explicit_mutation_authority(self) -> None:
        contents = ROUTER.read_text(encoding="utf-8").lower()
        self.assertIn("standalone beads-writer", contents)

    def test_reconciliation_workers_report_gaps_to_coordinator(self) -> None:
        contents = " ".join(RECONCILIATION.read_text(encoding="utf-8").lower().split())
        self.assertIn("report gap candidates", contents)
        self.assertNotIn("a. create a new child bead", contents)


if __name__ == "__main__":
    unittest.main()
