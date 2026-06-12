---
name: th-engineering
description: >
  Use for engineering-quality work on any change or codebase — holding an implementation or
  review to the engineering quality bar, judging code readability and maintainability,
  assessing test-suite rigor, auditing module boundaries and dependency chains, hunting
  compatibility cruft after refactors/renames/migrations, creating or auditing codebase
  documentation (READMEs, docs trees, doc sites, code-cited facts), creating or reviewing
  skills against the skill quality bar, or producing Excalidraw diagrams. Route to exactly
  one subskill per subdomain; fan out subagents when a task spans several. Triggers: "hold
  this to the engineering bar", "is this change done", "is this code readable", "review
  these tests", "are these tests meaningful", "untangle these dependencies", "clean up
  this refactor", "finish this migration", "document this service", "audit the docs",
  "review this skill", "audit our skills", "draw a diagram", "visualize this architecture".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
compatibility: skill-standards auditing and excalidraw rendering require uv and Python 3.11+; excalidraw-diagram additionally requires Playwright Chromium setup on first render.
---

# TH Engineering

Superskill router for the engineering quality bar. Eight subskills live under
`subskills/`; each is a complete standard skill package (own `SKILL.md`,
`references/`, optional `scripts/`). Subskills are **not** installed in the
global skill catalog — discover them lazily from this package and load **at
most one** subskill body per subdomain. When a task spans several subdomains,
prefer one subagent per subskill over loading multiple bodies yourself (see
"Subagent dispatch").

Where `/th-projects` governs the project (doctrine, specs, topology, audits),
this superskill governs the change: the quality bar code must clear while it
is being written, reviewed, or cleaned up.

## Discover subskills

```bash
PKG="$(dirname "<absolute-path-to-this-SKILL.md>")"
find "$PKG/subskills" -maxdepth 2 -name SKILL.md
rg -n "^name:|^description:" "$PKG"/subskills/*/SKILL.md
```

## Routing table

| Task intent | Subskill | Typical trigger |
|---|---|---|
| Hold a change to the canonical engineering bar: default engineering biases, definition of done, durable-fix and same-change-documentation discipline. Also the source projects reference when authoring their `about/craft-and-care/` pillar. | [subskills/engineering-bar/SKILL.md](subskills/engineering-bar/SKILL.md) | "hold this to the engineering bar", "is this change complete", "what's our default quality bar" |
| Judge or improve readability and maintainability: naming, function shape, abstraction altitude, comment discipline, simplicity over cleverness. | [subskills/code-readability/SKILL.md](subskills/code-readability/SKILL.md) | "is this readable", "simplify this code", "review naming and structure" |
| Judge or improve test quality: behavior-focused assertions, edge and failure-path coverage, regression tests for bugfixes, tautological/flaky test elimination. | [subskills/test-rigor/SKILL.md](subskills/test-rigor/SKILL.md) | "review these tests", "are these tests meaningful", "what coverage is missing" |
| Audit module boundaries and dependency chains: dependency direction, layering, cycles, public surface, third-party admission and upgrades. | [subskills/dependency-hygiene/SKILL.md](subskills/dependency-hygiene/SKILL.md) | "untangle these dependencies", "is this layering right", "should we add this library" |
| Create, review, or audit codebase documentation: concise project synthesis, architecture/data-flow/error-handling diagrams, contract-level code-cited facts under a maintenance contract, interface semantics cards (side effects, idempotency, failure), human-readable doc sites (OpenAPI, MkDocs, Sphinx). | [subskills/documentation/SKILL.md](subskills/documentation/SKILL.md) | "document this service", "audit docs for stale claims", "is this README adequate", "make the API docs readable" |
| Finish same-repo refactors/renames/migrations: delete lingering aliases, re-exports, wrappers, fallback branches, deprecated flags. | [subskills/cruft-cleanup/SKILL.md](subskills/cruft-cleanup/SKILL.md) | "clean up this refactor", "old path still works", "finish this migration" |
| Create, update, review, or audit a skill or superskill against the skill quality bar (triggers, grounding, metadata, routing, context efficiency, scripts, validation). | [subskills/skill-standards/SKILL.md](subskills/skill-standards/SKILL.md) | "review this skill", "is this SKILL.md well designed", "should this be a superskill" |
| Convert a workflow, architecture, protocol, concept, or Mermaid graph into (or out of) an Excalidraw diagram that argues visually. | [subskills/excalidraw-diagram/SKILL.md](subskills/excalidraw-diagram/SKILL.md) | "draw a diagram", "visualize this flow", "convert this Mermaid" |

## Routing rules

- **Bar vs. subdomain**: "is this change good/done" holistically → engineering-bar.
  An ask naming one subdomain (tests, naming, dependencies, leftover wrappers)
  → that subskill directly. engineering-bar states the biases; the subdomain
  subskills operationalize them.
- **Change-level vs. project-level**: single change, diff, PR, or module →
  here. Repo-wide health audits, spec governance, prioritization, knowledge
  architecture → `/th-projects`. When th-projects' project-shape authors a
  `craft-and-care` pillar, it consults engineering-bar for the default biases
  rather than restating them.
- **Docs craft vs. knowledge architecture**: README/docs/diagram/doc-site
  quality for any repo → documentation. Establishing or auditing the
  five-pillar knowledge architecture itself → `/th-projects` (project-shape).
  documentation consumes excalidraw-diagram for its diagrams — that pairing
  is expected, not a routing violation.
- **Tooling subdomains stand alone**: skill-standards and excalidraw-diagram
  are self-contained crafts; route to them on their triggers without loading
  the code-quality subskills.
- **Fallback**: if the task is quality-adjacent but no row fits, answer from
  router-level context or ask — do not load a subskill to browse.

## Subagent dispatch

The subskills are independent subdomains, so multi-subdomain work parallelizes
cleanly. Prefer subagents over serial subskill loading:

- **Quality sweep over a change** (e.g. review covering cruft + readability +
  tests + dependencies): dispatch one subagent per relevant subskill. Each
  subagent prompt must include (1) the absolute path to its
  `subskills/<name>/SKILL.md` with the instruction to read and apply it,
  (2) the exact scope (diff, files, or directories), and (3) the required
  output: a list of findings, each with file:line evidence and a proposed fix.
  Synthesize and dedupe in the parent; conflicts between subdomains resolve
  via engineering-bar's biases.
- **Iteration-heavy single subdomains**: excalidraw-diagram's render-view-fix
  loop and skill-standards' audit-and-fix loop burn context quickly — delegate
  the whole loop to one subagent and review only the artifact it returns.
- **Don't dispatch for one narrow question** ("is this name clear?") — load
  the single relevant subskill and answer directly.

## Shared invariants (all subskills)

- Quality claims are reviewable expectations, not taste: every finding cites
  file:line (or skill-path) evidence and states which expectation it violates.
- engineering-bar's default biases are the baseline every other subskill
  assumes. A project's `about/craft-and-care/` pillar may override them; when
  it exists, the project's pillar wins.
- Fix-it-now beats file-it-away: when a finding is small and in scope, the
  deliverable is the fix, not a ticket.
- Subskills reference each other by relative path (`../engineering-bar/…`)
  inside this package; those paths are package-internal and stable.
