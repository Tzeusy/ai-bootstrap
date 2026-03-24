---
name: gastown-coordinator
description: Coordinate Gas Town work by continuously selecting ready beads across rigs and slinging them to polecats with dynamic agent/model selection. Run by the mayor for unattended cross-rig throughput.
---

# Gas Town Coordinator

## Overview

Run a coordinator loop from the mayor that pulls ready Beads across all
operational rigs and dispatches them to polecats via `gt sling`. The
coordinator selects an appropriate agent tier based on bead complexity and
monitors worker health periodically.

**The coordinator never implements code. It coordinates.**

Gas Town handles worktree isolation, merge queues, and session lifecycle.
The coordinator's job is: discover work, pick the right agent, sling it,
and monitor.

## Use This Skill When

- "sling all ready beads across rigs"
- "coordinate work across Gas Town"
- "keep polecats busy with ready beads"
- "run the mayor coordination loop"

## Agent Tiers

Six custom agents are registered via `gt config agent`. The coordinator
selects the tier matching each bead's complexity.

| Tier | Claude Agent | Codex Agent |
|------|-------------|-------------|
| Complex | `claude-complex` (Opus) | `codex-complex` (gpt-5.3-codex high) |
| Default | `claude-default` (Sonnet) | `codex-default` (gpt-5.3-codex high) |
| Simple | `claude-simple` (Haiku) | `codex-simple` (gpt-5.3-codex medium) |

### Selecting a Tier

Evaluate the bead's description, acceptance criteria, type, and parent epic:

| Signal | Tier |
|--------|------|
| Epic decomposition, architecture decisions, cross-cutting changes | **Complex** |
| Multi-file implementation, new features, non-trivial bugs | **Default** |
| Single-file fixes, formatting, config changes, doc updates, chores | **Simple** |

**Default to Default tier.** Only escalate to Complex when the bead clearly
requires architectural reasoning. Only downgrade to Simple when the change
is mechanical.

### Selecting a Provider (Claude vs Codex)

Check the rig's configured agent:

```bash
gt rig config show <rig>
# Look for 'agent' key in output
```

- If `agent` is set (e.g., `agent = codex`), use that provider's tier.
- If no `agent` is set, use `claude-*` tiers (the town default).

This means the coordinator respects per-rig provider preferences while
still selecting the appropriate complexity tier.

> **CRITICAL: `--agent` flag is mandatory on every `gt sling` call.**
> The rig config `agent` setting is NOT reliably picked up by `gt sling`.
> Always pass `--agent <agent-name>` explicitly. Without it, sling
> defaults to `claude` regardless of rig config.

## Coordinator Loop

### Prerequisites

Before entering the loop:

1. Verify Gas Town services are healthy:
   ```bash
   gt status
   ```
2. List operational rigs:
   ```bash
   gt rig list --json
   ```
   Only coordinate rigs with `status: "operational"`.

3. Check Dolt health:
   ```bash
   bd dolt status
   ```

### Constraints

| Constraint | Value |
|---|---|
| Max polecats per rig | `max_polecats` from `gt rig config show <rig>` (default 10) |
| Sling method | **Sequential, one at a time** per rig. Never parallel sling. |
| Inter-sling delay | **5 seconds** between slings (prevents Dolt/worktree races) |
| Issue tracker | `bd` CLI only |
| Merge strategy | Default (`mr` = merge queue). The refinery handles conflicts. |
| Bead closure | Polecats close their own beads via `bd close`. Coordinator does NOT close beads. |
| Checkup interval | **15 minutes** between full health sweeps |

### 0. Health Check & Stale Cleanup

Run at the start and every 15 minutes during the loop:

```bash
# Check each operational rig for stale polecats
for rig in $(gt rig list --json | jq -r '.[] | select(.status=="operational") | .name'); do
  gt polecat stale "$rig" --cleanup
done
```

For each rig, also check for polecats marked "working" but with dead sessions:

```bash
gt polecat list <rig> --json
```

If a polecat has `state: "working"` or `state: "done"` but
`session_running: false`, it crashed or finished without cleanup.

**Dead polecat cleanup sequence (order matters):**

