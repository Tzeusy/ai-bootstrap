---
name: beads-cleanup
description: Use when a Beads coordinator needs to reconcile stale worker state, PR-review bookkeeping, or orphaned worktrees before dispatching new work.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-04-12"
compatibility: Requires a Beads-backed git repository with `bd`, `git`, `gh`, `jq`, and git worktree support. Authenticated GitHub access is required for PR reconciliation and branch cleanup.
---

# Beads Cleanup

Run this skill before a `beads-coordinator` loop when stale worker state may
have been left behind by crashes, compaction, out-of-token exits, or missed
handoffs.

This skill is a read-heavy reconciliation pass. It repairs Beads metadata and
git artifacts; it does not implement code, dispatch workers, or invent new
workflow rules.

## Use This Skill When

- starting or resuming a `beads-coordinator` loop
- recovering after a crashed coordinator or killed worker
- auditing stuck `in_progress`, `blocked`, `pr-review`, or `review-running`
  state
- cleaning orphaned coordinator worktrees or branches tied to Beads issues

## Do Not Use This Skill When

- implementing the assigned issue itself
- performing normal ready-work selection or worker dispatch
- creating new beads for discovered work
- repairing GitHub review threads inside an active PR review worker

## Source Of Truth

This skill is a routing layer over the existing Beads operating model.

- Repository workflow and ownership model: `../../../../../README.md`
- Coordinator mutation authority, atomic claim, and stall-heartbeat rules:
  `../beads-coordinator/references/runtime-and-safety.md`
- Coordinator loop and PR-review lane behavior:
  `../beads-coordinator/references/coordinator-loop.md`
- PR-review worker closure boundary and review-lock vocabulary:
  `../beads-pr-reviewer-worker/SKILL.md`

If these sources disagree with this skill, fix this skill. Do not let cleanup
become a competing doctrine.

## Non-Negotiable Boundaries

- Never implement code.
- Never mutate a bead held by a live actor. Decide ownership by the bead's
  `assignee` plus a fresh stall heartbeat, per
  `../beads-coordinator/references/runtime-and-safety.md`.
- **Never mutate PR-review bead state from PR outcome.** Cleanup does not run
  `bd close` / reopen / PR-driven label changes in response to a PR being
  `MERGED` or `CLOSED`. It inspects PR state and **reports** the finding plus a
  recommended action; the coordinator's Step 0 is the sole PR-state mutator.
- Cleanup retains ownership of worktree / branch / Dolt hygiene and stale
  `review-running` lock release (a liveness repair, not PR-state
  reconciliation — see Pass 5b/Pass 6 in `local-state-reconciliation.md`).
- Never create new beads from cleanup. Missing wiring should be reported for the
  coordinator loop to self-heal.
- Never touch `.beads/dolt/` manually.
- Append notes for every bead mutation so later operators can see what cleanup
  changed and why.

## Load Only The Reference You Need

- [`references/local-state-reconciliation.md`](references/local-state-reconciliation.md)
  Load for stale `in_progress` claims, dependency unblocking, Dolt/worktree
  health, and stale `review-running` labels.
- [`references/pr-review-reconciliation.md`](references/pr-review-reconciliation.md)
  Load for blocked original `pr-review` beads and blocked
  `pr-review-task` review beads.
- [`references/reporting.md`](references/reporting.md)
  Load for the cleanup report shape, rig-routing notes, command quick reference,
  and final mutation summary.

## Workflow

1. Read `../beads-coordinator/references/runtime-and-safety.md` if you need the
   exact claim, stall-heartbeat, and mutation-authority rules before touching
   Beads state.
2. Run the relevant passes from the reference files in order, skipping mutation
   when evidence is incomplete or a bead is held by a live actor (fresh
   heartbeat). For PR-review beads, run detection only and report findings.
3. Keep canonical PR metadata on the original implementation bead only; review
   beads must not invent their own `external_ref`.
4. Clean worktrees and branches conservatively. Preserve anything that may still
   contain useful unpublished work.
5. Produce the structured report from `references/reporting.md` so the
   coordinator has a clear mutation ledger before dispatch begins.
