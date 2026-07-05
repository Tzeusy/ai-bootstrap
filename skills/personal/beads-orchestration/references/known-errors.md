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
- **Fix**: either give the nested repo its own DB (`bd init --prefix <p>`), or
  prefix commands with the global directory flag: `bd -C /path/to/parent
  <command>`.
- **This workspace**: `~/.dotfiles` → DB `dotfiles` (prefix `dotfiles-`,
  shell/dotfiles work); `~/.dotfiles/ai-bootstrap` → DB `aib` (prefix `aib-`,
  skill/agent work). Both now live on the **shared external Dolt server**
  (`127.0.0.1:3307`, `~/gt/.dolt-data`) as per-project databases — migrated
  from per-repo embedded Dolt on 2026-06-17. Repo→DB selection is still
  per-`.beads/`, so **ID-prefix auto-routing does NOT work across them**
  (`bd show dotfiles-ac7` from ai-bootstrap fails) — always use `bd -C <repo>`
  when addressing the other repo's beads.
- Observed: 2026-06-12, updated 2026-06-17, bd 1.0.4.

### Migrating a repo from embedded Dolt to the shared external server
- **Goal**: move an embedded-mode repo's beads onto the shared 3307 server as
  its own per-project DB (keeps all repos on one server, data still isolated).
- **Steps**: (1) `bd export` to refresh `.beads/issues.jsonl` AND tar the whole
  `.beads/` aside as a backup; (2) create the target DB:
  `mysql -h127.0.0.1 -P3307 -uroot --ssl-mode=DISABLED -e "CREATE DATABASE <db>;"`;
  (3) re-init in external-server mode importing from JSONL:
  `BEADS_DOLT_PASSWORD= bd init --server --external --server-host 127.0.0.1
  --server-port 3307 --server-user root --database <db> --prefix <prefix>
  --from-jsonl --reinit-local --non-interactive --destroy-token DESTROY-<prefix>
  --skip-agents --skip-hooks`; (4) verify counts server-side
  (`SELECT COUNT(*) FROM issues;`) match the export; (5) persist connection to
  tracked config: `bd dolt set host/port/database <v> --update-config`;
  (6) delete the orphaned `.beads/embeddeddolt` only after `metadata.json`
  shows `"dolt_mode": "server"`.
- **Gotchas**: `--prefix` defaults to the *directory name* on re-init — pass it
  explicitly or `ai-bootstrap` becomes prefix `ai-bootstrap`, not `aib`.
  Non-interactive re-init refuses without `--destroy-token DESTROY-<prefix>`
  (the JSONL is the import source, so this is safe with a backup). Do NOT use
  `--shared-server` — that points at bd's *own* managed server
  (`~/.beads/shared-server/`), not the existing `~/gt/.dolt-data` one; use
  `--server --external`. Root has no password → `BEADS_DOLT_PASSWORD=` (empty).
- Observed: 2026-06-17, bd 1.0.4.

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

- **Claiming a blocked bead** (`bd update <id> --claim` on a `pr-review-task`
  or any `status=blocked` bead): fails with `Error claiming <id>: issue not
  claimable: status blocked` (exit 0, no mutation). `--claim` only accepts
  `open`/`in_progress`. WORKAROUND: route through open first —
  `bd update <id> --status open` then `bd update <id> --claim`. Note a
  same-call `--claim --add-label X` will silently apply the label but skip the
  claim; verify `assignee` after. Observed 2026-06-13, bd 1.0.4 (the
  coordinator review-lane dispatch hits this every cycle).
- **Force-closing a bead with open logical deps**: `bd close <id>` fails with
  `cannot close <id>: blocked by open issues [<dep>] (use --force to override)`.
  When the deliverable is confirmed merged (PR MERGED) but a logical-ordering
  dep is still open, `bd close <id> --force --reason "..."` is correct.
  Observed 2026-06-13 (hud-bq0gl.2: PR #765 merged out-of-order ahead of its
  dep hud-bq0gl.1).

## Other quirks

### `bd edit` blocks agents
`bd edit` opens `$EDITOR` interactively. Never run it from an agent; use
`bd update <id> --title/--description/--notes/--design` instead.

### `bd create --json` returns a plain object, not an array
`bd create --json` emits a single object → extract the id with `jq -r '.id'`.
By contrast `bd show --json` and `bd update --json` emit an ARRAY → use
`jq -r '.[0].id'`. The defensive `jq -r '.id // .[0].id'` works for both;
`.[0].id // .id` does NOT (it throws `Cannot index object with number` on the
create object). Observed 2026-06-13, bd 1.0.4.

