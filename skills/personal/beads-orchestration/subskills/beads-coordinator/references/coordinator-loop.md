# Coordinator Loop

Load this file when you need the exact cycle, PR-review priority lane, claim and
heartbeat rules, worker bootstrap rules, monitoring details, or adaptive polling.

## Preflight

- Before entering the loop, run `../beads-cleanup/SKILL.md`. This is mandatory.
- Create a fresh coordinator session ID for this run (used as the stall-heartbeat
  owner; atomic claiming is handled by `bd update --claim`).
- If running from outside the target rig, point `bd` at the rig workspace with
  the global `-C <path>` flag, e.g. `bd -C /path/to/rig ready --json`. The
  removed `--rig` flag is no longer supported (bd 1.0.4+).
- Commands that accept an existing bead ID (`bd update`, `bd close`, `bd show`,
  `bd dep`) auto-route via prefix-based routing and need neither `-C` nor a
  rig flag.

## Constraints

| Constraint | Value |
|---|---|
| Max parallel workers | 3 by default; override only when explicitly requested |
| Worker isolation | each worker gets its own beads worktree and branch |
| Worktree creation | `bd worktree create` |
| Branch naming | `agent/<issue-id>` |
| Worktree root | `.worktrees/parallel-agents/` |
| Worker bootstrap | worker must prove `pwd == WORKTREE_PATH` and expected branch |
| Issue tracker | `bd` CLI only |
| Metadata persistence | Dolt DB via auto-started sql-server |
| PR review cooldown | 5 minutes after PR `createdAt` |

The stall-heartbeat model (TTL, renewal cadence), the per-runtime stall
threshold, and the model-selection tables live in `runtime-and-safety.md`. Do
not restate them here.

Repeat this rule during the whole run:

Before any `bd` mutation: confirm you are the bead's `assignee`, renew the stall
heartbeat if near expiry, then mutate. Never mutate a bead assigned to another
live actor.

## Step 0: Normalize PR-Review State

Step 0 is the **sole PR-state mutator** in the system. Only the coordinator
closes, reopens, or relabels beads in response to PR state (`MERGED`,
`CLOSED`-unmerged, etc.). `beads-cleanup` only inspects and reports PR-state
findings; it never mutates PR-review bead state.

When a `beads-cleanup` pass ran immediately before this loop, consume its
"PR-state findings (for coordinator Step 0)" report section instead of
re-querying `gh pr view` for those same PRs. Re-verify with `gh` only in the
moment right before an actual mutation, so a stale finding never drives an
irreversible close/reopen.

Before discovering new work, and whenever a worker frees a slot, check:

```bash
bd list --status=blocked --label pr-review --json
```

This list may include:
- blocked original implementation beads waiting on PR outcome
- blocked dedicated PR-review beads with label `pr-review-task`

Canonical PR metadata is stored on the original implementation bead only.

### 0a. Dedupe review beads

Before creating or dispatching any review bead, dedupe by:
- original implementation bead ID
- `external_ref` PR number on the original bead

If multiple review beads refer to the same original bead or PR:
- keep the oldest non-closed review bead as canonical
- remove stale `review-running` labels from duplicates
- append notes to duplicates explaining they were superseded
- close duplicates if safe, or leave them blocked for explicit cleanup if
  closure would be ambiguous

Never create a new `pr-review-task` bead while a canonical open or blocked one
already exists for the same original bead / PR.

Run this dedupe check immediately before **any** `bd create` of a review bead,
not only at the start of a cycle. Step 0c and Step 7 both create review beads;
each must rerun this check (by original bead ID and `external_ref` PR number)
right before creating, and skip creation if a canonical review bead exists.

### 0a1. Claim review beads before dispatch

Review-lane dispatch must use the same atomic `--claim` discipline as ready
work. A blocked `pr-review-task` bead is not dispatchable until the coordinator
has claimed it successfully.

Required sequence:
1. Read the review bead and inspect its `assignee`.
2. If it is assigned to another live actor, skip it.
3. Claim atomically with `bd update <id> --claim --json` (sets `assignee` and
   `status=in_progress`), then add the `review-running` label and write the
   stall heartbeat note.
