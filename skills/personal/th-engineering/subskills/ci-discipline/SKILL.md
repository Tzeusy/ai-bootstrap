---
name: ci-discipline
description: >
  Use when designing, auditing, or speeding up a CI/CD pipeline, or when
  deciding where a check should run — gate placement by cost tier, computing
  each verdict once per tree, affected-only selection, merge-queue topology,
  queue-wait vs execution diagnosis, runtime budgets, and agent push/run
  habits that multiply CI runs. Complements test-rigor (what a test is
  worth) with where and how often checks run.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Opus 5.5
  status: active
  last_reviewed: "2026-11-01"
---

# CI Discipline

A pipeline's job: give a trustworthy merge verdict on the exact tree that
lands, as early and as cheaply as possible, and never compute the same verdict
twice. Slow CI is usually placement and duplication, not test count; test
count is the last lever, not the first.

## Use This Skill When

- CI is slow, clogged, or queues; PRs wait on runs that repeat work
- Deciding where a new check runs (editor loop, pre-commit, PR, merge
  queue, nightly)
- Auditing CI triggers, required checks, sharding, caching, or a merge queue
- Writing or reviewing guidance that tells agents when to run tests or push

## Do Not Use This Skill For

- Whether an individual test is worth keeping, or suite tiers and
  condensation — [test-rigor](../test-rigor/SKILL.md)
- Why a specific run is red or flaky — [diagnosis](../diagnosis/SKILL.md)
- Release readiness for one deploy — `/engineering:deploy-checklist`

## Core Rule

