# PR Review Reconciliation

Load this file when cleanup needs to inspect blocked Beads that are tied to a
GitHub pull request and report PR-state findings for the coordinator.

**Report-only for PR state.** Cleanup is NOT the PR-state mutator. It does not
`bd close` on `MERGED`, reopen on `CLOSED`-unmerged, or relabel beads from PR
outcome, and it does not create missing review beads or mutate GitHub review
threads. It runs the detection logic below, then records each finding (bead id,
PR number, observed state, recommended action) in the cleanup report's
"PR-state findings" section. The coordinator's Step 0 consumes those findings
and performs the actual mutations (and the post-closure branch deletion).

## Preconditions

- This pass performs no PR-driven bead mutation; it only inspects and reports.
- Canonical PR metadata (`external_ref=gh-pr:<N>`) lives on the original
  implementation bead only.
- `pr-review-task` beads must not set their own `external_ref`.
- `review-running` is only a lock label; it is not proof that a reviewer is
  still active.

## Pass 2: Blocked Original Beads With `pr-review`

```bash
PR_REVIEW_JSON=$(bd list --status=blocked --label pr-review --json --limit 0)
```

For each blocked bead with `pr-review` but not `pr-review-task`:

1. Resolve the PR number from `external_ref`:

```bash
PR_NUMBER=$(echo "${BEAD_JSON}" | jq -r '
  (.external_ref // "") as $ref |
  ($ref | capture("^gh-pr:(?<n>[0-9]+)$")?.n) // empty')
```

2. If no PR number is present, record a report finding (no bead mutation):
   `bead <id>: no canonical external_ref gh-pr:N found; recommend manual
   triage`.

3. Query GitHub:

```bash
PR_STATE_JSON=$(gh pr view "${PR_NUMBER}" --json state,mergedAt 2>&1)
```

4. Record a PR-state finding by observed state (detect, do not execute):

| PR state | Report finding + recommended action (for coordinator Step 0) |
|---|---|
| `MERGED` | Record: `<id>` blocked on merged PR #N; recommend close + post-closure worktree/branch cleanup. |
| `CLOSED` and not merged | Record: `<id>` blocked on closed-unmerged PR #N; recommend reopen, remove `pr-review`, re-triage. |
| `OPEN` | Record whether a corresponding `pr-review-task` bead exists; if missing, recommend coordinator self-heal. Do not create one here. |
| `gh` failure | Record the transient failure in the report; do not infer state. |

## Pass 3: Blocked `pr-review-task` Review Beads

```bash
PRT_JSON=$(bd list --status=blocked --label pr-review-task --json --limit 0)
```

For each review bead:

1. Resolve the original implementation bead from the description:

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

2. Resolve the PR number from the original bead's canonical `external_ref`:

```bash
if [ -n "${ORIGINAL_ID}" ]; then
  ORIG_JSON=$(bd show "${ORIGINAL_ID}" --json)
  PR_NUMBER=$(echo "${ORIG_JSON}" | jq -r '
    (.[0].external_ref // .external_ref // "") as $ref |
    ($ref | capture("^gh-pr:(?<n>[0-9]+)$")?.n) // empty')
fi
```

If needed, parse the PR URL from the review bead description as a fallback, but
do not write a new canonical `external_ref` onto the review bead.

3. Query GitHub:

```bash
gh pr view "${PR_NUMBER}" --json state,mergedAt
```

4. Record a PR-state finding by observed state (detect, do not execute):

| PR state | Original bead state | Report finding + recommended action (for coordinator Step 0) |
|---|---|---|
| `MERGED` | open / in_progress / blocked | Record: recommend closing the review bead and the original bead, plus post-closure worktree/branch cleanup. |
| `MERGED` | already closed | Record: recommend closing only the review bead. |
| `CLOSED` and not merged | any | Record: recommend closing the review bead, reopening the original and removing `pr-review` for re-triage. |
| `OPEN` | any | Leave both beads as-is. The only mutation cleanup may do here is the liveness `review-running` release (Pass 6) when no active worktree and no live actor exist — that is a lock repair, not PR-state mutation. |
| PR cannot be resolved | any | Record the unresolved finding in the report; do not mutate. |

Cleanup does not run `bd close`, reopen, or `--remove-label pr-review` on the
basis of PR outcome. Capture the recommendation in the report and let the
coordinator's Step 0 execute it.

## Missing Review Wiring

If the original bead is blocked on an open PR but no dedicated review bead can
be found:

- do not create a new review bead from cleanup
- append a note on the original bead or record it in the final report
- let the coordinator loop's self-heal path create or dedupe review wiring

That keeps cleanup focused on reconciliation rather than lifecycle creation.
