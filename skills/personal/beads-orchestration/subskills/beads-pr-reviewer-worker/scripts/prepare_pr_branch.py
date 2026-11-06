#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Prepare an isolated review snapshot without rewriting the implementation branch.

A clean merge-tree probe preserves the author's head and its evidence. Conflicts,
unsupported probes, or tracker data in the patch return to the implementation
owner. The reviewer never takes over the author's worktree or force-pushes it.
"""
import argparse
import json
import re
import subprocess
import sys


def run(cmd, allow_failure=False):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0 and not allow_failure:
        raise RuntimeError(result.stderr.strip() or "command failed")
    return result


def run_stdout(cmd):
    return run(cmd).stdout


def emit(output, exit_code=0):
    json.dump(output, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    if exit_code:
        sys.exit(exit_code)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-branch", required=True)
    parser.add_argument("--head-branch", required=True)
    parser.add_argument("--review-id", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    common = {"base_branch": args.base_branch, "head_branch": args.head_branch,
              "review_branch": f"review/{args.review_id}", "rebased": False,
              "pushed_prepared_head": False}
    if not re.fullmatch(r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+(?:\.[0-9]+)*", args.review_id):
        emit({**common, "ok": False, "status": "blocked", "error": "invalid-review-id"}, 1)
    if args.dry_run:
        emit({**common, "ok": True, "status": "dry-run"})
        return
    try:
        if run_stdout(["git", "symbolic-ref", "--short", "HEAD"]).strip() != common["review_branch"]:
            raise RuntimeError("not-the-assigned-review-branch")
        if run_stdout(["git", "status", "--porcelain"]).strip():
            raise RuntimeError("review-worktree-is-dirty")
        # A clean index does not prove the branch is disposable: a session
        # may have committed recovery work without publishing it. Check its
        # provenance before fetch can move any remote-tracking references.
        if not run_stdout(["git", "branch", "-r", "--contains", "HEAD"]).strip():
            raise RuntimeError("review-head-has-no-published-provenance")
        base_ref, head_ref = f"origin/{args.base_branch}", f"origin/{args.head_branch}"
        for branch in (args.base_branch, args.head_branch):
            run(["git", "check-ref-format", "--branch", branch])
        run(["git", "fetch", "origin", args.base_branch, args.head_branch])
        remote_head = run_stdout(["git", "rev-parse", head_ref]).strip()
        run(["git", "checkout", "-B", common["review_branch"], remote_head])
        probe = run(["git", "merge-tree", "--write-tree", base_ref, "HEAD"], allow_failure=True)
        if probe.returncode:
            reason = "conflict-with-base" if probe.returncode == 1 else "merge-tree-unavailable"
            emit({**common, "ok": False, "status": "corrections-required" if probe.returncode == 1 else "blocked",
                  "error": reason, "head_commit": remote_head}, 1)
        if run_stdout(["git", "diff", f"{base_ref}...HEAD", "--", ".beads/"]).strip():
            emit({**common, "ok": False, "status": "corrections-required",
                  "error": "beads-divergence", "head_commit": remote_head}, 1)
        emit({**common, "ok": True, "status": "ready", "rebase_reason": "not-needed",
              "base_commit": run_stdout(["git", "rev-parse", base_ref]).strip(),
              "head_commit": remote_head,
              "head_tree": run_stdout(["git", "rev-parse", "HEAD^{tree}"]).strip()})
    except Exception as exc:
        emit({**common, "ok": False, "status": "blocked", "error": str(exc)}, 1)


if __name__ == "__main__":
    main()
