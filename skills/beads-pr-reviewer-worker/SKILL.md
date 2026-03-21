---
name: beads-pr-reviewer-worker
description: Handle PR-review follow-up beads (`pr-review-task`) by reviewing PR threads, posting review comments, resolving threads, and optionally merging/closing related beads when no issues remain.
---

# Beads PR Reviewer Worker

## Overview

You are a **Beads PR Reviewer Worker**. You process exactly one dedicated
PR-review bead (label `pr-review-task`) tied to a GitHub PR.

Primary responsibilities:
- review unresolved PR threads and code deltas,
- leave code-review comments (review threads) on notable issues,
- apply/follow up fixes when needed,
- when no notable issues remain, merge the PR and close both beads.

## Use This Skill When

- The assigned bead is `blocked` with label `pr-review-task`
- The bead references its original implementation bead (in description and/or dependency graph)
- `beads-coordinator` dispatches PR-review follow-up work

## Context (Injected by Coordinator)

| Variable | Description |
|---|---|
| `ISSUE_ID` | The PR-review bead ID |
| `ISSUE_JSON` | Full issue details from `bd show <id> --json` |
| `WORKTREE_PATH` | Isolated beads worktree path |
| `REPO_ROOT` | Main repository root |

## Environment Setup

**CRITICAL: Always use a dedicated worktree. NEVER switch branches or operate
directly in the main repository (`REPO_ROOT`).** Switching branches in the main
repo disrupts the coordinator and other workers sharing that checkout. All git
operations (checkout, rebase, commit, push) MUST happen inside `WORKTREE_PATH`.

```bash
# Validate worktree before any work
if [ -z "${WORKTREE_PATH}" ] || [ "${WORKTREE_PATH}" = "${REPO_ROOT}" ]; then
  echo "ERROR: Worker must run in a dedicated worktree, not the main repo."
  bd update "${ISSUE_ID}" \
    --status blocked \
    --append-notes "Worker aborted: no dedicated worktree provided. WORKTREE_PATH must differ from REPO_ROOT."
  exit 1
fi
cd "${WORKTREE_PATH}"
```

The coordinator creates worktrees via `bd worktree create`, which sets up a
review-isolated checkout for `agent/<issue-id>`. Beads metadata is stored in
a shared Dolt database; worktrees access it via a redirect file. Do not commit
`.beads/` changes on PR branches.

## Workflow

Before review work, ensure this bead is locked to avoid duplicate dispatch:
```bash
bd update "${ISSUE_ID}" --status in_progress --add-label review-running --json
```

### 1. Identify PR and original implementation bead

1. Prefer explicit metadata from this review bead:
   ```bash
   ORIGINAL_ID=$(echo "${ISSUE_JSON}" | jq -r '
     (.[0].description // .description // "") as $d |
     ($d | capture("Original implementation bead: (?<id>[^.[:space:]]+)")?.id) // empty')
   ```
2. If metadata is missing, fall back to dependency lookup:
   ```bash
   if [ -z "${ORIGINAL_ID}" ]; then
     ORIGINAL_ID=$(bd list --status=blocked --label pr-review --json | \
       jq -r '.[] | select(any(.dependencies[]?; .depends_on_id=="'"${ISSUE_ID}"'")) | .id' | \
       head -n1)
   fi
   ```
3. If original bead is still unknown, release lock and re-block:
   ```bash
   if [ -z "${ORIGINAL_ID}" ]; then
     bd update "${ISSUE_ID}" \
       --status blocked \
       --remove-label review-running \
       --append-notes "Unable to resolve original implementation bead for PR review."
     exit 0
   fi
   ```
4. Resolve PR number from the original bead's `external_ref` (canonical source):
   ```bash
   ORIGINAL_JSON=$(bd show "${ORIGINAL_ID}" --json)
   PR_NUMBER=$(echo "${ORIGINAL_JSON}" | jq -r '
     (.[0].external_ref // .external_ref // "") as $ref |
     ($ref | capture("^gh-pr:(?<n>[0-9]+)$")?.n) // empty')
   ```
5. If `external_ref` is missing on the original bead, fall back to parsing PR URL
   from the review-bead description:
   ```bash
   if [ -z "${PR_NUMBER}" ]; then
     PR_URL=$(echo "${ISSUE_JSON}" | jq -r '
       (.[0].description // .description // "") as $d |
       ($d | capture("Review PR (?<url>https://github\\.com/[^[:space:]]+/pull/[0-9]+)")?.url) // empty')
     PR_NUMBER=$(echo "${PR_URL}" | sed -n 's#.*/pull/\\([0-9][0-9]*\\).*#\\1#p')
   fi
   ```
