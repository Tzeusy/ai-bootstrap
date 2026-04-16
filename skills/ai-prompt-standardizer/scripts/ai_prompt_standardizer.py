#!/usr/bin/env python3
"""
Synchronize canonical ai-bootstrap/skills and ai-bootstrap/agents into tool-specific folders.
"""

from __future__ import annotations

import argparse
import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Set

SKIP_DIRS = {".codex", ".claude", ".gemini", ".github"}


@dataclass(frozen=True)
class PlannedOp:
    action: str  # "copy" or "remove"
    src: Optional[Path]
    dest: Path
    kind: str  # "skills" or "agents" (professions)
    content: Optional[str] = None
    existed: bool = False


@dataclass
class Summary:
    copied: int = 0
    overwritten: int = 0
    removed: int = 0
    warnings: List[str] = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []


def default_base_dir() -> Path:
    # .../ai-bootstrap/skills/ai-prompt-standardizer/scripts/ai_prompt_standardizer.py
    return Path(__file__).resolve().parents[3]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync ai-bootstrap skills and professions into tool-specific prompt folders."
    )
    parser.add_argument("--dry-run", action="store_true", help="Print planned operations without writing")
    parser.add_argument("--verbose", action="store_true", help="Print detailed operation info")
    parser.add_argument(
        "--only",
        choices=["skills", "agents", "all"],
        default="all",
        help="Sync only skills, only agents (professions), or both",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Remove orphaned generated files that no longer have a source",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if changes would be made",
    )
    parser.add_argument(
        "--base",
        default=str(default_base_dir()),
        help="Base directory containing skills/ and professions/ (default: ai-bootstrap)",
    )
    return parser.parse_args()


def validate_base(base_dir: Path) -> None:
    if not base_dir.exists():
        raise RuntimeError(f"Base directory does not exist: {base_dir}")
    skills_dir = base_dir / "skills"
    professions_dir = base_dir / "professions"
    if not skills_dir.is_dir():
        raise RuntimeError(f"Missing skills directory: {skills_dir}")
    if not professions_dir.is_dir():
        raise RuntimeError(f"Missing professions directory: {professions_dir}")


def iter_files(root: Path) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for filename in filenames:
            yield Path(dirpath) / filename


def iter_files_with_skip(root: Path, skip_dirs: Set[str]) -> Iterable[Path]:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        for filename in filenames:
            yield Path(dirpath) / filename


def ensure_writable(dest: Path) -> None:
    if dest.exists() and not os.access(dest, os.W_OK):
        raise RuntimeError(f"Destination is read-only: {dest}")


def skills_plan(base_dir: Path) -> List[PlannedOp]:
    skills_dir = base_dir / "skills"
    dest_roots = [
        base_dir / ".codex" / "skills",
        base_dir / ".claude" / "skills",
        base_dir / ".gemini" / "skills",
        base_dir / ".github" / "skills",
    ]

    ops: List[PlannedOp] = []
    for src in sorted(iter_files(skills_dir)):
        rel = src.relative_to(skills_dir)
        if any(part in SKIP_DIRS for part in rel.parts):
            continue
        for dest_root in dest_roots:
            dest = dest_root / rel
            ops.append(
                PlannedOp(
                    action="copy",
                    src=src,
                    dest=dest,
                    kind="skills",
                    existed=dest.exists(),
                )
            )
    return ops


def profession_sources(professions_dir: Path) -> List[Path]:
    sources = []
    for src in iter_files(professions_dir):
        if src.name == "AGENTS.md":
            rel = src.relative_to(professions_dir)
            if any(part in SKIP_DIRS for part in rel.parts):
                continue
            sources.append(src)
    return sorted(sources)


def github_agent_filename(rel: Path) -> str:
    if rel == Path("AGENTS.md"):
        return "root.agent.md"
    safe = "__".join(rel.parent.parts)
    return f"{safe}.agent.md"


