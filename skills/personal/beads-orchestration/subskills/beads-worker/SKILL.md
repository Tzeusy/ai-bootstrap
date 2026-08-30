---
name: beads-worker
description: Use when implementing exactly one Beads issue in a dedicated worker worktree after a coordinator or operator provides ISSUE_ID and WORKTREE_PATH.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
compatibility: Requires a Beads-backed git repository with git worktrees, bd, jq, gh, Python 3, authenticated GitHub access, and network access for push/PR operations.
---

# Beads Worker

Implement one dispatched issue in its isolated worktree, verify it, push it,
and emit a structured handoff. You do not coordinate or mutate Beads lifecycle
state.

## Required context

- `ISSUE_ID`, `WORKTREE_PATH`, `REPO_ROOT`
- Optional `ISSUE_JSON`; otherwise fetch only
  `{id,title,description,acceptance_criteria,notes,design,labels,type,priority}`.
- Correction mode additionally requires `REVIEW_CORRECTION_MODE=yes`,
  `EXISTING_PR_NUMBER`, `REVIEW_BEAD_ID`, and `CORRECTION_THREADS_JSON`.

## Hard stops

- Work only inside `WORKTREE_PATH`, never `REPO_ROOT`.
- Branch must be `agent/<ISSUE_ID>` and must not be `main` or `master`.
- Never run `bd create`, `bd update`, `bd dep add`, or `bd close`; coordinator
  is the sole lifecycle mutation authority.
- Do not spawn code-writing helpers, create hidden implementation tracks, or
  commit `.beads/`.

## Start here

1. Run [`scripts/assert_worker_context.py`](scripts/assert_worker_context.py)
   before deep issue reading or edits. On failure, stop and use
   [`scripts/emit_worker_report.py`](scripts/emit_worker_report.py) with
   `invalid-runtime-context`.
2. Load [runtime contract](references/runtime-contract.md) for bootstrap,
   guidance discovery, gate discovery, and push/PR failure routing.
3. Read the projected issue and relevant code. If repo guidance exposes a
   project-owned `craft-and-care/SKILL.md`, load it before editing.
4. Load [execution flow](references/execution-flow.md) for implementation,
   verification, direct/PR/correction handoff, and blocker handling.
5. At handoff, load [worker report](references/worker-report.md) and emit it
   with [`scripts/emit_worker_report.py`](scripts/emit_worker_report.py).

Load [known worker errors](references/known-errors.md) only after a matching
worker-helper failure. Search first with `rg -i -n '<distinctive error>'` and
read only the matching section. For an unexpected `bd` failure, use the root
package's grep-first known-error catalog.

## Correction boundary

In correction mode, update the existing canonical PR branch and push with
`--force-with-lease`. Confirm the PR remains open and its `headRefOid` equals
the pushed SHA. Do not call `gh pr create`; report the existing PR so the
coordinator can restore exact-head independent review.

## Completion

Accepted statuses are `completed-pr-opened`,
`completed-direct-merge-candidate`, `blocked-awaiting-coordinator`, and
`invalid-runtime-context`. A worker may open or update an authorized PR but
never merges it. Never close or reclassify the bead.
