# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import re
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_PATH = SKILL_ROOT / "SKILL.md"
README_PATH = SKILL_ROOT / "README.md"
MERMAID_REF = SKILL_ROOT / "references" / "mermaid-interoperability.md"
TEMPLATE_PATH = SKILL_ROOT / "references" / "render_template.html"
VENDOR_BUNDLE = SKILL_ROOT / "references" / "vendor" / "excalidraw.bundle.mjs"
MERMAID_SCRIPT = SKILL_ROOT / "scripts" / "excalidraw_to_mermaid.py"


def find_repo_refresh_script() -> Path:
    for parent in Path(__file__).resolve().parents:
        candidate = parent / "scripts" / "refresh.sh"
        if candidate.exists():
            return candidate

    raise AssertionError("Unable to locate scripts/refresh.sh from test path")


REPO_REFRESH = find_repo_refresh_script()


class SkillPackageTests(unittest.TestCase):
    def test_all_skill_python_entrypoints_use_pep723_metadata(self) -> None:
        python_files = sorted((SKILL_ROOT / "scripts").glob("*.py")) + sorted((SKILL_ROOT / "tests").glob("*.py"))
        self.assertTrue(python_files)

        for path in python_files:
            contents = path.read_text(encoding="utf-8")
            self.assertIn("# /// script", contents, path)
            self.assertIn('requires-python = ">=3.11"', contents, path)

    def test_skill_frontmatter_declares_compatibility(self) -> None:
        text = SKILL_PATH.read_text(encoding="utf-8")
        frontmatter = text.split("---", 2)[1]
        self.assertIn("compatibility:", frontmatter)

    def test_docs_use_skill_relative_renderer_paths(self) -> None:
        skill_text = SKILL_PATH.read_text(encoding="utf-8")
        readme_text = README_PATH.read_text(encoding="utf-8")

        self.assertIn("uv run scripts/render_excalidraw.py", skill_text)
        self.assertIn("uv run scripts/render_excalidraw.py", readme_text)
        self.assertNotIn(".claude/skills/excalidraw-diagram", skill_text)
        self.assertNotIn(".claude/skills/excalidraw-diagram", readme_text)

    def test_skill_references_theme_catalog_instead_of_color_palette(self) -> None:
        skill_text = SKILL_PATH.read_text(encoding="utf-8")
        readme_text = README_PATH.read_text(encoding="utf-8")

        self.assertNotIn("color-palette.md", skill_text)
        self.assertNotIn("color-palette.md", readme_text)
        self.assertRegex(skill_text, re.compile(r"theme", re.IGNORECASE))

    def test_mermaid_reference_exists(self) -> None:
        self.assertTrue(MERMAID_REF.exists(), MERMAID_REF)

    def test_mermaid_export_script_exists(self) -> None:
        self.assertTrue(MERMAID_SCRIPT.exists(), MERMAID_SCRIPT)
        contents = MERMAID_SCRIPT.read_text(encoding="utf-8")
        self.assertIn("# /// script", contents)
        self.assertIn('requires-python = ">=3.11"', contents)

    def test_template_uses_local_vendor_bundle(self) -> None:
        template_text = TEMPLATE_PATH.read_text(encoding="utf-8")
        self.assertNotIn("esm.sh", template_text)
        self.assertIn("./vendor/excalidraw.bundle.mjs", template_text)
        self.assertTrue(VENDOR_BUNDLE.exists(), VENDOR_BUNDLE)

    def test_repo_refresh_script_exists_and_mentions_excalidraw(self) -> None:
        self.assertTrue(REPO_REFRESH.exists(), REPO_REFRESH)
        refresh_text = REPO_REFRESH.read_text(encoding="utf-8")
        self.assertIn("excalidraw", refresh_text)
        self.assertRegex(refresh_text, re.compile(r"npm|npx", re.IGNORECASE))

    def test_skill_has_no_machine_specific_home_paths(self) -> None:
        forbidden = "/home/" + "tze"
        for path in SKILL_ROOT.rglob("*"):
            if not path.is_file():
                continue
            if "__pycache__" in path.parts or ".venv" in path.parts:
                continue

            contents = path.read_text(encoding="utf-8")
            self.assertNotIn(forbidden, contents, path)


if __name__ == "__main__":
    unittest.main()
