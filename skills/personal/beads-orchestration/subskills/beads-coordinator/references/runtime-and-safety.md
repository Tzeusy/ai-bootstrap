# Runtime And Safety

Load this file before dispatching workers or mutating Beads state.

## Claiming And The Stall Heartbeat

Mutual exclusion comes from two real mechanisms, **not** from notes-based
tokens:

1. **Atomic claim** — `bd update <id> --claim` atomically sets the bead's
   `assignee` to you and `status=in_progress` in one operation. It is idempotent
   if you already hold it. This is the cross-actor mutual-exclusion primitive:
   only one actor can win the `assignee`. Verify success from the command
   result (`assignee` is this coordinator), not from a later reread.
2. **Worktree creation backstop** — `bd worktree create` fails when the
   `agent/<id>` branch already exists. This prevents a same-actor session from
   double-dispatching a bead it already has in flight. If worktree creation
   fails on an existing branch, do not dispatch a second worker.

Never model claiming as a read-then-write of a token in `notes`/`design`. There
is no atomic conditional update / compare-and-swap via the notes field; that
would be a read-then-write race. The `bd update --claim` flag is the atomic
operation.

### Stall heartbeat (stall detection only)

The coordinator writes a heartbeat timestamp so a crashed/abandoned claim can be
detected and reclaimed by a recovery pass (cleanup or another coordinator). This
heartbeat is **explicitly not a mutual-exclusion mechanism** — `assignee` is.

Store exactly one canonical heartbeat block in `notes` (replace it in place;
never append duplicates):

```text
[beads-heartbeat]
owner=coordinator:<session-id>
last_heartbeat_at=<iso8601>
[/beads-heartbeat]
```

Heartbeat and stall parameters (canonical; do not restate elsewhere):
- Heartbeat TTL: 20 minutes.
- Renewal target: every 5 minutes while active, and before every mutation.
- Worker stall threshold: at least 30 minutes without a progress signal before
  force-release, unless a runtime-specific note below states otherwise. Team
  Leads get 3x this threshold (see `epic-coordination.md`).

Repeat this rule during long runs:

Before any `bd` mutation: confirm you are the bead's `assignee`, renew the stall
heartbeat if near expiry, then mutate.

Mandatory heartbeat-renewal points:
1. Immediately after claim.
2. Before every `bd create`, `bd update`, `bd dep add`, or `bd close`.
3. After any long external action such as `gh`, tests, rebase, or merge work.
4. Before sleeping, polling, or waiting on agents for a long window.

Ownership rule:
- If the `assignee` is another actor, do not touch the bead — its claim wins.
- If the bead is assigned to another actor but its heartbeat is expired past the
  stall threshold, a recovery pass (cleanup or coordinator) may reclaim it:
  re-claim with `bd update <id> --claim` and reset the heartbeat.
- Never "win" a live foreign claim by writing a newer timestamp; the heartbeat
  does not arbitrate ownership.

## Model Selection Strategy

The coordinator has discretion on subagent model choice based on task type.

### Complexity Constants

| Strategy | Claude | ChatGPT | Gemini |
|---|---|---|---|
| `EPIC_COMPLEXITY_MODEL` | Opus 4.8 | 5.6 Sol Max | gemini-3-pro |
| `HIGH_COMPLEXITY_MODEL` | Sonnet 5 | 5.6 Terra Max | gemini-3-pro |
| `MEDIUM_COMPLEXITY_MODEL` | Sonnet 5 | 5.6 Luna High | gemini-3-pro |
| `LOW_COMPLEXITY_MODEL` | 4.5 Haiku | 5.6 Luna Medium | gemini-3-flash-preview |

The ChatGPT column is a Pareto frontier: move up only when the assigned
complexity tier requires it. Reserve Sol Max for the most complicated tasks at
`EPIC_COMPLEXITY_MODEL`; never use it for high-, medium-, or low-complexity
work.

### Assignment Rules

| Task Type | Model Complexity |
|---|---|
| Epic / team-coordinated work | `EPIC_COMPLEXITY_MODEL` |
| Reconciliation bead for a medium-or-higher epic | `EPIC_COMPLEXITY_MODEL` (floor — see below) |
| Planning, research, architecting | `HIGH_COMPLEXITY_MODEL` |
| Coding | `MEDIUM_COMPLEXITY_MODEL` unless trivial |
| Orchestration | `HIGH_COMPLEXITY_MODEL` |
| Simple bugfixes | `MEDIUM_COMPLEXITY_MODEL` |
| Formatting, linting | `LOW_COMPLEXITY_MODEL` |

## Review Risk Tiers

Every review verdict is bound to the **exact head SHA** inspected. If the head
moves, merge readiness expires until that SHA is reviewed.

| Tier | Examples | Review policy |
|---|---|---|
| High | auth/authorization, approvals, secrets, cross-schema boundaries, migrations/persisted contracts, concurrency/distributed state, replay/idempotence, data loss | Dedicated independent exact-head review. Any reviewer-authored semantic fix or material risk-changing correction requires a fresh independent reviewer. |
| Standard | Cohesive product/backend/UI behavior with bounded failure surface | Independent exact-head review; retain the same reviewer for correction rechecks when independence is intact. |
| Low | Tiny docs, tests, formatting, chore, or mechanical refactor with no observable contract/risk change | Schedule a sequential convoy of 3-4 same-domain review beads to one sticky reviewer identity. Process one PR/SHA and emit one verdict at a time; escalate on any semantic finding. |

