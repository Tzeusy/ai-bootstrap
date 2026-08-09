# Fixture: "ready to write specs?" → project-direction (launch gate)

## Input

**Trigger phrase**: "We've been going round on the RFCs for weeks. Are we ready
to start writing specifications yet?"

**Context**: The project has adopted doctrine (`about/heart-and-soul/vision.md`,
`v1.md`) and a drafted-but-unaccepted design corpus under
`about/legends-and-lore/`. `openspec/` does not exist yet. Successive review
rounds keep producing findings and the owner cannot tell whether that is
progress or churn.

**Session state**: Cold start — no upstream project-review packet, no
feature-request spec delta.

## Expected Outcome

**Routing**: → `project-direction/SKILL.md`, launch-gate focus mode
(`references/launch-gate.md`)

**Rationale**: Doctrine exists, so this is not a project-shape bootstrap. The
ask is whether the layers *above* specs have settled enough to specify from —
Core Rule 9's precondition on Phase 2, not a maturity score of the pillars.
The router's "Baseline before judgment" rule routes "doctrine adopted but no
specs yet + can we start specifying" here.

## Key Assertions

1. Skill does NOT jump to Phase 2 changeset synthesis for a first spec.
2. Skill administers the question series to a **fresh-context reviewer
   subagent** — not from the orchestrator's own reading, and without briefing
   it on "how it's going".
3. Verdicts use the closed vocabulary `Met` / `Not met` / `Unknown(reason)`;
   no "partially met", no aggregate score standing in for per-question
   verdicts.
4. E3's empty reopen-list is recorded as `Unknown` unless the reviewer supplies
   the concept→shape trace table.
5. A `NOT READY` verdict produces a remediation brief routed by finding class,
   not an inline fix and not a beads graph.
6. No verdict is treated as an owner decision; deferrals are owner-only.
7. The absence of `openspec/` is not itself a finding — pre-gate absence is
   correct.

## Boundary

This fixture distinguishes "is the shape good enough to specify from?" (gate,
here) from "does the shape exist and how mature is it?" (`project-shape`
scanner). See `../missing-doctrine/FIXTURE.md` for the case where there is
nothing to administer the gate against.
