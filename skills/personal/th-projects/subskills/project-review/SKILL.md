---
name: project-review
description: Use when auditing a repository's overall health, tech debt, maintainability, or architecture quality; processing a third-party repo-wide audit; or exhaustively reconciling OpenSpec specs against implementation. Triggers include "review this project", "audit the codebase", "assess project health", "does code match the spec", and "reconcile spec vs implementation" — not single-PR review or backlog prioritization.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - Claude Sonnet 4.6
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
---

# Project Review

Audit and classify with evidence. Review never schedules work or creates Beads;
confirmed findings hand off to project-direction. Single-diff review belongs to
`/th-engineering`.

## Invariants

- Establish the five-pillar normative baseline before judging code. Source
  order: heart-and-soul + legends-and-lore, OpenSpec, lay-and-land, then
  README/docs/issues, then code/history inference.
- A weak or absent shape lowers confidence and is itself a planning risk; it
  does not justify treating README claims as proven truth.
- Cite every major claim and label it `[Observed]`, `[Inferred]`, or
  `[Unknown]`. Every criticism includes a concrete remedy.
- Calibrate scope, maturity, and project type. Do not score generated code or
  inflate a personal project with irrelevant enterprise criteria.
- Before delivery, independently challenge every Critical/High/P0/P1 finding
  and leading recommendation. Only confirmed findings enter the risk register,
  roadmap, or direction packet.
- The durable output is a review report plus
  `docs/reviews/YYYY-MM-DD-{scope}-packet.md`, whose first line records the
  reviewed commit SHA. The packet carries the baseline, confirmed findings,
  required normative updates, sequencing constraints, deprioritized items, and
  evidence index.

## Common start

Run [`../project-shape/scripts/shape-scan.sh`](../project-shape/scripts/shape-scan.sh)
and [`scripts/project-scan.sh`](scripts/project-scan.sh). Load
[`../project-shape/references/maturity-rubric.md`](../project-shape/references/maturity-rubric.md)
only when interpreting scan ratings, and
[`references/project-type-adaptations.md`](references/project-type-adaptations.md)
only when calibrating the selected scope.

## Select a mode

| Mode | Selection | Load |
|---|---|---|
| Full review | Repo-wide health and architecture audit | [`references/investigation-guides.md`](references/investigation-guides.md), [`references/scoring-rubric.md`](references/scoring-rubric.md), and [`references/subagent-template.md`](references/subagent-template.md); synthesize with [`references/report-template.md`](references/report-template.md). |
| Focused review | Named categories only | The relevant guide/rubric sections and report template; retain baseline, scoped scorecard, risks, and handoff packet. |
| Quick health check | User explicitly accepts a provisional scan | Baseline + automated scan + a bounded high-risk sweep. Mark low confidence and do not present it as a full review. |
| Third-party review | Validate an external audit | [`references/third-party-review.md`](references/third-party-review.md); fact-check and preserve only confirmed findings. |
| Spec reconciliation | Exhaustive bidirectional spec-to-code and code-to-spec audit | [`references/spec-reconciliation.md`](references/spec-reconciliation.md) and the shared [`../../references/spec-format.md`](../../references/spec-format.md). Sample nothing. Remediation requires explicit authorization. |

Every mode uses
[`references/review-veracity-gate.md`](references/review-veracity-gate.md)
before delivery. Formatting or invocation claims require local-checkout or
GitHub-blob evidence; otherwise classify them `[Unverifiable]`.

Project craft-and-care sets the bar. Where it is absent or silent, load only
the implicated `/th-engineering` or `/th-design` subskill. Investigation guides
are evidence checklists, not a competing quality doctrine.

Write the report with [`references/report-template.md`](references/report-template.md),
then hand the packet to [`../project-direction/SKILL.md`](../project-direction/SKILL.md).
Planning, prioritization, and Beads lifecycle remain outside this skill.
