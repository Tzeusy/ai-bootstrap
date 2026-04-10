---
name: beads-cleanup
description: Audit and repair beads state before coordinator work begins. Detects orphaned in_progress beads, stale review locks, merged/closed PRs with open beads, blocked beads whose blockers are resolved, and orphaned worktrees. Run at the start of every beads-coordinator loop.
---

# Beads Cleanup

## Overview

Audit all `in_progress` and `blocked` beads, detect inconsistent state caused by
killed workers, out-of-token failures, or lost context, and repair it. This skill
is a **read-heavy, write-careful** state reconciler — it never implements code,
only fixes bead metadata and cleans up git artifacts.

**Run this at the start of every `beads-coordinator` loop**, before discovering
or dispatching any work.

## Use This Skill When

- Starting a `beads-coordinator` session (mandatory first step)
- Resuming work after a crash, compaction, or session restart
- "clean up beads state" / "audit beads" / "fix stuck beads"
- Suspecting workers died without updating their beads

## Principles

1. **Read before write** — always verify external state (PR, worktree, branch)
   before mutating a bead.
2. **Log every mutation** — append a note explaining what was fixed and why.
3. **Conservative defaults** — when uncertain, leave the bead alone and append a
   note for human triage rather than making a wrong state transition.
4. **Idempotent** — running cleanup twice in a row produces no additional changes.
5. **Respect lease ownership** — a live foreign lease is a hard stop. Cleanup
   may mutate only when the lease is absent, expired, or clearly belongs to a
   dead session.

---

## Cleanup Procedure

Execute each pass in order. Collect a summary of all mutations for the final
report.

### Lease Guard (mandatory for every pass)

Before mutating any bead:
- inspect lease metadata if present
- if a live foreign lease exists, skip mutation for that bead
- do not treat mere ownership mismatch as stale
- only expired leases, missing leases, or clearly dead owners are eligible for
  cleanup mutation

This guard applies to all reopen, close, relabel, unblock, and release actions
below.

**Rig routing:** If running from outside the target rig (e.g., from the mayor
or town root), pass `--rig <rig>` to `bd list` and `bd ready` calls so they
query the correct project database. Commands that take an existing bead ID
(`bd update`, `bd close`, `bd show`, `bd dep`) auto-route via the ID prefix.
**Note:** `bd search`, `bd blocked`, `bd count`, and `bd query` do **not**
support `--rig` — use `bd list --rig <rig>` with filters as a workaround.

### Pass 1: Stale `in_progress` beads (abandoned workers)

Workers that were killed (OOT, pkill, crash) leave beads stuck in `in_progress`.

```bash
PROG_JSON=$(bd list --status=in_progress --json --limit 0)
```

For each `in_progress` bead, determine if a worker is still active:

1. **Check for a live worktree:**
   ```bash
   WORKTREE_PATH="${REPO_ROOT}/.worktrees/parallel-agents/${ISSUE_ID}"
   if [ -d "${WORKTREE_PATH}" ]; then
     WORKTREE_EXISTS=true
   else
     WORKTREE_EXISTS=false
   fi
   ```
2. **Check for a pushed branch:**
   ```bash
   BRANCH_EXISTS=$(git ls-remote --heads origin "agent/${ISSUE_ID}" | wc -l)
   ```
3. **Decision matrix:**

