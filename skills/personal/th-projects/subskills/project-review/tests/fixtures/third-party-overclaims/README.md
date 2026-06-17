# Fixture: third-party-overclaims

A deliberately flawed third-party review for calibrating the Phase 3.5
Veracity Gate. Every claim in `input-review.md` is annotated in
`expected-gate-output.md` with its correct classification and the
invalidating or confirming evidence.

## Purpose

- Demonstrate the class of failures that Phase 3.5 is designed to catch
- Provide a calibration reference before applying the gate to an unfamiliar review
- Show the correct Veracity Ledger output format

## Failure classes in this fixture

| Failure class | Description | Example claim |
|---|---|---|
| Nonexistent path | Claim references a file that does not exist in the package | `scripts/validate-routing.sh` |
| Overclaimed routing conflict | Claims two subskills handle the same trigger, but one explicitly excludes it | review vs. direction overlap |
| Raw-render formatting claim | Asserts file exceeds line-length limit based on browser/renderer output, not blob bytes | 120-char line claim |
| Missing-signoff claim contradicted by file | Asserts signoff is absent, but the SKILL.md defines it explicitly | sign-off visibility |
| Inflated P0 — must demote | P0 severity assigned to a claim that is already addressed or overstated | routing overlap P0 |

## How to use

1. Read `input-review.md` (the flawed external review).
2. Apply Phase 3.5 using the procedure in `references/review-veracity-gate.md`.
3. Compare your gate output against `expected-gate-output.md`.
4. Verify your Veracity Ledger matches the expected ledger entries.

Expected result: all five failure-class claims are either rejected or demoted,
and none enters the final risk register or planning handoff.
