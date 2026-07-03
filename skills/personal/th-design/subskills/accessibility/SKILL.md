---
name: accessibility
description: >
  Use when building or reviewing any user surface for accessibility — keyboard
  operability, focus management, contrast ratios, semantic markup and screen
  reader support, hit-target sizing, reduced motion — or when auditing an
  existing UI against WCAG-level expectations.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-07-03"
---

# Accessibility

Accessible by default: designed in from the first draft, verified before
ship. The bar is WCAG 2.2 AA as a floor, applied with judgment — a retrofitted
accessibility pass is itself a finding against the process.

## Use This Skill When

- Building any new user surface (web, TUI, CLI output) — apply during design,
  not after
- Auditing an existing UI for keyboard, contrast, or screen-reader gaps
- Reviewing a PR that adds or changes interactive elements
- Answering "is this accessible enough to ship"

Example trigger phrasings: "audit accessibility", "contrast check", "does this
work with a screen reader", "keyboard navigation is broken", "is this WCAG
compliant".

## Do Not Use This Skill For

- Keyboard *ergonomics* beyond operability (chords, palettes) —
  [discoverability](../discoverability/SKILL.md)
- Choosing the palette's meanings — [visual-language](../visual-language/SKILL.md)
  (this skill constrains those choices)

## Reviewable Expectations

### Keyboard

- Everything operable by keyboard alone: every action reachable, every widget
  usable, no pointer-only interactions (hover-only menus, drag-only reorder
  without an alternative).
- Focus is always visible (a real focus ring — never `outline: none` without
  replacement), tab order follows reading order, focus never gets trapped.
- Modals: focus moves in on open, returns to the trigger on close, Esc
  closes.
- TUI/CLI count too: interactive terminal UIs need the same complete keyboard
  paths and visible focus/selection state.

### Contrast and color

- Text ≥ 4.5:1 against its background (3:1 for large text); interactive
  component boundaries and icons ≥ 3:1. Verify with a checker, don't eyeball.
- Both themes verified: a palette that passes in dark mode and fails in light
  mode fails.
- Color is never the only signal: pair state colors with an icon, label, or
  position ([visual-language](../visual-language/SKILL.md) enforces the same
  rule from the palette side).

### Semantics

- Native elements first: `<button>`, `<a>`, `<label>`, `<table>`, headings in
  order. ARIA only to fill genuine gaps — a `div` with a click handler is a
  defect, not a style choice.
- Icon-only controls carry an accessible name (`aria-label` or equivalent);
  images that inform carry alt text; decorative ones are hidden from the
  tree.
- Dynamic results are announced: async completions, optimistic updates, and
  validation errors reach the screen reader (`aria-live`/status regions), not
  just the pixels — the snappy patterns in
  [interaction-speed](../interaction-speed/SKILL.md) must stay perceivable
  without sight.

### Ergonomic floor

- Hit targets ≥ 44×44 CSS px (Apple HIG) / 48dp (Material) on touch; WCAG
  2.2 AA (2.5.8) sets the hard minimum at 24×24. Generous click areas
  everywhere (whole row, not just the 12px icon).
- `prefers-reduced-motion` (or platform equivalent) honored: animations
  reduce to instant state changes. This skill owns the rule;
  [visual-language](../visual-language/SKILL.md) defers here.
- Text resizes to 200% without loss of content or function (1.4.4); content
  reflows without horizontal scrolling down to a 320px viewport / 400% zoom
  (1.4.10).

## Review Method

1. Unplug the mouse: complete the primary flows by keyboard alone; note every
   dead end and invisible focus stop.
2. Run a contrast check over the token palette (both themes); cite failing
   pairs with ratios.
3. Grep interactive markup for defect patterns — `onClick` on non-semantic
   elements, `outline: none`, icon buttons without labels, missing `alt` —
   cite file:line.
4. Screen-reader pass on the primary flow (or static-analysis equivalent when
   a reader isn't available): names, roles, announcements present.

No built UI yet? Apply the same expectations to the spec's described
behavior; evidence cites the spec section or screen region.

Severity follows blast radius: an unlabeled primary action outranks a
low-contrast footnote. Fix in scope now, per
[design-bar](../design-bar/SKILL.md).
