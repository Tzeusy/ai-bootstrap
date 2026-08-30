---
name: beads-orchestration
description: >-
  Use for any Beads (`bd`) issue workflow in a Beads-backed repository:
  backlog execution, one dispatched implementation, PR-review follow-up,
  stale-state cleanup, or backlog authoring. Route to exactly one subskill.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
compatibility: Requires bd v1.0.4+ and git. Execution routes also require gh, jq, Python 3, and git worktrees.
---

# Beads Orchestration

Select one package-local workflow. Load only its `SKILL.md`; subskills are not
installed in the global catalog.

| Intent | Route |
|---|---|
| Process ready work, claim, dispatch, and reconcile. Sole owner of execution-time `bd create/update/dep/close`. | [beads-coordinator](subskills/beads-coordinator/SKILL.md) |
| Implement one issue after receiving `ISSUE_ID` and `WORKTREE_PATH`. | [beads-worker](subskills/beads-worker/SKILL.md) |
| Review one existing PR from a dispatched `pr-review-task` bead. | [beads-pr-reviewer-worker](subskills/beads-pr-reviewer-worker/SKILL.md) |
| Audit/reconcile stale claims, review state, or worktrees without running the loop. | [beads-cleanup](subskills/beads-cleanup/SKILL.md) |
| Create, decompose, or groom backlog items outside an execution run. | [beads-writer](subskills/beads-writer/SKILL.md) |

Routing boundaries:

- A backlog-processing request routes to coordinator, never directly to worker.
- Worker/reviewer requires a dispatched contract. Cleanup is preflight/recovery,
  not a loop. Writer yields mutation authority when execution begins.
- One-off read-only queries need no subskill. Project priority belongs to
  `th-projects`.
- Ambiguous author-and-execute requests need writer and coordinator as separate
  sequential phases, never two simultaneously loaded workflows.

Shared hard stops:

- Coordinator is the sole mutation authority during execution. Workers report;
  they do not mutate Beads lifecycle state.
- Standalone beads-writer may mutate backlog state during explicit authoring;
  it yields that authority before execution begins.
- Worktrees are `.worktrees/parallel-agents/<id>` on `agent/<id>`; never commit
  `.beads/`.
- Load [decision autonomy](references/decision-autonomy.md) only for a
  decision-shaped blocker.
- Load [token efficiency](references/token-efficiency.md) once before the first
  `bd`/`gh` loop; project JSON and tail verbose gate logs.
- On unexpected `bd` behavior, grep
  [known errors](references/known-errors.md) first:
  `rg -i -n '<distinctive error>' references/known-errors.md`. Read only the
  matching section; follow its maintenance contract for a genuinely new error.

Unloaded routing cases live in [`evals/routing.json`](evals/routing.json).
