# Fixture: "break this approved spec into work" → beads planning (decomposition proceeds)

## Input

**Trigger phrase**: "The spec for the new notification system has been
approved. Break it into sequenced chunks so we can start implementing."

**Context**: The `openspec/changes/notifications/specs/notify/spec.md`
changeset was reviewed, reconciled, and signed off by the user in a prior
`project-direction` run. The user is now asking for the work to be
decomposed into actionable beads.

**Session state**: Signed-off spec delta available (the approved changeset
lives in the repo). No further spec or doctrine work is requested.

## Expected Outcome

**Routing**: → Phase 3 (beads generation) via `project-direction/SKILL.md`,
then handoff to `beads-orchestration` (beads-writer)

**Rationale**: `project-direction` SKILL.md under "Adapting to Focus":
> **Work decomposition** ("break this down"): assumes an approved spec.
> Phase 1 skipped unless the spec lacks a doctrine link.
> Phase 2 = one verify-tier pass confirming implementability.
> **Phase 3 is the primary artifact** (mechanical validations +
> verify-tier pass).

The spec is already approved; this is decomposition-only. Phase 3
generates the full beads dependency graph from the changeset.

## Key Assertions

1. Phase 1 is skipped (spec already links to doctrine; no re-check needed).
2. Phase 2 is a single verify-tier pass (one subagent confirming the spec
   is implementable), not a full investigation cycle.
3. Phase 3 is the primary deliverable: a full acyclic dependency graph of
   epics/tasks with explicit bead-to-spec traceability.
4. Beads include required reconciliation/report structural beads per
   beads-writer conventions.
5. Skill does NOT re-open spec discussions or request doctrine edits.
6. Skill does NOT execute/deliver the beads plan — hands off to
   `beads-orchestration` (beads-coordinator) explicitly.
7. No implementation begins in this run.

## Boundary

This fixture asserts that an *approved* spec skips spec-writing phases.
If the spec were NOT approved, the correct route would be full
project-direction (cold start or feature-request funnel first).
Decomposition proceeds only when sign-off is explicit — "approved" in the
trigger is load-bearing.
