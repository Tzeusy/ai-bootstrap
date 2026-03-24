# Law and Lore — Design Contracts Layer Guide

## Purpose

The design contracts layer answers **HOW**: how the system works at the wire/protocol/API level. These are the authoritative technical contracts that code must conform to — protobuf schemas, state machines, field allocations, latency budgets, and integration contracts.

## Recommended Structure

```
about/law-and-lore/
├── rfcs/                    # Numbered design documents
│   ├── 0001-<name>.md       # Each RFC defines a subsystem contract
│   ├── 0002-<name>.md
│   └── ...
├── reviews/                 # Review rounds per RFC
│   ├── 0001/
│   │   ├── round-1.md       # Reviewer feedback + author responses
│   │   └── round-2.md
│   └── ...
├── prompts/                 # Epic definitions derived from RFCs (optional)
│   ├── PREAMBLE.md          # Authority rules for epic creation
│   └── NN-<epic-name>.md    # One per implementation epic
└── notes/                   # Informal design notes, explorations (optional)
```

## RFC Format

Each RFC should follow a consistent structure:

```markdown
# RFC NNNN: <Title>

**Status:** Draft | Review | Accepted | Superseded
**Author:** <name>
**Date:** <YYYY-MM-DD>

## Summary
One paragraph: what this RFC defines and why.

## Motivation
What problem does this solve? Link to doctrine principles.

## Design
The technical contract. Include:
- Data models / protobuf schemas
- State machines with transition rules
- Wire formats and field allocations
- Quantitative budgets (latency, size, capacity)
- Error handling contracts

## Integration
How this subsystem connects to others. Cross-RFC references.

## Alternatives Considered
What was rejected and why. Prevents re-litigation.

## V1 Scope
What ships in v1 vs defers. Must align with doctrine's v1.md.
```

## Numbering Convention

- 4-digit zero-padded: `0001`, `0002`, etc.
- Numbers are permanent — never reuse a retired number
- Group related RFCs by functional area when possible

## Reviews

Reviews are critical for design quality. Structure:

```markdown
# RFC NNNN Review — Round N

**Reviewer:** <name/agent>
**Date:** <YYYY-MM-DD>

## Findings
- [Section §X.Y] <concern or question>
- [Section §X.Y] <concern or question>

## Author Response
- [Finding 1] <resolution>
- [Finding 2] <resolution>
```

Review rounds capture *why* a design took its current form. They're the project's institutional memory for trade-offs.

## Key Contracts

Identify and highlight load-bearing contracts — decisions that, if violated, break cross-subsystem integration. List these prominently in the local `law-and-lore` skill so agents see them immediately.

Examples of load-bearing contracts:
- Field number allocations in protobuf envelopes
- State machine transition rules
- Latency budgets on hot paths
- Priority/arbitration stacks

## Maturity Levels

| Level | Signal |
|-------|--------|
| Absent | No design docs beyond inline code comments |
| Nascent | Some design docs exist but unnumbered and unreviewed |
| Structured | Numbered RFCs in `about/law-and-lore/rfcs/`, some reviews |
| Mature | Complete RFC coverage of all subsystems, review rounds, cross-references, field allocation maps |

## Evolution

Design contracts evolve faster than doctrine but slower than code. When an RFC needs updating:
1. Create a new RFC or amendment (don't silently edit accepted RFCs)
2. Update downstream specs to reflect the change
3. Link the change to the motivating doctrine principle or implementation discovery
