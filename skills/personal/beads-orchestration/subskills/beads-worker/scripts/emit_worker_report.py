# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import argparse
import json
import sys


VALID_STATUSES = {
    "completed-pr-opened",
    "completed-direct-merge-candidate",
    "blocked-awaiting-coordinator",
    "invalid-runtime-context",
}
VALID_HANDOFF_PATHS = {
    "pr-required",
    "direct-merge-candidate",
    "blocked-awaiting-coordinator",
    "invalid-runtime-context",
}
VALID_BRANCH_PUSHED = {"yes", "no"}
VALID_RECOVERY_STATES = {"branch-pushed", "local-only", "no-code-changes"}
VALID_GATE_RESULTS = {"pass", "fail", "not-run"}
EXPECTED_GATES = ("lint", "typecheck", "tests")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Emit a validated machine-readable Beads worker report.",
    )
    parser.add_argument("--status", required=True, choices=sorted(VALID_STATUSES))
    parser.add_argument("--issue-id", required=True)
    parser.add_argument("--branch")
    parser.add_argument("--worktree-path", required=True)
    parser.add_argument("--head-commit", required=True)
    parser.add_argument("--branch-pushed", required=True, choices=sorted(VALID_BRANCH_PUSHED))
    parser.add_argument("--handoff-path", required=True, choices=sorted(VALID_HANDOFF_PATHS))
    parser.add_argument("--pr-url", default="n/a")
    parser.add_argument("--pr-number", default="n/a")
    parser.add_argument("--base-branch", default="n/a")
    parser.add_argument("--review-reason", default="n/a")
    parser.add_argument("--recovery-state", default="no-code-changes")
    parser.add_argument("--resume-condition", default="n/a")
    parser.add_argument("--failing-command", default="n/a")
    parser.add_argument("--remote-branch", default="n/a")
    parser.add_argument("--dirty-worktree", default="unknown")
    parser.add_argument("--unpushed-commits", default="unknown")
    parser.add_argument("--summary", required=True)
    parser.add_argument("--quality-gate", action="append", default=[])
    parser.add_argument("--changes", action="append", default=[])
    parser.add_argument("--tests", action="append", default=[])
    parser.add_argument("--discovered-follow-ups-json", default="[]")
    parser.add_argument("--blockers-json", default="[]")
    return parser.parse_args()


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def parse_json_array(raw: str, field_name: str) -> list[object]:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field_name} must be valid JSON: {exc}") from exc
    if not isinstance(value, list):
        raise ValueError(f"{field_name} must be a JSON array")
    return value


def parse_quality_gates(raw_gates: list[str]) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for item in raw_gates:
        if "=" not in item:
            raise ValueError(f"Quality gate '{item}' must use key=value format")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key not in EXPECTED_GATES:
            raise ValueError(
                f"Unknown quality gate '{key}'. Expected only: {', '.join(EXPECTED_GATES)}"
            )
        if value not in VALID_GATE_RESULTS:
            raise ValueError(
                f"Invalid result '{value}' for quality gate '{key}'. "
                f"Expected one of: {', '.join(sorted(VALID_GATE_RESULTS))}"
            )
        parsed[key] = value

    for gate in EXPECTED_GATES:
        parsed.setdefault(gate, "not-run")
    return parsed


def validate_args(args: argparse.Namespace, blockers: list[object]) -> None:
    expected_branch = f"agent/{args.issue_id}"
    if args.branch is None:
        args.branch = expected_branch

    if args.recovery_state not in VALID_RECOVERY_STATES:
        raise ValueError(
            f"Recovery-State must be one of: {', '.join(sorted(VALID_RECOVERY_STATES))}"
        )

    if args.status == "completed-pr-opened":
        if args.handoff_path != "pr-required":
            raise ValueError("completed-pr-opened requires Handoff-Path: pr-required")
        if args.branch_pushed != "yes":
            raise ValueError("completed-pr-opened requires Branch-Pushed: yes")
        if args.pr_url == "n/a":
            raise ValueError("completed-pr-opened requires PR-URL")
        if args.pr_number == "n/a":
            raise ValueError("completed-pr-opened requires PR-Number")
    elif args.status == "completed-direct-merge-candidate":
        if args.handoff_path != "direct-merge-candidate":
            raise ValueError(
                "completed-direct-merge-candidate requires Handoff-Path: direct-merge-candidate"
            )
        if args.branch_pushed != "yes":
            raise ValueError("completed-direct-merge-candidate requires Branch-Pushed: yes")
        if args.pr_url != "n/a" or args.pr_number != "n/a":
            raise ValueError(
                "completed-direct-merge-candidate requires PR-URL and PR-Number to be n/a"
            )
    elif args.status == "blocked-awaiting-coordinator":
        if args.handoff_path != "blocked-awaiting-coordinator":
            raise ValueError(
                "blocked-awaiting-coordinator requires Handoff-Path: blocked-awaiting-coordinator"
            )
        if not blockers:
            raise ValueError("blocked-awaiting-coordinator requires at least one blocker")
        if args.failing_command == "n/a":
            raise ValueError("blocked-awaiting-coordinator requires Failing-Command")
    elif args.status == "invalid-runtime-context":
        if args.handoff_path != "invalid-runtime-context":
            raise ValueError(
                "invalid-runtime-context requires Handoff-Path: invalid-runtime-context"
            )


def main() -> int:
    args = parse_args()

    try:
        gates = parse_quality_gates(args.quality_gate)
        follow_ups = parse_json_array(args.discovered_follow_ups_json, "Discovered-Follow-Ups-JSON")
        blockers = parse_json_array(args.blockers_json, "Blockers-JSON")
        validate_args(args, blockers)
    except ValueError as exc:
        return fail(str(exc))

    changes = args.changes or ["- none recorded"]
    tests = args.tests or ["- none recorded"]

    report = "\n".join(
        [
            f"## Worker Report: {args.issue_id}",
            "",
            f"Status: {args.status}",
            f"Issue: {args.issue_id}",
            f"Branch: {args.branch}",
            f"Worktree: {args.worktree_path}",
            f"Head-Commit: {args.head_commit}",
            f"Branch-Pushed: {args.branch_pushed}",
            f"Handoff-Path: {args.handoff_path}",
            f"PR-URL: {args.pr_url}",
            f"PR-Number: {args.pr_number}",
            f"Base-Branch: {args.base_branch}",
            f"Review-Reason: {args.review_reason}",
            f"Recovery-State: {args.recovery_state}",
            f"Resume-Condition: {args.resume_condition}",
            f"Summary: {args.summary}",
            "",
            "Recovery-Details:",
            f"- Failing-Command: {args.failing_command}",
            f"- Remote-Branch: {args.remote_branch}",
            f"- Dirty-Worktree: {args.dirty_worktree}",
            f"- Unpushed-Commits: {args.unpushed_commits}",
            "",
            "Quality-Gates:",
            f"- lint: {gates['lint']}",
            f"- typecheck: {gates['typecheck']}",
            f"- tests: {gates['tests']}",
            "",
            "Changes:",
            *[f"- {item}" for item in changes],
            "",
            "Tests:",
            *[f"- {item}" for item in tests],
            "",
            "Discovered-Follow-Ups-JSON:",
            "```json",
            json.dumps(follow_ups, separators=(",", ":")),
            "```",
            "",
            "Blockers-JSON:",
            "```json",
            json.dumps(blockers, separators=(",", ":")),
            "```",
        ]
    )

    print(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