4. Verify success from the command result (`assignee` is this coordinator).
5. Only then dispatch the reviewer worker.

If dispatch fails after the claim:
- return the bead to `blocked`
- remove `review-running`
- renew the stall heartbeat note so cleanup can see when the failed attempt
  went idle

### 0b. Reconcile blocked PR-review beads

For each blocked issue:
- if it is an original bead, read its own `external_ref` (`gh-pr:<number>`)
- if it is a dedicated `pr-review-task` bead, resolve its original bead first,
  then read the original bead's `external_ref`

If no PR number can be resolved, append a note and skip mutation for that bead.

When PR number is available, check:

```bash
gh pr view <number> --json state,mergedAt,createdAt
```

Handle each case:

| PR State | Action |
|---|---|
| `MERGED` | renew heartbeat, then close review/original beads as appropriate; then run the post-closure branch/worktree cleanup below |
| `CLOSED` and not merged | renew heartbeat, then reopen original for re-triage; block/close review bead as appropriate |
| `OPEN` with `pr-review-task` | wait for cooldown; once elapsed, atomically claim the review bead with `bd update <id> --claim`, then dispatch review worker if slot is open |
| `OPEN` without `pr-review-task` | ensure exactly one dedicated review bead exists |
| `gh` failure | log warning, skip; do not mutate on transient errors |

### Post-closure branch and worktree cleanup (merged PRs)

The reviewer merges with `gh pr merge --squash` and does **not** delete the
branch, so the `agent/<id>` branch name survives until the coordinator removes
it. This keeps branch-name → bead correlation intact if a crash happens between
merge and the worker report. Branch deletion is therefore the coordinator's
responsibility, performed only **after** the relevant bead(s) are closed:

```bash
# After bd close on the review/original beads:
git push origin --delete "agent/<id>" 2>/dev/null \
  || gh api -X DELETE "repos/<owner>/<repo>/git/refs/heads/agent/<id>" 2>/dev/null || true
bd worktree remove ".worktrees/parallel-agents/<id>" --force 2>/dev/null || true
git branch -D "agent/<id>" 2>/dev/null || true
```

Do not delete the branch before closure; correlation depends on it.

Priority rule:
- if any `pr-review-task` bead is dispatchable and a slot is open, dispatch it
  before selecting from `bd ready`
- do not start new implementation work while a dispatchable `pr-review-task`
  is waiting for an open slot

### 0c. Self-heal rule

Reconcile open PRs back into Beads even if workers failed to mutate metadata:

```bash
gh pr list --state open --json number,url,headRefName,createdAt
```

For each PR whose `headRefName` matches `agent/<issue-id>`:
- ensure the original bead is `status=blocked`, has
  `external_ref=gh-pr:<N>`, and label `pr-review`
- ensure exactly one dedicated `pr-review-task` bead exists; if missing, create
  it sequentially and wire the dependency with `bd dep add`
- if duplicates exist, dedupe before dispatch

Safe PR-review bead creation pattern:

```bash
REVIEW_JSON=$(bd create \
  "Conduct a thorough code review of ${PR_URL}" \
  --description="Review PR ${PR_URL} thoroughly. Original implementation bead: ${ORIGINAL_ID}. Leave PR comments on notable issues, apply fixes if needed, and report merge readiness back to the coordinator." \
  -t task -p 1 --json)
REVIEW_ID=$(echo "${REVIEW_JSON}" | jq -r '.id // .[0].id')
bd dep add "${ORIGINAL_ID}" "${REVIEW_ID}"
bd update "${REVIEW_ID}" \
  --status blocked \
  --add-label pr-review \
  --add-label pr-review-task \
  --append-notes "Review target bead: ${ORIGINAL_ID}. PR: ${PR_URL}"
```

## Step 1: Discover Ready Work

Only run this step when Step 0 found no dispatchable `pr-review-task` issues
for currently available slots.

```bash
bd ready --json
```

If the list is empty, enter idle polling mode.

## Step 2: Select Next Issue