| Worktree exists | Remote branch | Labels | Action |
|---|---|---|---|
| yes | yes | `direct-merge` | Worker finished, coordinator missed it. Process as direct-merge (see Pass 5). |
| yes | yes | `pr-review` | Worker created PR, coordinator missed it. Process in Pass 2. |
| yes | yes | (none) | Worker may still be running or stalled. If a live foreign lease exists, skip. Otherwise check `bd stale` age. If updated >30min ago with no subagent activity, release: `bd update <id> --status open --append-notes "Released stale in_progress claim (no activity, worktree exists)"`. Remove worktree. |
| yes | no | any | Worker died mid-work. If a live foreign lease exists, skip. Otherwise check for meaningful commits in the worktree (`git -C <worktree> log --oneline origin/HEAD..HEAD`). If commits exist, **do not push**. Add label `recovery-needed`, append a note that unpublished recovery work exists, and release only if you preserve the recovery worktree/branch for later coordinator inspection. If no commits, just clean up worktree and release to open. |
| no | yes | `direct-merge` | Process as direct-merge (Pass 5). |
| no | yes | `pr-review` | Process in Pass 2. |
| no | yes | (none) | If a live foreign lease exists, skip. Otherwise stale claim. Release to open: `bd update <id> --status open --append-notes "Released stale claim (no worktree, unpushed branch exists)"`. |
| no | no | any | If a live foreign lease exists, skip. Otherwise fully orphaned. Release to open: `bd update <id> --status open --append-notes "Released orphaned in_progress claim (no worktree, no branch)"`. |

Also remove `review-running` label from any bead that has it but is not actively
being processed by a live worker (no worktree), but only if no live foreign
lease exists:
```bash
bd update <id> --remove-label review-running
```

### Pass 2: Blocked beads with `pr-review` label (PR state reconciliation)

These are original implementation beads waiting on PR outcome.

```bash
PR_REVIEW_JSON=$(bd list --status=blocked --label pr-review --json --limit 0)
```

For each blocked bead with `pr-review` label (but **not** `pr-review-task`):

1. **Resolve PR number** from `external_ref`:
   ```bash
   PR_NUMBER=$(echo "${BEAD_JSON}" | jq -r '
     (.external_ref // "") as $ref |
     ($ref | capture("^gh-pr:(?<n>[0-9]+)$")?.n) // empty')
   ```
   If no PR number found, append note and skip, but only when no live foreign
   lease exists:
   ```bash
   bd update <id> --append-notes "Cleanup: no external_ref gh-pr:N found, needs manual triage"
   ```

2. **Check PR state:**
   ```bash
   PR_STATE_JSON=$(gh pr view "${PR_NUMBER}" --json state,mergedAt 2>&1)
   ```

3. **Handle by PR state:**

| PR State | Action |
|---|---|
| **MERGED** | If no live foreign lease exists, close this bead: `bd close <id> --reason "Cleanup: PR #${PR_NUMBER} already merged"`. Clean up worktree and remote branch if they exist. |
| **CLOSED** (not merged) | If no live foreign lease exists, reopen for re-triage: `bd update <id> --status open --remove-label pr-review --append-notes "Cleanup: PR #${PR_NUMBER} closed without merge — needs re-triage"`. |
| **OPEN** | PR still active — leave bead as-is. Verify exactly one corresponding `pr-review-task` bead exists (check dependents). If missing or duplicated, append note for coordinator dedupe/rebuild on next loop. |
| **gh fails** | Append note, skip. Do not mutate on transient errors. |

### Pass 3: Blocked `pr-review-task` beads (review bead reconciliation)

These are dedicated PR-review beads waiting to be dispatched.

```bash
PRT_JSON=$(bd list --status=blocked --label pr-review-task --json --limit 0)
```

For each `pr-review-task` bead:

1. **Resolve the original implementation bead** (from description or dependency
   graph):
   ```bash
   ORIGINAL_ID=$(echo "${BEAD_JSON}" | jq -r '
     (.description // "") as $d |
     ($d | capture("Original implementation bead: (?<id>[^.[:space:]]+)")?.id) // empty')

   if [ -z "${ORIGINAL_ID}" ]; then
     ORIGINAL_ID=$(echo "${BEAD_JSON}" | jq -r '
       (.description // "") as $d |
       ($d | capture("Review target bead: (?<id>[^.[:space:]]+)")?.id) // empty')
   fi
   ```

2. **Resolve PR number** from the original bead's `external_ref`:
   ```bash
   if [ -n "${ORIGINAL_ID}" ]; then
     ORIG_JSON=$(bd show "${ORIGINAL_ID}" --json)
     PR_NUMBER=$(echo "${ORIG_JSON}" | jq -r '
       (.[0].external_ref // .external_ref // "") as $ref |
       ($ref | capture("^gh-pr:(?<n>[0-9]+)$")?.n) // empty')
   fi
   ```
   Also try parsing PR URL from the review bead's own description as fallback.

