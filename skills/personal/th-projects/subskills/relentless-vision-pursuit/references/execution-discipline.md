# Execution Discipline: Throttle · Routing · Checkpoint · Resume

Pursuit fan-outs are the largest orchestrations in th-projects. A run that
violates any rule below is a defect, not a style choice — this is the
`/th-engineering` bar applied to the orchestration itself: deterministic
ordering, idempotent resume, fail-safe writes, no silent caps. Prefer a
boring, resumable script over a clever one.

## 1. Throttle — never more than 3 agents in flight

The only sanctioned launch path is staggered batches. There is no
"all-at-once" mode; do not offer or build one even under a `+Nk` token
budget — a larger budget buys *depth over hours*, never concurrency.

- Order all fan-out `agent()` thunks deterministically, split into batches
  of **2–3** via a `BATCH_SIZES` array and an `args.batch` cumulative
  counter. Run batches sequentially, each as one `await parallel(slice)`
  with `slice.length <= 3`.
- **Never pass the full agent array to one `parallel()`/`pipeline()` call**
  — that hands Workflow its default up-to-16-way concurrency.
- Guard in code before the first launch:
  `if (Math.max(...BATCH_SIZES) > 3) throw ...`, and `log()` the batch plan
  so the cap is auditable from run output.
- One batch per hourly `ScheduleWakeup(3600)` tick: launch batch 1, then
  re-invoke with `{scriptPath, resumeFromRunId, args: {batch: N+1}}` each
  tick — prior batches hit the resume cache; only the newest 2–3 agents run
  live. Synthesis only after the final batch. Workflow-completion
  notifications are informational — the wakeup drives cadence, never launch
  early on one. A full ~25-agent run ≈ 12–16h wall clock; that is the
  design, not a problem to optimize away.

**Precedent:** the 2026-07-22 butlers pursuit run launched ~10 concurrent
agents and took the owner from 5%→80% of the usage window in ~15 minutes;
it was killed mid-flight and resumed as `[3,2,2,…]` hourly batches. These
rules exist to make that mistake structurally unrepresentable.

## 2. Model routing by task difficulty

Tier each agent to its actual task; the lever is targeting, not blanket
cheapening. Assign via `agent(prompt, {model, effort})`:

| Role | `model` | `effort` |
|------|---------|----------|
| Orchestrator (this session): grounding, surface clustering, batch planning, synthesis, dossier authorship | session model | — |
| Cross-cutting sweepers and ideation lens agents (whole-system reasoning, must name real integration points) | `opus` | `high` |
| Per-surface auditors (scoped critique against a known bar — the bulk) | `sonnet` | `medium` |
| Mechanical passes (surface scoping, ledger-dedup extraction, wiring checks) | `haiku` | `low` |

When genuinely unsure which tier a task needs, round **up** — a weak plan
costs more than the model that would have made a good one.

## 3. Checkpoint every batch to disk

Harvested findings must never live only in conversation context or an
unfinished Workflow run — a kill loses at most one batch.

- After each batch, harvest structured outputs from the run's transcript
  dir (`journal.jsonl` records each `agent()` return; `agent-<id>.jsonl`
  is the fallback) and **append** to a durable harvest file
  (`<dossier-home>/<date>-vision-pursuit-harvest.json`), keyed by agent
  label.
- Write atomically: temp path in the same dir, then `rename()` over the
  target — a crash mid-write never leaves torn JSON.
- Maintain a state file
  `{last_batch, last_run_id, harvest_path, batch_plan, models}` beside it,
  updated after every batch. Harvest + state together must be sufficient to
  resume or hand-synthesize from a cold start; Phase 3 reads the harvest
  file, not live returns, so the dossier can be rebuilt from disk even if
  the resume chain or session context is lost.

## 4. Cadence, scale, and resume hygiene

- Scale the fan-out to the surface count. Small projects (≤6 surfaces) may
  skip Workflow entirely and run audits inline, sequentially — the phases
  and posture still apply; only the orchestration shrinks.
- Keep the state file current so wakeups survive context summarization.
- Re-run soon after a release → expect fewer NEW findings; that is success.
  Report movement, don't pad.
- If a fleet is mid-execution on a prior pursuit epic: audit the surfaces
  it has already landed (to measure) and ideate the lenses it is not
  touching; note the overlap in the report instead of filing colliding
  beads.
