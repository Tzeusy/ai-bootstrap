from __future__ import annotations

import copy
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SKILL_DIR = Path(__file__).resolve().parents[1]
SCRIPT_PATH = SKILL_DIR / "scripts" / "render_excalidraw.py"


def load_renderer_module():
    spec = importlib.util.spec_from_file_location("render_excalidraw", SCRIPT_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Unable to load module spec from {SCRIPT_PATH}")

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class RenderScriptTests(unittest.TestCase):
    EXPECTED_THEMES = {
        "default",
        "vscode-dark",
        "vscode-light",
        "midnight",
        "monokai",
        "solarized-dark",
        "solarized-light",
        "tomorrow-night-blue",
        "abyss",
        "kimbie-dark",
        "red",
        "quiet-light",
    }

    def test_renderer_script_declares_pep723_metadata(self):
        script = SCRIPT_PATH.read_text(encoding="utf-8")
        self.assertIn("# /// script", script)
        self.assertIn('requires-python = ">=3.11"', script)
        self.assertIn('"playwright>=1.40.0"', script)

    def test_theme_catalog_has_default_theme(self):
        renderer = load_renderer_module()
        catalog = renderer.load_theme_catalog(SKILL_DIR)

        self.assertEqual(catalog.default_theme, "default")
        self.assertEqual(set(catalog.themes), self.EXPECTED_THEMES)
        self.assertEqual(catalog.themes["default"].mode, "dark")
        self.assertEqual(catalog.themes["default"].background, "#1F1F1F")

    def test_apply_theme_uses_catalog_and_document_theme(self):
        renderer = load_renderer_module()
        catalog = renderer.load_theme_catalog(SKILL_DIR)

        document = {
            "type": "excalidraw",
            "version": 2,
            "elements": [
                {
                    "id": "shape",
                    "type": "rectangle",
                    "x": 0,
                    "y": 0,
                    "width": 100,
                    "height": 40,
                    "strokeColor": "#569CD6",
                    "backgroundColor": "#264F78",
                },
                {
                    "id": "label",
                    "type": "text",
                    "x": 10,
                    "y": 10,
                    "width": 80,
                    "height": 20,
                    "strokeColor": "#9CDCFE",
                    "backgroundColor": "transparent",
                    "text": "Title",
                    "originalText": "Title",
                },
            ],
            "appState": {
                "viewBackgroundColor": "#1F1F1F",
                "excalidrawDiagramTheme": "default",
            },
            "files": {},
        }

        themed = renderer.apply_theme(copy.deepcopy(document), catalog, target_theme_name="midnight")

        self.assertEqual(themed["appState"]["excalidrawDiagramTheme"], "midnight")
        self.assertEqual(themed["appState"]["viewBackgroundColor"], "#111827")
        self.assertEqual(themed["elements"][0]["backgroundColor"], "#1f2937")
        self.assertEqual(themed["elements"][0]["strokeColor"], "#93c5fd")
        self.assertEqual(themed["elements"][1]["strokeColor"], "#93c5fd")
        self.assertEqual(themed["elements"][1]["backgroundColor"], "transparent")

    def test_apply_theme_remaps_evidence_text_colors(self):
        renderer = load_renderer_module()
        catalog = renderer.load_theme_catalog(SKILL_DIR)

        document = {
            "type": "excalidraw",
            "version": 2,
            "elements": [
                {
                    "id": "code-text",
                    "type": "text",
                    "x": 0,
                    "y": 0,
                    "width": 80,
                    "height": 20,
                    "strokeColor": "#4EC9B0",
                    "backgroundColor": "transparent",
                    "text": "payload",
                    "originalText": "payload",
                }
            ],
            "appState": {
                "viewBackgroundColor": "#1F1F1F",
                "excalidrawDiagramTheme": "default",
            },
            "files": {},
        }

        themed = renderer.apply_theme(copy.deepcopy(document), catalog, target_theme_name="midnight")
        self.assertEqual(themed["elements"][0]["strokeColor"], "#4ade80")

    def test_output_path_uses_theme_suffix(self):
        renderer = load_renderer_module()
        output_path = renderer.default_output_path(Path("/tmp/diagram.excalidraw"), fmt="svg", theme_name="midnight")

        self.assertEqual(output_path, Path("/tmp/diagram_midnight.svg"))

    def test_invalid_theme_fails_without_traceback(self):
        document = {
            "type": "excalidraw",
            "version": 2,
            "elements": [
                {
                    "id": "shape",
                    "type": "rectangle",
                    "x": 0,
                    "y": 0,
                    "width": 10,
                    "height": 10,
                    "strokeColor": "#1e3a5f",
                    "backgroundColor": "#3b82f6",
                }
            ],
            "appState": {
                "viewBackgroundColor": "#ffffff",
                "excalidrawDiagramTheme": "does-not-exist",
            },
            "files": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            diagram_path = Path(tmpdir) / "invalid-theme.excalidraw"
            diagram_path.write_text(json.dumps(document), encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(diagram_path)],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unknown theme", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_render_svg_with_vendored_bundle(self):
        renderer = load_renderer_module()
        document = {
            "type": "excalidraw",
            "version": 2,
            "source": "https://excalidraw.com",
            "elements": [
                {
                    "id": "shape",
                    "type": "rectangle",
                    "x": 0,
                    "y": 0,
                    "width": 160,
                    "height": 80,
                    "angle": 0,
                    "strokeColor": "#1e3a5f",
                    "backgroundColor": "#3b82f6",
                    "fillStyle": "solid",
                    "strokeWidth": 2,
                    "strokeStyle": "solid",
                    "roughness": 0,
                    "opacity": 100,
                    "groupIds": [],
                    "roundness": {"type": 3},
                    "seed": 1,
                    "version": 1,
                    "versionNonce": 1,
                    "isDeleted": False,
                    "boundElements": [],
                    "updated": 0,
                    "link": None,
                    "locked": False,
                }
            ],
            "appState": {
                "viewBackgroundColor": "#ffffff",
                "gridSize": 20,
                "excalidrawDiagramTheme": "default",
            },
            "files": {},
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            diagram_path = Path(tmpdir) / "renderable.excalidraw"
            output_path = Path(tmpdir) / "renderable.svg"
            diagram_path.write_text(json.dumps(document), encoding="utf-8")

            result_path = renderer.render(diagram_path, output_path=output_path, fmt="svg")

            self.assertEqual(result_path, output_path)
            svg = output_path.read_text(encoding="utf-8")

        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)


if __name__ == "__main__":
    unittest.main()
