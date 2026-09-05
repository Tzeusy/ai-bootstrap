#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
import argparse
import json
import re
import subprocess
import sys


BEAD_ID_PATTERN = r"[a-z][a-z0-9]*(?:-[a-z0-9]+)+(?:\.[0-9]+)*"
BEAD_ID_RE = re.compile(rf"{BEAD_ID_PATTERN}")
MARKER_PATTERNS = [
    r"\b(?i:original implementation bead)(?:\s*:\s*|\s+)(\S+)",
    r"\b(?i:review target bead):\s*(\S+)",
]
TRAILING_ID_PUNCTUATION = ".,;:)"


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


class EvidenceError(Exception):
    """A compact, safe failure for malformed read-only tracker evidence."""

    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def requested_record(payload, issue_id):
    """Require ``bd show`` to return exactly the requested singleton record."""
    if not isinstance(payload, list) or len(payload) != 1 or not isinstance(payload[0], dict):
        raise EvidenceError("invalid-show-response", "bd show did not return one record")
    record = payload[0]
    if record.get("id") != issue_id:
        raise EvidenceError("mismatched-record-id", "bd show returned a different record")
    return record


def dependency_target_id(record):
    """Read one unambiguous current or legacy dependency target."""
    if not isinstance(record, dict):
        raise EvidenceError("invalid-dependency-row", "dependency evidence was not a record")
    has_current = "id" in record
    has_legacy = "depends_on_id" in record
    if not has_current and not has_legacy:
        raise EvidenceError("invalid-dependency-row", "dependency target id was missing")
    current = record.get("id")
    legacy = record.get("depends_on_id")
    if has_current and has_legacy and current != legacy:
        raise EvidenceError("invalid-dependency-row", "dependency target fields conflicted")
    candidate = current if has_current else legacy
    if not isinstance(candidate, str) or not BEAD_ID_RE.fullmatch(candidate):
        raise EvidenceError("invalid-dependency-row", "dependency target id was malformed")
    return candidate


def dependency_targets(records, source_id):
    """Validate dependency rows and preserve their unique target identities."""
    if not isinstance(records, list):
        raise EvidenceError("invalid-dependency-row", "dependencies were not a list")
    targets = []
    seen = set()
    for record in records:
        target = dependency_target_id(record)
        if target == source_id:
            raise EvidenceError("invalid-dependency-row", "dependency target was a self-link")
        if target in seen:
            raise EvidenceError("invalid-dependency-row", "dependency target was duplicated")
        seen.add(target)
        relation_type = record.get("dependency_type", record.get("type"))
        if relation_type != "parent-child":
            targets.append(target)
    return sorted(targets)


def extract_original_id(description):
    matches = []
    malformed = []
    for pattern in MARKER_PATTERNS:
        for match in re.finditer(pattern, description or ""):
            candidate = match.group(1)
            if BEAD_ID_RE.fullmatch(candidate):
                matches.append(candidate)
                continue

            if candidate[-1:] in TRAILING_ID_PUNCTUATION:
                candidate_without_punctuation = candidate[:-1]
                if BEAD_ID_RE.fullmatch(candidate_without_punctuation):
                    matches.append(candidate_without_punctuation)
                    continue

            # The whitespace marker form also matches generic prose such as
            # "original implementation bead before merging". A colon-delimited
            # marker or an ID-like invalid token is explicit and must fail closed.
            marker_prefix = match.group(0)[:-len(candidate)]
            candidate_core = candidate.rstrip(TRAILING_ID_PUNCTUATION)
            if ":" in marker_prefix or "-" in candidate_core or "." in candidate_core:
                malformed.append(candidate)

    return sorted(matches), sorted(set(malformed))


def extract_pr_number(description):
    match = re.search(r"https://github\.com/[^/\s]+/[^/\s]+/pull/([0-9]+)", description or "")
    return match.group(1) if match else ""


def main():
    parser = argparse.ArgumentParser(description="Resolve original bead and PR context for a pr-review-task bead.")
    parser.add_argument("--issue-id", required=True, help="Review bead id, for example bd-123")
    args = parser.parse_args()

    try:
        review_payload = run_json(["bd", "show", args.issue_id, "--json"])
        review = requested_record(review_payload, args.issue_id)
        review_description = review.get("description") or ""

        extracted_ids, malformed_ids = extract_original_id(review_description)
        if malformed_ids:
            fail(
                "malformed-original-id",
                "invalid original bead id found in review-bead description",
                candidates=malformed_ids,
            )
        if len(extracted_ids) > 1:
            fail("ambiguous-original-id", "multiple original bead ids found in review-bead description", candidates=extracted_ids)

        original_id = extracted_ids[0] if extracted_ids else ""

        # Fallback A (forward direction): coordinator-style linkage where the
        # REVIEW bead's own dependencies point AT the original implementation
        # bead (review --depends-on/blocks--> original) and the description
        # carries no marker. Follow those edges. Parent-child edges (epic
        # membership) are excluded; when several edges remain, prefer the target
        # that carries a gh-pr external_ref (the bead under review) so gate /
        # blocker dependencies do not masquerade as the original.
        if not original_id:
            review_deps = review.get("dependencies", [])
            dep_targets = dependency_targets(review_deps, args.issue_id)
            if dep_targets:
                pr_bearing = []
                for target in dep_targets:
                    try:
                        target_bead = requested_record(run_json(["bd", "show", target, "--json"]), target)
                    except EvidenceError:
                        raise
                    except RuntimeError:
                        continue
                    if re.fullmatch(r"gh-pr:[0-9]+", target_bead.get("external_ref") or ""):
                        pr_bearing.append(target)
                chosen = sorted(set(pr_bearing)) or dep_targets
                if len(chosen) > 1:
                    fail(
                        "ambiguous-original-id",
                        "multiple candidate original beads reachable via review-bead dependencies",
                        candidates=chosen,
                    )
                original_id = chosen[0]

        # Fallback B (reverse direction): another pr-review bead declares a
        # dependency pointing back AT this review bead.
        fallback_matches = []
        if not original_id:
            candidates = run_json(["bd", "list", "--label", "pr-review", "--json", "--limit", "0"])
            for candidate in candidates:
                if candidate.get("id") == args.issue_id:
                    continue
                dependencies = candidate.get("dependencies", [])
                if args.issue_id in dependency_targets(dependencies, candidate.get("id")):
                    fallback_matches.append(candidate.get("id") or "")

            fallback_matches = sorted({match for match in fallback_matches if match})
            if len(fallback_matches) > 1:
                fail("ambiguous-original-id", "multiple original beads depend on the review bead", candidates=fallback_matches)
            if len(fallback_matches) == 1:
                original_id = fallback_matches[0]

        if not original_id:
            fail("missing-original-id", "unable to resolve original implementation bead")

        original_payload = run_json(["bd", "show", original_id, "--json"])
        original = requested_record(original_payload, original_id)
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
    except EvidenceError as exc:
        fail(exc.code, str(exc))
    except RuntimeError as exc:
        fail("command-failed", str(exc))
    except Exception as exc:
        fail("unexpected-error", str(exc))


if __name__ == "__main__":
    main()
