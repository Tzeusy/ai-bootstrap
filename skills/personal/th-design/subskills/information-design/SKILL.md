---
name: information-design
description: >
  Use when deciding what a screen, page, dashboard, table, or output says and in
  what order — calibrating information density, establishing visual hierarchy,
  tightening copy and labels, organizing layout, or laying out forms and their
  validation timing — including judging whether a surface is too dense or too
  sparse.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-07-03"
---

# Information Design

What a surface says, in what order, at what density. The bar: succinct,
organized, dense **where the user's task benefits** — never sparse for
aesthetics, never dense for its own sake.

## Use This Skill When

- Laying out a screen, dashboard, table, CLI output, or report
- Judging whether a surface is too dense or too diluted
- Tightening labels, microcopy, headings, or empty-state text
- Deciding between table, list, cards, or prose for a body of information

Example trigger phrasings: "is this too dense", "this feels cluttered",
"organize this screen", "tighten this copy", "should this be a table".

## Do Not Use This Skill For

- Color, spacing scales, or motion — [visual-language](../visual-language/SKILL.md)
- Whether users can *find* a feature, or whether an empty state routes them
  to the action that fills it — [discoverability](../discoverability/SKILL.md)
  (this skill owns the empty state's *copy*)
- Chart and data-graphic construction — `/dataviz` (this bar still governs
  density and hierarchy choices there)

## Reviewable Expectations

### Hierarchy

- Every surface answers "what do I look at first?" in one glance: one primary
  element per view, established by size/weight/position — not by adding boxes.
- Reading order matches task order: the thing the user acts on next is where
  their eye lands next.
- Grouping follows the user's task, not the data model or the database schema.

### Density

- Calibrate to user mode: monitoring, comparison, and power-user surfaces
  (dashboards, tables, logs, admin panels) run dense — more rows, tighter
  spacing, abbreviations the audience knows. First-run, decision, and
  confirmation surfaces run sparse — one question at a time.
- Whitespace is a hierarchy tool, not a goal. Padding that forces scrolling or
  pagination on a comparison task is a defect, same as a wall of undifferentiated
  text on a decision task.
- Progressive disclosure: summary first, detail on demand — but never hide
  what the user checks *every* time behind a click. Frequency of access
  decides what is surfaced, not tidiness.
- Truncation is a last resort: wrap, reflow, or widen before ellipsizing data
  the user came to read. Ellipsized identifiers (IDs, paths, names) that the
  user must distinguish are a defect.

### Copy

- Words earn their place: labels are a few words, sentences appear only where
  the user genuinely reads. No filler ("Please note that…", "In order to…"),
  no restating what the UI already shows.
- Microcopy states the action, not the category: "Save draft", not "Submit";
  "Delete 3 files", not "Confirm".
- One name per concept: the same entity or action carries the same word
  everywhere — UI, palette entries, errors, docs. Synonym drift ("remove" /
  "delete" / "discard" for one operation) is a defect.
- Error text says what happened and what to do next, in that order.
- Numbers formatted for scanning: aligned decimals, thousands separators,
  units on the column header not every cell.

### Forms and validation

- Validate on blur or submit, never per keystroke: don't red-flag a field the
  user is still typing in. Live-as-you-type feedback is for positive
  confirmation (name available, password strong enough), not for
  errors-in-progress.
- Errors sit inline at the offending field; any summary links to them.
- Failure never destroys input: the form re-renders with every entered value
  intact ([interaction-speed](../interaction-speed/SKILL.md) owns state
  preservation).
- Ask only what can't be defaulted, remembered, or inferred (design-bar's
  Defaults question); every optional field justifies its presence.

### Presentation

- Tables for comparison across items; lists for scanning one attribute; prose
  for narrative only. Never prose where a table fits.
- Icons accompany labels; icon-only is reserved for universally known glyphs
  or space-critical dense surfaces (with tooltips and accessible labels —
  see [accessibility](../accessibility/SKILL.md)).

## Review Method

1. Identify the surface's user mode (first-run / decision / monitoring /
   power-loop) — density findings are relative to mode, not absolute.
2. Squint test: blur the layout; the primary element and grouping should
   survive. If everything has equal weight, hierarchy is missing.
3. Read every string aloud; cut words until meaning would break.
4. For each hidden-by-default detail, ask: how often is it checked? Daily →
   surface it.

No built UI yet? Apply the same expectations to the spec's described
behavior; evidence cites the spec section or screen region.

Findings cite the element and the expectation violated; severity follows the
design-bar rule (friction × frequency —
[design-bar](../design-bar/SKILL.md)).