Pick the issue with the lowest `priority` number, breaking ties by oldest
`created_at`. Skip any issue that:
- is already assigned to a running worker
- is assigned to another live actor (per `assignee`)
- is blocked by a dispatchable review task that should run first

## Step 3: Claim The Issue

Claim atomically with `bd update <id> --claim`. This is the real mutual-exclusion
mechanism, not the notes-based heartbeat.

1. Read the bead and confirm its `assignee` is empty or already this coordinator.
   If it is assigned to another live actor, skip this bead.
2. Claim atomically:

```bash
bd update <id> --claim --json
```

   `--claim` sets `assignee` to you and `status=in_progress` in one atomic,
   idempotent operation (a no-op if you already hold it). This provides
   cross-actor mutual exclusion: only one actor wins the assignee.
3. Verify success from the command result (`assignee` is this coordinator,
   `status=in_progress`).
4. Write the initial stall heartbeat note (see the durable-heartbeat model in
   `runtime-and-safety.md`). The heartbeat is stall detection only; it is NOT
   the claim mechanism.
5. Only after a verified claim may the coordinator create the worktree or
   dispatch a worker.

Mutual exclusion comes from two layers:
- **Atomic `--claim`** (cross-actor): only one actor can win the assignee.
- **`bd worktree create` failing when `agent/<id>` already exists** (the
  dispatch-level backstop, including a same-actor session that double-dispatches).
  If worktree creation fails because the branch exists, treat the bead as
  already in flight and do not dispatch a second worker.

## Step 4: Prepare Worker Environment

```bash
bd worktree create .worktrees/parallel-agents/<id> --branch agent/<id>
```

This creates an isolated code worktree for the worker branch. Beads metadata is
shared across worktrees via a Dolt DB redirect file.

## Step 5: Build The Worker Prompt

Choose worker skill by issue type:
- epic-complexity issue: dispatch as team lead; see `epic-coordination.md`
- default implementation issue: `../beads-worker/SKILL.md`
- `pr-review-task` issue: `../beads-pr-reviewer-worker/SKILL.md`

A `reconciliation`-labelled bead still uses `../beads-worker/SKILL.md`, but its
model is floored at `EPIC_COMPLEXITY_MODEL` for medium-or-higher epics — apply
the "Reconciliation Floor" in `runtime-and-safety.md` when picking the model in
Step 6.

Inject only:
- `ISSUE_ID`
- `WORKTREE_PATH`
- `REPO_ROOT`
- a 2-4 line issue summary plus its acceptance criteria

Do not inline full `bd show <id> --json` output. `ISSUE_JSON` is deprecated as a
dispatch field: the worker runs `bd show <id> --json` itself when it needs more
detail. Keep the prompt compact; carry only the summary, acceptance criteria,
and likely edit targets.

## Step 6: Dispatch The Worker

Spawn via the runtime's native subagent mechanism using the constructed prompt.
Use `fork_context=false` for Codex worker dispatches unless you are explicitly
dispatching a coordinator-like helper that must inherit thread history.

Reviewer-worker precondition:
- before dispatching a reviewer worker for PR `agent/<original-id>`, remove the
  original implementation worktree if it still exists so the reviewer can check
  out the PR branch in its own worktree safely

## Step 6a: Bootstrap The Worker

A spawned worker is not considered running until it proves it is operating from
the assigned worktree.

Bootstrap contract:
- `pwd` must equal `WORKTREE_PATH`
- current branch must equal expected worker branch
- `pwd` must not equal `REPO_ROOT`

If the runtime supports interim updates, require a short bootstrap
acknowledgement before continuing. If bootstrap never arrives, or if the worker
reports repo-root / `main` / `master` context, treat dispatch as failed and
renew the heartbeat before releasing the bead.

Codex note: a missing completion event is not a bootstrap failure. Bootstrap
failure requires explicit invalid context or no bootstrap evidence within the
bootstrap window.

## Step 7: Monitor Workers

- Track each worker's issue ID, branch, worktree path, start time, bootstrap
  status, and last progress signal.
- Do not count a slot as occupied until bootstrap succeeds.
- A missing bootstrap acknowledgement is a dispatch failure, not an
  implementation stall.