Risk tiers reduce repeated context loading, never the evidence required for the
actual change. Do not batch high-risk work or merge an unreviewed moved head.
"Sequential convoy" never means one multi-PR reviewer worker: the one-bead,
one-PR report contract remains intact, and the coordinator dispatches the next
low-risk bead only after the prior verdict returns.

### Reconciliation Floor (mandatory)

A reconciliation bead (label `reconciliation`, title `Reconcile spec-to-code
(gen-N) …`) is a deep spec-to-code audit, not ordinary coding. Its `task` type
would otherwise route it to `MEDIUM_COMPLEXITY_MODEL`, which is too weak to
catch coverage gaps across a large epic.

Rule: before dispatching a reconciliation bead, resolve its parent epic's
complexity tier (see `epic-coordination.md` → "Epic Complexity Tiers"). If the
epic is **medium or higher** (1+ positive classification signal, or it carries
the `team-coordination` label), you MUST dispatch the reconciliation bead at
`EPIC_COMPLEXITY_MODEL` — i.e. Opus on Claude. This is a floor, not a
target: never drop below it for a qualifying epic, regardless of the bead's
`task` type. Only a low/trivial epic (0 signals) may reconcile at
`MEDIUM_COMPLEXITY_MODEL`.

To find the parent epic and its tier:

```bash
EPIC_ID=$(bd show <recon-id> --json | jq -r '.parent // .epic // empty')
bd show "${EPIC_ID}" --json   # inspect scope + labels for the tier signals
```

## Central Mutation Authority

The coordinator owns canonical Beads lifecycle mutations. Worker agents do not.

Coordinator-only operations:
- `bd create`
- `bd update`
- `bd dep add`
- `bd close`

Workers may:
- read Beads state for context
- push code branches
- open or merge PRs when their worker contract allows it
- report structured follow-up items for the coordinator to materialize

Workers may not:
- create follow-up beads
- claim or release beads
- add or remove dependencies
- close original or review beads

## Runtime-Specific Dispatch Notes

- Use the runtime's native subagent mechanism.
- Never shell out to `codex` / `claude` / `opencode` / `gemini` binaries
  directly to create workers.
- When referencing bundled files, prefer relative paths from this skill folder.

### Runtime Table

| Runtime | Dispatch mechanism | Permission flag |
|---|---|---|
| Claude Code | `Task` tool (subagent) | `--dangerously-skip-permissions` |
| Codex | built-in subagent | `--yolo` |
| OpenCode | built-in subagent dispatch | use runtime's full-auto mode |

### Codex-Specific Dispatch Hardening

These rules are mandatory when the coordinator runtime is Codex:

1. Dispatch workers with `fork_context=false`.
2. Treat `wait_agent` timeout as "still running", not failure.
3. Require bootstrap evidence (`pwd`, branch) before a worker counts as active.
4. Apply the default 30-minute stall threshold above; a `wait_agent` timeout is
   not itself a stall.
5. Send one interrupt heartbeat requesting a 2-line status before classifying a
   worker as stalled.
6. Close completed probe/worker agents promptly so thread limits do not block
   new dispatches.

### Gemini CLI Note

If the runtime is Gemini CLI, do not use the skill markdown directly. Invoke
the matching custom subagent (`beads-worker` or `beads-pr-reviewer-worker`)
using this JSON shape:

```json
{"ISSUE_ID":"<BEADS-ISSUE-ID>","BASE":"<main or master branch>","WORKTREE_PATH":"<WORKTREE-PATH>","query":"<full selected worker skill prompt here>"}
```

## Bead Mutation Safety

Beads data lives in Dolt DB, not git-tracked files.

`bd create/update/close/dep` mutate the Dolt database directly. The Dolt
sql-server is auto-started when needed. Worker worktrees share the same DB via
redirect files created by `bd worktree create`.

Rules:
1. Keep the Dolt server healthy. Run `bd dolt status` before heavy mutation
   loops.
2. Never commit `.beads/` contents on code branches. The directory is
   gitignored; accidental `.beads/` diffs on code branches must be stripped.
3. Create beads sequentially. Never create multiple beads in parallel because
   the ID counter can race and overwrite existing beads.
4. Do not use `--deps discovered-from:` in `bd create`; it can panic. Create
   the bead first, then wire dependencies with `bd dep add`.
5. Use `bd dolt commit/push/pull` for Dolt version control, not manual file
   surgery. Use `bd vc status` to check for uncommitted changes.
6. Before any `bd` mutation: confirm you are the bead's `assignee`, renew the
   stall heartbeat if near expiry, then mutate.

## Bead Closure Rule

A bead may only be closed by the coordinator when one of these conditions is
met:

1. Direct merge for trivial/simple changes:
   - worker pushes `agent/<id>`
   - worker reports `direct-merge-candidate`
   - coordinator fast-forward merges to `main`
   - coordinator closes the bead
2. GitHub PR merged:
   - worker pushes branch and opens PR, or coordinator opens it during
     reconciliation
   - coordinator blocks the original bead and stores `external_ref=gh-pr:<N>`
   - coordinator creates or reuses exactly one dedicated PR-review bead
   - reviewer worker may merge the PR, but coordinator confirms merge and then
     closes the review and original beads

Implementation workers and reviewer workers must never call `bd close`.

## Quality Gates

Workers must pass all quality gates defined in the repository's `AGENTS.md` /
`CLAUDE.md` before coordinator closure. The specific gate commands are
language/project-dependent. If a worker skips gates, the coordinator should
flag the issue and re-dispatch or escalate.
