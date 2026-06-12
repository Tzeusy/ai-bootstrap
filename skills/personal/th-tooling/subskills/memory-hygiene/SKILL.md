---
name: memory-hygiene
description: >
  Use to compact agent memory stores that grow append-only and rot —
  AGENTS.md "Notes to self" sections, bd memories, CLAUDE.md instruction
  drift — by deduplicating, merging superseded entries, and retiring notes
  whose subject no longer exists. Triggers: "compact my notes to self",
  "AGENTS.md is huge", "clean up bd memories", "stale agent memory".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
compatibility: Operates on AGENTS.md / CLAUDE.md files and the bd CLI where present.
---

# Memory Hygiene

Agent memory is append-only by habit: every session adds a note, none
removes one. The result is the same rot as unused skills — every future
session pays to read superseded, duplicate, or orphaned notes. The
canonical failure mode (observed in ~/.dotfiles AGENTS.md): a defect is
recorded in one bullet and declared fixed three bullets later — both
survive forever.

## Scope

- `AGENTS.md` "Notes to self" sections (repo-level memory contract)
- `bd memories` entries where beads is in use
- `CLAUDE.md` files only for *factual drift* (paths/commands that no longer
  exist) — their instructions are the user's, not yours to compact

## Workflow

1. **Inventory**: read the target store end-to-end. For each entry record:
   subject, date (if any), and whether its subject still exists (file
   paths, skill names, flags — verify with a quick `ls`/`rg`, don't trust
   the note).
2. **Classify** each entry:
   - **superseded** — a later entry updates or reverses it (the
     defect-then-fixed pair merges into one resolved-state note)
   - **duplicate** — same fact stated twice with different wording
   - **orphaned** — subject was deleted/renamed (e.g. notes about a skill
     path that moved to `skills/archive/`)
   - **live** — still accurate and load-bearing
3. **Propose the compaction as a diff** — merged entries keep the *current
   truth* plus the date; history belongs to git, not to the note. Never
   silently drop a note that encodes a hard-won lesson ("do not reintroduce
   X") — those stay even when old, they are guardrails, not status.
4. Apply on approval, one store per commit, with before/after entry counts
   in the commit message.
5. For `bd memories`: list with `bd memories`, then retire/update via the
   bd commands available in that version (`bd remember` to restate; check
   `bd --help` for delete semantics before assuming).

## Judgment lines

- A note is a **guardrail** if removing it could cause a regression
  (anti-pattern warnings, "don't reintroduce" rules) — keep, even if old.
- A note is **status** if it describes a point-in-time state ("X is broken",
  "Y pending") — verify current state and either update or delete.
- When a store mixes both per entry, split the entry rather than keeping
  the stale half alive.

## Hard stops

- Never compact another agent's *active* coordination state (beads notes
  fields used as heartbeats, `.pm/` folders) — memory hygiene is for
  durable knowledge stores only.
- Preserve the memory contract header/format of the file you compact; the
  next session must still know where to append.
