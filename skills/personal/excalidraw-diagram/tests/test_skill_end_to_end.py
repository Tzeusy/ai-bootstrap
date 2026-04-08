from __future__ import annotations

import importlib.util
import shutil
import sys
import subprocess
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
RENDER_SCRIPT_PATH = SKILL_DIR / "scripts" / "render_excalidraw.py"
MERMAID_SCRIPT_PATH = SKILL_DIR / "scripts" / "excalidraw_to_mermaid.py"
FIXTURE_PATH = SKILL_DIR / "tests" / "fixtures" / "skill-workflow.excalidraw"
OUTPUT_DIR = SKILL_DIR / "tests" / "output"


def load_renderer_module():
    spec = importlib.util.spec_from_file_location("render_excalidraw", RENDER_SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load module spec from {RENDER_SCRIPT_PATH}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class SkillEndToEndTests(unittest.TestCase):
    def test_skill_workflow_fixture_exists(self):
        self.assertTrue(FIXTURE_PATH.exists(), FIXTURE_PATH)

    def test_output_directory_exists(self):
        OUTPUT_DIR.mkdir(exist_ok=True)
        self.assertTrue(OUTPUT_DIR.exists(), OUTPUT_DIR)

    def test_skill_workflow_fixture_is_copied_to_output_directory(self):
        OUTPUT_DIR.mkdir(exist_ok=True)
        copied_fixture_path = OUTPUT_DIR / FIXTURE_PATH.name

        shutil.copy2(FIXTURE_PATH, copied_fixture_path)

        self.assertTrue(copied_fixture_path.exists(), copied_fixture_path)
        self.assertEqual(
            copied_fixture_path.read_text(encoding="utf-8"),
            FIXTURE_PATH.read_text(encoding="utf-8"),
        )

    def test_skill_workflow_renders_for_default_and_midnight_themes(self):
        renderer = load_renderer_module()
        OUTPUT_DIR.mkdir(exist_ok=True)

        outputs = {}
        for theme_name in ("default", "midnight"):
            output_path = OUTPUT_DIR / f"skill-workflow-{theme_name}.svg"
            outputs[theme_name] = renderer.render(
                FIXTURE_PATH,
                output_path=output_path,
                fmt="svg",
                theme_name=theme_name,
            )

        default_svg = outputs["default"].read_text(encoding="utf-8")
        midnight_svg = outputs["midnight"].read_text(encoding="utf-8")

        self.assertIn("How excalidraw-diagram works", default_svg)
        self.assertIn("How excalidraw-diagram works", midnight_svg)
        self.assertIn("#1F1F1F", default_svg)
        self.assertIn("#111827", midnight_svg)
        self.assertNotEqual(default_svg, midnight_svg)

    def test_skill_workflow_generates_mermaid_output(self):
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_path = OUTPUT_DIR / "skill-workflow.mmd"

        subprocess.run(
            [sys.executable, str(MERMAID_SCRIPT_PATH), str(FIXTURE_PATH), "--output", str(output_path)],
            check=True,
            capture_output=True,
            text=True,
        )

        mermaid = output_path.read_text(encoding="utf-8")
        self.assertIn("flowchart TD", mermaid)
        self.assertIn("step1_box", mermaid)
        self.assertIn("1. Receive prompt<br/>and target diagram", mermaid)
        self.assertIn("5. Render locally with<br/>Playwright + bundle", mermaid)
        self.assertIn("Optional branch: convert Mermaid into or out of Excalidraw", mermaid)


if __name__ == "__main__":
    unittest.main()