```bash
# 1. Reset the bead FIRST (while polecat still exists for reference)
bd update <bead-id> --status open
gt sling respawn-reset <bead-id>

# 2. Nuke the polecat (destroys session, worktree, branch)
gt polecat nuke <rig>/<polecat> -f
```

**If nuke leaves orphaned worktree directories** (common after startup
crashes), clean up manually:

```bash
# Check for leftover worktrees
git -C $HOME/gt/<rig> --git-dir=.repo.git worktree list
# Remove orphaned ones
git -C $HOME/gt/<rig> --git-dir=.repo.git worktree remove polecats/<name>/<rig> --force
rm -rf $HOME/gt/<rig>/polecats/<name>
```

Also check for beads stuck in **HOOKED** state (not just `in_progress`).
This happens when a polecat dies during sling startup before claiming the
bead. Reset these the same way:

```bash
bd update <bead-id> --status open
```

### 1. Discover Ready Work (per rig)

For each operational rig:

```bash
bd ready --rig <rig> --json
```

Filter out system beads (prefixes like `*-rig-*`, `*-polecat-*`, `*-wisp-*`).

> **bd JSON regression (v0.59.0):** `bd list --json` and `bd ready --json`
> may return the string `"No issues found."` instead of `[]` when empty.
> Always defensively parse: check if output starts with `[` before JSON
> decoding. Treat non-JSON output as "no results."

### 2. Check Capacity

For each rig, count active polecats:

```bash
gt polecat list <rig> --json
```

Count entries with `state: "working"` and `session_running: true`.
Compare against `max_polecats` from rig config.

If at capacity, skip this rig for now.

> **Important:** `session_running: true` means the tmux session exists, not
> that the polecat is actually executing work. Use `gt peek` checks in health
> scans before concluding a worker is making progress.

### 3. Select & Prioritize

From all ready beads across all rigs with available capacity:

1. Sort by `priority` ascending (P0 first).
2. Break ties by `created_at` ascending (oldest first).
3. Skip any bead already assigned to a running polecat.

### 4. Evaluate Complexity & Select Agent

For the selected bead, read its details:

```bash
bd show <bead-id> --json
```

Determine the tier (Complex / Default / Simple) based on:

- **Description length and detail**: >500 chars with architectural language = Complex
- **Type**: `epic` = Complex, `chore` = Simple, others = Default
- **Priority**: P0 = at least Default, P4 = consider Simple
- **Acceptance criteria count**: >5 criteria = Complex, 1-2 = Simple
- **Parent epic**: If bead is a child of a well-decomposed epic with clear
  scope, it's likely Default even if the epic itself is Complex

Determine the provider from rig config:

```bash
gt rig config show <rig>
# Look for 'agent' key
```

Map to agent name:

| Provider | Complex | Default | Simple |
|----------|---------|---------|--------|
| claude (or unset) | `claude-complex` | `claude-default` | `claude-simple` |
| codex | `codex-complex` | `codex-default` | `codex-simple` |

### 5. Sling the Bead

```bash
gt sling <bead-id> <rig> --agent <selected-agent>
```

Wait for the command to complete (it spawns the polecat and starts the
session). Check exit code.

**If sling fails:**

- If "respawn limit reached": `gt sling respawn-reset <bead-id>`, then retry once.
- If "worktree already exists": clean up the stale worktree:
  ```bash
  git -C $HOME/gt/<rig> --git-dir=.repo.git worktree remove polecats/<name>/<rig> --force
  rm -rf $HOME/gt/<rig>/polecats/<name>
  ```
  Then retry.
- If "session died during startup": the bead may be stuck in HOOKED state.
  Reset it: `bd update <bead-id> --status open`. Log the failure, skip this
  bead for now, and move to the next. It will be retried next cycle.
- On any other error: log and skip.

**After successful sling:** wait 5 seconds before slinging the next bead.

### 6. Epic Handling

Do NOT sling epics directly. When an epic appears in `bd ready`:

1. Check if it has children:
   ```bash
   bd list --rig <rig> --status=all --json | jq '[.[] | select(.parent == "<epic-id>")]'
   ```

2. **If children exist**: skip the epic itself. Its children will appear in
   `bd ready` when unblocked. Sling those individually.

3. **If no children exist**: the epic needs decomposition. Sling it with
   a Complex-tier agent and add args instructing decomposition:
   ```bash
   gt sling <epic-id> <rig> --agent <complex-agent> \
     --args "This is an epic that needs decomposition. Break it into child beads, then implement the first child."
   ```

