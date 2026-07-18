---
name: design-bar
description: >
  Use when designing or reviewing anything with a user surface and you need the
  canonical design quality bar — default UX biases, the UX walkthrough ritual,
  and the definition of done — or when resolving conflicts between design
  subdomain findings.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-07-18"
---

# Design Bar

Canonical default quality bar for user-facing work. The goal is **seamless
UX**: the interface moves as fast as the user's thought and never makes them
hunt, wait, or re-read. Everything here is a reviewable expectation: a reviewer
can reject a design or change for violating it. A project's own design system
overrides individual biases where present; when a bias is not overridden, it
applies.

## Use This Skill When

- Designing any feature with a user surface — web UI, TUI, CLI, config file,
  API ergonomics, error message — and deciding what "good" requires
- Reviewing a design, mockup, or implemented UI holistically before shipping
- Resolving a conflict between subdomain findings (e.g. density vs.
  accessibility) — biases set the tiebreak

Example trigger phrasings: "hold this to the design bar", "walk through the
UX", "is this UX done", "design this feature", "review this flow".

## Do Not Use This Skill For

- Deep work in one subdomain — route to the sibling subskill
  ([information-design](../information-design/SKILL.md),
  [visual-language](../visual-language/SKILL.md),
  [interaction-speed](../interaction-speed/SKILL.md),
  [discoverability](../discoverability/SKILL.md),
  [accessibility](../accessibility/SKILL.md))
- Implementation code quality — `/th-engineering`

## Locate the Project Design System First

Before applying the default biases, spend one search pass finding the project's
own design system — it overrides individual biases wherever it speaks, and a
review that cites a generic bias where the project has a settled rule is a
wrong finding. Look for, in rough order of authority:

- **Design-language specs** — e.g. `openspec/specs/*design-language*/`,
  `specs/**/design*`, or a requirements doc naming tokens, type scale,
  motion vocabulary, and copy rules. Spec-form design systems are binding:
  cite their requirement headings in findings, and route proposed changes to
  the language through the project's spec workflow, not ad-hoc edits.
- **Doctrine/principles docs** — `docs/design*`, `about/**/design*`, a
  DESIGN.md: the WHY layer (settled decisions like theme commitment or
  accessibility floor) that shapes how the concrete rules are interpreted.
- **Token/theme files** — `tokens.css`, `index.css`, `theme.ts`, Tailwind
  config: the de facto palette and scale when nothing more explicit exists.

When these disagree with each other, prefer spec over doctrine over de facto
implementation, and flag the disagreement itself as a finding. When nothing is
found, say so and apply the default biases in full.

## Default Design Biases

Unless a project's design system explicitly overrides them, these apply:

1. **Seamless UX is the goal** — Any point where the user waits on the
   interface, hunts for a feature, re-reads to understand, or repeats an
   action to make it stick is a defect, not a nicety.
2. **Walk the UX of everything** — No user-facing change ships without the
   walkthrough below. "It's just a config option" is not an exemption; config
   options have users too.
3. **Density where logical, never for its own sake — in either direction** —
   Don't dilute information to look minimal; don't cram to look powerful.
   Calibrate to the user's mode.
   ([information-design](../information-design/SKILL.md) operationalizes.)
4. **Accessible by default** — Keyboard-operable, contrast-safe,
   screen-reader-sane from the first draft. Retrofitted accessibility is a
   defect. ([accessibility](../accessibility/SKILL.md) operationalizes.)
5. **Consistency over novelty** — Color is welcome; each color, pattern, and
   control carries one meaning everywhere. Novel presentation needs a reason.
   ([visual-language](../visual-language/SKILL.md) operationalizes.)
6. **Motion must earn its keep** — Animation only when it communicates state;
   decorative animation is a defect.
   ([visual-language](../visual-language/SKILL.md) operationalizes.)
7. **Discoverable power** — Features are findable in the product itself, and
   frequent actions grow shortcut paths (command palettes, keybindings).
   ([discoverability](../discoverability/SKILL.md) operationalizes.)
8. **Fast beats fancy** — Perceived latency is a design property, not an
   implementation detail. Preload, cache, and render optimistically where
   effects are reversible.
   ([interaction-speed](../interaction-speed/SKILL.md) operationalizes,
   including where optimism is forbidden.)

## The UX Walkthrough

Simulate the user before shipping. Answer each question with evidence from the
actual flow, not intention:

- **Entry** — How does the user reach this? How many clicks/keystrokes from
  intent to done? Every step must justify itself.
- **First glance** — What do they see first? Is it the thing they came for?
- **Pace** — Where do they wait? Is every wait acknowledged within ~100ms and
  does the UI stay usable during it? Does the interface keep up with a user
  who already knows what they want?
- **Repetition** — Will they click this control more than once? Is a repeat
  click safe (idempotent), and if they *needed* to repeat it, what feedback
  failed?
- **Defaults** — What must the user specify that the product could have
  known, remembered, or inferred from context? Every pre-fillable field is
  pre-filled; every repeated choice is remembered.
- **Recovery** — What happens on error or mis-click? Prefer undo over
  confirm dialogs where the action is actually reversible; require explicit
  confirmation where it is not — never replace a confirm with an undo that
  can't undo. Does the error say what to do next?
- **Habit** — After the tenth use, what will annoy them? That annoyance is the
  shortcut or default to build now.

A "no" or "don't know" on any question is an open finding, not a note.

## Definition of Done

A user-facing change is complete when all of these hold:

- **Walkthrough passed** — every walkthrough question answered from the real
  flow, findings fixed (bias 2).
- **No dead waits** — every operation >100ms acknowledges immediately; nothing
  blocks input without cause (bias 8).
- **Repeat-safe** — no control double-fires; destructive actions are undoable
  or explicitly confirmed (bias 1).
- **Findable** — the feature is reachable from the product surface (UI,
  `--help`, completion) without external docs; frequent paths have a
  keyboard/palette route (bias 7).
- **Accessible** — keyboard path, visible focus, AA contrast verified
  (bias 4).
- **Consistent** — reuses the project's existing colors, spacing, controls,
  and vocabulary; deviations are deliberate and documented (bias 5).

## Applying the Bar in Review

- Cite the bias or done-criterion a finding violates, with evidence (screen,
  component, file:line, spec section, or walkthrough step). Specs and
  mockups are reviewable exactly like built UI: apply the same expectations
  to the described behavior.
- Severity = friction × frequency: a 300ms stall on a hot path outranks a
  color inconsistency on a settings page.
- When two biases tension (e.g. density vs. accessibility), prefer the one
  protecting the user's flow and ability to act; say which you chose and why.
- Classify findings before expanding work:
  - Small, local violations clearly inside the approved outcome (label, focus,
    copy, spacing, existing-state feedback) get fixed in the current change by
    its implementation owner, not filed as new beads.
  - Missing correctness required for the approved flow stays in the current
    task/PR even when non-trivial; rewrite acceptance scenarios when repeated
    review shows the original matrix was incomplete.
  - Consent, authentication, trust-boundary, persisted-contract, or new behavior
    discoveries return to `/th-projects` at the earliest affected feature/spec
    gate before implementation; if required for the active outcome, link them
    as a prerequisite rather than absorbing them. Do not improvise product
    policy during review.
  - Duplicate or already-active outcomes link to existing work; do not create a
    second finding bead.
- Preserve independent review: "fix now" assigns work to the current author or
  recovery lane. If a reviewer authors a semantic correction, require a fresh
  independent review of the exact resulting head.
