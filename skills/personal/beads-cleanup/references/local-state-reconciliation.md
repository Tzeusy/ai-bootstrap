# Local State Reconciliation

Load this file when the cleanup pass needs to reconcile local Beads and git
state: stale `in_progress` claims, dependency unblocking, Dolt/worktree health,
and stale `review-running` locks.

## Preconditions

- Run from the target repository root, or pass `--rig <rig>` to `bd list` and
  `bd ready` when operating from outside the target rig.
- Before any `bd` mutation, inspect lease state using
  `../beads-coordinator/references/runtime-and-safety.md`.
- If a live foreign lease or recent heartbeat exists, skip mutation and record
  the bead as manual triage.
- Append a note for every mutation.
- Never mutate `.beads/dolt/` manually.

## Pass 1: Stale `in_progress` Beads

```bash
PROG_JSON=$(bd list --status=in_progress --json --limit 0)
```

For each `in_progress` bead:

1. Confirm there is no live foreign lease.
2. Check for a live worktree:

```bash
WORKTREE_PATH="${REPO_ROOT}/.worktrees/parallel-agents/${ISSUE_ID}"
if [ -d "${WORKTREE_PATH}" ]; then
  WORKTREE_EXISTS=true
else
  WORKTREE_EXISTS=false
fi
```

3. Check for a pushed worker branch:

```bash
BRANCH_EXISTS=$(git ls-remote --heads origin "agent/${ISSUE_ID}" | wc -l)
```

4. When a worktree exists but the worker may be stalled, inspect whether it has
   meaningful unpublished commits:

```bash
git -C "${WORKTREE_PATH}" log --oneline origin/HEAD..HEAD
```

5. Apply this decision matrix:

| Worktree exists | Remote branch | Labels | Action |
|---|---|---|---|
| yes | yes | `direct-merge` | Do not close here. Record it for coordinator-style merge handling after confirming no live foreign lease. |
| yes | yes | `pr-review` | Defer to PR reconciliation in `pr-review-reconciliation.md`. |
| yes | yes | none | Treat as stalled only when stale age is high and no live lease or worker activity remains. Then `bd update <id> --status open --append-notes "Cleanup: released stale in_progress claim (no active worker evidence)"`, then remove the worktree. |
| yes | no | any | If meaningful commits exist, push `agent/<id>` first if safe, then release to `open`. If no commits exist, remove the worktree and release to `open`. |
| no | yes | `direct-merge` | Record for coordinator-style merge handling. |
| no | yes | `pr-review` | Defer to PR reconciliation. |
| no | yes | none | `bd update <id> --status open --append-notes "Cleanup: released stale claim (no worktree, remote branch exists)"` |
| no | no | any | `bd update <id> --status open --append-notes "Cleanup: released orphaned in_progress claim (no worktree, no branch)"` |

If a bead still carries `review-running` but has no active worktree, remove the
label after lease checks:

```bash
bd update <id> --remove-label review-running \
  --append-notes "Cleanup: removed stale review-running label during in_progress reconciliation"
```

## Pass 4: Blocked Beads Whose Blockers Are Closed

```bash
ALL_BLOCKED=$(bd list --status=blocked --json --limit 0)
```

For each blocked bead not already handled by PR reconciliation:

1. Confirm there is no live foreign lease.
2. Read dependencies:

```bash
DEPS_JSON=$(bd dep list <id> --json)
```

3. Inspect each blocking dependency:

```bash
for dep_id in $(echo "${DEPS_JSON}" | jq -r '.[].depends_on_id'); do
  DEP_STATUS=$(bd show "${dep_id}" --json | jq -r '.[0].status // .status')
done
```

4. If all blockers are closed, reopen the bead:

```bash
bd update <id> --status open \
  --append-notes "Cleanup: all blocking dependencies are closed, unblocking"
```

## Pass 5a: Dolt Health

Validate the Beads database before branch or worktree cleanup:

```bash
bd dolt status
bd doctor
```

If Dolt is unhealthy, record it in the report and continue only with the
non-DB-destructive portions of cleanup. Do not try to repair `.beads/dolt/`
manually inside this skill.

## Pass 5b: Coordinator Worktrees And Branches

```bash
bd worktree list
```

Only inspect worktrees under `.worktrees/parallel-agents/`.

1. Extract the base bead ID from the worktree directory name:

```bash
BASE_ID=$(echo "${WT_NAME}" | sed -E 's/(-coord-|-stalefix-|-revive-|-review-|-clean[0-9]*).*//')
```

2. Look up the bead:

```bash
bd show "${BASE_ID}" --json
```

3. Reconcile using this table:

| Bead state | Action |
|---|---|
| closed | Remove the worktree. Delete local and remote worker branches only after confirming they are not needed for unpublished work. |
| open | Remove the worktree only. Preserve the branch if it may still contain useful commits. |
| missing | Remove the worktree. Delete local and remote worker branches if they still exist and no unpublished work needs to be preserved. |
| in_progress or blocked | Leave the worktree alone unless other evidence proves it is stale and unleased. |

Typical removal commands:

```bash
bd worktree remove ".worktrees/parallel-agents/${WT_NAME}" --force 2>/dev/null || true
git branch -d "agent/${WT_NAME}" 2>/dev/null || true
git push origin --delete "agent/${WT_NAME}" 2>/dev/null || true
```

## Pass 6: Stale `review-running` Labels

```bash
bd list --label review-running --json --limit 0
```

For each bead with `review-running`:

- If status is not `in_progress`, or no active worktree exists, and no live
  foreign lease exists, remove the label:

```bash
bd update <id> --remove-label review-running \
  --append-notes "Cleanup: removed stale review-running label (no active worker)"
```

- If a live worker or lease still exists, leave it alone.
