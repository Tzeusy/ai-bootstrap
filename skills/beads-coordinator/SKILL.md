---
name: beads-coordinator
description: Coordinate Beads issue execution by continuously selecting the highest-priority ready issue from `bd ready`, claiming it, and dispatching a fresh worker in an isolated beads worktree. Use for unattended parallel issue throughput in Beads-backed repos.
---

# Beads Coordinator

## Overview

Run a coordinator loop that repeatedly pulls ready Beads work and fans it out
to parallel workers with isolated branches and worktrees. Each worker receives
either:
- the **beads-worker** skill prompt for implementation issues, or
- the **beads-pr-reviewer-worker** skill prompt for `pr-review-task` issues.

Worker prompts:
- `~/.claude/skills/beads-worker/SKILL.md`
- `~/.claude/skills/beads-pr-reviewer-worker/SKILL.md`

**The coordinator never implements code. It coordinates.**

## Use This Skill When

- "while true, tackle the next highest-priority Beads issue"
- "dispatch each Beads issue to a new parallel agent"
- "keep N workers processing `bd ready` backlog"
- "coordinate beads work across parallel agents"

## Model Selection Strategy

The coordinator has discretion on the model being used for subagents based on the nature of the task.

### Complexity Constants
| Strategy | Models (Subject to change) |
|---|---|
| **EPIC_COMPLEXITY_MODEL** | Opus 4.6, gpt-5.3-codex, gemini-3-pro |
| **HIGH_COMPLEXITY_MODEL** | Sonnet 4.6, gpt-5.3-codex, gemini-3-pro |
| **MEDIUM_COMPLEXITY_MODEL** | Sonnet 4.6, gpt-5.3-codex, gemini-3-pro |
| **LOW_COMPLEXITY_MODEL** | 4.5 Haiku, gpt-5.3-codex-spark, gemini-3-flash-preview |

### Assignment Rules
| Task Type | Model Complexity |
|---|---|
| **Epic / Team-coordinated work** | EPIC_COMPLEXITY_MODEL (team lead — see Team Coordination Mode) |
| **Planning, Research, Architecting** | HIGH_COMPLEXITY_MODEL |
| **Coding** | MEDIUM_COMPLEXITY_MODEL (unless trivial) |
| **Orchestration** | HIGH_COMPLEXITY_MODEL |
| **Simple Bugfixes** | MEDIUM_COMPLEXITY_MODEL (Coordinator discretion) |
| **Formatting, Linting** | LOW_COMPLEXITY_MODEL |

## Coordinator Loop

**Before entering the loop**, run the `/beads-cleanup` skill to audit and repair stale state left
by killed/crashed workers. This is mandatory — do not skip it.

**Rig targeting:** If running from outside the target rig (e.g., from the mayor
or town root), pass `--rig <rig>` to `bd create`, `bd list`, and `bd ready` so
they query the correct project database. Commands that accept an existing bead
ID (`bd update`, `bd close`, `bd show`, `bd dep`) auto-route via prefix-based
routing and do not need `--rig`. **Note:** `bd search`, `bd blocked`, `bd count`,
and `bd query` do **not** support `--rig` — use `bd list --rig <rig>` with
filters as a workaround.

Follow this loop. Use the current runtime's **native subagent dispatch** to
spawn workers (e.g., Task tool in Claude Code, subagent in Codex, etc.).
**Never shell out to `codex`/`claude`/`opencode`/`gemini` binaries directly.**

### Constraints

