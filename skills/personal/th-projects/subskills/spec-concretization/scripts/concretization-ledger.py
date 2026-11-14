#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.10"
# dependencies = []
# ///
"""concretization-ledger.py — the already-known ledger for a spec-concretization run.

Joins three sources the run must reconcile before filing or drafting anything:

  1. every requirement in the effective spec (main specs + non-archived active
     deltas), parsed by th-projects' own spec-trace-check.py so there is one
     parser, with scope, test-citation state, and active-change governance
     (signed or unsigned);
  2. every bead (all statuses), joined to requirements by the REQ- IDs on its
     `Requirements:` line (ownership) or anywhere else in its text (mention),
     and to capabilities by `spec_id` and `Audit-key: spec:<kind>:<cap>`;
  3. prior run state: active changes (tasks, linked beads, sign-off marker),
     the last convergence record, prior owner decisions and their states.

Output is compact and projected (one line per requirement / bead). Read the
Summary, then grep a slice's lines (`rg '^REQ-<cap>-'`) into dispatch prompts
as "already known" — never the whole ledger, never into the vision-gate brief. It does not judge
implementation — coverage of code is the run's semantic work.

Usage:
  uv run concretization-ledger.py <repo_root> [--tests-dir DIR ...]
      [--beads-json FILE | --no-beads] [--allow-parent-db]
      [--closed-limit N] [--json]

  --beads-json FILE   read beads from a `bd list --all --limit 0 --json` dump
                      instead of calling bd (fixtures, offline runs)
  --no-beads          spec-only ledger (no tracker); says so in the output
  --allow-parent-db   accept a beads database resolved outside <repo_root>
  --closed-limit N    unmatched recently closed beads to list (default 30)
  --json              machine-readable ledger instead of markdown

Exit 0 = ledger emitted. Exit 2 = missing tool, unreadable or malformed
source, empty or foreign tracker, or no openspec/ tree — the ledger never
guesses the backlog. Structural spec errors do not fail the ledger; they are
counted and the run is told to fix them via spec-trace-check.py first.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

CHECKER = Path(__file__).resolve().parents[3] / "scripts" / "spec-trace-check.py"
TEXT_FIELDS = ("title", "description", "design", "acceptance_criteria", "notes")
REQ_RE = re.compile(r"REQ[-_][a-z0-9]+(?:[-_][a-z0-9]+)*[-_]\d{3}(?!\d)", re.IGNORECASE)
OWNS_RE = re.compile(r"^\s*Requirements:\s*(.+)$", re.M)
VERIFIES_RE = re.compile(r"^\s*Verifies:\s*(.+)$", re.M)
AUDIT_KEY_RE = re.compile(r"Audit-key:\s*spec:([a-z-]+):([A-Za-z0-9._-]+)\S*")
NOTE_SHA_RE = re.compile(r"spec-concretization @([0-9a-f]{7,40})")
SIGNOFF_RE = re.compile(r"^\s*(?:\*\*)?Sign-off(?:\*\*)?:\s*\S", re.M)  # spec-format § Sign-off marker
DECISION_ROW_RE = re.compile(r"^\|\s*\d+\s*\|\s*`(concretize:[^`]+)`\s*\|[^|]*\|\s*([^|]+?)\s*\|", re.M)


class Refuse(Exception):
    """Fail-closed condition: exit 2 with a one-line reason."""


def load_checker():
    if not CHECKER.is_file():
        raise Refuse(f"missing {CHECKER}")
    spec = importlib.util.spec_from_file_location("spec_trace_check", CHECKER)
    module = importlib.util.module_from_spec(spec)
    sys.modules["spec_trace_check"] = module  # dataclasses resolve annotations here
    spec.loader.exec_module(module)
    return module


def norm(raw: str) -> str:
    tail = raw[4:].replace("_", "-").lower()
    return "REQ-" + tail


def proposal_signed(repo: Path, change: str) -> bool:
    proposal = repo / "openspec" / "changes" / change / "proposal.md"
    return proposal.is_file() and bool(SIGNOFF_RE.search(proposal.read_text(encoding="utf-8")))


def requirements(stc, repo: Path, tests_dirs):
    view = stc.capture_current(repo, tests_dirs)
    findings, reqs, _seen, _hashes = stc.analyze(repo, view)
    cited = {norm(m.group(0)) for path, raw in view.tests.items()
             for m in REQ_RE.finditer(stc.decode_body(raw, path))}
    openspec = repo / "openspec"
    rows = []
    for r in reqs:
        rel = Path(r.file).relative_to(openspec)
        change = rel.parts[1] if rel.parts[0] == "changes" else None
        rows.append({
            "id": r.req_id, "title": r.title, "capability": r.spec_name,
            "change": change, "op": r.op.split()[0], "scope": r.scope,
            "signed": proposal_signed(repo, change) if change else None,
            "tested": bool(r.req_id and r.req_id in cited),
            "path": str(Path("openspec") / rel), "line": r.line,
        })
    # A main requirement restated by an active MODIFIED/REMOVED delta is
    # governed by that delta only once the change is signed off.
    restated = {(x["capability"], x["title"]): x for x in rows
                if x["change"] and x["op"] in ("MODIFIED", "REMOVED")}
    for row in rows:
        if not row["change"]:
            d = restated.get((row["capability"], row["title"]))
            row["governed_by"] = (f'{d["change"]} ({d["op"]}, {"signed" if d["signed"] else "UNSIGNED — judge main text"})'
                                  if d else None)
    return rows, len(findings.errors), len(findings.warnings)


def run_bd(repo: Path, *argv):
    out = subprocess.run(["bd", *argv], cwd=repo, capture_output=True, text=True)
    if out.returncode != 0:
        raise Refuse(f"bd {' '.join(argv)} failed: {out.stderr.strip()[:300]}")
    return out.stdout


def load_beads(repo: Path, args):
    """Returns (beads, done_statuses, database_note)."""
    if args.beads_json:
        data = json.loads(Path(args.beads_json).read_text(encoding="utf-8"))
        done, where = {"closed"}, f"from {args.beads_json}"
    else:
        if not shutil.which("bd"):
            raise Refuse("bd CLI not found (use --beads-json or --no-beads)")
        where = run_bd(repo, "where").strip().splitlines()[0:1]
        where = where[0].strip() if where else ""
        if not args.allow_parent_db and not Path(where).resolve().is_relative_to(repo):
            raise Refuse(f"bd resolved database {where or '(none)'} outside {repo}; "
                         "pass --allow-parent-db if that backlog is really this repo's")
        raw = run_bd(repo, "list", "--all", "--limit", "0", "--json")
        if not raw.strip():
            raise Refuse("bd list returned no output; refusing to treat the backlog as empty")
        data = json.loads(raw)
        done = {"closed"}
        try:
            statuses = json.loads(run_bd(repo, "statuses", "--json"))
            done |= {s["name"] for s in statuses.get("custom_statuses") or []
                     if s.get("category") == "done"}
        except (Refuse, json.JSONDecodeError, AttributeError, KeyError):
            pass
    if not isinstance(data, list) or any(not isinstance(b, dict) or "id" not in b for b in data):
        raise Refuse("unexpected beads JSON shape: expected a list of objects with an id")
    return data, done, where


def links(bead, capabilities):
    text = "\n".join(str(bead.get(k) or "") for k in TEXT_FIELDS)
    owned = {norm(m.group(0)) for line in OWNS_RE.findall(text) for m in REQ_RE.finditer(line)}
    verifies = {norm(m.group(0)) for line in VERIFIES_RE.findall(text) for m in REQ_RE.finditer(line)}
    mentioned = {norm(m.group(0)) for m in REQ_RE.finditer(text)} - owned - verifies
    keys = AUDIT_KEY_RE.findall(text)
    spec_id = bead.get("spec_id") or ""
    caps = {c for c in capabilities
            if re.match(rf"^(\./)?openspec/(changes/[^/]+/)?specs/{re.escape(c)}(/|$)", spec_id)}
    caps |= {cap for _kind, cap in keys if cap in capabilities}
    change = re.match(r"^(\./)?openspec/changes/([^/]+)", spec_id)
    shas = NOTE_SHA_RE.findall(str(bead.get("notes") or ""))
    return {"owned": owned, "verifies": verifies, "mentioned": mentioned,
            "closeout": any(kind == "closeout" for kind, _ in keys),
            "keys": [f"spec:{k}:{c}" for k, c in keys], "caps": sorted(caps),
            "change": change.group(2) if change else None,
            "last_note": shas[-1] if shas else None}


def bead_line(b, extra="", noted=None):
    bits = [b["id"], str(b.get("status")), str(b.get("issue_type") or "")]
    if noted:
        bits.append(f"noted@{noted[:7]}")
    if b.get("parent"):
        bits.append(f'parent:{b["parent"]}')
    if b.get("assignee"):
        bits.append(f'@{b["assignee"]}')
    if b.get("labels"):
        bits.append("[" + ",".join(b["labels"]) + "]")
    return " ".join(x for x in bits if x) + f' {b.get("title", "")}{extra}'


def active_changes(repo: Path, change_beads):
    rows = []
    changes = repo / "openspec" / "changes"
    if not changes.is_dir():
        return rows
    for d in sorted(p for p in changes.iterdir() if p.is_dir() and p.name != "archive"):
        tasks = d / "tasks.md"
        text = tasks.read_text(encoding="utf-8") if tasks.is_file() else None
        rows.append({
            "change": d.name, "signed": proposal_signed(repo, d.name),
            "tasks_done": len(re.findall(r"^\s*- \[[xX]\]", text, re.M)) if text is not None else None,
            "tasks_total": len(re.findall(r"^\s*- \[[ xX]\]", text, re.M)) if text is not None else None,
            "beads": sorted(change_beads.get(d.name, [])),
        })
    return rows


def prior_state(repo: Path):
    reviews = sorted((repo / "docs" / "reviews").glob("*spec-concretization*.md"))
    record = []
    if reviews:
        record = [ln for ln in reviews[-1].read_text(encoding="utf-8").splitlines()
                  if re.match(r"^(Concretized|Rows|Actions|Notes|Owner gates):", ln)]
    qroot = Path(os.environ.get("QUESTIONNAIRE_STATE_ROOT", Path.home() / ".tmp" / "user-questionnaire"))
    name = repo.name
    decisions, packets = {}, []
    if qroot.is_dir():
        for d in sorted(qroot.glob(f"*{name}*spec-concretization*")):
            packets.append(str(d))
            packet = d / "packet.md" if d.is_dir() else d
            if packet.is_file():
                for did, state in DECISION_ROW_RE.findall(packet.read_text(encoding="utf-8")):
                    decisions[did] = f"{state} ({d.name})"  # later packets win
    return {"last_record_file": str(reviews[-1].relative_to(repo)) if reviews else None,
            "last_record": record, "questionnaires": packets, "decisions": decisions}


def build(args):
    repo = Path(args.repo_root).resolve()
    if not (repo / "openspec").is_dir():
        raise Refuse(f"no openspec/ under {repo}")
    stc = load_checker()
    try:
        reqs, errors, warnings = requirements(stc, repo, args.tests_dir or ())
    except ValueError as error:
        raise Refuse(str(error))
    capabilities = {r["capability"] for r in reqs}
    beads, done, where = ([], {"closed"}, "not loaded (--no-beads)") if args.no_beads else load_beads(repo, args)

    # One governing row per ID: an active delta restatement governs its main row.
    governing = {}
    for r in reqs:
        if r["id"] and (r["id"] not in governing or (r["change"] and r["signed"])):
            governing[r["id"]] = r
    owners = {rid: [] for rid in governing}
    mentions = {rid: [] for rid in governing}
    buckets = {"orphan": [], "closeout": [], "spec_linked": [], "other_live": [], "closed": []}
    change_beads = {}
    for b in beads:
        ln = links(b, capabilities)
        live = b.get("status") not in done
        tag = f'{b["id"]}({b.get("status")}{"," + b["issue_type"] if b.get("issue_type") == "epic" else ""}'
        tag += f',noted@{ln["last_note"][:7]})' if ln["last_note"] else ")"
        if ln["change"]:
            change_beads.setdefault(ln["change"], []).append(f'{b["id"]}({b.get("status")})')
        if ln["closeout"]:
            if live:
                buckets["closeout"].append(bead_line(b, "  verifies: " + " ".join(sorted(ln["verifies"] | ln["owned"]))))
            continue
        for rid in ln["owned"]:
            if rid in owners:
                owners[rid].append(tag)
        for rid in ln["mentioned"]:
            if rid in mentions:
                mentions[rid].append(tag)
        unknown = sorted(r for r in ln["owned"] | ln["mentioned"] if r not in governing)
        hit = any(r in governing for r in ln["owned"] | ln["mentioned"])
        if live and unknown:
            buckets["orphan"].append(bead_line(b, "  cites unknown: " + " ".join(unknown)))
        elif hit:
            continue
        elif live and (ln["keys"] or ln["caps"] or ln["change"]):
            link = " ".join(ln["keys"] + [f"spec:{c}" for c in ln["caps"]]
                            + ([f'change:{ln["change"]}'] if ln["change"] else []))
            buckets["spec_linked"].append(bead_line(b, f"  links: {link}", ln["last_note"]))
        elif live:
            buckets["other_live"].append(bead_line(b, noted=ln["last_note"]))
        else:
            buckets["closed"].append((b.get("closed_at") or "", bead_line(b)))
    buckets["closed"] = [line for _, line in sorted(buckets["closed"], reverse=True)[: args.closed_limit]]

    by_id = {b["id"]: b for b in beads}

    def live_owner(tag):
        bid = tag.split("(")[0]
        return by_id.get(bid, {}).get("status") not in done and by_id.get(bid, {}).get("issue_type") != "epic"

    overlaps = []
    for rid, tags in owners.items():
        live = [t for t in tags if live_owner(t)]
        parents = {by_id[t.split("(")[0]].get("parent") for t in live}
        if len(live) > 1 and not (len(live) == 2 and any(t.split("(")[0] in parents for t in live)):
            overlaps.append(f"{rid}: " + " ".join(live))
    for r in reqs:
        r["owners"] = owners.get(r["id"], []) if r["id"] and governing.get(r["id"]) is r else []
        r["mentions"] = mentions.get(r["id"], []) if r["id"] and governing.get(r["id"]) is r else []

    # Unsigned deltas are proposals: listed, never in scope.
    in_scope = [r for r in governing.values()
                if r["op"] not in ("REMOVED", "RENAMED") and r["scope"] == "v1-mandatory"
                and (not r["change"] or r["signed"])]
    statuses = {}
    for b in beads:
        statuses[b.get("status")] = statuses.get(b.get("status"), 0) + 1
    return {
        "repo": str(repo), "database": where,
        "summary": {
            "requirements": len(governing),
            "in_active_changes": sum(1 for r in governing.values() if r["change"]),
            "in_signed_changes": sum(1 for r in governing.values() if r["change"] and r["signed"]),
            "without_id": sum(1 for r in reqs if not r["id"] and r["op"] not in ("REMOVED", "RENAMED")),
            "v1_mandatory": len(in_scope),
            "v1_mandatory_untested": sum(1 for r in in_scope if not r["tested"]),
            "untested_main_no_live_owner": sum(
                1 for r in in_scope if not r["tested"] and not r["change"]
                and not any(live_owner(t) for t in owners.get(r["id"], []))),
            "spec_errors": errors, "spec_warnings": warnings,
            "beads": "not loaded (--no-beads)" if args.no_beads else statuses,
        },
        "requirements": reqs,
        "overlaps": overlaps,
        "orphan_beads": buckets["orphan"],
        "closeout_paths": buckets["closeout"],
        "spec_linked_beads": buckets["spec_linked"],
        "other_live_beads": buckets["other_live"],
        "recently_closed_unmatched": buckets["closed"],
        "active_changes": active_changes(repo, change_beads),
        "prior": prior_state(repo),
    }


def render(ledger):
    s = ledger["summary"]
    beads = s["beads"] if isinstance(s["beads"], str) else (
        " · ".join(f"{k} {v}" for k, v in sorted(s["beads"].items())) or "none")
    out = ["## Summary",
           f'Database: {ledger["database"]}',
           f'Requirements: {s["requirements"]} ({s["in_active_changes"]} in active changes: '
           f'{s["in_signed_changes"]} signed, {s["in_active_changes"] - s["in_signed_changes"]} unsigned; '
           f'{s["without_id"]} without ID) · v1-mandatory {s["v1_mandatory"]}, untested '
           f'{s["v1_mandatory_untested"]}, untested main-spec with no live owner {s["untested_main_no_live_owner"]}',
           f'Spec structure: {s["spec_errors"]} error(s), {s["spec_warnings"]} warning(s)'
           + (" — run spec-trace-check.py and fix errors before reconciling" if s["spec_errors"] else ""),
           f"Beads: {beads}", "", "## Requirements → beads"]
    for r in ledger["requirements"]:
        where = f'change:{r["change"]}{"" if r["signed"] else "(UNSIGNED)"} {r["op"]}' if r["change"] else "main"
        gov = f' governed-by:{r["governed_by"]}' if r.get("governed_by") else ""
        test = "tested" if r["tested"] else "UNTESTED"
        owns = " ".join(r["owners"]) or "-"
        ment = f' mentioned-by: {" ".join(r["mentions"])}' if r["mentions"] else ""
        out.append(f'{r["id"] or "(no ID)"} {r["scope"] or "(no scope)"} {test} {where}{gov} '
                   f'"{r["title"]}" {r["path"]}:{r["line"]} owners: {owns}{ment}')
    sections = [("IDs owned by more than one live bead (excluding epic/child)", ledger["overlaps"]),
                ("Open closeout paths (reuse before creating)", ledger["closeout_paths"]),
                ("Live beads citing unknown requirement IDs (orphans)", ledger["orphan_beads"]),
                ("Live beads linked to specs without a requirement ID", ledger["spec_linked_beads"]),
                ("Other live beads (fuzzy-match candidates)", ledger["other_live_beads"]),
                ("Recently closed, unmatched", ledger["recently_closed_unmatched"])]
    for title, rows in sections:
        out += ["", f"## {title}"] + (rows or ["(none)"])
    out += ["", "## Active changes"]
    for c in ledger["active_changes"]:
        tasks = "no tasks.md" if c["tasks_total"] is None else f'{c["tasks_done"]}/{c["tasks_total"]}'
        out.append(f'{c["change"]} {"signed" if c["signed"] else "UNSIGNED"} tasks: {tasks} '
                   f'beads: {" ".join(c["beads"]) or "-"}')
    if not ledger["active_changes"]:
        out.append("(none)")
    p = ledger["prior"]
    out += ["", "## Last convergence record"]
    out += ([p["last_record_file"]] + p["last_record"]) if p["last_record_file"] else ["(none — first run)"]
    out += ["", "## Prior owner decisions"]
    out += [f"{k} {v}" for k, v in sorted(p["decisions"].items())] or ["(none)"]
    return "\n".join(out)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("repo_root")
    ap.add_argument("--tests-dir", action="append")
    src = ap.add_mutually_exclusive_group()
    src.add_argument("--beads-json")
    src.add_argument("--no-beads", action="store_true")
    ap.add_argument("--allow-parent-db", action="store_true")
    ap.add_argument("--closed-limit", type=int, default=30)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    try:
        ledger = build(args)
    except (Refuse, json.JSONDecodeError, OSError, UnicodeDecodeError) as error:
        print(f"concretization-ledger: {error}", file=sys.stderr)
        return 2
    print(json.dumps(ledger, indent=1) if args.json else render(ledger))
    return 0


if __name__ == "__main__":
    sys.exit(main())
