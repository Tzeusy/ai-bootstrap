# Lifecycle, recovery and verification

Read the relevant section for remote access, resuming, manual handover, stopping,
or maintaining this package. Routine checkpoints do not need this file.

## Launch choices

Commands use `uv run "$DASHBOARD" --slug "$SLUG" <command>`. Global `--root`
belongs before the subcommand and overrides the default workspace parent
`~/.tmp`; reserve overrides for tests or explicit placement. Slugs contain 1–80
lowercase letters, digits or hyphens and start with a letter/digit.

`serve` starts/reuses one detached process and returns `{url,pid,reused}`. The
default is IPv4 loopback, port chosen automatically. For remote access use an
existing SSH forward, or explicitly launch with
`serve --bind <this-host-Tailscale-IPv4>`. Only loopback/Tailscale IPv4 addresses
are accepted. Tailnet HTTP exposure is an explicit launch choice. The helper
never configures Tailscale Serve, firewalls, public listeners or global daemons.
Changing a live server's address/port requires `stop` first.

`init --no-feedback` makes a new workspace read-only. Repeating `init` retains
existing title, outcome and feedback mode; it does not reconfigure them. Keep
capability URLs private and outside commits/PRs. Directory mode is 0700;
generated state, feedback and server files are 0600.

## Resume or repair

Reuse the existing session locator: helper path, slug, actor, repository,
revision and feedback cursor. Repeat `init` with the same actor/repository to
verify ownership and repair three generated progress files from `state.json`;
then `serve` if a browser is needed. A different actor/repository refuses reuse.
Recover the revision from `init`/`status`, not from Markdown stamps after an
interrupted projection write. Preserve pending feedback and manual handover.

The snapshot is the display source of truth; the owning tracker remains the
work source of truth. Do not hand-edit generated Markdown, substitute it for
tracker state or reload it at every checkpoint. A conflict requires targeted
reconciliation of intended fields before retrying with the current revision.

## Manual handover

`handover.md` starts with a scaffold marker. Only an explicit manual owner
request authorizes writing it:

```bash
uv run "$DASHBOARD" --slug "$SLUG" handover \
  --owner-request "Exact owner request from this session" \
  --input "$HANDOVER_TEXT_FILE"
```

The example supplies a UTF-8 text file; `--input -` reads stdin. The helper records the request separately
in `handover-request.json`. Supply the actual request, not a claimed generic
approval. Checkpoints, telemetry, feedback submission/acknowledgement,
compaction, stop and automatic close never update handover. A stop request
alone is not a handover request; routine recovery stays in the snapshot and
the workflow's existing journal.

## Stop and retained state

At completion or an explicit stop, publish final current progress, then run:

```bash
uv run "$DASHBOARD" --slug "$SLUG" stop
```

`stop` verifies server instance/PID via health response before signalling it;
stale metadata alone never authorizes killing a process. It preserves all
workspace content. If no verified server is reachable, it reports that no
process was signalled. Do not substitute an unverified PID kill. Deliberately
ongoing runs name their lifecycle owner and stop command in the session report.
Different slugs keep separate state, feedback and ports.

## Maintainer verification

Run documented CLI subcommands with `--help` after changing command guidance.
The [workspace/HTTP tests](../tests/test_progress_dashboard.py),
[telemetry tests](../tests/test_loop_telemetry.py), and
[browser journey](../tests/test_dashboard_browser.py) cover public behavior.
Use the shared [package validator](../../../scripts/validate-th-projects.sh)
for the defined gate; browser checks explicitly skip without Chromium. Route
verbose gate output to a local log and report exit status plus failure tail.
Do not add an extra broad run when unchanged-tree evidence already covers it.
