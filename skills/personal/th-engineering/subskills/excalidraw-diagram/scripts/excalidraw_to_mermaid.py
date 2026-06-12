# /// script
# requires-python = ">=3.11"
# ///
"""Convert Excalidraw JSON into Mermaid flowchart syntax.

Usage:
    uv run scripts/excalidraw_to_mermaid.py path/to/diagram.excalidraw
    uv run scripts/excalidraw_to_mermaid.py path/to/diagram.excalidraw --output path/to/diagram.mmd
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


NODE_TYPES = {"rectangle", "diamond", "ellipse"}


@dataclass(frozen=True)
class MermaidNode:
    element_id: str
    mermaid_id: str
    label: str
    element_type: str
    x: float
    y: float


def sanitize_identifier(raw: str) -> str:
    identifier = re.sub(r"[^0-9A-Za-z_]", "_", raw)
    identifier = re.sub(r"_+", "_", identifier).strip("_") or "node"
    if identifier[0].isdigit():
        identifier = f"node_{identifier}"
    return identifier


def normalize_text(value: str) -> str:
    return " ".join(value.split())


def mermaid_label(value: str) -> str:
    return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "<br/>")


def load_excalidraw(path: Path) -> dict:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"ERROR: Invalid JSON in {path}: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    if data.get("type") != "excalidraw":
        print(f"ERROR: Expected type 'excalidraw', got '{data.get('type')}'", file=sys.stderr)
        raise SystemExit(1)

    return data


def absolute_point(element: dict, index: int) -> tuple[float, float]:
    point_x, point_y = element.get("points", [[0, 0]])[index]
    return (element.get("x", 0) + point_x, element.get("y", 0) + point_y)


def distance_squared(a: tuple[float, float], b: tuple[float, float]) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def node_center(element: dict) -> tuple[float, float]:
    return (
        element.get("x", 0) + abs(element.get("width", 0)) / 2,
        element.get("y", 0) + abs(element.get("height", 0)) / 2,
    )


def collect_nodes(elements: list[dict]) -> tuple[list[MermaidNode], list[str], list[MermaidNode]]:
    bound_text: dict[str, str] = {}
    standalone_text: list[dict] = []

    for element in elements:
        if element.get("isDeleted") or element.get("type") != "text":
            continue

        text = element.get("text") or element.get("originalText")
        if not isinstance(text, str) or not text.strip():
            continue

        container_id = element.get("containerId")
        if container_id:
            bound_text[container_id] = text.strip()
        else:
            standalone_text.append(element)

    nodes: list[MermaidNode] = []
    notes: list[MermaidNode] = []
    node_floor = min(
        (
            element.get("y", 0)
            for element in elements
            if not element.get("isDeleted") and element.get("type") in NODE_TYPES
        ),
        default=0,
    )

    for element in elements:
        if element.get("isDeleted") or element.get("type") not in NODE_TYPES:
            continue

        label = bound_text.get(element["id"])
        if not label:
            continue

        nodes.append(
            MermaidNode(
                element_id=element["id"],
                mermaid_id=sanitize_identifier(element["id"]),
                label=label,
                element_type=element["type"],
                x=element.get("x", 0),
                y=element.get("y", 0),
            )
        )

    heading_comments: list[str] = []
    for index, element in enumerate(sorted(standalone_text, key=lambda item: (item.get("y", 0), item.get("x", 0)))):
        label = element["text"].strip()
        if element.get("y", 0) < node_floor:
            heading_comments.append(normalize_text(label))
            continue

        notes.append(
            MermaidNode(
                element_id=element["id"],
                mermaid_id=sanitize_identifier(f"note_{index}_{element['id']}"),
                label=label,
                element_type="note",
                x=element.get("x", 0),
                y=element.get("y", 0),
            )
        )

    nodes.sort(key=lambda node: (node.y, node.x, node.mermaid_id))
    notes.sort(key=lambda node: (node.y, node.x, node.mermaid_id))
    return nodes, heading_comments, notes


def node_syntax(node: MermaidNode) -> str:
    label = mermaid_label(node.label)
    if node.element_type == "diamond":
        return f'{{"{label}"}}'
    if node.element_type == "ellipse":
        return f'(["{label}"])'
    return f'["{label}"]'


def find_endpoint_node(arrow: dict, node_lookup: dict[str, MermaidNode], positions: dict[str, tuple[float, float]], *, key: str, point_index: int) -> MermaidNode | None:
    binding = arrow.get(key)
    if isinstance(binding, dict):
        element_id = binding.get("elementId")
        if isinstance(element_id, str):
            return node_lookup.get(element_id)

    point = absolute_point(arrow, point_index)
    nearest_id = min(positions, key=lambda element_id: distance_squared(point, positions[element_id]), default=None)
    if nearest_id is None:
        return None
    return node_lookup[nearest_id]


def collect_edges(elements: list[dict], nodes: list[MermaidNode]) -> list[tuple[str, str]]:
    node_lookup = {node.element_id: node for node in nodes}
    positions = {
        element["id"]: node_center(element)
        for element in elements
        if not element.get("isDeleted") and element.get("type") in NODE_TYPES and element["id"] in node_lookup
    }

    edges: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for element in elements:
        if element.get("isDeleted") or element.get("type") not in {"arrow", "line"}:
            continue

        source = find_endpoint_node(element, node_lookup, positions, key="startBinding", point_index=0)
        target = find_endpoint_node(element, node_lookup, positions, key="endBinding", point_index=-1)
        if source is None or target is None or source.element_id == target.element_id:
            continue

        edge = (source.mermaid_id, target.mermaid_id)
        if edge in seen:
            continue
        seen.add(edge)
        edges.append(edge)

    return edges


def convert_to_mermaid(data: dict) -> str:
    elements = data.get("elements", [])
    nodes, heading_comments, notes = collect_nodes(elements)
    edges = collect_edges(elements, nodes)

    if not nodes:
        raise ValueError("Scene does not contain any labeled flowchart nodes")

    lines: list[str] = []
    for comment in heading_comments:
        lines.append(f"%% {comment}")
    lines.append("flowchart TD")

    for node in nodes:
        lines.append(f"    {node.mermaid_id}{node_syntax(node)}")

    for source, target in edges:
        lines.append(f"    {source} --> {target}")

    for note in notes:
        lines.append(f'    {note.mermaid_id}["{mermaid_label(note.label)}"]')

    return "\n".join(lines) + "\n"


def default_output_path(excalidraw_path: Path) -> Path:
    return excalidraw_path.with_suffix(".mmd")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Convert Excalidraw JSON into Mermaid flowchart syntax.")
    parser.add_argument("input", type=Path, help="Path to the source .excalidraw file")
    parser.add_argument("--output", type=Path, help="Path to the output Mermaid file (.mmd)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    data = load_excalidraw(args.input)

    try:
        mermaid = convert_to_mermaid(data)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc

    output_path = args.output or default_output_path(args.input)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(mermaid, encoding="utf-8")
    print(output_path)


if __name__ == "__main__":
    main()
