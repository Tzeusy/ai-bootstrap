---
name: config-surface-audit
description: >
  Use to audit the non-skill recurring context surfaces of the AI tools —
  configured MCP servers (tool schemas load every session), permission
  allowlists, and hooks in settings.json / config.toml — against actual
  usage from transcripts, and recommend removing what never fires.
  Triggers: "audit my MCP servers", "are these permissions stale", "what
  hooks do I have", "config bloat".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
compatibility: Reads ~/.claude settings/transcripts and ~/.codex/config.toml; jq helpful but optional.
---

# Config Surface Audit

Skill frontmatter is not the only recurring context cost. Every configured
MCP server injects its tool schemas, every hook runs on its event, and
permission allowlists grow monotonically as one-off grants accumulate.
Same discipline as [../audit-skill-hygiene/SKILL.md](../audit-skill-hygiene/SKILL.md):
measure configured-vs-used from transcripts, recommend removals with
evidence, let the user decide.

## Inventory the configured surface

```bash
# Claude Code: global + project settings (NOT settings.local.json if gitignored — check first)
jq '{mcpServers: (.mcpServers // {} | keys), hooks: (.hooks // {} | keys), permissions: (.permissions.allow // [] | length)}' \
  ~/.claude/settings.json 2>/dev/null
cat ~/.claude.json 2>/dev/null | jq '.mcpServers | keys' 2>/dev/null
# Codex
grep -E '^\[mcp_servers\.' ~/.codex/config.toml 2>/dev/null
```

Also list plugin marketplaces (`~/.claude/plugins/`) — installed plugins
carry their own skills/commands into context.

## Measure actual use from transcripts

MCP tool calls are grep-able by their canonical names:

```bash
LC_ALL=C grep -rhoE '"name":"mcp__[a-zA-Z0-9_]+__' ~/.claude/projects --include="*.jsonl" \
  | sort | uniq -c | sort -rn
```

A configured server with zero `mcp__<server>__*` calls over the window is a
removal candidate. For hooks, check the hook's own side effects or log
lines; for permissions, sample which allow rules actually match recent tool
calls (rule prefix vs. `"name":"Bash"` command strings).

## Recommend, with the same caveats as skill audits

- Window vs. retention: a zero may mean "rarely needed", not "never" —
  report the window alongside the verdict.
- Some servers are seasonal (e.g. a calendar MCP used monthly); 1–2 uses is
  a keep-lean signal, not a delete order.
- Permission rules are cheap individually; recommend pruning only clearly
  dead ones (referencing removed tools/paths) rather than micro-optimizing.

## Hard stops

- Config files may embed tokens or URLs with credentials — never quote
  secret values into reports; reference keys by name only.
- Do not edit `settings.json`/`config.toml` without showing the exact diff
  first; a wrong hook or permission edit changes harness behavior for every
  future session.
- Removing an MCP server that an active workflow depends on breaks it
  silently — search the skills tree for references to the server name
  before recommending removal (`rg -l "mcp__<server>" skills/`).
