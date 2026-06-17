# Fixture: Gate 4 Park — Sound Idea, No Technical Path Yet

## Input

**Trigger phrase**: "I want the CLI to automatically detect when a spec has
become stale based on semantic similarity to recent commits."

**Context**: A developer wants semantic drift detection — the tool would
compare spec prose to commit messages/diffs using ML similarity scoring and
flag divergence automatically. The idea aligns with the project's goal of
keeping specs current. However, the project has no ML inference
infrastructure; the only dependency is a local Dolt database. Adding an LLM
inference layer would require resolving model hosting, latency budgets,
offline guarantees, and privacy constraints — none of which have been
decided.

**Session state**: Cold start. One request. Shape pillars present;
`about/lay-and-land/` shows a thin local-only CLI stack.

## Expected Outcome

**Gate reached**: Gate 4 — Design Sketch
**Decision**: Park → write exploratory RFC stub, stop

**Rationale**: The idea is doctrine-aligned (keeping specs current is the
project's stated goal) and placeable in the topology. But Gate 4 finds no
technically credible path today: ML inference infrastructure does not exist
and decisions blocking it are unresolved. `project-feature-request` SKILL.md:
> **Parked** (sound idea, no technical path yet) → write an exploratory RFC
> stub in legends-and-lore and stop.

## Key Assertions

1. **One request per run**: only this request is processed.
2. Gate 0 runs (baseline: shape present).
3. Gate 1 runs (motif concretized: "semantic drift detection against commits").
4. Gate 2 passes (doctrine: aligned with spec-currency goal, citation provided).
5. Gate 3 runs (topology: would live in a new `drift-detector` component;
   crossing no existing boundaries but requiring new ML dependency).
6. Gate 4 parks: no technically credible path — ML infra decisions unresolved.
7. An exploratory RFC stub is written in `about/legends-and-lore/` documenting
   what would need to become true (model hosting decision, latency budget,
   offline guarantee, privacy posture).
8. Gates 5–6 do NOT run (no spec written, no engineering bar set).
9. **No implementation or sequencing**: no code, no beads, no sequencing plan.
10. **No leakage**: skill does not outline a partial implementation or suggest
    interim workarounds that would implicitly advance the request.

## Boundary

Parked ≠ doctrine conflict. A parked request could ship in the future once
the blocking technical questions are resolved. A doctrine conflict cannot
ship without changing the project's commitments. See
`../doctrine-conflict/FIXTURE.md` for the distinction.

Parked ≠ too-vague-to-specify. This request is concrete enough to specify
(clear motif, clear topology); it fails on technical feasibility, not
clarity. See `../too-vague-to-specify/FIXTURE.md` for the latter.
