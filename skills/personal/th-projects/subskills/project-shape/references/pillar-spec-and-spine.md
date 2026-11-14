# Spec and Spine — Capability Specs Layer Guide

## Purpose

The capability specs layer answers **WHAT**: exactly what must be built, with testable requirements tracing to design contracts and doctrine. Specs bridge design to implementation — acceptance criteria for every feature.

## Recommended Structure

```
openspec/
├── config.yaml                  # OpenSpec configuration
├── specs/                       # Main specs — current source of truth
│   ├── <domain>/spec.md         # One spec per domain/subsystem
│   └── ...
└── changes/
    └── <change-name>/           # Active specification change
        ├── proposal.md          # Why this change, impact assessment
        ├── design.md            # Design decisions for this change
        ├── tasks.md             # Task breakdown with counts
        ├── .openspec.yaml       # Change metadata
        └── specs/               # Delta specs — override main while active
            ├── <domain>/spec.md # ADDED/MODIFIED/REMOVED Requirements
            └── ...
```

## Requirement Format and Traceability

File syntax — heading hierarchy, main-vs-delta headings, `ID`/`Source`/`Scope`
lines, WHEN/THEN rules, test-tagging convention — is the package-wide shared
contract: [`../../../references/spec-format.md`](../../../references/spec-format.md).
Do not restate it; write to it.

Pillar-level rules on top of that syntax:

- Every requirement traces both ways: **up** to an RFC section or doctrine
  principle (its `Source:` line) and **down** to ≥1 WHEN/THEN scenario and a
  test citing its `ID`.
- The chain: `doctrine principle → RFC §section → spec requirement (ID) →
  WHEN/THEN scenario → test → code`.
- Check the chain mechanically before semantic review:
  `uv run <th-projects>/scripts/spec-trace-check.py <repo-root>`.

## Spec Lifecycle

Specs evolve through a managed lifecycle:

<!-- [DIAGRAM: spec-lifecycle]
Style: conceptual, simple. Use /th-engineering (excalidraw-diagram).
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
| **Code ahead of spec** | Implementation exists, no spec covers it | Draft from observed behavior, vision-gate it, bookkeep only behavior that serves cited doctrine (`[Observed]` main-spec edit); doctrine-neutral or conflicting behavior is an owner decision (`../../spec-concretization/` flow A) |
| **Spec ahead of code** | v1-mandatory requirement, no implementation | Reconcile with the existing backlog first, then plan the remaining work (`../../spec-concretization/` flow B) |
| **Spec-code mismatch** | Behavior contradicts spec | Spec wins by default (fix the code); amend the spec only on named evidence (doctrine/RFC/decision/external consumer) with owner sign-off |
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
1. Follow the shared spec-format routing rule: proposed behavior uses a delta;
   observed-behavior bookkeeping edits the main spec with evidence
2. Preserve RFC traceability on every modification
3. After syncing, main specs become the new source of truth
4. Bug fixes that reveal ambiguity → clarify the requirement
5. Refactors that change behavior → update affected scenarios