### Epic→task linkage: `bd dep add` rejects it; use `--parent`
- **Symptom**: wiring an epic to its child tasks with
  `bd dep add <epic> <task>` fails: `Error: epics can only block other epics,
  not tasks`.
- **Cause**: epic membership is a parent-child relation, not a `blocks` edge.
- **Fix**: `bd update <task> --parent <epic>` per child (the epic's `bd show`
  then renders a CHILDREN tree with completion %). Reserve `bd dep add` (type
  `blocks`, default) for genuine ordering between tasks.
- Observed: 2026-06-17, bd 1.0.4.

### `bd doctor` unsupported in embedded mode
`bd doctor` is server-mode only; in embedded repos it prints manual
troubleshooting steps instead. Use `bd dolt status`, `bd version`, and
`ls .beads/embeddeddolt/` for embedded diagnostics.

### bd WRITE path silently reverts; jsonl auto-import clobbers committed state (post-3307-migration)
- **Symptom**: `bd update`/`bd close`/`bd update --claim` print `✓ Updated`/
  `✓ Closed` (exit 0) but the change does NOT persist — a later `bd show`/`bd
  ready` shows the bead back at its prior state. Every `bd` call logs
  `auto-importing N bytes from issues.jsonl into empty database`. Under
  concurrent worker `bd` reads it is worse: even a direct
  `mysql … UPDATE … ; CALL DOLT_COMMIT()` to the server gets reverted by the
  next `bd` read.
- **Diagnosis** (aib repo, 2026-06-17, bd 1.0.4): `bd dolt show`/`bd dolt test`
  report the 3307 connection OK and `bd show` DOES read server state (write a
  sentinel via mysql+`DOLT_COMMIT` → `bd show` sees it). But each `bd`
  invocation auto-imports the working-tree `issues.jsonl` and commits it over
  server `main`. When that jsonl is stale (auto-export had failed its `git add`
  on the gitignored `.beads`, and/or the 60s `export.interval` throttle), the
  import REVERTS recent mutations. So jsonl is the de-facto source of truth and
  bd's own write→export→reimport cycle loses writes. `bd dolt show` reports
  `Mode: per-project` (bd wants to run its OWN server from data-dir
  `.beads/dolt`) while the external shared server already holds 3307 → split
  brain.
- **Reliable workaround** (kept a coordinator loop running across 11 closures):
  treat `issues.jsonl` as the store. Mutate by editing it directly, then `bd
  stats >/dev/null` once to propagate jsonl→server. READS (`bd ready`/`bd
  show`) are fine. Avoid `bd create`/`bd dep` (need synthesized records); use
  inline coordinator PR review instead of separate review beads. Also set `bd
  config set export.git-add false` and `export.interval 0` so exports stop
  aborting/throttling.
- **Real fix (TODO, needs human)**: properly establish external-server mode so
  bd stops auto-importing jsonl — re-init per the "Migrating … to the shared
  external server" entry above (`bd init --server --external … --from-jsonl
  --reinit-local`), then remove the orphaned `.beads/dolt` per-project data-dir
  once `metadata.json` shows server mode. Until then, bd writes are unsafe.
- Observed: 2026-06-17, bd 1.0.4.

### `bd worktree remove` may rewrite `.gitignore` comments
- **Symptom**: after removing a worktree through `bd worktree remove`,
  `.gitignore` is modified even though the removed worktree path is gone; in
  observed cases, explanatory `# bd worktree` comments around ignored historical
  worktree paths were stripped.
- **Cause**: the helper rewrites the worktree ignore block instead of preserving
  surrounding comments byte-for-byte.
- **Workaround**: for cleanup of Rust/code worktrees that were created with
  `git worktree add`, prefer plain `git worktree remove <path>` plus explicit
  `git branch -D agent/<id>` and remote-branch cleanup after bead closure. If
  `bd worktree remove` was already used, inspect `git diff -- .gitignore` and
  restore comment-only churn unless the ignore entries themselves changed.
- Observed: 2026-06-18, bd 1.0.4.

## resolve_review_context.py: `missing-original-id` on freeform review-bead descriptions

The pr-reviewer-worker helper `resolve_review_context.py` only recognizes the
markers `Original implementation bead:` / `Review target bead:` in the review
bead's description. A coordinator-authored description using freeform phrasing
like `Original bead: bu-xxxxx` fails with `missing-original-id` even though the
mapping is unambiguous (observed 2026-07-05, review bead bu-mm41k). Workaround:
reviewer falls back to the ORIGINAL_BEAD value in its dispatch prompt +
`gh pr view`. Durable fix: coordinators should write
`Original implementation bead: <id>` verbatim in review-bead descriptions.
