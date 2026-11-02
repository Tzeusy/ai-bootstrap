# Review Cycle

One iteration of the review lane. This lane is the sticky reviewer lane of
`../../beads-coordinator/references/runtime-and-safety.md` → "Review Risk
Tiers": one session reviews PR after PR, which keeps the repo context cached.
It owns PR state for every unit that implement lanes hand off. It never
authors fixes, so this mode has no reviewer-as-fixer path. `CO` is the
absolute path of the `beads-coordinator` package, and `RV` the absolute path
of the `beads-pr-reviewer-worker` package. Resolve `REPO_ROOT` with the
command in `../SKILL.md` → "Launch". Renew the stall heartbeat and the
registration through long reviews and CI waits, exactly as the implement
cycle's "Work" step says.

## 1. Sweep Every Unit You Hold

Run the canonical [Owner merge hold](../../beads-coordinator/references/coordinator-loop.md#owner-merge-hold)
inventory on every cycle, including frontier/final reports: all OPEN held PRs,
number/title/actual CI or UNKNOWN; none only after a successful empty read.
Foreign PRs are listed without adoption. Partial/error inventory is unavailable.
Apply its fresh guard immediately before every enqueue/merge/close, including
queue-direct re-enrollment and each retry; cached normalizer advice is never
authorization. Owner-performed terminal MERGED/CLOSED state still reconciles
normally even with the label remaining.

Start each wake with every original assigned to `LOOPER_ID`. Reconcile each
one against its PR using the `$CO/references/coordinator-loop.md` → "0b.
Reconcile blocked PR-review beads" table:

- **`MERGED`**: close the review bead (if any) and the original. Run that
  file's "Post-closure branch and worktree cleanup", copy receipts and delete
  the original's `<id>-*` artifacts, then run
  `bd --actor "$LOOPER_ID" epic close-eligible --json`.
- **`CLOSED` unmerged**: close the review bead as superseded, then release
  the original for re-triage. Remove `pr-review` while releasing, because the
  ranker never queues a bead that carries it:

  ```bash
  bd --actor "$LOOPER_ID" update <original-id> --if-assignee "$LOOPER_ID" --status open \
    --assignee '' --remove-label pr-review --append-notes "[pr-closed] <why>" --json
  ```

- **`OPEN` + `owner-merge`**: keep the canonical unit, report held-for-owner,
  and perform no enrollment/merge/close action, including queued/armed PRs.
  Preserve authorized correction/review work; no auto-dequeue, hold-only blocker
  or repeated review of the same head solely to merge. Check again next cycle;
  label removal resumes normal rules without another reset.
- **`OPEN`**: apply the table's queue rows after the fresh hold overlay. If
  the PR is queued, wait; it counts as near-term work for the wake cadence. If auto-merge is armed but
  the PR is not queued, clear the stale label and wait. A `queue-direct` PR
  that is not enrolled gets enrolled again. Any other held unit goes to step
  3 as a retry once its review bead has no open blockers.

## 2. Adopt Orphans

Some originals sit `blocked` with `gh-pr:<N>` and no live holder. Take them
over, then reconcile them as in step 1 within the same wake:

- **Unassigned, and the PR is `MERGED`, `CLOSED`, or labelled `queue-direct`:**

  ```bash
  bd --actor "$LOOPER_ID" update <original-id> --if-assignee '' --if-status blocked \
    --assignee "$LOOPER_ID" --json    # exit 13: a peer took it; skip
  ```

  An unassigned original whose `OPEN` PR has a review bead is not an orphan.
  It is a unit waiting for review, and step 3 handles it.
- **Held by a dead coordinator** under "Parallel Coordinators", whatever the
  PR state. The ranker lists these as `orphaned_blocked` rows of kind `pr`
  (`$CO/scripts/rank_ready_work.py`). Adopt each with
  `--if-assignee '<dead-id>'`. Adopt its review bead in the same way,
  original first and review bead second.

## 3. Select The Next Review

```bash
uv run "$CO/scripts/normalize_pr_review_state.py" --repo-root "$REPO_ROOT"
```

The scan is the inventory and the fail-closed gate. On `partial` or `fatal`,
review nothing this wake. Its recommendations do not authorize anything;
re-read the live `bd`/`gh` state before each mutation. A unit is reviewable
only when all of these hold. The fresh owner-hold overlay outranks dispatch
recommendations: a held PR may receive authorized review/corrections, but skip
same-head redispatch whose sole purpose is a merge attempt:

- Its PR is `OPEN`, not in a merge queue, and past the cooldown
  (`$CO/references/coordinator-loop.md` → "Constraints").
- It is handed off, or already yours:
  - **Handed off**: the original is `blocked`, labelled `pr-review`, and
    unassigned. The review bead is unassigned, or yours and labelled
    `corrections-requested`, which means the corrected head is back.
  - **Yours, as a retry**: the original and the `blocked` review bead are
    both yours, and the review bead has no open blockers.
- `capacity.free > 0`, as reported by `$CO/scripts/rank_ready_work.py`.

Take the oldest PR first. A high-tier PR (risk tiers above) needs a fresh
independent reviewer. Spawn a new `beads-pr-reviewer-worker` subagent for it
instead of reviewing in this session, and reconcile its report as your own.

## 4. Take The Unit

`--claim` refuses `blocked` beads (`../../../references/known-errors.md`).
Every take is therefore a guarded update:

```bash
# original: skip this line when it is already yours
bd --actor "$LOOPER_ID" update <original-id> --if-assignee '' --if-status blocked \
  --assignee "$LOOPER_ID" --json     # exit 13: skip the unit
# review bead: use --if-assignee "$LOOPER_ID" when it is already yours
bd --actor "$LOOPER_ID" update <review-id> --if-assignee '' --if-status blocked \
  --assignee "$LOOPER_ID" --status in_progress --json
bd --actor "$LOOPER_ID" update <review-id> --add-label review-running \
  --remove-label corrections-requested --json
```

If the review bead's update exits 13 after you took the original, release the
original again (`--if-assignee "$LOOPER_ID" --assignee ''`) and skip the
unit. Then write the stall heartbeat on the review bead.

## 5. Review

Create the review worktree, keyed by the review bead:

```bash
(cd "$REPO_ROOT" && bd worktree create ".worktrees/parallel-agents/<review-id>" --branch "agent/<review-id>")
```

Read `$RV/SKILL.md` once per session and run its Phases 1-5 there, passing
`MERGE_QUEUE` from the preflight. Apply the two-stage branch attestation
(`$CO/references/coordinator-loop.md` → "Step 6a: Bootstrap The Worker").

Skip Phase 2 step 1 of that skill, which unconditionally removes the
original's worktree. An implement lane tears its worktree down before it
releases, so normally no worktree holds `agent/<original-id>` here. If one
does, it belongs to whoever holds the original, which is you now. Clear it
with the implement cycle's "Clear leftovers" procedure, which quarantines
unpublished work rather than deleting it. The skill's report is the input to
step 6.

## 6. Reconcile By Reviewer Status

Follow `$CO/references/coordinator-loop.md` → "When a reviewer worker
completes", with these looper-specific differences:

- **`held-for-owner`**: freshly verify OPEN + held labels; require
  `Merge-Performed: no` and `PR-Closed: no`. Remove `review-running`, keep the
  canonical original/review relationship, and record the hold without a
  hold-only blocker. Retain Head-Commit, Reviewed-Head-Commit, Reviewer-Identity,
  Risk-Tier, Review-Actions-JSON and findings; actionable corrections still go
  to the implement lane, and exceptional pushed fixes still require a fresh
  independent reviewer. Do not repeat same-head review solely to merge.
  Recompute next cycle; if the owner already MERGED/CLOSED, use step 1 instead.
- **`merged-pr`**: confirm `MERGED`, then reconcile as in step 1.
- **`merge-queued`**: confirm the queue entry. Label the review bead
  `merge-queued`, remove `review-running`, and set it back to `blocked`. Keep
  holding both beads, and let step 1 close them on `MERGED`.
- **`corrections-required`**: return the work to the implement lanes.
  1. Tear down the review worktree **first**, so `agent/<original-id>` is
     free.
  2. While you still hold the original, update its `[review-cycle]` note in
     place. If the count reaches that note's two-correction checkpoint, apply
     the checkpoint now.
  3. Hand the original back, and keep the review bead so the same reviewer
     re-checks the corrected head:

  ```bash
  bd --actor "$LOOPER_ID" dep remove <original-id> <review-id>
  bd --actor "$LOOPER_ID" update <review-id> --status blocked \
    --remove-label review-running --add-label corrections-requested --json
  bd --actor "$LOOPER_ID" update <original-id> --if-assignee "$LOOPER_ID" --status open \
    --assignee '' --remove-label pr-review --add-label review-correction \
    --append-notes "[review-correction] pr=<N> review=<review-id> reviewed_head=<sha>" --json
  ```

- **`blocked-awaiting-coordinator`**:
  - If the author can fix the cause (a `rebase-conflict`, or a CI failure
    caused by the diff), hand it back as `corrections-required` and name the
    conflict or failure in the correction note.
  - Decide anything else that the decision-autonomy rules let you decide.
  - File external blockers as beads and run
    `bd --actor "$LOOPER_ID" dep add <review-id> <blocker-id>`. Keep the unit
    with the review bead `blocked`. Step 1 retries it once those blockers
    close.
- **`invalid-runtime-context`**: set the review bead back to `blocked` and
  remove `review-running`. Tear down, then release both beads with
  `--assignee ''`, and report. Stop the loop if it repeats.

## 7. Tear Down

Check that the review worktree is clean, then run
`bd worktree remove ".worktrees/parallel-agents/<review-id>" --force`. Delete
its local branches, `agent/<review-id>` and the local `agent/<original-id>`.
The reviewer pushes only prepared heads, so nothing in the worktree is
unpublished. Only the post-closure cleanup deletes the remote branch.
