#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""spec-trace-check.py — mechanical traceability validator for OpenSpec trees.

Validates the spec side of the doctrine -> RFC -> spec -> test chain defined
in th-projects references/spec-format.md:

  ERRORS (always fail):
    - main spec using delta headings, or delta spec using main headings
    - requirement with no scenario (main specs; delta ADDED/MODIFIED)
    - scenario without exactly 1 WHEN and 1 THEN bullet
    - duplicate or malformed requirement IDs (ID spec-name must match dir)
    - stale test citations: REQ- IDs cited in tests but absent from specs

  WARNINGS (errors under --strict):
    - requirement missing ID / Source / Scope lines (legacy specs)
    - v1-mandatory requirement with no test citation (when a test tree exists)

Usage:
  uv run spec-trace-check.py <repo-root> [--tests-dir DIR ...] [--strict]

Exit 0 = clean (warnings allowed unless --strict). Exit 1 = findings.
Exit 2 = no openspec/ tree found.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

MAIN_H2 = {"Purpose", "Requirements"}
DELTA_H2 = {
    "ADDED Requirements",
    "MODIFIED Requirements",
    "REMOVED Requirements",
    "RENAMED Requirements",
}
SCENARIO_FREE_OPS = {"REMOVED Requirements", "RENAMED Requirements"}
ID_LINE_RE = re.compile(r"^ID:\s*(\S+)\s*$")
ID_FORMAT_RE = re.compile(r"^REQ-([a-z0-9-]+)-(\d{3})$")
SOURCE_LINE_RE = re.compile(r"^Source:\s*\S")
SCOPE_LINE_RE = re.compile(r"^Scope:\s*(v1-mandatory|v1-reserved|post-v1)\s*$")
TEST_ID_RE = re.compile(r"REQ[-_][a-z0-9]+(?:[-_][a-z0-9]+)*[-_]\d{3}", re.IGNORECASE)
TEST_FILE_HINT = re.compile(r"(^|[._-])(test|spec)s?([._-]|$)", re.IGNORECASE)
TEST_SUFFIXES = {".py", ".ts", ".tsx", ".js", ".jsx", ".go", ".rs", ".java", ".kt", ".rb", ".sh", ".ex", ".exs", ".cs", ".swift"}


@dataclass
class Requirement:
    title: str
    spec_name: str
    file: Path
    line: int
    op: str  # "Requirements", "ADDED Requirements", ...
    req_id: str | None = None
    id_line: int | None = None
    has_source: bool = False
    scope: str | None = None
    scenarios: int = 0


@dataclass
class Findings:
    errors: list = field(default_factory=list)
    warnings: list = field(default_factory=list)

    def error(self, path, line, msg):
        self.errors.append(f"ERROR  {path}:{line}: {msg}")

    def warn(self, path, line, msg):
        self.warnings.append(f"WARN   {path}:{line}: {msg}")


def parse_spec(path: Path, spec_name: str, is_delta: bool, f: Findings) -> list:
    """Parse one spec.md; emit structural findings; return requirements."""
    rel = path
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    reqs: list[Requirement] = []
    cur: Requirement | None = None
    cur_op = None
    scen_line = None
    when_count = then_count = 0

    def close_scenario():
        nonlocal scen_line, when_count, then_count
        if scen_line is not None and (when_count != 1 or then_count != 1):
            f.error(rel, scen_line,
                    f"scenario needs exactly 1 WHEN and 1 THEN bullet (found {when_count} WHEN, {then_count} THEN)")
        scen_line, when_count, then_count = None, 0, 0

    for i, raw in enumerate(lines, 1):
        line = raw.rstrip()
        m2 = re.match(r"^## (.+)$", line)
        if m2:
            close_scenario()
            cur = None
            h2 = m2.group(1).strip()
            cur_op = h2
            if is_delta and h2 in MAIN_H2:
                f.error(rel, i, f"delta spec uses main-spec heading '## {h2}' — use ADDED/MODIFIED/REMOVED/RENAMED Requirements")
            elif not is_delta and h2 in DELTA_H2:
                f.error(rel, i, f"main spec uses delta heading '## {h2}' — main specs use '## Requirements'")
            continue
        m3 = re.match(r"^### Requirement:\s*(.+)$", line)
        if m3:
            close_scenario()
            cur = Requirement(title=m3.group(1).strip(), spec_name=spec_name,
                              file=path, line=i, op=cur_op or "?")
            reqs.append(cur)
            continue
        m4 = re.match(r"^#### Scenario:", line)
        if m4:
            close_scenario()
            scen_line = i
            if cur:
                cur.scenarios += 1
            continue
        if scen_line is not None:
            if re.match(r"^-\s+\*\*WHEN\*\*", line):
                when_count += 1
            elif re.match(r"^-\s+\*\*THEN\*\*", line):
                then_count += 1
            continue
        if cur and cur.scenarios == 0:
            mid = ID_LINE_RE.match(line)
            if mid:
                cur.req_id, cur.id_line = mid.group(1), i
            elif SOURCE_LINE_RE.match(line):
                cur.has_source = True
            else:
                msc = SCOPE_LINE_RE.match(line)
                if msc:
                    cur.scope = msc.group(1)
                elif line.startswith("Scope:"):
                    f.error(rel, i, f"invalid Scope value: {line!r} (use v1-mandatory | v1-reserved | post-v1)")
    close_scenario()
    return reqs


