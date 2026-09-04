#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Prepare a PR head branch for reviewer work.

Rebase policy (conflict-only): the head is rebased onto the latest base ONLY
when a dry three-way merge (`git merge-tree --write-tree`) reports a conflict,
or when `--force-rebase` is passed. A head that merges cleanly is reviewed and
merged as-is; GitHub's squash merge handles the integration. Unconditional
rebasing rewrote every PR head before review, which cancelled the worker's CI
run and forced the whole suite to re-run once per merge to the base.
"""
import argparse
import json
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


def decide_rebase(base_ref, force_rebase):
    """Return (should_rebase, reason).

    reasons: forced | conflict-with-base | not-needed | merge-tree-unsupported
    """
    if force_rebase:
        return True, "forced"
    probe = run(["git", "merge-tree", "--write-tree", base_ref, "HEAD"], allow_failure=True)
    if probe.returncode == 0:
        return False, "not-needed"
    if probe.returncode == 1:
        return True, "conflict-with-base"
    # Older git (< 2.38) has no --write-tree mode; fall back to the historical
    # unconditional rebase so the reviewer still gets a base-current head.
    return True, "merge-tree-unsupported"


def main():
    parser = argparse.ArgumentParser(description="Prepare a PR head branch for reviewer work.")
    parser.add_argument("--base-branch", required=True)
    parser.add_argument("--head-branch", required=True)
    parser.add_argument(
        "--force-rebase",
        action="store_true",
        help="Rebase onto the base branch even when the head merges cleanly.",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print what would be done without performing any git mutations.")
    args = parser.parse_args()

    if args.dry_run:
        emit({
            "ok": True,
            "status": "dry-run",
            "base_branch": args.base_branch,
            "head_branch": args.head_branch,
            "note": "no git mutations performed",
        })
        return

    base_ref = f"origin/{args.base_branch}"
    try:
        run(["git", "fetch", "origin", args.base_branch, args.head_branch])
        run(["git", "checkout", "-B", args.head_branch, f"origin/{args.head_branch}"])
        remote_head = run_stdout(["git", "rev-parse", f"origin/{args.head_branch}"]).strip()

        should_rebase, rebase_reason = decide_rebase(base_ref, args.force_rebase)
        rebased = False
        if should_rebase:
            rebase = run(["git", "rebase", base_ref], allow_failure=True)
            if rebase.returncode != 0:
                run(["git", "rebase", "--abort"], allow_failure=True)
                emit({
                    "ok": False,
                    "status": "rebase-conflict",
                    "error": rebase.stderr.strip() or "rebase failed",
                    "base_branch": args.base_branch,
                    "head_branch": args.head_branch,
                    "rebase_reason": rebase_reason,
                }, exit_code=1)
            rebased = True

        beads_diff = run_stdout(["git", "diff", f"{base_ref}...HEAD", "--", ".beads/"]).strip()
        stripped_beads_divergence = False
        pushed_cleanup_commit = False
        pushed_prepared_head = False

        if beads_diff:
            run(["git", "checkout", base_ref, "--", ".beads/"])
            dirty = run(["git", "status", "--porcelain"]).stdout.strip()
            if dirty:
                run(["git", "add", ".beads/"])
                run(["git", "commit", "-m", "fix: remove .beads divergence from feature branch"])
                stripped_beads_divergence = True

        local_head = run_stdout(["git", "rev-parse", "HEAD"]).strip()
        if stripped_beads_divergence or local_head != remote_head:
            push = run(
                ["git", "push", "--force-with-lease", "origin", args.head_branch],
                allow_failure=True,
            )
            if push.returncode != 0:
                emit({
                    "ok": False,
                    "status": "blocked",
                    "error": f"failed to push prepared head: {push.stderr.strip() or 'unknown push error'}",
                    "base_branch": args.base_branch,
                    "head_branch": args.head_branch,
                    "rebased": rebased,
                    "rebase_reason": rebase_reason,
                    "stripped_beads_divergence": stripped_beads_divergence,
                    "remote_head": remote_head,
                    "local_head": local_head,
                }, exit_code=1)
            pushed_prepared_head = True
            pushed_cleanup_commit = stripped_beads_divergence

        emit({
            "ok": True,
            "status": "ready",
            "base_branch": args.base_branch,
            "head_branch": args.head_branch,
            "rebased": rebased,
            "rebase_reason": rebase_reason,
            "stripped_beads_divergence": stripped_beads_divergence,
            "pushed_cleanup_commit": pushed_cleanup_commit,
            "pushed_prepared_head": pushed_prepared_head,
            "head_commit": local_head,
        })
    except Exception as exc:
        emit({
            "ok": False,
            "status": "blocked",
            "error": str(exc),
            "base_branch": args.base_branch,
            "head_branch": args.head_branch,
        }, exit_code=1)


if __name__ == "__main__":
    main()
