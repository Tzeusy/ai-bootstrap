# PR Review Reconciliation

Load this file when cleanup needs to reconcile blocked Beads that are tied to a
GitHub pull request.

The cleanup skill does not create missing review beads or mutate GitHub review
threads. It only normalizes existing Beads state after confirming PR state.

## Preconditions

- Confirm there is no live foreign lease before mutating any bead.
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

2. If no PR number is present, append a note and skip mutation:

```bash
bd update <id> --append-notes "Cleanup: no canonical external_ref gh-pr:N found; needs manual triage"
```

3. Query GitHub:

```bash
PR_STATE_JSON=$(gh pr view "${PR_NUMBER}" --json state,mergedAt 2>&1)
```

4. Reconcile by PR state:

| PR state | Action |
|---|---|
| `MERGED` | `bd close <id> --reason "Cleanup: PR #${PR_NUMBER} already merged"` and clean the matching worktree/branch if safe. |
| `CLOSED` and not merged | `bd update <id> --status open --remove-label pr-review --append-notes "Cleanup: PR #${PR_NUMBER} closed without merge; needs re-triage"` |
| `OPEN` | Leave the original bead blocked. Verify a corresponding `pr-review-task` bead exists; if missing, append a note for coordinator self-heal rather than creating one here. |
| `gh` failure | Append a note or record it in the report, then skip mutation. |

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

4. Reconcile by PR state:

| PR state | Original bead state | Action |
|---|---|---|
| `MERGED` | open / in_progress / blocked | Close the review bead and the original bead after confirming no live foreign lease. Clean matching worktree/branch if safe. |
| `MERGED` | already closed | Close only the review bead. |
| `CLOSED` and not merged | any | Close the review bead. Reopen the original bead and remove `pr-review` so it can be re-triaged. |
| `OPEN` | any | Leave both beads as-is. Remove stale `review-running` only if no active worktree and no live foreign lease exist. |
| PR cannot be resolved | any | Append a note and skip mutation. |

When reopening the original bead after a closed-unmerged PR, use a note like:

```bash
bd update <original-id> --status open --remove-label pr-review \
  --append-notes "Cleanup: PR #${PR_NUMBER} closed, review bead closed; needs re-triage"
```

## Missing Review Wiring

If the original bead is blocked on an open PR but no dedicated review bead can
be found:

- do not create a new review bead from cleanup
- append a note on the original bead or record it in the final report
- let the coordinator loop's self-heal path create or dedupe review wiring

That keeps cleanup focused on reconciliation rather than lifecycle creation.
