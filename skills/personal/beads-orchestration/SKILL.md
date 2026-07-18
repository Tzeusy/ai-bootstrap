---
name: beads-orchestration
description: Use for any Beads (`bd`) issue workflow in a Beads-backed repository — coordinating unattended execution of ready issues across parallel workers, implementing a single dispatched issue in a worktree, handling PR-review follow-up tasks, reconciling stale worker/PR/worktree state, or creating and decomposing backlog issues. Route to exactly one subskill per task.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-07-18"
compatibility: Requires bd (beads) CLI v1.0.4+, git, and a Beads-backed repository. Execution subskills additionally require gh (authenticated), jq, python3, and git worktree support.
---

# Beads Orchestration

Superskill router for the Beads issue-execution fleet. Five subskills live under
`subskills/`; each is a complete standard skill package (own `SKILL.md`,
`references/`, `scripts/`). Subskills are **not** installed in the global skill
catalog — discover them lazily from this package, and load **at most one**
subskill body per task (the coordinator may additionally point dispatched
workers at a second one; the workers load it themselves).

## Discover subskills

```bash
find "$(dirname "$SKILL_PATH")/subskills" -maxdepth 2 -name SKILL.md
rg -n "^name:|^description:" subskills/*/SKILL.md
```

## Routing table

| Task intent | Subskill | Typical trigger |
|---|---|---|
| Run the unattended loop: select ready issues, claim, dispatch workers, reconcile outcomes. Owns ALL `bd` lifecycle mutations. | [subskills/beads-coordinator/SKILL.md](subskills/beads-coordinator/SKILL.md) | "while true, tackle the next issue", "keep N workers processing the backlog" |
| Implement exactly one Beads issue; requires ISSUE_ID and WORKTREE_PATH from a coordinator or operator. | [subskills/beads-worker/SKILL.md](subskills/beads-worker/SKILL.md) | Dispatched with a worker contract for one implementation bead |
| Process one `pr-review-task` bead: triage threads, report corrections to the implementation lane, attest exact-head merge readiness. | [subskills/beads-pr-reviewer-worker/SKILL.md](subskills/beads-pr-reviewer-worker/SKILL.md) | Dispatched with a `pr-review-task` bead for an open GitHub PR |
| Reconcile stale worker state, PR-review bookkeeping, and orphaned worktrees before dispatching new work. | [subskills/beads-cleanup/SKILL.md](subskills/beads-cleanup/SKILL.md) | Coordinator preflight; recovery after a crashed loop; "clean up stale beads state" |
| Create or decompose backlog issues: features, bugs, epics, grooming, vague ask → actionable beads. | [subskills/beads-writer/SKILL.md](subskills/beads-writer/SKILL.md) | "file beads for X", "break this epic down", backlog grooming |

## Routing rules

- **Coordinator vs. worker**: if the request is to *process the backlog*, route
  to the coordinator — never start implementing issues yourself. Route to a
  worker subskill only when a coordinator/operator has already supplied the
  worker contract (ISSUE_ID, WORKTREE_PATH).
- **Cleanup is a preflight, not a loop**: the coordinator invokes it before its
  first cycle; route to it directly only for explicit recovery/audit asks.
- **Writer is standalone**: backlog creation needs no worktrees and no
  coordinator; it never dispatches execution.
- **Fallback**: if the task is Beads-adjacent but none of the rows fit (e.g.
  one-off `bd` queries, project prioritization), do not load a subskill — use
  plain `bd` commands or a dedicated skill such as `th-projects`
  (project-direction subskill).

## Shared invariants (all subskills)

- During an execution run, the coordinator is the **sole mutation authority**
  for canonical lifecycle state (`bd create/update/dep/close`); dispatched
  workers and cleanup report instead of mutating. The standalone beads-writer
  may create/update/depend backlog items during explicit authoring before
  dispatch, but hands mutation authority to the coordinator once execution
  starts.
- Worktrees live at `.worktrees/parallel-agents/<id>` on branch `agent/<id>`.
- `.beads/` is Dolt-backed and gitignored — never commit it to code branches.
- bd 1.0.4 has no `--rig` flag: target another project with `bd -C <path> …`.
- **Decide, don't defer.** Engineering-judgment choices are resolved
  autonomously per [`references/decision-autonomy.md`](references/decision-autonomy.md);
  blocking on a human is reserved for its hard-gate list. Load that file before
  filing or reconciling any decision-shaped blocker.

## When `bd` itself misbehaves

On any unexpected `bd` error (connection failures, unknown flags, refused
mutations, weird exit states), load
[`references/known-errors.md`](references/known-errors.md) **before**
debugging from scratch — it catalogs known errors, deprecations, and
workarounds. If you hit a rough edge that is not listed, append an entry
after resolving it: that file is this skill's persistent memory, and an
unrecorded fix gets re-debugged by the next session.
