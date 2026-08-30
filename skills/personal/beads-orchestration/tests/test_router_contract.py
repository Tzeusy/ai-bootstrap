# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class BeadsRouterContractTests(unittest.TestCase):
    def test_router_stays_small_and_routes_all_workflows(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertLessEqual(len(skill.splitlines()), 80)
        for route in (
            "beads-coordinator",
            "beads-worker",
            "beads-pr-reviewer-worker",
            "beads-cleanup",
            "beads-writer",
        ):
            self.assertIn(f"subskills/{route}/SKILL.md", skill)

    def test_router_preserves_authority_and_grep_first_boundaries(self) -> None:
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8").lower()
        self.assertIn("sole mutation authority", skill)
        self.assertIn("rg -i -n", skill)
        self.assertIn("known errors", skill)

    def test_routing_cases_cover_all_kinds_and_routes(self) -> None:
        payload = json.loads((ROOT / "evals" / "routing.json").read_text(encoding="utf-8"))
        cases = payload["cases"]
        self.assertEqual({case["kind"] for case in cases}, {"positive", "negative", "ambiguous"})
        positive_routes = {
            case["expected_routes"][0] for case in cases if case["kind"] == "positive"
        }
        self.assertEqual(
            positive_routes,
            {
                "beads-coordinator",
                "beads-worker",
                "beads-pr-reviewer-worker",
                "beads-cleanup",
                "beads-writer",
            },
        )


if __name__ == "__main__":
    unittest.main()
