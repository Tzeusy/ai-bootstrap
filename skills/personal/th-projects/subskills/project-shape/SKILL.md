---
name: project-shape
description: >
  Use when bootstrapping or auditing a project's doctrine, design contracts,
  specifications, topology, and engineering standards; deciding where project
  knowledge belongs; maintaining those five pillars; or generating a
  layman-friendly project overview. Triggers: "project shape", "bootstrap
  project docs", "where should this decision live", "audit our project
  documentation", "set up doctrine and specs", "explain this project".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
compatibility: Scripts require bash, git, find, grep, and uv. Local-skill validation uses Python 3.11+ through uv.
---

# Project Shape

Build and maintain one normative knowledge architecture. The five pillars are:

| Pillar | Question | Canonical path |
|---|---|---|
| Heart and Soul | Why does this project exist, and what must it not become? | `about/heart-and-soul/` |
| Legends and Lore | Which design contracts and decisions govern it? | `about/legends-and-lore/` |
| Spec and Spine | What observable behavior must exist? | `openspec/` |
| Lay and Land | Where do components, boundaries, and data flows live? | `about/lay-and-land/` |
| Craft and Care | What quality bar governs changes? | `about/craft-and-care/` |

README communicates; these pillars govern. A project exposes them through one
local `doctrine` superskill with one navigator per pillar, never five competing
global skill entries.

## Invariants

- Preserve the five-pillar vocabulary and source-of-truth boundaries. Do not
  invent a parallel doctrine system.
- Doctrine changes are proposals until the owner adopts them. Specifications
  require owner signoff before implementation.
- VISION remains a continuous constraint; downstream artifacts cite the
  baseline commit and revalidate affected mandates after it moves.
- Label major claims `[Observed]`, `[Inferred]`, or `[Unknown]`. Normative
  authoring receives independent semantic review proportional to blast radius;
  scripts establish structure, not truth.
- Ask the human only for irreducible intent, priorities, and tolerances. Derive
  repository facts directly, one dependent question at a time.
- Shape creates and maintains governance artifacts. Feature specification,
  repo-health scoring, prioritization, and execution route to their owning
  subskills.

## Select a mode

| Mode | Selection | Load and execute |
|---|---|---|
| Assess / place | Determine current maturity or where knowledge belongs | Run [`scripts/shape-scan.sh`](scripts/shape-scan.sh). Use [`references/maturity-rubric.md`](references/maturity-rubric.md) only to interpret ratings. Place content by the five questions above. |
| Bootstrap | New or unshaped project needs the pillars | Read [`references/bootstrapping.md`](references/bootstrapping.md), then [`references/consultative-bootstrapping.md`](references/consultative-bootstrapping.md). Scaffold with [`scripts/shape-init.sh`](scripts/shape-init.sh), but replace prompts with discovered project truth. |
| Audit / maintain | Existing shape may be stale, contradictory, or incomplete | Scan first, then use [`references/review-protocol.md`](references/review-protocol.md). Reconcile cross-pillar contradictions without silently deciding owner questions. |
| Overview | Explain the project for a lay reader without weakening canonical docs | Read [`references/generate-overview.md`](references/generate-overview.md); use [`references/diagram-specs.md`](references/diagram-specs.md) only when diagrams materially help. |
| Doctrine amendment | Heart-and-soul needs to change | Follow [`references/doctrine-amendment.md`](references/doctrine-amendment.md): proposal, blast-radius review, owner adoption, downstream sweep. |
| Feature request | One idea needs behavioral requirements | Route to [`../project-feature-request/SKILL.md`](../project-feature-request/SKILL.md); do not run shape bootstrap merely because some pillars are absent. |

Constrained environments use **Lite** review: separate coherence and
adversarial passes with explicit owner validation. **No-diagram** mode uses
Mermaid or prose and skips image generation; it does not block shape work.

## Pillar guides

Load only the pillar being authored or repaired:

- Heart and Soul: [`references/pillar-heart-and-soul.md`](references/pillar-heart-and-soul.md)
- Legends and Lore: [`references/pillar-legends-and-lore.md`](references/pillar-legends-and-lore.md)
- Spec and Spine: [`references/pillar-spec-and-spine.md`](references/pillar-spec-and-spine.md)
- Lay and Land: [`references/pillar-lay-and-land.md`](references/pillar-lay-and-land.md)
- Craft and Care: [`references/pillar-craft-and-care.md`](references/pillar-craft-and-care.md)

For local doctrine navigation, read
[`references/local-skill-templates.md`](references/local-skill-templates.md),
generate the package with `shape-init.sh --skills-only`, and validate it with
[`scripts/validate_local_skill.py`](scripts/validate_local_skill.py) through
the documented scripts. Never hand-copy pillar content into navigator skills.

## Verification and supporting visuals

After changes to shape routing, scanner, scaffolder, or fallbacks, run
[`scripts/self-test.sh`](scripts/self-test.sh) and
[`scripts/eval-fallbacks.sh`](scripts/eval-fallbacks.sh). Package behavior
scenarios live in
[`references/evaluation-scenarios.md`](references/evaluation-scenarios.md).

Load a visual only for the matching explanation; editable sources sit beside
each SVG:

- [`assets/five-pillars-load-bearing.svg`](assets/five-pillars-load-bearing.svg) ([source](assets/five-pillars-load-bearing.excalidraw))
- [`assets/five-pillars-health-risks.svg`](assets/five-pillars-health-risks.svg) ([source](assets/five-pillars-health-risks.excalidraw))
- [`assets/pillar-traceability.svg`](assets/pillar-traceability.svg) ([source](assets/pillar-traceability.excalidraw))
- [`assets/idea-funnel.svg`](assets/idea-funnel.svg) ([source](assets/idea-funnel.excalidraw))
- [`assets/review-fanout.svg`](assets/review-fanout.svg) ([source](assets/review-fanout.excalidraw))
- [`assets/coordinator-workflow.svg`](assets/coordinator-workflow.svg) ([source](assets/coordinator-workflow.excalidraw))

Do not collapse pillars into a monolith, treat README as doctrine, author specs
without doctrine, preserve stale design contracts, or self-approve normative
changes.
