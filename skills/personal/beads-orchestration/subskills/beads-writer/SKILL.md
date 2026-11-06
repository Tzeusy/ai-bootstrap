---
name: beads-writer
description: Use when creating or decomposing Beads issues for a project backlog, including new features, bugs, epics, backlog grooming, or converting vague asks into actionable Beads work in a Beads-backed repository.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-11-06"
compatibility: Requires a Beads-backed repository with the `bd` CLI available. Assumes the agent can inspect the target project workspace before creating issues.
---

# Beads Writer

Create high-quality beads issues through repo-grounded research and deliberate field selection. This skill is a routing layer over the Beads operating model described in [`../../../../../README.md`](../../../../../README.md): issue writing should reinforce that workflow, not compete with it.

Write a concise current packet with exact governing references so a fresh owner can act without the creation chat. Tracking and delivery granularity differ: related existing beads may share one package while retaining their own acceptance.

## Use This Skill When

- A user asks to create one or more beads issues for a feature, bug, task, or backlog item
- A user wants a vague ask decomposed into actionable beads or an epic with child beads
- A discovered issue needs a proper bead instead of a quick title-only stub
- A backlog-grooming pass needs better scope, dependencies, or acceptance criteria

## Do Not Use This Skill When

- The work already exists as a well-formed bead and should now be implemented: use `beads-worker`
- The task is to review a whole repository or generate a roadmap from audit findings: use `th-projects` (project-review or project-direction subskills)
- The task is exhaustive spec-versus-code reconciliation rather than issue writing: use `th-projects` (project-review spec-reconciliation mode)

## Core Rules

- Ground every bead in the target repo's actual code, naming, issue graph, and constraints before writing it.
- Prefer one bead per testable outcome. Split unrelated acceptance criteria.
- Apply the shared
  [`th-projects` work-allocation contract](../../../th-projects/references/work-allocation.md)
  before creating or decomposing implementation work.
- Keep accepted outcomes finite and visibly partial until mandatory acceptance is met.
- Use one cross-child closeout path when needed; an existing outcome checklist or report may suffice. Do not create recursive reconciliation generations or split to meet a child-count quota.
- Use `bd create`, not `bd q`, when you need a real description.
- Do not pass dependency flags to `bd create`; create first, then wire with `bd dep add`.
- Reconcile against the existing backlog before creating: `bd search` the
  surface and title terms; attach, supersede, or reopen an existing bead
  before filing a new one. Audit-derived batches follow
  [`th-engineering/subskills/greenfield-parity/references/idempotent-audit.md`](../../../th-engineering/subskills/greenfield-parity/references/idempotent-audit.md)
  (ledger, audit-key, convergence record) so re-runs file nothing twice.
- Stamp an execution-complexity label on every bead at creation:
  `complexity:low`, `complexity:medium`, `complexity:high`, or
  `complexity:epic`. The coordinator maps this label straight to a worker
  model tier unless the design/specification override or Reconciliation Floor
  in `../beads-coordinator/references/runtime-and-safety.md` applies. Calibrate
  honestly: `low` is docs/config/test-only or single-file mechanical work with
  no design judgment; when in doubt between two tiers, pick the lower — the
  coordinator escalates on evidence.
- Keep non-lane work out of the dispatch queue with one of two labels, which
  `rank_ready_work.py` excludes:
  - `no-dispatch` for tracking or meta beads, such as a trial log, a decision
    record, or an owner checklist.
  - `scope:local-state` for work on gitignored state that exists only in the
    main checkout (`.beads/` leftovers, caches, local databases), which no
    worktree reaches. Split a mixed bead so the tracked-file part stays
    ordinary lane work; the owner does the local-state part, or names a
    looper for it.

## Read Order

| File | Read when | Content |
|------|-----------|---------|
| [`references/workflow.md`](references/workflow.md) | Every real use of this skill | Research-first workflow, decomposition rules, creation sequence, and verification flow |
| [`../../../th-projects/references/work-allocation.md`](../../../th-projects/references/work-allocation.md) | Shaping implementation boundaries or dispatch packets | Cohesive delivery boundaries, current packets, semantic readiness, and discovery triage |
| [`references/fields-and-examples.md`](references/fields-and-examples.md) | Crafting issue text or choosing fields | Field schema, type/priority guidance, and example beads |
| [`references/reconciliation-beads.md`](references/reconciliation-beads.md) | Writing or checking an epic | Finite outcome closeout, optional closeout-bead contract, and evidence prompt |
| [`references/quality-checklist.md`](references/quality-checklist.md) | Before finalizing or after creating beads | Final checklist, persistence checks, and anti-patterns |

## Trigger Sanity Check

- Should trigger: "Break this feature request into beads and make sure each child has enough context for a fresh worker."
- Should not trigger: "Implement bead `bd-123` in its assigned worktree."

## Resources

### references/
- `workflow.md` — Primary execution flow for research, decomposition, creation, and verification.
- `fields-and-examples.md` — Field schema, type selection guide, priority calibration table, and exemplary beads.
- `reconciliation-beads.md` — Finite outcome closeout and an optional verification prompt.
- `quality-checklist.md` — Final review checklist, persistence checks, and anti-patterns to remove.
