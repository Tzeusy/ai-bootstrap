---
name: th-projects
description: >
  Use for project-level engineering governance in any repository — establishing or auditing a
  project's knowledge architecture (doctrine, design contracts, specs, topology, engineering
  standards), deciding what to work on next via spec-driven planning, or running a repo-wide
  health audit. Route to exactly one subskill per task. Triggers: "project shape", "bootstrap
  docs", "where should this be documented", "knowledge architecture", "what should we work on
  next", "prioritize features", "does the code match the spec", "should we build this", "break
  this down into chunks", "review this project", "audit the codebase", "assess project health".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
compatibility: Subskill scripts require bash, git, grep, find. project-direction additionally assumes the bd (beads) CLI and an OpenSpec-capable environment for changeset synthesis.
---

# TH Projects

Superskill router for spec-driven project governance. Three subskills live under
`subskills/`; each is a complete standard skill package (own `SKILL.md`,
`references/`, `scripts/`). Subskills are **not** installed in the global skill
catalog — discover them lazily from this package and load **at most one**
subskill body per task. A subskill may itself tell you to consult a sibling
(e.g. project-review runs project-shape's scanner); follow those links from the
subskill, not from here.

The three subskills cover one lifecycle:

1. **Shape** establishes the normative baseline — what the project believes,
   how it is designed, what exactly must be built, where everything lives, and
   the engineering bar for changing it.
2. **Review** audits the implementation against that baseline and generic
   health criteria, producing confirmed findings.
3. **Direction** turns baseline + findings into a prioritized, spec-linked work
   plan and hands execution to beads tooling.

## Discover subskills

```bash
find "$(dirname "$SKILL_PATH")/subskills" -maxdepth 2 -name SKILL.md
rg -n "^name:|^description:" subskills/*/SKILL.md
```

## Routing table

| Task intent | Subskill | Typical trigger |
|---|---|---|
| Bootstrap or audit the project's knowledge architecture (five pillars: heart-and-soul, legends-and-lore, openspec, lay-and-land, craft-and-care); decide where an idea should be documented; generate a layman overview. | [subskills/project-shape/SKILL.md](subskills/project-shape/SKILL.md) | "set up project structure", "bootstrap docs", "where should this go", "audit documentation health" |
| Decide what to work on next; evaluate a feature proposal; check spec-to-code drift; turn an approved spec into a prioritized beads work plan. | [subskills/project-direction/SKILL.md](subskills/project-direction/SKILL.md) | "what's highest leverage", "should we build this", "break this down", "is this roadmap aligned" |
| Repo-wide health audit: code quality, reliability, security, docs, maintainability — scored, evidence-based, with a planning handoff packet. | [subskills/project-review/SKILL.md](subskills/project-review/SKILL.md) | "review this project", "audit the codebase", "assess project health", "process this external audit" |

## Routing rules

- **Baseline before judgment**: review and direction both consume the shape
  baseline. If the repo has no shape artifacts at all and the user's real ask is
  "make this project legible", route to project-shape even if they said
  "review".
- **Audit vs. plan**: project-review *classifies* (scores, risks, confirmed
  findings); project-direction *decides* (sequencing, specs, beads). "What's
  wrong with this repo" → review. "What should we do about it / next" →
  direction. A full review naturally hands off to direction — that handoff
  happens inside the subskills.
- **Scope guard**: single-PR or diff review is not project-level — use
  `/code-review`. Exhaustive bidirectional spec↔code reconciliation belongs to
  `/reconcile-spec-to-project`. Backlog mechanics without direction analysis
  belong to `/beads-orchestration` (beads-writer).
- **Fallback**: if the task is project-adjacent but none of the rows fit,
  answer from router-level context or ask — do not load a subskill to browse.

## Shared invariants (all subskills)

- The five-pillar shape model (`about/heart-and-soul`, `about/legends-and-lore`,
  `openspec/`, `about/lay-and-land`, `about/craft-and-care`) is the single
  normative vocabulary; subskills must not redefine it.
- Specifications are the source of truth for work planning; implementation
  without spec coverage is a finding, not a baseline.
- Every major claim cites evidence and is labeled [Observed], [Inferred], or
  [Unknown].
- Subskills reference each other by relative path (`../project-shape/…`) inside
  this package; those paths are package-internal and stable.
