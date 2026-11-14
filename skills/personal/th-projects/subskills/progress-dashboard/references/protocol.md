# Snapshot and feedback protocol

Read for additional schema fields, feedback queue handling, transport or revision
conflicts. Routine publication needs only the skill's minimal example. Commands
use this package's [CLI](../scripts/progress_dashboard.py) as `DASHBOARD`; global
`--slug`/`--root` flags precede the subcommand.
The [server transport](../scripts/dashboard_server.py) owns browser requests;
inspect it only when maintaining HTTP behavior.

## Snapshot fields

`state.json` (`progress-dashboard/v1`) stores the committed display snapshot.
`in-progress.md`, `todo.md` and `complete.md` are deterministic, per-file atomic
projections with revision stamps. They remain readable without the server. A
crash between writes is repaired by `init` or the next checkpoint; the browser
renders a coherent snapshot directly from JSON. Do not edit generated Markdown.

Optional fields below replace their value; omitted fields persist. Lists replace
their collection, so retain completed agents when publishing a roster. No
model-generated telemetry fields are accepted.

```json
{
  "summary": "Core behavior passes; independent review is running.",
  "phase": "review",
  "tasks": [
    {"id":"task-1","title":"Deliver accepted behavior","status":"in-progress",
     "detail":"Waiting on independent review.",
     "evidence":"Focused tests pass; PR records the head and checks."}
  ],
  "findings": ["The background collector does not wake the model."],
  "agents": [
    {"id":"reviewer-1","name":"Independent review","role":"reviewer",
     "status":"running","task":"task-1","summary":"Checking recovery paths.",
     "model":"runtime-reported model","updated_at":"2026-11-14T09:30:00+00:00"}
  ],
  "artifacts": [{"path":"architecture.svg","label":"Workspace architecture"}]
}
```

Task status is `in-progress`, `todo` or `complete`; blocked/waiting work remains
in-progress with its precise condition in `detail`. Use actual tracker IDs when
one exists; projections never replace claims, acceptance, dependencies or status.
Agent status is `running`, `waiting`, `complete`, `failed` or `unknown`; it is an
observation, not a liveness lease. Native delegation/results supply summaries,
not a model reading child sessions. Supply known timestamps; omitted agent
timestamps are maintained by the helper. Stale timestamps remain visible.

Unknown fields, duplicate identities and malformed statuses refuse publication.
Limits: snapshot 256KiB, tasks 200, findings/agents 100 each, artifacts 40. Keep
content concise rather than using those limits as targets.

## Compact checkpoint responses

`checkpoint --expected-revision N --input snapshot.json` merges supplied fields.
Empty/unchanged content retains the revision and repairs projections. It returns
`revision` plus the feedback envelope below. `status --since N` adds `changed`
and `phase`; `changed` compares snapshot revisions only, so inspect feedback even
when false. `inbox` returns revision and the same feedback envelope. These do not
return full documents, roster or usage history.

Checkpoint/status/inbox accept `--after-feedback N` (default `0`). Retain returned
`feedback_cursor` beside revision and pass it at the next existing checkpoint.
The response includes `pending_count` (all unacknowledged items, including ones
already surfaced), `feedback_cursor`, `feedback_more`, and `feedback`.

Batches contain at most ten items and 8KiB of feedback payload, projecting only
`id`, `kind`, `target`, `revision` and `text`. When the first item exceeds the
budget, `target_preview`/`text_preview` replace `target`/`text`, with
`truncated:true`. Retrieve its exact record before interpreting, acting on or
acknowledging it:

```bash
uv run "$DASHBOARD" --slug "$SLUG" inbox --id "$FEEDBACK_ID"
```

The explicit lookup returns `{feedback: <full record>}` without `client_id`. A cursor only
marks what this session has surfaced; reads do not consume or acknowledge items.
Keep unresolved IDs/dispositions in existing workflow state. `feedback_more`
permits another bounded read at the same safe checkpoint. After losing the
session cursor, resume from `0`; acknowledged items stay excluded.

## Revision conflicts

A conflict refuses publication. Run `status --since "$REVISION"` with the saved
feedback cursor, then inspect only fields you intend to change from local
`state.json` (for example, `jq '{summary,phase}' "$WORKSPACE/state.json"`).
Reconcile against authoritative work and retry with the current revision. Do not
resend a stale full snapshot or reload all generated documents. No background
process queries a tracker, GitHub or a model.

## Feedback and browser transport

The fixed [HTML](../assets/web/index.html), [CSS](../assets/web/style.css) and
[JavaScript](../assets/web/app.js) run offline without a build. A random capability
prefix gates routes. `GET <prefix>/api/state` returns snapshot, rendered documents,
usage and feedback history; ETags support unchanged responses. Use compact CLI
responses for model checkpoints instead of fetching this browser payload. No raw
transcripts, arbitrary-file browser, execution or lifecycle mutation API exists.
Host/Origin validation and a JSON-only custom-header POST protect feedback.

`POST <prefix>/api/feedback` requires `X-Loop-Feedback: 1` and JSON fields
`client_id`, `kind` (`feedback|steer|question`), `target` (`loop` or a current
task/agent ID), `text`, and viewed `revision`. Stable client IDs make retries
idempotent after a lost response. Feedback preserves its viewed revision; old
messages keep their original context. Failed saves preserve browser drafts.
Writes and acknowledgements serialize under the workspace lock.

`ack --id N --response <disposition>` durably records what the parent did. State
what changed, what is deferred or which gate applies; acknowledgement alone
claims no implementation. History is bounded at 2000 entries/3MiB with explicit
refusal, never silent deletion. The byte limit includes dispositions; a refused
update preserves the readable inbox and can be retried with a shorter response.

There is no runtime event injection or new LLM timer. Feedback waits for an
existing safe parent checkpoint; urgent interrupts use direct runtime input.
Formal owner decisions use user-questionnaire and the owning operational gate.
