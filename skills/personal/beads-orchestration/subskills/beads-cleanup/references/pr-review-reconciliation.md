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
