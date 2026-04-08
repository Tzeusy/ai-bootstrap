# /// script
# requires-python = ">=3.11"
# dependencies = [
#   "playwright>=1.40.0",
# ]
# ///
"""Render Excalidraw JSON to PNG or SVG using Playwright + headless Chromium.

Usage:
    uv run scripts/render_excalidraw.py --install-browser
    uv run scripts/render_excalidraw.py path/to/diagram.excalidraw
    uv run scripts/render_excalidraw.py path/to/diagram.excalidraw --format svg
    uv run scripts/render_excalidraw.py path/to/diagram.excalidraw --theme midnight
"""

from __future__ import annotations

import argparse
import contextlib
import json
import subprocess
import sys
import threading
from dataclasses import dataclass
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path


MAX_BOUND_TEXT_WIDTH_RATIO = 0.75
MAX_BOUND_TEXT_HEIGHT_RATIO = 0.65
MIN_BOUND_TEXT_HORIZONTAL_PADDING = 24
MIN_BOUND_TEXT_VERTICAL_PADDING = 14


@dataclass(frozen=True)
class Theme:
    name: str
    mode: str
    background: str
    fills: dict[str, str]
    strokes: dict[str, str]
    text: dict[str, str]
    evidence: dict[str, str]
    preserve: tuple[str, ...]

    @classmethod
    def from_dict(cls, data: dict) -> "Theme":
        return cls(
            name=data["name"],
            mode=data["mode"],
            background=data["background"],
            fills=data.get("fills", {}),
            strokes=data.get("strokes", {}),
            text=data.get("text", {}),
            evidence=data.get("evidence", {}),
            preserve=tuple(data.get("preserve", [])),
        )


@dataclass(frozen=True)
class ThemeCatalog:
    default_theme: str
    themes: dict[str, Theme]

    def get_theme(self, name: str | None = None) -> Theme:
        theme_name = name or self.default_theme
        try:
            return self.themes[theme_name]
        except KeyError as exc:
            known = ", ".join(sorted(self.themes))
            raise ValueError(f"Unknown theme '{theme_name}'. Known themes: {known}") from exc


def skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_theme_catalog(skill_dir: Path | None = None) -> ThemeCatalog:
    root = skill_dir or skill_root()
    theme_dir = root / "references" / "themes"
    catalog_path = theme_dir / "catalog.json"
    raw_catalog = json.loads(catalog_path.read_text(encoding="utf-8"))

    themes: dict[str, Theme] = {}
    for theme_name, filename in raw_catalog["themes"].items():
        theme_path = theme_dir / filename
        theme_data = json.loads(theme_path.read_text(encoding="utf-8"))
        themes[theme_name] = Theme.from_dict(theme_data)

    return ThemeCatalog(default_theme=raw_catalog["default_theme"], themes=themes)


def document_theme_name(data: dict, catalog: ThemeCatalog) -> str:
    app_state = data.get("appState", {})
    return app_state.get("excalidrawDiagramTheme", catalog.default_theme)


def theme_color_groups(theme: Theme, property_name: str, element_type: str) -> tuple[dict[str, str], ...]:
    if property_name == "backgroundColor":
        return (theme.fills, theme.evidence)

    if property_name == "strokeColor" and element_type == "text":
        return (theme.text, theme.evidence, theme.strokes)

    return (theme.strokes,)


def find_color_slot(theme: Theme, property_name: str, element_type: str, color: str) -> tuple[str, str] | None:
    for group_name, group in (
        ("fills", theme.fills),
        ("evidence", theme.evidence),
        ("text", theme.text),
        ("strokes", theme.strokes),
    ):
        if group not in theme_color_groups(theme, property_name, element_type):
            continue
        for slot_name, slot_color in group.items():
            if slot_color.lower() == color.lower():
                return (group_name, slot_name)

    return None


def resolve_target_color(theme: Theme, group_name: str, slot_name: str) -> str | None:
    group = getattr(theme, group_name, None)
    if not isinstance(group, dict):
        return None
    return group.get(slot_name)


def apply_theme(data: dict, catalog: ThemeCatalog, target_theme_name: str, source_theme_name: str | None = None) -> dict:
    source_theme = catalog.get_theme(source_theme_name or document_theme_name(data, catalog))
    target_theme = catalog.get_theme(target_theme_name)

    app_state = data.setdefault("appState", {})
    app_state["viewBackgroundColor"] = target_theme.background
    app_state["exportWithDarkMode"] = False
    app_state["excalidrawDiagramTheme"] = target_theme.name
    app_state["excalidrawDiagramMode"] = target_theme.mode

    preserve = {"transparent", *source_theme.preserve, *target_theme.preserve}

    for element in data.get("elements", []):
        element_type = element.get("type", "")
        for property_name in ("strokeColor", "backgroundColor"):
            color = element.get(property_name)
            if not isinstance(color, str) or color.lower() in preserve:
                continue

            slot = find_color_slot(source_theme, property_name, element_type, color)
            if slot is None:
                continue

            group_name, slot_name = slot
            target_color = resolve_target_color(target_theme, group_name, slot_name)
            if target_color:
                element[property_name] = target_color

    return data


