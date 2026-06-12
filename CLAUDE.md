# Project Instructions for AI Agents

This file provides instructions and context for AI coding agents working on this project.

<!-- BEGIN BEADS INTEGRATION v:1 profile:minimal hash:7510c1e2 -->
## Beads Issue Tracker

This project uses **bd (beads)** for issue tracking. Run `bd prime` to see full workflow context and commands.

### Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work
bd close <id>         # Complete work
```

### Rules

- Use `bd` for ALL task tracking — do NOT use TodoWrite, TaskCreate, or markdown TODO lists
- Run `bd prime` for detailed command reference and session close protocol
- Use `bd remember` for persistent knowledge — do NOT use MEMORY.md files

**Architecture in one line:** issues live in a local Dolt DB; sync uses `refs/dolt/data` on your git remote; `.beads/issues.jsonl` is a passive export. See https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md for details and anti-patterns.

## Session Completion

**When ending a work session**, you MUST complete ALL steps below. Work is NOT complete until `git push` succeeds.

**MANDATORY WORKFLOW:**

1. **File issues for remaining work** - Create issues for anything that needs follow-up
2. **Run quality gates** (if code changed) - Tests, linters, builds
3. **Update issue status** - Close finished work, update in-progress items
4. **PUSH TO REMOTE** - This is MANDATORY:
   ```bash
   git pull --rebase
   git push
   git status  # MUST show "up to date with origin"
   ```
5. **Clean up** - Clear stashes, prune remote branches
6. **Verify** - All changes committed AND pushed
7. **Hand off** - Provide context for next session

**CRITICAL RULES:**
- Work is NOT complete until `git push` succeeds
- NEVER stop before pushing - that leaves work stranded locally
- NEVER say "ready to push when you are" - YOU must push
- If push fails, resolve and retry until it succeeds
<!-- END BEADS INTEGRATION -->


## Beads Database Topology

This repo has its **own** beads DB (prefix `aib-`) because bd discovery stops
at the git-repo boundary — sessions here cannot see the parent
`~/.dotfiles/.beads` (prefix `dotfiles-`). Use the `aib` DB for skill/agent
work; address the parent's beads explicitly with `bd -C ~/.dotfiles <cmd>`.
ID-prefix auto-routing across these embedded DBs does NOT work. Known bd
errors and workarounds are cataloged in
`skills/personal/beads-orchestration/references/known-errors.md` — append new
rough edges there after resolving them.

## Build & Test

There is no repo-wide build. Skill packages with tests carry them in
`<skill>/tests/`; run them with:

```bash
python3 -m pytest skills/personal/beads-orchestration/subskills/*/tests/ --import-mode=importlib -q
```

Symlinks into tool homes (`~/.claude/skills` etc.) are managed by the parent
repo's `bootstrap.sh`, which prunes `subskills/` so superskills install as one
catalog entry.

## Project Shape Navigation

The five-pillar shape docs live under `about/` and `openspec/`;
`about/README.md` is the reading-order index and each pillar's `README.md`
routes within that pillar. There are no catalog skills for them — this repo's
`.claude/skills` doubles as the user's global `~/.claude/skills`, so
repo-specific skills would leak into every session. Before structural,
placement, or quality-bar decisions here, start from `about/README.md` (or
the relevant pillar README) and follow its routing. Reading
`about/craft-and-care/` is mandatory for non-trivial changes.

## Architecture Overview

Skills-first (see README.md). Canonical skills live in `skills/`;
`skills/personal/` is the user-maintained layer, everything else is
upstream-derived (submodules or vendored). Superskills (`beads-orchestration`,
`th-projects`, `th-engineering`) are router `SKILL.md` + `subskills/` packages;
only the router enters the global catalog. `agents/` is legacy/reference.

## Conventions & Patterns

- Follow `skills/personal/th-engineering/subskills/skill-standards/` when
  creating or updating skills (trigger quality, routing, context efficiency).
- Keep `SKILL.md` a thin router; detailed guidance goes in `references/`,
  helpers in `scripts/` (PEP 723 headers for Python).
- Update doctrine worth remembering in the parent repo's `AGENTS.md`
  "Notes to self" at session end.
