# Decision Record Templates

Default paths and minimal structure when the project has no established ADR or
RFC home. **Project conventions always take precedence** — check
`about/legends-and-lore/` for existing patterns before using these defaults.

## Rejected feature request

Path: `about/legends-and-lore/decisions/YYYY-MM-DD-rejected-{slug}.md`

Minimum sections:

- **Request summary** — one-paragraph restatement of the original request
- **Rejection reason** — cite the contradicted doctrine principle or scope
  boundary; do not soften into a backlog item
- **What would change the outcome** — conditions for reconsideration, or
  "doctrine is authoritative"

## Parked RFC stub

Path: `about/legends-and-lore/rfcs/YYYY-MM-DD-parked-{slug}.md`

Minimum sections:

- **Idea summary** — one-paragraph restatement of the sound idea
- **Why parked** — the missing technical path or unresolved dependency
- **What would need to become true** — specific conditions to unpark

## Ideas ledger

Path: `about/legends-and-lore/ideas-ledger.md` — the index that keeps parked
and rejected records discoverable. Individual records scatter as dated files;
the ledger is the one file `project-direction` (milestone synthesis) scans to
find unparkable ideas. **Every park or reject decision appends a ledger line
in the same change that writes the record** — a record with no ledger line is
invisible to future planning.

Create the file with this header when absent:

```markdown
# Ideas Ledger

Index of parked and rejected requests. Maintenance contract: append one line
per park/reject decision in the same change that writes the decision record;
flip a line to `unparked` (with date + evidence) when project-direction
revives it; never delete lines — this file is planning memory.

| Date | Status | Idea | Unpark condition / rejection reason | Record |
|------|--------|------|-------------------------------------|--------|
```

Status values: `parked` · `rejected` · `unparked (YYYY-MM-DD)`. The unpark
condition column repeats the record's "what would need to become true" in one
line so milestone synthesis can evaluate it without opening every record.
