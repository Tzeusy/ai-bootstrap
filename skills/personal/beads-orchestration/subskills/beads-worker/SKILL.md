---
name: beads-worker
description: Use when implementing one cohesive Beads delivery package in a dedicated worker worktree after a coordinator or operator provides ISSUE_ID and WORKTREE_PATH.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
    - Claude Fable 5.1
  status: active
  last_reviewed: "2026-11-06"
compatibility: Requires a Beads-backed git repository with git worktrees, git, bd, jq, gh, and python3 available, plus authenticated GitHub access and network access for push and PR operations.
---

# Beads Worker

Implement a cohesive package in its isolated `agent/<ISSUE_ID>` worktree. ISSUE_ID
is an existing anchor; without a delivery manifest this remains a one-bead job.
The same implementation owner retains ordinary test/review corrections and related
packages until the accepted outcome is finished or explicitly handed off.

Use when dispatched with `ISSUE_ID`, `WORKTREE_PATH`, `REPO_ROOT` and optional
`DELIVERY_FILE`: “implement this package”, “correct this existing PR”, “continue
this accepted outcome”. Backlog processing without a dispatch uses
[beads-looper](../beads-looper/SKILL.md) or
[coordinator](../beads-coordinator/SKILL.md); authoring uses
[writer](../beads-writer/SKILL.md).

## Contract

Read [shared delivery model](../../references/delivery-model.md) for packages,
branch choices, evidence, recovery and per-member acceptance. This worker writes
code, commits, pushes and opens/updates its authorized PR. Its lifecycle controller
owns Beads writes; never claim/release/close or create follow-up issues here.
A looper applying these phases performs lifecycle updates separately as holder.

Dispatch authorizes accepted scope, tests, ordinary corrections, commits and push;
edit examples are guidance unless explicitly an ownership boundary. Resolve routine
engineering choices. Stop only for actual scope/trust/architecture/authorization
changes or inaccessible external capability under
[decision autonomy](../../references/decision-autonomy.md). Keep unaffected work going.
Do not spawn overlapping implementation tracks or commit Dolt-managed `.beads/`.

## Inputs and continuation

| Field | Meaning |
|---|---|
| ISSUE_ID | Existing package anchor; branch remains agent/<anchor> |
| WORKTREE_PATH / REPO_ROOT | Isolated worktree and actual shared repository root |
| DELIVERY_FILE | Optional beads-delivery/v1 manifest, required for a multi-bead package |
| Current packet locator | Current instructions, member AC, authority references and recovery state |
| REVIEW_CORRECTION_MODE=yes | Continue existing PR using EXISTING_PR_NUMBER, REVIEW_BEAD_ID and CORRECTION_THREADS_JSON |

Resume the same Claude session/Codex thread for corrections or a related package.
A new package revalidates cwd/branch/claims; guidance and relevant content evidence
carry over only while their assumptions hold. A fresh session is recovery with an
explicit published packet, never evidence of same-owner continuation by itself.

## Bootstrap

1. Set actual process cwd to WORKTREE_PATH; read
   [runtime contract](references/runtime-contract.md) for guidance discovery and
   protected/shared Git identity rules.
2. Invoke [assert_worker_context.py](scripts/assert_worker_context.py) by absolute
   skill path with `--worktree-path`, `--repo-root`, `--issue-id`, `--current-path`
   and, for a package, `--delivery-file`. It rejects an unrelated repository,
   protected/wrong branch, manifest mismatch or cwd mismatch. Stop and emit
   `invalid-runtime-context` if it fails.
3. Read target AGENTS/CLAUDE and
   [craft-and-care gate](../../references/craft-and-care-gate.md); reuse unchanged
   guidance on continuation. Read the concise current operative packet and exact
   referenced contracts/source. Fetch projected current fields only as needed;
   do not load every member's historical notes or inline archives.

## Implement and verify

Inspect the actual source before relying on planning assumptions. Implement logical
commits on the package branch, marking member IDs for traceability. Several related
corrections can share fixtures/tests, owner and PR; unrelated outcomes stay separate.
Preserve each member's actual acceptance and hard gates. Do not silently replace
an accepted feature with foundation-only scope.

Extend nearest relevant checks under
[test growth](../../references/test-growth-gate.md). Run scoped checks while iterating;
the full required gate runs on the landing tree in the repository-assigned tier
under [token efficiency](../../references/token-efficiency.md). Reuse unchanged
content evidence; refresh affected assumptions and time-sensitive runtime facts.
No local duplicate of a required hosted gate is mandated here. No lighter check
substitutes for a repo-required one. Finish applicable craft review before handoff.

Ordinary failing tests/CI and review findings stay with this owner. Correct and
push to the same PR, then send changed content and tests directly to the independent
reviewer. The controller receives state-change receipts, not permissions per hunk.
If a shared prerequisite/authority boundary is missing, name exactly its dependent
work and resume event; never create a second substrate implementation privately.

## Publish and handoff

Prefer one PR per cohesive package, targeting the approved integration base.
Push `agent/<ISSUE_ID>` and use `gh pr create --body-file` with actual newlines.
PR maps every member to acceptance/evidence and explicitly names partial scope.
Only the lifecycle controller sets anchor `external_ref` and one review relation.

In correction mode update EXISTING_PR_NUMBER; do not create a new PR/review record.
Use ordinary push for appended commits; `--force-with-lease` only for a justified
history rewrite. Verify PR head and base after pushing. Never put runtime session
URLs or session-attribution trailers in commits/PRs.

A direct-merge candidate is only a repository-permitted trivial change with an
independent verdict and the required local gate; a merge queue/required review
cannot be bypassed by calling it direct. When policy is unknown, use the PR path.
An intermediate integration branch is accumulation, never proof of main delivery.

On push/PR failure follow [runtime failure routing](references/runtime-contract.md):
one justified local retry, then a precise external-blocker receipt. Preserve useful
commits, remote branch and dirty/local-only work. Never delete a worktree because
review begins. Session preemption/recovery publishes packet/claims/head/findings and
explicit handoff rather than reallocating ordinary corrections.

## Report

Use [emit_worker_report.py](scripts/emit_worker_report.py); field schemas/examples
are in [worker-report.md](references/worker-report.md). Multi-bead reports include
`--delivery-file` and complete `--member-results-json` coverage, individually
satisfied, partial or blocked with evidence. Ready-for-review does not close any
member. Acceptance-inclusive runtime proof may still be unmet after source merge.

Statuses remain `completed-pr-opened`, `completed-direct-merge-candidate`,
`blocked-awaiting-coordinator`, `invalid-runtime-context`. “Completed” describes
this handoff, never the whole owner outcome. Include recovery state and exact resume
event when blocked. Current correctness discoveries stay in this package; genuinely
new behavior is reported separately after dedupe, without silently expanding scope.

Finish on a report, never a plan or promise. Search
[known errors](../../references/known-errors.md) before debugging an unfamiliar
tracker/PR failure and record newly confirmed reusable fixes there.
