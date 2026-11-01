# Implement Cycle

One iteration of an implement lane: take one bead, finish it, and then either
land it or hand its PR to the review lane. The worktree is gone by the end of
the iteration. `CO` below is the absolute path of the `beads-coordinator`
package, and `WK` the absolute path of the `beads-worker` package. Resolve
both from this file's location, never from your cwd. Resolve `REPO_ROOT` with
the command in `../SKILL.md` → "Launch".

## 1. Select

1. **Rank.** Run this on every wake. It reports capacity and the recovery
   candidates as well as the queue:

   ```bash
   uv run "$CO/scripts/rank_ready_work.py" --repo-root "$REPO_ROOT" \
     --coordinator "$LOOPER_ID" [--scope-epic <epic-id>]
   ```

   If the envelope is `fatal`, dispatch nothing this wake.
2. **Recover the dead.** Release each `unowned_claims` row and clear each
   `stranded` row with the guarded commands in
   `$CO/references/runtime-and-safety.md` → "Parallel Coordinators" → "Adopt
   the dead, guarded". Exit 13 means a peer got there first, so move on.
   `orphaned_blocked` rows are not yours to adopt. Kind `pr` belongs to the
   review lane. Kind `gate` is blocked by status alone, which only the owner
   lifts, so it goes in the report under "Needs owner".
3. **Corrections first.** Start here only while `capacity.free > 0`. A
   returned PR is the outcome closest to done. The ranker leaves these beads
   out of its queue, so you have to ask for them:

   ```bash
   bd ready --label review-correction --unassigned --json \
     | jq -c '[.[] | {id, title, created_at}] | sort_by(.created_at)'
   ```

