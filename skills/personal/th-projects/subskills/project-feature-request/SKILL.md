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
  last_reviewed: "2026-06-13"
---

# Project Feature Request

One request through the idea funnel: fuzzy in, precise out. Deliverable = a
**signed-off spec delta** (plus design sketch when warranted) and a handoff —
never implementation, never sequencing. Operationalizes project-shape's
"Translate Ideas into Requirements" funnel for one request.

Two governing rules:

1. **Specification before work.** Nothing leaves without testable WHEN/THEN
   scenarios and explicit out-of-scope boundaries — or an explicit kill/park
   decision.
2. **Proportionality.** Depth scales with blast radius, not ceremony. Gates are
   always *answered*; only *deep* when the answer is contested.

## Sizing the Request

Classify early; it sets every gate's depth:

| Size | Signals | Gate depth |
|------|---------|-----------|
| **Small** | One component, no new boundaries, no doctrine tension | All gates inline in one pass; minutes, not sessions |
| **Medium** | Several components, new external surface, or observable-behavior changes | Each gate answered explicitly in funnel summary; design sketch required |
| **Large** | New subsystem, doctrine implications, or cross-boundary contracts | Subagent per gate; independent review of spec delta before sign-off |

## Interview Discipline

Funnel = decision tree; run it like a grilling, not a form. Walk each branch,
resolving dependencies one at a time — an answer at one gate constrains the
next, so never batch-ask across gates.

- **One question at a time.** No questionnaire dumps. Ask, absorb, then ask
  what the answer raises.
- **Carry a recommended answer.** Pose the question *and* your best default
  with reasoning — requester reacts to a concrete proposal, not a blank.
- **Explore before asking.** Answerable from codebase, `about/`, or
  `openspec/`? Go read it. Ask the human only what only the human knows
  (intent, priorities, tolerances).
- **Grill until shared understanding.** Stay on a branch until the answer is
  falsifiable, not just plausible. "Roughly"/"probably" → push, don't move on.

## The Funnel

Load [`references/funnel-gates.md`](references/funnel-gates.md) for per-gate
inputs, exit criteria, and kill conditions, plus the funnel summary template —
read it before running the gates. The sequence:

**Gate 0 — Baseline.** Check what shape exists (run
`../project-shape/scripts/shape-scan.sh` or read `about/` + `openspec/`). Use
whatever pillars exist as normative baseline. Shape absent → proceed in lite
mode with [Inferred] labels. Do **not** force a shape bootstrap on someone who
asked for a feature; note the gap, suggest `../project-shape/SKILL.md`
separately.

**Gate 1 — Concretize the motif.** Restate as: problem, who it serves,
observable success criteria, and the underlying motif (the recurring need this
instances). Challenge vagueness via
`../project-shape/references/consultative-bootstrapping.md` — accept a vague
answer only to push deeper, never to ship.

**Gate 2 — Doctrine.** Aligns with `about/heart-and-soul/`? Outcomes: aligned
(cite the principle); conflict (reject, or escalate a doctrine change — never
both silently); or no doctrine exists (record alignment judgment as [Inferred]).

**Gate 3 — Topology.** Where does it live? Name components touched, boundaries
crossed, integration points, against `about/lay-and-land/` when it exists. A
request that lives "everywhere" isn't concrete — return to Gate 1.

**Gate 4 — Design sketch.** Medium+ → draft the design delta: state machines,
wire contracts, trade-offs considered, in `about/legends-and-lore/` style (see
`../project-shape/references/pillar-legends-and-lore.md`). Small → one sentence
on why no sketch is needed.

**Gate 5 — Specification.** Write the spec delta: WHEN/THEN scenarios,
acceptance criteria, explicit **out of scope** list, per
`../../references/spec-format.md` and existing `openspec/` conventions (active
changes override main specs — extend, don't fork).

**Gate 6 — Engineering bar.** Pull relevant standards from
`about/craft-and-care/` (testing discipline, observability, review
expectations) into acceptance criteria so quality is specified, not hoped for.
Craft-and-care absent → assumed bar is `/th-engineering`'s engineering-bar
default biases; cite that explicitly rather than inventing one.

## Sign-off and Handoff

Present the funnel summary: sizing, each gate's outcome with evidence, the spec
delta, open questions. Then:

- **Approved** → hand the spec delta to `../project-direction/SKILL.md` for
  sequencing and decomposition; for a small single-task request, file directly
  via `/beads-orchestration` (beads-writer) with the spec reference.
- **Doctrine conflict** → record the rejection and its reasoning where the
  project keeps decisions; do not soften into a backlog item.
- **Parked** (sound idea, no technical path yet) → write an exploratory RFC
  stub in legends-and-lore and stop.
- **Not specifiable** (still too vague) → split into smaller motifs and
  re-enter at Gate 1, or return to the requester with the specific questions
  blocking specification.

Sign-off is the user's, not yours. "Not quite right" → return to the failing
gate; don't patch the spec text.

## Boundaries

- One request per run. A list of features is N runs (or `/project-direction`
  if the real ask is prioritization).
- No implementation, no estimates, no sequencing — those belong to
  project-direction and execution tooling.
- Evidence labeling matches sibling subskills: [Observed], [Inferred],
  [Unknown].
