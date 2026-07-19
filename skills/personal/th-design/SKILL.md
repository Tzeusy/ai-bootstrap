---
name: th-design
description: >
  Use for UI/UX design work on anything with a user surface — web UI, TUI, CLI
  ergonomics, dashboards, editors, internal tools — holding a design, spec,
  mockup, or implementation to the owner's design bar, and building or
  polishing distinctive production-grade frontends (websites, landing pages,
  components, styling/beautifying any web UI). The bar: seamless snappy UX,
  accessible consistent visuals, calibrated information density, discoverable
  features with shortcut surfaces (command palettes), perceived-performance
  engineering, motion restraint. Chart construction (dataviz) executes under
  this bar. Triggers: "design this UI", "build/style this page or component",
  "hold this to the design bar", "walk through the UX", "is this too
  dense/sparse", "review this UX", "make this feel faster", "feels sluggish",
  "add a command palette", "audit accessibility", "is this animation
  necessary", "pick colors", "make this look less generic".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-07-19"
---

# TH Design

Superskill router for the owner's design bar. Seven subskills live under
`subskills/`, each a complete skill package. **Not** in the global catalog —
discover lazily, load **at most one** subskill body per subdomain, and fan
out subagents only when scope warrants (see "Subagent dispatch").

The thesis: **seamless UX**. The interface moves as fast as the user's thought,
shows what matters without dilution, and never makes them hunt, wait, or
re-read. This bar applies to *anything* a human uses — a button, a CLI flag, a
config file, an error message — not just web frontends.

`/th-engineering` governs how the code is built; this superskill governs how
the product feels. Execution craft lives in the `frontend-design` subskill
(greenfield builds and styling), the external `impeccable` package (see
"External craft skills"), and `/dataviz` (charts); when any of them conflicts
with this bar, this bar wins.

## Routing table

| Task intent | Subskill | Typical trigger |
|---|---|---|
| Holistic design bar: default biases, the UX walkthrough ritual, definition of done for any user-facing change. | [subskills/design-bar/SKILL.md](subskills/design-bar/SKILL.md) | "hold this to the design bar", "walk through the UX", "is this UX done" |
| Information density, hierarchy, succinct copy, layout organization, forms and validation timing: what a surface says and in what order. | [subskills/information-design/SKILL.md](subskills/information-design/SKILL.md) | "is this too dense/sparse", "organize this screen", "tighten this copy" |
| Color semantics, visual consistency, typography/spacing scales, motion restraint; establishing a project design system (tokens, meanings, design-language spec). | [subskills/visual-language/SKILL.md](subskills/visual-language/SKILL.md) | "pick colors", "is this consistent", "is this animation necessary", "set up a design system" |
| Perceived performance: latency budgets, preloading, caching, optimistic rendering, idempotent controls, interruption and toast policy. | [subskills/interaction-speed/SKILL.md](subskills/interaction-speed/SKILL.md) | "make this feel faster", "feels sluggish", "users double-click this" |
| Feature discoverability and shortcut surfaces: command palettes, keyboard paths, CLI help/completions, contextual controls, empty states that teach. | [subskills/discoverability/SKILL.md](subskills/discoverability/SKILL.md) | "add a command palette", "nobody finds this feature", "keyboard-first" |
| Accessibility: keyboard operability, focus, contrast, semantics, reduced motion. | [subskills/accessibility/SKILL.md](subskills/accessibility/SKILL.md) | "audit accessibility", "contrast check", "screen reader support" |
| Execution: build or restyle distinctive production-grade web UI (pages, components, artifacts) with a committed aesthetic direction, avoiding generic-AI looks. Output obeys the bar subskills above. | [subskills/frontend-design/SKILL.md](subskills/frontend-design/SKILL.md) | "build this page/component", "style/beautify this UI", "make this look less generic" |

## Routing rules

- **Bar vs. subdomain**: holistic "is this good/designed right" → design-bar;
  an ask naming one subdomain → that subskill directly.
