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
- do a semantic close-out pass first: restate the request, compare it against
  the current diff and tests, and check repo-local doctrine or contract docs if
  the concern touches behavior or wording
- use `Accepted in <commit>.` followed by `Reason: ...` or `Wontfix.` followed
  by `Reason: ...` explicitly
- include the concrete change, verification, or justification in one sentence
- do not resolve the thread until the reply is truthful and terminal
- include a stable `--dedupe-key` on retries so duplicate replies are skipped
- validate the body with `python3 scripts/validate_review_text.py --kind reply`
  before posting if you are building the reply text manually
- do not quote reviewer text verbatim if it contains personal data, secrets, or
  other sensitive material; paraphrase and redact instead
- the bundled reply and resolve helpers enforce the same terminal/safety
  contract, so let them fail closed instead of bypassing them

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
- the answer fully addresses the concern, and
- the latest reply passes the terminal reply and text-safety validator

If the latest reply is not terminal or contains unsafe text, fix the reply
first. Closing the thread without a valid terminal reply is a contract
violation, not a convenience step.

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
- validate the body with `python3 scripts/validate_review_text.py --kind comment`
  before posting if you are drafting the text manually

## Close Out Semantics

Before you close a thread, run the semantic pass in your head:

1. Rephrase the review request without changing its meaning.
2. Check the current diff, tests, and repository guidance against that request.
3. Decide whether the request is now satisfied or whether the correct outcome is
   a reasoned `Wontfix`.
4. If the reply would expose PII or secrets, rewrite it before posting.
5. Only then call the resolve helper.

## Close A PR Instead Of Merging

If the correct outcome is to close the PR:

```bash
gh pr comment "${PR_NUMBER}" --body "Closing PR #${PR_NUMBER}: <clear reason>."
gh pr close "${PR_NUMBER}"
```

Always comment before closing.
