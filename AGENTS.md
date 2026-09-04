# Agent Instructions

This project uses **bd** (beads) for issue tracking. Run `bd prime` for full workflow context.

> **Architecture in one line:** Issues live in a local Dolt database
> (`.beads/dolt/`); cross-machine sync uses `bd dolt push/pull` (a
> git-compatible protocol), stored under `refs/dolt/data` on your git
> remote — separate from `refs/heads/*` where your code lives.
> `.beads/issues.jsonl` is a passive export, not the wire protocol.
>
> See [SYNC_CONCEPTS.md](https://github.com/gastownhall/beads/blob/main/docs/SYNC_CONCEPTS.md)
> for the one-screen overview and anti-patterns (don't treat JSONL as the
> source of truth; don't `bd import` during normal operation; don't
> reach for third-party Dolt hosting before trying the default).

## Quick Reference

```bash
bd ready              # Find available work
bd show <id>          # View issue details
bd update <id> --claim  # Claim work atomically
bd close <id>         # Complete work
bd dolt push          # Push beads data to remote
```

## Non-Interactive Shell Commands

**ALWAYS use non-interactive flags** with file operations to avoid hanging on confirmation prompts.

Shell commands like `cp`, `mv`, and `rm` may be aliased to include `-i` (interactive) mode on some systems, causing the agent to hang indefinitely waiting for y/n input.

**Use these forms instead:**
```bash
# Force overwrite without prompting
cp -f source dest           # NOT: cp source dest
mv -f source dest           # NOT: mv source dest
rm -f file                  # NOT: rm file

# For recursive operations
rm -rf directory            # NOT: rm -r directory
cp -rf source dest          # NOT: cp -r source dest
```

**Other commands that may prompt:**
- `scp` - use `-o BatchMode=yes` for non-interactive
- `ssh` - use `-o BatchMode=yes` to fail instead of prompting
- `apt-get` - use `-y` flag
- `brew` - use `HOMEBREW_NO_AUTO_UPDATE=1` env var

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

## Project Shape Navigation

The five-pillar shape docs live under `about/` and `openspec/`;
`about/README.md` is the reading-order index and each pillar's `README.md`
routes within that pillar. They are deliberately not exposed as catalog
skills — the tool skill surfaces double as the user's global catalogs on
installed machines. Before structural, placement, or quality-bar decisions
here, start from `about/README.md` (or the relevant pillar README) and follow
its routing. Reading `about/craft-and-care/` is mandatory for non-trivial
changes.

# Notes to self

- Before dispatching a baseline-pinned ready bead, verify its governing paths still exist on current `main` and reconcile prior merged PRs plus later history; a stale ready record may describe work that was completed and then deliberately removed, and must not resurrect that surface.
- Global skill catalog is 8 routers (`beads-orchestration`, `bws-cli-skill`, six `th-*`); every description loads into every session, so a new capability joins an existing superskill as a subskill before it earns a top-level entry. `skills/personal/th-workflow/` (fork of `obra/superpowers`) and `th-engineering/subskills/skill-creator/` (fork of `anthropics/skills`) replaced seven standalone entries on 2026-09-02; unused `doc-coauthoring` sits in `skills/archive/`.
- `skills/.system/` is a Codex-managed system-skill mirror; `scripts/link-ai-skills.sh` and `~/.dotfiles/bootstrap.sh` prune it from discovery. Without that prune, deleting a same-named top-level skill lets the `.system` copy leak into the Claude/Gemini catalogs.
- `beads-orchestration` keeps every numeric policy (stall TTL, wake cadence 4m50s / 60 min / 3 no-op wakes, model tables) canonical in `beads-coordinator/references/runtime-and-safety.md`; other files point, never restate. Its `subskills/*/tests/test_*contract*.py` pin doc *wording* (`assertIn` on phrases), so moving doctrine between files (e.g. the normalizer's fail-closed rules now live in the script docstring) means updating those tests in the same change, not loosening the docs.
- Oversized subskills (`beads-pr-reviewer-worker` 499 lines against the audit's hard 500 cap, counted as newlines+1, `beads-worker` 323, `blogpost-editor` 259, `project-direction`/`project-shape` ~250) exceed the 150-line guideline but run linearly, so fanning them into `references/` saves little; revisit only if a conditional slice (e.g. beads-worker handoff paths) grows.
- Merge-flow doctrine (2026-09-04): `prepare_pr_branch.py` rebases only on a `git merge-tree --write-tree` conflict (or `--force-rebase`); a clean PR head is reviewed and merged as-is. When the base has a GitHub merge-queue ruleset (`MERGE_QUEUE=yes` in coordinator preflight) merges go through `gh pr merge --squash --auto`, the reviewer reports `merge-queued`, and the coordinator opens `queue-direct` PRs instead of fast-forwarding `main`. Never `--admin`.
- Test-growth governance for the autonomous lane lives in `beads-orchestration/references/test-growth-gate.md` (one gate species per behavior, `Tests: +a ~b -c` delta line, repo test-budget ratchet); beads-writer/th-projects/th-workflow all point at it rather than restating.
