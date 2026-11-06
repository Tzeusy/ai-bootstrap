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


    def test_every_documented_mutation_carries_the_looper_actor(self) -> None:
        for path in (IMPLEMENT, REVIEW):
            for match in BD_MUTATION.finditer(read(path)):
                self.assertIn('--actor "$LOOPER_ID"', match.group(1), f"{path.name}: {match.group(0)}")







if __name__ == "__main__":
    unittest.main()
