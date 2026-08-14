# PR Review Reconciliation

Load this file when cleanup needs to inspect Beads tied to a GitHub pull
request and report findings for the coordinator.

**The coordinator is the sole mutation authority.** Cleanup is report-only: it
does not alter Beads, review wiring, GitHub threads, worktrees, or branches.

Run the report-only [`cleanup_scan.py`](../scripts/cleanup_scan.py) first. Its
nested `beads-pr-review-normalization/v1` report invokes the canonical
`resolve_review_context.py` helper for review tasks. Cleanup never reparses a
description, falls back to an ad hoc PR reference, or truncates dotted child
IDs.

Immediately before any coordinator action, re-verify the current PR, Beads,
assignee, and heartbeat state. Scan findings are evidence, not authorization.
A nonzero delegated normalizer or malformed PR evidence is a partial
manual-triage result even when its stdout parses.
A zero-exit delegated envelope must provide list-shaped `errors`, `findings`,
and `self_heal_candidates` collections whose status matches its evidence.
Otherwise cleanup downgrades the nested and outer reports to partial manual
triage and preserves no actionable recommendation.
Each retained finding or candidate must also pass its type-appropriate opaque
identity, positive PR number, PR-state, and recommendation semantics. Missing,
malformed, or incompatible evidence adds the sanitized
`invalid-normalizer-evidence` error and preserves only `manual-triage`. A
well-shaped `success` envelope with no sanitized findings or candidates is
normalized to `empty`, never retained as a misleading success-without-work.
`dedupe-review-task` must identify a distinct duplicate, never self-link its
review ID to the canonical review ID. `review-wiring-current` and
`self-heal-original-wiring` candidates must cross-link to a matching resolved
canonical `pr-review-task` finding for the same original ID and PR. Any failed
cross-link is invalid normalizer evidence and remains partial manual triage.
A source relation that is self or equivocal—including an original ID reused as
a review, canonical-review, or duplicate ID—adds
`invalid-normalizer-evidence` and preserves only partial manual triage.
Direct `bd show` evidence for a blocker or worktree must be singleton and must
echo its requested ID; otherwise cleanup reports partial manual triage. Cleanup
also enforces collection-wide role binding: a review or canonical-review ID may
map to only one original/PR scope, and each such scope may have only one
canonical review ID. Distinct canonical-plus-duplicate review tasks remain
valid when their IDs and roles are unambiguous.

## Pass 2: Blocked Original Beads With `pr-review`

Use the normalizer findings for blocked original beads. The original owns the
canonical `external_ref=gh-pr:<N>`; a missing or malformed reference is a
manual-triage finding.

| PR state | Report recommendation for coordinator Step 0 |
|---|---|
| `MERGED` | close the appropriate Beads and perform post-closure hygiene after fresh verification |
| `CLOSED` and not merged | reopen/re-triage the original after fresh verification |
| `OPEN` with no canonical review task | self-heal review wiring after fresh verification |
| Unknown, malformed, or query failure | `manual-triage` |

## Pass 3: Blocked `pr-review-task` Review Beads

The canonical normalizer includes all non-closed review tasks, including active
ones, when selecting the oldest deterministic canonical task by parsed creation
chronology. Invalid creation timestamps fail closed to partial manual triage;
it never compares raw timestamp text. It preserves dotted child IDs and reports
duplicates without changing them.
A list-shaped but malformed `pr-review-task` inventory is still incomplete:
the normalizer reports partial manual triage and gives every self-heal candidate
the `manual-triage` recommendation until a clean inventory can be collected.

| PR state | Report recommendation for coordinator Step 0 |
|---|---|
| `MERGED` | close the review and original as appropriate after fresh verification |
| `CLOSED` and not merged | close/reopen/re-triage as appropriate after fresh verification |
| `OPEN` | wait for cooldown or dispatch the canonical task |
| Unresolved context or state | `manual-triage` |

## Missing Review Wiring

If an original is blocked on an open PR but no dedicated review task can be
resolved, record the finding in the report. The coordinator loop owns any
subsequent self-heal or dedupe decision.
