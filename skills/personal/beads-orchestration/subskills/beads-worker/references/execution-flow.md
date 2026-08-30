# Worker Execution Flow

Load after runtime attestation and issue projection succeed.

## Implement

1. Inspect dependencies and relevant code; form a focused file/test plan.
2. Make scoped changes following local conventions. Update tests and contract
   docs when behavior changes.
3. Keep all work in the assigned worktree. If the issue needs multiple writing
   tracks, stop and report decomposition instead of creating them.
4. Commit with `<type>: <summary> [<ISSUE_ID>]`. Never include session URLs or
   runtime-attribution trailers; plain `Co-Authored-By` is allowed.

## Verify

Use project-defined gates discovered through `runtime-contract.md`.

- Iterate on the smallest relevant test selection.
- Immediately before handoff, run the full defined gate once with quiet output
  redirected to a log. Read only exit status and failure tail.
- Re-run the failed subset after a failure, then the full gate once more.
- Apply any repo-owned craft-and-care bar to the actual diff: favor simple,
  explicit, fail-fast code; remove same-repo cruft; update docs/contracts in
  the same change; scale evidence to risk.

## Select handoff

Use PR review for security/auth/public APIs, schema changes, backward-
compatibility risk, or more than five files / 200 changed lines. Documentation,
config, test-only, or small single-file fixes may be direct-merge candidates.
When uncertain, open a PR.

### New PR

```bash
git push -u origin "agent/${ISSUE_ID}"
BASE=$(git remote show origin | sed -n 's/.*HEAD branch: //p')
PR_URL=$(gh pr create --base "${BASE}" --head "agent/${ISSUE_ID}" \
  --title "<type>: <summary> [${ISSUE_ID}]" --body "<changes and why>")
```

Extract the PR number from `PR_URL` and verify state, base/head names, and
`headRefOid` with an explicit `gh pr view --json ...` field list.

### Direct-merge candidate

Push `agent/${ISSUE_ID}` and report `completed-direct-merge-candidate`. This is
a handoff classification, not merge authorization.

### Existing-PR correction

When `REVIEW_CORRECTION_MODE=yes`:

1. Treat `CORRECTION_THREADS_JSON` and coordinator-updated acceptance criteria
   as the bounded task.
2. Push `agent/${ISSUE_ID}` with `--force-with-lease`.
3. Verify `EXISTING_PR_NUMBER` is open, targets this branch, and reports the
   pushed exact head SHA.
4. Do not create a second PR. Report `completed-pr-opened` with the existing PR
   URL and number so independent review can resume.

## Blockers and discoveries

A choice between sound implementations is not a blocker. For a decision-shaped
obstacle, load the root `references/decision-autonomy.md`, decide unless it
names a hard gate, and record `[decision]` in the summary.

For out-of-scope work over two minutes, add a concrete object to
`Discovered-Follow-Ups-JSON`; do not create a bead.

On a real external blocker:

1. Record the exact failing command and unblock event.
2. Commit useful partial work and push it when remote recovery helps.
3. Report `blocked-awaiting-coordinator` with recovery state, remote branch,
   dirtiness, unpushed-commit state, and non-empty `Blockers-JSON`.
4. Never mutate Beads lifecycle state.
