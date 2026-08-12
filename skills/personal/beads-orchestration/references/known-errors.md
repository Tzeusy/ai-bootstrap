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
- **Claiming an already-`in_progress` bead with an empty assignee**:
  `bd update <id> --claim` fails with `Error claiming <id>: issue not
  claimable: status in_progress`. This occurs when older coordinator state
  left the lifecycle status without an assignee. WORKAROUND: after confirming
  no live worker owns the bead, route `in_progress -> open -> --claim`, verify
  the new assignee, then apply the intended terminal status/metadata in a
  separate update. Observed 2026-07-13, bd 1.0.4.
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

### A `|| bd create …` jq-fallback creates a DUPLICATE bead
- **Symptom**: one reconciliation ran `bd create … --json | jq -r '…' || bd
  create … 2>&1 | tail`, and a later `bd ready` showed TWO identical review
  beads (bu-foon5 + bu-63tvy) with the SAME `created_at` second and identical
  descriptions. Observed 2026-07-24, bd 1.0.x.
- **Cause**: `bd create` also prints a human `✓ Created issue: …` line, and
  `bd create --json` output can carry control characters that make the piped
  `jq` exit non-zero EVEN THOUGH the create already committed to Dolt. The `||`
  then re-runs `bd create`, minting a second bead. This is the create-side twin
  of the "jq parse error but the write still landed" race.
- **Fix**: NEVER chain `bd create` with a `|| bd create` (or any `||` that
  re-invokes a mutating command). Run the create exactly once; write long
  `--description` to a file and pass `--description="$(cat file)"`; read the
  new id from the plain `✓ Created issue: <id>` line (or a separate `bd list`),
  not from a jq-or-retry. If a duplicate slips through, the coordinator closes
  the unclaimed twin with `bd close <dup> --reason "Duplicate of <canonical>"`.
  Related: control-character jq breakage at "zsh `echo` can corrupt compact
  `bd --json`" below.

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
- **Recurrence + trap (2026-07-06)**: the failure is INTERMITTENT, which makes
  it look fixed. A session saw `bd create`/`--claim`/`bd close` persist across
  several consecutive reads, concluded the write path was healed — then a later
  batch of `bd close` calls half-reverted (2 of 4 closures survived, the rest
  came back `in_progress`/`open` after the next `auto-importing … into empty
  database` cycle). Writes persist only while they win the race against the
  next stale-jsonl re-import. Do NOT trust a small number of persisting writes
  as evidence of a fix; verify `bd dolt show` no longer reports
  `Mode: per-project` before trusting bd writes. Until the real fix lands, use
  the jsonl-edit workaround above for anything you can't afford to lose.

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

## create_inline_review_comment.py broken on gh 2.95.0 (2026-07-05, butlers PR #2996 review)

