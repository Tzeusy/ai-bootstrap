# Spec and Spine — Capability Specs Layer Guide

## Purpose

The capability specs layer answers **WHAT**: what exactly must be built, with testable requirements that trace to design contracts and doctrine. Specs bridge design to implementation — they're the acceptance criteria for every feature.

## Recommended Structure

```
openspec/
├── config.yaml                  # OpenSpec configuration
└── changes/
    └── <change-name>/           # Active specification change
        ├── proposal.md          # Why this change, impact assessment
        ├── design.md            # Design decisions for this change
        ├── tasks.md             # Task breakdown with counts
        ├── .openspec.yaml       # Change metadata
        └── specs/               # Normative capability specs
            ├── <domain>/spec.md # One spec per domain/subsystem
            └── ...
```

## Requirement Format

Every requirement follows a consistent testable pattern:

```markdown
### Requirement: <Name>

<Normative text using SHALL/MUST/SHOULD per RFC 2119>

Source: RFC NNNN §X.Y
Scope: v1-mandatory | v1-reserved | post-v1

#### Scenario: <Name>
- **WHEN** <precondition or trigger>
- **THEN** <expected behavior or outcome>

#### Scenario: <Another Name>
- **WHEN** <different precondition>
- **THEN** <expected behavior>
```

### Scope Tags

- **v1-mandatory** — Must be implemented. Generates tasks, tests, and implementation planning.
- **v1-reserved** — Schema defined, implementation may be minimal or stubbed. Forward-compatible.
- **post-v1** — Documented for awareness. No implementation required.

### Traceability

Every requirement must include:
- **Source**: Which RFC section and doctrine principle justify it
- **Scenarios**: WHEN/THEN pairs that serve as acceptance criteria
- **Scope**: Whether it's mandatory for current milestone

The chain: `doctrine principle → RFC §section → spec requirement → WHEN/THEN scenario → test → code`

## Spec Lifecycle

Specs evolve through a managed lifecycle:

<!-- [DIAGRAM: spec-lifecycle]
Style: conceptual, simple. Use /excalidraw-diagram.
Layout: horizontal timeline with spiral/cycle return.
Elements:
  - 7 stages as small dots on a horizontal timeline line, each with a free-floating label above:
    "explore" → "new" → "continue" → "apply" → "verify" → "sync" → "archive"
  - Arrows connecting each dot sequentially left-to-right
  - A dashed cycle arrow from "verify" back to "continue", labeled "issues found — iterate"
  - Color gradient: early stages (explore, new) in lighter/cooler tones, later stages (sync, archive) in warmer/darker tones
  - "archive" endpoint as a filled dot (completion)
Argument: Specs have a lifecycle — they're not write-once. The verify→continue loop ensures specs stay honest.
-->

| Phase | Action |
|-------|--------|
| **explore** | Investigate and clarify requirements before committing |
| **new** | Create a delta spec (additions/modifications within a change) |
| **continue** | Resume work on an in-progress spec change |
| **apply** | Merge finalized spec artifacts |
| **verify** | Validate: does code satisfy spec? Does spec match RFC? |
| **sync** | Propagate delta specs to main specs |
| **archive** | Close the change after verification |

## Divergence Patterns

Four patterns to watch for and resolve:

| Pattern | Signal | Resolution |
|---------|--------|------------|
| **Code ahead of spec** | Implementation exists, no spec covers it | Create delta spec documenting the capability |
| **Spec ahead of code** | v1-mandatory requirement, no implementation | Create implementation tasks for unimplemented requirements |
| **Spec-code mismatch** | Behavior contradicts spec | Determine which is correct (consult RFC/doctrine), fix the wrong one |
| **New feature** | Neither spec nor code exists | Start with explore, then spec, then code |

## Domain Organization

Organize specs by subsystem domain. Each domain maps to one or more RFCs:

```
specs/
├── scene-graph/spec.md          ← RFC 0001
├── runtime-kernel/spec.md       ← RFC 0002
├── timing-model/spec.md         ← RFC 0003
└── ...
```

Keep the mapping table in the local `spec-and-spine` skill so agents can look up which spec covers their current work.

## Maturity Levels

| Level | Signal |
|-------|--------|
| Absent | No formal requirements, features defined only in issues/tickets |
| Nascent | Some requirements exist but informal, no WHEN/THEN scenarios |
| Structured | `openspec/` folder with specs, some traceability to RFCs |
| Mature | Full spec coverage of v1 scope, all requirements traced to RFCs, WHEN/THEN scenarios for each, actively maintained via lifecycle |

## Evolution

Specs evolve at the pace of implementation. When updating:
1. Never silently edit — use the delta spec lifecycle
2. Preserve RFC traceability on every modification
3. After syncing, main specs become the new source of truth
4. Bug fixes that reveal ambiguity → clarify the requirement
5. Refactors that change behavior → update affected scenarios
