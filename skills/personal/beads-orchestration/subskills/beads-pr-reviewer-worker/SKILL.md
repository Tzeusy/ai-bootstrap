---
name: beads-pr-reviewer-worker
description: Use when a coordinator dispatches one `pr-review-task` bead for an existing GitHub PR needing thread triage, exact-head review, correction follow-up, or merge assessment in an isolated worktree.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
compatibility: Requires a Beads-backed git repository with git worktrees, bd, jq, gh, Python 3, authenticated GitHub access, and network access for review/merge operations.
---

# Beads PR Reviewer Worker

Review one dispatched `pr-review-task` bead and its existing PR. Triage
resolvable threads, assess the exact head against the current base and required
checks, then emit a validated report. Do not mutate Beads lifecycle state.

## Required context

- `ISSUE_ID`, `WORKTREE_PATH`, `REPO_ROOT`
- Optional projected `ISSUE_JSON`; otherwise fetch only fields needed to
  resolve the original implementation and PR.
- `MERGE_AUTHORIZED=yes|no` from the coordinator/operator. Readiness is evidence,
  never authority; absent explicit `yes`, do not merge.
- `MINIMUM_REQUIRED_CHECKS` from repository policy; default to `1` when no
  explicit policy exists.

## Non-Negotiable boundaries

- Start in `WORKTREE_PATH`; never operate in or `cd` to `REPO_ROOT`.
- Never run `bd create`, `bd update`, `bd dep add`, or `bd close`; coordinator
  is the sole mutation authority and owns locks/claims.
- Preserve reviewer independence. Semantic corrections are semantic regardless
  of line count and return to the original author or recovery worker.
- A reviewer-authored semantic change requires a fresh independent reviewer.
- Do not create hidden code-writing tracks or require synthetic no-issue
  comments.

## Start here

1. Attest isolated runtime context and GitHub auth. On failure, stop with
   `invalid-runtime-context` or `blocked-awaiting-coordinator`.
2. Use [`scripts/resolve_review_context.py`](scripts/resolve_review_context.py).
   Its `bd show` evidence must contain exactly one record whose ID matches the
   requested ID.
3. Load [review cycle](references/review-cycle.md) for branch preparation,
   thread triage, verification, exact-head/current-base readiness, and the
   authorized merge sequence.
4. Load [thread operations](references/thread-operations.md) only when replying,
   resolving, or creating a line-level finding. Its helpers are
   [`scripts/list_review_threads.py`](scripts/list_review_threads.py),
   [`scripts/reply_to_review_thread.py`](scripts/reply_to_review_thread.py),
   [`scripts/resolve_review_thread.py`](scripts/resolve_review_thread.py), and
   [`scripts/create_inline_review_comment.py`](scripts/create_inline_review_comment.py).
5. Load [failure protocol](references/failure-protocol.md) only for corrections,
   exceptional fixer work, retry limits, or blocked outcomes.
6. At handoff, load [reviewer report](references/reviewer-report.md) and use
   [`scripts/emit_reviewer_report.py`](scripts/emit_reviewer_report.py).

Other deterministic helpers:

- [`scripts/prepare_pr_branch.py`](scripts/prepare_pr_branch.py) rebases the PR
  head onto the fetched base, strips `.beads/` divergence, and reports both
  exact prepared head and base SHA. .beads branch-hygiene cleanup is
  non-semantic pre-review preparation.
- [`scripts/evaluate_merge_readiness.py`](scripts/evaluate_merge_readiness.py)
  fails closed on moved head, stale base, too few required checks, nonterminal
  required checks, unresolved threads, review rejection, or unsafe PR state.
- [`scripts/discover_quality_gates.py`](scripts/discover_quality_gates.py) gives
  candidates only when project guidance does not name gates.

For helper/trigger contract changes, load
[evaluation](references/evaluation.md) and run its validation tracks.

## Outcomes

Use exactly one: `merged-pr`, `corrections-required`, `pushed-review-fixes`,
`blocked-awaiting-coordinator`, or `invalid-runtime-context`.

The two-correction checkpoint applies after two substantive reopenings: keep
same-invariant repair on the existing PR with a rewritten failure matrix;
escalate a new subsystem, trust boundary, architecture prerequisite, or risk
class for spec/design triage. Never merge with unresolved threads, incomplete
check evidence, a moved exact head SHA, a stale base, or missing authority.
