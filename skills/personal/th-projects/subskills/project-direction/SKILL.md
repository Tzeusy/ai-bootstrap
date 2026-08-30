---
name: project-direction
description: Use when deciding what a project should work on next, comparing competing priorities, deriving a milestone from VISION, brainstorming new feature candidates that fit the project's doctrine, judging whether a project's goals and requirements are settled enough to begin authoring specifications, sequencing an approved specification into an execution graph, or deciding what to do about already-confirmed spec drift. Triggers on "what should we work on next", "prioritize features", "is this roadmap aligned", "what's highest leverage", "what's the next milestone", "should we build this or Y", "are we ready to write specs", "break this approved spec down", "brainstorm features", "what could we build".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
---

# Project Direction

Decide what the project works on next. Produce a doctrine-aligned analysis or
approved-spec work graph; hand execution to `/beads-orchestration`.

## Invariants

- VISION is continuous: every candidate, delta, bead, discovery, and closeout
  cites its mandate. Revalidate affected mandates when the baseline changes.
- Specs are planning truth. No implementation graph precedes spec signoff; no
  work item lacks a spec link.
- Cite files, functions, and spec sections; label major claims `[Observed]`,
  `[Inferred]`, or `[Unknown]`. Push back on misaligned or infeasible work.
- Consume fresh review packets and signed-off feature deltas without
  re-deriving them. Fresh means the recorded baseline still matches, or the
  user explicitly accepts staleness.
- Semantic review depth follows risk and protects changed normative artifacts.
  Consumed artifacts need verification, not repeated ceremony. Mechanical
  trace, cycle, mandate-coverage, and spec-link checks remain mandatory.
- Resolve small in-scope gaps; make real unknowns explicit. Never hide work in
  TODOs or expand the active graph with adjacent scope.
- Direction may design and create a Beads planning graph through
  `/beads-orchestration` (beads-writer), but never claims, dispatches, executes,
  merges, or closes that graph.

## Select a mode

| Mode | Selection | Direct reference |
|---|---|---|
| Full direction / portfolio | Competing initiatives, roadmap alignment, or confirmed findings need a decision | Read [`references/direction-model.md`](references/direction-model.md), then [`references/alignment-review.md`](references/alignment-review.md) for synthesis and push-back. |
| Launch gate | Doctrine exists but the project has no specs and asks whether it is ready to specify | Administer [`references/launch-gate.md`](references/launch-gate.md). A non-empty reopen list returns to project-shape; no work graph is created. |
| Milestone synthesis | No proposals are supplied, or a milestone closed | Derive candidates from uncovered doctrine mandates with [`references/milestone-synthesis.md`](references/milestone-synthesis.md). Owner selection precedes specification. |
| Ideation | User asks for divergent, doctrine-grounded feature candidates | Use [`references/ideation.md`](references/ideation.md). Pursued candidates go to project-feature-request; this mode creates no specs or Beads graph. |
| Feature evaluation | Compare one proposal against competing priorities | Use [`references/alignment-review.md`](references/alignment-review.md). A lone fuzzy proposal routes to project-feature-request instead. |
| Spec drift | Confirmed drift needs analysis or authorized correction | Inventory read-only by default. Authorized correction uses [`references/openspec-changeset.md`](references/openspec-changeset.md), then owner signoff. Unconfirmed "does code match?" routes to project-review. |
| Work decomposition | An approved spec needs an execution graph | Load [`../../references/work-allocation.md`](../../references/work-allocation.md), verify implementability, then invoke beads-writer. |

For cold-start or portfolio modes, run
[`scripts/spec-scan.sh`](scripts/spec-scan.sh) and obtain the project-shape
baseline. A fresh `docs/reviews/*-packet.md` supplies confirmed findings; a
fresh feature-request delta supplies settled doctrine, topology, design, and
behavior. Only revisit affected claims when their recorded baseline moved.

## Outputs and supporting routes

- Direction handoff format: [`references/work-plan-template.md`](references/work-plan-template.md).
- OpenSpec changeset mechanics: [`references/openspec-changeset.md`](references/openspec-changeset.md).
- Evidence-role and independent-review prompts, only when the selected mode
  needs them: [`references/subagent-template.md`](references/subagent-template.md).
- Epic closeout contract: [`references/epic-report.md`](references/epic-report.md);
  scaffold with [`scripts/epic-report-scaffold.sh`](scripts/epic-report-scaffold.sh).
- Workflow visual: [`references/diagrams/project-direction-workflow.svg`](references/diagrams/project-direction-workflow.svg)
  ([source](references/diagrams/project-direction-workflow.excalidraw)).
- Artifact visual: [`references/diagrams/project-direction-artifacts.svg`](references/diagrams/project-direction-artifacts.svg)
  ([source](references/diagrams/project-direction-artifacts.excalidraw)).

The final report answers the real direction, the next outcome, what to stop
pretending is viable, and why the proposed graph is coherent. It also adds a
milestone-close callback: refresh VISION coverage and re-enter milestone
synthesis while approved mandates remain uncovered.

Hard stops: no doctrine and no specs -> project-shape bootstrap; conflicting
specs -> owner resolution; unavailable OpenSpec tooling -> analysis only; an
unconverged normative artifact -> report the evidence and stop.
