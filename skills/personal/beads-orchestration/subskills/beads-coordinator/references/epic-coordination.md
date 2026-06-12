# Epic Coordination

Load this file only when the selected bead is an epic or when a worker reports
a hard blocker that needs new bead creation.

## Epic Decomposition

Do not dispatch epics to workers directly. First classify the epic's complexity
to choose between independent dispatch and team coordination mode.

### Classification Heuristics

| Signal | Points toward epic complexity |
|---|---|
| Cross-cutting scope across API + frontend + DB + tests | yes |
| Tightly coupled subtasks | yes |
| Integration risk across separate branches | yes |
| Shared design decisions needed up front | yes |
| More than 3 interdependent children | yes |
| Independent, parallelizable subtasks | no; use independent dispatch |
| Purely additive work | no; use independent dispatch |

Default to independent dispatch. Escalate to team coordination mode only when
two or more positive signals are present.

## Independent Dispatch

1. Inspect children:
   ```bash
   bd children <epic-id> --json
   ```
2. If children exist, dispatch each ready child as a separate worker.
3. If no children exist, the coordinator must create the child beads
   sequentially before dispatch:
   ```bash
   CHILD_JSON=$(bd create "<subtask title>" \
     --description="<details>" \
     -t task -p <priority> \
     --json)
   CHILD_ID=$(echo "${CHILD_JSON}" | jq -r '.id // .[0].id')
   bd dep add <epic-id> "${CHILD_ID}"
   ```
4. Then dispatch the subtasks.

## Team Coordination Mode

When the heuristics indicate tightly coupled work, dispatch a Team Lead agent
instead of individual workers. The Team Lead is a high-capability model
(`EPIC_COMPLEXITY_MODEL`) that acts as a mini-coordinator for code work, but it
does not own Beads lifecycle mutations.

### Slot Reservation

A Team Lead reserves all available worker slots for the duration of its
execution unless `team_size` is explicitly constrained.

While a Team Lead is active:
- no new independent workers are dispatched
- the coordinator continues looping, but only for PR-review handling and
  monitoring

### Team Lead Rules

- The Team Lead may plan and integrate code work.
- The Team Lead may spawn code-writing subworkers.
- Every code-writing subworker must have its own worktree and branch.
- The Team Lead must not ask multiple writers to share a worktree.
- The Team Lead must not run `bd create`, `bd update`, `bd dep add`, or
  `bd close`.
- If new child beads are needed, the Team Lead reports proposals and the
  coordinator creates them sequentially.

### Team Lead Dispatch

1. Label the epic:
   ```bash
   bd update <epic-id> --add-label team-coordination
   ```
2. Claim it with the coordinator lease.
3. Create Team Lead worktree:
   ```bash
   bd worktree create .worktrees/parallel-agents/<epic-id> --branch agent/<epic-id>
   ```
4. Build prompt:

```text
You are a Team Lead for an epic-complexity issue. Your job is to architect,
coordinate sub-workers, integrate their output, and deliver one consolidated
PR.

ISSUE_ID: <epic-id>
WORKTREE_PATH: <team-lead-worktree-path>
REPO_ROOT: <repo-root>
TEAM_SIZE: <number of sub-workers you may spawn>

Issue details:
<bd show --json output>

Rules:
- Do not mutate Beads lifecycle.
- If you need follow-up beads, report concrete proposals for the coordinator.
- Every code-writing subworker must get its own worktree and branch.
- You own integration and final verification.
```

5. Dispatch using `EPIC_COMPLEXITY_MODEL`.

### Team Lead Subworker Isolation

Recommended naming:
- Team Lead branch: `agent/<epic-id>`
- Subworker branch: `agent/<epic-id>/<slice-id>`
- Subworker worktree:
  `.worktrees/parallel-agents/<epic-id>-<slice-id>`

The Team Lead integrates subworker branches into `agent/<epic-id>` after each
subworker completes.

### Monitoring Team Leads

Use the same monitoring process as normal workers, with these additions:
- Team Leads get 3x the normal stall timeout before intervention.
- If a Team Lead stalls but has pushed sub-branches:
  1. check which slices are complete versus still open
  2. release the epic back to `open` with a note listing completed work
  3. on the next cycle, re-evaluate whether a fresh Team Lead should finish
     integration only
- When the Team Lead finishes, apply the same closure rule as regular workers.

## Handling Blockers

If a worker or Team Lead reports a hard blocker:

1. The coordinator creates a blocker issue:
   ```bash
   BLOCKER_JSON=$(bd create "Blocker: <description>" \
     --description="<details>" \
     -t bug -p 0 \
     --json)
   BLOCKER_ID=$(echo "${BLOCKER_JSON}" | jq -r '.id // .[0].id')
   bd dep add <original-id> "${BLOCKER_ID}"
   ```
2. The coordinator releases the original issue back to `open` or `blocked` as
   appropriate.
