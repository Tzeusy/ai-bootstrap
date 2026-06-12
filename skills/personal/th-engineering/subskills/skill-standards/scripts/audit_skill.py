#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pyyaml>=6",
# ]
# ///
"""Mechanical conformance audit for an agentskills.io-style skill package.

Checks the parts of the skill-standards quality bar that don't need judgment:
frontmatter validity, name/description limits, metadata fields, link
integrity, orphaned support files, PEP 723 compliance of Python helpers,
tool-adapter YAML validity, and superskill (subskills/) layout.

Usage:
  uv run scripts/audit_skill.py <skill-package-dir> [--strict] [--stale-days N]
  uv run scripts/audit_skill.py --all <skills-root> [--skip NAME ...] [--json]

--all discovers every package under the root (a dir with SKILL.md, excluding
subskills/ trees, fixtures, and hidden dirs) and audits each; --skip excludes
packages by directory name. --json emits a machine-readable report for CI.
Links inside fenced code blocks are treated as illustrative and ignored.

Exit codes: 0 = no errors (warnings allowed unless --strict), 1 = errors found,
2 = bad invocation. Judgment items (trigger quality, scope, grounding) are NOT
checked here — see references/quality-bar.md.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

import yaml

NAME_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
MAX_NAME_LEN = 64
MAX_DESCRIPTION_LEN = 1024
SKILL_MD_LINE_BUDGET = 500
PEP723_RE = re.compile(r"^# /// script\s*$.*?^# ///\s*$", re.MULTILINE | re.DOTALL)
PLACEHOLDER_RE = re.compile(r"replace with|todo|tbd|fixme", re.IGNORECASE)
# Markdown links to local files; skips http(s), mailto, and anchors.
LOCAL_LINK_RE = re.compile(r"\[[^\]]*\]\((?!https?://|mailto:|#)([^)#\s]+)")
KNOWN_DIRS = {"references", "scripts", "assets", "subskills", "agents", "tests"}
MAIN_GUARD_RE = re.compile(r"""__name__\s*==\s*["']__main__["']""")
VALID_STATUS = {"active", "draft", "deprecated"}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def parse_frontmatter(skill_md: Path, rep: Report, label: str) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        rep.error(f"{label}: SKILL.md does not start with YAML frontmatter")
        return {}
    parts = text.split("---", 2)
    if len(parts) < 3:
        rep.error(f"{label}: unterminated YAML frontmatter")
        return {}
    try:
        fm = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        rep.error(f"{label}: invalid YAML frontmatter: {exc}")
        return {}
    if not isinstance(fm, dict):
        rep.error(f"{label}: frontmatter is not a mapping")
        return {}
    return fm


def check_frontmatter(fm: dict, rep: Report, label: str, dir_name: str) -> None:
    name = fm.get("name")
    if not name:
        rep.error(f"{label}: missing required field 'name'")
    else:
        if not NAME_RE.match(str(name)):
            rep.error(f"{label}: name {name!r} is not lowercase-hyphen-digits")
        if len(str(name)) > MAX_NAME_LEN:
            rep.error(f"{label}: name exceeds {MAX_NAME_LEN} chars")
        if str(name) != dir_name:
            rep.warn(f"{label}: name {name!r} != directory name {dir_name!r}")

    desc = fm.get("description")
    if not desc:
        rep.error(f"{label}: missing required field 'description'")
    else:
        if len(str(desc)) > MAX_DESCRIPTION_LEN:
            rep.error(f"{label}: description exceeds {MAX_DESCRIPTION_LEN} chars")
        if PLACEHOLDER_RE.search(str(desc)):
            rep.error(f"{label}: description contains placeholder text")

    meta = fm.get("metadata") or {}
    if not isinstance(meta, dict):
        rep.warn(f"{label}: metadata is not a mapping")
        meta = {}
    for field in ("owner", "authors", "status", "last_reviewed"):
        if field not in meta:
            rep.warn(f"{label}: metadata.{field} missing (recommended)")
    status = meta.get("status")
    if status and status not in VALID_STATUS:
        rep.warn(f"{label}: metadata.status {status!r} not one of {sorted(VALID_STATUS)}")


def check_staleness(fm: dict, rep: Report, label: str, stale_days: int) -> None:
    raw = (fm.get("metadata") or {}).get("last_reviewed")
    if not raw:
        return
    try:
        reviewed = dt.date.fromisoformat(str(raw))
    except ValueError:
        rep.warn(f"{label}: metadata.last_reviewed {raw!r} is not ISO YYYY-MM-DD")
        return
    age = (dt.date.today() - reviewed).days
    if age > stale_days:
        rep.warn(f"{label}: last_reviewed is {age} days old (> {stale_days})")


FENCE_RE = re.compile(r"^(```|~~~)[^\n]*\n.*?^\1\s*$", re.MULTILINE | re.DOTALL)
CODE_SPAN_RE = re.compile(r"`[^`\n]+`")


def collect_local_links(md_file: Path) -> list[str]:
    """Extract local markdown link targets, ignoring code.

    Links inside fenced blocks or inline code spans are illustrative
    (templates, examples for target projects), not package links."""
    text = md_file.read_text(encoding="utf-8")
    text = FENCE_RE.sub("", text)
    text = CODE_SPAN_RE.sub("", text)
    return LOCAL_LINK_RE.findall(text)


def check_links(pkg: Path, rep: Report, label: str) -> tuple[set[Path], set[Path]]:
    """Verify local markdown links resolve.

    Returns (linked-from-anywhere, linked-directly-from-SKILL.md)."""
    linked: set[Path] = set()
    skill_linked: set[Path] = set()
    for md in [pkg / "SKILL.md", *sorted((pkg / "references").rglob("*.md"))]:
        if not md.exists():
            continue
        for target in collect_local_links(md):
            resolved = (md.parent / target).resolve()
            if resolved.exists():
                linked.add(resolved)
                if md.name == "SKILL.md":
                    skill_linked.add(resolved)
            else:
                rep.error(f"{label}: {md.relative_to(pkg)} links to missing file {target!r}")
    return linked, skill_linked


def check_orphans(pkg: Path, linked: set[Path], skill_linked: set[Path], rep: Report, label: str) -> None:
    """Warn on context-bearing files no doc links to.

    Docs (references/**/*.md) must always be discoverable. For scripts/ and
    assets/ only top-level files count — nested files are package internals or
    script-consumed data, as are non-markdown files under references/."""
    candidates = [
        *(pkg / "references").rglob("*.md"),
        *(pkg / "scripts").glob("*"),
        *(pkg / "assets").glob("*"),
    ]
    for f in sorted(candidates):
        rel_parts = f.relative_to(pkg).parts
        hidden = any(p.startswith(".") or p == "__pycache__" for p in rel_parts)
        if not f.is_file() or f.name == "__init__.py" or hidden:
            continue
        if f.resolve() not in linked:
            rep.warn(f"{label}: {f.relative_to(pkg)} is never linked from SKILL.md or references/")
    # Deep reference chains: a reference doc reachable only via another reference.
    for f in sorted((pkg / "references").rglob("*.md")):
        if f.resolve() in linked and f.resolve() not in skill_linked:
            rep.warn(
                f"{label}: {f.relative_to(pkg)} is linked only transitively (deep reference "
                "chain) — link important support files directly from SKILL.md"
            )


def check_pep723(pkg: Path, rep: Report, label: str) -> None:
    """Require PEP 723 metadata on entry-point scripts; exempt library modules.

    Top-level scripts/*.py are always entry points. Nested .py files count only
    when they carry a shebang or a __main__ guard; __init__.py never does."""
    scripts_dir = pkg / "scripts"
    for py in sorted(scripts_dir.rglob("*.py")):
        if py.name == "__init__.py" or "__pycache__" in py.parts:
            continue
        text = py.read_text(encoding="utf-8")
        if PEP723_RE.search(text):
            continue
        if py.parent == scripts_dir or text.startswith("#!") or MAIN_GUARD_RE.search(text):
            rep.error(
                f"{label}: {py.relative_to(pkg)} lacks PEP 723 inline metadata "
                "(# /// script ... # ///) — required so it runs via `uv run` in any environment"
            )


def check_skill_md_budget(pkg: Path, rep: Report, label: str) -> None:
    lines = (pkg / "SKILL.md").read_text(encoding="utf-8").count("\n") + 1
    if lines > SKILL_MD_LINE_BUDGET:
        rep.warn(f"{label}: SKILL.md is {lines} lines (> {SKILL_MD_LINE_BUDGET} budget) — fan content out")


def check_adapters(pkg: Path, rep: Report, label: str) -> None:
    for adapter in sorted((pkg / "agents").glob("*.y*ml")):
        try:
            data = yaml.safe_load(adapter.read_text(encoding="utf-8"))
        except yaml.YAMLError as exc:
            rep.error(f"{label}: {adapter.relative_to(pkg)} is invalid YAML: {exc}")
            continue
        if not isinstance(data, dict):
            rep.error(f"{label}: {adapter.relative_to(pkg)} is not a YAML mapping")
            continue
        interface = data.get("interface")
        if not isinstance(interface, dict) or not interface.get("display_name"):
            rep.warn(
                f"{label}: {adapter.relative_to(pkg)} has no interface.display_name — "
                "hollow adapter, fill it in or delete it"
            )


def check_layout(pkg: Path, rep: Report, label: str) -> None:
    for entry in sorted(pkg.iterdir()):
        if entry.is_dir() and entry.name not in KNOWN_DIRS and not entry.name.startswith("."):
            rep.warn(f"{label}: unexpected top-level directory {entry.name}/")


def audit_package(pkg: Path, rep: Report, stale_days: int, label: str | None = None) -> None:
    label = label or pkg.name
    skill_md = pkg / "SKILL.md"
    if not skill_md.exists():
        rep.error(f"{label}: no SKILL.md found")
        return
    fm = parse_frontmatter(skill_md, rep, label)
    if fm:
        check_frontmatter(fm, rep, label, pkg.name)
        check_staleness(fm, rep, label, stale_days)
    check_skill_md_budget(pkg, rep, label)
    linked, skill_linked = check_links(pkg, rep, label)
    check_orphans(pkg, linked, skill_linked, rep, label)
    check_pep723(pkg, rep, label)
    check_adapters(pkg, rep, label)
    check_layout(pkg, rep, label)


def audit_superskill(pkg: Path, rep: Report, stale_days: int) -> None:
    subskills = pkg / "subskills"
    if not subskills.is_dir():
        return
    # Real markdown links only — a fence-quoted path is illustrative, not routing.
    router_md = pkg / "SKILL.md"
    router_links: set[Path] = set()
    if router_md.exists():
        for target in collect_local_links(router_md):
            router_links.add((router_md.parent / target).resolve())
    names: dict[str, str] = {}
    for sub in sorted(p for p in subskills.iterdir() if p.is_dir()):
        label = f"{pkg.name}/subskills/{sub.name}"
        audit_package(sub, rep, stale_days, label=label)
        fm = parse_frontmatter(sub / "SKILL.md", Report(), label) if (sub / "SKILL.md").exists() else {}
        name = str(fm.get("name", ""))
        if name in names:
            rep.error(f"{label}: subskill name {name!r} duplicates {names[name]}")
        elif name:
            names[name] = label
        if (sub / "SKILL.md").resolve() not in router_links:
            rep.error(f"{pkg.name}: router SKILL.md has no routing-table link to subskills/{sub.name}/SKILL.md")


# Dirs whose nested SKILL.md files are fixtures or internals, not packages.
NON_PACKAGE_PARTS = {"subskills", "references", "scripts", "assets", "tests", "fixtures", "node_modules"}


def discover_packages(root: Path, skips: set[str]) -> list[Path]:
    pkgs = []
    for skill_md in sorted(root.rglob("SKILL.md")):
        rel_parts = skill_md.parent.relative_to(root).parts
        if any(p.startswith(".") or p in NON_PACKAGE_PARTS for p in rel_parts):
            continue
        if any(p in skips for p in rel_parts):
            continue
        pkgs.append(skill_md.parent)
    return pkgs


def audit_one(pkg: Path, stale_days: int) -> Report:
    rep = Report()
    audit_package(pkg, rep, stale_days)
    audit_superskill(pkg, rep, stale_days)
    return rep


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("package", type=Path, nargs="?", help="path to one skill package directory")
    parser.add_argument("--all", type=Path, metavar="ROOT", help="discover and audit every package under ROOT")
    parser.add_argument("--skip", action="append", default=[], metavar="NAME", help="directory name to exclude from --all (repeatable)")
    parser.add_argument("--json", action="store_true", help="emit a machine-readable JSON report")
    parser.add_argument("--strict", action="store_true", help="treat warnings as errors")
    parser.add_argument("--stale-days", type=int, default=180, help="warn when last_reviewed is older (default 180)")
    args = parser.parse_args()

    if bool(args.package) == bool(args.all):
        print("error: pass exactly one of <package> or --all ROOT", file=sys.stderr)
        return 2

    if args.all:
        root = args.all.resolve()
        if not root.is_dir():
            print(f"error: {root} is not a directory", file=sys.stderr)
            return 2
        pkgs = discover_packages(root, set(args.skip))
        if not pkgs:
            print(f"error: no skill packages found under {root}", file=sys.stderr)
            return 2
    else:
        pkgs = [args.package.resolve()]
        if not pkgs[0].is_dir():
            print(f"error: {pkgs[0]} is not a directory", file=sys.stderr)
            return 2

    results = [(pkg, audit_one(pkg, args.stale_days)) for pkg in pkgs]
    failed = any(rep.errors or (args.strict and rep.warnings) for _, rep in results)

    if args.json:
        print(json.dumps({
            "strict": args.strict,
            "status": "FAIL" if failed else "PASS",
            "packages": [
                {
                    "package": str(pkg),
                    "name": pkg.name,
                    "errors": rep.errors,
                    "warnings": rep.warnings,
                    "status": "FAIL" if rep.errors or (args.strict and rep.warnings) else "PASS",
                }
                for pkg, rep in results
            ],
        }, indent=2))
        return 1 if failed else 0

    for pkg, rep in results:
        for msg in rep.errors:
            print(f"ERROR  {msg}")
        for msg in rep.warnings:
            print(f"WARN   {msg}")
        pkg_failed = bool(rep.errors) or (args.strict and bool(rep.warnings))
        print(f"{pkg.name}: {len(rep.errors)} error(s), {len(rep.warnings)} warning(s) — {'FAIL' if pkg_failed else 'PASS'}")
    if len(results) > 1:
        n_fail = sum(1 for _, rep in results if rep.errors or (args.strict and rep.warnings))
        print(f"\n{len(results)} package(s): {len(results) - n_fail} pass, {n_fail} fail")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