| Constraint | Value |
|---|---|
| Max parallel workers | **3 by default** (overrideable, e.g. 4 when explicitly requested) |
| Worker isolation | Each worker gets its own **beads worktree** and branch |
| Worktree creation | `bd worktree create` (isolated code checkout for `agent/<issue-id>`) |
| Branch naming | `agent/<issue-id>` |
| Worktree root | `.worktrees/parallel-agents/` |
| Worker bootstrap | Mandatory: worker must prove `pwd` = `WORKTREE_PATH` and branch = expected worker branch before being counted as running |
| Issue tracker | `bd` CLI only — no markdown TODOs, no external trackers |
| Rig routing | `bd create/list/ready` default to whichever `.beads/` DB is discovered from `$PWD`. **If running from a different directory (e.g., mayor or town root), pass `--rig <rig>` to target the correct project.** Commands that take an existing bead ID (`bd update`, `bd close`, `bd show`, `bd dep`) auto-route via the ID prefix. **Note:** `bd search`, `bd blocked`, `bd count`, `bd stale`, and `bd query` do **not** support `--rig` — use `bd list` with filters instead (e.g., `bd list --rig <rig> --status=open` to find issues), or `cd` into the rig's workspace directory first. |
| Metadata persistence | Dolt DB (`.beads/dolt/`) via auto-started sql-server; shared across worktrees via redirect |
| PR review cooldown | **5 minutes** after PR `createdAt` before dispatching reviewer (lets external bots post comments first) |
| **Bead closure rule** | See **Bead Closure Rule** section below. |
| **Bead mutation safety** | See **Bead Mutation Safety** section below. |

### Bead Mutation Safety

> **CRITICAL: Beads data lives in Dolt DB, not in git-tracked files.**
>
> `bd create/update/close/dep` mutate the Dolt database directly. The Dolt
> sql-server is auto-started when needed. Worker worktrees share the same DB
> via redirect files created by `bd worktree create`.
>
> **Rules:**
> 1. **Workers only push code.** Workers may read Beads state, but coordinator
>    owns canonical lifecycle mutations (`bd close`, review-bead creation, and
>    status normalization) from `REPO_ROOT`.
> 2. **Keep Dolt server healthy.** Run `bd dolt status` to verify the server
>    is running before heavy mutation loops.
> 3. **Never commit `.beads/` contents on code branches.** The `.beads/`
>    directory is gitignored; accidental `.beads/` diffs on code branches
>    must be stripped.
> 4. **Create beads sequentially.** Never create multiple beads in parallel —
>    this races on the ID counter, causing collisions that overwrite existing
>    beads. Use `&&`-chained sequential commands.
> 5. **Do NOT use `--deps discovered-from:`** in `bd create` — this flag can
>    cause a SIGSEGV panic. Create the bead first, then wire the dependency
>    separately with `bd dep add`.
> 6. **Use `bd dolt commit/push/pull` for Dolt version control**, not manual
>    file surgery. Use `bd vc status` to check for uncommitted changes.

### Bead Closure Rule

> **CRITICAL closure boundary:**
>
> A bead may ONLY be closed when one of these conditions is met:
> 1. **Direct merge (trivial/simple changes)** — the worker pushes `agent/<id>`
>    and reports `direct-merge-candidate`. The coordinator (Step 7) fast-forward
>    merges the branch to `main` and closes the bead.
> 2. **GitHub PR raised** — the worker pushes branch and opens PR (or
>    coordinator opens it during reconciliation). The coordinator:
>    - blocks the original bead and stores `external_ref=gh-pr:<N>`,
>    - creates a dedicated PR-review bead (title:
>      `Conduct a thorough code review of <PR_URL>`),
>    - links dependency direction `original -> depends on -> PR-review` via
>      `bd dep add <original> <pr-review>`,
>    - labels review bead `pr-review` + `pr-review-task`.
>    Then Step 0 dispatches `beads-pr-reviewer-worker` for review/merge.
>
> Implementation workers (`beads-worker`) must never call `bd close` and should
> not run lifecycle mutations (`bd create/update/dep`) for assigned issue flow.
> `beads-pr-reviewer-worker` may close review/original beads only after it has
> confirmed the PR is merged.

### 0. Check PR-review issues (priority lane)

Before discovering new work, and whenever a worker frees a slot, check for
beads that are blocked on PR review:

```bash
bd list --status=blocked --label pr-review --json
```

The list may include:
- blocked original implementation beads (waiting on PR outcome)
- blocked dedicated PR-review beads (label `pr-review-task`)

Canonical PR metadata is stored on the original implementation bead only.
For each blocked issue:
- if it is an original bead (no `pr-review-task` label), read its own
  `external_ref` (`gh-pr:<number>`).
