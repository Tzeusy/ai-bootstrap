# Independent review cycle

Serve persistent outcome owners; do not take their implementation claims. Shared
[delivery policy](../../../references/delivery-model.md) owns content evidence and
per-member acceptance; [reviewer worker](../../beads-pr-reviewer-worker/SKILL.md)
owns substantive review and fail-closed merge readiness.

## Take a review

Look for canonical package-anchor review records. Dedupe by anchor/PR, never create
one per member. Acquire only the review bead with this actor and mark `review-running`;
implementation claims remain with their owner. For an unassigned blocked review,
use guarded acquisition (native `--claim` refuses blocked records):

```bash
bd --actor "$LOOPER_ID" update <review-id> --if-assignee '' \
  --if-status blocked --assignee "$LOOPER_ID" --status in_progress \
  --add-label review-running --json
```

Exit 13 loses the race and dispatches nothing. For your existing blocked review,
use your own assignee in the guard and continue the same reviewer. A live peer's
review claim cannot be taken. Register/count this review capacity using the existing
registry; recover dead review sessions under existing guarded liveness rules.

Resolve anchor manifest and PR; create a separate `review/<review-id>` worktree at
the published head. Never remove the implementation owner's worktree or check out
its branch here. Native reviewer bootstrap verifies repository identity and branch.
The preparation helper fetches a snapshot; actual conflicts go to the owner.

## Review and communicate

Use the worker's review phases. Check member acceptance, runtime claims, contracts,
callers and failure seams, not just diff formatting. Report every evidenced finding.
Reuse previous independent content verdicts when unchanged relevant content and
assumptions are proved; recheck affected deltas after corrections. Current merge
checks/labels/permissions remain time-sensitive. The receipt binds current head to
its fresh/reused content evidence; broad required final-tree CI still runs where
repository policy places it.

Send actionable findings directly to the existing implementation session in the
anchor packet. Keep same review record and session for rechecks. Notify its lifecycle
controller of state changes only; avoid relaying each comment through a coordinator.
A reviewer who authored semantic fixes cannot attest those changes independently.

## Reconcile review state

| Report | Action |
|---|---|
| corrections-required | Keep canonical review blocked, remove review-running, send findings to existing owner. Do not reopen/unassign original or remove its worktree. |
| merge-queued | Verify actual queue entry; mark review waiting, notify owner, resume on queue event. |
| held-for-owner | Preserve findings/content evidence, remove review-running; no merge/close/enqueue or hold-only blocker; notify dependent scope. |
| merged-pr | Notify owner with fresh MERGED/base/content evidence. Owner applies per-member closure; reviewer never closes all members from merge state alone. |
| pushed-review-fixes | Preserve recovery evidence; request another independent reviewer for authored content. |
| blocked-awaiting-coordinator | Send concrete external/hard gate to owner/controller; ordinary CI/conflict corrections go to implementer. |
| invalid-runtime-context | Preserve work, release only guarded own review claim to blocked; stop repeated invalid bootstrap. |

Every merge/queue/close action uses the current
[owner hold guard](../../beads-coordinator/references/coordinator-loop.md#owner-merge-hold),
required checks and independent current-head receipt. Failed/partial reads block
the action. No main-policy bypass for integration branches or grouped tracking.

Delete only the review snapshot after proving clean/no unpublished work; retain
review record, findings and affinity through corrections. Retire on independence
loss or demonstrated drift, with an explicit published handoff. Wait on events,
not repeated same-head reviews solely to attempt a held merge.
