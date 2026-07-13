# Fixture: Large Cross-Boundary Request → project-direction for Sequencing

## Input

**Trigger phrase**: "We need a real-time collaboration layer so multiple
users can edit the same spec document simultaneously — with conflict
resolution."

**Context**: A product team wants collaborative editing for `openspec/`
documents. This requires: a new WebSocket service, an operational
transformation (OT) or CRDT conflict-resolution algorithm, a presence
system (cursors, user avatars), authentication integration changes, and
client-side state management refactors. Touches 4+ existing components,
introduces two new external surfaces (WebSocket endpoint, presence API),
and carries doctrine implications (the project currently models specs as
local-first, single-author files).

**Session state**: Cold start. One request. `about/` pillars present.

## Expected Outcome

**Size**: Large — new subsystem, doctrine implications, cross-boundary
contracts.

**One funnel owner.** Dedicated specialists may own the independent protocol
design and user-experience review; a fresh reviewer checks the converged spec
delta before sign-off.

**Decision**: Approved (pending Gate 2 escalation resolution) → hand spec
delta to `../project-direction/SKILL.md` for sequencing and decomposition.

**Rationale**: `project-feature-request` SKILL.md:
> **Approved** → hand the spec delta to `../project-direction/SKILL.md`
> for sequencing and decomposition.

The sizing table keeps one owner across the sequential gates, adding dedicated
specialists only for independently reviewable artifacts or contested gates.
`project-direction` owns the work graph and sequencing — feature-request ends
at the signed-off spec delta.

**Gate 2 escalation**: the request's "real-time, multi-user" model
conflicts with the current "local-first, single-author" doctrine in
`about/heart-and-soul/`. This triggers a doctrine-change escalation (not
a silent rejection), which must be resolved before gates 3–6 proceed.

## Gate Summary (Abbreviated)

- **G0**: shape present; `about/heart-and-soul/` and `about/lay-and-land/`
  both constrain this request.
- **G1 Motif**: "Multiple authors blocked from concurrent edits → lost
  work, merge pain. Success: two users edit the same spec simultaneously;
  both changes persist coherently. Motif: *collaborative document editing*."
- **G2 Doctrine**: ⚠ **Escalation required** — request challenges
  "local-first, single-author" model. Funnel pauses; escalates to user:
  "Should we update the doctrine to allow multi-user collab, or reject?"
  — must be resolved before proceeding.
- **G3 Topology**: new `collab-service` (WebSocket); presence API; OT/CRDT
  library; auth integration; `openspec` editor client refactor.
- **G4 Design sketch**: OT vs CRDT trade-off; wire contract for
  `collab-service`; cursor/presence protocol; conflict scenarios. `/th-design`
  adds discoverability, accessibility, loading, latency, and error-state
  expectations for the human-facing collaboration surface.
- **G5 Spec**: WHEN/THEN for concurrent edits, network partition,
  rejoin-after-disconnect, and single-user baseline.
- **G6 Bar**: integration tests for conflict scenarios, observability for
  presence events, rollback plan for WebSocket infra.

## Key Assertions

1. **One request per run**: only this request is processed; no other
   features are entertained.
2. Gate 2 doctrine escalation is raised explicitly and funnel pauses for
   user resolution (not silently bypassed).
3. Independent subagent reviews the spec delta before sign-off.
4. After approved sign-off, skill hands off to `project-direction` with
   the spec delta — it does NOT begin sequencing or generating beads.
5. **No implementation leakage**: no code, no task ordering, no sprint
   plans, no file paths for where to write code.
6. **No sequencing leakage**: no dependency graph, no "do X before Y"
   ordering — that is `project-direction`'s job.
7. The funnel summary documents sizing rationale and each gate outcome.
8. The spec delta is the terminal deliverable of this run.
9. Funnel summary records the doctrine/spec baseline commit and human sign-off
   identity/date before handoff.

## Boundary

Large ≠ rejected. Size determines gate depth, not fate. A large request
that passes all gates (including doctrine escalation) produces a signed-off
spec delta and hands off to `project-direction`.

The doctrine escalation in Gate 2 here distinguishes this fixture from
`../doctrine-conflict/FIXTURE.md`: an *escalation* pauses the funnel and
invites the user to change doctrine; a *conflict* (when the user declines
to escalate) terminates the funnel with a rejection.
