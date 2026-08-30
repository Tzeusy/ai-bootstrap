#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Emit a compact, validated Beads PR-reviewer handoff report."""

from __future__ import annotations

import argparse
import json
import sys


STATUSES = {
    "merged-pr",
    "corrections-required",
    "pushed-review-fixes",
    "blocked-awaiting-coordinator",
    "invalid-runtime-context",
}
YES_NO = {"yes", "no"}
RISK_TIERS = {"high", "standard", "low"}
GATE_RESULTS = {"pass", "fail", "not-run"}
GATES = ("lint", "typecheck", "tests")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit a validated machine-readable Beads PR Reviewer Report."
    )
    parser.add_argument("--status", required=True, choices=sorted(STATUSES))
    parser.add_argument("--issue-id", required=True)
    parser.add_argument("--original-issue", default="unknown")
    parser.add_argument("--branch", default="n/a")
    parser.add_argument("--worktree-path", required=True)
    parser.add_argument("--head-commit", default="n/a")
    parser.add_argument("--reviewed-head-commit", default="n/a")
    parser.add_argument("--reviewer-identity", default="unknown")
    parser.add_argument("--risk-tier", default="standard", choices=sorted(RISK_TIERS))
    parser.add_argument("--branch-pushed", default="no", choices=sorted(YES_NO))
    parser.add_argument("--pr-url", default="n/a")
    parser.add_argument("--pr-number", default="n/a")
    parser.add_argument("--base-branch", default="n/a")
    parser.add_argument("--merge-authorized", default="no", choices=sorted(YES_NO))
    parser.add_argument("--merge-performed", default="no", choices=sorted(YES_NO))
    parser.add_argument("--pr-closed", default="no", choices=sorted(YES_NO))
    parser.add_argument("--summary", required=True)
    parser.add_argument("--quality-gate", action="append", default=[])
    parser.add_argument("--review-actions-json", default="[]")
    parser.add_argument("--discovered-follow-ups-json", default="[]")
    parser.add_argument("--blockers-json", default="[]")
    return parser.parse_args()


def json_array(raw: str, name: str) -> list[object]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{name} must be valid JSON: {exc}") from exc
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a JSON array")
    return value


def quality_gates(items: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"quality gate {item!r} must use key=value")
        name, value = (part.strip() for part in item.split("=", 1))
        if name not in GATES:
            raise ValueError(f"unknown quality gate {name!r}")
        if value not in GATE_RESULTS:
            raise ValueError(f"invalid quality-gate result {value!r}")
        result[name] = value
    return {name: result.get(name, "not-run") for name in GATES}


def validate(
    args: argparse.Namespace, actions: list[object], blockers: list[object]
) -> None:
    if args.merge_performed == "yes" and args.merge_authorized != "yes":
        raise ValueError("Merge-Performed: yes requires Merge-Authorized: yes")
    if args.status == "merged-pr":
        if args.merge_authorized != "yes" or args.merge_performed != "yes":
            raise ValueError("merged-pr requires authorized, performed merge")
        if args.pr_url == "n/a" or args.pr_number == "n/a":
            raise ValueError("merged-pr requires PR metadata")
        if args.reviewed_head_commit == "n/a" or args.head_commit != args.reviewed_head_commit:
            raise ValueError("merged-pr requires matching exact head and reviewed head")
        if blockers:
            raise ValueError("merged-pr cannot contain blockers")
    elif args.status == "corrections-required":
        if args.merge_performed == "yes":
            raise ValueError("corrections-required cannot report a merge")
        if not any(
            isinstance(action, dict) and action.get("action") == "correction-required"
            for action in actions
        ):
            raise ValueError("corrections-required needs a correction-required action")
    elif args.status == "pushed-review-fixes":
        if args.branch_pushed != "yes" or args.merge_performed == "yes":
            raise ValueError("pushed-review-fixes requires a pushed, unmerged branch")
    elif args.status == "blocked-awaiting-coordinator":
        if not blockers:
            raise ValueError("blocked-awaiting-coordinator requires a blocker")
        if args.merge_performed == "yes":
            raise ValueError("blocked-awaiting-coordinator cannot report a merge")
    elif args.status == "invalid-runtime-context":
        if args.merge_performed == "yes" or args.pr_closed == "yes":
            raise ValueError("invalid-runtime-context cannot mutate PR state")


def main() -> int:
    args = parse_args()
    try:
        gates = quality_gates(args.quality_gate)
        actions = json_array(args.review_actions_json, "Review-Actions-JSON")
        follow_ups = json_array(
            args.discovered_follow_ups_json, "Discovered-Follow-Ups-JSON"
        )
        blockers = json_array(args.blockers_json, "Blockers-JSON")
        validate(args, actions, blockers)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    lines = [
        f"## PR Reviewer Report: {args.issue_id}",
        "",
        f"Status: {args.status}",
        f"Issue: {args.issue_id}",
        f"Original-Issue: {args.original_issue}",
        f"Branch: {args.branch}",
        f"Worktree: {args.worktree_path}",
        f"Head-Commit: {args.head_commit}",
        f"Reviewed-Head-Commit: {args.reviewed_head_commit}",
        f"Reviewer-Identity: {args.reviewer_identity}",
        f"Risk-Tier: {args.risk_tier}",
        f"Branch-Pushed: {args.branch_pushed}",
        f"PR-URL: {args.pr_url}",
        f"PR-Number: {args.pr_number}",
        f"Base-Branch: {args.base_branch}",
        f"Merge-Authorized: {args.merge_authorized}",
        f"Merge-Performed: {args.merge_performed}",
        f"PR-Closed: {args.pr_closed}",
        f"Summary: {args.summary}",
        "",
        "Quality-Gates:",
        *[f"- {name}: {gates[name]}" for name in GATES],
    ]
    for name, value in (
        ("Review-Actions-JSON", actions),
        ("Discovered-Follow-Ups-JSON", follow_ups),
        ("Blockers-JSON", blockers),
    ):
        lines.extend(("", f"{name}:", "```json", json.dumps(value, separators=(",", ":")), "```"))
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
