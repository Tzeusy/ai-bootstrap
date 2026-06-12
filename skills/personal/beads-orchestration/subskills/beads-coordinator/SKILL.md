---
name: beads-coordinator
description: Coordinate Beads issue execution by continuously selecting the highest-priority ready issue from `bd ready`, claiming it atomically with `bd update --claim`, and dispatching a fresh worker in an isolated beads worktree. Use for unattended parallel issue throughput in Beads-backed repos.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-06-12"
compatibility: Requires a Beads-backed repository with `bd` v1.0.4+, `git`, an authenticated `gh`, `jq`, git worktree support, and network access for `gh` PR operations.
---

# Beads Coordinator

Run a coordinator loop that repeatedly pulls ready Beads work and fans it out to
parallel workers in isolated branches and worktrees. This skill is a routing
layer over the Beads operating model in [`../../../../../README.md`](../../../../../README.md);
it coordinates, it never implements code.

This router states the non-negotiable invariants once, then points at the
reference that owns each detailed procedure. Load only the reference you need.

## Use This Skill When

- "while true, tackle the next highest-priority Beads issue"
- "dispatch each Beads issue to a new parallel agent"
- "keep N workers processing the `bd ready` backlog"
- "coordinate beads work across parallel agents"

## Do Not Use This Skill When

- implementing a single assigned issue yourself: use `../beads-worker/SKILL.md`
- reviewing one open PR: use `../beads-pr-reviewer-worker/SKILL.md`
- only reconciling stale state before a run: use `../beads-cleanup/SKILL.md`
- authoring or decomposing backlog beads: use `../beads-writer/SKILL.md`

## Non-Negotiable Invariants

State these hold for the entire run; the references elaborate, never override.

- **Sole mutation authority.** The coordinator owns every canonical Beads
  lifecycle mutation (`bd create`, `bd update`, `bd dep add`, `bd close`).
  Workers read state, push code, and report; they never mutate Beads lifecycle.
- **Claim atomically, then mutate as assignee.** Claim with
  `bd update <id> --claim` (atomic; sets `assignee` + `in_progress`). Before
  mutating a bead, confirm you are its `assignee` and renew the stall heartbeat.
  Never mutate a bead assigned to another live actor; the notes heartbeat is
  stall detection, not mutual exclusion.
- **Closure only after merge confirmation.** A bead is closed only after the
  coordinator confirms its change reached `main` (direct fast-forward merge) or
  its PR is merged. Workers never call `bd close`.
- **Native dispatch only.** Spawn workers through the runtime's native subagent
  mechanism. Never shell out to `claude`/`codex`/`opencode`/`gemini` binaries.
- **`.beads/` is Dolt-managed.** Beads data lives in the Dolt DB, not git-tracked
  files. Never commit `.beads/` contents on a code branch; strip accidental
  `.beads/` diffs.

## Read Order

| File | Read when you need to | Owns |
|------|-----------------------|------|
| [`references/coordinator-loop.md`](references/coordinator-loop.md) | run the cycle | Exact steps 0-8, PR-review priority lane, worker bootstrap, report contracts, reconciliation, progress report, adaptive polling |
| [`references/runtime-and-safety.md`](references/runtime-and-safety.md) | dispatch or mutate safely | Model-selection tables, atomic `--claim` + stall-heartbeat model + thresholds, mutation safety, closure rule, runtime dispatch notes, quality gates |
| [`references/epic-coordination.md`](references/epic-coordination.md) | the bead is an epic or a worker hits a hard blocker | Epic classification, independent dispatch, Team Lead mode + prompt, blocker handling |
| [`references/commands.md`](references/commands.md) | a quick command lookup | `bd` quick reference, claim/heartbeat checklist, session-completion checklist |


Diagrams (load only when you need a visual of the flow): the full cycle is
[`assets/coordinator-cycle.svg`](assets/coordinator-cycle.svg) and the
PR-review priority lane is
[`assets/pr-review-lane.svg`](assets/pr-review-lane.svg); editable sources are
[`assets/coordinator-cycle.excalidraw`](assets/coordinator-cycle.excalidraw) and
[`assets/pr-review-lane.excalidraw`](assets/pr-review-lane.excalidraw).

## Rig Targeting

`bd create`, `bd list`, and `bd ready` default to the `.beads/` DB discovered
from `$PWD`. To target a different project (running from the mayor or town root),
use the global `-C <path>` flag to point `bd` at the rig's workspace, e.g.
`bd -C /path/to/rig list --status=open`. Do not rely on bead-ID prefixes
auto-routing to the right DB — that fails across embedded-mode workspaces
(see `../../references/known-errors.md`); pass `-C` explicitly.

## Dispatch Quickstart

1. Run `../beads-cleanup/SKILL.md` before entering the loop. Mandatory.
2. Create a coordinator session ID for this run (the stall-heartbeat owner).
3. Loop the steps in `references/coordinator-loop.md`: normalize the PR-review
   lane (Step 0), then atomically `--claim` and dispatch ready work.
4. Build a **compact** dispatch prompt carrying `ISSUE_ID`, `WORKTREE_PATH`,
   `REPO_ROOT`, and a 2-4 line issue summary plus acceptance criteria. Do not
   inline full `bd show` JSON; the worker self-fetches if it needs more.
5. Choose the worker skill by issue type:
   - default implementation issue → `../beads-worker/SKILL.md`
   - `pr-review-task` issue → `../beads-pr-reviewer-worker/SKILL.md`
   - epic-complexity issue → Team Lead, see `references/epic-coordination.md`
6. Pick the model per the assignment rules in `references/runtime-and-safety.md`.
7. Require bootstrap proof (`pwd == WORKTREE_PATH`, expected branch, not
   `REPO_ROOT`) before counting a worker as running.

Worker skill paths (when a runtime needs the absolute location):
- `~/.claude/skills/beads-orchestration/subskills/beads-worker/SKILL.md`
- `~/.claude/skills/beads-orchestration/subskills/beads-pr-reviewer-worker/SKILL.md`
