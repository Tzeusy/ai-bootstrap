#!/usr/bin/env python3
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


def main():
    parser = argparse.ArgumentParser(description="Prepare a PR head branch for reviewer work.")
    parser.add_argument("--base-branch", required=True)
    parser.add_argument("--head-branch", required=True)
    args = parser.parse_args()

    try:
        run(["git", "fetch", "origin", args.base_branch, args.head_branch])
        run(["git", "checkout", "-B", args.head_branch, f"origin/{args.head_branch}"])
        rebase = run(["git", "rebase", f"origin/{args.base_branch}"], allow_failure=True)
        if rebase.returncode != 0:
            run(["git", "rebase", "--abort"], allow_failure=True)
            output = {
                "ok": False,
                "status": "rebase-conflict",
                "error": rebase.stderr.strip() or "rebase failed",
                "base_branch": args.base_branch,
                "head_branch": args.head_branch,
            }
            json.dump(output, sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
            sys.exit(1)

        beads_diff = run_stdout(["git", "diff", f"origin/{args.base_branch}...HEAD", "--", ".beads/"]).strip()
        stripped_beads_divergence = False
        pushed_cleanup_commit = False

        if beads_diff:
            run(["git", "checkout", f"origin/{args.base_branch}", "--", ".beads/"])
            dirty = run(["git", "status", "--porcelain"]).stdout.strip()
            if dirty:
                run(["git", "add", ".beads/"])
                run(["git", "commit", "-m", "fix: remove .beads divergence from feature branch"])
                stripped_beads_divergence = True
                push = run(["git", "push", "--force-with-lease", "origin", args.head_branch], allow_failure=True)
                if push.returncode != 0:
                    output = {
                        "ok": False,
                        "status": "blocked",
                        "error": push.stderr.strip() or "failed to push cleanup commit",
                        "base_branch": args.base_branch,
                        "head_branch": args.head_branch,
                        "stripped_beads_divergence": stripped_beads_divergence,
                    }
                    json.dump(output, sys.stdout, indent=2, sort_keys=True)
                    sys.stdout.write("\n")
                    sys.exit(1)
                pushed_cleanup_commit = True

        output = {
            "ok": True,
            "status": "ready",
            "base_branch": args.base_branch,
            "head_branch": args.head_branch,
            "stripped_beads_divergence": stripped_beads_divergence,
            "pushed_cleanup_commit": pushed_cleanup_commit,
        }
        json.dump(output, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    except Exception as exc:
        output = {
            "ok": False,
            "status": "blocked",
            "error": str(exc),
            "base_branch": args.base_branch,
            "head_branch": args.head_branch,
        }
        json.dump(output, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
