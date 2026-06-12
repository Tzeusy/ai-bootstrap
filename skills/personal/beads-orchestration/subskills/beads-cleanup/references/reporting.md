# Reporting And Quick Reference

Load this file when you need the exact cleanup report shape, rig-routing note,
or command quick reference.

## Rig Routing Note

If running from outside the target rig, use `bd -C <rig-path>` as a global
flag prefix so all commands query the correct project database. For example:

```bash
bd -C <rig-path> list --status=in_progress --json --limit 0
bd -C <rig-path> ready
```

Commands that take an existing bead ID (`bd update`, `bd close`, `bd show`,
`bd dep`) auto-route via the ID prefix and do not require `-C`.

`bd search`, `bd blocked`, `bd count`, and `bd query` do not support the rig
routing shorthand. Use `bd -C <rig-path> list` with filters as a workaround.

## Cleanup Report

```text
## Beads Cleanup Report

Timestamp: <ISO 8601>
Passes completed: 6/6

### Pass 1: Stale in_progress
- <id>: released to open (reason)
- <id>: deferred to PR reconciliation
- (none found)

### Pass 2: PR-review beads (findings only — no mutation here)
- <id>: PR #N MERGED; recommend close + branch cleanup (coordinator Step 0)
- <id>: PR #N CLOSED-unmerged; recommend reopen + re-triage
- <id>: missing canonical external_ref gh-pr:N; recommend manual triage
- (none found)

### Pass 3: PR-review-task beads (findings only — no mutation here)
- <id>: PR #N MERGED; recommend close review + original <orig-id>
- <id>: skipped (missing canonical PR reference)
- (none found)

### Pass 4: Unblocked beads
- <id>: unblocked (all blockers closed)
- (none found)

### Pass 5a: Dolt DB health
- Dolt server: healthy
- Dolt server: unhealthy (manual triage required)

### Pass 5b: Stale worktrees
- <path>: removed (bead <id> closed)
- <path>: preserved branch, removed worktree (bead reopened)
- (none found)

### Pass 6: Stale labels
- <id>: removed review-running label
- (none found)

### PR-state findings (for coordinator Step 0)

Cleanup only reports these; the coordinator's Step 0 performs the mutation and
re-verifies with `gh` immediately before acting.

| Bead ID | PR # | Observed state | Recommended action |
|---|---|---|---|
| <id> | <N> | MERGED | close review + original bead; delete branch post-closure |
| <orig-id> | <N> | CLOSED-unmerged | reopen original, remove `pr-review`, re-triage |
| <id> | <N> | OPEN, no `pr-review-task` | coordinator self-heal: create/wire review bead |
| <id> | — | unresolved / `gh` failure | manual triage; do not mutate |

### Summary
| Metric | Count |
|---|---|
| Beads released to open | N |
| Beads closed | N |
| Beads unblocked | N |
| Dolt DB issues detected | N |
| Worktrees cleaned | N |
| Labels fixed | N |
| Skipped (manual triage) | N |
| Total mutations | N |
```

## Constraints

- Never implement code.
- Never create new beads from cleanup.
- Never close a bead without confirming the external state that justifies it.
- Never delete a branch that may contain unpublished work without preserving it
  first.
- Never mutate `.beads/dolt/` manually.
- Treat transient `gh` failures as non-authoritative; log and skip instead of
  guessing.

## Command Quick Reference

| Action | Command |
|---|---|
| All `in_progress` beads | `bd list --status=in_progress --json --limit 0` |
| All blocked beads | `bd list --status=blocked --json --limit 0` |
| Blocked `pr-review` beads | `bd list --status=blocked --label pr-review --json --limit 0` |
| Blocked `pr-review-task` beads | `bd list --status=blocked --label pr-review-task --json --limit 0` |
| By label | `bd list --label <label> --json --limit 0` |
| Show bead | `bd show <id> --json` |
| List dependencies | `bd dep list <id> --json` |
| Check PR state | `gh pr view <N> --json state,mergedAt` |
| Close bead | `bd close <id> --reason "<reason>"` |
| Update bead | `bd update <id> --status <status> --append-notes "<note>"` |
| Remove label | `bd update <id> --remove-label <label>` |
| List worktrees | `bd worktree list` |
| Remove worktree | `bd worktree remove <path>` |
| Delete remote branch | `git push origin --delete <branch>` |
| Dolt status | `bd dolt status` |
| Repository health | `bd doctor` |
