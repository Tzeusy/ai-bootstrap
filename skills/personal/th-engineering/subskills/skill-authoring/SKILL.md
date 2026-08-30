---
name: skill-authoring
description: Use when creating or substantially updating a repo-owned skill that must follow this repository's superskill, provenance, cross-tool adapter, PEP 723, unloaded routing-eval, and strict-audit conventions. Do not use as a replacement for the current platform-native skill-creation manual.
license: Derived guidance; upstream terms are in ../../../../skill-creator/LICENSE.txt
metadata:
  owner: tze
  authors:
    - tze
    - Anthropic (upstream)
    - OpenAI Codex (local tuning)
  status: active
  last_reviewed: "2026-08-31"
  provenance:
    source: skills/skill-creator/SKILL.md
    source_commit: d685954ab55df87de90d462c333bf8e418d3cb88
    relationship: local cross-tool delta only
compatibility: Requires uv for the repository audit loop.
---

# Skill Authoring

Apply this repository's local and cross-tool deltas after reading the current
platform-native creator for general skill anatomy and authoring guidance. This
package intentionally does not duplicate that manual.

## Local Decisions

1. Read repository guidance and relevant project-shape docs before deciding
   placement. Author shared workflows under `skills/`; keep tool facades thin.
2. Choose one standard skill or a router-style superskill. For the local
   `subskills/` extension, read
   [superskills](../skill-standards/references/superskills.md); bootstrap prunes
   hidden subskills rather than flattening them into the global catalog.
3. Preserve provenance for upstream-derived or intentionally forked content:
   record the source, revision when known, relationship, authors, and license.
   Explain tool-specific divergence instead of silently copying it.
4. Keep canonical instructions portable. Put genuine client-only UI or policy
   in adapters such as `agents/openai.yaml`, and keep adapter descriptions
   aligned with `SKILL.md`. Check flattened skill names for collisions.
5. Give each executable Python helper PEP 723 inline metadata and invoke it
   with `uv run`. Do not add resources without a concrete consumer.
6. Keep realistic trigger samples unloaded. For a superskill, add
   `evals/routing.json` with positive coverage for every route plus negative
   and ambiguous cases; the audit validates structure, not model behavior.

## Verification Loop

Run the package's helpers with `--help`, exercise changed behavior, then run:

```bash
uv run <skill-standards>/scripts/audit_skill.py <skill-dir> --strict
```

Read the full [quality bar](../skill-standards/references/quality-bar.md) while
authoring and use the [review checklist](../skill-standards/references/review-checklist.md)
before handoff. Fix every error and warning; forward-test routing behavior when
risk warrants it.

## Provenance

Tuned from the repository's retained Anthropic `skills/skill-creator` import at
commit `d685954ab55df87de90d462c333bf8e418d3cb88`. Retained ideas are limited to
progressive disclosure and purposeful resources; all instructions above are
repository-specific deltas for superskills, provenance, adapters, PEP 723,
cross-tool placement, routing evals, and the strict audit loop.
