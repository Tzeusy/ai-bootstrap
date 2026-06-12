# Beads CLI Known Errors

Living catalog of `bd` errors, deprecations, and workarounds. This file is the
superskill's own memory: it is symlinked into every tool home, so an entry
written once is available to every future agent session.

## Maintenance contract (read this first)

When you hit a `bd` error or rough edge that is NOT already listed here:

1. Resolve or circumvent it.
2. **Append an entry below in the same format** (symptom verbatim, cause,
   fix/workaround, date observed, bd version from `bd version`).
3. Prune entries that a later bd release fixes — note the fixed version
   instead of silently deleting, then drop the entry one revision later.

Do not skip step 2 because the fix felt obvious. The next agent pays the
debugging cost again unless it lands here.

## Connectivity / server

### Cannot connect to Dolt server (Gastown rigs)
- **Symptom**: `bd` commands fail with connection-refused / "no local beads
  server" style errors in repos whose beads run off the shared Gastown Dolt
  server.
- **Cause**: the Gastown Dolt sql-server (listening on `localhost:3307`,
  config `~/gt/.dolt-data/config.yaml`) is down.
- **Fix**: `gt dolt start`, then retry. Verify with
  `ss -tlnp | grep 3307`.
- **Note**: not every repo uses the server — some run embedded
  (`bd dolt status` says `Dolt engine: embedded`). Embedded repos are
  unaffected by the server being down.
- Observed: 2026-06-12, bd 1.0.4.

## Deprecated / removed commands and flags

Deprecations land without much warning between releases. When a documented
command errors with `unknown flag` or `unknown command`, check
`bd <subcommand> --help` and `bd upgrade review` (release history) before
assuming breakage, then record the rename here AND fix the subskill docs.

### `--rig <rig>` flag removed (≤1.0.3 → 1.0.4)
- **Symptom**: `Error: unknown flag: --rig` on `bd ready`/`bd list`/`bd create`.
- **Fix**: use the global `-C <path>` flag instead:
  `bd -C /path/to/rig list --status=open`. ID-prefixed commands
  (`bd update/close/show/dep`) auto-route without `-C`.
- Observed: 2026-06-12, bd 1.0.4.

## Database / config state

### `database not initialized: issue_prefix config is missing`
- **Symptom**: mutations (`bd create`, `bd update`) fail with this error while
  reads (`bd ready`, `bd list`, `bd stats`) may still work. `bd bootstrap`
  says "Database already exists: Nothing to do" and `bd init --prefix X`
  aborts because the DB exists. `bd config set issue_prefix` is refused.
- **Cause**: DB directory exists but its config lost/never had `issue_prefix`
  (seen after version upgrades).
- **Fix**: back up first (`bd export > /tmp/backup.jsonl` — though it exports
  0 issues if the DB is empty), then `bd init --reinit-local --prefix <prefix>`
  and re-import data (see next entry). Note bd may normalize the prefix
  (`.dotfiles` became `dotfiles`).
- Observed: 2026-06-12, bd 1.0.4.

### Auto-export daemon overwrites `.beads/issues.jsonl` within seconds
- **Symptom**: you restore a historical `issues.jsonl` (e.g. from git) to
  re-import it, but by the time `bd import` runs the file holds only the
  current (possibly empty) DB state.
- **Fix**: never import via the working-tree file; pipe from git instead:
  `git show <ref>:.beads/issues.jsonl | bd import -`.
- **Related**: commit hooks that run `bd export` can stage a deletion or
  truncation of `issues.jsonl` into an unrelated commit when the DB is
  empty/broken. Inspect `git show --stat` after committing; use
  `--no-verify` while the DB is being repaired.
- Observed: 2026-06-12, bd 1.0.4.

### `bd import` → `Error: commit: dolt commit: Error 1105: nothing to commit`
- **Symptom**: import errors (and dumps full flag usage) even though nothing
  is wrong — the import simply produced no DB change.
- **Workaround**: treat as success-with-no-op; verify with `bd stats` or
  `bd import --dry-run <file>` rather than trusting the exit status.
- Observed: 2026-06-12, bd 1.0.4.

## Environment

### `no beads database found` inside a nested git repository
- **Symptom**: every `bd` command fails with `Error: no beads database found`
  (and `bd where` reports no active workspace) even though a parent directory
  has a healthy `.beads/`.
- **Cause**: bd's database discovery walks up from `$PWD` but stops at the
  enclosing git repository boundary. A nested repo (e.g. a submodule or a
  repo-within-a-repo) without its own `.beads/` cannot see the parent's DB.
  Session hooks keyed on `.beads/` detection also do not fire there.
- **Fix**: either give the nested repo its own DB (`bd init --prefix <p>` —
  done for `ai-bootstrap` on 2026-06-12, prefix `aib`), or prefix commands
  with the global directory flag: `bd -C /path/to/parent <command>`.
- **This workspace**: `~/.dotfiles` uses prefix `dotfiles` (shell/dotfiles
  work); `~/.dotfiles/ai-bootstrap` uses prefix `aib` (skill/agent work).
  **ID-prefix auto-routing does NOT work across these embedded DBs**
  (verified: `bd show dotfiles-ac7` from ai-bootstrap fails) — always use
  `bd -C <repo>` when addressing the other repo's beads.
- Observed: 2026-06-12, bd 1.0.4.

### Stale duplicate `bd` binary on PATH
- **Symptom**: `bd version` warns about multiple binaries; behavior differs
  between shells/worktrees.
- **Cause**: an old dev build (e.g. `~/go/bin/bd`) shadowed by the real one
  (`~/.local/bin/bd`) — PATH-order dependent.
- **Fix**: `which -a bd`, delete or rebuild the stale binary.
- Observed: 2026-06-12 (`~/go/bin/bd` was v1.0.0-dev vs installed 1.0.4).

## State-transition quirks

Some lifecycle transitions error even though the end state is legitimate.
When a direct `bd update <id> --status <to>` is rejected:

- Try routing through an intermediate state
  (e.g. `blocked → open → in_progress` instead of `blocked → in_progress`),
  or `bd close` + reopen (`bd update <id> --status open`) when the guard is
  on the closed path.
- If a transition only fails with extra flags combined, split into two
  `bd update` calls (status first, then labels/notes).
- Record the exact rejected transition and the route that worked as a new
  entry here.

(No concrete rejected-transition entry yet — add the first one you hit.)

## Other quirks

### `bd edit` blocks agents
`bd edit` opens `$EDITOR` interactively. Never run it from an agent; use
`bd update <id> --title/--description/--notes/--design` instead.

### `bd doctor` unsupported in embedded mode
`bd doctor` is server-mode only; in embedded repos it prints manual
troubleshooting steps instead. Use `bd dolt status`, `bd version`, and
`ls .beads/embeddeddolt/` for embedded diagnostics.