- if it is a dedicated `pr-review-task` bead, first resolve its original bead
  ID (description/dependency), then read that original bead's `external_ref`.

If no PR number can be resolved, append a note and skip mutation for that bead.
When PR number is available, check state:

```bash
gh pr view <number> --json state,mergedAt,createdAt
```

Handle each case:

| PR State | Action |
|---|---|
| **MERGED** | `bd close <id> --reason "PR #<number> merged"`. Clean up worktree + branch. |
| **CLOSED** (not merged) | `bd update <id> --status open --remove-label pr-review --remove-label pr-review-task --remove-label review-running --append-notes "PR #<number> closed without merge — needs re-triage"`. |
| **OPEN** + `pr-review-task` label | **Review cooldown**: Do NOT dispatch a PR-review worker until at least **5 minutes** have elapsed since the PR's `createdAt` timestamp. This gives external review bots (Gemini Code Assist, CodeRabbit, Codex, etc.) time to post their comments before the reviewer worker pulls threads. If the cooldown has not elapsed, skip this bead for now — it will be picked up on a future coordinator cycle. Once the cooldown has passed: if a worker slot is available, acquire lock and dispatch `beads-pr-reviewer-worker`: `bd update <id> --status in_progress --add-label review-running --json`, then dispatch. If dispatch fails, revert to blocked: `bd update <id> --status blocked --remove-label review-running --json`. If no slot is available, leave the bead blocked/unlocked so it is first in line the moment a slot opens. |
| **OPEN** (without `pr-review-task`) | No action. This is typically the original implementation bead waiting on review/merge. |
| **gh fails** | Log warning, skip. Do not change the bead on transient errors. |

Priority rule:
- If any `pr-review-task` bead is dispatchable and a slot is open, dispatch it
  before selecting from `bd ready`.
- Do not start new implementation work while a dispatchable `pr-review-task`
  is waiting for an open slot.
- After each coordinator cycle, re-run a PR-state normalization pass
  (`blocked` + `pr-review` / `pr-review-task`) before dispatching more workers,
  rather than assuming prior status updates remained authoritative.

Self-heal rule (mandatory each cycle):
- Reconcile open PRs back into Beads even if workers failed to mutate metadata.
- Scan open PRs with `headRefName` matching `agent/<issue-id>`.
  ```bash
  gh pr list --state open --json number,url,headRefName,createdAt
  ```
- For each match:
  - ensure original bead has `status=blocked`, `external_ref=gh-pr:<N>`,
    and `pr-review` label.
  - ensure a dedicated `pr-review-task` bead exists. If missing, create it
    sequentially, then wire dependency with `bd dep add`.
  - keep canonical PR reference only on the original bead.

Safe PR-review bead creation pattern:
```bash
REVIEW_JSON=$(bd create \
  "Conduct a thorough code review of ${PR_URL}" \
  --description="Review PR ${PR_URL} thoroughly. Original implementation bead: ${ORIGINAL_ID}. Leave PR comments on notable issues and resolve each thread with a verdict." \
  -t task -p 1 --json)
REVIEW_ID=$(echo "${REVIEW_JSON}" | jq -r '.id // .[0].id')
bd dep add "${ORIGINAL_ID}" "${REVIEW_ID}"
bd update "${REVIEW_ID}" \
  --status blocked \
  --add-label pr-review \
  --add-label pr-review-task \
  --append-notes "Review target bead: ${ORIGINAL_ID}. PR: ${PR_URL}"
```

### 1. Discover ready work

Only run this step when Step 0 found no dispatchable `pr-review-task` issues
for currently available slots.

```bash
bd ready --json
```

If the list is empty, wait and poll again.

### 2. Select next issue

Pick the issue with the **lowest `priority` number** (P0 first).
Break ties by **oldest `created_at`**.
Skip any issue already assigned to a running worker.

### 3. Claim the issue

```bash
bd update <id> --status in_progress --json
```

### 4. Prepare worker environment

```bash
bd worktree create .worktrees/parallel-agents/<id> --branch agent/<id>
```

This creates an isolated code worktree for the worker branch. Beads metadata
is shared across all worktrees via a Dolt DB redirect file.

