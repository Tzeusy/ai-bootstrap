#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys


THREAD_COUNT_QUERY = """
query($owner:String!, $repo:String!, $number:Int!, $after:String) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$number) {
      reviewThreads(first:100, after:$after) {
        nodes { isResolved }
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


def unresolved_count(owner, repo, pr_number):
    total = 0
    after = None
    while True:
        cmd = [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={THREAD_COUNT_QUERY}",
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
        total += sum(1 for node in review_threads["nodes"] if not node["isResolved"])
        if not review_threads["pageInfo"]["hasNextPage"]:
            return total
        after = review_threads["pageInfo"]["endCursor"]


def fetch_required_checks(pr_number):
    result = subprocess.run(
        ["gh", "pr", "checks", str(pr_number), "--required", "--json", "state"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        fail("required-checks-unavailable", result.stderr.strip() or "unable to fetch required checks", pr_number=pr_number)
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
        unresolved = unresolved_count(args.owner, args.repo, args.pr_number)
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
        "required_non_green": required_non_green,
        "merge_ok": len(reasons) == 0,
        "reasons": reasons,
    }
    json.dump(output, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