def validate_excalidraw(data: dict) -> list[str]:
    errors: list[str] = []

    if data.get("type") != "excalidraw":
        errors.append(f"Expected type 'excalidraw', got '{data.get('type')}'")

    if "elements" not in data:
        errors.append("Missing 'elements' array")
    elif not isinstance(data["elements"], list):
        errors.append("'elements' must be an array")
    elif len(data["elements"]) == 0:
        errors.append("'elements' array is empty — nothing to render")

    return errors


def summarize_text_label(text: str, limit: int = 64) -> str:
    normalized = text.replace("\n", " / ").strip()
    if len(normalized) <= limit:
        return normalized
    return normalized[: limit - 3] + "..."


def lint_layout_warnings(data: dict) -> list[str]:
    warnings: list[str] = []
    elements = data.get("elements", [])
    elements_by_id = {
        element["id"]: element
        for element in elements
        if isinstance(element, dict) and isinstance(element.get("id"), str) and not element.get("isDeleted")
    }

    for element in elements:
        if element.get("isDeleted") or element.get("type") != "text":
            continue

        container_id = element.get("containerId")
        if not isinstance(container_id, str):
            continue

        container = elements_by_id.get(container_id)
        if container is None:
            continue

        container_width = abs(float(container.get("width", 0) or 0))
        container_height = abs(float(container.get("height", 0) or 0))
        text_width = abs(float(element.get("width", 0) or 0))
        text_height = abs(float(element.get("height", 0) or 0))
        if container_width <= 0 or container_height <= 0 or text_width <= 0 or text_height <= 0:
            continue

        container_x = float(container.get("x", 0) or 0)
        container_y = float(container.get("y", 0) or 0)
        text_x = float(element.get("x", 0) or 0)
        text_y = float(element.get("y", 0) or 0)

        left_padding = text_x - container_x
        right_padding = (container_x + container_width) - (text_x + text_width)
        top_padding = text_y - container_y
        bottom_padding = (container_y + container_height) - (text_y + text_height)

        label = summarize_text_label(element.get("text") or element.get("originalText") or element["id"])
        width_ratio = text_width / container_width
        height_ratio = text_height / container_height

        if width_ratio > MAX_BOUND_TEXT_WIDTH_RATIO:
            warnings.append(
                f"Bound text '{label}' uses {width_ratio:.0%} of container '{container_id}' width; target <= 75%."
            )

        if height_ratio > MAX_BOUND_TEXT_HEIGHT_RATIO:
            warnings.append(
                f"Bound text '{label}' uses {height_ratio:.0%} of container '{container_id}' height; target <= 65%."
            )

        if min(left_padding, right_padding) < MIN_BOUND_TEXT_HORIZONTAL_PADDING:
            warnings.append(
                f"Bound text '{label}' in container '{container_id}' has horizontal padding below 24px."
            )

        if min(top_padding, bottom_padding) < MIN_BOUND_TEXT_VERTICAL_PADDING:
            warnings.append(
                f"Bound text '{label}' in container '{container_id}' has vertical padding below 14px."
            )

    return warnings


def compute_bounding_box(elements: list[dict]) -> tuple[float, float, float, float]:
    min_x = float("inf")
    min_y = float("inf")
    max_x = float("-inf")
    max_y = float("-inf")

    for element in elements:
        if element.get("isDeleted"):
            continue

        x = element.get("x", 0)
        y = element.get("y", 0)
        width = element.get("width", 0)
        height = element.get("height", 0)

        if element.get("type") in ("arrow", "line") and "points" in element:
            for point_x, point_y in element["points"]:
                min_x = min(min_x, x + point_x)
                min_y = min(min_y, y + point_y)
                max_x = max(max_x, x + point_x)
                max_y = max(max_y, y + point_y)
        else:
            min_x = min(min_x, x)
            min_y = min(min_y, y)
            max_x = max(max_x, x + abs(width))
            max_y = max(max_y, y + abs(height))

    if min_x == float("inf"):
        return (0, 0, 800, 600)

    return (min_x, min_y, max_x, max_y)


def default_output_path(excalidraw_path: Path, fmt: str, theme_name: str, default_theme_name: str = "default") -> Path:
    if theme_name == default_theme_name:
        return excalidraw_path.with_suffix(f".{fmt}")

    return excalidraw_path.with_suffix("").with_name(f"{excalidraw_path.stem}_{theme_name}.{fmt}")


def install_browser() -> None:
    subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"], check=True)