6. If PR number is still missing, release lock and re-block:
   ```bash
   if [ -z "${PR_NUMBER}" ]; then
     bd update "${ISSUE_ID}" \
       --status blocked \
       --remove-label review-running \
       --append-notes "Unable to resolve PR number. Expected original bead ${ORIGINAL_ID} to carry external_ref=gh-pr:<N>."
     exit 0
   fi
   ```
7. Inspect PR state:
   ```bash
   gh pr view "${PR_NUMBER}" --json number,url,state,isDraft,mergeStateStatus,reviewDecision,headRefName,mergedAt
   ```
8. Release the original implementation worktree so this worker can check out
   the PR head branch (git prohibits the same branch in two worktrees):
   ```bash
   if [ -n "${ORIGINAL_ID}" ]; then
     bd worktree remove "${REPO_ROOT}/.worktrees/parallel-agents/${ORIGINAL_ID}" 2>/dev/null || true
   fi
   ```
   **Use absolute paths for `bd worktree remove` — never `cd` to `REPO_ROOT`.**
9. Check out the PR head branch and rebase onto latest base branch upfront,
   so all review runs against current main.
   **CRITICAL: Verify you are in `WORKTREE_PATH` before ANY git checkout/rebase.**
   Running `git checkout` from `REPO_ROOT` will switch the main repo's branch
   and break the coordinator and all other workers.
   ```bash
   # Safety: assert we are in the worktree, not the main repo
   cd "${WORKTREE_PATH}"
   if [ "$(pwd -P)" = "$(cd "${REPO_ROOT}" && pwd -P)" ]; then
     echo "FATAL: about to run git checkout in REPO_ROOT — aborting"
     exit 1
   fi

   PR_META=$(gh pr view "${PR_NUMBER}" --json headRefName,baseRefName)
   PR_HEAD_BRANCH=$(echo "${PR_META}" | jq -r '.headRefName')
   PR_BASE_BRANCH=$(echo "${PR_META}" | jq -r '.baseRefName')
   git fetch origin "${PR_BASE_BRANCH}" "${PR_HEAD_BRANCH}"
   git checkout -B "${PR_HEAD_BRANCH}" "origin/${PR_HEAD_BRANCH}"

   if ! git rebase "origin/${PR_BASE_BRANCH}"; then
     # Resolve conflicts logically and continue rebase until complete.
     # Preserve intended behavior from both branches.
     # Do not resolve entire files with blanket --ours/--theirs.
     bd update "${ISSUE_ID}" \
       --status blocked \
       --remove-label review-running \
       --add-label pr-review \
       --add-label pr-review-task \
       --append-notes "Rebase onto ${PR_BASE_BRANCH} failed for PR #${PR_NUMBER}; conflicts need resolution on ${PR_HEAD_BRANCH}."
     exit 0
   fi
   git push --force-with-lease origin "${PR_HEAD_BRANCH}"
   ```

### 1b. Strip .beads divergence

`.beads/` is gitignored and should never appear in PR diffs. Beads metadata
lives in the Dolt database, not in git-tracked files.

Any `.beads/` diffs on the PR branch are stale snapshots accidentally committed
by workers. The authoritative metadata state lives in the Dolt DB, not in
the feature branch's files.

**CRITICAL: Never `git stash`, `git checkout main`, or `git push origin main`
from a worktree to "apply" drifted beads state. This destroys uncommitted beads
state from the coordinator and other workers, because worktrees share the git
stash and object store with the main repo.**

1. Check whether the PR branch carries any `.beads/` changes relative to base:
   ```bash
   BEADS_DIFF=$(git diff "origin/${PR_BASE_BRANCH}...HEAD" -- .beads/)
   ```
2. If divergence exists, simply strip it from the feature branch:
   ```bash
   if [ -n "${BEADS_DIFF}" ]; then
     git checkout "origin/${PR_BASE_BRANCH}" -- .beads/
     git commit -m "fix: remove .beads divergence from feature branch"
     git push --force-with-lease origin "${PR_HEAD_BRANCH}"

     bd update "${ISSUE_ID}" \
       --append-notes "Stripped .beads divergence from ${PR_HEAD_BRANCH}. Drifted state discarded (metadata belongs in Dolt DB)."
   fi
   ```

