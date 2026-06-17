# Fixture: Gate 5 Not-Specifiable → Return to Gate 1 or Flag Blocking Questions

## Input

**Trigger phrase**: "We should make the onboarding experience better."

**Context**: A stakeholder feels that new users struggle to get started.
They cannot describe a concrete failure scenario when asked. After Gate 1
grilling:
- **Problem**: "users seem confused" (no concrete instance produced)
- **Who**: "new users" (persona not refined past this)
- **Success**: "they should feel more confident" (feeling, not observable
  behaviour)
- **Motif**: cannot be named — the requester agrees the observation is real
  but cannot give a falsifiable outcome

**Session state**: Cold start. One request. No shape pillars.

## Expected Outcome

**Gate reached**: Gate 5 — Specification (or Gate 1, looped back)
**Decision**: Not specifiable → split into smaller motifs or return to
requester with specific blocking questions

**Rationale**: Gate 1 exit criterion: "problem + success criteria are
falsifiable; the motif is named." This request cannot pass Gate 1.
`project-feature-request` SKILL.md sign-off section:
> **Not specifiable** (still too vague) → split into smaller motifs and
> re-enter at Gate 1, or return to the requester with the specific
> questions blocking specification.

Even if advanced to Gate 5, the request resists WHEN/THEN phrasing —
"feel confident" cannot be expressed as observable behaviour — triggering
the Gate 5 kill condition.

## Key Assertions

1. **One request per run**: only this request is processed.
2. Gate 0 runs (baseline noted; shape absent in this scenario, lite mode).
3. Gate 1 grilling is applied: one-question-at-a-time, with recommended
   answers, concrete instance demanded.
4. Gate 1 does NOT pass: no falsifiable success criterion obtained after
   grilling.
5. Funnel halts; skill returns specific blocking questions to requester:
   - "Give me the last time a real user got stuck — what did they try to do,
     and where did they stop?"
   - "What observable behaviour would tell us onboarding succeeded?"
6. Skill may offer to split into candidate motifs (e.g., "empty-state
   guidance", "first-run wizard", "documentation discoverability") and
   invite the requester to pick one to re-enter at Gate 1.
7. **No implementation or sequencing**: no spec delta, no design sketch, no
   beads.
8. **No leakage**: skill does not begin writing scenarios or acceptance
   criteria from the vague "better onboarding" description.
9. The funnel summary notes the gate at which the request stalled and why.

## Boundary

Too-vague-to-specify ≠ parked. A parked request is concrete but technically
blocked. A not-specifiable request is not yet concrete enough to evaluate
feasibility. See `../parked/FIXTURE.md`.

Too-vague-to-specify ≠ doctrine conflict. The idea may or may not conflict
with doctrine — we cannot reach Gate 2 with a meaningful verdict when Gate 1
cannot produce a falsifiable statement. See `../doctrine-conflict/FIXTURE.md`.
