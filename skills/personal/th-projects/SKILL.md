---
name: th-projects
description: >
  Use for project-level engineering governance in any repository — establishing or auditing a
  project's knowledge architecture (doctrine, design contracts, specs, topology, engineering
  standards), deciding what to work on next via spec-driven planning, running a repo-wide
  health audit, concretizing a feature request into a spec delta, or reconciling specs against
  implementation. Route to exactly one subskill per task. Triggers: "project shape", "bootstrap
  docs", "knowledge architecture", "what should we work on next", "prioritize features",
  "does the code match the spec", "should we build this", "break this down into chunks",
  "review this project", "audit the codebase", "assess project health", "I want to add X",
  "spec this feature", "turn this idea into requirements", "reconcile spec vs implementation".
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

Superskill router for spec-driven project governance. Four subskills live under
`subskills/`; each is a complete standard skill package (own `SKILL.md`,
`references/`, `scripts/`). Subskills are **not** installed in the global skill
catalog — discover them lazily from this package and load **at most one**
subskill body per task. A subskill may itself tell you to consult a sibling
(e.g. project-review runs project-shape's scanner); follow those links from the
subskill, not from here.

The four subskills cover one lifecycle:

1. **Shape** establishes the normative baseline — what the project believes,
   how it is designed, what exactly must be built, where everything lives, and
   the engineering bar for changing it.
2. **Feature request** runs one concrete proposal through the idea funnel
   against that baseline, producing a signed-off spec delta.
3. **Review** audits the implementation against the baseline and generic
   health criteria (including exhaustive spec↔code reconciliation), producing
   confirmed findings.
4. **Direction** turns baseline + spec deltas + findings into a prioritized,
   spec-linked work plan and hands execution to beads tooling.

## Discover subskills

```bash
PKG="$(dirname "$SKILL_PATH")"
find "$PKG/subskills" -maxdepth 2 -name SKILL.md
rg -n "^name:|^description:" "$PKG"/subskills/*/SKILL.md
```

## Routing table

| Task intent | Subskill | Typical trigger |
|---|---|---|
| Bootstrap or audit the project's knowledge architecture (five pillars: heart-and-soul, legends-and-lore, openspec, lay-and-land, craft-and-care); decide where an idea should be documented; generate a layman overview. | [subskills/project-shape/SKILL.md](subskills/project-shape/SKILL.md) | "set up project structure", "bootstrap docs", "where should this go", "audit documentation health" |
| Concretize ONE fuzzy feature/project request into a signed-off spec delta: motif, doctrine gate, topology placement, design sketch, WHEN/THEN scenarios. | [subskills/project-feature-request/SKILL.md](subskills/project-feature-request/SKILL.md) | "I want to add X", "spec this feature", "turn this idea into requirements", "what would it take to build X" |
| Decide what to work on next; evaluate competing priorities; check roadmap alignment; turn approved specs into a prioritized beads work plan. | [subskills/project-direction/SKILL.md](subskills/project-direction/SKILL.md) | "what's highest leverage", "what should we work on next", "break this down", "is this roadmap aligned" |
| Repo-wide health audit: code quality, reliability, security, docs, maintainability — scored, evidence-based, with a planning handoff packet. Includes the exhaustive spec-reconciliation mode (bidirectional spec↔code gap audit + remediation). | [subskills/project-review/SKILL.md](subskills/project-review/SKILL.md) | "review this project", "audit the codebase", "assess project health", "reconcile spec vs implementation", "what's implemented but undocumented" |

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
- **Feature vs. direction**: one concrete proposal → feature-request; many
  competing priorities or "what next" → direction. A feature request that
  survives its funnel hands its spec delta to direction for sequencing.
- **Scope guard**: single-PR or diff review is not project-level — use
  `/code-review`. Change-level engineering-quality judgment (the engineering
  bar, readability, test rigor, dependency hygiene, cruft cleanup, skill
  reviews, diagrams) belongs to `/th-engineering`; project-shape's
  craft-and-care pillar adopts that bar by reference. Backlog mechanics
  without direction analysis belong to `/beads-orchestration` (beads-writer).
  Hygiene of this machine's AI-tooling harness (installed skills, dotfiles,
  snapshot state) belongs to `/th-tooling`.
- **Fallback**: if the task is project-adjacent but none of the rows fit,
  answer from router-level context or ask — do not load a subskill to browse.

## Shared invariants (all subskills)

- The five-pillar shape model (`about/heart-and-soul`, `about/legends-and-lore`,
  `openspec/`, `about/lay-and-land`, `about/craft-and-care`) is the single
  normative vocabulary; subskills must not redefine it.
- Specifications are the source of truth for work planning; implementation
  without spec coverage is a finding, not a baseline. The OpenSpec file format
  these subskills read and write is one shared contract,
  [`references/spec-format.md`](references/spec-format.md) at this package root,
  not owned by any single subskill.
- Every major claim cites evidence and is labeled [Observed], [Inferred], or
  [Unknown].
- Subskills reference each other by relative path (`../project-shape/…`) inside
  this package; those paths are package-internal and stable.
