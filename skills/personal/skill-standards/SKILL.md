---
name: skill-standards
description: Use when creating or updating a skill and you need a concrete quality bar for triggers, project grounding, metadata, authorship, context efficiency, and validation.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-04-12"
---

# Skill Standards

Use this skill as the review bar for both new skills and updates to existing
ones.

The standard is simple: a skill should be easy to discover, cheap to load,
grounded in the right source of truth, and explicit about who owns it.

## Use This Skill When

- Creating a new skill and you want a quality bar before shipping it
- Updating an existing skill and you want to check for drift, bloat, or stale
  package metadata
- Reviewing whether a skill is discoverable, grounded, concise, and maintainable

## Do Not Use This Skill For

- Replacing `/skill-creator` for initial scaffolding or end-to-end authoring
  workflow
- Replacing project-specific doctrine or navigation skills such as
  `/project-shape`
- Acting as the domain skill itself; this is a rubric for skill quality, not
  domain guidance

## Non-Negotiable Requirements

### 1. Follow Agent Skills best practices

Every skill must follow the current `agentskills.io` model:

- `SKILL.md` begins with valid YAML frontmatter.
- `name` and `description` are present and accurate.
- The `description` is trigger-oriented. It explains when to use the skill,
  not the full workflow.
- The body stays lean and acts as guidance or routing, not a giant duplicate of
  all related documentation.
- Progressive discovery is mandatory for non-trivial skills. Use `SKILL.md` as
  the routing layer, then fan detailed or compartmentalized guidance out into
  `references/`, deterministic helpers into `scripts/`, and output resources
  into `assets/`.
- Supporting files must be discoverable progressively. If details live in
  `references/`, `scripts/`, or `assets/`, link them from `SKILL.md` and say
  when to read or use them so only the relevant slice gets loaded.
- Write valid, portable YAML. Do not rely on client-specific parser quirks.

### 2. Ground project-specific skills in project shape

If the skill is specific to one repository or product, it must align with that
project's documented source of truth.

- Read the relevant `/project-shape` pillars first when they exist:
  `about/heart-and-soul/`, `about/legends-and-lore/`, `openspec/`,
  `about/lay-and-land/`, and `about/craft-and-care/`.
- Treat the skill as a navigation and execution layer over those docs, not a
  competing doctrine.
- If the skill and the project docs disagree, fix the inconsistency. Do not let
  the skill become a third truth source.
- Project-local terminology, boundaries, and quality expectations should match
  the project's own shape docs exactly.

### 3. Require clear metadata and authorship

Every skill must make ownership obvious.

- Required loader metadata: `name`, `description`.
- Recommended local metadata:
  - `metadata.owner`: accountable human owner
  - `metadata.authors`: who authored or substantially revised it
  - `metadata.status`: `active`, `draft`, or `deprecated`
  - `metadata.last_reviewed`: last substantive review date
- Add `compatibility` only when runtime requirements or environment assumptions
  materially affect use.
- If `agents/openai.yaml` exists, keep it in sync with the `SKILL.md`
  description and actual purpose.

## Additional Standards To Encourage

These should usually be enforced even when not explicitly requested.

### 4. Sharp scope and trigger quality

- One skill should solve one coherent class of problems.
- The title and description should help the agent find the skill from real
  symptoms, user phrasing, and task context.
- Include clear "use when" boundaries and, where helpful, brief "do not use
  when" guidance.
- Avoid vague umbrella skills unless they are intentionally routing skills.

### 5. Progressive disclosure and context discipline

- Emphasize progressive discovery, not just brevity. `SKILL.md` should help the
  agent decide what to load next rather than trying to carry the whole skill in
  one file.
- Keep `SKILL.md` short enough to load cheaply.
- Fan heavy or domain-specific reference material into `references/` so those
  parts can be discovered separately when needed.
- Fan deterministic, repeated, or fragile procedures into `scripts/` so the
  executable logic can be used without bloating the core instructions.
- Move output-only resources into `assets/`.
- Link every important support file from `SKILL.md` with explicit selection
  guidance.
- Avoid deep reference chains. Important support files should usually be linked
  directly from `SKILL.md`, not discovered through multiple hops.
- Prefer several narrow supporting files over one monolithic support document
  when the subject naturally splits by task, framework, domain, or workflow
  step.

### 6. Evidence over generic prose

- Skills should capture proven workflows, recurring failure modes, or durable
  repo knowledge.
- Prefer concrete heuristics, checklists, and commands over abstract advice.
- Do not write a skill as a narrative of one session.
- Do not preserve stale workaround text after the underlying problem or tooling
  has changed.

### 7. Script repeated or complex workflows

- When a workflow is complex, fragile, repeated, or expensive to reconstruct
  from prose, prefer a standardized script over long inline instructions.
- Well-documented scripts let future agents reuse a known-good workflow instead
  of reinventing it from scratch.
- Python is a strong default for these helpers unless another language is
  clearly a better fit for the environment.
- Prefer `uv`-managed standalone scripts with PEP 723 inline metadata so the
  script declares its own dependencies and Python requirements.
- Run scripts with `uv run` and initialize or maintain metadata with
  `uv init --script` and `uv add --script`.
- If reproducibility matters, encourage `uv lock --script` and commit the
  adjacent lockfile when the repository wants locked script environments.
- Scripts should include a short purpose statement, clear usage examples, and
  stable flags so agents can invoke them correctly without rereading large docs.

### 8. Safe and explicit operational boundaries

- State prerequisites, destructive edges, and hard stops clearly.
- Fail closed when the environment is missing required tools, auth, or context.
- Do not hide risky actions inside broad workflow language.
- Do not create misleading or surprise behavior relative to the skill's stated
  purpose.

### 9. Update discipline

When updating a skill:

1. Read the current `SKILL.md`, `agents/openai.yaml`, and any referenced helper
   files before editing.
2. Remove stale guidance instead of only appending new text.
3. Re-check trigger wording, related-skill references, metadata, and
   compatibility notes.
4. Verify that referenced files, commands, and paths still exist.
5. Keep examples, scripts, and UI metadata synchronized with the revised skill.

### 10. Verification before calling it done

- Test the skill against at least one realistic "should trigger" case.
- If scope is subtle, test one "should not trigger" case too.
- For updates, verify the revised skill still matches the package layout and
  referenced files.
- If the skill contains executable helpers, verify the documented invocation is
  still correct.

## Recommended Review Checklist

Use this checklist before shipping a new or updated skill:

1. Is the description about activation, not workflow summary?
2. Is the skill grounded in the right source of truth?
3. Does `SKILL.md` route well, or should more content fan out into
   `references/` or `scripts/`?
4. Should any repeated or fragile workflow be turned into a standardized script?
5. Are metadata, authorship, and compatibility fields clear and factual?
6. Are related files and `agents/openai.yaml` aligned with the current skill?
7. Does the skill define boundaries, prerequisites, and failure modes?
8. Would another agent find this skill from the way a real user asks for help?

## Anti-Patterns

- Bloated `SKILL.md` files that duplicate reference docs
- Treating progressive discovery as optional instead of as the default design
  pattern
- Re-explaining the same complex workflow in prose instead of encapsulating it
  in a reusable script
- Descriptions that summarize the process instead of describing triggers
- Project-specific rules invented without checking project-shape docs
- Skills with no accountable owner or review date
- Stale references, dead scripts, or mismatched `agents/openai.yaml`
- Session stories disguised as reusable guidance
