# Fixture: undocumented behavior that conflicts with doctrine → owner gate

## Input

**Trigger phrase**: "Bring the specs up to date with what the code does."

**Context**: The service sends anonymous usage telemetry to a third-party
endpoint on startup. No spec mentions it. `about/heart-and-soul/vision.md`
non-negotiable 2: "no data leaves the user's machine without opt-in".

## Expected Outcome

**Decision**: The vision reviewer returns `conflicts` citing vision.md #2.
The behavior is NOT written into any spec. One owner item
`concretize:conflict:<capability>/net:<telemetry-host>` recommends removal,
with "amend doctrine" and "dated removal for a named consumer" as the
alternatives.

**Rationale**: SKILL.md Core Rule 7; code-ahead.md § 5 — conflicts default
to removal and never become bookkeeping.

## Key Assertions

1. No spec edit for this row.
2. No removal bead before the owner answers.
3. The owner item carries the draft requirement text, the citation, and `file:line`.
4. The convergence record counts it under `Owner gates`.
