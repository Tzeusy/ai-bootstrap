# Fixture: "write us some specs" with no doctrine → project-shape

## Input

**Trigger phrase**: "Let's get specs written for this project so we can start
building."

**Context**: The repository has a `README.md` describing the tool's commands,
some code, and nothing else. No `about/heart-and-soul/`, no `.syzygy/`, no RFCs,
no vision or scope statement anywhere. The user's intent is genuine — they want
to specify — but nothing states what the project is for.

**Session state**: Cold start.

## Expected Outcome

**Routing**: → `project-shape/SKILL.md` (bootstrap), returning to
`project-direction` once doctrine is adopted

**Rationale**: The launch gate is administered *against* an adopted goal
statement; with none, most of section A has no artifact to cite and the whole
series returns `Unknown`. A gate run here burns a reviewer and produces a
record that says only "there is no doctrine" — which the shape scanner reports
for far less. project-direction's edge-case table routes "no specs *and* no
doctrine" to bootstrap explicitly.

## Key Assertions

1. Skill does NOT administer the launch gate against absent doctrine.
2. Skill does NOT synthesize a first changeset from the README.
3. Skill names what is missing (doctrine/goal statement) rather than inferring
   a vision from the code and proceeding on it.
4. Skill states the return path: bootstrap doctrine → launch gate → Phase 2.
5. No beads are generated.

## Boundary

This fixture guards the gate's precondition. See `../ready-to-specify/FIXTURE.md`
for the case where doctrine exists and the gate is the correct instrument.
