# Fixture: code disagrees with a clear spec → defect, spec untouched

## Input

**Trigger phrase**: "Do a full spec reconciliation before the release."

**Context**: `REQ-core-session-003` requires sessions to expire after 30
minutes idle; the code expires them after 24 hours. No doctrine, RFC,
decision record, or external consumer supports 24 hours. No bead mentions it.

## Expected Outcome

**Decision**: Row classified `divergent`; the divergence decision finds no
named evidence that the spec is wrong, so the spec wins and the row becomes
`spec-ahead` (defect). One new bead with
`Audit-key: spec:defect:core-session` and `Requirements: REQ-core-session-003`.

**Rationale**: SKILL.md Core Rule 5; spec-ahead.md § 1.

## Key Assertions

1. The spec is not edited to say 24 hours.
2. The ledger was checked first; `new` only because nothing matched.
3. Acceptance requires a test citing REQ-core-session-003.
4. No owner item: the spec is clear and nothing contradicts it.
