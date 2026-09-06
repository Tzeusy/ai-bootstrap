# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys


def git_worktree_identity(path: str) -> tuple[str, str, str] | None:
    """Return canonical worktree identity and branch without inherited redirects."""
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    try:
        result = subprocess.run(
            [
                "git",
                "--no-optional-locks",
                "-C",
                path,
                "rev-parse",
                "--path-format=absolute",
                "--show-toplevel",
                "--git-common-dir",
                "--abbrev-ref",
                "HEAD",
            ],
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            check=False,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None

    lines = result.stdout.splitlines()
    if result.returncode != 0 or len(lines) != 3:
        return None
    return os.path.realpath(lines[0]), os.path.realpath(lines[1]), lines[2].strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate that a Beads worker is running in the expected Git worktree.",
    )
    parser.add_argument("--worktree-path", required=True)
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--issue-id", required=True)
    parser.add_argument("--current-path", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    expected_branch = f"agent/{args.issue_id}"
    current_path = os.path.realpath(args.current_path)
    worktree_path = os.path.realpath(args.worktree_path)
    repo_root = os.path.realpath(args.repo_root)
    process_cwd = os.path.realpath(os.getcwd())
    reasons: list[str] = []

    if process_cwd != current_path:
        reasons.append("process-cwd-does-not-match-current-path")
    if current_path != worktree_path:
        reasons.append("current-path-does-not-match-worktree-path")
    if current_path == repo_root:
        reasons.append("current-path-equals-repo-root")
    repo_identity = git_worktree_identity(repo_root)
    worktree_identity = git_worktree_identity(worktree_path)
    branch = worktree_identity[2] if worktree_identity is not None else ""
    if repo_identity is None:
        reasons.append("repo-root-git-identity-unverifiable")
    elif repo_identity[0] != repo_root:
        reasons.append("repo-root-is-not-repository-root")
    if worktree_identity is None:
        reasons.append("worktree-git-identity-unverifiable")
    elif worktree_identity[0] != worktree_path:
        reasons.append("worktree-path-is-not-worktree-root")
    if (
        repo_identity is not None
        and worktree_identity is not None
        and repo_identity[1] != worktree_identity[1]
    ):
        reasons.append("worktree-is-not-owned-by-repo-root")
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