### 2. Review unresolved threads and notable issues

1. Fetch unresolved review threads:
   ```bash
   OWNER_REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
   OWNER=${OWNER_REPO%/*}
   REPO=${OWNER_REPO#*/}

   THREADS_JSON=$(gh api graphql \
     -f query='
     query($owner:String!, $repo:String!, $number:Int!) {
       repository(owner:$owner, name:$repo) {
         pullRequest(number:$number) {
           reviewThreads(first:100) {
             nodes {
               id
               isResolved
               comments(first:20) {
                 nodes { id author { login } body path line url }
               }
             }
           }
         }
       }
     }' \
     -F owner="${OWNER}" \
     -F repo="${REPO}" \
     -F number="${PR_NUMBER}")

   UNRESOLVED_COUNT=$(echo "${THREADS_JSON}" | jq \
     '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved==false)] | length')
   ```
2. For each unresolved thread:
   - investigate the feedback in code/tests,
   - if fixes are needed, apply them on the PR head branch (already checked out
     and rebased onto latest base in Phase 1 step 9), then commit each fix
     referencing the review thread,
   - reply in-thread with verdict (`fixed`, `answered`, or `won't fix` + rationale),
   - resolve the thread.
3. After applying fixes and passing quality gates, push with lease:
   ```bash
   git push --force-with-lease origin "${PR_HEAD_BRANCH}"
   ```
4. If you identify new notable issues not already tracked in threads, leave
   line-level code-review comments so they create resolvable review threads.
   Do not use top-level timeline comments (`gh pr comment`) for merge-readiness
   tracking unless no suitable code anchor exists.

### 3. Decide merge vs keep blocked

Evaluate merge guards after thread processing:

```bash
PR_JSON=$(gh pr view "${PR_NUMBER}" --json state,isDraft,mergeStateStatus,reviewDecision,mergedAt,url,baseRefName,headRefName)
UNRESOLVED_COUNT=$(gh api graphql \
  -f query='
  query($owner:String!, $repo:String!, $number:Int!) {
    repository(owner:$owner, name:$repo) {
      pullRequest(number:$number) {
        reviewThreads(first:100) { nodes { isResolved } }
      }
    }
  }' \
  -F owner="${OWNER}" -F repo="${REPO}" -F number="${PR_NUMBER}" | \
  jq '[.data.repository.pullRequest.reviewThreads.nodes[] | select(.isResolved==false)] | length')

REQUIRED_NON_GREEN=$(gh pr checks "${PR_NUMBER}" --required --json state | \
  jq '[.[] | select(.state != "SUCCESS" and .state != "SKIPPED" and .state != "NEUTRAL")] | length')

IS_DRAFT=$(echo "${PR_JSON}" | jq -r '.isDraft')
REVIEW_DECISION=$(echo "${PR_JSON}" | jq -r '.reviewDecision // "REVIEW_REQUIRED"')
MERGE_STATE=$(echo "${PR_JSON}" | jq -r '.mergeStateStatus // "UNKNOWN"')
MERGE_OK=false
if [ "${IS_DRAFT}" = "false" ] && \
   [ "${UNRESOLVED_COUNT}" -eq 0 ] && \
   [ "${REQUIRED_NON_GREEN}" -eq 0 ] && \
   [ "${REVIEW_DECISION}" != "CHANGES_REQUESTED" ] && \
   { [ "${MERGE_STATE}" = "CLEAN" ] || [ "${MERGE_STATE}" = "HAS_HOOKS" ] || [ "${MERGE_STATE}" = "UNSTABLE" ]; }; then
  MERGE_OK=true
fi
```

Merge is allowed only when all are true:
- PR is not draft.
- No unresolved review threads (`UNRESOLVED_COUNT == 0`).
- No required checks failing/pending (`REQUIRED_NON_GREEN == 0`).
- `reviewDecision` is not `CHANGES_REQUESTED`.
- `mergeStateStatus` is mergeable (for example `CLEAN`/`HAS_HOOKS`/`UNSTABLE`).
- No-issues marker thread can be created and resolved.

Hard merge gate:

```bash
if [ "${MERGE_OK}" != "true" ]; then
  echo "Skip merge: PR is not mergeable (mergeStateStatus=${MERGE_STATE})."
fi
```

