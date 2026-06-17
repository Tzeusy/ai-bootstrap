# Fixture: Gate 2 Doctrine Conflict → Reject, Do Not Soften

## Input

**Trigger phrase**: "I want to add user analytics tracking — capture every
click and scroll so we can build a richer feature roadmap."

**Context**: This is a privacy-first developer tool. `about/heart-and-soul/`
states explicitly:
> "We do not collect behavioral data from users' local environments.
> Telemetry is opt-in only and covers installation health, not usage patterns."

**Session state**: Cold start. One request. `about/heart-and-soul/` is
present and normative.

## Expected Outcome

**Gate reached**: Gate 2 — Doctrine
**Decision**: Conflict → **Reject**

**Rationale**: The request directly contradicts a stated non-negotiable in
`about/heart-and-soul/`. `project-feature-request` SKILL.md:
> **Doctrine conflict** → record the rejection and its reasoning where the
> project keeps decisions; **do not soften into a backlog item**.

The funnel ends at Gate 2 with a recorded rejection. The requester is
told which principle was violated and the decision is documented.

## Key Assertions

1. **One request per run**: only this request is processed.
2. Gate 0 runs (baseline: doctrine present and constraining).
3. Gate 1 runs (motif concretized: "behavioral analytics for roadmapping").
4. Gate 2 kills the request with an explicit doctrine citation.
5. Gates 3–6 do NOT run.
6. The rejection is recorded (where the project keeps decisions).
7. The rejection is NOT softened into "maybe later" or a parking note.
8. **No implementation or sequencing**: no spec delta, no beads, no design
   sketch.
9. **No leakage**: skill does not suggest workarounds or partial
   implementations that might satisfy the spirit of the request.

## Boundary

Doctrine conflict ≠ parked. A parked request has a sound idea but no
technical path — it could ship once the path exists. A doctrine conflict is
a categorical rejection because the idea violates the project's core
commitments. See `../parked/FIXTURE.md` for the distinction.
