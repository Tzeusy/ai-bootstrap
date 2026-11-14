---
name: progress-dashboard
description: >
  Use when asked to "give this session a dashboard", "show loop progress",
  "monitor subagents", or "steer this run in a browser": a durable local
  workspace for current work, findings, agents, measured usage and feedback.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-11-14"
compatibility: Python 3.11+ and uv; stdlib-only server on Linux/macOS. Codex uses its local runtime relationship index; explicit Codex/Claude JSONL attachment remains available. No frontend build or model API.
---

# Progress Dashboard

Publish any running workflow's progress to `~/.tmp/<slug>/` and a local dashboard.
Fixed helpers scaffold `in-progress.md`, `todo.md`, `complete.md`, `handover.md`
and serve the UI. The owning tracker, claims, acceptance and authorization gates
remain authoritative; progress files only project them. Supply concise content,
not per-run server code or frontend rewrites.

## Start or resume

Resolve `DASHBOARD` to this package's
[`scripts/progress_dashboard.py`](scripts/progress_dashboard.py). Choose a stable
slug per parent session; other live sessions use different slugs. Retain the
helper path, slug, actor, repository, revision and feedback cursor (initially `0`)
in the workflow's existing session locator across compaction. Load this skill once.

```bash
uv run "$DASHBOARD" --slug "$SLUG" init \
  --title "Accepted outcome" --actor "$ACTOR" --repo-root "$REPO_ROOT" \
  --outcome "$OUTCOME"
uv run "$DASHBOARD" --slug "$SLUG" serve
```

Report the workspace and printed private URL; keep the URL outside commits/PRs.
In Codex, `init` binds `CODEX_THREAD_ID` automatically; the server resolves
published children through the runtime index. Keep actual agent IDs/names in
the roster. See [usage adapters](references/telemetry.md) for existing workspaces,
an unavailable index or other runtimes.
The server defaults to loopback. For remote access, custom roots, or recovery,
read [lifecycle](references/lifecycle.md). Initial `init --no-feedback` disables
feedback. Repeating `init` verifies identity and repairs projections.

## Publish at existing checkpoints

Publish meaningful changes: admission, delegation, findings, waits, corrections,
completion or requested updates. Reuse existing tracker reads and native agent
results. No dashboard-only agents, child-transcript summaries, backlog reloads,
model refresh timers or extra wakeups. Browser polling and incremental usage
collection run in the server.

```bash
uv run "$DASHBOARD" --slug "$SLUG" checkpoint \
  --expected-revision "$REVISION" --after-feedback "$FEEDBACK_CURSOR" \
  --input "$SNAPSHOT_JSON"
```

Send only changed fields; omitted fields persist, but a supplied list replaces
that collection. Retain completed agents with their outcomes. Use actual workflow
IDs. The helper renders progress files and returns revision plus pending feedback;
identical content keeps the revision. Minimal snapshot:

```json
{"summary":"Implementation passes; review is running.","phase":"review",
 "tasks":[{"id":"task-1","title":"Deliver behavior","status":"in-progress",
           "detail":"Waiting on independent review."}],
 "agents":[{"id":"reviewer-1","status":"running","task":"task-1",
            "summary":"Checking failure and recovery paths."}]}
```

At native delegation/report events, include each agent's concise paragraph
`summary`, known `branch`/`worktree`/`pr_url`, and up to eight `activity` strings.
These populate expandable work details; no extra agent interview is needed.

Without changes, use `status --since "$REVISION" --after-feedback "$FEEDBACK_CURSOR"`
at an existing safe checkpoint. Retain returned revision and `feedback_cursor`;
do not reread generated documents or copy snapshots into chat. Read
[snapshot/feedback protocol](references/protocol.md) for additional fields,
queue handling, `truncated` feedback or revision conflicts. Retrieve full feedback
with `inbox --id N` before interpreting or acknowledging a truncated preview.

## Feedback and authority

Feedback waits for the parent's next safe checkpoint; it cannot interrupt the
runtime or execute commands. Record a disposition after evaluating it:

```bash
uv run "$DASHBOARD" --slug "$SLUG" ack --id 3 \
  --response "Accepted; the next package will prioritize this verification."
```

Say what changed, what is deferred, or which gate applies. Acknowledgement claims
no implementation. Feedback cannot mutate the tracker, approve a merge/deployment
or bypass gates. Formal choices use
[user-questionnaire](../user-questionnaire/SKILL.md); urgent interrupts use the
runtime's direct input. Existing bounded waits govern feedback latency.

## Handover and retirement

`handover.md` stays scaffold-only until an explicit manual owner request. No
checkpoint, telemetry, compaction, stop or automatic close updates it. For that
request, use the [manual handover command](references/lifecycle.md#manual-handover).
On completion/stop, publish final current state then run
`uv run "$DASHBOARD" --slug "$SLUG" stop`; retained content survives.
An ongoing run names its server owner and stop command.

## Load only the needed slice

- [Usage adapters](references/telemetry.md): automatic Codex attribution or explicit logs;
  explain measured, partial and unknown usage without estimating.
- [Artifacts](references/artifacts.md): publish images, diagrams or PDFs through
  the existing shell without rebuilding it.
- [Lifecycle](references/lifecycle.md): network choices, identity/recovery,
  manual handover and maintainer verification.
