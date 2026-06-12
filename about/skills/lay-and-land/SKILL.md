---
name: lay-and-land
description: >
  Load ai-bootstrap's topology maps when working in the ai-bootstrap repository
  and you need to know where something lives: which paths are canonical source,
  which are mirrors, which are installed runtime targets, and which are
  local-only. Use before adding components, changing the mirror/install flow,
  or touching tool facades. Only applies inside ai-bootstrap; routes to
  about/lay-and-land/ rather than restating it.
---

# ai-bootstrap Topology — Lay and Land

`about/lay-and-land/` maps the ai-bootstrap repository: tool facades, shared
authoring layers, mirror surfaces, install targets, and local-only state. This
skill is a routing index — read the canonical files; do not rely on summaries
of them.

**Consult before:**
- Adding or moving a top-level directory or skill tree
- Changing how skills are mirrored or installed into tool homes
- Touching `.claude/`, `.codex/`, `.gemini/`, or `opencode/` surfaces
- Deciding whether a path is canonical, mirrored, or local-only

## Map Index

| Map | Read when... | Key content |
|-----|-------------|-------------|
| `about/lay-and-land/components.md` | Need ownership and boundaries | Component inventory, tracked-vs-local splits, boundary notes |
| `about/lay-and-land/data-flow.md` | Need to trace authored → installed content | Authoring-to-consumption flow, generated-asset flow, trust and drift boundaries |
| `about/lay-and-land/deployment.md` | Need install semantics | Clone/symlink runtime topology, environment boundaries |
| `about/lay-and-land/assets/README.md` | Adding topology diagrams | Diagram source/render conventions |

## Key Boundaries

The load-bearing distinctions (read `components.md` for the full versions):
canonical authored source (`skills/`, with `skills/personal/` primary) vs.
mirror/entrypoint surfaces (tool skill dirs) vs. installed runtime targets
(`$HOME` paths) vs. local-only state (never canonical).

## Quick Reference

| Need | Go to |
|------|-------|
| Why a boundary is constitutional | `about/heart-and-soul/` |
| The contract that defines the layers | `about/legends-and-lore/` (RFC 0001) |
| The testable requirements on the layout | `openspec/` |
| How to verify a structural change | `about/craft-and-care/` |
