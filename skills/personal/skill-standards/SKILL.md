---
name: skill-standards
description: Use when creating or updating a skill or superskill and you need a concrete quality bar for triggers, project grounding, metadata, authorship, routing, context efficiency, and validation.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-05-17"
---

# Skill Standards

Use this skill as the review bar for both new skills and updates to existing
ones, including router-style superskills.

The standard is simple: a skill should be easy to discover, cheap to load,
grounded in the right source of truth, and explicit about who owns it.

## Use This Skill When

- Creating a new skill and you want a quality bar before shipping it
- Updating an existing skill and you want to check for drift, bloat, or stale
  package metadata
- Reviewing whether a skill is discoverable, grounded, concise, and maintainable
- Designing a superskill that routes to internal subskills without putting
  every subskill in the global skill catalog

## Do Not Use This Skill For

- Replacing `/skill-creator` for initial scaffolding or end-to-end authoring
  workflow
- Replacing project-specific doctrine or navigation skills such as
  `/project-shape`
- Acting as the domain skill itself; this is a rubric for skill quality, not
  domain guidance

## Workflow

1. Read the target skill's `SKILL.md`, `agents/openai.yaml`, and any support
   files it already references.
2. If the skill is project-specific, read the relevant `/project-shape` docs
   first so the skill stays aligned with the repo's actual doctrine, topology,
   and spec surface.
3. Use [`references/quality-bar.md`](./references/quality-bar.md) for the full
   review criteria:
   - Agent Skills structure and metadata requirements
   - project-shape grounding rules for local skills
   - progressive-discovery and context-discipline expectations
   - superskill boundaries and internal subskill routing
   - scripting, safety, and update-discipline standards
4. Use [`references/superskills.md`](./references/superskills.md) when a
   skill is broad enough to act as a router over internal workflows instead of a
   single narrow procedure.
5. Use [`references/review-checklist.md`](./references/review-checklist.md)
   when making changes:
   - pre-ship checklist
   - update steps
   - verification expectations
   - anti-patterns to remove rather than preserve
6. Keep `SKILL.md`, `agents/openai.yaml`, and referenced support files aligned.
   If the skill still reads as a monolith after the review, split the heavy
   guidance into direct support files instead of appending more prose.

## Output Expectations

- Tighten trigger wording before expanding workflow prose.
- Prefer direct links to a small number of support files over deep reference
  chains.
- For superskills, keep only the router in the top-level catalog and require
  subskills to be found lazily from the router's package.
- Remove stale guidance instead of layering new rules on top of it.
- Verify at least one realistic "should trigger" case before calling the skill
  done.
