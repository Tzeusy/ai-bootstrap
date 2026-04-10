# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import subprocess
import tempfile
import textwrap
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = SKILL_ROOT / "scripts" / "quick_validate.py"


class QuickValidateTests(unittest.TestCase):
    def test_validator_accepts_compatibility_frontmatter(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "example-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    name: example-skill
                    description: Example skill used for validator coverage.
                    compatibility: Requires git and network access.
                    ---

                    # Example Skill
                    """
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(VALIDATOR), str(skill_dir)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Skill is valid!", result.stdout)

    def test_validator_rejects_mismatched_directory_name(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skill_dir = Path(tmp) / "example-skill"
            skill_dir.mkdir()
            (skill_dir / "SKILL.md").write_text(
                textwrap.dedent(
                    """\
                    ---
                    name: different-skill
                    description: Example skill used for validator coverage.
                    ---

                    # Example Skill
                    """
                ),
                encoding="utf-8",
            )

            result = subprocess.run(
                ["python3", str(VALIDATOR), str(skill_dir)],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("directory name", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
