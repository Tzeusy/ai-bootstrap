# Spec Reconciliation Mode

Exhaustive bidirectional reconciliation between OpenSpec specs and the actual implementation. Finds mismatches both ways and remediates: undocumented features get specs; unimplemented requirements get beads.

Run when the user asks to "reconcile spec vs implementation", "what's implemented but undocumented", "what's specified but missing", after a milestone, or before a release. Replaces the retired standalone `reconcile-spec-to-project` skill.

Exhaustive by design: every spec checked, both directions, no sampling. Still consumes the Phase 0 baseline (shape scan) and the same evidence labels ([Observed], [Inferred], [Unknown]).

## Phase R1: Inventory both sides

Build two parallel inventories with subagents — the orchestrator merges and decides, it doesn't do the heavy file-reading itself.

**Spec inventory** — one subagent per spec category, for each `openspec/specs/*/spec.md`:
- Spec name (directory) + category (infer from naming convention)
- Key requirements (Requirement headings + WHEN/THEN scenarios)
- Delta specs in active `openspec/changes/*/specs/` that override/extend the main spec — **active changes override main specs**; always check non-archived changes before flagging a gap

**Implementation inventory** — one subagent per major source directory:
- Read CLAUDE.md / README / `about/lay-and-land/` first for layout + conventions
- Walk each major source directory; identify modules, services, API routes, configuration, tools, tests
- Per unit: name, what it does, what it exposes
- Dedicated subagents for cross-cutting concerns (shared schemas, APIs, config)

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

## Phase R4: Remediation

The one project-review mode that creates artifacts beyond the report — every artifact traces 1:1 to a confirmed spec gap, so no direction analysis is smuggled in.

**Gap list B (undocumented) — write specs:**
1. Fits an existing spec's scope → extend it; else create `openspec/specs/{spec-name}/spec.md`
2. Follow [`spec-format.md`](../../../references/spec-format.md) exactly (heading hierarchy, WHEN/THEN bullets, naming)
3. Extract requirements from observed behavior; describe purpose + observable behavior, never internal architecture

**Gap list A (unimplemented) — file beads:**
1. More than 3 gaps → create a parent epic first: `bd create --title="Implement spec gaps from reconciliation audit" --type=epic --priority=2`
2. File each gap via `/beads-orchestration` (beads-writer subskill): reference the spec path + specific unmet requirements; set epic as parent; priority P1 core/infra, P2 domain logic, P3 UI/cosmetic
3. Create child beads sequentially (`&&`-chained, never parallel — ID collision risk); wire ordering with `bd dep add` after creation, not `--deps`
4. **Escalate instead of filing** when a gap is strategic (changes architecture, conflicts with doctrine, needs sequencing judgment) → `/project-direction` handoff packet, not straight to beads.

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
