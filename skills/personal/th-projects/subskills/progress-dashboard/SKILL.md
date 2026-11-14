---
name: progress-dashboard
description: >
  Give a running session a durable progress workspace and local interactive
  dashboard showing current work, findings, agent status, measured token usage,
  artifacts and asynchronous feedback. Use for "show loop progress", "give this
  session a dashboard", "monitor subagents", or "steer this run in a browser".
  Works with any workflow; the owning tracker and authorization gates remain
  authoritative. Formal owner decisions use user-questionnaire.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-11-14"
compatibility: Python 3.11+ and uv; stdlib-only server on Linux/macOS. Optional usage adapters consume explicitly attached Codex or Claude JSONL transcripts. No frontend build or model API.
---

# Progress Dashboard

One session owns `~/.tmp/<slug>/` and one background server. Fixed scripts and
assets handle persistence, rendering, feedback and incremental telemetry. The
LLM supplies concise content and optional generated visuals, never per-run web
infrastructure. The workspace is a progress projection, not a second task tracker.

## Launch once

Resolve `DASHBOARD` from this canonical skill's absolute location to
[`scripts/progress_dashboard.py`](scripts/progress_dashboard.py). Choose a stable
slug per parent session; independent live sessions use different slugs. Reuse it
after compaction. Load this skill once; retain helper/slug/revision in the existing
session locator instead of reloading it every cycle. Consult
[the protocol](references/protocol.md) only for usage adapters, visuals or recovery.

```bash
uv run "$DASHBOARD" --slug "$SLUG" init \
  --title "Accepted outcome" --actor "$ACTOR" --repo-root "$REPO_ROOT" \
  --outcome "$OUTCOME"
uv run "$DASHBOARD" --slug "$SLUG" serve
```

`serve` starts or reuses a detached process and prints a capability URL. Default
binding is `127.0.0.1`; use an existing SSH forward for remote access, or explicitly
pass `--bind <this-host-Tailscale-IPv4>`. It never configures Tailscale Serve,
changes firewall rules, or opens a public listener. Keep the private URL in the
session report, outside commits and PRs. `--no-feedback` on initial `init` makes
the surface read-only. `--root` overrides `~/.tmp` for tests or explicit placement.

## Publish at existing checkpoints

Publish on meaningful state changes: task admission, delegation, a substantive
finding, review/CI wait, correction, completion, or an owner-requested update.
Project IDs/status from the owning workflow's existing reads; use native agent
results for child summaries. Do not reread the whole backlog or summarize child
transcripts for the dashboard. Keep completed agents visible with their outcome.

```bash
uv run "$DASHBOARD" --slug "$SLUG" checkpoint \
  --expected-revision "$REVISION" --input "$SNAPSHOT_JSON"
```

The input is a partial structured snapshot. The helper regenerates only changed
`in-progress.md`, `todo.md`, and `complete.md`; it returns the new revision and a
bounded batch of pending feedback. A stale revision refuses the write. Reuse the
returned revision; repeat publication of identical content leaves it unchanged.
The optional agents and artifacts collections render from the same snapshot.

Minimal snapshot (omit unchanged fields, keep actual workflow IDs):

```json
{"summary":"Implementation passes; review is running.","phase":"review",
 "tasks":[{"id":"task-1","title":"Deliver behavior","status":"in-progress",
           "detail":"Waiting on independent review."}],
 "agents":[{"id":"reviewer-1","status":"running","task":"task-1",
            "summary":"Checking failure and recovery paths."}]}
```

**Token efficiency is part of the contract.** There are no model-driven refresh
cycles, per-second skill calls, generated frontend rewrites, or dashboard-only
subagents. Browser polling and bounded incremental usage collection happen in the
server process. Run `status --since <revision>` or `inbox` only at the workflow's
existing wake/checkpoint when no publication is needed. Both return compact
feedback/status, not the rendered documents, full roster, or usage history.
Publish only changed fields; do not copy the full snapshot into chat.

## Feedback and authority

Feedback stays pending until the parent records its disposition:

```bash
uv run "$DASHBOARD" --slug "$SLUG" ack --id 3 \
  --response "Accepted; the next package will prioritize this verification."
```

Read the owner's message as steering through the current workflow. Acknowledge
with what changed, what is deferred, or the actual gate; acknowledgement alone
does not claim implementation. Feedback cannot execute commands, mutate tasks,
close beads, approve a merge/deployment, or bypass a hard gate. Gated owner
choices still route through [user-questionnaire](../user-questionnaire/SKILL.md).
The dashboard does not inject messages into another runtime or interrupt work;
pending feedback is consumed at the next safe parent checkpoint. Existing bounded
waits still govern how soon that checkpoint occurs.

## Handover and retirement

`handover.md` begins with a scaffold marker and **is never updated by checkpoints,
telemetry, feedback submission, compaction, stop, or automatic session close**.
Only an explicit manual owner request authorizes:

```bash
uv run "$DASHBOARD" --slug "$SLUG" handover \
  --owner-request "Owner explicitly asked for a handover in this session" \
  --input "$HANDOVER_TEXT"
```

Routine recovery data stays in the live snapshot and the owning workflow's
existing journal. A request to stop, a feedback acknowledgement, or compaction
alone is not a request to update handover. Resume verifies actor/repository
identity and repairs generated progress files from `state.json`.

Report the workspace and URL at launch; report status/feedback freshness and
measured versus unknown usage when relevant. On completion or an explicit stop,
publish the final current state, then run `stop`. A deliberately ongoing run may
retain its server; name its lifecycle owner and stop command. `stop` verifies
server identity before signalling a PID and preserves all workspace content.
No deployment, global daemon, tool-home hook, or new catalog skill is installed.

## Verification

The [workspace/HTTP tests](tests/test_progress_dashboard.py),
[telemetry tests](tests/test_loop_telemetry.py), and
[browser journey](tests/test_dashboard_browser.py) cover the public behavior.
The shared [package validator](../../scripts/validate-th-projects.sh) runs the
deterministic suites; browser checks report an explicit skip without Chromium.