Never call `gh pr merge` unless `MERGE_OK=true`.

If all guards pass:

1. Re-assert mergeability immediately before merge:
   ```bash
   test "${MERGE_OK}" = "true"
   ```
2. Post a reviewer-worker "no issues detected" marker thread and resolve it:
   ```bash
   PR_ID=$(gh pr view "${PR_NUMBER}" --json id -q .id)
   FILES_JSON=$(gh api "repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}/files")
   MARKER_OK=false
   MARKER_PATH=$(echo "${FILES_JSON}" | jq -r 'map(select(.status != "removed"))[0].filename // empty')
   MARKER_LINE=$(echo "${FILES_JSON}" | jq -r '
     (map(select(.status != "removed"))[0].patch // "") as $p |
     ($p | capture("@@ -[0-9,]+ \\+(?<start>[0-9]+)(,(?<count>[0-9]+))? @@")?.start // empty)')

   if [ -n "${PR_ID}" ] && [ -n "${MARKER_PATH}" ] && [ -n "${MARKER_LINE}" ]; then
     MARKER_THREAD_JSON=$(gh api graphql \
       -f query='
       mutation($pullRequestId:ID!, $path:String!, $line:Int!, $body:String!) {
         addPullRequestReviewThread(input:{
           pullRequestId:$pullRequestId,
           path:$path,
           line:$line,
           side:RIGHT,
           body:$body
         }) {
           thread {
             id
             comments(first:1) { nodes { url } }
           }
         }
       }' \
       -F pullRequestId="${PR_ID}" \
       -F path="${MARKER_PATH}" \
       -F line="${MARKER_LINE}" \
       -F body="No issues detected by beads-pr-reviewer-worker. Marking this PR as reviewed by worker.")

     MARKER_THREAD_ID=$(echo "${MARKER_THREAD_JSON}" | jq -r '.data.addPullRequestReviewThread.thread.id // empty')

     if [ -n "${MARKER_THREAD_ID}" ]; then
       gh api graphql \
         -f query='
         mutation($threadId:ID!) {
           resolveReviewThread(input:{threadId:$threadId}) {
             thread { id isResolved }
           }
         }' \
         -F threadId="${MARKER_THREAD_ID}"
       MARKER_OK=true
     fi
   else
     gh pr comment "${PR_NUMBER}" --body "No issues detected by beads-pr-reviewer-worker, but no suitable diff line was found to create a review thread marker. PR remains blocked until marker thread can be created and resolved."
   fi

   if [ "${MARKER_OK}" != "true" ]; then
     bd update "${ISSUE_ID}" \
       --status blocked \
       --remove-label review-running \
       --add-label pr-review \
       --add-label pr-review-task \
       --append-notes "Merge deferred for PR #${PR_NUMBER}: reviewer-worker could not create/resolve no-issues marker thread."
     exit 0
   fi
   ```
3. Merge PR:
   ```bash
   gh pr merge "${PR_NUMBER}" --squash --delete-branch
   ```
4. Confirm merge happened before closing beads:
   ```bash
   MERGED_OK=$(gh pr view "${PR_NUMBER}" --json state,mergedAt -q '.state == "MERGED" and (.mergedAt != null)')
   test "${MERGED_OK}" = "true"
   ```
5. Close this PR-review bead:
   ```bash
   bd close "${ISSUE_ID}" --reason "PR #${PR_NUMBER} reviewed and merged"
   ```
6. Close original implementation bead (if found):
   ```bash
   if [ -n "${ORIGINAL_ID}" ]; then
     bd close "${ORIGINAL_ID}" --reason "PR #${PR_NUMBER} merged after PR review"
   fi
   ```
7. Clean original worktree/branch (if found):
   ```bash
   if [ -n "${ORIGINAL_ID}" ]; then
     bd worktree remove ".worktrees/parallel-agents/${ORIGINAL_ID}" 2>/dev/null || true
     git -C "${REPO_ROOT}" branch -d "agent/${ORIGINAL_ID}" 2>/dev/null || true
   fi
   ```

If any guard fails:

1. Re-block this review bead and release lock:
   ```bash
   if [ "${MERGE_OK}" != "true" ]; then
     bd update "${ISSUE_ID}" \
       --status blocked \
       --remove-label review-running \
       --add-label pr-review \
       --add-label pr-review-task \
       --append-notes "Merge deferred for PR #${PR_NUMBER}: mergeStateStatus=${MERGE_STATE}, unresolved=${UNRESOLVED_COUNT}, required_non_green=${REQUIRED_NON_GREEN}, reviewDecision=${REVIEW_DECISION}."
   fi
   ```
