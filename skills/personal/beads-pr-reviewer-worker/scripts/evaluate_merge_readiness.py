#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from typing import Any

from review_text_policy import validate_review_text


THREADS_QUERY = """
query($owner:String!, $repo:String!, $number:Int!, $after:String) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$number) {
      reviewThreads(first:100, after:$after) {
        nodes {
          id
          isResolved
          comments(last:1) {
            nodes {
              body
            }
          }
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
}
""".strip()

ALLOWED_MERGE_STATES = {"CLEAN", "HAS_HOOKS", "UNSTABLE"}


def fail(code, message, **extra):
    payload = {"ok": False, "error_code": code, "error": message}
    payload.update(extra)
    print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
    sys.exit(1)


def run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "command failed")
    return result.stdout


def run_json(cmd):
    return json.loads(run(cmd))


def review_thread_closure_state(owner, repo, pr_number):
    total = 0
    threads: list[dict[str, Any]] = []
    after = None
    while True:
        cmd = [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={THREADS_QUERY}",
            "-F",
            f"owner={owner}",
            "-F",
            f"repo={repo}",
            "-F",
            f"number={pr_number}",
        ]
        if after:
            cmd.extend(["-F", f"after={after}"])
        payload = run_json(cmd)
        review_threads = payload["data"]["repository"]["pullRequest"]["reviewThreads"]
        threads.extend(review_threads["nodes"])
        if not review_threads["pageInfo"]["hasNextPage"]:
            break
        after = review_threads["pageInfo"]["endCursor"]

    total = sum(1 for node in threads if not node["isResolved"])
    non_terminal_resolved = []
    for node in threads:
        comments = node.get("comments", {}).get("nodes", []) or []
        latest = comments[-1] if comments else None
        if node["isResolved"] and latest is not None:
            problems = validate_review_text(latest.get("body", ""), "reply")
            if problems:
                non_terminal_resolved.append(
                    {
                        "thread_id": node.get("id"),
                        "latest_comment_body": latest.get("body", ""),
                        "problems": problems,
                    }
                )
        elif node["isResolved"] and latest is None:
            non_terminal_resolved.append(
                {
                    "thread_id": node.get("id"),
                    "latest_comment_body": "",
                    "problems": ["resolved thread has no comments"],
                }
            )
    return total, non_terminal_resolved


def fetch_required_checks(pr_number):
    result = subprocess.run(
        ["gh", "pr", "checks", str(pr_number), "--required", "--json", "state"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        stderr = result.stderr.strip()
        # Repos without branch protection rules report no required checks.
        # Treat this as zero required checks rather than a hard failure.
        if "no required checks" in stderr.lower():
            return []
        fail("required-checks-unavailable", stderr or "unable to fetch required checks", pr_number=pr_number)
    return json.loads(result.stdout)


def main():
    parser = argparse.ArgumentParser(description="Evaluate whether a PR is merge-ready.")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr-number", required=True, type=int)
    args = parser.parse_args()

    try:
        pr = run_json([
            "gh",
            "pr",
            "view",
            str(args.pr_number),
            "--json",
            "state,isDraft,mergeStateStatus,reviewDecision,mergedAt,url,baseRefName,headRefName",
        ])
        unresolved, non_terminal_resolved = review_thread_closure_state(
            args.owner, args.repo, args.pr_number
        )
        checks = fetch_required_checks(args.pr_number)
    except RuntimeError as exc:
        fail("command-failed", str(exc), pr_number=args.pr_number)
    except Exception as exc:
        fail("unexpected-error", str(exc), pr_number=args.pr_number)

    required_non_green = sum(
        1
        for check in checks
        if check.get("state") not in {"SUCCESS", "SKIPPED", "NEUTRAL"}
    )

    reasons = []
    if pr.get("state") != "OPEN":
        reasons.append(f"state={pr.get('state')}")
    if pr.get("isDraft"):
        reasons.append("draft")
    if unresolved:
        reasons.append(f"unresolved_threads={unresolved}")
    if required_non_green:
        reasons.append(f"required_non_green={required_non_green}")
    if (pr.get("reviewDecision") or "REVIEW_REQUIRED") == "CHANGES_REQUESTED":
        reasons.append("review_decision=CHANGES_REQUESTED")
    if (pr.get("mergeStateStatus") or "UNKNOWN") not in ALLOWED_MERGE_STATES:
        reasons.append(f"merge_state={pr.get('mergeStateStatus') or 'UNKNOWN'}")
    if non_terminal_resolved:
        reasons.append(f"resolved_threads_missing_terminal_reply={len(non_terminal_resolved)}")

    output = {
        "ok": True,
        "pr_url": pr.get("url"),
        "state": pr.get("state"),
        "is_draft": pr.get("isDraft"),
        "merge_state_status": pr.get("mergeStateStatus"),
        "review_decision": pr.get("reviewDecision") or "REVIEW_REQUIRED",
        "merged_at": pr.get("mergedAt"),
        "base_branch": pr.get("baseRefName"),
        "head_branch": pr.get("headRefName"),
        "unresolved_count": unresolved,
        "resolved_threads_missing_terminal_reply": non_terminal_resolved,
        "required_non_green": required_non_green,
        "merge_ok": len(reasons) == 0,
        "reasons": reasons,
    }
    json.dump(output, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
