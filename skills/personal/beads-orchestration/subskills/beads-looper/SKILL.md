---
name: beads-looper
description: Use when one self-paced session should work a Beads backlog as its own single-lane coordinator, with no central coordinator session — typically under `/loop`, one of several tmux panes sharing a tracker. Implement mode takes the next finish-first bead, works it to acceptance in its own worktree, passes an adversarial verifier, then lands it or hands its PR off; review mode is the sticky review lane that reviews, merges, closes, and returns corrections for handed-off PRs.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Opus 5.5
  status: active
  last_reviewed: "2026-11-01"
compatibility: Requires a Beads-backed repository with `bd` v1.3+ (`--claim`, `--if-assignee`), `uv`, `git` with worktree support, an authenticated `gh`, `jq`, and `python3`, plus a native subagent mechanism for the verifier and a self-paced repeat primitive such as Claude Code's `/loop`.
---

# Beads Looper

A looper is one long-lived session that acts as both coordinator and worker for
a single lane. Each iteration it claims one bead, works it in that bead's own
worktree, reconciles the outcome itself, removes the worktree, and schedules
its next wake. Several loopers, usually one tmux pane each, share a tracker
through the same registry, atomic claims, finish-first queue, and global lane
budget that parallel coordinators use. Because no central session exists,
none has to be paid for. Context travels in bead fields, PRs, and notes, so
beads must be cold-start self-contained (`../beads-writer/SKILL.md`).

## Use This Skill When

- "run this pane as a beads lane", "/loop through the ready queue"
- several independent lanes should share one backlog without a coordinator
- a pane should be the review lane for PRs the other lanes open

## Do Not Use This Skill When

- one session should run several lanes with central reconciliation and Team
  Lead mode: use `../beads-coordinator/SKILL.md`
- a coordinator already dispatched you one bead: use `../beads-worker/SKILL.md`
  or `../beads-pr-reviewer-worker/SKILL.md`
- authoring or decomposing beads: use `../beads-writer/SKILL.md`

## Modes

| Mode | Takes | Does | Read |
|---|---|---|---|
| `implement` (default) | a `review-correction` bead first, then the top claimable row of the finish-first queue, optionally scoped to one epic | runs beads-worker's phases, passes the verifier, lands the bead or hands its PR to the review lane | [`references/implement-cycle.md`](references/implement-cycle.md), [`references/adversarial-verifier.md`](references/adversarial-verifier.md) |
| `review` | PR units handed off by implement lanes, oldest PR first | runs beads-pr-reviewer-worker's phases at the exact head, then merges and closes, or returns corrections | [`references/review-cycle.md`](references/review-cycle.md) |

Implement lanes only open PRs. Without a review lane, handed-off PRs wait, so
run one review lane per tracker. Load only your mode's references.

## Launch

Size the lane budget to the panes first. Every looper spends one lane while it
holds an `in_progress` bead, the review lane included. Only the owner sets
`beads.max_lanes` (`../beads-coordinator/references/runtime-and-safety.md` →
"Parallel Coordinators"). Unattended panes also need a permission mode that
cannot stall on a prompt.

```bash
tmux new-session -d -s beads -c "$REPO_ROOT"   # then one window per lane, each running `claude`
```

Start each pane with one line naming the mode and, optionally, a focus epic:

```text
/loop Use beads-orchestration → beads-looper, implement mode, epic <epic-id>
/loop Use beads-orchestration → beads-looper, review mode
```

## Non-Negotiable Invariants

- **Register as a coordinator.** Mint `LOOPER_ID` with
  `../beads-coordinator/scripts/coordinator_registry.py new-id --runtime <runtime>`.
  The id keeps the `coordinator:` prefix, so the lane budget, guarded
  adoption, and `beads-cleanup` count the looper as a coordinator. Register
  `--startup` on the first iteration and deregister on stop. Renew on every
  wake, and also at the heartbeat checkpoints during long work, with
  `--wake-minutes` sized to cover the next stretch. A looper that is busy but
  silent reads as dead, and a peer adopts its bead. Pass
  `--actor "$LOOPER_ID"` on every `bd` command. Print `LOOPER_ID` in every
  iteration report so it survives compaction. If it is lost anyway, mint a new
  id; the old claims return through guarded adoption once their registration
  lapses.
- **One bead at a time, inside the budget.** Claim only while
  `rank_ready_work.py` reports `capacity.free > 0`, always with the atomic
  `--claim`. A refused claim means a peer won the bead: take the next row and
  never contest it.
- **Hold-only mutation authority.** You may mutate only the beads assigned to
  `LOOPER_ID`, plus the beads you create. You take a bead over only by claim,
  by guarded adoption of a dead peer's bead, or by a compare-and-swap on a
  handed-off one (`--if-assignee ''`, where exit 13 means a peer got there
  first).
