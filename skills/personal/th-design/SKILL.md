---
name: th-design
description: >
  Use for UI and UX work on web, TUI, CLI, dashboard, or internal-tool
  surfaces: design review, information density, visual language, perceived
  speed, discoverability, accessibility, and production frontend styling.
  Routes each concern to one package-local subskill; use th-engineering for
  implementation quality.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
---

# TH Design

Select the row matching the user-facing concern, then read that subskill
completely. Internal subskills are package-local and load only after selection.
Route distinct concerns independently; execution orchestration remains
caller-owned.

| Intent | Read |
|---|---|
| Holistic design bar or UX walkthrough | [design-bar](subskills/design-bar/SKILL.md) |
| Density, hierarchy, copy, layout, forms | [information-design](subskills/information-design/SKILL.md) |
| Color, typography, spacing, motion, design systems | [visual-language](subskills/visual-language/SKILL.md) |
| Perceived latency, optimistic UI, interruption | [interaction-speed](subskills/interaction-speed/SKILL.md) |
| Feature discovery, command palettes, keyboard paths | [discoverability](subskills/discoverability/SKILL.md) |
| Keyboard, focus, contrast, semantics, reduced motion | [accessibility](subskills/accessibility/SKILL.md) |
| Build or restyle distinctive production web UI | [frontend-design](subskills/frontend-design/SKILL.md) |

## Boundaries

- Product feel routes here; implementation readability, tests, dependencies,
  and diagnosis route to `/th-engineering`.
- "Feels slow" routes to `interaction-speed`; an unexplained measured
  regression routes to `/th-engineering` diagnosis after the UX bar is clear.
- Chart interaction and app-level visual semantics route here; chart mark and
  encoding construction routes to `/dataviz`.
- Use the local `frontend-design` workflow by default. For optional deep polish
  in a project already wired for Impeccable, read
  [external craft setup](references/external-craft.md) before selecting it.
- If no row fits, answer from this boundary context or ask one clarifying
  question. Do not load subskills speculatively.
