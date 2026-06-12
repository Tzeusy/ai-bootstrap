# Failure Protocol

Use this protocol when review work cannot proceed safely.

## Core Rule

Do not mutate Beads lifecycle state on failure paths. Report the condition in
the worker report and let the coordinator reconcile it.

## Failure Classes

### `invalid-runtime-context`

Use when bootstrap failed before meaningful work started. Examples:
- `pwd` is not `WORKTREE_PATH`
- current branch is `main` or `master`
- worktree and repo root resolve to the same checkout

Stop immediately. Do not change code or GitHub state.

### `blocked-awaiting-coordinator`

Use when the worker cannot continue safely without outside help. Examples:
- original bead or PR number cannot be resolved
- GitHub auth or permissions are missing
- rebase conflicts require human or coordinator judgment
- required checks are failing for reasons you did not fix in this pass
- merge readiness is false because of external blockers

Rules:
- if a rebase is in progress and you are not finishing it, run
  `git rebase --abort`
- preserve useful code changes in the worktree or pushed branch
- record a concrete blocker with an unblock condition
- treat ambiguous context resolution, incomplete thread pagination, and
  unavailable required-check status as blockers, not soft warnings

### `pushed-review-fixes`

Use when:
- you made review fixes and pushed them, but merge is still not safe, or
- you replied to review threads and intentionally left the PR open for another
  cycle

This is not a hard failure. It means the coordinator should retry review later
or create explicit follow-up work from the reported blockers.

Retries must be idempotent:
- use stable dedupe keys for thread replies and inline review comments
- skip creating duplicate comments when the same dedupe key is already present
- resolving an already-resolved thread should be treated as success, not error

### `merged-pr`

Use only when:
- `gh pr merge` succeeded, and
- a follow-up `gh pr view` confirms the PR is merged

Do not close review or original beads here. The coordinator handles closure.
