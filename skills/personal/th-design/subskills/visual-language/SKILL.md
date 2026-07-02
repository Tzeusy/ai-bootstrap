---
name: visual-language
description: >
  Use when choosing or reviewing colors, typography, spacing, component styling,
  or motion/animation for a user surface — establishing consistent visual
  semantics, judging whether an animation is justified, or auditing a UI for
  visual drift and inconsistency.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-07-03"
---

# Visual Language

Color, type, spacing, and motion. The bar: **clean and consistent** — color is
welcome, but every visual choice carries one meaning everywhere, and motion
exists only to communicate.

## Use This Skill When

- Picking a palette or assigning colors to states, categories, or actions
- Auditing a UI for visual drift: same concept styled differently, or same
  style meaning different things
- Judging whether an animation or transition should exist
- Setting typography, spacing, radius, or elevation conventions

Example trigger phrasings: "pick colors for this", "is this consistent", "is
this animation necessary", "this UI looks messy", "set up design tokens".

## Do Not Use This Skill For

- What content appears and at what density —
  [information-design](../information-design/SKILL.md)
- Contrast ratios and non-color signaling as compliance concerns —
  [accessibility](../accessibility/SKILL.md) (this skill still forbids
  inaccessible choices)
- Chart-specific palettes — `/dataviz`, under these semantics

## Reviewable Expectations

### Color

- One hue, one meaning, everywhere: red = destructive/error, green =
  success/healthy, yellow/orange = caution, one accent hue = interactive.
  A hue reused with a second meaning is a defect.
- Adding a color = adding a meaning. Name it and record it (tokens, style
  guide, or a comment block if that's all the project has). Unnamed one-off
  hex values are drift.
- Color is welcome and encouraged where it encodes information (status,
  category, severity) — but never as the *only* channel; pair with icon,
  label, or position ([accessibility](../accessibility/SKILL.md)).
- Neutrals do the layout work; saturated color is spent on meaning and
  attention, so it stays scarce enough to keep working.
- Use tokens/variables, not literals, so light/dark themes stay one mapping
  away.

### Consistency

- One spacing scale, one type scale (≤2 families, few sizes), one
  radius/shadow vocabulary per product. New values join the scale or don't
  ship.
- The same control looks and behaves identically everywhere: a primary button
  on one screen is a primary button on all screens. Same for empty states,
  errors, and loading treatments.
- Novelty needs a reason: a deviation from the established pattern is either
  justified in review or reverted.

### Motion

- Animation exists only to communicate: where something came from or went
  (spatial continuity), that state changed (a toggle, a completed async
  action), or where attention is needed. Decoration, delight-loops, parallax,
  and animated page furniture are defects.
- Budget: transitions ~100–200ms, ease-out; never longer on a path the user
  hits repeatedly. An animation the user waits *through* twice a minute is a
  latency bug ([interaction-speed](../interaction-speed/SKILL.md)).
- Motion never blocks input, and honors `prefers-reduced-motion` (or the
  platform equivalent) by reducing to instant state changes.
- When in doubt, no animation. The absence of an animation is never a defect;
  an unjustified one always is.

## Review Method

1. Inventory: list every color, font size, spacing value, and animation in
   scope (grep styles/tokens where possible — cite file:line).
2. For each color: state its meaning; flag hues with two meanings or meanings
   with two hues.
3. For each animation: state what it communicates; no answer → remove.
4. Diff same-concept components across screens; flag divergence.

Findings cite the element and expectation violated; conflicts with density or
accessibility resolve via [design-bar](../design-bar/SKILL.md) biases.
