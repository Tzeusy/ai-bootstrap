# GenAI Project Shape

This repository is the canonical local source for portable AI-assistant configuration and shared skills across multiple coding assistants. It is skills-first: most reusable workflow logic lives under `skills/`, while `agents/` remains an older reference layer used selectively. It is a documentation-first repo: most artifacts exist to be read, symlinked, copied, or mirrored into tool-specific homes rather than executed as a single application.

## The Four Pillars

- `about/heart-and-soul/` answers why this repository exists, what it is trying to preserve, and what it refuses to become.
- `about/legends-and-lore/` captures the design contracts that govern where shared assets live, when tool-specific divergence is allowed, and how distribution works.
- `about/lay-and-land/` maps the repository topology: the tool facades, the shared layers, and the data flow from authored content to installed local environments.
- `openspec/` turns those design decisions into testable repository requirements and change records.

## Reading Order

1. Read [`heart-and-soul/vision.md`](./heart-and-soul/vision.md) for the thesis and non-negotiables.
2. Read [`heart-and-soul/v1.md`](./heart-and-soul/v1.md) for scope boundaries.
3. Read [`legends-and-lore/rfcs/0001-repository-shape-and-distribution.md`](./legends-and-lore/rfcs/0001-repository-shape-and-distribution.md) for the core structural contract.
4. Read [`lay-and-land/components.md`](./lay-and-land/components.md) and [`lay-and-land/data-flow.md`](./lay-and-land/data-flow.md) to orient on structure and movement.
5. Read [`../openspec/changes/bootstrap-project-shape/specs/repository-shape/spec.md`](../openspec/changes/bootstrap-project-shape/specs/repository-shape/spec.md) for the normative repository requirements.

## Shape Thesis

The repo's job is to keep shared AI-assistant knowledge stable, explicit, and portable while still allowing each tool to have its own thin adapter layer. For local mirroring and placement, `skills/` is the primary source of truth even when some non-`personal/` skills are upstream-derived. When contributors add or modify content, the default question is not "what command runs this?" but "where should this live so humans and agents can find it, maintain it, and reuse it across tools?"