### 5. Build the worker prompt

Choose worker skill by issue type:
- **epic-complexity issue** (see Team Coordination Mode): dispatch as team lead
- default implementation issue: `beads-worker`
- `pr-review-task` issue: `beads-pr-reviewer-worker`

Construct a dispatch prompt by injecting issue-specific context:

| Variable | Source |
|---|---|
| `ISSUE_ID` | The beads issue ID (e.g. `bd-42`) |
| `ISSUE_JSON` | Full output of `bd show <id> --json` |
| `WORKTREE_PATH` | Absolute path to the worktree directory |
| `REPO_ROOT` | Absolute path to the main repository |

Keep the prompt compact. Prefer a short issue summary, acceptance criteria, and
likely edit targets over pasting giant Beads JSON blobs unless the extra detail
is truly needed.

Example dispatch prompt (`beads-worker`):

```
You are a Beads Worker. Follow the beads-worker skill instructions
(~/.claude/skills/beads-worker/SKILL.md).

ISSUE_ID: bd-42
WORKTREE_PATH: /path/to/repo/.worktrees/parallel-agents/bd-42
REPO_ROOT: /path/to/repo

Issue details:
<paste bd show --json output here>
```

For `pr-review-task` issues, use the same structure but reference
`beads-pr-reviewer-worker` in the prompt.

### 6. Dispatch the worker

Spawn a subagent using the **current runtime's native subagent mechanism** with
the constructed prompt. Never shell out to CLI binaries directly.

If you are Gemini CLI, DO NOT use the skill markdown directly; instead, invoke
the matching custom subagent (`beads-worker` or `beads-pr-reviewer-worker`),
including in your prompt the beads issue to work on and the worktree path, in
this EXACT JSON format:
```json
{"ISSUE_ID":"<BEADS-ISSUE-ID>","BASE":"<main or master branch>","WORKTREE_PATH":"<WORKTREE-PATH>", "query": "<full selected worker skill prompt here>"}
``` 