`beads-pr-reviewer-worker/scripts/create_inline_review_comment.py`'s
`existing_comments()` calls `gh api` without `--method GET`, so gh 2.95.0
defaults to POST and always errors with a schema mismatch before the real
create call runs. `list_review_threads.py` and `resolve_review_thread.py`
are unaffected. Workaround: post the comment with raw
`gh api repos/{owner}/{repo}/pulls/{n}/comments -X POST ...`.
Fix when touching the script: add `--method GET` to the duplicate-check call.
ROOT CAUSE CONFIRMED (PR #3004 review): gh auto-switches to POST whenever -f/-F flags
are present, so the listing call with -F per_page=100 silently POSTs to the
create endpoint and 422s every time.
FIXED 2026-07-06: `--method GET` added to `existing_comments()` in the script
itself. Entry retained in case the regression pattern (gh api + -f/-F without
an explicit method) reappears in other scripts.

## `bd sync` removed in bd 1.0.4

- **Symptom**: `bd sync` fails with `Error: unknown command "sync" for "bd"`.
- **Cause**: Beads version control is now exposed through `bd vc` and
  `bd dolt`; the old aggregate `sync` command is absent.
- **Fix**: use `bd dolt commit -m "<message>"` for pending Beads changes,
  then `bd dolt push` when a Dolt remote is configured. `bd dolt push`
  safely reports and skips when the local database has no remote.
- Observed: 2026-07-10, bd 1.0.4.

## `bd dolt push` errors in external-server mode (no BEADS_DOLT_CLI_DIR)

- **Symptom**: `bd dolt push` fails with `Error: dolt push requires a local
  Dolt CLI database directory in external-server mode; set
  BEADS_DOLT_CLI_DIR to the local Dolt database path or use a remote type
  supported by SQL DOLT_PUSH/DOLT_PULL`. It does NOT "safely skip" as the
  `bd sync` entry above suggests — that skip behavior predates the
  shared-external-server migration.
- **Cause**: post-3307-migration repos run against the shared external
  server (`~/gt/.dolt-data`), where bd cannot drive a CLI push without an
  explicit local Dolt database path, and no Dolt remote is configured for
  the per-project DBs anyway.
- **Disposition**: session-end "push beads" is currently a no-op for these
  repos — durability rests on the shared server's data dir plus the jsonl
  export where one exists. Do not chase BEADS_DOLT_CLI_DIR; setting up a
  real Dolt remote is part of the same "needs human" external-server
  repair tracked in the WRITE-path entry above.
- Observed: 2026-07-19, bd 1.0.4, aib repo.

## zsh `echo` can corrupt compact `bd --json` before `jq`

- **Symptom**: piping a compact JSON object stored in a shell variable through
  `echo "$record" | jq ...` fails with `Invalid string: control characters
  from U+0000 through U+001F must be escaped`, while the original
  `bd show <id> --json | jq ...` succeeds.
- **Cause**: zsh's `echo` interprets backslash escapes by default. Escaped
  newlines in Beads notes become literal control characters before `jq` sees
  the JSON; the `bd` output itself is valid.
- **Fix**: project fields directly from `bd ... --json | jq ...`, or preserve
  the variable byte-for-byte with `printf '%s' "$record" | jq ...` (or zsh
  `print -r -- "$record"`).
- Observed: 2026-07-20, bd 1.0.4, zsh.

## `bd update --claim` refuses blocked beads: "issue not claimable: status blocked"

Observed bd 1.0.4 (butlers, 2026-07-25). The coordinator PR-review lane says to
atomically `--claim` a blocked `pr-review-task` bead before dispatch, but
`bd update <id> --claim` hard-fails on `status=blocked` beads with
`Error claiming <id>: issue not claimable: status blocked`.

Workaround (two steps, small non-atomic window is acceptable because review
beads are coordinator-owned):

```bash
bd update <id> --status open --json >/dev/null
bd update <id> --claim --json   # sets assignee + in_progress atomically
```

Verify `assignee` in the result as usual. Same applies to any blocked bead you
intend to claim for dispatch (e.g. after a decision sweep unblocks it).

## `resolve_review_context.py` misses reverse "blocks" dependent edges (review bead → original)

**Symptom:** A pr-reviewer worker's `resolve_review_context.py` reports missing-original-id even though the coordinator wired `bd dep add <original> <review>` correctly. Cause: that dep shape puts the link in the ORIGINAL bead's `dependents` array (original --blocks--> review); the helper only walks the review bead's own forward `dependencies` array (fallback A) or requires the pr-review label on the other side (fallback B). Hit twice on 2026-07-25 (bu-o4kzr, bu-zu768).

**Workaround:** The reviewer proceeds with the original_id/PR/head already supplied in the coordinator dispatch (always include them), or resolves manually: `bd show <review-bead> --json | jq '.[0].dependents'` / `bd show <original> --json | jq '.[0].dependents'` and cross-checks via `gh pr view`. Fix the helper to also walk dependents edges when convenient.
