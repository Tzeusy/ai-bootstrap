# OpenSpec Spec File Format Reference

Shared contract for every subskill that reads or writes specs. Defines what a
spec file looks like inside — both kinds — plus the traceability fields
(`ID`/`Source`/`Scope`) and the test-tagging convention that make the
doctrine → RFC → spec → test chain mechanically checkable.

Validate mechanically before semantic review:

```bash
uv run <th-projects>/scripts/spec-trace-check.py <repo-root> [--tests-dir <dir>] [--strict]
```

Not defined here:

- **Changeset scaffolding** — the `openspec` CLI owns it (`openspec new change
  "<name>"`); never hand-write `openspec/changes/` structure. Full authoring
  loop:
  [`../subskills/project-direction/references/openspec-changeset.md`](../subskills/project-direction/references/openspec-changeset.md).
- **Spec lifecycle** — explore → new → continue → apply → verify → sync →
  archive, and divergence resolution patterns:
  [`../subskills/project-shape/references/pillar-spec-and-spine.md`](../subskills/project-shape/references/pillar-spec-and-spine.md).

## Two File Kinds — Never Mix Their Headings

| Kind | Location | H2 headings | Written when |
|------|----------|-------------|--------------|
| **Main spec** | `openspec/specs/{spec-name}/spec.md` | `## Purpose`, `## Requirements` | Bookkeeping observed behavior (reconciliation R4); `openspec archive` syncing a finished change |
| **Delta spec** | `openspec/changes/{change}/specs/{spec-name}/spec.md` | `## ADDED Requirements`, `## MODIFIED Requirements`, `## REMOVED Requirements`, `## RENAMED Requirements` | Proposing future behavior (feature funnel Gate 5, direction Phase 2) |

Routing rule: **proposed future behavior goes through a delta changeset;
documenting behavior the code already exhibits edits main specs directly.**
Active (non-archived) changes override main specs — always check
`openspec/changes/*/specs/` before extending a main spec, and build on an
active delta rather than forking it.

`MODIFIED`/`REMOVED`/`RENAMED` sections match requirements by their exact
`### Requirement:` title text — copy the title verbatim from the main spec.

## Structure

Main spec:

```markdown
# {Main Title}

## Purpose
{1-3 sentence description of scope and value}

## Requirements

### Requirement: {Requirement Title}
ID: REQ-{spec-name}-001
Source: {RFC/design-doc §section, doctrine principle, or [Observed] code ref}
Scope: v1-mandatory

{1-2 sentence normative description; SHALL/MUST/SHOULD per RFC 2119}

#### Scenario: {Scenario Name}
- **WHEN** {condition/trigger}
- **THEN** {expected outcome}
- **AND** {additional outcome if applicable}
```

Delta spec: identical requirement/scenario blocks under the delta-operation
H2s instead of `## Requirements`, and no `## Purpose` section.

## Traceability Fields

Three plain-text lines immediately after each `### Requirement:` heading:

- **ID** — `REQ-{spec-name}-NNN`; `{spec-name}` is the spec directory name,
  `NNN` zero-padded and unique within the spec. IDs are permanent: `MODIFIED`
  keeps the ID, `REMOVED` retires it forever (never reuse), `ADDED` takes the
  next free number across main + active delta specs.
- **Source** — what justifies the requirement: RFC section
  (`RFC 0003 §2.1`), doctrine principle (`heart-and-soul/vision.md #3`), or
  observed behavior (`[Observed] src/config/loader.py`). One line, citable.
- **Scope** — `v1-mandatory` (must implement; generates tasks + tests) ·
  `v1-reserved` (schema defined, implementation may stub) · `post-v1`
  (documented for awareness only).

The chain these fields close: doctrine principle → RFC §section → spec
requirement (`ID`) → WHEN/THEN scenario → test citing the ID → code.

## Test Tagging

Every `v1-mandatory` requirement is cited by ≥1 test — the requirement ID in
the test name (`test_REQ_core_config_001_missing_field_blocks_startup`) or in
a comment/docstring adjacent to the test (`Spec: REQ-core-config-001`).
`spec-trace-check.py` greps the test tree for IDs and reports uncovered
requirements and stale IDs (cited in tests, absent from specs).

## Heading Hierarchy

- H1: Main spec title (one per file)
- H2: `Purpose` + `Requirements` (main) / delta-operation headings (delta)
- H3: Requirement (e.g., `### Requirement: Configuration Loading`)
- H4: Scenario (e.g., `#### Scenario: Valid config loads successfully`)

## WHEN/THEN/AND Rules

- Bullet list format (`- `)
- Bold keywords: `**WHEN**`, `**THEN**`, `**AND**`
- 1 WHEN, 1 THEN, 0-4 AND lines per scenario
- Describe *observable behavior*, not implementation details

## Formatting Conventions

| Pattern | Usage | Example |
|---------|-------|---------|
| Backticks | Code identifiers, config keys | `config.toml`, `load_config()` |
| Bold | Keywords and type names | **WHEN**, **AppConfig** |
| Quotes | String values, enum options | `"suggest"`, `"fail"` |

## Requirement Title Patterns

- State: "Requirement: Configuration Loading and Validation"
- Tools: "Requirement: Calendar Event CRUD Tools"
- Lifecycle: "Requirement: Startup Phase Sequence"
- Policy: "Requirement: Conflict Detection and Resolution"

## Scenario Naming

- Success: "Scenario: Valid config loads successfully"
- Error: "Scenario: Missing required field blocks startup"
- Edge: "Scenario: Unresolved env var blocks startup"

## Special Tags

`[TARGET-STATE]` marks aspirational/unimplemented requirements:

```markdown
### Requirement: [TARGET-STATE] Calendar Sync and Projection
```

## Spec Naming Conventions

Adopt a `{category}-{name}` pattern. Common categories:

- `core-{component}` — foundational infrastructure
- `module-{name}` — pluggable feature modules
- `api-{area}` — API surface areas
- `service-{name}` — standalone services
- `connector-{name}` — external integrations

Adapt categories to match the project's own architecture.

## Density Guidelines

- Purpose: 2-3 sentences
- Requirements per spec: 8-15 typical
- Scenarios per requirement: 2-5 typical
- Focus on *spirit and intent* — describe what the system does for the user,
  not internal architecture or data structures

## Legacy Specs Without IDs

Pre-existing specs missing `ID`/`Source`/`Scope` lines are not violations —
`spec-trace-check.py` warns (errors only under `--strict`). Backfill
opportunistically: any edit that touches a requirement adds its fields in the
same change. New requirements always carry all three.
