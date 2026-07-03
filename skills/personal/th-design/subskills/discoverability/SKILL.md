---
name: discoverability
description: >
  Use when users can't find a feature, when adding a command palette or
  launcher (Spotlight/Rofi-style), when designing keyboard shortcuts and power
  paths, or when reviewing whether a product's features are findable and its
  frequent actions have fast routes.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-07-03"
---

# Discoverability

Features are findable in the product itself, and frequent actions grow fast
paths. The bar: **discoverable power** — the first use needs no docs, the
tenth use needs no mouse.

## Use This Skill When

- Users (or the walkthrough) reveal a feature nobody finds
- Adding or designing a command palette / launcher (Spotlight, Rofi, Ctrl+K
  style) or a keyboard-shortcut scheme
- Placing a new control: where does it live so the user meets it when needed?
- Reviewing a product for hidden features, doc-dependent flows, or missing
  power paths

Example trigger phrasings: "nobody finds this feature", "add a command
palette", "make this keyboard-first", "where should this button go", "audit
what's discoverable".

## Do Not Use This Skill For

- What a screen says once the user is on it —
  [information-design](../information-design/SKILL.md)
- Keyboard *operability* as a compliance floor —
  [accessibility](../accessibility/SKILL.md) (this skill builds power paths on
  top of that floor)

## Reviewable Expectations

### Findability

- Every feature is reachable from the product surface without reading
  external docs. If a wiki or manual is the only path to a feature, the
  feature is hidden — a defect in the product, not the docs. For CLIs, the
  product surface *is* `--help`, man pages, and shell completion: a flag
  those expose is discoverable; one documented only in a README is not.
- Contextual surfacing: the control lives where the need arises (row actions
  on the row, filter where the list is), not in a distant settings page or
  junk-drawer menu.
- Empty states teach: an empty list shows the action that fills it, not just
  "No items".
- Search over navigation once a surface is large: past a screenful of
  destinations or actions, hierarchical menus stop scaling; give the user a
  type-to-find path.

### Shortcut surfaces — hold in high regard

- A **command palette** (fuzzy, keyboard-invoked, Spotlight/Rofi-style) is a
  first-class feature, not a power-user garnish. Any app with more than a
  screenful of actions or destinations should have one; for internal tools
  and dev-facing products it is the default expectation.
- Palette contract: opens on Ctrl/Cmd+K by convention — captured only while
  focus is inside the app, never globally shadowing browser or system
  chords — with a visible affordance (a ⌘K hint in the chrome) so the chord
  isn't the only way in. Fuzzy-matches verbs *and* nouns (actions,
  navigation, entities), shows recents first, executes without further mouse
  input, and displays each entry's keybinding inline — the palette is where
  shortcuts are learned.
- Everything in menus is in the palette; the palette may contain more than
  the menus.
- CLI analog: shell completion and did-you-mean suggestions are the palette.
  A CLI that ships without completions fails this expectation.

### Keyboard paths

- Every frequent mouse path has a keyboard path. Full operability is the
  accessibility floor; this bar adds *ergonomics* — chords for hot actions,
  not just Tab-Tab-Tab-Enter.
- Shortcuts are advertised where the action lives: in the tooltip, beside the
  menu item, in the palette entry. A shortcut listed only in a help page
  doesn't exist.
- Follow platform conventions before inventing chords; never shadow
  system-level or browser-level bindings.

### Progressive power

- Defaults for the first use, accelerators for the tenth: the novice path and
  the fast path coexist, and the product nudges the transition (e.g. tooltip
  showing the chord after repeated menu use).
- The design-bar walkthrough's **Habit** question feeds this skill: whatever
  annoys the tenth use is the shortcut to build
  ([design-bar](../design-bar/SKILL.md)).

## Review Method

1. Feature census: list user-facing capabilities; for each, record the
   discovery path (visible control / menu / palette / docs-only / tribal).
   Docs-only and tribal entries are findings.
2. Hot-action census: list the 5–10 most frequent actions; each needs a
   keyboard route and (if a palette exists) a palette entry, with the binding
   advertised in the UI. Cite the missing surface.
3. For a new control: name the moment of need, place the control in that
   moment's screen region, then add its palette/keyboard route in the same
   change — not as follow-up.

No built UI yet? Apply the same expectations to the spec's described
surfaces; evidence cites the spec section or screen region.
