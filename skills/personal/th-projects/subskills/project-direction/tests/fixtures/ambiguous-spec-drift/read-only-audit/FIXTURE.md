# Fixture: "does code match spec?" → project-review (read-only audit)

## Input

**Trigger phrase**: "Does the code actually match the spec?"

**Context**: A developer has noticed the authentication module behaves
differently than documented. They want to know whether the drift is real before
deciding what to do about it. No corrective action has been requested yet.

**Session state**: Cold start — no upstream project-review packet, no
feature-request spec delta.

## Expected Outcome

**Routing**: → `project-review/SKILL.md` (read-only audit)

**Rationale**: The ask is to *confirm* findings, not to *act* on them.
`project-direction` SKILL.md explicitly says under "Do not use when":
> Score repo health / confirm findings → `../project-review/SKILL.md`
> (hands its packet here)

The word "actually" signals doubt about whether drift exists — this is an
audit question, not an action question. Routing to `project-review` is
correct; it will produce a packet and hand off to `project-direction` only
when confirmed findings warrant it.

## Key Assertions

1. Skill does NOT begin Phase 1/2/3 of project-direction immediately.
2. Skill does NOT assume drift is confirmed before evidence is gathered.
3. Skill routes to `project-review` and explains that the audit packet will
   return here if action is needed.
4. No spec changeset is created in this pass.
5. No beads are generated.

## Boundary

This fixture distinguishes "does X match Y?" (audit) from "we confirmed drift,
now what?" (action). See `../action-after-confirmed-drift/FIXTURE.md` for the
latter case.
