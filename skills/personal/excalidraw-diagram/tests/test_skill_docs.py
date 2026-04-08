# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SKILL_MD = SKILL_DIR / "SKILL.md"
README_MD = SKILL_DIR / "README.md"


class SkillDocsTests(unittest.TestCase):
    def test_skill_frontmatter_declares_compatibility(self):
        contents = SKILL_MD.read_text(encoding="utf-8")
        frontmatter = contents.split("---", 2)[1]

        self.assertIn("compatibility:", frontmatter)
        self.assertIn("Python", frontmatter)
        self.assertIn("uv", frontmatter)
        self.assertNotIn("compatibility:\n", frontmatter)

    def test_docs_use_relative_script_paths(self):
        for path in (SKILL_MD, README_MD):
            contents = path.read_text(encoding="utf-8")
            self.assertNotIn(".claude/skills/excalidraw-diagram", contents, path.name)
            self.assertIn("scripts/render_excalidraw.py", contents, path.name)

    def test_docs_do_not_reference_removed_dark_mode_or_uv_sync(self):
        for path in (SKILL_MD, README_MD):
            contents = path.read_text(encoding="utf-8")
            self.assertNotIn("--dark", contents, path.name)
            self.assertNotIn("uv sync", contents, path.name)

    def test_skill_is_slimmer_than_five_hundred_lines(self):
        line_count = len(SKILL_MD.read_text(encoding="utf-8").splitlines())
        self.assertLessEqual(line_count, 500)

    def test_theme_catalog_is_documented(self):
        contents = README_MD.read_text(encoding="utf-8")

        self.assertRegex(contents, re.compile(r"theme catalog", re.IGNORECASE))
        self.assertRegex(contents, re.compile(r"default theme", re.IGNORECASE))

    def test_docs_explain_vendored_bundle_refresh_flow(self):
        for path in (SKILL_MD, README_MD):
            contents = path.read_text(encoding="utf-8")
            self.assertRegex(contents, re.compile(r"scripts/refresh\.sh", re.IGNORECASE), path.name)
            self.assertRegex(contents, re.compile(r"vendored|bundle", re.IGNORECASE), path.name)

    def test_skill_and_readme_document_mermaid_interoperability(self):
        skill_contents = SKILL_MD.read_text(encoding="utf-8")
        readme_contents = README_MD.read_text(encoding="utf-8")

        self.assertRegex(skill_contents, re.compile(r"mermaid", re.IGNORECASE))
        self.assertRegex(readme_contents, re.compile(r"mermaid", re.IGNORECASE))
        self.assertRegex(skill_contents, re.compile(r"mermaid.*excalidraw|excalidraw.*mermaid", re.IGNORECASE))

    def test_skill_documents_container_fit_rules_and_layout_lint(self):
        contents = SKILL_MD.read_text(encoding="utf-8")

        self.assertRegex(contents, re.compile(r"70.?75%", re.IGNORECASE))
        self.assertRegex(contents, re.compile(r"60.?65%", re.IGNORECASE))
        self.assertRegex(contents, re.compile(r"layout lint|layout warning", re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
