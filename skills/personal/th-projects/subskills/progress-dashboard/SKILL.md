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
    - Anthropic Claude
  status: active
  last_reviewed: "2026-11-14"
compatibility: Python 3.11+ and uv; stdlib-only server on Linux/macOS. Codex uses its local runtime relationship index; explicit Codex/Claude JSONL attachment remains available. No frontend build or model API.
---

# Progress Dashboard

Publish a running workflow's progress to `~/.tmp/<slug>/` and a local page. The
helper owns files, layout, charts, usage collection and the server; supply only
short changed content. The owning tracker, claims and gates stay authoritative.

## Start or resume

Resolve `DASHBOARD` to [`scripts/progress_dashboard.py`](scripts/progress_dashboard.py)
and pick one stable slug per parent session. Keep only that path and slug across
compaction; the workspace retains revision and feedback position. Load this skill once.

```bash
uv run "$DASHBOARD" --slug "$SLUG" start --title "Accepted outcome" --outcome "$TRACKER_ID"
```

`start` creates or resumes the workspace and server and prints the private URL;
report it, and keep it out of commits/PRs. Repeating it is safe. Remote access,
custom identity, recovery: [lifecycle](references/lifecycle.md). Token usage is
measured automatically for Codex; other runtimes: [usage](references/telemetry.md).

## Publish deltas at existing checkpoints

Publish when something meaningful changes: admission, delegation, a finding, a
wait, completion. Reuse tracker reads and native agent results you already have.
Never add dashboard-only agents, transcript summaries, timers or wakeups.

```bash
uv run "$DASHBOARD" --slug "$SLUG" checkpoint <<'JSON'
{"phase":"review",
 "tasks":[{"id":"task-1","status":"complete","evidence":"PR 12 merged; 31 tests pass."},
          {"id":"task-2","title":"Verify recovery","status":"in-progress"}],
 "agents":[{"id":"reviewer-1","name":"Reviewer","role":"review","task":"task-2",
            "summary":"Checking failure and recovery paths.","activity":["Started review."]}],
 "findings":["Recovery survives a restart."]}
JSON
```

Rows merge by `id`: send only new rows and the changed fields of existing ones.
Never resend the roster. A new task needs `title`; statuses are
`in-progress|todo|complete` (tasks) and `running|waiting|complete|failed|unknown`
(agents). `findings` and agent `activity` append. `summary` is the one current
paragraph. Link an agent to its task with `task`; add `branch`, `worktree` and
`pr_url` when known. The page derives counts, charts, links and the activity
log; never write markup. For a chart or table, send rows to a fixed
[panel template](references/protocol.md#panels); for files, see
[artifacts](references/artifacts.md).

The reply is `{revision, pending_count, feedback, ...}`. Do not reread generated
files or copy state into chat. With nothing to publish, `inbox` reads feedback.

## Feedback and authority

Each reply carries feedback not yet shown to this session. It waits for your
next checkpoint and cannot run commands, change the tracker or approve a gate.
After evaluating an item, record what you did:

```bash
uv run "$DASHBOARD" --slug "$SLUG" ack --id 3 --response "Accepted; verifying recovery next."
```

A `truncated` item must be read in full (`inbox --id N`) before acting. Formal
owner decisions use [user-questionnaire](../user-questionnaire/SKILL.md).
Details: [protocol](references/protocol.md).

## Finish

Publish the final state, then `uv run "$DASHBOARD" --slug "$SLUG" stop`; content
is retained. `handover.md` changes only on an explicit owner request through the
[manual handover command](references/lifecycle.md#manual-handover).