def github_agent_content(source_rel: Path, source_text: str) -> str:
    header = "# GENERATED FILE - DO NOT EDIT\n"
    header += f"# Source: professions/{source_rel.as_posix()}\n\n"
    return header + source_text


def professions_plan(base_dir: Path, warnings: List[str]) -> List[PlannedOp]:
    professions_dir = base_dir / "professions"
    sources = profession_sources(professions_dir)
    if not (professions_dir / "AGENTS.md").exists():
        warnings.append("Missing professions/AGENTS.md (root agent instructions)")

    ops: List[PlannedOp] = []
    for src in sources:
        rel = src.relative_to(professions_dir)

        # Codex
        if rel == Path("AGENTS.md"):
            dest = base_dir / ".codex" / "AGENTS.md"
        else:
            dest = base_dir / ".codex" / rel.parent / "AGENTS.override.md"
        ops.append(PlannedOp("copy", src, dest, "agents", existed=dest.exists()))

        # Claude
        if rel == Path("AGENTS.md"):
            dest = base_dir / ".claude" / "CLAUDE.md"
        else:
            dest = base_dir / ".claude" / rel.parent / "CLAUDE.md"
        ops.append(PlannedOp("copy", src, dest, "agents", existed=dest.exists()))

        # Gemini
        if rel == Path("AGENTS.md"):
            dest = base_dir / ".gemini" / "GEMINI.md"
        else:
            dest = base_dir / ".gemini" / rel.parent / "GEMINI.md"
        ops.append(PlannedOp("copy", src, dest, "agents", existed=dest.exists()))

        # GitHub
        dest = base_dir / ".github" / "agents" / github_agent_filename(rel)
        content = github_agent_content(rel, src.read_text(encoding="utf-8"))
        ops.append(
            PlannedOp(
                "copy",
                src,
                dest,
                "agents",
                content=content,
                existed=dest.exists(),
            )
        )

    return ops


def clean_ops(dest_roots: Iterable[Path], expected: Set[Path], kind: str) -> List[PlannedOp]:
    ops: List[PlannedOp] = []
    for root in dest_roots:
        if not root.exists():
            continue
        for existing in iter_files(root):
            if existing not in expected:
                ops.append(PlannedOp("remove", None, existing, kind))
    return ops


def skill_clean_roots(base_dir: Path) -> List[Path]:
    return [
        base_dir / ".codex" / "skills",
        base_dir / ".claude" / "skills",
        base_dir / ".gemini" / "skills",
        base_dir / ".github" / "skills",
    ]


def iter_agent_dest_files(base_dir: Path) -> Iterable[Path]:
    codex_root = base_dir / ".codex"
    if codex_root.exists():
        for existing in iter_files_with_skip(codex_root, {"skills"}):
            if existing.name in {"AGENTS.md", "AGENTS.override.md"}:
                yield existing

    claude_root = base_dir / ".claude"
    if claude_root.exists():
        for existing in iter_files_with_skip(claude_root, {"skills"}):
            if existing.name == "CLAUDE.md":
                yield existing

    gemini_root = base_dir / ".gemini"
    if gemini_root.exists():
        for existing in iter_files_with_skip(gemini_root, {"skills"}):
            if existing.name == "GEMINI.md":
                yield existing

    github_agents = base_dir / ".github" / "agents"
    if github_agents.exists():
        for existing in iter_files_with_skip(github_agents, set()):
            if existing.name.endswith(".agent.md"):
                yield existing


def agent_clean_ops(base_dir: Path, expected: Set[Path]) -> List[PlannedOp]:
    ops: List[PlannedOp] = []
    for existing in iter_agent_dest_files(base_dir):
        if existing not in expected:
            ops.append(PlannedOp("remove", None, existing, "agents-clean"))
    return ops


def agent_clean_roots(base_dir: Path) -> List[Path]:
    return [
        base_dir / ".codex",
        base_dir / ".claude",
        base_dir / ".gemini",
        base_dir / ".github" / "agents",
    ]


