## Context

Project-governance workflows can discover real owner gates, but their review
context often spans many artifacts and cannot always be resolved synchronously.
The transport must remain reusable across repositories while deferring to each
target project's doctrine, specifications, topology, engineering standards, and
tracker. It must also distinguish a recorded signoff from permission to mutate
canonical or external state.

## Goals / Non-Goals

**Goals:**

- Preserve a comprehensive, resumable local review surface while presenting one
  concise decision at a time.
- Make independent adversarial review of both framing and recommendation an
  enforceable precondition.
- Retain exact evidence freshness, owner-answer provenance, and authorization
  boundaries.
- Route downstream effects through the workflow that already owns the artifact
  or operation.

**Non-Goals:**

- Defining doctrine, product scope, specifications, priorities, or Bead graphs.
- Escalating ordinary engineering judgment to the owner.
- Mutating specs, doctrine, trackers, runtimes, credentials, deployments, or
  external systems from the questionnaire workflow.

## Decisions

1. **Cross-cutting internal subskill, not a lifecycle stage.** The parent
   `th-projects` router exposes questionnaire intent while existing subskills
   retain governance authority. A separate top-level superskill would duplicate
   routing and obscure the source of truth.
2. **Markdown packet with stable IDs.** A local ignored document is portable,
   inspectable, and resumable without adding a database or service. Canonical
   project artifacts remain authoritative.
3. **Two independent semantic verdicts.** A fresh subagent separately judges
   whether the question is a genuine, correctly bounded owner gate and whether
   the options/recommendation best satisfy the project shape and engineering
   bar. Structural validation cannot substitute for semantic review.
4. **Fail-closed deterministic validator.** Review-ready packets require closed
   states, exact reviewer identity/verdict grammar, complete item bodies,
   distinct options, recommendation integrity, and answer provenance for
   decided states. Focused tests encode known bypasses.
5. **Record and route, never directly apply.** A user may ask the questionnaire
   to transport signoffs, but the destination workflow must independently
   enforce its own mutation, review, and external-action gates.

## Risks / Trade-offs

- **Packet staleness after asynchronous delay** → refresh drift-prone evidence
  before each walkthrough session/item and before routing.
- **False owner workload** → apply the local decision-autonomy policy before
  admission and adversarially review the problem scope.
- **Validator mistaken for semantic proof** → require named subagent verdicts
  and describe mechanical validation as structural only.
- **Edited answers bypass review** → treat a material option/boundary edit as a
  new artifact requiring post-answer review.
- **Sensitive data leaks into the dossier** → record safe provenance only and
  prohibit secrets or owner-private values.