4. **Otherwise take ranked rows top-down**, preferring the epic you just
   worked (`$CO/references/coordinator-loop.md` → "Step 2: Select Next
   Issue"). Gate each row before claiming it:
   - Apply the dispatch-readiness gate (`$CO/references/coordinator-loop.md`
     → "Dispatch readiness gate"). If a row fails, stamp it under that
     section's "Stamp every rejection" idempotence rules, then take the next
     row. This is the one write a looper makes on a bead it does not hold, so
     guard it:

     ```bash
     bd --actor "$LOOPER_ID" update <id> --if-assignee '' --add-label needs-shaping \
       --append-notes "dispatch-readiness <YYYY-MM-DD> $LOOPER_ID: missing <field list>" --json
     ```

     The stamp takes the bead out of every lane's queue and lists it under
     `excluded.needs_shaping_standalone` or its epic's `needs_shaping`.
     Shaping belongs to `beads-writer`; never re-scope a bead to keep the lane
     busy.
   - Skip a row whose required model tier exceeds this session's model.
   - Never claim an epic. Report `childless_epics` for the writer and leave
     Team Lead mode to coordinators.
5. **Claim** with `bd --actor "$LOOPER_ID" update <id> --claim --json`. Check
   that `assignee` is you, then write the stall heartbeat note
   (`$CO/references/runtime-and-safety.md` → "Claiming And The Stall
   Heartbeat").

## 2. Worktree

**Clear leftovers.** Once you hold the claim, any worktree or local branch
still named `agent/<id>` was left by an earlier holder that crashed or failed
to tear down. Never delete work that exists nowhere else:

```bash
cd "$REPO_ROOT"
OLD=$(git worktree list --porcelain | awk -v b="branch refs/heads/agent/$ID" '/^worktree /{p=$2} $0==b{print p}')
UNPUBLISHED=$( { [ -n "$OLD" ] && git -C "$OLD" status --porcelain; \
  git log --oneline "agent/$ID" --not --remotes 2>/dev/null; } | head -1)
```

- **Unpublished work: quarantine it.** Move it onto a recovery branch, so
  `agent/<id>` becomes free:

  ```bash
  TS=$(date -u +%Y%m%dT%H%M%SZ)
  if [ -n "$OLD" ]; then git -C "$OLD" switch -c "recovery/$ID-$TS"   # keeps uncommitted changes
    git worktree move "$OLD" ".worktrees/recovery/$ID-$TS"
  else git branch -m "agent/$ID" "recovery/$ID-$TS"; fi
  ```

  Then run `git branch -D "agent/$ID"` if the branch still exists, and add a
  note on the bead naming the recovery branch.
- **Nothing unpublished: remove it.** Run
  `bd worktree remove "$OLD" --force` when there is a worktree, then
  `git branch -D "agent/$ID"`. The `--force` is safe here because the check
  above just proved there is nothing to lose.

**Create the worktree.** Base it on the previous holder's pushed branch when
one exists, and otherwise on `origin/<base>`:

```bash
WORKTREE_PATH="$REPO_ROOT/.worktrees/parallel-agents/$ID"
(cd "$REPO_ROOT" && bd worktree create ".worktrees/parallel-agents/$ID" --branch "agent/$ID")
cd "$WORKTREE_PATH"
BASE=$(git remote show origin | sed -n 's/.*HEAD branch: //p')
if git ls-remote --exit-code --heads origin "agent/$ID" >/dev/null; then
  git fetch origin "agent/$ID" && git reset --hard FETCH_HEAD   # resume the previous holder's state
else
  git fetch origin "$BASE" && git reset --hard "origin/$BASE"    # never inherit REPO_ROOT's HEAD
fi
```

**Check for an open PR.** If one exists for `agent/<id>` and the bead is not a
`review-correction`, an earlier holder opened it and crashed before handing
it off. Find it with
`gh pr list --head "agent/$ID" --state open --json number,url,headRefOid`.
Confirm that its head is your `HEAD`, then skip straight to the
`completed-pr-opened` hand-off in step 4.

## 3. Work

Read `$WK/SKILL.md` once per session and run its Phases 1-4 with `ISSUE_ID`,
`WORKTREE_PATH`, and `REPO_ROOT`. Every later bead in this session counts as a
lane continuation under that skill's "Lane Continuation" rules. For a
`review-correction` bead, read the `[review-correction]` note and set the
worker's correction-mode variables from it. `CORRECTION_THREADS_JSON` comes
from the PR's unresolved threads.

Keep your liveness fresh through long work. Renew the stall heartbeat and the
registration (`register --wake-minutes` sized to cover the next stretch) at
the runtime-and-safety checkpoints: after the full gate, after each verifier
round, and after any long `gh` wait. These are liveness writes, not lifecycle
writes. Without them, a busy looper reads as dead, and a peer adopts its bead.

When the full gate passes, run the verifier
([`adversarial-verifier.md`](adversarial-verifier.md)). Then choose the
hand-off path with the worker's Phase 5 table and emit its Worker Report with
`$WK/scripts/emit_worker_report.py`. That report is the input to step 4.

If a decision-shaped blocker comes up, it is yours to decide
(`../../../references/decision-autonomy.md`): record the `[decision]` and keep
working. Only an external or hard-gated blocker ends the work early.

## 4. Reconcile By Worker Status

Verify each reported side effect (PR, pushed branch, head SHA) before any
mutation, as in `$CO/references/coordinator-loop.md` → "Step 7: Monitor
Workers". Classify discoveries before any `bd create` under "Discovery
classification" there. Create follow-up beads unassigned.

**Ordering rule.** A release (`--assignee ''`) is always the iteration's last
write, and it always comes after step 5's tear-down. The next holder must
find `agent/<id>` free. If the release exits 13, a peer adopted the bead
because it believed you were dead. Touch nothing more and report `lost-claim`.
Your work is already pushed or quarantined.

### `completed-direct-merge-candidate`

- **Base behind a merge queue.** Open a `queue-direct` PR and enable
  auto-merge, as in Step 7. Tear down, then hand the original off without a
  review bead:

  ```bash
  bd --actor "$LOOPER_ID" update <id> --if-assignee "$LOOPER_ID" --status blocked \
    --external-ref "gh-pr:$PR_NUMBER" --add-label pr-review --assignee '' --json
  ```

- **Otherwise, fast-forward from the worktree.** Never land through
  `REPO_ROOT`:

  ```bash
  git fetch origin "$BASE"
  git merge-base --is-ancestor "origin/$BASE" HEAD || git rebase "origin/$BASE"
  git push origin "HEAD:refs/heads/$BASE"     # fast-forward only; a rejection means a peer landed first
  ```

  If the base had moved, the pushed head is no longer the verified head. In
  that case, re-run the full gate after the rebase and force-push
  `agent/<id>` with `--force-with-lease` before pushing to the base. If the
  rebase conflicts, resolve it and also re-run the verifier. A rejected push
  means another lane landed first: retry once. If the second push also loses,
  or the base refuses direct pushes, take the PR path below.

  After the push lands, close the bead with a `--reason` naming the merged
  SHA, delete the remote branch, tear down, and run
  `bd --actor "$LOOPER_ID" epic close-eligible --json`.

### `completed-pr-opened`

The review lane must be able to take the PR unit as a whole. Wire it
completely while you still hold the original:

1. Run the review-bead dedupe check (`$CO/references/coordinator-loop.md` →
   "0a. Dedupe review beads"). If a canonical review bead already exists,
   reuse it and skip the next step.
2. Create the review bead `blocked`, labelled, and unassigned in one call. A
   bead that starts `open` sits in the ready queue until it is updated, so a
   peer could claim it as implementation work. Take the title, description,
   design, and acceptance text verbatim from the "Safe PR-review bead creation
   pattern" in that file's Step 0c:

   ```bash
   REVIEW_ID=$(bd --actor "$LOOPER_ID" create "Conduct a thorough code review of ${PR_URL}" \
     --description="…" --design="…" --acceptance="…" \
     -t task -p 1 -s blocked -l pr-review,pr-review-task --validate --json | jq -r '.id // .[0].id')
   bd --actor "$LOOPER_ID" update "$REVIEW_ID" --append-notes "Review target bead: ${ID}. PR: ${PR_URL}"
   bd --actor "$LOOPER_ID" dep add <id> "$REVIEW_ID"
   ```

3. Tear down (step 5), then release the original:

   ```bash
   bd --actor "$LOOPER_ID" update <id> --if-assignee "$LOOPER_ID" --status blocked \
     --external-ref "gh-pr:$PR_NUMBER" --add-label pr-review --assignee '' --json
   ```

**Correction pass.** The PR and its review bead already exist, so create
neither again. Restore the review gate, tear down, and then release:

```bash
bd --actor "$LOOPER_ID" dep add <id> <review-id>
bd --actor "$LOOPER_ID" update <id> --if-assignee "$LOOPER_ID" --status blocked \
  --remove-label review-correction --add-label pr-review --assignee '' \
  --append-notes "[review-correction] pushed head=<sha>" --json
```

### `blocked-awaiting-coordinator`

You are the coordinator for this bead, so triage `Blockers-JSON` as in
`$CO/references/coordinator-loop.md` → Step 7:

- For a decision without a hard gate, decide it, record it, and resume work.
- File each external or hard-gated blocker as a bead. Hard gates use the
  escalation format. Wire the original to depend on each one.
- Preserve recovery state. Push the branch if it holds useful work, and
  quarantine local-only work as in step 2.
- Tear down, then release the original as `--status open --assignee ''`,
  guarded by `--if-assignee`. Its new dependencies keep it out of `bd ready`
  until they close. It then returns to the queue on its own, and the next
  holder resumes from `origin/agent/<id>`.

### `invalid-runtime-context`

Tear down, unclaim the bead, and report. If it happens twice in a row, stop
the loop, because the environment is broken, not the bead.

## 5. Tear Down

```bash
cd "$REPO_ROOT"
test -z "$(git -C "$WORKTREE_PATH" status --porcelain)" \
  && test -z "$(git -C "$WORKTREE_PATH" log --oneline HEAD --not --remotes)" \
  || echo "unpublished work: quarantine it as in step 2"
bd worktree remove ".worktrees/parallel-agents/$ID" --force   # safe: the check above just passed
git branch -D "agent/$ID"
```

Delete the local branch on every path. A later holder recreates it from the
remote.

Build artifacts follow their bead. On a direct merge, copy the receipts to the
bead's evidence and delete the `<id>-*` artifact directories now. On a PR
hand-off, leave them: the review lane deletes them when it closes the bead.

## Local-State Beads

A `scope:local-state` bead changes state that git does not track and that
exists only in `REPO_ROOT`: `.beads/` leftovers, caches, local databases. No
worktree can reach it, so the ranker leaves it out. A lane takes one only when
the owner names it, in the launch prompt or on the bead. Then:

- Claim it by id, as in step 1.
- Do any tracked-file part in a worktree as usual. It lands, or opens a PR,
  like any other change.
- Do the local-state part in `REPO_ROOT`, touching only the paths the bead
  names. Move, never delete: rename each target to
  `<path>.retired-<UTC timestamp>`, so the owner can restore it. Never touch
  tracked files, the checkout, or the live Dolt data, and never run
  `bd init`.
- Record every move on the bead (`[local-state] moved <path> -> <new path>`),
  then run the bead's verification.
- Close the bead only once its tracked-file part, if any, has merged.