def execute_ops(ops: List[PlannedOp], dry_run: bool, summary: Summary) -> None:
    for op in ops:
        if op.action == "copy":
            ensure_writable(op.dest)
            if dry_run:
                continue
            op.dest.parent.mkdir(parents=True, exist_ok=True)
            if op.content is not None:
                op.dest.write_text(op.content, encoding="utf-8")
            else:
                assert op.src is not None
                shutil.copy2(op.src, op.dest)
        elif op.action == "remove":
            ensure_writable(op.dest)
            if dry_run:
                continue
            op.dest.unlink()
        else:
            raise RuntimeError(f"Unknown action: {op.action}")


def remove_empty_dirs(roots: Iterable[Path], dry_run: bool) -> None:
    for root in roots:
        if not root.exists():
            continue
        for dirpath, dirnames, filenames in os.walk(root, topdown=False):
            if dirnames or filenames:
                continue
            path = Path(dirpath)
            if dry_run:
                continue
            try:
                path.rmdir()
            except OSError:
                pass


def print_ops(ops: List[PlannedOp], prefix: str) -> None:
    for op in ops:
        if op.action == "copy":
            action = "OVERWRITE" if op.existed else "COPY"
            print(f"{prefix} {action}: {op.src} -> {op.dest}")
        else:
            print(f"{prefix} REMOVE: {op.dest}")


def summarize(summary: Summary) -> None:
    print("Summary:")
    print(f"copied: {summary.copied}")
    print(f"overwritten: {summary.overwritten}")
    print(f"removed: {summary.removed}")
    print(f"warnings: {len(summary.warnings)}")
    for warning in summary.warnings:
        print(f"warning: {warning}")


def populate_summary_from_ops(ops: List[PlannedOp], summary: Summary) -> None:
    for op in ops:
        if op.action == "copy":
            if op.existed:
                summary.overwritten += 1
            else:
                summary.copied += 1
        elif op.action == "remove":
            summary.removed += 1


def main() -> int:
    args = parse_args()
    base_dir = Path(args.base).resolve()

    try:
        validate_base(base_dir)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    summary = Summary()
    ops: List[PlannedOp] = []

    if args.only in ("skills", "all"):
        ops.extend(skills_plan(base_dir))

    if args.only in ("agents", "all"):
        ops.extend(professions_plan(base_dir, summary.warnings))

    # Deterministic ordering
    ops = sorted(ops, key=lambda o: (str(o.dest), o.action))

    if args.clean:
        expected: Set[Path] = {op.dest for op in ops if op.action == "copy"}
        clean_ops_list: List[PlannedOp] = []
        if args.only in ("skills", "all"):
            clean_ops_list.extend(clean_ops(skill_clean_roots(base_dir), expected, "skills-clean"))
        if args.only in ("agents", "all"):
            clean_ops_list.extend(agent_clean_ops(base_dir, expected))
        ops.extend(clean_ops_list)
        ops = sorted(ops, key=lambda o: (str(o.dest), o.action))

    populate_summary_from_ops(ops, summary)

    show_ops = True
    if show_ops and ops:
        prefix = "PLAN" if (args.dry_run or args.check) else "APPLY"
        print_ops(ops, prefix)

    if args.check:
        try:
            for op in ops:
                ensure_writable(op.dest)
        except RuntimeError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 1
        summarize(summary)
        return 2 if ops else 0

    try:
        execute_ops(ops, args.dry_run, summary)
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    if args.clean:
        clean_roots: List[Path] = []
        if args.only in ("skills", "all"):
            clean_roots.extend(skill_clean_roots(base_dir))
        if args.only in ("agents", "all"):
            clean_roots.extend(agent_clean_roots(base_dir))
        remove_empty_dirs(clean_roots, args.dry_run)

    summarize(summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
