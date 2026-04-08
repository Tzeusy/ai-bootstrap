# Runtime And Safety

Load this file before dispatching workers or mutating Beads state.

## Durable Lease Model

The coordinator must use durable leases for every bead it claims.

Assume Beads v1.0.0 supports atomic conditional updates on the Dolt-backed
store. Use them. Do not model claiming as an unconditional overwrite when a
compare-and-swap style update is available.

Preferred machine-readable fields:
- `lease_owner`
- `lease_token`
- `lease_expires_at`
- `last_heartbeat_at`

Preferred claim semantics:
- read current lease state
- perform an atomic conditional update that succeeds only if:
  - no live lease exists, or
  - the existing lease already belongs to this coordinator session/token
- verify success from the command result, not just from a later reread

If Beads does not support custom per-bead fields, store exactly one canonical
lease block in `notes` or `design` and replace that block atomically instead of
appending duplicates:

```text
[beads-lease]
owner=coordinator:<session-id>
token=<lease-token>
expires_at=<iso8601>
last_heartbeat_at=<iso8601>
[/beads-lease]
```

Repeat this rule during long runs:

Before any `bd` mutation: verify lease ownership, renew if near expiry, then
mutate.

Mandatory renewal points:
1. Immediately after claim.
2. Before every `bd create`, `bd update`, `bd dep add`, or `bd close`.
3. After any long external action such as `gh`, tests, rebase, or merge work.
4. Before sleeping, polling, or waiting on agents for a long window.

If the lease is expired or owned by another live session:
- stop mutating Beads state
- append a note only if safe to do so under ownership rules
- fall back to human triage or cleanup flow

If a live foreign lease exists:
- do not overwrite it
- do not "win" by writing a newer timestamp
- do not dispatch a worker for that bead

## Model Selection Strategy

The coordinator has discretion on subagent model choice based on task type.

### Complexity Constants

| Strategy | Models (subject to change) |
|---|---|
| `EPIC_COMPLEXITY_MODEL` | Opus 4.6, gpt-5.3-codex, gemini-3-pro |
| `HIGH_COMPLEXITY_MODEL` | Sonnet 4.6, gpt-5.3-codex, gemini-3-pro |
| `MEDIUM_COMPLEXITY_MODEL` | Sonnet 4.6, gpt-5.3-codex, gemini-3-pro |
| `LOW_COMPLEXITY_MODEL` | 4.5 Haiku, gpt-5.3-codex-spark, gemini-3-flash-preview |

### Assignment Rules

| Task Type | Model Complexity |
|---|---|
| Epic / team-coordinated work | `EPIC_COMPLEXITY_MODEL` |
| Planning, research, architecting | `HIGH_COMPLEXITY_MODEL` |
| Coding | `MEDIUM_COMPLEXITY_MODEL` unless trivial |
| Orchestration | `HIGH_COMPLEXITY_MODEL` |
| Simple bugfixes | `MEDIUM_COMPLEXITY_MODEL` |
| Formatting, linting | `LOW_COMPLEXITY_MODEL` |

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
4. For implementation beads, require at least 30 minutes of no progress signal
   before force-releasing.
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
6. Before any `bd` mutation: verify lease ownership, renew if near expiry, then
   mutate.

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
