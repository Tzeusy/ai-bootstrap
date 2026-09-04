# Failure Protocol

Use this protocol when review work cannot proceed safely.

## Core Rule

Do not mutate Beads lifecycle state on failure paths. Report the condition in
the worker report and let the coordinator reconcile it.

## Failure Classes

### `corrections-required`

Use when review found actionable correctness gaps inside the accepted outcome.
Leave resolvable threads and return implementation to the **original author**
when resumable or a **recovery worker** on the same PR branch. Do not create a
new review bead and do not author semantic code in the independent review lane.

Bind every verdict to the **exact head SHA** reviewed. Prefer the same
independent reviewer for the corrected-head recheck while independence remains
intact. Require a **fresh independent reviewer** after any reviewer-authored
semantic change or a high-risk correction involving auth, approvals, migrations,
cross-schema access, concurrency, or data loss.

Apply the **two-correction checkpoint** after two substantive reopenings:

- same seam/invariant: retain the PR, rewrite its acceptance/failure matrix,
  and return it to the implementation owner;
- new subsystem, trust boundary, architecture prerequisite, or risk class:
  report a linked blocker and require upstream spec/design triage before resume.

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
- rebase conflicts require coordinator judgment
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
- the coordinator explicitly authorized the exceptional reviewer-as-fixer path
  and you pushed a mechanical correction

This is not a hard failure. It means the coordinator should retry review later
with a fresh independent reviewer or create explicit follow-up work from the
reported blockers. Never merge the reviewer-authored head in the same pass.

Retries must be idempotent:
- use stable dedupe keys for thread replies and inline review comments
- skip creating duplicate comments when the same dedupe key is already present
- resolving an already-resolved thread should be treated as success, not error

### `merged-pr`

Use only when:
- `gh pr merge --squash` succeeded (without `--delete-branch`), and
- a follow-up `gh pr view` confirms the PR is merged

Do not delete the `agent/<id>` branch; the coordinator deletes it after closure
so the branch-name → bead correlation survives a crash. Do not close review or
original beads here either. The coordinator handles closure and branch cleanup.

### `merge-queued`

Use only when:
- the base branch is behind a merge queue (`merge_queue: true` from the
  readiness helper or `MERGE_QUEUE=yes` from the coordinator), and
- every merge gate held for the exact reviewed head, and
- `gh pr merge --squash --auto` succeeded and `gh pr view --json
  autoMergeRequest` is non-null.

This is a successful terminal outcome, not a failure. The queue rebuilds the PR
on the latest base and runs CI once more; the coordinator confirms `MERGED` in
Step 0 and closes the beads. If the queue later ejects the PR (CI failed on the
merge group, or a conflict appeared), the coordinator re-dispatches a review
bead and may authorize `--force-rebase`. Never bypass the queue with `--admin`.