- If `main` or the repo-root checkout advances unexpectedly while a worker is
  supposedly active, stop and investigate worktree misbinding before
  dispatching more workers.
- Renew the coordinator stall heartbeat before every mutation and after long external
  checks.

Implementation-worker report contract:
- accepted `Status` values:
  - `completed-pr-opened`
  - `completed-direct-merge-candidate`
  - `blocked-awaiting-coordinator`
  - `invalid-runtime-context`
- required fields include `Branch`, `Head-Commit`, `Branch-Pushed`,
  `Handoff-Path`, `Recovery-State`, and `Resume-Condition`
- `Discovered-Follow-Ups-JSON` and `Blockers-JSON` must be valid JSON arrays
- parse those JSON arrays with a real JSON parser such as `jq`; do not infer
  structure from prose
- `blocked-awaiting-coordinator` is a valid terminal worker outcome, not a
  stall
- implementation workers are single-writer executors; if a worker reports that
  the issue needs multiple code-writing tracks, route it back through the
  coordinator or team-lead flow instead of letting the worker fan out locally

When an implementation worker completes, reconcile from the explicit Worker
Report first, then verify the reported branch / PR state:

1. Parse the report. If `Status` is missing, ambiguous, or contradicts the
   artifacts, do one recovery probe. If it remains ambiguous, treat it as a
   reconciliation failure instead of guessing.
2. Verify any reported side effects:
   - if a PR was reported, confirm it via `gh pr view <number>` or
     `gh pr list --state open --head "agent/<id>"`
   - if `Branch-Pushed=yes`, confirm the remote branch exists
   - if `Head-Commit` was reported, confirm the branch tip matches or explain
     the divergence before mutating Beads state
3. Handle by `Status`:
   - `completed-pr-opened`:
     - require a verified open PR
     - renew heartbeat, then block the original bead and set
       `external_ref=gh-pr:<N>`
     - run the Step 0a dedupe check, then ensure exactly one dedicated
       `pr-review-task` bead exists (create only if the dedupe check finds none)
     - create any discovered follow-up beads from
       `Discovered-Follow-Ups-JSON`
     - re-run Step 0 immediately so review/merge is prioritized
   - `completed-direct-merge-candidate`:
     - require `Branch-Pushed=yes` and no open PR
     - attempt fast-forward merge:
       ```bash
       git fetch origin
       git checkout main && git pull --ff-only
       git merge --ff-only origin/agent/<id>
       git push origin main
       ```
     - on success: renew heartbeat, then `bd close <id> --reason "Simple change merged to main"`
     - on failure: open a PR, set `external_ref`, ensure the review bead, and
       route through the PR-review lane
   - `blocked-awaiting-coordinator`:
     - do not treat this as stalled
     - renew heartbeat
     - convert `Blockers-JSON` entries into blocker beads and wire the original
       bead to depend on them
     - convert `Discovered-Follow-Ups-JSON` entries into linked follow-up beads
     - set the original bead to `blocked`
     - preserve recovery state explicitly:
       - if `Recovery-State=branch-pushed`, keep the remote branch for the next
         worker and clean the local worktree only after verifying the remote
         branch exists
       - if `Recovery-State=local-only`, quarantine the worktree under
         `.worktrees/recovery/<id>-<timestamp>` and append the recovery path in
         notes if the schema allows it; never silently delete unrecoverable
         local progress
       - if `Recovery-State=no-code-changes`, no quarantine is needed
   - `invalid-runtime-context`:
     - renew heartbeat, release the bead back to `open`, and clean the worktree
     - do not create blocker beads unless the report includes a separate
       project-level blocker that truly belongs in Beads
4. Only treat the run as stalled if the worker disappears after bootstrap or
   the report remains unusable after the recovery probe.

Ensure any discovered follow-up work from `Discovered-Follow-Ups-JSON` is
converted into new beads by the coordinator using sequential creation:

```bash
NEW_JSON=$(bd create "<title>" --description="<details>" -t <type> -p <priority> --json)
NEW_ID=$(echo "${NEW_JSON}" | jq -r '.id // .[0].id')
bd dep add "<original-id>" "${NEW_ID}"
```

