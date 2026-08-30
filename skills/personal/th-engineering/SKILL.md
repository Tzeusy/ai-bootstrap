---
name: th-engineering
description: >
  Use for engineering-quality work on a change or codebase: holistic
  completeness, readability, tests, dependencies, diagnosis, refactor cleanup,
  documentation, skill authoring or review, and Excalidraw diagrams. Routes
  each concern to one package-local subskill; use th-projects for project
  governance and th-design for product UX.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
compatibility: skill-standards auditing and Excalidraw rendering require uv and Python 3.11+; Excalidraw rendering also requires Playwright Chromium setup.
---

# TH Engineering

Select the row matching the task, then read that subskill completely. Internal
subskills are package-local and load only after selection. Route distinct
concerns independently; execution orchestration remains caller-owned.

| Intent | Read |
|---|---|
| Holistic quality and definition of done | [engineering-bar](subskills/engineering-bar/SKILL.md) |
| Readability, naming, abstraction, comments | [code-readability](subskills/code-readability/SKILL.md) |
| Test design, coverage, flakes, suite discipline | [test-rigor](subskills/test-rigor/SKILL.md) |
| Module boundaries, layering, cycles, libraries | [dependency-hygiene](subskills/dependency-hygiene/SKILL.md) |
| Hard bugs, regressions, performance diagnosis | [diagnosis](subskills/diagnosis/SKILL.md) |
| Refactor or migration cruft removal | [cruft-cleanup](subskills/cruft-cleanup/SKILL.md) |
| Codebase documentation and interface semantics | [documentation](subskills/documentation/SKILL.md) |
| Create or update a repo-owned, cross-tool skill | [skill-authoring](subskills/skill-authoring/SKILL.md) |
| Review or audit a skill or superskill | [skill-standards](subskills/skill-standards/SKILL.md) |
| Create, render, or convert Excalidraw diagrams | [excalidraw-diagram](subskills/excalidraw-diagram/SKILL.md) |

## Boundaries

- Change-level quality routes here; doctrine, specs, topology, prioritization,
  and repo-wide audits route to `/th-projects`.
- Implementation quality routes here; user-facing behavior, visual language,
  accessibility, and perceived speed route to `/th-design`.
- Documentation craft routes to `documentation`; five-pillar knowledge shape
  routes to `/th-projects`.
- Skill content routes to `skill-authoring` or `skill-standards`; installed
  catalog usage, links, and snapshot freshness route to `/th-tooling`.
- If no row fits, answer from this boundary context or ask one clarifying
  question. Do not load subskills speculatively.
