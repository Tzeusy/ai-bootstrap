---
name: audit-skill-hygiene
description: >
  Use to produce a content-safe, reproducible measurement-only audit of
  cataloged skill usage from Claude Code and Codex. Emits an aggregate
  decision matrix; it never changes catalogs or recommends direct archival.
  Triggers: "audit skill usage", "which skills are actually used", "is our
  skill catalog bloated".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-14"
compatibility: Requires uv (Python 3.9+), git, and the canonical ai-bootstrap repository; reads configured Claude and Codex transcript sources without modifying them.
---

# Audit Skill Hygiene

Every cataloged skill adds recurring frontmatter context. This subskill measures
usage conservatively so an owner can make a later, reversible catalog decision
with evidence. It is measurement-only: it does not exclude, relink, mirror,
archive, bootstrap, or otherwise alter any skill surface.

## Reproducible workflow

1. Choose a fixed UTC observation point and run
   [`scripts/skill_usage_audit.py`](./scripts/skill_usage_audit.py) from the
   canonical repository:

   ```bash
   uv run skills/personal/th-tooling/subskills/audit-skill-hygiene/scripts/skill_usage_audit.py \
     --repo-root . \
     --as-of 2026-08-14T00:00:00Z
   ```

   The primary window is 90 days, with a 30-day sensitivity window. Override
   either only when the report records the fixed `--as-of` value alongside it.
   Add `--json` only when a machine-readable aggregate matrix is needed.

2. The audit invokes the linker's read-only catalog-manifest mode. That mode
   reuses the installer's exclusions, prune list, shallowest-path selection,
   lexical tiebreaker, ownership detection, and managed-surface definitions;
   it creates no tool-home entries. Manifest sources are repository-relative
   and identify repository versus submodule ownership. The canonical surface
   is `skills/`; the managed mirror surfaces are `.claude/skills`,
   `.codex/skills`, `.gemini/skills`, and `.gemini/antigravity/skills`.

3. Read the 13-row decision matrix as an evidence ledger, not an execution
   plan. It records aggregate Claude/Codex counts for both windows, coverage,
   catalog token cost, freshness, ownership, trigger and overlap rationale,
   and a conservative disposition.

## What counts as usage

- Claude Skill: an `assistant` record whose assistant message contains a
  `tool_use` block named `Skill` with a string `input.skill`.
- Claude slash: a `user` record whose user-message string has the complete
  command-message, command-name, and optional command-args event shape.
- Codex: a `response_item` whose `function_call` payload is the `read_file`
  function and whose JSON `arguments.path` is a `SKILL.md` path.

Raw catalog mentions, prose tags, command arguments, and unrelated record
values never count.

Transcript records are streamed only to aggregate counters. Reports retain no
transcript body, identifier, filename, project label, or absolute path. The
report exposes source availability and coverage counts so a zero is never
mistaken for complete retention history.

## Interpretation rules

- Incomplete history makes zero-use rows `insufficient-evidence`.
- Newly added and unknown-age skills remain protected (`retain`).
- With complete coverage and established age: three or more uses is `retain`,
  one or two is `marginal-review`, and zero is `candidate-follow-up` only.
- `using-superpowers` remains `measurement-limited`: native catalog injection
  can satisfy its session-start role without a readable call.
- `dispatching-parallel-agents` and `subagent-driven-development` retain their
  separate contracts: independent parallel dispatch versus plan execution and
  review checkpoints.

## Hard stops

- Do not treat any disposition as authorization for a catalog change.
- Do not inspect or quote raw transcript content to override a result.
- Any exclusion, deduplication, relink, mirror, submodule, or tool-home change
  is a separate reversible follow-up with its own relink verification.
- This audit has no catalog rollout to roll back. A later owner-approved
  catalog change must define its rollback and verify the canonical surface and
  every managed mirror before and after the change.
