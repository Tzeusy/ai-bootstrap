---
name: th-tooling
description: >
  Use for hygiene of this machine's AI-tooling harness: measure catalog
  usage, review dotfiles, refresh installed snapshots, manage transcript
  retention, compact agent memory, or audit MCP, permission, and hook
  surfaces. Route one harness task to one package-local workflow. Not for
  general project engineering or manual sudo and TTY handoffs.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
compatibility: Usage auditing requires uv and Python 3.9+; workflows assume the ~/.dotfiles and ai-bootstrap layout.
---

# TH Tooling

Six package-local workflows keep the AI-tooling harness measurable, lean, and
reproducible. Select one before reading its body. Use `/th-engineering` for
change quality and `/th-projects` for project governance.

## Discover subskills

```bash
PKG="$(dirname "<absolute-path-to-this-SKILL.md>")"
find "$PKG/subskills" -maxdepth 2 -name SKILL.md
rg -n "^name:|^description:" "$PKG"/subskills/*/SKILL.md
```

## Routing table

| Task intent | Subskill | Typical trigger |
|---|---|---|
| Measure cataloged skill usage without changing any catalog surface. | [subskills/audit-skill-hygiene/SKILL.md](subskills/audit-skill-hygiene/SKILL.md) | "audit my skills", "which skills are used" |
| Review dotfiles (rc files, aliases, env, tool config) for conflicts, dead config, and best practices — without touching secret files. | [subskills/dotfiles-review/SKILL.md](subskills/dotfiles-review/SKILL.md) | "review my dotfiles", "clean up my zshrc", "are my aliases conflicting" |
| Verify or refresh links, submodules, plugins, and managed mirrors. | [subskills/refresh-snapshots/SKILL.md](subskills/refresh-snapshots/SKILL.md) | "refresh snapshots", "relink skills", "is my harness healthy" |
| Disk retention for session transcripts and tool logs: inventory, age-tiered compress/delete policy, audit-window trade-off. | [subskills/transcript-retention/SKILL.md](subskills/transcript-retention/SKILL.md) | "transcripts eating disk", "clean up old sessions" |
| Compact append-only agent memory: AGENTS.md notes-to-self, bd memories — dedupe, merge superseded, retire orphans, keep guardrails. | [subskills/memory-hygiene/SKILL.md](subskills/memory-hygiene/SKILL.md) | "AGENTS.md is huge", "compact my notes", "stale memories" |
| Audit non-skill context surfaces: MCP servers, permission allowlists, hooks — configured vs. actually used in transcripts. | [subskills/config-surface-audit/SKILL.md](subskills/config-surface-audit/SKILL.md) | "audit my MCP servers", "stale permissions", "config bloat" |

## Routing rules

- **Measure vs. act**: usage auditing reports evidence only. Archive, relink,
  mirror, or config changes require a separately authorized task.
- **Config content vs. installed state**: questions about what the dotfiles
  *say* (aliases, exports, rc files) → dotfiles-review; questions about
  whether what's *installed* matches the repo (links, submodules, mirrors) →
  refresh-snapshots.
- **Broad hygiene request**: identify the independent workflows, then let the
  caller choose execution order or orchestration. This router does not grant
  mutation authority.
- **Fallback**: harness-adjacent but no row fits (e.g. authoring a new skill
  → `/th-engineering` skill-standards; bootstrap.sh logic changes → plain
  engineering work). Do not load a subskill to browse.

## Boundaries

- Read-only measurement never authorizes archive, config, or mirror changes.
- Never read or quote secret material: anything gitignored, under
  `credentials/`, or in `to_source/machine_specific` / `to_source/passwords`
  is out of bounds (verify with `git check-ignore` when unsure).
- Non-destructive by default: prefer `skills/archive/` moves and idempotent
  re-runs over deletion; everything must be restorable with one `git mv` or
  one bootstrap re-run.
- Manual sudo, TTY, 2FA, or out-of-band handoffs are cross-tool base policy,
  not harness hygiene. Tool instruction files route directly to
  [the canonical handoff reference](references/manual-user-handoff.md); load
  its [root-disk example](references/manual-user-handoff-example.md) only when
  a concrete sudo diagnostic pattern helps.
