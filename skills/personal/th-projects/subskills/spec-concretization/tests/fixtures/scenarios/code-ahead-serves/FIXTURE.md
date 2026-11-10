# Fixture: undocumented behavior that serves a mandate → bookkeeping

## Input

**Trigger phrase**: "Reconcile the specs with the code."

**Context**: The CLI implements `export --format csv`, tested in
`tests/test_export.py`. No requirement mentions export formats.
`about/heart-and-soul/v1.md` ship list item 4: "users can take their data
out in a spreadsheet-readable form".

## Expected Outcome

**Decision**: Flow A drafts one requirement (export with CSV format), the
fresh-context vision reviewer returns `serves` citing v1.md item 4, and the
lead lands it as main-spec bookkeeping.

**Rationale**: code-ahead.md § 4 — only `serves` enters the spec unasked.

## Key Assertions

1. The ledger shows no live bead owning `cli:export--format`, so the row is not `Owned`.
2. The draft (behavior-only paragraph plus Effects list) is written before the gate and judged by a subagent that did not read the code.
3. `Source: [Observed] <path>:<line> — serves about/heart-and-soul/v1.md #4`.
4. `Scope: v1-mandatory` because the mandate is a v1 ship item.
5. `tests/test_export.py` already asserts the CSV behavior → the same bookkeeping change adds `Spec: REQ-<capability>-NNN` to it; no `unverified` bead.
6. No owner item is created for this row.