- **A PR has one holder at a time.** The implement lane holds the original
  bead while implementing or correcting it. It then releases the PR unit
  (original plus review bead) to the review lane. The review lane holds the
  unit through review, merge, and closure, and releases the original back to
  the implement lanes when corrections are needed. Every hand-off is a guarded
  update, and two lanes never hold one unit's beads at once, with one
  exception. During corrections the review lane keeps the review bead so the
  same reviewer re-checks, while an implement lane holds the original. A
  release is always the iteration's last write, after the worktree is gone. If
  a guarded release exits 13, a peer adopted the bead, so stop touching it and
  report `lost-claim`.
- **One worktree per bead, gone when the bead leaves the lane.** Create it at
  claim under `.worktrees/parallel-agents/`. Base it on `origin/<base>`, or on
  `origin/agent/<id>` when a previous holder pushed one. When the bead is
  closed, handed off, or released, remove the worktree and its local branch.
  The remote branch carries whatever state the next holder needs. Never edit
  in `REPO_ROOT` and never move its checkout, because every pane shares it.
  Quarantine unpublished work rather than deleting it.
- **Verify before anything leaves the lane.** An implementation lands or opens
  a PR only after a fresh, read-only adversarial verifier has checked it
  against its acceptance criteria. A lane never reviews work it authored.
- **Close only after merge confirmation**
  (`../beads-coordinator/references/runtime-and-safety.md` → "Bead Closure
  Rule").
- **The package invariants still hold** (`../../SKILL.md` → "Shared
  invariants"). These include spirit over spec over DAG (the readiness gate,
  `needs-shaping`), finish-first ordering, decide-don't-defer, token
  efficiency, the quality gates, and build artifacts dying with the bead.
  Every iteration ends on a report.

## Iteration Skeleton

1. **Wake.** Renew the registration, and recover dead peers' claims from the
   ranker's `unowned_claims` and `stranded` rows (guarded). On the first
   iteration, also run the preflight: `bd doctor`, the `beads-cleanup` scan
   (`../beads-cleanup/scripts/cleanup_scan.py`, report-only), and
   `MERGE_QUEUE` detection (`../beads-coordinator/references/coordinator-loop.md`
   → "Preflight"). Read the target repo's `AGENTS.md`/`CLAUDE.md`. Act on
   cleanup findings only where "Parallel Coordinators" allows adoption.
2. **Select and claim.** Follow the steps for your mode.
3. **Work.** Follow the execution subskill's phases inside the bead's
   worktree. Its "never mutate Beads" boundary binds lifecycle writes in this
   step; those wait for step 4. The liveness renewals (stall heartbeat and
   registration) still run.
4. **Reconcile.** As holder, apply the outcome to your own beads, then close
   the bead or wire the hand-off.
5. **Tear down, then release.** Remove the worktree and local branch, and
   delete build artifacts the outcome retired. Then make the guarded release
   that hands the bead off.
6. **Report and schedule.** Write one compact block: `LOOPER_ID`, mode, bead,
   outcome, PR, epic progress, beads skipped and why, next wake. Then schedule
   the next wake.

## Wake Cadence

- After an iteration that did work, wake at the runtime's minimum delay,
  because more work is likely.
- When nothing is claimable, follow
  `../beads-coordinator/references/runtime-and-safety.md` → "Orchestrator
  Wake Cadence" and its "No-progress frontier", stop rule included. A review
  lane holding merge-queued PRs has near-term work.
- On stop, deregister and write a final report. Under `/loop`, stop by ending
  the loop, and pass the same `/loop` prompt back on every wake.

## Retire Instead Of Drifting

A looper runs one model for its whole life, because caches are per model.
Skip a row whose required tier exceeds this session's model
(`../beads-coordinator/references/runtime-and-safety.md` → "Assignment Rules"
and "Reconciliation Floor"), and name it in the report. On compaction drift
(re-asking settled questions, contradicting earlier decisions, losing the
acceptance criteria), finish reconciling the current bead, then deregister
and stop with a `retired` report. The operator restarts the pane cold
(`../../references/token-efficiency.md` → "Retire a lane").

## References

| File | Read when |
|---|---|
| [`references/implement-cycle.md`](references/implement-cycle.md) | implement mode: selection, worktree, work, landing, PR hand-off, blockers, corrections |
| [`references/review-cycle.md`](references/review-cycle.md) | review mode: sweeps, taking a unit, review, merge and closure, correction hand-back |
| [`references/adversarial-verifier.md`](references/adversarial-verifier.md) | implement mode, before anything leaves the lane |
| [`../beads-coordinator/references/runtime-and-safety.md`](../beads-coordinator/references/runtime-and-safety.md) | claim, heartbeat, registry, adoption, budget, cadence, closure rules (canonical numbers live here) |
| [`../../references/known-errors.md`](../../references/known-errors.md) | any unexpected `bd`/`gh` error: search it, never read it whole |