def check_requirements(reqs, f: Findings, strict_missing_fields: bool):
    seen_ids: dict[str, Requirement] = {}
    for r in reqs:
        rel, needs_scenarios = r.file, r.op not in SCENARIO_FREE_OPS
        if needs_scenarios and r.scenarios == 0:
            f.error(rel, r.line, f"requirement '{r.title}' has no scenarios")
        if r.req_id:
            m = ID_FORMAT_RE.match(r.req_id)
            if not m:
                f.error(rel, r.id_line, f"malformed ID '{r.req_id}' (expected REQ-{r.spec_name}-NNN)")
            elif m.group(1) != r.spec_name:
                f.error(rel, r.id_line, f"ID '{r.req_id}' names spec '{m.group(1)}' but lives in spec '{r.spec_name}'")
            elif r.req_id in seen_ids:
                prev = seen_ids[r.req_id]
                if prev.op == "Requirements" and r.op != "Requirements" and prev.title == r.title:
                    pass  # delta legitimately re-states a main-spec requirement it modifies
                else:
                    f.error(rel, r.id_line, f"duplicate ID '{r.req_id}' (also at {prev.file}:{prev.line})")
            else:
                seen_ids[r.req_id] = r
        report = f.error if strict_missing_fields else f.warn
        missing = [name for name, ok in
                   (("ID", r.req_id), ("Source", r.has_source), ("Scope", r.scope)) if not ok]
        if missing:
            report(rel, r.line, f"requirement '{r.title}' missing {'/'.join(missing)} line(s)")
    return seen_ids


def find_test_files(repo: Path, tests_dirs):
    roots = [repo / d for d in tests_dirs] if tests_dirs else [
        p for p in repo.rglob("*") if p.is_dir() and p.name in ("tests", "test")
        and "node_modules" not in p.parts and ".git" not in p.parts
        and len(p.relative_to(repo).parts) <= 3
    ]
    files = []
    for root in roots:
        if not root.is_dir():
            print(f"WARN   tests dir not found: {root}", file=sys.stderr)
            continue
        files.extend(p for p in root.rglob("*")
                     if p.is_file() and p.suffix in TEST_SUFFIXES and TEST_FILE_HINT.search(p.name))
    return files


def normalize_test_id(raw: str) -> str:
    return raw.upper().replace("_", "-").replace("REQ-", "REQ-", 1).lower().replace("req-", "REQ-", 1)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("repo_root", type=Path)
    ap.add_argument("--tests-dir", action="append", default=[],
                    help="test directory relative to repo root (repeatable; default: auto-detect tests/ + test/)")
    ap.add_argument("--strict", action="store_true",
                    help="treat missing ID/Source/Scope and uncovered v1-mandatory requirements as errors")
    args = ap.parse_args()

    repo = args.repo_root.resolve()
    openspec = repo / "openspec"
    if not openspec.is_dir():
        print(f"no openspec/ tree at {repo}", file=sys.stderr)
        return 2

    f = Findings()
    reqs: list[Requirement] = []

    for spec in sorted(openspec.glob("specs/*/spec.md")):
        reqs += parse_spec(spec, spec.parent.name, is_delta=False, f=f)
    for spec in sorted(openspec.glob("changes/*/specs/*/spec.md")):
        if "archive" in spec.relative_to(openspec).parts:
            continue
        reqs += parse_spec(spec, spec.parent.name, is_delta=True, f=f)

    if not reqs and not f.errors:
        print("no requirements found under openspec/ — nothing to check")
        return 0

    seen_ids = check_requirements(reqs, f, strict_missing_fields=args.strict)

    test_files = find_test_files(repo, args.tests_dir)
    cited: set[str] = set()
    citations: dict[str, tuple] = {}
    for tf in test_files:
        try:
            text = tf.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for m in TEST_ID_RE.finditer(text):
            rid = normalize_test_id(m.group(0))
            cited.add(rid)
            citations.setdefault(rid, (tf, text[:m.start()].count("\n") + 1))

    for rid, (tf, line) in sorted(citations.items()):
        if rid not in seen_ids:
            f.error(tf, line, f"stale test citation: '{rid}' not found in any spec")

    if test_files:
        report = f.error if args.strict else f.warn
        for rid, r in sorted(seen_ids.items()):
            if r.scope == "v1-mandatory" and rid not in cited:
                report(r.file, r.line, f"v1-mandatory requirement '{rid}' has no test citation")
    else:
        print("note: no test tree found — skipping test-citation coverage", file=sys.stderr)

    for msg in f.errors + f.warnings:
        print(msg)
    ok = not f.errors
    print(f"\nspec-trace-check: {len(reqs)} requirements, {len(seen_ids)} IDs, "
          f"{len(f.errors)} error(s), {len(f.warnings)} warning(s) — {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
