# GitHub Review Thread Operations

Use these patterns when replying to existing review threads, resolving them, or
creating new line-level review comments. Prefer the bundled helper scripts over
manual `gh api` commands so retries stay idempotent and outputs stay
machine-readable. Prefer review-thread comments over top-level PR comments when
the issue is anchored to code.

Helper scripts:
- `python3 scripts/reply_to_review_thread.py ...`
- `python3 scripts/resolve_review_thread.py ...`
- `python3 scripts/create_inline_review_comment.py ...`

## Reply To An Existing Review Thread

Use the numeric database ID of the top-level review comment from the thread.

```bash
gh api "repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}/comments" \
  -f body="${BODY}" \
  -F in_reply_to="${COMMENT_ID}"
```

Guidance:
- use `fixed`, `answered`, or `won't-fix` language explicitly
- reference the concrete change or rationale
- do not resolve the thread until the reply is truthful
- include a stable `--dedupe-key` on retries so duplicate replies are skipped

## Resolve A Review Thread

Use the GraphQL thread ID:

```bash
gh api graphql \
  -f query='
  mutation($threadId:ID!) {
    resolveReviewThread(input:{threadId:$threadId}) {
      thread { id isResolved }
    }
  }' \
  -F threadId="${THREAD_ID}"
```

Only resolve when:
- the fix is committed and verified, or
- the answer fully addresses the concern

## Create A New Inline Review Comment

Use the PR head commit SHA plus a concrete path and line:

```bash
HEAD_SHA=$(gh pr view "${PR_NUMBER}" --json headRefOid -q .headRefOid)

gh api "repos/${OWNER}/${REPO}/pulls/${PR_NUMBER}/comments" \
  -f body="${BODY}" \
  -f commit_id="${HEAD_SHA}" \
  -f path="${PATH}" \
  -F side='RIGHT' \
  -F line="${LINE}"
```

Guidance:
- prefer concise, actionable comments
- use this only for notable issues that should become resolvable threads
- do not use top-level timeline comments for merge-readiness tracking when a
  code anchor exists
- include a stable `--dedupe-key` on retries so duplicate comments are skipped

## Close A PR Instead Of Merging

If the correct outcome is to close the PR:

```bash
gh pr comment "${PR_NUMBER}" --body "Closing PR #${PR_NUMBER}: <clear reason>."
gh pr close "${PR_NUMBER}"
```

Always comment before closing.