- **Feel vs. build**: how the product should behave and look → here. Code
  quality of the implementation → `/th-engineering`. Chart palette and mark
  *construction* → `/dataviz`, under this bar's biases; a chart hue that
  contradicts the app's color semantics is a visual-language finding.
- **Doctrine vs. execution**: bar subskills decide what "good" means;
  execution craft produces it. Web build/styling asks → the
  `frontend-design` subskill; deep iterative polish of an existing frontend
  in a project wired for it → external `impeccable` (below). On conflict,
  design-bar's biases win.
- **Speed symptoms vs. perf bugs**: "feels slow/janky" → interaction-speed
  first; it sets the behavioral bar. Escalate to `/th-engineering` diagnosis
  only once a previously met bar has demonstrably regressed and the cause is
  unknown.
- **Fallback**: design-adjacent but no row fits → answer from router-level
  context or ask; don't load a subskill to browse.

## Discover subskills

The routing table above is the primary index — route from it directly. Run
this only when the table seems stale or you need to verify subskill
frontmatter:

```bash
PKG="$(dirname "<absolute-path-to-this-SKILL.md>")"
find "$PKG/subskills" -maxdepth 2 -name SKILL.md
rg -n "^name:|^description:" "$PKG"/subskills/*/SKILL.md
```

Resolve `PKG` from the base directory your skill loader reported when it
loaded this file; never assume the current working directory is the package.

## External craft skills

`impeccable` (upstream: `pbakaus/impeccable`) is deliberately kept outside
every scanned skills directory — its broad triggers would collide with this
router's in the catalog. Load it by path when a project needs its deep
iterative frontend-polish workflow:

```text
~/.agents/vendor/impeccable/SKILL.md
```

Caveats: it expects a project-side `.agents/skills/impeccable/` install (its
context loader runs `node .agents/skills/impeccable/scripts/load-context.mjs`
from the project root) and PRODUCT.md/DESIGN.md conventions. If the target
project lacks that wiring, prefer the `frontend-design` subskill instead of
fighting impeccable's gates. Its output remains subject to this bar.

## Subagent dispatch

Subskills are independent subdomains; multi-subdomain work parallelizes —
but scale dispatch to scope:

- **Small scope, several subdomains** (one screen, one flow, one CLI): run
  design-bar's walkthrough inline and consult subdomain expectations
  directly; no fan-out.
- **Design review sweep** (multi-screen/multi-flow scope AND ≥3 subdomains):
  one subagent per relevant subskill. Each prompt
  carries (1) the absolute path to its `subskills/<name>/SKILL.md` with
  instruction to read and apply it, (2) exact scope (screens, components,
  files, flows), (3) the output contract: findings with evidence
  (screen/component/file:line) and a proposed fix. Parent synthesizes and
  dedupes; conflicts resolve via design-bar's biases.
- **Iteration-heavy single subdomains** (color-palette tuning,
  command-palette build, density pass on one dashboard): delegate the whole
  loop, review the returned artifact.
- **One narrow question**: load the single subskill, answer directly.

## Shared invariants (all subskills)

- [subskills/design-bar/SKILL.md](subskills/design-bar/SKILL.md) owns the
  baseline every subskill assumes — the default biases, evidence-cited
  findings, severity rule, and fix-it-now policy. A project's own design
  system overrides individual biases where present; absence of one never
  lowers the bar. Design-bar also owns the locate step: find the project's
  design system (design-language specs, doctrine docs, token files) before
  reviewing, and cite it over generic biases. Some projects keep the design
  language as a normative spec (e.g. `openspec/specs/*design-language*/`) —
  changes to the language then go through the spec workflow, not ad-hoc edits.
- Expectations apply to specs and mockups as much as built UI.
- Small in-scope findings fix now; consent/auth, trust-boundary, contract, or
  genuinely new behavior discoveries return to `/th-projects` at the earliest
  affected spec gate. Full finding classification lives in design-bar.
- Subskills reference each other by relative path (`../design-bar/…`); those
  paths are package-internal and stable.