@contextlib.contextmanager
def serve_references_dir(references_dir: Path):
    class Handler(SimpleHTTPRequestHandler):
        extensions_map = {
            **SimpleHTTPRequestHandler.extensions_map,
            ".js": "text/javascript",
            ".mjs": "text/javascript",
        }

        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(references_dir), **kwargs)

        def log_message(self, format: str, *args) -> None:
            return

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        host, port = server.server_address
        yield f"http://{host}:{port}"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def render(
    excalidraw_path: Path,
    output_path: Path | None = None,
    scale: int = 2,
    max_width: int = 1920,
    fmt: str = "png",
    theme_name: str | None = None,
) -> Path:
    raw = excalidraw_path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON in {excalidraw_path}: {exc}", file=sys.stderr)
        sys.exit(1)

    errors = validate_excalidraw(data)
    if errors:
        print("ERROR: Invalid Excalidraw file:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)

    layout_warnings = lint_layout_warnings(data)
    if layout_warnings:
        print("WARNING: Layout risks detected:", file=sys.stderr)
        for warning in layout_warnings:
            print(f"  - {warning}", file=sys.stderr)

    try:
        catalog = load_theme_catalog()
        target_theme_name = theme_name or document_theme_name(data, catalog)
        data = apply_theme(data, catalog, target_theme_name)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("ERROR: playwright not installed.", file=sys.stderr)
        print("Run: uv run scripts/render_excalidraw.py --install-browser", file=sys.stderr)
        sys.exit(1)

    elements = [element for element in data["elements"] if not element.get("isDeleted")]
    min_x, min_y, max_x, max_y = compute_bounding_box(elements)
    padding = 80
    diagram_width = max_x - min_x + padding * 2
    diagram_height = max_y - min_y + padding * 2

    viewport_width = min(int(diagram_width), max_width)
    viewport_height = max(int(diagram_height), 600)

    if output_path is None:
        output_path = default_output_path(excalidraw_path, fmt, target_theme_name, catalog.default_theme)

    references_dir = skill_root() / "references"
    template_path = references_dir / "render_template.html"
    if not template_path.exists():
        print(f"ERROR: Template not found at {template_path}", file=sys.stderr)
        sys.exit(1)

    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(headless=True)
        except Exception as exc:
            if "Executable doesn't exist" in str(exc) or "browserType.launch" in str(exc):
                print("ERROR: Chromium not installed for Playwright.", file=sys.stderr)
                print("Run: uv run scripts/render_excalidraw.py --install-browser", file=sys.stderr)
                sys.exit(1)
            raise

        with serve_references_dir(references_dir) as base_url:
            page = browser.new_page(
                viewport={"width": viewport_width, "height": viewport_height},
                device_scale_factor=scale,
            )
            console_errors: list[str] = []
            page_errors: list[str] = []
            page.on(
                "console",
                lambda message: console_errors.append(message.text) if message.type == "error" else None,
            )
            page.on("pageerror", lambda error: page_errors.append(str(error)))

            page.goto(f"{base_url}/render_template.html")
            try:
                page.wait_for_function("window.__moduleReady === true", timeout=30000)
            except Exception:
                details = page_errors + console_errors
                detail_text = " | ".join(details[-5:]) if details else "module did not finish loading"
                print(f"ERROR: Renderer page failed to initialize: {detail_text}", file=sys.stderr)
                browser.close()
                sys.exit(1)

            result = page.evaluate(f"window.renderDiagram({json.dumps(data)})")
            if not result or not result.get("success"):
                error_message = result.get("error", "Unknown render error") if result else "renderDiagram returned null"
                print(f"ERROR: Render failed: {error_message}", file=sys.stderr)
                browser.close()
                sys.exit(1)

            page.wait_for_function("window.__renderComplete === true", timeout=15000)
            svg_element = page.query_selector("#root svg")
            if svg_element is None:
                print("ERROR: No SVG element found after render.", file=sys.stderr)
                browser.close()
                sys.exit(1)

            if fmt == "svg":
                output_path.write_text(svg_element.evaluate("el => el.outerHTML"), encoding="utf-8")
            else:
                svg_element.screenshot(path=str(output_path))

        browser.close()

    return output_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Render Excalidraw JSON to PNG or SVG")
    parser.add_argument("input", nargs="?", type=Path, help="Path to .excalidraw JSON file")
    parser.add_argument("--output", "-o", type=Path, default=None, help="Output path (default: derived from input and theme)")
    parser.add_argument("--format", "-f", choices=["png", "svg"], default="png", help="Output format (default: png)")
    parser.add_argument("--scale", "-s", type=int, default=2, help="Device scale factor for PNG output")
    parser.add_argument("--width", "-w", type=int, default=1920, help="Max viewport width")
    parser.add_argument("--theme", "-t", default=None, help="Theme name from references/themes/catalog.json")
    parser.add_argument("--install-browser", action="store_true", help="Install Playwright Chromium for this script environment")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.install_browser:
        install_browser()
        if args.input is None:
            return

    if args.input is None:
        parser.error("input is required unless --install-browser is used by itself")

    if not args.input.exists():
        print(f"ERROR: File not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    output_path = render(
        excalidraw_path=args.input,
        output_path=args.output,
        scale=args.scale,
        max_width=args.width,
        fmt=args.format,
        theme_name=args.theme,
    )
    print(str(output_path))


if __name__ == "__main__":
    main()
