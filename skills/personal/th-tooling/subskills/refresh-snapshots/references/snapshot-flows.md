# Snapshot Flows Catalog

## Maintenance contract (read this first)

This is living state, not static guidance. When normal use surfaces a new
snapshot flow (any script or step that copies/links version-controlled
content into a runtime location), **append it here in the same change**.
When a flow's command or verification changes, update its entry. When a
flow is removed from the harness, note the removing commit and drop the
entry one revision later. Each entry records: what is snapshotted, refresh
command, verification, and last-verified date.

## 1. Skill symlinks into tool homes

- **Snapshot**: `ai-bootstrap/{.claude,.codex,.gemini,.gemini/antigravity}/skills/*`
  symlinks, generated from `ai-bootstrap/skills/` discovery.
- **Source**: `~/.dotfiles/bootstrap.sh` ("Linking shared AI skills"
  section). Discovery prunes `subskills/` (superskills install as one
  catalog entry) and `archive/` (retired skills stay cloned but unlinked).
  Stale-removal only touches managed links — symlinks into
  `ai-bootstrap/skills/` or broken links; manual links (e.g. `impeccable`
  → `~/.agents/skills/`) are preserved.
- **Refresh**: `~/.dotfiles/bootstrap.sh` (full run is idempotent; the
  skills section alone can be extracted for a fast pass).
- **Verify**: no broken links and no archived names linked:

  ```bash
  find ~/.dotfiles/ai-bootstrap/.codex/skills ~/.dotfiles/ai-bootstrap/.gemini/skills \
       ~/.dotfiles/ai-bootstrap/.gemini/antigravity/skills ~/.dotfiles/ai-bootstrap/.claude/skills \
       -maxdepth 1 -xtype l
  ```

- **Last verified**: 2026-06-12

## 2. Git submodules

- **Snapshot**: submodule checkouts pinned to recorded pointers —
  `~/.dotfiles` records `ai-bootstrap`; `ai-bootstrap` records skill
  submodules (see its `.gitmodules`; archived ones live under
  `skills/archive/`) and `.claude/plugins/marketplaces/`.
- **Refresh** (to recorded pointer — safe):
  `git submodule update --init --recursive` in each repo.
- **Advance** (moves pointers):
  `git submodule update --remote <path>`, then commit the bump; in
  `~/.dotfiles` use the `Update ai-bootstrap pointer` message convention.
  Note: a full `bootstrap.sh` run advances all dotfiles submodules
  (`--remote` in its "Git Submodules" section) — a full bootstrap is a
  pointer-advancing operation, not just a restore.
- **Verify**: `git submodule status --recursive` shows no `-` (missing) or
  `+` (drifted from recorded pointer) prefixes you did not just create.
- **Last verified**: 2026-06-12

## 3. oh-my-zsh and custom plugin clones

- **Snapshot**: `~/.oh-my-zsh` framework plus custom plugin clones
  (`zsh-autosuggestions`, `zsh-syntax-highlighting` under
  `~/.oh-my-zsh/custom/plugins/`), installed by `bootstrap.sh` but updated
  out-of-band.
- **Refresh**: `omz update` (or `git -C ~/.oh-my-zsh pull`), then
  `git -C ~/.oh-my-zsh/custom/plugins/<p> pull` per plugin.
- **Verify**: `zsh -ic exit` loads cleanly.
- **Last verified**: 2026-06-12

## 4. Beads issue export

- **Snapshot**: `.beads/issues.jsonl` (passive export of the Dolt DB,
  regenerated automatically on `bd` writes; gitignored in these repos).
- **Refresh**: automatic; remote sync via `bd dolt push` / `bd dolt pull`.
- **Verify**: `bd doctor`.
- **Last verified**: 2026-06-12