2. If still blocked due conflicts/protection/check-gates, create follow-up:
   ```bash
   if [ "${MERGE_OK}" != "true" ] && \
      { [ "${MERGE_STATE}" = "DIRTY" ] || [ "${MERGE_STATE}" = "BLOCKED" ] || [ "${MERGE_STATE}" = "BEHIND" ] || [ "${REQUIRED_NON_GREEN}" -gt 0 ]; }; then
     MERGE_BLOCKER_JSON=$(bd create \
       "Resolve merge blockers for PR #${PR_NUMBER}" \
       --description="PR #${PR_NUMBER} is not mergeable yet (mergeStateStatus=${MERGE_STATE}) after review. Rebase/update head branch, satisfy required checks, then re-run PR review workflow." \
       -t task -p 1 --json)
     MERGE_BLOCKER_ID=$(echo "${MERGE_BLOCKER_JSON}" | jq -r '.id // .[0].id')

     if [ -n "${ORIGINAL_ID}" ] && [ -n "${MERGE_BLOCKER_ID}" ]; then
       bd dep add "${ORIGINAL_ID}" "${MERGE_BLOCKER_ID}"
     elif [ -n "${MERGE_BLOCKER_ID}" ]; then
       bd dep add "${ISSUE_ID}" "${MERGE_BLOCKER_ID}"
     fi
   fi
   ```
3. Keep this review bead blocked so coordinator can prioritize follow-up retry.

If you intentionally close the PR instead of merging (for example, superseded
or invalid), you must leave an explanatory PR comment first, then close:

```bash
gh pr comment "${PR_NUMBER}" --body "Closing PR #${PR_NUMBER}: <clear reason>."
gh pr close "${PR_NUMBER}"
```

## Constraints

- **NEVER operate in the main repository checkout.** All git operations
  (checkout, rebase, commit, push) must happen inside a dedicated worktree.
  Switching branches in the main repo disrupts the coordinator and other
  parallel workers. If `WORKTREE_PATH` is unset or equals `REPO_ROOT`, abort.
- **NEVER `cd` to `REPO_ROOT`.** Use absolute paths (e.g.,
  `${REPO_ROOT}/.worktrees/...`) or `git -C "${REPO_ROOT}"` when you need to
  reference the main repo. If you `cd` to `REPO_ROOT` and then run
  `git checkout`, you will switch the main repo off `main` and break
  everything. Always `cd "${WORKTREE_PATH}"` before git operations.
- Do not merge if unresolved issues remain.
- Do not close beads before PR merge.
- Do not merge draft PRs.
- Always rebase PR head onto latest base branch at the start of review
  (Phase 1 step 9), not just when fixes are needed.
- Resolve rebase conflicts logically (intent-preserving merges), not by blanket
  `--ours`/`--theirs` file replacement.
- Do not attempt merge when `mergeStateStatus` is `DIRTY`/`BLOCKED`/`BEHIND`.
- When no issues are detected, create and resolve a reviewer-worker marker
  thread before merge.
- If closing a PR, leave an explanatory comment before issuing close.
- On PR-driven flows, this reviewer worker may close PR-review/original beads
  only after confirmed PR merge. On direct-merge flows, coordinator closes the
  original bead after main is updated.
- The coordinator should verify final bead state after worker completion using
  `bd show` and `bd dolt status`.
- No `.beads/` changes should exist on the PR branch. If `.beads/` diffs are
  found, strip them from the feature branch (see Phase 1b).
  **Never stash, checkout main, or push main from a worktree** — this
  destroys the coordinator's uncommitted beads state.
- Do not modify unrelated files.

## Output Format

```
## PR Reviewer Report: <ISSUE_ID>

**Status**: merged-and-closed | blocked
**PR**: <url>
**Original Bead**: <id or unknown>

### Review Actions
- <thread-url-or-id>: fixed | answered | won't-fix (reason)
- <thread-url-or-id>: noted issue (new code-review thread)

### Merge Decision
- merged: yes | no
- reason: <why merged or why blocked>

### Bead Updates
- review bead: closed | blocked
- original bead: closed | unchanged
- cleanup: worktree/branch removed | skipped
```
