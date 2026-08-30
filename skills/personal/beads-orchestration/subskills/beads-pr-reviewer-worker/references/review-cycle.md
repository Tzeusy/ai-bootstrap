# PR Review Cycle

Load after runtime and GitHub auth checks pass.

## Resolve and prepare

1. Resolve original issue, canonical PR, owner/repo, branches, and head SHA:

   ```bash
   CONTEXT_JSON=$(python3 scripts/resolve_review_context.py --issue-id "${ISSUE_ID}")
   ```

2. Record reviewer identity and risk tier (`high`, `standard`, `low`) using the
   coordinator runtime-and-safety policy. Load repo-owned craft-and-care when
   present.
3. Remove an obsolete original implementation worktree only when the
   coordinator contract authorizes that cleanup. Prepare the PR branch:

   ```bash
   PREP_JSON=$(python3 scripts/prepare_pr_branch.py \
     --base-branch "${PR_BASE_BRANCH}" --head-branch "${PR_HEAD_BRANCH}")
   ```

4. Stop on conflict/blocked output. Verify reported `head_commit` equals local
   `HEAD` and GitHub `headRefOid`. Retain reported `base_commit` for final
   current-base attestation. Any prepared-head push uses `--force-with-lease`.

The helper's `.beads` cleanup is authorized non-semantic hygiene. Any other
reviewer-authored change is semantic and requires the exceptional fixer path
plus a fresh independent reviewer.

## Triage review threads

List every page with `list_review_threads.py`; incomplete or ambiguous evidence
blocks review. For each unresolved thread, inspect code/tests and classify it:

- current-PR correctness -> `correction-required`, leave unresolved
- answered or won't-fix -> reply concretely; resolve only when truthful
- duplicate -> link the canonical finding, then resolve duplicate
- prerequisite/new behavior -> report for coordinator materialization

Anchor new notable findings to changed lines with stable dedupe keys. Default
to no code changes. Auth/authorization, approvals, persistence, migrations,
cross-schema access, concurrency, replay/idempotence, and data loss are semantic
regardless of line count.

## Verify and evaluate

Run documented project gates. If unclear, use `discover_quality_gates.py` as
candidate discovery, not blind truth. Iterate on targeted tests; redirect the
single final full gate to a log and read only status/failure tail.

Immediately before verdict:

```bash
REVIEWED_HEAD=$(git rev-parse HEAD)
MERGE_JSON=$(python3 scripts/evaluate_merge_readiness.py \
  --owner "${OWNER}" --repo "${REPO}" --pr-number "${PR_NUMBER}" \
  --reviewed-head "${REVIEWED_HEAD}" \
  --expected-base-sha "${PREPARED_BASE_SHA}" \
  --minimum-check-count "${MINIMUM_REQUIRED_CHECKS:-1}")
```

The helper must report `merge_ok: true`; local `HEAD` and GitHub head must still
equal `REVIEWED_HEAD`. It fails closed unless the PR is open/non-draft, base is
current, required-check count meets the declared minimum, all required checks
are terminal green/neutral/skipped, no unresolved threads remain, review is not
`CHANGES_REQUESTED`, and merge state is `CLEAN`, `HAS_HOOKS`, or `UNSTABLE`.

## Merge or report

Merge only if both conditions hold:

1. `MERGE_JSON.merge_ok == true`
2. the dispatched contract explicitly says `MERGE_AUTHORIZED=yes`

Then run `gh pr merge "${PR_NUMBER}" --squash` without deleting the branch and
confirm `gh pr view --json state,mergedAt,headRefOid` says merged at the reviewed
head. Coordinator owns bead closure and branch cleanup.

Otherwise report corrections/blockers. To close instead of merge, authorization
must be explicit; comment with the reason before `gh pr close`.