Recommended extraction pattern:

```bash
FOLLOWUPS_JSON='<parse fenced JSON block from Worker Report>'
BLOCKERS_JSON='<parse fenced JSON block from Worker Report>'

echo "${FOLLOWUPS_JSON}" | jq -e 'type == "array"' >/dev/null
echo "${BLOCKERS_JSON}" | jq -e 'type == "array"' >/dev/null
```

Reviewer-worker report contract:
- accepted `Status` values:
  - `merged-pr`
  - `pushed-review-fixes`
  - `blocked-awaiting-coordinator`
  - `invalid-runtime-context`
- `Review-Actions-JSON`, `Discovered-Follow-Ups-JSON`, and `Blockers-JSON`
  must be valid JSON arrays
- `merged-pr` means GitHub merge is complete but Beads closure still belongs to
  the coordinator
- `pushed-review-fixes` means the worker changed GitHub state or pushed code,
  but the review bead should remain blocked for another pass

When a reviewer worker completes:
- if it reports `merged-pr`, confirm the PR is merged, then renew the heartbeat,
  close the review and original beads, and run the post-closure branch/worktree
  cleanup in Step 0b (`git push origin --delete agent/<id>`, remove the worktree
  and local branch) — the reviewer left the branch in place on purpose
- if it reports `blocked-awaiting-coordinator`, keep the review bead blocked
  and create any follow-up merge-blocker bead from the structured report if one
  does not already exist
- if it reports `pushed-review-fixes`, keep the review bead blocked and rely on
  the PR-review lane to revisit it later
- if it reports `invalid-runtime-context`, release the review bead back to
  `blocked`, remove `review-running`, and retry later after environment repair

If a worker fails bootstrap, or stalls after bootstrap:
- log the failure
- in Codex, send one interrupt heartbeat/status request before release
- renew heartbeat
- release the issue:
  - `pr-review-task`: `bd update <id> --status blocked --remove-label review-running --json`
  - otherwise: `bd update <id> --status open --json`
- clean up the worktree

## Step 8: Adaptive Polling And Loop

Do not use frequent free-running polling by default. Prefer state-driven
rechecks.

Immediate recheck triggers:
- worker completion
- worker bootstrap failure
- slot freed
- PR discovered, merged, or closed
- review bead created or deduped

Polling modes:
- active mode: 1-2 minute polls only when there is known near-term work waiting
  such as a dispatchable `pr-review-task`, a just-freed slot, or a PR cooldown
  about to expire
- idle mode: 10-15 minute polls when no workers are active and no dispatchable
  near-term review work exists

Prefer low-cost evidence over narrative heartbeats:
- worktree exists
- branch moved
- new commit
- PR state changed

After each cycle, return to Step 0.

## Progress Report

Render a progress report only when bead status actually changed since the last
report. Never derive the report from an unfiltered `bd list --json`; use
filtered queries plus targeted checks of the ids dispatched this cycle.

1. Query active work and the ids you dispatched or reconciled this cycle:
   ```bash
   bd list --status=in_progress --json
   ```
   Then `bd show <id> --json` for each recently dispatched / reconciled id to
   confirm closures, merges, or status moves.
2. If nothing changed, skip the report and proceed to Step 0.
3. If something changed, print the table once. For each closed bead, confirm
   the merge route:
   ```bash
   gh pr view <number> --json state,mergedAt   # PR-based merges
   ```
   The "Merged to main?" column shows `Yes`, `No`, or `—`.

```
═══════════════════════════════════════════════════════════════
  Beads Coordinator — Progress Report
  <TZ=Asia/Singapore date '+%Y-%m-%d %H:%M SGT'>
═══════════════════════════════════════════════════════════════

| # | Bead ID   | Title                    | Status      | Merged to main? |
|---|-----------|--------------------------|-------------|-----------------|
| 1 | beads-042 | Fix login redirect       | closed      | Yes             |
| 2 | beads-045 | Add pagination           | in_progress | —               |

Total closed this session: 1 / 10 open at start
═══════════════════════════════════════════════════════════════
```
