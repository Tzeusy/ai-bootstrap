# Spec Reconciliation Mode

Exhaustive bidirectional reconciliation between OpenSpec specifications and the
actual implementation. Finds mismatches in both directions and remediates them:
undocumented features get specs; unimplemented requirements get beads.

Run this mode when the user asks to "reconcile spec vs implementation", "what's
implemented but undocumented", "what's specified but missing", after a
milestone, or before a release. It replaces the retired standalone
`reconcile-spec-to-project` skill.

Unlike the health audit, this mode is exhaustive by design: every spec is
checked, both directions, no sampling. It still consumes the Phase 0 baseline
(shape scan) and uses the same evidence labels ([Observed], [Inferred],
[Unknown]).

## Phase R1: Inventory Both Sides

Build two parallel inventories using subagents — the orchestrator merges and
decides; it does not do the heavy file-reading itself.

**Spec inventory** — one subagent per spec category, for each
`openspec/specs/*/spec.md`:
- Spec name (directory name) and category (infer from naming convention)
- Key requirements (extract Requirement headings and WHEN/THEN scenarios)
- Any delta specs in active `openspec/changes/*/specs/` that override or extend
  the main spec — **active changes override main specs**; always check
  non-archived changes before flagging a gap

**Implementation inventory** — one subagent per major source directory:
- Read CLAUDE.md / README / `about/lay-and-land/` first for layout and
  conventions
- Walk each major source directory; identify modules, services, API routes,
  configuration, tools, and tests
- Capture per implementation unit: name, what it does, what it exposes
- Dedicated subagents for cross-cutting concerns (shared schemas, APIs, config)

## Phase R2: Cross-Reference

Build the mapping table in the main thread (it needs both inventories):

| Spec | Category | Implementation Location | Coverage | Notes |
|------|----------|------------------------|----------|-------|

Coverage ratings:
- **Full** — all spec requirements have corresponding implementation
- **Partial** — some requirements implemented, gaps remain
- **None** — spec exists but no implementation found
- **Undocumented** — implementation exists but no spec covers it

Judge coverage by **spirit, not implementation details**: a spec is satisfied
when the intent and user-facing behavior it describes are fulfilled — not when
the code structure matches the spec's wording. Internal data structures, module
boundaries, and private APIs are not spec concerns unless they are load-bearing
contracts other components depend on. Only flag a gap when functional
capability is missing or documented behavior diverges from reality.

## Phase R3: Gap Analysis

Produce two gap lists:

**A. Specified, not implemented** (coverage = None or Partial):
- Each unmet requirement with its spec file path and scenario text
- Priority grouping: core infrastructure > domain logic > UI/cosmetic

**B. Implemented, no spec** (coverage = Undocumented):
- Each implementation with file paths and a behavioral summary
- Grouped by category

## Phase R4: Remediation

This is the one project-review mode that creates artifacts beyond the report,
because every artifact traces 1:1 to a confirmed spec gap — no direction
analysis is being smuggled in.

**Gap list B (undocumented implementations) — write specs:**
1. If the feature fits an existing spec's scope, extend that spec; otherwise
   create `openspec/specs/{spec-name}/spec.md`
2. Follow [`spec-format.md`](./spec-format.md) exactly (heading hierarchy,
   WHEN/THEN bullet format, naming conventions)
3. Extract requirements from observed behavior; describe purpose and
   observable behavior, never internal architecture

**Gap list A (unimplemented requirements) — file beads:**
1. If more than 3 gaps, create a parent epic first:
   `bd create --title="Implement spec gaps from reconciliation audit" --type=epic --priority=2`
2. File each gap via `/beads-orchestration` (beads-writer subskill): reference
   the spec path and the specific unmet requirements; set the epic as parent;
   priority P1 core/infrastructure, P2 domain logic, P3 UI/cosmetic
3. Create child beads sequentially (`&&`-chained, never parallel — ID collision
   risk); wire ordering with `bd dep add` after creation, not `--deps`
4. **Escalate instead of filing** when a gap is strategic: it changes
   architecture, conflicts with doctrine, or needs sequencing judgment. Those
   go into the `/project-direction` handoff packet, not straight to beads.

## Phase R5: Summary Report

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

Reconciliation answers "do spec and code agree, and patch the bookkeeping". It
does not score health categories, build risk registers, or assign verdicts —
that is the main audit flow. If the user wants both, run the audit and invoke
this mode from it; do not let reconciliation findings inflate or substitute
for scored evidence.
