# Epic Report Bead

Execution guide for the **epic report bead** — a child bead created by `/th-project-direction` during work plan materialization. This bead generates a human-readable report of what was built, for a human to review.

This file is referenced in the report bead's description. The executor (human, `/beads-worker`, or agent) follows this guide.

---

## Bead Template

When `/th-project-direction` calls `/beads-writer` to create the epic, include a report bead with this structure:

```
Title: "Generate epic report for: {epic title}"
Type: task
Priority: same as epic
Parent: {epic-id}
Dependencies: ALL implementation children + reconciliation bead (this runs last)
Description: |
  Generate a human-readable epic report following the guide in
  /th-project-direction references/epic-report.md.

  Epic ID: {epic-id}
  Spec sections covered: {list}

  Bootstrap with:
    bash <skill_dir>/scripts/epic-report-scaffold.sh {epic-id}

  Then fill sections, generate diagrams via /excalidraw-diagram,
  create follow-up beads, and commit.

Acceptance criteria:
  - Report exists at docs/reports/{epic-id}-{slug}.md
  - Architecture diagram(s) rendered and embedded
  - Spec compliance matrix complete
  - Follow-up beads created for remaining TODOs
  - Report linked to epic via bd update --append-notes
```

---

## When to Include

Include a report bead for epics that are:
- Non-trivial (>=3 children or >100 lines expected)
- Touching multiple modules or introducing architectural changes
- Delivering a user-facing milestone

Skip for: single-bead fixes, config changes, doc-only epics.

---

## Execution Workflow

When the report bead is claimed and executed:

### Step 1: Gather inputs

```bash
bd show <epic-id> --json
bd children <epic-id> --json
bd dep tree <epic-id>
git log --oneline --all --grep="<epic-id>"
```

### Step 2: Run scaffold

```bash
bash <skill_dir>/scripts/epic-report-scaffold.sh <epic-id>
```

This creates `docs/reports/<epic-id>-<slug>.md` with metadata pre-filled from beads (children table, commit history, files changed). The scaffold contains TODO markers for each section.

### Step 3: Fill report sections

See the section guide below for each section's content.

### Step 4: Generate diagrams

Use `/excalidraw-diagram` to create architecture/workflow diagrams. Render to PNG and embed in the report markdown.

**Color conventions**:
- New/added components: `#a7f3d0` fill (green)
- Modified components: `#fef3c7` fill (yellow)
- Existing/unchanged: `#e2e8f0` fill (gray)
- Removed/deprecated: `#fecaca` fill (red)
- External dependencies: `#ddd6fe` fill (purple)

**When to generate diagrams**:

| Epic scope | Diagrams needed |
|-----------|----------------|
| Single module, <5 files | None (code references suffice) |
| Single module, 5-15 files | 1 diagram: component or data flow |
| Multi-module, >15 files | 2 diagrams: component overview + detail of most complex area |
| Architectural change | 2 diagrams: before/after |

Store diagram sources at `docs/reports/diagrams/<epic-id>-*.excalidraw` with rendered PNGs alongside.

### Step 5: Create follow-up beads

For each TODO or gap identified during report writing:

```bash
NEW_ID=$(bd create --title="..." --type=task --priority=2 --parent=<epic-id> --json | jq -r '.id')
bd dep add $NEW_ID <depends-on-id>  # if needed
```

### Step 6: Close out

```bash
bd update <epic-id> --append-notes "Epic report: docs/reports/<epic-id>-<slug>.md"
bd close <report-bead-id> --reason="Report generated. Created N follow-up beads."
git add docs/reports/ && git commit -m "docs: epic report for <epic-id>"
```

---

## Report Sections

### 1. Summary

2-3 paragraphs covering:
- What was built and why (link to project spirit)
- Key design decisions made during implementation
- Current state: what works, what's provisional, what's deferred

### 2. Architecture

1-2 excalidraw diagrams showing what was built or changed.

Diagram types to consider:

| Diagram | When to use |
|---------|------------|
| Component diagram | New modules/services added |
| Data flow diagram | New data paths added |
| Sequence diagram | New multi-step workflows |
| Before/after | Refactoring or redesign |
| Dependency graph | New integrations |

### 3. Implementation Walkthrough

For each child bead:

```markdown
### {child-bead-title} ({bead-id})
**Status**: {closed / open}
**Spec section**: {linked spec section}

**What was done**: {1-3 sentences}

**Key code locations**:
- `src/auth/middleware.ts:42-68` — JWT validation logic

**Design decisions**:
- {decision}: {why} — [Observed] from `{file:line}`

**Caveats**: {known limitations, when to address}
```

Always use `file:line-range` format for code references.

### 4. Spec Compliance Matrix

```markdown
| Spec Section | Status | Evidence | Notes |
|-------------|--------|---------|-------|
| `spec/auth.md §3.1` | Implemented | `src/auth/middleware.ts:42` | — |
| `spec/auth.md §3.2` | Partially | `src/auth/refresh.ts:10` | Missing token rotation |
```

Statuses: **Implemented** / **Partially implemented** / **Contradicted** / **Deferred** / **Not applicable**

### 5. Test Coverage

- New/changed test files with counts and coverage description
- Coverage gaps with risk level and whether a follow-up bead is needed
- Brief confidence assessment: behavior vs implementation testing

### 6. Subsequent Work

- Open beads (existing children not yet closed)
- New follow-up beads (created during report generation)
- Deferred decisions with revisit triggers

### 7. Risks & Reviewer Notes

- Known risks with severity, mitigation, and evidence
- Questions needing human judgment
- Prioritized list of files/areas for human review

### 8. Appendix

- Commits referencing this epic
- Files changed (git diff --stat)
- Diagram source files table

---

## Diagram Quality Checklist

Before embedding:
- [ ] All boxes have readable labels (no truncation)
- [ ] Arrows have clear direction and labeled relationships
- [ ] Color coding matches convention
- [ ] Diagram has a title
- [ ] No overlapping elements
- [ ] Rendered PNG is crisp at normal zoom
