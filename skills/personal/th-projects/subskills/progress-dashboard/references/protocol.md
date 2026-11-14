# Workspace protocol

Resolve commands from `progress-dashboard/scripts/progress_dashboard.py`; all
examples below use that path as `DASHBOARD`. Every command accepts `--slug` and
optional `--root` **before** its subcommand. The workspace lives outside Git.
Directory mode is 0700; generated state, feedback and server files are 0600.
The CLI delegates HTTP transport to [dashboard_server.py](../scripts/dashboard_server.py)
and usage parsing to [loop_telemetry.py](../scripts/loop_telemetry.py).

## Content boundary

`state.json` (`progress-dashboard/v1`) is the last committed display snapshot.
`in-progress.md`, `todo.md` and `complete.md` are deterministic, per-file atomic
projections with revision stamps. They are readable without the server. In a
Beads workflow, their task IDs refer to actual beads; snapshots never replace
claims, acceptance, dependencies or canonical status. A crash between projection
writes is repaired on resume or the next checkpoint; the browser renders one
coherent snapshot directly from JSON. Do not edit generated progress Markdown.

The schema accepts these optional replacement fields; omitted fields retain
their current value. Lists replace their collection, so retain completed agents
when publishing a current roster. No model-generated telemetry fields are accepted.

```json
{
  "summary": "Core behavior passes; independent review is running.",
  "phase": "review",
  "tasks": [
    {"id":"task-1","title":"Deliver accepted behavior","status":"in-progress",
     "detail":"Implementation finished; waiting on independent review.",
     "evidence":"Focused tests pass; current PR records the head and checks."}
  ],
  "findings": ["The background collector does not wake the model."],
  "agents": [
    {"id":"reviewer-1","name":"Independent review","role":"reviewer",
     "status":"running","task":"task-1","summary":"Reviewing recovery and feedback paths.",
     "model":"runtime-reported model","updated_at":"2026-11-14T09:30:00+00:00"}
  ],
  "artifacts": [{"path":"architecture.svg","label":"Workspace architecture"}]
}
```

Task status is `in-progress`, `todo` or `complete`; blocked/waiting work stays
in-progress with its precise condition in `detail`. Agent status is `running`,
`waiting`, `complete`, `failed` or `unknown`. Parent summaries come from existing
delegation/report events, not another model reading child sessions. Stale
timestamps remain visible. Agent status is an observation, not a liveness lease.
Inputs reject unknown fields, duplicate identities and malformed statuses.

`checkpoint --expected-revision N --input snapshot.json` merges the supplied
fields and returns only `{revision,pending_count,feedback}`. Revision conflicts
require refreshing `status`, reconciling the content and retrying; never overwrite
a newer snapshot blindly. An empty or unchanged checkpoint is a no-op apart from
repairing generated files. `status --since N` returns `{revision,changed,phase,
pending_count,feedback}`; `inbox` returns the bounded pending batch and revision.
No background process queries a tracker, GitHub, or a model.

## Measured usage

Attach explicitly known runtime log locators once per parent/child. The agent ID
must be the workspace actor or an existing roster entry. No runtime log discovery
scan runs at launch, at each checkpoint, or in the background.

```bash
uv run "$DASHBOARD" --slug "$SLUG" attach --id "$ACTOR" \
  --provider codex --path "$EXPLICIT_PARENT_TRANSCRIPT"
uv run "$DASHBOARD" --slug "$SLUG" attach --id reviewer-1 \
  --provider claude --path "$EXPLICIT_CHILD_TRANSCRIPT"
```

Only explicit non-secret JSONL sources are supported. No auth files are read.
The collector consumes at most 1MiB per source per three-second background tick,
keeps byte offsets and counters in `telemetry-cache.json`, and does not rewrite
unchanged caches. Restart resumes offsets. Attached sources remain attributed to
their agent, including completed agents. Duplicate source paths refuse to prevent
double-counting. A changed file identity/truncated log resets that source's
measurement; it is not presented as uninterrupted lifetime usage.

Codex counters use the latest `event_msg/token_count` cumulative totals; repeated
counters do not add tokens. Claude counters deduplicate streamed assistant
records by hashed message ID. Claude input includes uncached input, cache reads
and cache writes; cached input is the read subset. Cached input is included in
input, never added again to the total. Context tokens describe the latest usage
sample, not a known context-window capacity. No prices or inferred token estimates
are displayed.

Unknown/error sources have null counters. `catching-up` identifies a bounded read
that has not reached the file end. Aggregate totals contain only measured sources;
coverage includes the parent and known agents, including unattached sessions,
and per-source timestamps identify what was observed. A successful HTTP
poll says only that the page is reachable. It proves neither fresh model activity
nor complete usage coverage. If runtime usage is unavailable, retain agent status
but show unknown usage; never generate a guess or crawl private session state.

## Browser transport and feedback

The fixed [HTML](../assets/web/index.html), [CSS](../assets/web/style.css) and
[JavaScript](../assets/web/app.js) run offline without a build. A random capability
prefix gates all routes. `GET <prefix>/api/state` returns the snapshot, rendered
document text, current usage projection and feedback history. ETags support
unchanged responses. No raw transcripts, command execution, arbitrary local-file
browser, or lifecycle mutation API is exposed. Host/Origin validation and a
JSON-only custom-header POST protect feedback against cross-site submission.

`POST <prefix>/api/feedback` requires `X-Loop-Feedback: 1` and JSON fields
`client_id`, `kind` (`feedback|steer|question`), `target` (`loop` or a current
task/agent ID), `text`, and the viewed `revision`. A stable client ID makes retries
idempotent even after a lost response. Feedback pins the viewed revision; old
feedback is retained with its original context, not silently rewritten. Writes
and acknowledgements serialize under the workspace lock. A failed save preserves
the browser draft. `ack --id N --response <disposition>` durably records what the
parent did with it; reads never consume it. Feedback history is bounded at 2000
entries/3MiB with explicit refusal, never silent deletion. The serialized byte
limit also covers acknowledgement dispositions; a refused update preserves the
previous readable inbox and can be retried with a shorter disposition.

There is no event injection into Codex/Claude and no new LLM wake timer. Steering
is observed at the existing next safe checkpoint. Critical immediate interrupts
still use the runtime's direct input surface. Hard owner decisions continue
through user-questionnaire and the owning operational gate.

## Generated visuals

Put a rendered image or PDF under `<workspace>/artifacts/`, then publish its
relative path and label in `artifacts`. Supported formats: PNG, JPEG, WebP, GIF,
SVG, PDF, and Excalidraw source downloads; use the existing Excalidraw renderer for
source diagrams. Only explicitly listed files below that directory are served,
with symlink/traversal checks; PDFs and source files download as attachments.
HTML/JS artifacts are not executable dashboard plugins. The LLM can guide
diagram/chart content while the page shell stays fixed. Keep credentials and raw
transcripts out of all content and rendered artifacts.

## Lifecycle and retained state

`serve` starts or reuses one detached server per workspace; `stop` authenticates
the server's instance/PID before signalling it. No process is signalled from stale
metadata alone. State and feedback persist after stop. Different slugs use
independent ports/state/feedback; init refuses a slug owned by another actor or
repository. Resume carries the slug, actor, repository and revision with the
workflow's ordinary recovery locator. It does not create or update a handover.
The one manual `handover` command records the exact owner request separately.

For a local browser, use the loopback URL. Across machines, forward its port over
existing SSH, or explicitly bind to the host's Tailscale IPv4 and use that printed
capability URL. HTTP exposure on the tailnet is an explicit launch choice; the
helper does not change global network configuration or start a public listener.
