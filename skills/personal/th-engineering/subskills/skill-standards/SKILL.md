---
name: skill-standards
description: Use when creating, updating, reviewing, or auditing a skill or superskill and you need a concrete quality bar for triggers, project grounding, metadata, authorship, routing, context efficiency, scripts, and validation.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
    - Claude
  status: active
  last_reviewed: "2026-07-19"
compatibility: Requires uv to run scripts/audit_skill.py.
---

# Skill Standards

Review bar for new skills and updates to existing ones, including
router-style superskills.

The standard: easy to discover, cheap to load, grounded in the right source
of truth, explicit about who owns it.

## Use This Skill When

- Creating a new skill; you want a quality bar before shipping it
- Reviewing or auditing a skill for discoverability, grounding, context
  efficiency, and maintainability
- Updating a skill; checking for drift, bloat, or stale metadata
- Designing a superskill that routes to internal subskills without putting
  every subskill in the global skill catalog

Example trigger phrasings: "review this skill", "is this SKILL.md well
designed", "audit our skills for quality", "should this be a superskill",
"clean up this skill package".

## Do Not Use This Skill For

- Replacing `/skill-creator` for initial scaffolding or end-to-end authoring
- Replacing project-specific doctrine or navigation skills such as
  `/th-projects`
- Acting as the domain skill itself; this is a rubric for skill quality, not
  domain guidance
- Measuring whether installed skills are actually *used* and archiving dead
  ones — `/th-tooling` (audit-skill-hygiene); this skill judges content
  quality, not catalog hygiene

## Workflow

1. Run the mechanical audit
   [`scripts/audit_skill.py`](./scripts/audit_skill.py) first — it checks
   frontmatter, name/description limits, metadata fields, link integrity,
   orphaned support files and deep reference chains, PEP 723 compliance of
   Python entry-point scripts, adapter YAML, and superskill layout:

   ```bash
   uv run <this-package>/scripts/audit_skill.py <target-skill-dir>
   ```

   Resolve `<this-package>` from the path of the `SKILL.md` you loaded —
   this subskill lives under the `th-engineering` package's `subskills/`,
   not a global skills directory.

   Fix every ERROR. Triage WARNs deliberately — fix or justify. Any Python
   helper script flagged for missing PEP 723 inline metadata must be brought
   into compliance as part of the change, not left for later (see
   quality-bar section 8 for the required header).
2. Read the target skill's `SKILL.md` and any support files it references.
   For project-specific skills, read the relevant project-shape docs first
   (via `/th-projects`) so the skill stays aligned with the repo's actual
   doctrine, topology, and spec surface.
3. Judge what the script cannot, using
   [`references/quality-bar.md`](./references/quality-bar.md):
   trigger quality, scope sharpness, project grounding, progressive
   discovery, script-vs-prose decisions, runtime token economics of
   prescribed commands (projected output, log-tail readback, targeted
   gates, grep-first catalogs), operational safety, and maintenance
   contracts on stateful reference docs (catalogs of errors, projects, or
   quirks must tell consuming agents when to write back).
4. Use [`references/superskills.md`](./references/superskills.md) only when
   the skill is broad enough to route over internal workflows rather than run
   a single narrow procedure.
5. Follow [`references/review-checklist.md`](./references/review-checklist.md)
   for the update procedure, verification steps, and anti-patterns.
6. Keep `SKILL.md`, tool-specific adapter files (e.g. `agents/openai.yaml`),
   and referenced support files aligned. If the skill still reads as a
   monolith after review, split heavy guidance into direct support files
   instead of appending more prose.
