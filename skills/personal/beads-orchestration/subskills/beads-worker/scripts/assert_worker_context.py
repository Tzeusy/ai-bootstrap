# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import argparse
import json
import os
import sys


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that a Beads worker is running in the expected worktree and branch.",
    )
    parser.add_argument("--worktree-path", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--issue-id", required=True)
    parser.add_argument("--current-path", required=True)
    parser.add_argument("--branch", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected_branch = f"agent/{args.issue_id}"
    current_path = os.path.realpath(args.current_path)
    worktree_path = os.path.realpath(args.worktree_path)
    repo_root = os.path.realpath(args.repo_root)
    branch = args.branch.strip()
    reasons: list[str] = []

    if current_path != worktree_path:
        reasons.append("current-path-does-not-match-worktree-path")
    if current_path == repo_root:
        reasons.append("current-path-equals-repo-root")
    if not branch:
        reasons.append("branch-is-empty")
    if branch in {"main", "master"}:
        reasons.append("branch-is-protected-base")
    if branch and branch != expected_branch:
        reasons.append(f"branch-must-equal-{expected_branch}")

    payload = {
        "status": "ok" if not reasons else "invalid-runtime-context",
        "issue_id": args.issue_id,
        "expected_branch": expected_branch,
        "branch": branch,
        "current_path": current_path,
        "worktree_path": worktree_path,
        "repo_root": repo_root,
        "reasons": reasons,
    }
    print(json.dumps(payload, separators=(",", ":")))
    return 0 if not reasons else 1


if __name__ == "__main__":
    sys.exit(main())
