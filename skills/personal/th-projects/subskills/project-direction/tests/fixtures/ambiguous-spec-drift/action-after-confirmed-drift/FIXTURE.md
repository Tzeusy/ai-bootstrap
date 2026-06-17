# Fixture: "what do we do about confirmed drift?" → project-direction (action/sequencing)

## Input

**Trigger phrase**: "We confirmed the authentication module has drifted from
the spec — what should we do about it?"

**Context**: A project-review audit has already been completed. The review
packet confirms: the `auth/session.py` module's token-expiry behaviour
diverges from `openspec/changes/core/specs/auth/spec.md` section 3.2.
The user is now asking for a corrective action plan.

**Session state**: Upstream `project-review` packet available and fresh
(reviewed at HEAD). Confirmed drift findings supplied.

## Expected Outcome

**Routing**: → `project-direction/SKILL.md` — action/sequencing mode
(spec-drift focus, with corrective changeset)

**Rationale**: Drift is already confirmed; the ask is for action, not audit.
`project-direction` SKILL.md under "Adapting to Focus":
> **Spec-drift check** ("does code match spec?"): Phase 2 emphasizes B + C + D;
> produce a corrective changeset (change-tier) **only for confirmed drift the
> user wants fixed**.

The user has explicitly said "we confirmed … what do we do?" — this
activates the corrective-changeset path, not a read-only inventory.

**Receiver Protocol**: Because a fresh project-review packet is present,
project-direction MUST consume it (Receiver Protocol):
- Adopt Phase 0 baseline from the packet (not re-derive).
- Confirmed findings feed Phase 2 directly.
- Phase 1 = doctrine *check*, not re-derivation.

## Key Assertions

1. Skill accepts the upstream project-review packet and does NOT re-run the
   full audit from scratch.
2. Phase 1 runs as verify-tier (doctrine consumed, not modified).
3. Phase 2 produces a corrective OpenSpec changeset with change-tier
   reconciliation (because a normative artifact is being modified).
4. Phase 3 generates beads from the approved changeset.
5. Skill does NOT route back to project-review (audit is complete).
6. Skill does NOT begin implementation — deliverable is the work plan +
   beads graph, not code.

## Boundary

This fixture distinguishes "we confirmed drift, now act" (this fixture) from
"we don't know yet if there's drift" (see `../read-only-audit/FIXTURE.md`).
Both start from an ambiguous user phrasing about spec drift; the presence of
a confirmed-findings packet is the routing signal.