3. **Check PR state** and handle:

| PR State | Original bead status | Action |
|---|---|---|
| **MERGED** | open/in_progress/blocked | If neither bead has a live foreign lease, close both beads: `bd close <review-id> --reason "Cleanup: PR #N already merged"` and `bd close <original-id> --reason "Cleanup: PR #N already merged"`. Clean up worktree/branch. |
| **MERGED** | already closed | If no live foreign lease exists on the review bead, close only the review bead. |
| **CLOSED** (not merged) | any | If neither bead has a live foreign lease, close review bead: `bd close <review-id> --reason "Cleanup: PR #N closed without merge"`. Update original: `bd update <original-id> --status open --remove-label pr-review --append-notes "Cleanup: PR #N closed, review bead closed — needs re-triage"`. |
| **OPEN** | any | PR still active — leave both beads as-is. Check for stale `review-running` label only when no live foreign lease exists. |
| Cannot resolve PR | — | Append note to review bead, skip mutation. |

### Pass 4: Blocked beads whose blockers are all closed

Before unblocking ordinary blocked work, dedupe any PR-review beads:
- group `pr-review-task` beads by original implementation bead and PR number
- keep the oldest still-relevant blocked bead as canonical
- close or note duplicates so the coordinator does not dispatch two reviewers,
  but skip any duplicate carrying a live foreign lease

A duplicate review bead must never survive cleanup silently.

A bead may be `blocked` because it depends on other beads. If all blocking beads
are now closed, the blocked bead should be unblocked.

```bash
ALL_BLOCKED=$(bd list --status=blocked --json --limit 0)
```

For each blocked bead (skip those already handled in Pass 2/3):

1. **Get dependencies:**
   ```bash
   DEPS_JSON=$(bd dep list <id> --json)
   ```
2. **Check each `blocks` dependency** — is the blocking bead closed?
   ```bash
   for dep_id in $(echo "${DEPS_JSON}" | jq -r '.[].depends_on_id'); do
     DEP_STATUS=$(bd show "${dep_id}" --json | jq -r '.[0].status // .status')
     # If any blocker is NOT closed, bead stays blocked
   done
   ```
3. If **all blockers are closed** and no live foreign lease exists, unblock:
   ```bash
   bd update <id> --status open \
     --append-notes "Cleanup: all blocking dependencies are now closed, unblocking"
   ```

### Pass 5: Stale worktrees, sync-worktree health, and orphaned branches

Metadata persistence is handled by the Dolt database (`.beads/dolt/`).
Cleanup must never delete the `.beads/` directory or its Dolt data.

#### 5a. Validate Dolt DB health

```bash
bd dolt status
bd doctor
```

If the Dolt server is unhealthy, append a cleanup note and continue
with branch/worktree cleanup; do not mutate `.beads/dolt/` manually
inside this pass.

#### 5b. Remove coordinator worktrees for closed/not-found beads

```bash
bd worktree list
```

For each worktree under `.worktrees/parallel-agents/` only:

1. **Extract the base bead ID** from the worktree directory name. Worktree names
   may have suffixes appended by coordinators or staleness fixers — strip them:
   ```bash
   # Strip known suffixes: -coord-*, -stalefix-*, -revive-*, -review-*, -clean*
   BASE_ID=$(echo "${WT_NAME}" | sed -E 's/(-coord-|-stalefix-|-revive-|-review-|-clean[0-9]*).*//')
   ```
2. Look up the bead: `bd show "${BASE_ID}" --json`.
3. **If bead is closed** — remove worktree and delete local/remote branch:
   ```bash
   bd worktree remove ".worktrees/parallel-agents/${WT_NAME}" --force 2>/dev/null || true
   git branch -d "agent/${WT_NAME}" 2>/dev/null || true
   git push origin --delete "agent/${WT_NAME}" 2>/dev/null || true
   ```
