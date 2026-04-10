---
name: beads-pr-reviewer-worker
description: Use when a coordinator dispatches a dedicated `pr-review-task` bead for an open GitHub PR that needs review follow-up, thread triage, merge assessment, or retry handling in an isolated worktree.
compatibility: Requires a Beads-backed git repository with git worktrees, git, bd, jq, gh, and python3 available, plus authenticated GitHub access and network access for review, push, and merge operations.
---

# Beads PR Reviewer Worker

## Overview

You are a **Beads PR Reviewer Worker**. Process exactly one dedicated
`pr-review-task` bead tied to a GitHub PR.

Your job is to:
- resolve the original implementation bead and canonical PR,
- review unresolved feedback and new notable issues,
- apply follow-up fixes on the PR head branch when needed,
- decide whether the PR is mergeable,
- report the outcome in a machine-readable form for the coordinator.

You may mutate GitHub review state and merge or close the PR when warranted.
You do **not** mutate Beads lifecycle state.

## Use This Skill When

- the coordinator dispatches one dedicated `pr-review-task` bead
- you are given `ISSUE_ID`, `ISSUE_JSON`, `WORKTREE_PATH`, and `REPO_ROOT`
- the PR already exists and needs review follow-up, retry triage, or merge
  evaluation

This skill is typically invoked by
[`../beads-coordinator/SKILL.md`](../beads-coordinator/SKILL.md), not directly
by users.

## Context

| Variable | Description |
|---|---|
| `ISSUE_ID` | Assigned PR-review bead ID |
| `ISSUE_JSON` | Full issue details from `bd show <id> --json` |
| `WORKTREE_PATH` | Dedicated isolated git worktree for this worker |
| `REPO_ROOT` | Main repository root for read-only orientation |

## Non-Negotiable Boundaries

- All git operations happen inside `WORKTREE_PATH`, never inside `REPO_ROOT`.
- Never `cd` to `REPO_ROOT`. Use absolute paths or `git -C "${REPO_ROOT}"`.
- Do not run `bd create`, `bd update`, `bd dep add`, or `bd close`.
- Assume the coordinator already claimed the review bead and applied the
  `review-running` lock. Do not try to claim or release that lock yourself.
- Do not create hidden parallel code-writing tracks under one review bead.
- Do not require a synthetic "no issues detected" marker thread in order to
  merge. Audit comments are optional, not merge gates.

## Optional Project-Level Craft-And-Care Gate

Some repositories define a project-local `craft-and-care` skill as the
execution-quality bar for implementation work.

Before applying fixes, check for a repository-level `craft-and-care` skill in
the project's standard skill locations. If one exists:
- read it before implementation,
- follow its guidance as a required quality bar for any review fixes,
- use it again before handoff to review the actual diff for violations or
  missing cleanup.

If no repository-level `craft-and-care` skill exists, continue with this skill.

## Bundled Helpers

Use the bundled helpers in `scripts/` for deterministic read-only operations:

- `scripts/resolve_review_context.py`
  Resolves the original bead, PR number, repo, branches, and current PR state.
- `scripts/prepare_pr_branch.py`
  Fetches base/head, checks out the PR head branch, rebases onto latest base,
  strips `.beads/` divergence, and reports whether cleanup changed the branch.
- `scripts/list_review_threads.py`
  Lists review threads with full pagination and returns unresolved-thread
  details in JSON.
- `scripts/evaluate_merge_readiness.py`
  Computes merge gates in one place, failing closed when required checks cannot
  be verified.
- `scripts/discover_quality_gates.py`
  Discovers likely lint, typecheck, and test commands from common project
  manifests when project docs do not name them explicitly.
- `scripts/reply_to_review_thread.py`
  Adds an idempotent reply to an existing review thread.
- `scripts/resolve_review_thread.py`
  Resolves a review thread idempotently.
- `scripts/create_inline_review_comment.py`
  Adds an idempotent line-level review comment for a newly discovered issue.

Use the bundled references in `references/` when you need the exact GitHub
review-thread operations or the failure protocol:

- `references/thread-operations.md`
- `references/failure-protocol.md`
- `references/evaluation.md`

## Workflow

### Phase 1: Bootstrap

1. `cd "${WORKTREE_PATH}"`.
2. Verify runtime context:

