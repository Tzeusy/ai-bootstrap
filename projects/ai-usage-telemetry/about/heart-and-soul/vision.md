# Vision

## What AI Usage Telemetry Is

**AI Usage Telemetry makes raw local AI-tool usage facts legible and queryable
as user-owned history.** It is for any developer who wants one durable account
of tokens, unique usage requests, and quota state across supported local tools
without surrendering private conversation content or account credentials.

[Observed] Claude Code and Codex already write structured local events from
which usage can be identified: Claude assistant events expose usage fields,
while Codex token-count events expose cumulative usage state, the most recently
stored usage contribution, and quota-related rate-limit data. Codex may re-emit
that contribution for a rate-limit-only change, so cumulative advancement—not
the physical record—is the candidate usage fact. Their record shapes and
semantics differ.

[Inferred] A self-contained, long-running local service can normalize those
facts into a durable SQLite ledger and independently project registered subsets
to optional OTLP Metrics and PostgreSQL sinks. The ledger, not either sink, is
the user's history.

## Thesis Test and Delivery Envelope

[Inferred] The first thesis checkpoint is the Synthetic-to-SQLite Usage Spine:
one fully synthetic, qualified source record must become one durable,
content-free, locally queryable contribution, and replay must not contribute it
again. The checkpoint occurs before implementation is authorized beyond that
spine. If it cannot meet that boundary without reading content, using
credentials, depending on a remote service, or weakening exact replay, the v1
thesis is falsified and the owner must reopen the product shape rather than
narrate the plumbing as success.

[Inferred] The second checkpoint is the pre-release native-architecture gate.
If the complete v1 cannot preserve identical normalized facts and privacy,
ledger, health, and projection contracts on both supported architectures, or
cannot repair either optional projection from the local ledger alone, the
portable local-service thesis is falsified before release.

[Observed] The currently committed delivery capacity is one human owner working
asynchronously with repository agents and existing local compute. No additional
human team, weekly-hours allocation, delivery deadline, or paid hosted service
is committed. V1 therefore advances as bounded, independently reviewable
capabilities; any plan that requires parallel human staffing, a calendar
promise, or paid infrastructure must return to the owner for a new resource
decision rather than silently assuming it.

## What It Is Not

[Inferred] The following exclusions are constitutional:

- It is not a prompt, response, conversation, or tool-call auditing system.
- It is not a billing ledger, token-cost calculator, or promise of provider
  invoice accuracy.
- It is not a dashboard or a bundled visualization stack.
- It is not a cloud-account collector and must not require provider or tool
  credentials.
- It is not a host-scheduler integration or a native Prometheus Pushgateway
  client.
- It is not a claim that every present or future AI tool exposes a registered
  local source for both usage and quota data.
- It is not an inbound telemetry service or API. V1 inspection is local and
  read-only through stable SQLite views.

## Non-Negotiable Principles

### 1. Local Facts Become User-Owned History.

[Inferred] Every identifiable, parseable usage event accepted from a supported
source contributes to a normalized local SQLite record retained indefinitely.
Optional external sinks are replaceable views of that local history; they must
never become the only durable account. Source deletion does not retract an
accepted fact, and ordinary maintenance must not silently prune or reset ledger
history.

**A violation is:** exporting a metric and then discarding the normalized event,
making a sink outage erase history, or pruning the ledger merely to simplify
storage management.

### 2. Content and Credentials Stay Outside.

[Inferred] Prompt and response content values must never be decoded, materialized,
logged, retained, or exported. Credential-bearing auth stores must never be
mounted. Account identity that would require credentials is represented only by
an explicitly configured local alias.

No configuration option or projection selection may weaken this rule.

**A violation is:** deserializing a message body for convenience, logging a raw
source record after a parse error, mounting a tool's auth store to discover an
account ID, or placing content or credentials in SQLite, OTLP, or PostgreSQL.

### 3. Accounting Is Eventually Exact.

