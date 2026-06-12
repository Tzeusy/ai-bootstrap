---
name: audit-skill-hygiene
description: >
  Use to measure which installed skills are actually used, from Claude Code
  and Codex session transcripts, and to recommend archiving the ones that
  are not. Produces per-skill invocation counts over a window (default 30
  days), exempts newly added skills, and emits ready-to-run git mv commands
  into skills/archive/. Triggers: "audit skill usage", "which skills are
  unused", "what skills can I remove", "skill frontmatter is bloating my
  context".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
compatibility: Requires uv (Python 3.9+); reads ~/.claude/projects and ~/.codex/sessions transcripts and runs git inside the skills repo.
---

# Audit Skill Hygiene

Every installed skill's frontmatter is loaded into the catalog of **every**
session, so an unused skill has a recurring context cost. This subskill
measures real usage and recommends moving dead weight to `skills/archive/`,
which `~/.dotfiles/bootstrap.sh` prunes from discovery — non-destructive and
reversible with one `git mv`.

## Workflow

1. Run the audit script
   [`scripts/skill_usage_audit.py`](./scripts/skill_usage_audit.py):

   ```bash
   uv run <this-subskill>/scripts/skill_usage_audit.py            # 30-day window
   uv run <this-subskill>/scripts/skill_usage_audit.py --since-days 90 --json
   ```

   It inventories installed skills (mirroring bootstrap.sh's discovery,
   including its `subskills`/`archive` prunes), counts real invocations, and
   prints used/unused/new tables plus `git mv` recommendations — each with
   its estimated per-session catalog token cost, so recommendations rank by
   tokens reclaimed. It also warns on duplicate skill names (two dirs, one
   name): link resolution is filesystem-order, so duplicates are a latent
   bug — archive or delete the shadowed copy.

2. Interpret with the known measurement caveats (below). Spot-check any
   surprising "unused" verdict by grepping a transcript before recommending
   removal.

3. Present the recommendation list to the user — archiving is their call.
   On approval, run the emitted `git mv` commands inside the skills repo,
   re-run the linking flow (see
   [../refresh-snapshots/SKILL.md](../refresh-snapshots/SKILL.md)), and
   verify the archived names left the tool homes and no broken links remain.

## What counts as real usage

- **Claude Code**: `Skill` tool calls (`"name":"Skill"` with an `input.skill`
  value) and `<command-name>` slash invocations in
  `~/.claude/projects/**/*.jsonl`.
- **Codex**: SKILL.md paths appearing inside `"type":"function_call"`
  records in `~/.codex/sessions/**/*.jsonl` — i.e. the agent actually read
  the skill file.
- Subskill usage attributes to its parent superskill (a superskill whose
  subskills are heavily used is heavily used).

## Measurement caveats (read before trusting a zero)

- **Catalog noise**: every skill's name and path appear in every session's
  injected catalog. Never count raw mentions; the script only counts the
  structured invocation forms above.
- **Window vs. retention**: "unused" means "no recorded use in the window or
  available transcript history, whichever is shorter". Check the script's
  reported earliest-transcript date before claiming "never used".
- **New skills**: a skill added to git within the window has had no chance
  to accumulate usage; the script marks it `new` and exempts it.
- **Marginal counts**: 1–2 uses may be the skill being *edited or tested*,
  not used. Inspect before archiving, and lean toward keeping.
- **Submodule-nested skills**: skills living inside vendored submodules
  (e.g. `mattpocock-skills`) cannot be dated or `git mv`'d from this repo,
  so the script exempts them instead of recommending a move. Retiring one
  means archiving its whole umbrella submodule.

## Hard stops

- Do not delete skill directories or submodule entries; archive only.
- Do not archive a skill the user added within the window, whatever the
  count says.
- Transcripts may contain sensitive session content — extract only skill
  names and counts from them, never quote transcript bodies into reports.
