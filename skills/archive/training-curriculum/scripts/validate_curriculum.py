#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Validate a generated curriculum/ tree against the training-curriculum contract.

Usage:
    uv run validate_curriculum.py --target /path/to/repo
    uv run validate_curriculum.py --target /path/to/repo/curriculum
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


ROOT_REQUIRED = {
    "README.md",
    "repository-thesis.md",
    "evidence-map.md",
    "research-ledger.md",
    "glossary.md",
    "mastery-rubric.md",
    "contribution-readiness.md",
    "open-questions.md",
    "paths/README.md",
}

PATH_HOURS_PATTERN = re.compile(
    r"Total estimated smart-human study time:\s*([0-9]+(?:\.[0-9]+)?)\s*hours",
    re.IGNORECASE,
)
MODULE_HOURS_PATTERN = re.compile(
    r"Estimated smart-human study time:\s*([0-9]+(?:\.[0-9]+)?)\s*hours",
    re.IGNORECASE,
)

PATH_README_MARKERS = [
    "## Section Overview",
    "## Stop Here If",
]

MODULE_MARKERS = [
    "## Why This Module Matters",
    "## Learning Goals",
    "### Why This Matters Here",
    "### Technical Deep Dive",
    "### Where It Appears In The Repo",
    "### Sample Q&A",
    "### Progress",
    "### Mastery Check",
    "## Module Mastery Gate",
]

RESEARCH_LEDGER_MARKERS = [
    "## Pass 1",
    "## Pass 2",
    "## Pass 3",
    "## Reconciliation",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate a curriculum/ directory against the training-curriculum contract.",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Path to the repo root or the curriculum/ directory itself.",
    )
    return parser.parse_args()


def resolve_curriculum_dir(target: Path) -> Path:
    if target.name == "curriculum" and target.is_dir():
        return target
    candidate = target / "curriculum"
    if candidate.is_dir():
        return candidate
    raise SystemExit(f"[ERROR] Could not find curriculum/ under: {target}")


def read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception as exc:  # pragma: no cover - defensive boundary
        errors.append(f"Failed to read {path}: {exc}")
        return ""


def require_files(curriculum_dir: Path, errors: list[str]) -> None:
    for relative_path in sorted(ROOT_REQUIRED):
        if not (curriculum_dir / relative_path).exists():
            errors.append(f"Missing required file: {relative_path}")


def parse_hours(pattern: re.Pattern[str], text: str) -> float | None:
    match = pattern.search(text)
    if not match:
        return None
    return float(match.group(1))


def validate_research_ledger(curriculum_dir: Path, errors: list[str]) -> None:
    ledger = curriculum_dir / "research-ledger.md"
    if not ledger.exists():
        errors.append("Missing required file: research-ledger.md")
        return
    text = read_text(ledger, errors)
    for marker in RESEARCH_LEDGER_MARKERS:
        if marker not in text:
            errors.append(f"{ledger} is missing required marker: {marker}")


def validate_path_dir(path_dir: Path, errors: list[str]) -> None:
    readme = path_dir / "README.md"
    if not readme.exists():
        errors.append(f"Missing path README: {readme}")
        return

    readme_text = read_text(readme, errors)
    for marker in PATH_README_MARKERS:
        if marker not in readme_text:
            errors.append(f"{readme} is missing required marker: {marker}")
    if "[ ]" not in readme_text and "[X]" not in readme_text:
        errors.append(f"{readme} is missing progress checkboxes.")

    hours = parse_hours(PATH_HOURS_PATTERN, readme_text)
    if hours is None:
        errors.append(f"{readme} is missing total estimated hours.")
    elif hours > 100:
        errors.append(f"{readme} exceeds 100-hour path cap: {hours}")

    modules_dir = path_dir / "modules"
    if not modules_dir.is_dir():
        errors.append(f"Missing modules directory: {modules_dir}")
        return

    module_files = sorted(modules_dir.glob("*.md"))
    if not module_files:
        errors.append(f"No module files found in {modules_dir}")
        return

    for module_file in module_files:
        validate_module(module_file, errors)


def validate_module(module_file: Path, errors: list[str]) -> None:
    text = read_text(module_file, errors)
    for marker in MODULE_MARKERS:
        if marker not in text:
            errors.append(f"{module_file} is missing required marker: {marker}")
    if "[ ]" not in text and "[X]" not in text:
        errors.append(f"{module_file} is missing progress checkboxes.")

    hours = parse_hours(MODULE_HOURS_PATTERN, text)
    if hours is None:
        errors.append(f"{module_file} is missing estimated hours.")
    elif hours > 10:
        errors.append(f"{module_file} exceeds 10-hour module cap: {hours}")


def validate_curriculum(curriculum_dir: Path) -> list[str]:
    errors: list[str] = []
    require_files(curriculum_dir, errors)
    validate_research_ledger(curriculum_dir, errors)

    paths_dir = curriculum_dir / "paths"
    if not paths_dir.is_dir():
        errors.append(f"Missing paths directory: {paths_dir}")
        return errors

    path_dirs = sorted(
        entry for entry in paths_dir.iterdir() if entry.is_dir()
    )
    if not path_dirs:
        errors.append(
            f"No curriculum path directories found under {paths_dir}. "
            "Create at least one real path before validation."
        )
        return errors

    for path_dir in path_dirs:
        validate_path_dir(path_dir, errors)

    return errors


def main() -> int:
    args = parse_args()
    target = Path(args.target).expanduser().resolve()
    curriculum_dir = resolve_curriculum_dir(target)
    errors = validate_curriculum(curriculum_dir)
    if errors:
        print("[ERROR] Curriculum validation failed:")
        for error in errors:
            print(f" - {error}")
        return 1

    print("[OK] Curriculum validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