[Inferred] For complete, supported records that become observable to the
collector, repeated and overlapping polls must converge on exactly one
normalized contribution per source fact. Coverage before a source is first
discovered is unknown; proven loss after discovery remains explicit. Identity
and its accounting fingerprint are stable ledger concerns: cursor position,
export selection, sink configuration, and descriptive projection changes cannot
alter either. A crash, restart, or sink retry may delay accounting but must
neither lose nor duplicate it. V1 counts tokens and unique source usage requests;
it does not invent cross-tool session or turn equivalence.

**A violation is:** incrementing totals again whenever a file is rescanned,
silently skipping a valid late-written event, or treating an aggregate snapshot
as a new delta without proving that semantic.

### 4. Partial Failure Is Explicit.

[Inferred] A source family contains independently ordered source streams, and a
stream contains records. Cursor, quarantine, freshness, and health are tracked
per stream. Only an explicitly registered irrelevant record may advance a
stream cursor without producing a fact; an unknown or malformed complete record
holds that cursor and quarantines that stream. Other healthy streams and sinks
continue, but family and global summaries must remain degraded rather than mask
the blocked stream. Silence and a stale success signal are failures.

**A violation is:** aborting the Claude family because a Codex stream changed
format, consuming an unknown record to keep a cursor moving, reporting global
health while one stream is stale, or withholding locally committed records
because PostgreSQL or an OTLP endpoint is unavailable.

### 5. Normalization Preserves Meaning.

[Observed] Claude usage-bearing assistant events and Codex token-count events
do not have the same native shape; Codex quota data also carries window state
whose age matters.

[Inferred] The normalized model must retain source identity and source
freshness. Quota utilization uses one canonical `0-1` scale and distinguishes
source observation time, collection time, and explicit fresh, stale, or unknown
state; collection time must not be presented as vendor freshness. Project labels
default to repository basenames, and configured account aliases stand in for
identities that would otherwise require credential access. Unknown or
unavailable dimensions remain unknown; they are never guessed.

**A violation is:** confusing percentages with fractions, presenting a stale
quota snapshot as current, treating unlike event types as equivalent turns, or
fabricating a model, project, or account label to fill a schema column.

### 6. The Runtime Boundary Is Portable and Narrow.

[Inferred] The product runs as one self-contained, long-running Docker image on
a configurable polling interval with a five-minute default. It receives only
explicit, resolved, read-only leaf mounts for registered Claude and Codex usage
sources and one writable volume for its own state. The container runs non-root,
exposes no inbound API or port, and behaves the same on the supported amd64 and
arm64 targets. Host scheduling, broad home-directory mounts, auth-store mounts,
and cloud API credentials sit outside the boundary.

**A violation is:** requiring a systemd or cron installation, mounting an
entire home directory or symlinked parent of a registered leaf, writing beside
source logs, opening an inbound service, or adding a cloud API call to
compensate for an incomplete local source.

### 7. Simplicity Serves the Contract.

[Inferred] One normalization core, small source-specific adapters, one durable
ledger, and independent optional sinks are enough for v1. Complexity is earned
only when it protects accounting, privacy, portability, or diagnosability.

**A violation is:** coupling sources directly to sinks, bundling dashboards or
Pushgateway behavior into the core, adding cost estimation before exact usage
accounting works, or building a generic plugin framework before a third source
has a proposed, reviewed, and owner-accepted end-to-end contract.

## What Success Looks Like

AI Usage Telemetry succeeds when a developer can leave one container running,
query a durable and eventually exact history of supported local usage, compare
available local quota state without unit ambiguity, and opt into bounded exports—while
being able to demonstrate that conversation content and credentials never
entered the system. Upstream format drift is visible as a scoped degradation,
not as a quiet hole in the history.

[Unknown] Future tools may not expose stable, credential-free local usage and
quota records. Support is earned source by source; the doctrine does not promise
universal compatibility.
