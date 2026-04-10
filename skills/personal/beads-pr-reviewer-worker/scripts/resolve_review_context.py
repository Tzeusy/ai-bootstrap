#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys


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


def first_record(payload):
    if isinstance(payload, list):
        if not payload:
            raise RuntimeError("empty JSON payload")
        return payload[0]
    return payload


def extract_original_id(description):
    patterns = [
        r"Original implementation bead:\s*([^\s.]+)",
        r"Review target bead:\s*([^\s.]+)",
    ]
    matches = []
    for pattern in patterns:
        match = re.search(pattern, description or "")
        if match:
            matches.append(match.group(1))
    matches = [match for match in matches if match]
    return sorted(set(matches))


def extract_pr_number(description):
    match = re.search(r"https://github\.com/[^/\s]+/[^/\s]+/pull/([0-9]+)", description or "")
    return match.group(1) if match else ""


def main():
    parser = argparse.ArgumentParser(description="Resolve original bead and PR context for a pr-review-task bead.")
    parser.add_argument("--issue-id", required=True, help="Review bead id, for example bd-123")
    args = parser.parse_args()

    try:
        review_payload = run_json(["bd", "show", args.issue_id, "--json"])
        review = first_record(review_payload)
        review_description = review.get("description") or ""

        extracted_ids = extract_original_id(review_description)
        if len(extracted_ids) > 1:
            fail("ambiguous-original-id", "multiple original bead ids found in review-bead description", candidates=extracted_ids)

        original_id = extracted_ids[0] if extracted_ids else ""
        fallback_matches = []
        if not original_id:
            candidates = run_json(["bd", "list", "--label", "pr-review", "--json", "--limit", "0"])
            for candidate in candidates:
                if candidate.get("id") == args.issue_id:
                    continue
                dependencies = candidate.get("dependencies") or []
                if any(dep.get("depends_on_id") == args.issue_id for dep in dependencies):
                    fallback_matches.append(candidate.get("id") or "")

            fallback_matches = sorted({match for match in fallback_matches if match})
            if len(fallback_matches) > 1:
                fail("ambiguous-original-id", "multiple original beads depend on the review bead", candidates=fallback_matches)
            if len(fallback_matches) == 1:
                original_id = fallback_matches[0]

        if not original_id:
            fail("missing-original-id", "unable to resolve original implementation bead")

        original_payload = run_json(["bd", "show", original_id, "--json"])
        original = first_record(original_payload)
        external_ref = original.get("external_ref") or ""
        pr_number = ""
        match = re.fullmatch(r"gh-pr:([0-9]+)", external_ref)
        if match:
            pr_number = match.group(1)

        if not pr_number:
            pr_number = extract_pr_number(review_description)

        if not pr_number:
            fail("missing-pr-number", "unable to resolve PR number", original_id=original_id)

        owner_repo = run(["gh", "repo", "view", "--json", "nameWithOwner", "-q", ".nameWithOwner"]).strip()
        owner, repo = owner_repo.split("/", 1)
        pr = run_json([
            "gh",
            "pr",
            "view",
            pr_number,
            "--json",
            "number,url,state,isDraft,mergeStateStatus,reviewDecision,headRefName,baseRefName,mergedAt,headRefOid",
        ])

        output = {
            "ok": True,
            "issue_id": args.issue_id,
            "original_id": original_id,
            "pr_number": int(pr_number),
            "pr_url": pr.get("url"),
            "owner": owner,
            "repo": repo,
            "owner_repo": owner_repo,
            "head_branch": pr.get("headRefName"),
            "base_branch": pr.get("baseRefName"),
            "head_sha": pr.get("headRefOid"),
            "state": pr.get("state"),
            "is_draft": pr.get("isDraft"),
            "merge_state_status": pr.get("mergeStateStatus"),
            "review_decision": pr.get("reviewDecision"),
            "merged_at": pr.get("mergedAt"),
        }
        json.dump(output, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    except RuntimeError as exc:
        fail("command-failed", str(exc))
    except Exception as exc:
        fail("unexpected-error", str(exc))


if __name__ == "__main__":
    main()