| Runtime | Dispatch mechanism | Permission flag |
|---|---|---|
| Claude Code | `Task` tool (subagent) | `--dangerously-skip-permissions` |
| Codex | Built-in subagent / `codex exec` | `--yolo` |
| OpenCode | Built-in subagent dispatch | (use runtime's full-auto mode) |

**Model selection** — select based on the Assignment Rules above:
- Use `EPIC_COMPLEXITY_MODEL` for team leads in Team Coordination Mode.
- Use `HIGH_COMPLEXITY_MODEL` for complex coding and orchestration tasks.
- Use `MEDIUM_COMPLEXITY_MODEL` for most fixes if the requirements and scope has already been fully scoped out.
- Use `LOW_COMPLEXITY_MODEL` for pure formatting/linting tasks.

Workers operate autonomously following their selected workflow:
- `beads-worker`: Understand → Implement → Verify → Handoff
- `beads-pr-reviewer-worker`: review threads/comments and decide merge/close
  path for `pr-review-task` beads

### 6a. Bootstrap the worker (mandatory)

A spawned worker is **not** considered running until it proves it is operating
from the assigned worktree.

Bootstrap contract:
- `pwd` must equal `WORKTREE_PATH`
- current branch must equal the expected worker branch (`agent/<id>` for normal
  workers, or the expected PR/review branch for review workers)
- `pwd` must **not** equal `REPO_ROOT`

If the runtime supports interim updates, require a short bootstrap
acknowledgement before continuing. If bootstrap never arrives, or if the worker
reports repo-root / `main` / `master` context, treat dispatch as failed and
release the bead immediately.

### 7. Monitor workers

- Track each worker's `ISSUE_ID`, branch, worktree path, start time, and
  bootstrap status.
- Do **not** count a slot as occupied until bootstrap succeeds.
- A missing bootstrap acknowledgement is a **dispatch failure**, not an
  implementation stall.
- If `main` or the repo root checkout advances unexpectedly while a worker is
  supposedly active, stop and investigate worktree misbinding before
  dispatching more workers.
- When an implementation worker completes, reconcile from branch/PR state plus
  worker report (not from worker-owned bead mutations):
  - Check for open PR on `agent/<id>`:
    ```bash
    gh pr list --state open --head "agent/<id>" --json number,url,createdAt
    ```
  - If PR exists:
    1. `bd update <id> --status blocked --external-ref "gh-pr:<N>" --add-label pr-review --json`
    2. Ensure dedicated `pr-review-task` bead exists; if missing, create with
       the safe sequential pattern above.
    3. Re-run Step 0 immediately so review/merge is prioritized.
  - If no PR exists and worker marked `direct-merge-candidate`, attempt
    fast-forward merge to `main`:
    ```bash
    git fetch origin
    git checkout main && git pull --ff-only
    git merge --ff-only origin/agent/<id>
    git push origin main
    ```
    On success: `bd close <id> --reason "Simple change merged to main"`.
    On ff-only failure: open PR from `agent/<id>` and route through PR-review
    flow (set `external_ref`, create review bead, dependency wire).
  - If no PR and no direct-merge candidacy signal, treat as stalled and follow
    stall handling below.
- Ensure any nontrivial discovered work from worker reports is converted into
  new beads by the coordinator using safe sequential creation:
  ```bash
  NEW_JSON=$(bd create "<title>" --description="<details>" -t <type> -p <priority> --json)
  NEW_ID=$(echo "${NEW_JSON}" | jq -r '.id // .[0].id')
  bd dep add "<original-id>" "${NEW_ID}"
  ```
- If a worker fails bootstrap, or stalls after bootstrap (no diff / commit / PR
  signal for >5 minutes):
  - Log the failure.
  - Release the issue:
    - for `pr-review-task` issues: `bd update <id> --status blocked --remove-label review-running --json`
    - otherwise: `bd update <id> --status open --json`
  - Clean up the worktree.

### 8. Progress Report & Loop

**Interval**: Wait **15 minutes** between coordinator cycles.

At the start of each cycle, check whether any beads changed status in the last
15 minutes (closed, merged, moved to `in_progress`, etc.). If there has been
progress, print a progress report before continuing to Step 0.

#### Progress Report Format

```
═══════════════════════════════════════════════════════════════
  Beads Coordinator — Progress Report
  <current date/time in Asia/Singapore timezone, e.g. 2026-03-08 14:30 SGT>
═══════════════════════════════════════════════════════════════

| # | Bead ID   | Title                          | Status      | Merged to main? |
|---|-----------|--------------------------------|-------------|-----------------|
| 1 | beads-042 | Fix login redirect             | closed      | Yes             |
| 2 | beads-045 | Add pagination to /users       | in_progress | —               |
| 3 | beads-048 | Review PR #31                  | closed      | Yes             |

Total closed this session: 3 / 10 open at start
═══════════════════════════════════════════════════════════════
```

**How to generate:**

1. Get the current Singapore time:
   ```bash
   TZ=Asia/Singapore date '+%Y-%m-%d %H:%M SGT'
   ```
2. List all beads that were updated recently:
   ```bash
   bd list --json
   ```
   Filter to beads whose `updated_at` falls within the last 15 minutes.
3. For each closed bead, check whether its branch was merged to main:
   ```bash
   git log --oneline main --grep="agent/<id>" || git branch -r --merged main | grep "agent/<id>"
   ```
   Or check via `external_ref` for PR-based merges:
   ```bash
   gh pr view <number> --json state,mergedAt
   ```
4. Print the table. Include **all beads that changed in the window**, not just
   closed ones. The "Merged to main?" column shows "Yes", "No", or "—" (not
   applicable / still in progress).

If no beads changed in the last 15 minutes, skip the report and proceed
directly to Step 0.

Return to Step 0.

---

## Epic Decomposition

Do NOT dispatch epics to workers directly. First classify the epic's
complexity to choose between **independent dispatch** (default) and
**Team Coordination Mode** (EPIC_COMPLEXITY).

### Classification Heuristics

Evaluate the epic to decide the dispatch strategy:

| Signal | Points toward EPIC_COMPLEXITY |
|---|---|
| **Cross-cutting scope** — touches API + frontend + DB + tests in one coherent change | Yes |
| **Tightly coupled subtasks** — subtask outputs feed into each other (e.g., schema change needed by both API and UI) | Yes |
| **Integration risk** — separate branches would conflict or require non-trivial merge resolution | Yes |
| **Shared design decisions** — subtasks need a consistent architectural approach decided up front | Yes |
| **>3 interdependent children** | Yes |
| **Independent, parallelizable subtasks** — each can ship as its own PR with no merge risk | No — use independent dispatch |
| **Purely additive work** — new files, no shared state | No — use independent dispatch |

**Default: independent dispatch.** Escalate to Team Coordination Mode only
when 2+ signals above are present.

### Independent Dispatch (default)

1. Inspect children: `bd children <epic-id> --json`.
2. If children exist, dispatch each ready child as a separate worker.
3. If no children exist, decompose first:
   ```bash
   CHILD_JSON=$(bd create "<subtask title>" \
     --description="<details>" \
     -t task -p <priority> \
     --json)
   CHILD_ID=$(echo "${CHILD_JSON}" | jq -r '.id // .[0].id')
   bd dep add <epic-id> "${CHILD_ID}"
   ```
4. Then dispatch the subtasks.

### Team Coordination Mode (EPIC_COMPLEXITY)

When the classification heuristics indicate tightly-coupled work, dispatch a
**Team Lead** agent instead of individual workers. The Team Lead is a
high-capability model (`EPIC_COMPLEXITY_MODEL`) that acts as a mini-coordinator
within a single worktree, spawning its own sub-workers for parallel subtasks.

#### Slot Reservation

A Team Lead **reserves all available worker slots** for the duration of its
execution (configurable via `team_size`, default = max parallel workers).
The coordinator treats it as a single super-worker occupying N slots.

While a Team Lead is active:
- No new independent workers are dispatched (PR-review lane excepted).
- The coordinator continues its loop but only processes Step 0 (PR reviews)
  and Step 7 (monitoring) until the Team Lead completes.

#### Team Lead Dispatch

1. **Label the epic**: `bd update <epic-id> --add-label team-coordination`.
2. **Claim**: `bd update <epic-id> --status in_progress --json`.
3. **Create worktree**: `bd worktree create .worktrees/parallel-agents/<epic-id> --branch agent/<epic-id>`.
4. **Build prompt** — inject all epic context plus the Team Lead instructions:

```
You are a Team Lead for an epic-complexity issue. Your job is to
architect, decompose, coordinate sub-workers, integrate their output,
and deliver one consolidated PR.

ISSUE_ID: <epic-id>
WORKTREE_PATH: <worktree-path>
REPO_ROOT: <repo-root>
TEAM_SIZE: <number of sub-workers you may spawn>

Issue details:
<bd show --json output>

## Your Workflow

### Phase 1: Architect
- Read the epic and all child issues (if any).
- Analyze the codebase to understand the change surface.
- Produce a brief implementation plan: which files change, in what
  order, what interfaces are shared between subtasks.
- Decide subtask boundaries. Create child beads if they don't exist:
  first `bd create ... --json`, then `bd dep add <epic-id> <child-id>`.

### Phase 2: Coordinate
- Spawn sub-workers (beads-worker skill) for independent subtasks.
  Each sub-worker operates in the SAME worktree on a sub-branch
  (`agent/<epic-id>/<subtask-id>`).
- For tightly coupled subtasks that must be sequential, implement
  them yourself or dispatch sequentially.
- After each sub-worker completes, integrate its branch:
  `git merge --no-ff agent/<epic-id>/<subtask-id>` into
  `agent/<epic-id>`.

### Phase 3: Integrate & Verify
- Resolve any merge conflicts from sub-worker branches.
- Run the full test suite / quality gates on the integrated branch.
- Fix integration issues directly — do not re-dispatch for glue work.

### Phase 4: Ship
- Push the consolidated `agent/<epic-id>` branch.
- Create a single PR covering the entire epic.
- Do not mutate bead lifecycle from the Team Lead. Report PR URL/branch so the
  coordinator can apply the Bead Closure Rule and create the review bead path.

## Rules
- You may spawn up to TEAM_SIZE sub-workers concurrently.
- Sub-workers use MEDIUM_COMPLEXITY_MODEL (or HIGH for complex subtasks).
- You are responsible for integration — sub-workers only implement
  their slice.
- If a sub-worker fails, you may retry once or implement that slice
  yourself.
- Never call `bd close` on the epic — the coordinator handles that
  after PR merge.
```

5. **Dispatch** using `EPIC_COMPLEXITY_MODEL` via the runtime's native
   subagent mechanism.

#### Monitoring Team Leads

Same as Step 7, with these additions:

- **Timeout**: Team Leads get 3x the normal stall timeout (30 min default)
  before the coordinator intervenes.
- **Partial progress**: If the Team Lead stalls but has pushed sub-branches,
  the coordinator should:
  1. Check which child beads are complete vs. still open.
  2. Release the epic back to `open` with a note listing completed subtasks.
  3. On next cycle, re-evaluate: if enough subtasks are done, dispatch a new
     Team Lead to finish integration only.
- **Completion**: When the Team Lead finishes, it follows the same Bead
  Closure Rule as regular workers (direct-merge or PR path). The coordinator
  processes accordingly in Step 7.

---

## Handling Blockers

If a worker reports a hard blocker:

1. Create a blocker issue:
   ```bash
   BLOCKER_JSON=$(bd create "Blocker: <description>" \
     --description="<details>" \
     -t bug -p 0 \
     --json)
   BLOCKER_ID=$(echo "${BLOCKER_JSON}" | jq -r '.id // .[0].id')
   bd dep add <original-id> "${BLOCKER_ID}"
   ```
2. Release the original issue back to `open`.

---

## Quality Gates

Workers must pass all quality gates defined in the repository's `AGENTS.md` /
`CLAUDE.md` before closing an issue. The specific gate commands are
language/project-dependent — worker skills instruct workers to read them from
the repository. If a worker skips gates, the coordinator should flag the issue
and re-dispatch or escalate. PR-review follow-up tasks are governed by
`beads-pr-reviewer-worker` review and merge criteria.

---

## Session Completion Checklist

```bash
# 1. Verify all workers finished or cleaned up
bd worktree list

# 2. Release stale claims
bd list --status=in_progress --json
# For each stale: bd update <id> --status open

# 3. Verify Dolt DB is healthy
bd dolt status

# 4. Push everything
git pull --rebase && git push
git status  # Must show "up to date with origin"
```

---

## bd Quick Reference

| Action | Command |
|---|---|
| Ready work | `bd ready --json` (add `--rig <rig>` if outside target rig) |
| All open | `bd list --status=open --json` (add `--rig <rig>` if outside target rig) |
| PR-review issues | `bd list --status=blocked --label pr-review --json` |
| PR-review-task issues | `bd list --status=blocked --label pr-review-task --json` |
| Claim review lock | `bd update <id> --status in_progress --add-label review-running --json` |
| Release review lock | `bd update <id> --status blocked --remove-label review-running --json` |
| Issue detail | `bd show <id> --json` |
| Check PR state | `gh pr view <number> --json state,mergedAt` |
| Find PR by worker branch | `gh pr list --state open --head "agent/<id>" --json number,url,createdAt` |
| Create issue | `bd create "<title>" --description="<desc>" -t <type> -p <priority> --json` (add `--rig <rig>` if outside target rig) |
| Claim issue | `bd update <id> --status in_progress --json` |
| Label for team coordination | `bd update <id> --add-label team-coordination` |
| Release issue | `bd update <id> --status open --json` |
| Remove PR labels | `bd update <id> --remove-label pr-review --remove-label pr-review-task` |
| Close issue | `bd close <id> --reason "<reason>"` |
| Add dependency | `bd dep add <issue> <depends-on>` |
| Children | `bd children <id> --json` |
| Blocked | `bd blocked --json` (no `--rig` support; use `bd list --rig <rig> --status=blocked` cross-rig) |
| Dolt server status | `bd dolt status` |
| Dolt version control | `bd vc status` |
