# Fixture: unbuilt requirements the backlog already holds → no duplicates

## Input

**Trigger phrase**: "Plan all the work to finish the spec."

**Context**: Three unmet `v1-mandatory` requirements. The ledger shows
`REQ-api-export-002` cited by open bead `x-12`; `REQ-api-export-004` cited
by closed bead `x-7` (closed two weeks ago) but still unmet; `REQ-api-export-005`
has no bead; open, unassigned bead `x-15` ("Implement the export
endpoint per core-api-export") owns that handler, and its stated outcome
already implies 005 though its acceptance omits it. `x-7` closed without its
acceptance being met (no test, no merged change). Open bead `x-20` cites `REQ-api-export-009`, which no spec defines.

## Expected Outcome

**Decision**: `002` → attach to `x-12`; `004` → reopen `x-7`
(closed without meeting it); `005` → extend `x-15`'s acceptance with the
guarded `--if-assignee '' --if-status open` update; `x-20` → orphan (close if
the requirement was removed, else route the idea to feature-request).
Zero new beads.

**Rationale**: SKILL.md Core Rule 8; spec-ahead.md §§ 3-4.

## Key Assertions

1. Coverage matrix gives each of the three IDs exactly one owning bead.
2. No new bead is created.
3. Reopen and close carry file-level evidence at the audited SHA.
4. Had `x-7` met the requirement at landing and later regressed, the row would be `regressed` (new defect bead, `caused-by` edge), not a reopen.
5. A re-run on the same head performs zero actions and adds no duplicate notes.