### 7. PR Review Workflow (for complex changes)

When the coordinator encounters a bead with labels indicating it produced a
PR (check `bd show <id> --json` for `external_ref` containing `gh-pr:`):

1. **Create a review bead** under the same parent/epic:
   ```bash
   REVIEW_JSON=$(bd create --rig <rig> \
     --title "Review PR #<N> for <original-title>" \
     --description="Review the PR, leave comments, iterate on feedback. Original bead: <id>. PR: <url>" \
     --type task --priority 1 --json)
   REVIEW_ID=$(echo "$REVIEW_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
   bd dep add <original-id> $REVIEW_ID
   ```

2. Sling the review bead with a Default-tier agent.

3. The original bead stays blocked until the review bead completes and the
   PR is merged via the refinery.

**Note:** For most work, the refinery merge queue handles review
automatically. Only create explicit review beads for P0/P1 changes or
when the bead description explicitly requests review.

### 8. Periodic Checkup (every 15 minutes)

Track time since last checkup. Every 15 minutes:

#### a. Worker Health Scan

```bash
gt polecat list --all --json
```

For each working polecat with `session_running: true`, verify the session
is making progress:

```bash
gt polecat status <rig>/<polecat>
gt peek <rig>/<polecat> --lines 80
```

Do **not** trust `Last Activity` alone. It can update even when the agent is
idle at a blank prompt.

Treat a polecat as **idle-not-working** when `gt peek` shows startup/banner
output and a bare prompt (`❯`) with no active tool lines (e.g., no
`● Bash(...)`, `Tool loaded.`, or command progress) after sling.

If idle-not-working:
1. Nudge once:
   ```bash
   gt nudge <rig>/<polecat> "Run gt hook now and execute the hooked bead immediately. Do not wait for confirmation."
   ```
2. Recheck after 5-10s with `gt peek`.
3. If still idle after 2 nudges over ~2 minutes, treat as startup failure:
   - If bead is open/hooked: `bd update <bead-id> --status open` + `gt sling respawn-reset <bead-id>`
   - Nuke polecat: `gt polecat nuke <rig>/<polecat> -f`
   - Re-sling bead in the next cycle.

If `Last Activity` is >30 minutes ago and peek confirms no progress, log a
stall warning. The witness can recover stalls, but the mayor should still
nudge when a session is clearly idle at prompt.

#### b. Dead Session Cleanup

For polecats with `state: "working"` but `session_running: false`:

1. Check bead status first: `bd show <bead-id>`
2. If bead is **closed** → work completed, just nuke:
   ```bash
   gt polecat nuke <rig>/<polecat> -f
   ```
3. If bead is **open/hooked** → work incomplete, reset and nuke:
   ```bash
   bd update <bead-id> --status open
   gt sling respawn-reset <bead-id>
   gt polecat nuke <rig>/<polecat> -f
   ```

#### c. Capacity Report

Log current state:
- Per rig: working/done/capacity polecats
- Ready beads per rig
- Blocked beads per rig

#### d. Error Pattern Detection

If a bead has failed 3+ times across sling attempts (check respawn
counter or notes), escalate:

1. Bump the agent tier (Simple -> Default -> Complex).
2. Add args with error context:
   ```bash
   gt sling <bead-id> <rig> --agent <upgraded-agent> \
     --args "Previous attempts failed. Investigate carefully before implementing."
   ```
3. If still failing after Complex tier, create a blocker bead and skip:
   ```bash
   BLOCKER_JSON=$(bd create --rig <rig> \
     --title "Investigate repeated failures on <bead-title>" \
     --description="Bead <id> has failed 3+ times at Complex tier. Needs manual investigation." \
     --type bug --priority 1 --json)
   BLOCKER_ID=$(echo "$BLOCKER_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
   bd dep add <bead-id> $BLOCKER_ID
   ```

#### e. Epic Error Spawning

When a polecat working on an epic child reports errors or the child bead
is closed with an error reason, create a fix bead under the same epic:

