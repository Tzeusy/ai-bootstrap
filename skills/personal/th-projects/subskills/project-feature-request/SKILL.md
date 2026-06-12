---
name: project-feature-request
description: >
  Concretize a single fuzzy feature or project request into a signed-off
  specification delta before any planning or implementation: extract the
  motifs, gate against doctrine, place it in the topology, sketch the design,
  and write testable WHEN/THEN scenarios. Use when someone proposes one concrete
  thing to build. Triggers: "I want to add X", "spec this feature", "turn this
  idea into requirements", "flesh out this request", "what would it take to
  build X", "write a spec for X".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
---

# Project Feature Request

Run one request through the idea funnel: fuzzy in, precise out. The deliverable
is a **signed-off spec delta** (plus a design sketch when warranted) and a
handoff — never implementation, never sequencing. This skill operationalizes
project-shape's "Translate Ideas into Requirements" funnel for a single
request.

Two rules govern everything:

1. **Specification before work.** Nothing leaves this skill without testable
   WHEN/THEN scenarios and explicit out-of-scope boundaries, or an explicit
   kill/park decision.
2. **Proportionality.** Depth scales with blast radius, not ceremony. Gates are
   always *answered*; they are only *deep* when the answer is contested.

## Sizing the Request

Classify early; it sets the depth of every gate:

| Size | Signals | Gate depth |
|------|---------|-----------|
| **Small** | One component, no new boundaries, no doctrine tension | Answer all gates inline in one pass; minutes, not sessions |
| **Medium** | Several components, new external surface, or observable-behavior changes | Each gate answered explicitly in the funnel summary; design sketch required |
| **Large** | New subsystem, doctrine implications, or cross-boundary contracts | Subagent per gate, independent review of the spec delta before sign-off |

## The Funnel

Read [`references/funnel-gates.md`](references/funnel-gates.md) for per-gate
inputs, exit criteria, and kill conditions. The sequence:

**Gate 0 — Baseline.** Check what shape exists (run
`../project-shape/scripts/shape-scan.sh` or read `about/` and `openspec/`
directly). Use whatever pillars exist as the normative baseline. If shape is
absent, proceed in lite mode with [Inferred] labels — do **not** force a shape
bootstrap on someone who asked for a feature; instead note the gap and suggest
`../project-shape/SKILL.md` separately.

**Gate 1 — Concretize the motif.** Restate the request as: problem, who it
serves, observable success criteria, and the underlying motif (the recurring
need this is an instance of). Challenge vagueness using the patterns in
`../project-shape/references/consultative-bootstrapping.md` — accept a vague
answer only to push deeper, never to ship.

**Gate 2 — Doctrine.** Does it align with `about/heart-and-soul/`? Outcomes:
aligned (cite the principle), conflicts (reject, or escalate a doctrine change
— never both silently), or no doctrine exists (record the alignment judgment as
[Inferred]).

**Gate 3 — Topology.** Where does it live? Name the components touched, the
boundaries crossed, and the integration points, against `about/lay-and-land/`
when it exists. A request that lives "everywhere" is not yet concrete — return
to Gate 1.

**Gate 4 — Design sketch.** For medium+ requests, draft the design delta:
state machines, wire contracts, trade-offs considered, in
`about/legends-and-lore/` style (see
`../project-shape/references/pillar-legends-and-lore.md`). For small requests,
record one sentence on why no sketch is needed.

**Gate 5 — Specification.** Write the spec delta: WHEN/THEN scenarios,
acceptance criteria, and an explicit **out of scope** list, following
`../../references/spec-format.md` and the project's existing
`openspec/` conventions (active changes override main specs — extend, don't
fork).

**Gate 6 — Engineering bar.** Pull the relevant standards from
`about/craft-and-care/` (testing discipline, observability, review
expectations) into the acceptance criteria so quality is specified, not
hoped for. If craft-and-care is absent, the assumed bar is `/th-engineering`'s
engineering-bar default biases — cite that explicitly rather than inventing
one.

## Sign-off and Handoff

Present the funnel summary: sizing, each gate's outcome with evidence, the
spec delta, and open questions. Then:

- **Approved** → hand the spec delta to `../project-direction/SKILL.md` for
  sequencing and decomposition; for a small single-task request, file it
  directly via `/beads-orchestration` (beads-writer) with the spec reference.
- **Doctrine conflict** → record the rejection and its reasoning where the
  project keeps decisions; do not soften it into a backlog item.
- **Parked** (sound idea, no technical path yet) → write an exploratory RFC
  stub in legends-and-lore and stop.
- **Not specifiable** → the request is still too vague; split it into smaller
  motifs and re-enter at Gate 1, or return it to the requester with the
  specific questions that block specification.

Sign-off is the user's, not yours. "Not quite right" means return to the
failing gate — don't patch the spec text.

## Boundaries

- One request per run. A list of features is N runs (or `/project-direction`
  if the real ask is prioritization).
- No implementation, no estimates, no sequencing — those belong to
  project-direction and execution tooling.
- Evidence labeling matches the sibling subskills: [Observed], [Inferred],
  [Unknown].
