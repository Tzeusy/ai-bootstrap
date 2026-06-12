#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Audit real skill usage from Claude Code and Codex transcripts.

Counts structured invocations only (Claude `Skill` tool calls and slash
commands; Codex function_call records that read a SKILL.md), never raw
catalog mentions. Inventories installed skills the same way bootstrap.sh
discovers them (pruning subskills/, archive/, etc.), attributes subskill
usage to the parent superskill, exempts skills added to git within the
window, and emits `git mv` recommendations into skills/archive/.

Usage:
    uv run skill_usage_audit.py                       # 30-day window
    uv run skill_usage_audit.py --since-days 90
    uv run skill_usage_audit.py --json                # machine-readable
"""

import argparse
import json
import re
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

PRUNE_DIRS = {".git", "node_modules", "tests", "fixtures", "assets", "subskills", "archive"}

CLAUDE_SKILL_RE = re.compile(r'"name":"Skill","input":\{[^}]{0,200}?"skill":"([^"]+)"')
CLAUDE_CMD_RE = re.compile(r"<command-name>/?([a-zA-Z0-9:_-]+)</command-name>")
CODEX_PATH_RE = re.compile(r"skills\\?/([a-zA-Z0-9_-]+)\\?/SKILL\.md")


def discover_skills(skills_root: Path):
    """Map installed skill name -> dir, subskill name -> parent superskill,
    and name -> [shadowed duplicate dirs] (resolution is filesystem-order
    in bootstrap.sh, so duplicates deserve a warning)."""
    skills, sub_to_super, dupes = {}, {}, {}
    def walk(d: Path):
        for child in sorted(d.iterdir()):
            if not child.is_dir() or child.name in PRUNE_DIRS:
                continue
            if (child / "SKILL.md").is_file():
                if child.name in skills:
                    dupes.setdefault(child.name, []).append(child)
                else:
                    skills[child.name] = child
                    subs = child / "subskills"
                    if subs.is_dir():
                        for s in sorted(subs.iterdir()):
                            if (s / "SKILL.md").is_file():
                                sub_to_super[s.name] = child.name
            walk(child)
    walk(skills_root)
    return skills, sub_to_super, dupes


def frontmatter_tokens(skill_dir: Path) -> int:
    """Rough token estimate (chars/4) of the SKILL.md frontmatter — the
    recurring per-session catalog cost of keeping the skill installed."""
    chars, fences = 0, 0
    try:
        for line in (skill_dir / "SKILL.md").read_text(errors="ignore").splitlines():
            if line.strip() == "---":
                fences += 1
                if fences == 2:
                    break
                continue
            if fences == 1:
                chars += len(line) + 1
    except OSError:
        pass
    return chars // 4


def recent_files(root: Path, cutoff: float):
    for p in root.rglob("*.jsonl"):
        try:
            if p.stat().st_mtime >= cutoff:
                yield p
        except OSError:
            continue


def scan(files, extractors):
    counts = Counter()
    for path in files:
        try:
            with open(path, encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    for guard, regex in extractors:
                        if guard in line:
                            counts.update(regex.findall(line))
        except OSError:
            continue
    return counts


def added_within(repo: Path, path: Path, cutoff: float) -> bool:
    """True if git says `path` was first added after the cutoff."""
    try:
        out = subprocess.run(
            ["git", "-C", str(repo), "log", "--diff-filter=A", "--follow",
             "--format=%ct", "--", str(path.relative_to(repo))],
            capture_output=True, text=True, timeout=30,
        ).stdout.split()
        if not out:
            # No add-commit visible from this repo: either genuinely uncommitted
            # (brand new) or nested inside a vendored submodule. Exempt both —
            # neither can be safely recommended for an archive move from here.
            return True
        return int(out[-1]) >= cutoff
    except (subprocess.SubprocessError, ValueError, OSError):
        return False  # unknown age: treat as not new, but flag manually if 0 uses


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--since-days", type=int, default=30)
    ap.add_argument("--skills-root", type=Path,
                    default=Path.home() / ".dotfiles/ai-bootstrap/skills")
    ap.add_argument("--claude-dir", type=Path, default=Path.home() / ".claude/projects")
    ap.add_argument("--codex-dir", type=Path, default=Path.home() / ".codex/sessions")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    cutoff = time.time() - args.since_days * 86400
    skills, sub_to_super, dupes = discover_skills(args.skills_root)
    if not skills:
        sys.exit(f"no skills found under {args.skills_root}")

    usage = Counter()
    if args.claude_dir.is_dir():
        usage += scan(recent_files(args.claude_dir, cutoff),
                      [('"name":"Skill"', CLAUDE_SKILL_RE),
                       ("<command-name>", CLAUDE_CMD_RE)])
    if args.codex_dir.is_dir():
        usage += scan(recent_files(args.codex_dir, cutoff),
                      [('"type":"function_call"', CODEX_PATH_RE)])

    # Attribute subskill usage to the parent superskill.
    rolled = Counter()
    for name, n in usage.items():
        rolled[sub_to_super.get(name, name)] += n

    used = {n: rolled[n] for n in skills if rolled[n] > 0}
    unused = [n for n in skills if rolled[n] == 0]
    new = {n for n in unused if added_within(args.skills_root, skills[n], cutoff)}
    removable = [n for n in unused if n not in new]

    earliest = min((p.stat().st_mtime for d in (args.claude_dir, args.codex_dir)
                    if d.is_dir() for p in d.rglob("*.jsonl")), default=None)

    report = {
        "window_days": args.since_days,
        "earliest_transcript": time.strftime("%Y-%m-%d", time.localtime(earliest)) if earliest else None,
        "used": dict(sorted(used.items(), key=lambda kv: -kv[1])),
        "new_exempt": sorted(new),
        "recommend_archive": sorted(removable, key=lambda n: -frontmatter_tokens(skills[n])),
        "catalog_cost_tokens": {n: frontmatter_tokens(skills[n])
                                for n in sorted(skills, key=lambda n: -frontmatter_tokens(skills[n]))},
        "shadowed_duplicates": {n: [str(p) for p in ps] for n, ps in sorted(dupes.items())},
        # Only skills this repo owns directly are movable; skills nested in
        # vendored submodules are reported above but cannot be git mv'd here.
        "commands": [
            f"git mv {skills[n].relative_to(args.skills_root.parent)} skills/archive/{n}"
            for n in sorted(removable)
            if skills[n].parent in (args.skills_root, args.skills_root / "personal")
        ],
    }
    if args.json:
        print(json.dumps(report, indent=2))
        return

    print(f"Window: last {args.since_days}d (transcripts back to {report['earliest_transcript']})\n")
    print(f"{'USES':>6}  SKILL")
    for n, c in report["used"].items():
        print(f"{c:>6}  {n}")
    for n in report["new_exempt"]:
        print(f"{'new':>6}  {n}  (added within window — exempt)")
    for n in report["recommend_archive"]:
        print(f"{0:>6}  {n}  (~{report['catalog_cost_tokens'][n]} catalog tokens/session)")
    reclaim = sum(report["catalog_cost_tokens"][n] for n in removable)
    print(f"\n{len(used)} used, {len(removable)} unused (recommend archive, "
          f"~{reclaim} catalog tokens/session reclaimable), {len(new)} new-exempt.")
    for n, ps in report["shadowed_duplicates"].items():
        print(f"WARNING: duplicate skill name '{n}' — linked copy is {skills[n]}, "
              f"shadowed: {', '.join(ps)} (resolution is filesystem-order; remove one)")
    if report["commands"]:
        print("\nRecommended (run inside the skills repo, then re-run bootstrap linking):")
        for c in report["commands"]:
            print(f"  {c}")


if __name__ == "__main__":
    main()
