#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# ///
"""Create the baseline curriculum/ tree inside a target repository.

Usage:
    uv run scaffold_curriculum.py --target /path/to/repo
    uv run scaffold_curriculum.py --target /path/to/repo --path-slug foundations
    uv run scaffold_curriculum.py --target /path/to/repo --path-slug foundations --module-slug architecture-prereqs
    uv run scaffold_curriculum.py --target /path/to/repo --force
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


BASE_FILES = {
    "README.md": (
        "# Curriculum\n\n"
        "Use this directory as the hub for one or more prerequisite curricula for this repository.\n"
        "Teach fundamental technical concepts first; use repo context only to explain why those concepts matter here.\n\n"
        "## Overview\n\n"
        "| Path or Section | Why You Need It | Estimated Hours | Progress |\n"
        "|---|---|---:|---|\n"
        "| Replace with real paths | Explain which technical concepts this path teaches and why they matter here. | 0 | [ ] |\n"
    ),
    "repository-thesis.md": (
        "# Repository Thesis\n\n"
        "Explain what this repository does, why the curriculum exists, and which technical concept "
        "domains block comprehension without preparation.\n"
    ),
    "evidence-map.md": (
        "# Evidence Map\n\n"
        "| Topic | Class | Depth | Confidence | Why It Matters Here | Repo Evidence | When Needed |\n"
        "|---|---|---|---|---|---|---|\n"
    ),
    "research-ledger.md": (
        "# Research Ledger\n\n"
        "Document the hard-minimum 3 independent deep-dive passes used to discover prerequisite concepts.\n\n"
        "## Pass 1\n\n"
        "- Angle:\n"
        "- Major concept clusters surfaced:\n"
        "- Evidence notes:\n\n"
        "## Pass 2\n\n"
        "- Angle:\n"
        "- Major concept clusters surfaced:\n"
        "- Evidence notes:\n\n"
        "## Pass 3\n\n"
        "- Angle:\n"
        "- Major concept clusters surfaced:\n"
        "- Evidence notes:\n\n"
        "## Reconciliation\n\n"
        "- Concepts that appeared across multiple passes:\n"
        "- Concepts that surfaced late and changed the curriculum:\n"
        "- Additional passes run beyond the minimum:\n"
    ),
    "glossary.md": "# Glossary\n\nDefine the essential vocabulary and acronyms.\n",
    "mastery-rubric.md": (
        "# Mastery Rubric\n\n"
        "Use this file to define what completion means across this curriculum.\n\n"
        "## Levels\n\n"
        "- `exposed`: I recognize the terms and basic purpose.\n"
        "- `working`: I can explain the concept and connect it to the repository.\n"
        "- `contribution-ready`: I can reason about trade-offs, failure modes, or safe changes here.\n"
    ),
    "open-questions.md": (
        "# Open Questions\n\n"
        "Capture weakly inferred prerequisites, missing evidence, and questions for maintainers instead of pretending certainty.\n"
    ),
    "contribution-readiness.md": (
        "# Contribution Readiness\n\n"
        "Describe what the learner should be able to understand or change after completing the curriculum.\n"
    ),
    "paths/README.md": (
        "# Curriculum Paths\n\n"
        "Document whether this repository needs one curriculum path or multiple separate curricula.\n\n"
        "## Path Planning\n\n"
        "| Path | Goal | Estimated Hours | Progress |\n"
        "|---|---|---:|---|\n"
        "| Replace with real paths | Explain the goal and why the split exists. | 0 | [ ] |\n"
    ),
}

SLUG_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def slug_to_title(slug: str) -> str:
    return " ".join(word.capitalize() for word in slug.split("-"))


def validate_slug(value: str, arg_name: str) -> str:
    if not SLUG_PATTERN.match(value):
        raise SystemExit(
            f"[ERROR] {arg_name} must be lowercase hyphen-case (letters, digits, hyphens): {value}"
        )
    return value


def build_path_readme(path_title: str) -> str:
    return (
        f"# {path_title}\n\n"
        "- Total estimated smart-human study time: 0 hours\n"
        "- Keep this path at or below 100 hours.\n\n"
        "## Section Overview\n\n"
        "| Module | Why You Need It | Estimated Hours | Depends On | Progress |\n"
        "|---|---|---:|---|---|\n"
        "| Replace with real modules | Explain the real module purpose. | 0 | None | [ ] |\n\n"
        "## Stop Here If\n\n"
        "State which learners can stop before the deeper modules in this path.\n"
    )


def build_module_template(module_title: str) -> str:
    return (
        f"# {module_title}\n\n"
        "- Estimated smart-human study time: 0 hours\n"
        "- Keep every module at or below 10 hours.\n\n"
        "## Why This Module Matters\n\n"
        "Explain why the learner must know this before the repository makes sense.\n\n"
        "## Learning Goals\n\n"
        "- Goal 1\n"
        "- Goal 2\n\n"
        "## Subsection: Replace Me\n\n"
        "### Why This Matters Here\n\n"
        "Connect this concept directly to the repository without turning the subsection into a repo tour.\n\n"
        "### Technical Deep Dive\n\n"
        "Teach the underlying technical concept in enough depth that it would still be meaningful outside this repository.\n\n"
        "### Where It Appears In The Repo\n\n"
        "- path/to/file\n"
        "- Keep this section concise and justify relevance rather than teaching scaffolding\n\n"
        "### Sample Q&A\n\n"
        "- Q: Replace with a challenge question.\n"
        "  A: Replace with the expected answer.\n\n"
        "### Progress\n\n"
        "- [ ] Exposed: I can define the key terms in this subsection\n"
        "- [ ] Working: I can explain the core idea in my own words\n"
        "- [ ] Working: I can answer the sample Q&A without looking\n\n"
        "### Mastery Check\n\n"
        "Target level: `working`\n\n"
        "You should be able to explain why this concept exists in the repository and answer the sample Q&A without notes.\n\n"
        "## Module Mastery Gate\n\n"
        "- [ ] I can summarize the core concepts in this module\n"
        "- [ ] I can answer the hardest subsection Q&A without notes\n"
        "- [ ] I can point to where these ideas appear in the repository\n"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Scaffold a curriculum/ directory for repo-specific prerequisite education.",
    )
    parser.add_argument(
        "--target",
        required=True,
        help="Path to the target repository root.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow writing missing baseline files even if curriculum/ already exists.",
    )
    parser.add_argument(
        "--path-slug",
        help="Optional real path slug to create under curriculum/paths/.",
    )
    parser.add_argument(
        "--path-title",
        help="Optional human-readable title for --path-slug. Defaults to title-cased slug.",
    )
    parser.add_argument(
        "--module-slug",
        help="Optional first module slug to create under the given path.",
    )
    parser.add_argument(
        "--module-title",
        help="Optional human-readable title for --module-slug. Defaults to title-cased slug.",
    )
    return parser.parse_args()


def ensure_target_repo(target_root: Path) -> None:
    if not target_root.exists():
        raise SystemExit(f"[ERROR] Target path does not exist: {target_root}")
    if not target_root.is_dir():
        raise SystemExit(f"[ERROR] Target path is not a directory: {target_root}")


def ensure_safe_destination(curriculum_dir: Path, force: bool) -> None:
    if not curriculum_dir.exists():
        return
    if not force:
        raise SystemExit(
            "[ERROR] curriculum/ already exists. Re-run with --force to add only missing baseline files."
        )


def write_file(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        return
    path.write_text(content, encoding="utf-8")


def scaffold(target_root: Path, force: bool) -> list[Path]:
    curriculum_dir = target_root / "curriculum"
    ensure_safe_destination(curriculum_dir, force)
    curriculum_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for relative_path, content in BASE_FILES.items():
        output_path = curriculum_dir / relative_path
        if output_path.exists():
            continue
        write_file(output_path, content)
        created.append(output_path)
    return created


def build_extra_files(
    path_slug: str | None,
    path_title: str | None,
    module_slug: str | None,
    module_title: str | None,
) -> dict[str, str]:
    extras: dict[str, str] = {}
    if path_slug is None:
        if module_slug is not None:
            raise SystemExit("[ERROR] --module-slug requires --path-slug.")
        return extras

    safe_path_slug = validate_slug(path_slug, "--path-slug")
    resolved_path_title = path_title or slug_to_title(safe_path_slug)
    extras[f"paths/{safe_path_slug}/README.md"] = build_path_readme(resolved_path_title)

    if module_slug is not None:
        safe_module_slug = validate_slug(module_slug, "--module-slug")
        resolved_module_title = module_title or slug_to_title(safe_module_slug)
        extras[
            f"paths/{safe_path_slug}/modules/01-{safe_module_slug}.md"
        ] = build_module_template(resolved_module_title)
    return extras


def main() -> int:
    args = parse_args()
    target_root = Path(args.target).expanduser().resolve()
    ensure_target_repo(target_root)
    created = scaffold(target_root, force=args.force)
    extras = build_extra_files(
        args.path_slug,
        args.path_title,
        args.module_slug,
        args.module_title,
    )
    curriculum_dir = target_root / "curriculum"
    for relative_path, content in extras.items():
        output_path = curriculum_dir / relative_path
        if output_path.exists():
            continue
        write_file(output_path, content)
        created.append(output_path)

    if created:
        print("[OK] Created:")
        for path in created:
            print(f" - {path}")
    else:
        print("[OK] No new files were needed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
