# Snapshot and feedback protocol

Read for the full field list, panel templates, removal, feedback queue handling
or concurrent writers. Routine publication needs only the skill's example.
Commands use this package's [CLI](../scripts/progress_dashboard.py) as
`DASHBOARD`; global `--slug`/`--root` flags precede the subcommand. The
[server transport](../scripts/dashboard_server.py) owns browser requests;
inspect it only when maintaining HTTP behavior.

## Delta checkpoints

`checkpoint` reads JSON from stdin (or `--input FILE`) and merges it into
`state.json` (`progress-dashboard/v1`). Omitted fields and rows persist.

| Field | Merge | Row fields |
|---|---|---|
| `summary`, `phase` | replace | text |
| `tasks` | by `id` | `title`, `status`, `detail`, `evidence` |
| `agents` | by `id` | `name`, `role`, `status`, `task`, `summary`, `model`, `branch`, `worktree`, `pr_url`, `thread_id`, `updated_at`, `activity` |
| `findings` | append, deduplicated | strings |
| `artifacts` | by `path` | `label` |
| `panels` | by `id` | `title`, `kind`, `rows`, `note` |

- A row carries its identity plus only the fields that changed.
- New tasks need `title` (status defaults to `todo`); new agents default to
  `running`; new panels need `title` and `kind`.
- Agent `activity` appends up to eight reports per checkpoint and keeps the
  latest eight. Panel `rows` replace that panel's rows.
- `{"id":"x","drop":true}` removes a row. `"replace":["findings"]` rebuilds the
  named collections from this checkpoint alone (an empty rebuild clears them).
- Unknown fields, duplicate identities and malformed statuses refuse the whole
  checkpoint and leave state untouched. No telemetry fields are accepted.

Task status is `in-progress`, `todo` or `complete`; blocked work stays
in-progress with its condition in `detail`. Use real tracker IDs. Agent status
is `running`, `waiting`, `complete`, `failed` or `unknown`: an observation, not
a liveness lease. `task` holds a task `id` so the page links the two. The helper
stamps `updated_at` when an agent row changes. PR links must be absolute
HTTP(S) URLs without credentials. `thread_id` disambiguates runtime attribution
when agent paths share a basename.

Limits: checkpoint 256KiB, tasks 200, findings/agents 100, artifacts 40, panels
12 with 30 rows of 6 cells. Keep content concise, not near the limits.

## Panels

Panels are the only way to add a chart or table: the page owns every mark,
color and layout, so a panel is rows, never markup.

```json
{"panels":[
 {"id":"gates","title":"Delivery gates","kind":"steps",
  "rows":[["Tests","done","31 pass"],["Review","active"],["Merge","todo"]]},
 {"id":"size","title":"Bundle size","kind":"bars","note":"Bytes, gzip.",
  "rows":[["Before",2140],["After",96]]}]}
```

| `kind` | Row shape | Rendered as |
|---|---|---|
| `stats` | `[label, value, note?]` | headline figures |
| `bars` | `[label, number ≥ 0, note?]` | horizontal bars on one shared scale |
| `steps` | `[label, done\|active\|todo\|failed, note?]` | ordered checklist |
| `table` | first row is the header; cells are text or numbers | table |

## Derived views

The helper, not the model, derives:

- `in-progress.md`, `todo.md`, `complete.md`: atomic Markdown projections,
  readable without the server and repaired by `start`/`init` or the next
  checkpoint. Do not edit them.
- The activity log: each checkpoint records phase changes, task and agent
  status changes, new findings and newly published visuals (latest 60).
- Counts, progress meter, task-to-agent links and per-session usage bars.

## Checkpoint responses and feedback

Every `checkpoint`, `inbox` and `status` reply is compact:
`{revision, pending_count, feedback, feedback_cursor, feedback_more}`;
`status --since N` adds `changed` and `phase`. Unchanged content keeps the
revision. None return documents, roster or usage.

`feedback` holds items not yet surfaced to the session, at most ten and 8KiB
per reply, each `{id, kind, target, revision, text}`. The workspace retains the
cursor, so no flag is needed. `feedback_more` permits another `inbox` at the
same checkpoint. `pending_count` counts every unacknowledged item, including
ones already surfaced; after losing context, `inbox --after-feedback 0`
re-reads them all. Reading never acknowledges.

An oversized first item arrives as `target_preview`/`text_preview` with
`truncated:true`. Read it in full before interpreting or acknowledging:

```bash
uv run "$DASHBOARD" --slug "$SLUG" inbox --id "$FEEDBACK_ID"
```

`ack --id N --response <disposition>` durably records what the parent did: what
changed, what is deferred or which gate applies. Acknowledgement claims no
implementation. History is bounded at 2000 entries/3MiB with explicit refusal,
never silent deletion; a refused update can be retried with a shorter response.

There is no runtime event injection or model timer. Feedback waits for an
existing safe checkpoint; urgent interrupts use direct runtime input. Formal
owner decisions use user-questionnaire and the owning operational gate.

## Concurrent writers

Deltas from one parent need no revision. When several writers share a slug,
pass `--expected-revision N`; a mismatch refuses publication. Then run
`status`, reconcile against authoritative work and resend only the intended
delta. Never resend a stale full snapshot.

## Browser transport

The fixed [HTML](../assets/web/index.html), [CSS](../assets/web/style.css) and
[JavaScript](../assets/web/app.js) run offline without a build. A random
capability prefix gates routes. `GET <prefix>/api/state` returns the snapshot,
usage, feedback history and any requested handover; ETags support unchanged
responses. Model checkpoints use the compact CLI replies, never this payload.
No raw transcripts, arbitrary-file browser, execution or lifecycle mutation API
exists. Host/Origin validation and a JSON-only custom-header POST protect
feedback.

`POST <prefix>/api/feedback` requires `X-Loop-Feedback: 1` and JSON fields
`client_id`, `kind` (`feedback|steer|question`), `target` (`loop` or a current
task/agent ID), `text`, and viewed `revision`. Stable client IDs make retries
idempotent after a lost response. Failed saves preserve browser drafts. Writes
and acknowledgements serialize under the workspace lock.