**Each verdict is computed once per tree, in the cheapest tier that can give
it, and reused until the tree changes.** A run whose result was already known
for this tree is waste, whoever ran it. A tree is the content being judged,
not the actor, branch, or session. For merge evidence it is the tree that
**lands** (the merge result), not the branch head
(`git rev-parse HEAD^{tree}` names a head's tree).

## Gate Tiers

Every check lives in exactly one tier. Promote a check only with a reason; a
check present in two tiers for the same tree is a finding.

| Tier | Runs | Budget | Holds |
|---|---|---|---|
| **Edit loop** (local) | Exact node, then its file or package | Seconds | The tests covering the change |
| **Pre-commit / pre-push** (local) | Deterministic, diff-scoped | ≤ ~10 s | Format, lint changed files, cheap guards |
| **PR** (hosted) | Affected-only selection plus guards | Minutes | Content signal: does this diff pass |
| **Terminal gate** (merge queue or exact-base gate) | Full broad suite on the exact tree that lands | Once per landing tree | Merge evidence |
| **Scheduled** (nightly) | Exhaustive, slow, quarantined, mutation, long e2e | Off the merge path | Drift detection; files issues, does not block |

- With a terminal gate, the PR tier never runs the full suite. Uncertainty in
  the affected-test planner widens the **selection** (add the lane, package,
  or dependent), not the whole run.
- Without a terminal gate, the PR's full run is the best gate available, not
  exact landing-tree evidence: it tests the merge with the base as it was when
  the run started. Nothing else recomputes it (not a local pre-PR copy, not a
  reviewer), and a post-merge run on the base branch catches the drift.
- **Skip a local broad run only when both hold**: the repo assigns broad lanes
  to hosted CI or a merge queue, and a required hosted check covers the tree
  that lands. Otherwise (no hosted CI, CI not required, a direct push to the
  base) the local broad run is the gate and is mandatory, once, on the head
  that will land. Reproducing a hosted failure locally is always fine.

## The Bar

Reviewable expectations; cite the one violated with file:line evidence.

1. **One placement policy, written down** — The repo states which tier owns
   which check (`AGENTS.md`, `docs/testing/ci.md`). Skills and agents defer
   to it; when it is missing, writing it is the first fix.
2. **No duplicate triggers** — One event per state change: `push` on every
   branch plus `pull_request` runs everything twice. Draft PRs and pre-PR
   branch pushes get the cheap tiers only. Superseded PR runs cancel
   (concurrency group per PR).
3. **Verdict reuse is explicit** — Evidence names the commit and tree it
   judged. Nobody re-runs a passing check on an unchanged tree for
   reassurance (engineering-bar bias 8). Independent review reads the hosted
   result on the exact head; it does not recompute it.
4. **Rebase only for a reason** — Conflicts, or an exact-base gate that
   requires it. A rebase of a green PR discards a paid run. With a merge
   queue, the queue integrates; nothing rebases to freshen.
5. **Budget the clock, not the count** — Track time-to-green p50/p95 split
   into queue wait, setup, and execution; the critical-path shard; and runs
   per merged PR. A test-count ratchet is a tripwire that prompts this
   measurement, not the budget itself.
6. **Diagnose before cutting** — Attribute the slow path, then take the fix
   ladder below in order. Condensing tests to fix runner queueing is a
   category error.
7. **Required checks are few and stable** — One aggregate verdict job is the
   required check, asserting which jobs each routing mode must run, so
   skipped jobs neither block nor silently pass.
   Changing the required set is a deliberate, reviewed change.
8. **Flakes leave the blocking path** — Quarantine with an owner and an
   expiry, measured on the scheduled tier. Retries in the blocking path are
   counted and reported, never silent (test-rigor bar 6).
9. **The pipeline is code under greenfield parity** — CI config has an
   owner and a size proportional to what it guards. A guard duplicating a
   test or lint rule is residue (one gate species per behavior). Frequent
   churn in the pipeline is itself a cost signal
   ([greenfield-parity](../greenfield-parity/SKILL.md) "tooling sprawl").

## Fix Ladder

Take the first rung that addresses the measured cause; re-measure before the
next.

1. **Remove duplicate runs** — triggers, local broad runs, reviewer re-runs,
   needless rebases, superseded runs not cancelled.
2. **Select, don't exhaust** — affected-only at the PR tier; the full suite
   once at the terminal gate.
3. **Cut setup** — dependency and build caches, reused databases, containers
   and migrations instead of per-test bootstrap.
4. **Balance the critical path** — shard by recorded duration so the slowest
   shard is not the floor.
5. **Fix capacity** — when queue wait dominates: runner pool size versus
   peak demand (jobs per run × concurrent runs), merge-queue build
   concurrency, fewer larger jobs.
6. **Condense the suite** — test-rigor's condensation pass, last.

## Agent Habits

Autonomous lanes multiply every waste above; agent guidance holds these:

- Iterate on the edit-loop tier; run the broad gate where the policy puts it.
- If pushes trigger CI, push when ready for review, not to back up WIP.
- Implementer and reviewer do not both recompute the hosted verdict; the
  reviewer reads it for the exact head and runs only targeted checks it has a
  specific reason for.
- Without a merge queue, keep one PR at the train head with fresh CI;
  hold overlapping PRs until it lands, then rebase the next only if it
  conflicts or the base requires up-to-date branches.
- Size watch deadlines from each job's observed p95; read the workflow's
  triggers and `run:` lines before claiming what CI covers.

## Workflow (pipeline audit)

1. **Inventory**: event × job matrix; tag each job with its tier. Mark
   duplicates (same verdict, same tree, two tiers or two actors), including
   local runs prescribed by agent guidance.
2. **Measure** a dated cohort: time-to-green split by queue, setup, and
   execution per job; runs per merged PR. Commands for GitHub Actions:
   [github-actions](references/github-actions.md).
3. **Attribute** the critical path, then pick the fix ladder rung.
4. **Write the placement policy** into the repo docs, in the same change as
   the pipeline edit.
5. **Verify**: re-measure on a comparable cohort; state before and after.

## Trigger Sanity Check

- Should trigger: "CI is too slow", "why does CI run twice", "pre-commit or
  CI?", "do we need a merge queue", "agents keep re-running the full suite".
- Should not trigger: "why is this test red" (diagnosis), "are these tests
  meaningful" (test-rigor), "cut a release" (deploy-checklist).
