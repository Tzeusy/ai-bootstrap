# Fixture: "does code match spec?" → spec-concretization (audit mode)

## Input

**Trigger phrase**: "Does the code actually match the spec?"

**Context**: A developer has noticed the authentication module behaves
differently than documented. They want to know whether the drift is real before
deciding what to do about it. No corrective action has been requested yet.

**Session state**: Cold start — no upstream review or concretization packet,
no feature-request spec delta.

## Expected Outcome

**Routing**: → `spec-concretization/SKILL.md` (audit mode, read-only)

**Rationale**: The ask is to *confirm* drift, not to *act* on it.
`project-direction` SKILL.md under "Do not use when":
> Exhaustive spec↔code reconciliation, or "does code match spec?" before any
> drift is confirmed → `../spec-concretization/SKILL.md`.

The word "actually" signals doubt about whether drift exists — this is an
audit question, not an action question. Spec-concretization's audit mode
classifies every requirement and behavior and stops at the report; confirmed
drift the user then wants fixed returns to `project-direction`'s spec-drift
focus (or a full concretization run).

## Key Assertions

1. Skill does NOT begin Phase 1/2/3 of project-direction immediately.
2. Skill does NOT assume drift is confirmed before evidence is gathered.
3. Skill routes to `spec-concretization` audit mode and explains that
   confirmed drift returns here if action is needed.
4. No spec changeset is created in this pass.
5. No beads are generated.

## Boundary

This fixture distinguishes "does X match Y?" (audit) from "we confirmed drift,
now what?" (action). See `../action-after-confirmed-drift/FIXTURE.md` for the
latter case.
