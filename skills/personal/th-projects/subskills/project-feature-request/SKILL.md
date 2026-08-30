---
name: project-feature-request
description: >
  Use when one concrete feature or project request is still fuzzy and needs a
  signed-off behavior specification before planning or implementation, or when
  implementation reveals its governing spec is wrong, ambiguous, or incomplete.
  Triggers: "I want to add X", "spec this feature", "turn this idea into
  requirements", "what would it take to build X", "write a spec for X", "the
  spec is wrong", "the spec doesn't match what I'm building".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
---

# Project Feature Request

Move one request from fuzzy intent to a signed-off spec delta, design sketch
when warranted, and planning handoff. Never implement or sequence it here.

## Invariants

- Specification before work: every surviving request has observable WHEN/THEN
  scenarios and explicit non-goals, or ends in an explicit reject/park verdict.
- VISION remains binding. Cite the doctrine baseline and revalidate affected
  mandates when it changes.
- Depth follows blast radius: small (one component, no new boundary), medium
  (several components or new external behavior), large (new subsystem,
  doctrine implication, or cross-boundary contract).
- Ask one dependent question at a time, with a reasoned default. Inspect the
  repo first; reserve human questions for intent, priorities, and tolerances.
- Major claims use `[Observed]`, `[Inferred]`, or `[Unknown]`. A separate
  semantic review is required for large or contested normative changes.
- Observable behavior and doctrine changes require owner signoff. A pure
  ambiguity clarification with no behavior change may proceed when recorded in
  the driving task.

## Select a mode

| Mode | When | Load and do |
|---|---|---|
| Standard funnel | One new proposal | Read [`references/funnel-gates.md`](references/funnel-gates.md). Run baseline, motif, doctrine, topology, design, specification, and engineering-bar gates in order. A missing shape permits an explicitly `[Inferred]` lite mode; it does not force bootstrap. |
| Amendment | Implementation finds the active spec wrong, ambiguous, or incomplete | Start with VISION sanity. Behavior-only clarification resumes at specification; topology, UX, boundary, or contract change resumes at topology/design; doctrine impact runs the full funnel. New scope is not an amendment. Use the same funnel reference for exit criteria. |

For user-facing behavior, load `/th-design` only for the implicated design
concern and carry its conclusions into the behavior contract. For an absent or
silent craft-and-care bar, load one relevant `/th-engineering` subskill. The
shared OpenSpec contract is
[`../../references/spec-format.md`](../../references/spec-format.md).

## Verdict and handoff

- **Approved** -> record signoff and baseline commit; hand the delta to
  `../project-direction/SKILL.md` for sequencing. A small single-task outcome
  may go directly to `/beads-orchestration` with its spec reference.
- **Doctrine conflict** -> reject or explicitly escalate a doctrine amendment;
  never do both silently.
- **Parked** -> preserve an exploratory design record and stop.
- **Not specifiable** -> split into smaller motifs or return the exact blocking
  questions.

Reject and park records follow
[`references/decision-record-template.md`](references/decision-record-template.md),
including the same-change ideas-ledger update. Project-native ADR/RFC
conventions take precedence.

One request per run. Lists route to project-direction when prioritization is
the real task. Do not estimate, implement, sequence, or silently absorb adjacent
scope.
