# Fixture: "does the code match the spec?" → audit mode, no mutations

## Input

**Trigger phrase**: "Does the auth module actually match what openspec says?"

**Context**: `openspec/specs/core-auth/spec.md` has 6 requirements. The user
suspects drift but asked nothing about fixing it.

## Expected Outcome

**Decision**: Audit mode — ledger, inventory, classification, mapping table,
then the audit-mode report listing what a full run would do.

**Rationale**: The ask is a question, not an instruction to act (SKILL.md
Use / Do Not Use; inventory-and-classification.md § Audit-mode report).

## Key Assertions

1. `spec-trace-check.py` and `concretization-ledger.py` run before any judgment.
2. Every requirement and observable auth behavior gets exactly one class.
3. No spec file is edited, no bead is created, updated, or closed.
4. No questionnaire is published.
5. The report states proposed actions as proposals.