```bash
FIX_JSON=$(bd create --rig <rig> \
  --title "Fix: <error summary from failed child>" \
  --description="Child bead <id> under epic <epic-id> failed. Error: <details>. Investigate and fix." \
  --type bug --priority 1 --json)
FIX_ID=$(echo "$FIX_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['id'])")
bd dep add <epic-id> $FIX_ID
```

This keeps the epic's scope complete even when individual children fail.

### 9. Loop

After processing all rigs, if no work was slung this cycle:

```bash
# Light poll — wait 60 seconds before rechecking
sleep 60
```

If work was slung, immediately loop back to Step 0 (work may have
unblocked new beads).

---

## Quick Reference

| Action | Command |
|---|---|
| Town status | `gt status` |
| List rigs | `gt rig list --json` |
| Rig config | `gt rig config show <rig>` |
| Ready work (per rig) | `bd ready --rig <rig> --json` |
| Bead details | `bd show <id> --json` |
| Sling work | `gt sling <bead> <rig> --agent <agent>` |
| List polecats | `gt polecat list <rig> --json` |
| Polecat status | `gt polecat status <rig>/<polecat>` |
| Polecat output peek | `gt peek <rig>/<polecat> --lines 80` |
| Nudge polecat | `gt nudge <rig>/<polecat> "<message>"` |
| Stale cleanup | `gt polecat stale <rig> --cleanup` |
| Nuke dead polecat | `gt polecat nuke <rig>/<polecat> -f` |
| Reset respawn | `gt sling respawn-reset <bead-id>` |
| Registered agents | `gt config agent list` |

---

## Operational Notes

### Sling Sequentially, Never in Parallel

Parallel `gt sling` causes:
- Dolt server contention (bead mutations race)
- Worktree allocation collisions
- Session startup crashes (tmux/agent init races)

Always sling one bead at a time with a 5-second gap.

### Rig Provider Preferences Are Authoritative

If a rig sets `agent = codex`, all polecats in that rig use codex variants.
The coordinator picks the complexity tier but never overrides the provider.

### The Refinery Handles Merges

Do not attempt direct merges or fast-forwards. All polecat work goes
through the refinery merge queue (`--merge=mr`, the default). The refinery
runs tests, resolves conflicts, and merges to main.

### Bead Lifecycle Ownership

- **Polecats** own their bead lifecycle: they claim, implement, and close.
- **The coordinator** only: discovers work, selects agents, slings, monitors,
  and creates new beads (review beads, blocker beads, epic children).
- **The witness** handles stall recovery and polecat health.
- **The refinery** handles merge queue processing.

### Session Instability

Some agent runtimes (especially codex) have higher session crash rates.
The coordinator should expect ~20-30% startup failure rate and handle it
gracefully via retry logic in Step 5. Do not treat a single startup
failure as a blocker — just move to the next bead and retry next cycle.

**False positive activity signals:** `session_running: true` and recent
`Last Activity` can still correspond to an idle Claude prompt. Always confirm
with `gt peek` before deciding a polecat is truly executing work.

**Dead polecat triage:** Most "dead" polecats (`session_running: false`)
have actually completed — bead is closed, commits merged. Known bug
(`hq-l4qi`): polecats `bd close` but skip `gt done`. Always check
`bd show <bead-id>` before assuming failure. If closed → just nuke.
If open → check branch for commits, rescue if needed, then reset & re-sling.

### Worktree Cleanup Is Critical

After nuking polecats, always verify that worktree directories were
actually removed. `gt polecat nuke -f` can leave orphaned directories
that block future slings with "worktree already exists" errors. The
manual cleanup sequence is:

```bash
# List all worktrees for a rig
git -C $HOME/gt/<rig> --git-dir=.repo.git worktree list

# Remove orphaned worktrees
git -C $HOME/gt/<rig> --git-dir=.repo.git worktree remove polecats/<name>/<rig> --force
rm -rf $HOME/gt/<rig>/polecats/<name>
```

### Beads State Can Be Stale

After a polecat dies, its bead may be stuck in `HOOKED`, `in_progress`,
or assigned to a nonexistent polecat. Always reset bead status to `open`
before re-slinging. The cleanup sequence in Step 0 is the canonical place
for this reconciliation.

### `bd create` Must Be Sequential

Never create multiple beads in parallel. This races on the Dolt ID counter,
causing collisions. Always chain with `&&` or wait for each to complete.
