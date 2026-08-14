#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Produce a transcript-minimizing skill-usage decision matrix.

The audit consumes the canonical catalog manifest emitted by
``scripts/link-ai-skills.sh --catalog-manifest``. It reads transcript files
only while streaming structured usage events into aggregate counters; it never
writes transcript-derived text, identifiers, filenames, projects, or absolute
paths into its report.
"""

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Iterator, List, Mapping, Optional, Sequence, Tuple


UTC = timezone.utc

CANDIDATE_PROFILES: Tuple[Tuple[str, str, str], ...] = (
    (
        "using-superpowers",
        "Session-start discovery guard for selecting applicable workflows.",
        "Native catalog injection can satisfy this guard without an observable file read.",
    ),
    (
        "brainstorming",
        "Clarify intent and design before creative implementation work.",
        "Complements implementation planning; it does not prescribe execution checkpoints.",
    ),
    (
        "writing-plans",
        "Turn an accepted design into a staged implementation plan.",
        "Distinct from brainstorming and from executing an already-written plan.",
    ),
    (
        "executing-plans",
        "Carry out a written plan with checkpoints in a separate session.",
        "Complements plan authoring rather than replacing independent-task dispatch.",
    ),
    (
        "using-git-worktrees",
        "Create isolated workspaces before risky or parallel implementation.",
        "Provides workspace isolation, not task delegation or review discipline.",
    ),
    (
        "test-driven-development",
        "Drive feature and bug-fix behavior from a failing test.",
        "Complements verification by defining implementation order rather than final evidence.",
    ),
    (
        "systematic-debugging",
        "Diagnose unexpected behavior before proposing a repair.",
        "Applies to failure analysis, not feature planning or test-first delivery.",
    ),
    (
        "verification-before-completion",
        "Collect current evidence before claiming a change is complete.",
        "Complements test-driven development with final exact-state verification.",
    ),
    (
        "dispatching-parallel-agents",
        "Dispatch two or more independent tasks that have no shared state.",
        "Distinct from subagent-driven-development: this coordinates independent work, not plan checkpoints.",
    ),
    (
        "subagent-driven-development",
        "Execute a written implementation plan with task and whole-branch review checkpoints.",
        "Distinct from dispatching-parallel-agents: this protects sequential plan execution and review.",
    ),
    (
        "finishing-a-development-branch",
        "Choose a safe integration path after a verified implementation is complete.",
        "Focuses on handoff and integration rather than code review itself.",
    ),
    (
        "requesting-code-review",
        "Request an independent quality pass for a completed change.",
        "Distinct from receiving-code-review, which evaluates and applies feedback.",
    ),
    (
        "receiving-code-review",
        "Evaluate code-review feedback rigorously before changing code.",
        "Distinct from requesting-code-review, which initiates the independent review.",
    ),
)

CLAUDE_COMMAND_RE = re.compile(r"<command-name>/?([A-Za-z0-9:_-]+)</command-name>")
CODEX_SKILL_PATH_RE = re.compile(r"(?:^|[\\/])([A-Za-z0-9_-]+)[\\/]SKILL\.md(?:$|[?\"'\s])")


def default_repo_root() -> Path:
    """Return the repository root when this script is run from its source tree."""
    return Path(__file__).resolve().parents[6]


def parse_utc_timestamp(value: str) -> datetime:
    """Accept only an explicit zero-offset timestamp for reproducible windows."""
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--as-of must be an explicit UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise argparse.ArgumentTypeError("--as-of must be an explicit UTC timestamp")
    return parsed.astimezone(UTC)


def timestamp_text(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_source_path(repo_root: Path, source: Any) -> Optional[Path]:
    """Resolve a manifest source only when it remains a repo-relative skill path."""
    if not isinstance(source, str):
        return None
    candidate = Path(source)
    if candidate.is_absolute() or candidate.parts[:1] != ("skills",) or ".." in candidate.parts:
        return None
    resolved_root = repo_root.resolve()
    resolved = (resolved_root / candidate).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        return None
    return resolved


def load_catalog_manifest(repo_root: Path, manifest_path: Optional[Path]) -> Dict[str, Dict[str, str]]:
    """Load a linker manifest without passing its raw filesystem inputs through."""
    if manifest_path is None:
        linker = repo_root / "scripts" / "link-ai-skills.sh"
        try:
            result = subprocess.run(
                ["bash", str(linker), "--catalog-manifest", str(repo_root)],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise ValueError("catalog manifest generation failed") from exc
        if result.returncode != 0:
            raise ValueError("catalog manifest generation failed")
        raw_manifest = result.stdout
    else:
        try:
            raw_manifest = manifest_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError("catalog manifest unavailable") from exc

    try:
        payload = json.loads(raw_manifest)
    except json.JSONDecodeError as exc:
        raise ValueError("catalog manifest is invalid") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("catalog manifest is invalid")
    entries = payload.get("skills")
    if not isinstance(entries, list):
        raise ValueError("catalog manifest is invalid")

    catalog: Dict[str, Dict[str, str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("catalog manifest is invalid")
        name = entry.get("name")
        source = entry.get("source")
        ownership = entry.get("ownership")
        if (
            not isinstance(name, str)
            or not name
            or not isinstance(source, str)
            or safe_source_path(repo_root, source) is None
            or ownership not in {"repo", "submodule"}
            or name in catalog
        ):
            raise ValueError("catalog manifest is invalid")
        catalog[name] = {"source": source, "ownership": ownership}
    return catalog


def frontmatter_tokens(skill_dir: Optional[Path]) -> Optional[int]:
    """Estimate catalog cost from the frontmatter actually exposed by the linker."""
    if skill_dir is None:
        return None
    chars = 0
    fences = 0
    try:
        for line in (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip() == "---":
                fences += 1
                if fences == 2:
                    break
            elif fences == 1:
                chars += len(line) + 1
    except OSError:
        return None
    return chars // 4


def walk_objects(value: Any) -> Iterator[Mapping[str, Any]]:
    if isinstance(value, dict):
        yield value
        for child in value.values():
            yield from walk_objects(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_objects(child)


def walk_strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for child in value.values():
            yield from walk_strings(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_strings(child)


def json_records(files: Sequence[Path]) -> Iterator[Any]:
    """Yield valid JSONL records while discarding malformed content immediately."""
    for entry_path in files:
        try:
            with entry_path.open(encoding="utf-8", errors="ignore") as handle:
                for line in handle:
                    try:
                        yield json.loads(line)
                    except json.JSONDecodeError:
                        continue
        except OSError:
            continue


def scan_claude(files: Sequence[Path]) -> Counter:
    """Count only Claude Skill calls and explicit slash-command event tags."""
    counts: Counter = Counter()
    for record in json_records(files):
        for item in walk_objects(record):
            if item.get("name") == "Skill" and isinstance(item.get("input"), dict):
                skill = item["input"].get("skill")
                if isinstance(skill, str):
                    counts[skill] += 1
        for text in walk_strings(record):
            counts.update(CLAUDE_COMMAND_RE.findall(text))
    return counts


def scan_codex(files: Sequence[Path]) -> Counter:
    """Count SKILL.md reads only within Codex function_call records."""
    counts: Counter = Counter()
    for record in json_records(files):
        for item in walk_objects(record):
            if item.get("type") != "function_call":
                continue
            for text in walk_strings(item):
                counts.update(CODEX_SKILL_PATH_RE.findall(text))
    return counts


def transcript_window(root: Path, as_of: datetime, primary_start: datetime, sensitivity_start: datetime) -> Tuple[Dict[str, Any], List[Path], List[Path]]:
    """Return only aggregate availability metadata plus file handles for scanning."""
    available = root.is_dir()
    candidates: List[Tuple[datetime, Path]] = []
    if available:
        try:
            iterator = root.rglob("*.jsonl")
            for entry_path in iterator:
                try:
                    observed = datetime.fromtimestamp(entry_path.stat().st_mtime, tz=UTC)
                except OSError:
                    continue
                if observed <= as_of:
                    candidates.append((observed, entry_path))
        except OSError:
            available = False
            candidates = []

    candidates.sort(key=lambda item: item[0])
    earliest = candidates[0][0] if candidates else None
    primary = [entry_path for observed, entry_path in candidates if observed >= primary_start]
    sensitivity = [entry_path for observed, entry_path in candidates if observed >= sensitivity_start]
    metadata = {
        "available": available,
        "files_available": len(candidates),
        "files_scanned_primary": len(primary),
        "files_scanned_sensitivity": len(sensitivity),
        "earliest_available": timestamp_text(earliest),
        "coverage_complete": bool(available and earliest is not None and earliest <= primary_start),
    }
    return metadata, primary, sensitivity


def source_freshness(repo_root: Path, source: Optional[str], ownership: str, primary_start: datetime) -> str:
    """Classify age conservatively; unknown history is protected, never actionable."""
    source_path = safe_source_path(repo_root, source)
    if source_path is None or not (source_path / "SKILL.md").is_file() or ownership == "submodule":
        return "unknown-age"
    try:
        inside_repo = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if inside_repo.returncode != 0 or inside_repo.stdout.strip() != "true":
            return "unknown-age"
        relative = source_path.relative_to(repo_root)
        history = subprocess.run(
            ["git", "-C", str(repo_root), "log", "--diff-filter=A", "--follow", "--format=%ct", "--", str(relative)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError, ValueError):
        return "unknown-age"
    if history.returncode != 0:
        return "unknown-age"
    timestamps = history.stdout.split()
    if not timestamps:
        return "new"
    try:
        first_added = datetime.fromtimestamp(int(timestamps[-1]), tz=UTC)
    except ValueError:
        return "unknown-age"
    return "new" if first_added >= primary_start else "established"


def counts_for(name: str, claude: Counter, codex: Counter) -> Dict[str, int]:
    claude_count = int(claude[name])
    codex_count = int(codex[name])
    return {"claude": claude_count, "codex": codex_count, "total": claude_count + codex_count}


def disposition_for(name: str, resolved: bool, coverage_complete: bool, freshness: str, primary_count: int) -> Tuple[str, Optional[str]]:
    """Return a review-only disposition; this function never authorizes catalog changes."""
    if name == "using-superpowers":
        return "measurement-limited", "native-limited"
    if not resolved:
        return "insufficient-evidence", "not-in-current-catalog"
    if not coverage_complete:
        return "insufficient-evidence", "incomplete-history"
    if freshness in {"new", "unknown-age"}:
        return "retain", freshness
    if primary_count >= 3:
        return "retain", None
    if primary_count >= 1:
        return "marginal-review", "one-or-two-recorded-uses"
    return "candidate-follow-up", "owner-review-before-any-catalog-change"


def build_report(repo_root: Path, catalog: Mapping[str, Mapping[str, str]], claude_dir: Path, codex_dir: Path, as_of: datetime, since_days: int, sensitivity_days: int) -> Dict[str, Any]:
    primary_start = as_of - timedelta(days=since_days)
    sensitivity_start = as_of - timedelta(days=sensitivity_days)
    claude_coverage, claude_primary, claude_sensitivity = transcript_window(
        claude_dir, as_of, primary_start, sensitivity_start
    )
    codex_coverage, codex_primary, codex_sensitivity = transcript_window(
        codex_dir, as_of, primary_start, sensitivity_start
    )
    coverage_complete = bool(claude_coverage["coverage_complete"] and codex_coverage["coverage_complete"])
    claude_primary_counts = scan_claude(claude_primary)
    codex_primary_counts = scan_codex(codex_primary)
    claude_sensitivity_counts = scan_claude(claude_sensitivity)
    codex_sensitivity_counts = scan_codex(codex_sensitivity)

    matrix: List[Dict[str, Any]] = []
    for name, trigger, overlap in CANDIDATE_PROFILES:
        entry = catalog.get(name)
        resolved = entry is not None
        source = entry["source"] if entry else None
        ownership = entry["ownership"] if entry else "unresolved"
        skill_dir = safe_source_path(repo_root, source)
        freshness = source_freshness(repo_root, source, ownership, primary_start)
        primary_counts = counts_for(name, claude_primary_counts, codex_primary_counts)
        sensitivity_counts = counts_for(name, claude_sensitivity_counts, codex_sensitivity_counts)
        disposition, protection_reason = disposition_for(
            name, resolved, coverage_complete, freshness, primary_counts["total"]
        )
        row: Dict[str, Any] = {
            "name": name,
            "catalog_status": "resolved" if resolved else "not-in-current-catalog",
            "source": source,
            "ownership": ownership,
            "catalog_token_cost": frontmatter_tokens(skill_dir),
            "freshness": freshness,
            "counts": {"primary": primary_counts, "sensitivity": sensitivity_counts},
            "trigger_rationale": trigger,
            "overlap_rationale": overlap,
            "disposition": disposition,
        }
        if protection_reason is not None:
            row["protection_reason"] = protection_reason
        matrix.append(row)

    return {
        "schema_version": 1,
        "as_of": timestamp_text(as_of),
        "windows": {"primary_days": since_days, "sensitivity_days": sensitivity_days},
        "coverage": {
            "complete": coverage_complete,
            "claude": claude_coverage,
            "codex": codex_coverage,
        },
        "measurement_policy": {
            "event_types": ["claude-skill", "claude-slash", "codex-function-call-skill-read"],
            "transcript_retention": "aggregate-counters-only",
            "catalog_change_authorization": "none",
        },
        "decision_matrix": matrix,
    }


def render_text(report: Mapping[str, Any]) -> str:
    """Render the same aggregate-only report without emitting filesystem details."""
    lines = [
        "Skill usage audit (measurement only)",
        "as-of: {0}".format(report["as_of"]),
        "coverage complete: {0}".format("yes" if report["coverage"]["complete"] else "no"),
        "",
        "PRIMARY  SENSITIVITY  DISPOSITION           SKILL",
    ]
    for row in report["decision_matrix"]:
        lines.append(
            "{0:>7}  {1:>11}  {2:<20}  {3}".format(
                row["counts"]["primary"]["total"],
                row["counts"]["sensitivity"]["total"],
                row["disposition"],
                row["name"],
            )
        )
    lines.extend(
        [
            "",
            "This is a measurement-only decision matrix; no catalog change is authorized.",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=default_repo_root())
    parser.add_argument("--catalog-manifest", type=Path)
    parser.add_argument("--skills-root", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--claude-dir", type=Path, default=Path.home() / ".claude/projects")
    parser.add_argument("--codex-dir", type=Path, default=Path.home() / ".codex/sessions")
    parser.add_argument("--as-of", type=parse_utc_timestamp, required=True)
    parser.add_argument("--since-days", type=int, default=90)
    parser.add_argument("--sensitivity-days", type=int, default=30)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.since_days <= 0 or args.sensitivity_days <= 0:
        parser.error("window lengths must be positive")
    if args.sensitivity_days > args.since_days:
        parser.error("--sensitivity-days cannot exceed --since-days")
    if args.skills_root is not None:
        inferred_root = args.skills_root.resolve().parent
        if args.repo_root.resolve() != default_repo_root().resolve() and args.repo_root.resolve() != inferred_root:
            parser.error("--skills-root must belong to --repo-root")
        args.repo_root = inferred_root
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    try:
        catalog = load_catalog_manifest(repo_root, args.catalog_manifest)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    report = build_report(
        repo_root,
        catalog,
        args.claude_dir,
        args.codex_dir,
        args.as_of,
        args.since_days,
        args.sensitivity_days,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
