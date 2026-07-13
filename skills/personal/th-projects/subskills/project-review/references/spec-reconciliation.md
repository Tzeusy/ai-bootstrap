# Spec Reconciliation Mode

Exhaustive bidirectional reconciliation between OpenSpec specs and the actual
implementation. Report-only is the default. Enter remediation only when the
user explicitly asks to fix the confirmed gaps: undocumented observed behavior
gets main-spec bookkeeping; unimplemented approved behavior gets allocated
work.

Run when the user asks to "reconcile spec vs implementation", "what's implemented but undocumented", "what's specified but missing", after a milestone, or before a release. Replaces the retired standalone `reconcile-spec-to-project` skill.

Exhaustive by design: every spec checked, both directions, no sampling. Still consumes the Phase 0 baseline (shape scan) and the same evidence labels ([Observed], [Inferred], [Unknown]).

## Phase R0: Mechanical pass first

Run `uv run <th-projects>/scripts/spec-trace-check.py <repo-root>` before any
subagent spends tokens: structural defects, ID integrity, and stale/missing
test citations come out mechanically. Fix or note its findings, then scope R1
on what remains — semantic judgment only where the script can't reach. When
specs carry `ID:` lines (spec-format.md), key the R2 mapping table on
requirement IDs instead of prose titles.

## Phase R1: Inventory both sides

Build two parallel inventories with subagents — the orchestrator merges and
decides, it doesn't do the heavy file-reading itself. Partition by bounded,
non-overlapping capability or user-visible contract, not independently by spec
category and source directory; cap dispatch to available worker slots.

**Spec inventory** — assign each capability slice a primary evidence owner; for
each `openspec/specs/*/spec.md` in that slice:
- Spec name (directory) + category (infer from naming convention)
- Key requirements (Requirement headings + WHEN/THEN scenarios)
- Delta specs in active `openspec/changes/*/specs/` that override/extend the main spec — **active changes override main specs**; always check non-archived changes before flagging a gap

**Implementation inventory** — the same capability owner follows the contract
through its implementation locations:
- Read CLAUDE.md / README / `about/lay-and-land/` first for layout + conventions
- Walk each major source directory; identify modules, services, API routes, configuration, tools, tests
- Per unit: name, what it does, what it exposes
- Add a cross-cutting specialist only when a shared contract is independently
  reviewable; it advises capability owners and does not duplicate their scan

## Phase R2: Cross-reference

Build the mapping table in the main thread (it needs both inventories):

| Spec | Category | Implementation Location | Coverage | Notes |
|------|----------|------------------------|----------|-------|

Coverage: **Full** (all requirements implemented) · **Partial** (some implemented, gaps remain) · **None** (spec exists, no implementation) · **Undocumented** (implementation exists, no spec).

Judge by **spirit, not implementation details**: a spec is satisfied when the intent and user-facing behavior it describes are fulfilled — not when code structure matches the spec's wording. Internal data structures, module boundaries, and private APIs aren't spec concerns unless they're load-bearing contracts other components depend on. Flag a gap only when functional capability is missing or documented behavior diverges from reality.

## Phase R3: Gap analysis

Two gap lists:
- **A. Specified, not implemented** (coverage None/Partial): each unmet requirement with spec file path + scenario text; priority grouping core infrastructure > domain logic > UI/cosmetic.
- **B. Implemented, no spec** (coverage Undocumented): each implementation with file paths + behavioral summary; grouped by category.

## Phase R4: Remediation (explicit authorization required)

The one project-review mode that may create artifacts beyond the report — every
artifact traces to a confirmed gap. If the user asked only to audit, stop after
R3/R5 with a remediation proposal; do not edit specs or mutate Beads.

**Gap list B (undocumented) — write specs:**
1. Follow `spec-format.md`'s authoritative routing: observed behavior is
   main-spec bookkeeping, while proposed behavior requires a signed-off delta
2. Fits an existing spec's scope → extend it; else create `openspec/specs/{spec-name}/spec.md`
3. Follow [`spec-format.md`](../../../references/spec-format.md) exactly
4. Extract requirements from observed behavior; describe purpose + observable behavior, never internal architecture

**Gap list A (unimplemented) — file beads:**
1. Load [`work-allocation.md`](../../../references/work-allocation.md). Group
   adjacent unmet requirements by cohesive implementation seam; never make one
   bead per gap automatically.
2. Multiple independent outcomes → create a parent epic, then file cohesive
   children via `/beads-orchestration` (beads-writer), each citing exact unmet
   requirements and acceptance criteria.
3. Create children sequentially; wire ordering with `bd dep add` after creation.
4. **Escalate instead of filing** when a gap is strategic (changes
   architecture, conflicts with doctrine, needs sequencing judgment) →
   `/project-direction` handoff packet.
5. Evidence unknown → create a bounded investigation only when authorized,
   with evidence target, owner, blocking status, and exit criterion.

## Phase R5: Summary report

```
## Reconciliation Summary

### Stats
- Specs audited: N
- Full coverage: N
- Partial coverage: N (M requirements gap)
- No implementation: N
- Undocumented implementations: N

### Actions Taken
- Beads created: N (epic: <id>)
- Specs created: N
- Specs extended: N

### Escalated to project-direction
- [strategic gaps with reasons]

### Remaining Risks
- [items needing human judgment]
```

## Scope Boundary

Reconciliation answers "do spec and code agree, and patch the bookkeeping". It does NOT score health categories, build risk registers, or assign verdicts — that's the main audit flow. Want both? Run the audit and invoke this mode from it; never let reconciliation findings inflate or substitute for scored evidence.