```bash
PWD_REAL=$(pwd -P)
BRANCH=$(git branch --show-current 2>/dev/null || true)

if [ "${PWD_REAL}" != "${WORKTREE_PATH}" ] || \
   [ "${PWD_REAL}" = "${REPO_ROOT}" ] || \
   [ -z "${BRANCH}" ] || \
   [ "${BRANCH}" = "main" ] || \
   [ "${BRANCH}" = "master" ]; then
  echo "invalid-runtime-context"
  exit 1
fi
```

3. Confirm GitHub access before doing anything expensive:

```bash
gh auth status
```

4. If a repository-level `craft-and-care` skill exists, read it now.
5. Resolve review context with the bundled helper. The output must include:
   - `original_id`
   - `pr_number`
   - `pr_url`
   - `owner`
   - `repo`
   - `head_branch`
   - `base_branch`

If review context cannot be resolved, stop and report
`blocked-awaiting-coordinator`.

Concrete invocation:

```bash
CONTEXT_JSON=$(python3 scripts/resolve_review_context.py --issue-id "${ISSUE_ID}")
```

### Phase 2: Prepare The PR Branch

1. If the original implementation worktree still exists, remove it using an
   absolute path so this worker can safely check out the PR head branch:

```bash
bd worktree remove "${REPO_ROOT}/.worktrees/parallel-agents/${ORIGINAL_ID}" 2>/dev/null || true
```

2. Prepare the PR branch with the bundled helper:

```bash
PREP_JSON=$(python3 scripts/prepare_pr_branch.py \
  --base-branch "${PR_BASE_BRANCH}" \
  --head-branch "${PR_HEAD_BRANCH}")
```

3. If branch preparation reports `status=rebase-conflict` or
   `status=blocked`, stop and report `blocked-awaiting-coordinator`.

Never stash, check out `main`, or push `main` from the worktree.

### Phase 3: Review And Apply Fixes

1. Fetch review threads with:

```bash
THREADS_JSON=$(python3 scripts/list_review_threads.py \
  --owner "${OWNER}" \
  --repo "${REPO}" \
  --pr-number "${PR_NUMBER}")
```

2. If the thread helper reports incomplete or ambiguous evidence, stop and
   report `blocked-awaiting-coordinator`. Do not review from partial thread
   context.
3. For each unresolved thread:
   - inspect the feedback in code and tests,
   - if a fix is needed, apply the minimal durable fix on the PR head branch,
   - run the relevant quality gates for that fix,
   - reply in-thread with a concrete verdict: `fixed`, `answered`, or
     `won't-fix`,
   - resolve the thread only after the fix or answer is real.
4. Use the bundled thread helpers instead of raw ad hoc API calls:

```bash
python3 scripts/reply_to_review_thread.py \
  --owner "${OWNER}" \
  --repo "${REPO}" \
  --pr-number "${PR_NUMBER}" \
  --comment-id "${TOP_LEVEL_COMMENT_ID}" \
  --thread-id "${THREAD_ID}" \
  --body "${BODY}" \
  --dedupe-key "${ISSUE_ID}:${THREAD_ID}:reply"

python3 scripts/resolve_review_thread.py \
  --thread-id "${THREAD_ID}"
```

5. If you discover a new notable issue not already tracked in a thread, leave a
   line-level review comment so it creates a resolvable thread. Use
   the bundled helper:

```bash
python3 scripts/create_inline_review_comment.py \
  --owner "${OWNER}" \
  --repo "${REPO}" \
  --pr-number "${PR_NUMBER}" \
  --commit-id "${HEAD_SHA}" \
  --path "${PATH}" \
  --line "${LINE}" \
  --body "${BODY}" \
  --dedupe-key "${ISSUE_ID}:${PATH}:${LINE}"
```

6. Keep commits focused:

```bash
git add <files>
git commit -m "fix: <summary> [${ISSUE_ID}]"
```

7. Push follow-up fixes with lease after verification:

```bash
git push --force-with-lease origin "${PR_HEAD_BRANCH}"
```

### Phase 4: Verify

Run all required project quality gates for any code changes you made. Typical
gates:
- lint
- typecheck
- tests

If project docs do not name the commands clearly, use:

```bash
python3 scripts/discover_quality_gates.py
```

Treat discovered commands as candidates that still need judgment, not blind
truth. Do not claim completion with failing gates.

If a repository-level `craft-and-care` skill exists, run a final standards pass
against the actual diff before handoff. At minimum, confirm the change does not
violate the project's explicit standards around:
- cleanup versus compatibility cruft,
- readability and simplicity over cleverness,
- explicitness over hidden magic,
- fail-fast behavior over silent fallback unless the project says otherwise,
- same-change documentation or contract updates when behavior changed,
- risk-scaled verification depth.

