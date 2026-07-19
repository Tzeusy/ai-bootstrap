---
name: th-tooling
description: >
  Use for hygiene of this machine's AI-tooling harness — the ~/.dotfiles
  repo, the ai-bootstrap skills tree, and the installed tool homes
  (~/.claude, ~/.codex, ~/.gemini): auditing real skill usage from
  transcripts, archiving unused skills, reviewing dotfiles for conflicting
  aliases/config, refreshing snapshot state (skill symlinks, submodules,
  mirrored assets), transcript disk retention, compacting agent memory
  (AGENTS.md notes, bd memories), and auditing MCP/permission/hook config
  against actual use. Route to exactly one subskill per task. Triggers:
  "audit my skills", "which skills are unused", "review my dotfiles",
  "clean up my zshrc", "refresh snapshots", "old transcripts eating disk",
  "compact my notes to self", "audit my MCP servers", "harness hygiene".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
compatibility: audit-skill-hygiene requires uv (Python 3.9+) and reads local Claude Code / Codex transcripts; all subskills assume the ~/.dotfiles + ai-bootstrap layout.
---

# TH Tooling

Superskill router for keeping the AI-tooling harness clean as cruft
accumulates over months of use. Three subskills live under `subskills/`,
each a complete skill package. They are **not** in the global catalog —
discover them lazily and load at most one per task.

`/th-engineering` governs the quality of a change; `/th-projects` governs a
project's knowledge architecture; this superskill governs the **harness
itself**: which skills are installed, what the dotfiles configure, and
whether snapshot state (symlinks, submodules, mirrors) is fresh.

## Discover subskills

```bash
PKG="$(dirname "<absolute-path-to-this-SKILL.md>")"
find "$PKG/subskills" -maxdepth 2 -name SKILL.md
rg -n "^name:|^description:" "$PKG"/subskills/*/SKILL.md
```

## Routing table

| Task intent | Subskill | Typical trigger |
|---|---|---|
| Measure real skill usage from Claude Code / Codex transcripts; recommend archiving non-new skills with no real usage in the window. | [subskills/audit-skill-hygiene/SKILL.md](subskills/audit-skill-hygiene/SKILL.md) | "audit my skills", "which skills are unused", "frontmatter is bloating my context" |
| Review dotfiles (rc files, aliases, env, tool config) for conflicts, dead config, and best practices — without touching secret files. | [subskills/dotfiles-review/SKILL.md](subskills/dotfiles-review/SKILL.md) | "review my dotfiles", "clean up my zshrc", "are my aliases conflicting" |
| Re-run every snapshot/mirror flow so installed state matches source: skill symlinks, git submodules, plugin updates. Also hosts the read-only harness doctor (all verify checks, no refresh). | [subskills/refresh-snapshots/SKILL.md](subskills/refresh-snapshots/SKILL.md) | "refresh snapshots", "update submodules", "relink skills", "is my harness healthy" |
| Disk retention for session transcripts and tool logs: inventory, age-tiered compress/delete policy, audit-window trade-off. | [subskills/transcript-retention/SKILL.md](subskills/transcript-retention/SKILL.md) | "transcripts eating disk", "clean up old sessions" |
| Compact append-only agent memory: AGENTS.md notes-to-self, bd memories — dedupe, merge superseded, retire orphans, keep guardrails. | [subskills/memory-hygiene/SKILL.md](subskills/memory-hygiene/SKILL.md) | "AGENTS.md is huge", "compact my notes", "stale memories" |
| Audit non-skill context surfaces: MCP servers, permission allowlists, hooks — configured vs. actually used in transcripts. | [subskills/config-surface-audit/SKILL.md](subskills/config-surface-audit/SKILL.md) | "audit my MCP servers", "stale permissions", "config bloat" |

## Routing rules

- **Measure vs. act**: "what is unused / what should go" → audit-skill-hygiene.
  Actually moving skills to `skills/archive/` is part of that subskill's
  output contract; the move itself needs no other subskill.
- **Config content vs. installed state**: questions about what the dotfiles
  *say* (aliases, exports, rc files) → dotfiles-review; questions about
  whether what's *installed* matches the repo (links, submodules, mirrors) →
  refresh-snapshots.
- **Full hygiene pass**: run all three as parallel subagents, each given the
  absolute path to its `subskills/<name>/SKILL.md`, the scope, and an output
  contract of findings + proposed commands. Synthesize before acting.
- **Fallback**: harness-adjacent but no row fits (e.g. authoring a new skill
  → `/th-engineering` skill-standards; bootstrap.sh logic changes → plain
  engineering work). Do not load a subskill to browse.

## Shared invariants (all subskills)

- Recommendations over silent action: archive moves, dotfile edits, and
  submodule advances are proposed with evidence (counts, file:line, command
  output) before being applied.
- Never read or quote secret material: anything gitignored, under
  `credentials/`, or in `to_source/machine_specific` / `to_source/passwords`
  is out of bounds (verify with `git check-ignore` when unsure).
- Non-destructive by default: prefer `skills/archive/` moves and idempotent
  re-runs over deletion; everything must be restorable with one `git mv` or
  one bootstrap re-run.