4. **If bead is open** (was released in an earlier pass) — remove worktree only
   unless the bead carries `recovery-needed` or an equivalent recovery note.
   Recovery-tagged worktrees must be preserved for coordinator inspection:
   ```bash
   if bead has recovery-needed label; then
     : preserve worktree for recovery
   else
     bd worktree remove ".worktrees/parallel-agents/${WT_NAME}" --force 2>/dev/null || true
   fi
   ```
5. **If bead does not exist** (deleted or corrupted) — remove worktree and
   branch:
   ```bash
   bd worktree remove ".worktrees/parallel-agents/${WT_NAME}" --force 2>/dev/null || true
   git branch -d "agent/${WT_NAME}" 2>/dev/null || true
   git push origin --delete "agent/${WT_NAME}" 2>/dev/null || true
   ```
6. **If bead is in_progress or blocked** — leave the worktree alone (may still
   be active or awaiting review).

### Pass 6: Stale `review-running` labels

Catch any remaining beads with `review-running` that weren't cleaned in earlier
passes:

```bash
bd list --label review-running --json --limit 0
```

For each bead with `review-running`:
- If status is NOT `in_progress`, or no worktree exists for it, and no live
  foreign lease exists:
  ```bash
  bd update <id> --remove-label review-running \
    --append-notes "Cleanup: removed stale review-running label (no active worker)"
  ```

---

## Output Format

After all passes complete, produce a structured summary:

```
## Beads Cleanup Report

**Timestamp**: <ISO 8601>
**Passes completed**: 6/6

### Pass 1: Stale in_progress
- <id>: released to open (reason)
- <id>: processed as direct-merge → Pass 5
- (none found)

### Pass 2: PR-review beads
- <id>: closed (PR #N merged)
- <id>: reopened for re-triage (PR #N closed without merge)
- (none found)

### Pass 3: PR-review-task beads
- <id>: closed (PR #N merged), original <orig-id> also closed
- (none found)

### Pass 4: Unblocked beads
- <id>: unblocked (all blockers closed)
- (none found)

### Pass 5a: Dolt DB health
- Dolt server: healthy | unhealthy (note appended)
- (none found)

### Pass 5b: Stale worktrees
- <path>: removed (bead <id> closed)
- <path>: removed (bead not found)
- (none found)

### Pass 6: Stale labels
- <id>: removed review-running label
- (none found)

### Summary
| Metric | Count |
|---|---|
| Beads released to open | N |
| Beads closed | N |
| Beads unblocked | N |
| Dolt DB issues detected | N |
| Worktrees cleaned | N |
| Labels fixed | N |
| Skipped (needs manual triage) | N |
| Total mutations | N |
```

---

## Constraints

- **Never implement code.** This skill only fixes bead metadata and git artifacts.
- **Never close a bead without confirming external state** (PR merged, branch
  merged, etc.).
- **Never force-delete branches with uncommitted work** — push first, then clean.
- **Always append notes** explaining why a mutation was made.
- **Idempotent** — safe to run multiple times with no side effects.
- **Do not create new beads** — only repair existing ones.
- Transient `gh` failures should be logged and skipped, never cause bead mutations.

---

## bd Quick Reference

| Action | Command |
|---|---|
| All in_progress | `bd list --status=in_progress --json --limit 0` |
| All blocked | `bd list --status=blocked --json --limit 0` |
| Blocked + pr-review | `bd list --status=blocked --label pr-review --json --limit 0` |
| Blocked + pr-review-task | `bd list --status=blocked --label pr-review-task --json --limit 0` |
| By label | `bd list --label <label> --json --limit 0` |
| Show issue | `bd show <id> --json` |
| Dependencies | `bd dep list <id> --json` |
| PR state | `gh pr view <N> --json state,mergedAt` |
| Close bead | `bd close <id> --reason "<reason>"` |
| Update bead | `bd update <id> --status <status> --append-notes "<note>"` |
| Remove label | `bd update <id> --remove-label <label>` |
| List worktrees | `bd worktree list` |
| Remove worktree | `bd worktree remove <path>` |
| Delete remote branch | `git push origin --delete <branch>` |
| Dolt server status | `bd dolt status` |