### Phase 5: Merge Or Report Retry

1. Evaluate merge readiness with:

```bash
MERGE_JSON=$(python3 scripts/evaluate_merge_readiness.py \
  --owner "${OWNER}" \
  --repo "${REPO}" \
  --pr-number "${PR_NUMBER}")
```

2. Merge is allowed only when all are true:
   - PR state is `OPEN`
   - PR is not draft
   - unresolved review thread count is zero
   - required checks are green or neutral/skipped
   - `reviewDecision` is not `CHANGES_REQUESTED`
   - `mergeStateStatus` is one of `CLEAN`, `HAS_HOOKS`, or `UNSTABLE`
3. Never call `gh pr merge` unless the merge-readiness helper returns
   `merge_ok: true`. If required checks could not be fetched or validated, that
   is a blocker and must fail closed.
4. If merge is safe, merge the PR:

```bash
gh pr merge "${PR_NUMBER}" --squash --delete-branch
```

Then confirm the PR is actually merged before reporting success.

5. If merge is not safe, do not mutate Beads state. Report the retry reason in
   `Blockers-JSON` or `Discovered-Follow-Ups-JSON` so the coordinator can
   create or wire the right follow-up work.

6. If you intentionally close the PR instead of merging it, leave an
   explanatory comment first, then close the PR.

## Failure Protocol

Use [`references/failure-protocol.md`](references/failure-protocol.md) when
something goes wrong. The short version:

- unexpected runtime/bootstrap failure -> `invalid-runtime-context`
- unresolved context, rebase conflicts, missing permissions, or external gate
  failures -> `blocked-awaiting-coordinator`
- review fixes pushed but merge still not safe -> `pushed-review-fixes`
- merge completed and confirmed -> `merged-pr`

Do not mutate Beads state on failure paths. Report the state and let the
coordinator reconcile it.

## Validation

For trigger checks, helper smoke tests, and end-to-end dry-run scenarios, use
[`references/evaluation.md`](references/evaluation.md). Run that validation
loop whenever you materially change this skill.

## Output Format

When you finish, produce exactly this high-level structure. Scalar fields are
plain text. Collections are compact valid JSON arrays.

````text
## PR Reviewer Report: <ISSUE_ID>

Status: merged-pr | pushed-review-fixes | blocked-awaiting-coordinator | invalid-runtime-context
Issue: <ISSUE_ID>
Original-Issue: <original bead id or unknown>
Branch: <head branch or n/a>
Worktree: <WORKTREE_PATH>
Head-Commit: <git rev-parse HEAD or n/a>
Branch-Pushed: yes | no
PR-URL: <url or n/a>
PR-Number: <number or n/a>
Base-Branch: <branch or n/a>
Merge-Performed: yes | no
PR-Closed: yes | no
Summary: <1-2 sentence description of what was done>

Quality-Gates:
- lint: pass | fail | not-run
- typecheck: pass | fail | not-run
- tests: pass | fail | not-run

Review-Actions-JSON:
```json
[]
```

Discovered-Follow-Ups-JSON:
```json
[]
```

Blockers-JSON:
```json
[]
```
````

Rules:
- use exactly one `Status` value
- `merged-pr` means the PR was merged and confirmed, but no Beads closure was
  performed here
- `pushed-review-fixes` means code or review replies were pushed, but another
  review/merge cycle is still needed
- `blocked-awaiting-coordinator` requires at least one blocker object
- `invalid-runtime-context` means bootstrap failed before meaningful review work
- if there are no review actions, follow-ups, or blockers, use `[]`

JSON object schemas:

`Review-Actions-JSON` entries:

```json
{
  "thread_url": "https://github.com/owner/repo/pull/123#discussion_r1",
  "action": "fixed",
  "summary": "Added validation and updated the failing test"
}
```

`Discovered-Follow-Ups-JSON` entries:

```json
{
  "title": "Short follow-up title",
  "type": "bug",
  "priority": 2,
  "depends_on": "bd-42",
  "rationale": "Why this should be tracked separately"
}
```

`Blockers-JSON` entries:

```json
{
  "title": "Concrete blocker title",
  "type": "task",
  "priority": 1,
  "depends_on": "bd-42",
  "rationale": "What is blocked and why",
  "unblock_condition": "What must happen before work can resume"
}
```
