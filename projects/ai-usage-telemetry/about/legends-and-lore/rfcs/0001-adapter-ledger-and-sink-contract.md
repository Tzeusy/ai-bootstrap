# RFC 0001: Adapter, Ledger, and Sink Contract

**Status:** Accepted through Owner Decision 0001
**Author:** Codex
**Date:** 2026-08-10

## Summary

This RFC defines the v1 design contract for collecting normalized AI usage from
local Claude Code and Codex state plus Codex rate-limit facts, committing them
to a durable SQLite ledger, and projecting them independently to optional OTLP
Metrics and PostgreSQL sinks. The collector is a long-running, non-root Python
process in a `uv`-managed container. It polls every five minutes by default,
reads only explicit source mounts, writes only `/data`, and never mounts a
tool's credential store.

The SQLite ledger is the accounting authority. Stable logical identities,
payload fingerprints, atomic transactions, rescan-safe deduplication, explicit
source quarantine, and per-sink pending checkpoints make accounting eventually
exact relative to the supported local source facts. OTLP is a bounded,
cumulative operational projection; PostgreSQL is an idempotent event-time
history. Neither sink is required for the other, and sink failure never causes
accepted local facts to be discarded.

## Motivation

Claude Code and Codex persist useful usage facts locally, but their record
shapes, attribution context, duplication behavior, and quota capabilities
differ.
A direct raw-record export would leak source-specific structure into every
consumer, make schema drift difficult to diagnose, and risk forwarding content
that the project has no reason to inspect. A metrics-only collector would lose
the durable event history needed to repair projections after failure or schema
change.

The contract therefore separates four responsibilities:

1. adapters interpret a supported local source without crossing its read-only boundary;
2. normalization preserves source meaning in registered, non-overlapping categories;
3. the local ledger owns identity, deduplication, history, cursors, aggregates, and delivery state;
4. optional sinks project that history for operational queries or durable relational analysis.

"Eventually exact" means exact over every complete, supported observation that
becomes observable to the collector. Reconciliation must discover late-readable
supported observations, while later source deletion does not retract accepted
history. Coverage before source discovery is `coverage_unknown`; a
`retention_gap` requires positive evidence such as disappearance or truncation
across a previously discovered stream's unconsumed cursor. Exactness does not
mean vendor billing accuracy or a mirror of files currently present, and a
locally recorded rate-limit observation is not evidence of live vendor quota
state.

## Defined Terms

**Release profile:** an immutable, code-owned contract embedded in every
release. Its ID and content digest cover the supported source-build families,
extraction manifests, identity and arithmetic rules, parser ceilings,
reconciliation deadlines, storage-admission parameters, OTLP vocabularies and
series budget, and the synthetic vectors that justify them. Operator
configuration may select a supported capability or narrow an allowlist, but it
cannot raise, replace, or patch release-profile values at runtime.

## Evidence Baseline

- **[Observed, version-specific] Claude Code session usage:** a fully synthetic,
  loopback-only client 2.1.226 capture proves the admitted assistant record paths,
  types, and co-occurrence. The vendor documents `request-id` as globally unique
  per API request. A deliberately non-conforming A/B/A header sequence proves
  that reused identity with changed record time must be rejected as a collision,
  not treated as a legitimate duplicate.
- **[Observed structure; inferred semantics] Codex token-count context:** local token-count records expose per-update and cumulative usage plus rate-limit windows, while preceding `turn_context` supplies model and working-directory context. V1 never looks ahead or crosses a stream. Whether a particular counter is inclusive, exclusive, or repeated on a rate-limit-only update is frozen by the versioned release profile and arithmetic/replay vectors before the adapter can accept it.
- **[Not established] Claude Code quota:** no credential-free, structurally validated local Claude quota source is admitted in v1. Claude quota reports `unavailable`; the collector does not add a speculative cache mount or authenticate to fill the gap.
- **[Observed] OpenCode has locally structured usage records:** its current
  local usage format appears adaptable, but identity, mutation/replay behavior,
  privacy projection, and failure semantics have not been evidence-backed end
  to end. OpenCode support is deferred while v1 proves that complete source
  contract with two adapters; absence of quota alone is not disqualifying.

The evidence-backed v1 capability matrix is therefore:

| Source | Usage events | Quota/rate-limit snapshots | V1 behavior |
|---|---|---|---|
| Claude Code sessions | Yes | No validated source | Collect supported usage; report Claude quota `unavailable`. |
| Codex rollouts | Yes | Yes, when registered `rate_limits` fields are present | Collect supported usage and snapshots; preserve absent or null rate-limit data as unavailable rather than zero. |

This matrix is the v1 target, not permission to guess an adapter contract. Each
source capability begins as `unsupported_profile`. A test-only harness may use
synthetic fixtures under finite candidate bounds, but a real source mount is not
opened and no fact is accepted until a separately reviewed adapter profile
freezes the exact local paths/types, native identity, replay/mutation behavior,
counter arithmetic, and error cases with pinned upstream and synthetic
evidence. RFC acceptance accepts this activation rule; it does not silently
accept a still-candidate adapter profile.

## Doctrine Trace

The following decisions are load-bearing. Their principle titles are reproduced
exactly so downstream specs can trace back without interpretation.

| Decision | Contract | Doctrine principle(s) |
|---|---|---|
| D1 | Keep an indefinite, normalized local ledger as the accounting authority. | **1. Local Facts Become User-Owned History**; **3. Accounting Is Eventually Exact** |
| D2 | Mount only fixed, explicit read-only source stores; parse mixed-content JSON through a code-owned field projection that never decodes content values; never mount credential stores; and keep `/data` as the only persistent writable volume. | **2. Content and Credentials Stay Outside**; **6. The Runtime Boundary Is Portable and Narrow** |
| D3 | Use one narrow `SourceAdapter` contract and ship only Claude Code and Codex adapters in v1. | **5. Normalization Preserves Meaning**; **6. The Runtime Boundary Is Portable and Narrow**; **7. Simplicity Serves the Contract** |
| D4 | Represent token usage as registered, non-overlapping category amounts and quota as a distinct snapshot type. | **2. Content and Credentials Stay Outside**; **5. Normalization Preserves Meaning** |
| D5 | Identify facts by an immutable composite namespace and native identity plus a versioned canonical accounting fingerprint; treat byte offsets only as a validated scan optimization. | **3. Accounting Is Eventually Exact**; **5. Normalization Preserves Meaning** |
| D6 | Atomically commit facts, amounts, aggregates, `ledger_seq`, source cursors, and sink obligations in SQLite; unknown kinds and recognized malformed records hold and quarantine only the affected source. | **3. Accounting Is Eventually Exact**; **4. Partial Failure Is Explicit** |
| D7 | Make OTLP Metrics and PostgreSQL independently optional, with failed delivery remaining pending for retry. | **1. Local Facts Become User-Owned History**; **4. Partial Failure Is Explicit**; **7. Simplicity Serves the Contract** |
| D8 | Export bounded monotonic cumulative OTLP sums from a stable ledger epoch, with a single leased exporter and explicit schema-reset rules; preserve event time only in historical stores. | **4. Partial Failure Is Explicit**; **5. Normalization Preserves Meaning**; **7. Simplicity Serves the Contract** |
| D9 | Store relational history in separate idempotent event, amount, and quota-snapshot tables with mandatory unique constraints and transactional projection checkpoints. | **1. Local Facts Become User-Owned History**; **3. Accounting Is Eventually Exact**; **5. Normalization Preserves Meaning** |
| D10 | Run and publish a locked, non-root, read-only-root, no-inbound, multi-architecture Python/`uv` container on a five-minute default polling loop, configured by TOML and standard sink-specific environment. | **2. Content and Credentials Stay Outside**; **6. The Runtime Boundary Is Portable and Narrow**; **7. Simplicity Serves the Contract** |

## Design

### Runtime and Trust Boundary

The collector runs as one long-running Python process in a `uv`-managed
container. It scans all configured sources and advances all enabled sinks on a
five-minute default interval. The interval is configurable in TOML; five
minutes is the v1 default because this is historical personal analytics, not a
low-latency control loop.

The image has three canonical source/state filesystem targets. A deployment may
choose the host paths backing them, but not different in-container paths:

| Target | Kind | Required mode | Purpose |
|---|---|---|---|
| `/sources/claude/sessions` | directory | read-only | Claude Code project-session JSONL |
| `/sources/codex/sessions` | directory | read-only | Codex rollout JSONL |
| `/data` | directory/volume | read-write | SQLite, migrations, and collector-owned state |

The read-only TOML file is a separate configuration surface. Its fixed
in-container path and mount-preflight behavior are owned by the
`portable-runtime-and-release` capability. `/tmp` is ephemeral container
scratch, not a canonical host-backed source/state target.

Startup fails closed unless each enabled source target is a distinct mount at
its canonical target, is read-only, and resolves without following a symlink.
Deployment preflight inspects every host-side path component without following
symlinks, requires the canonical leaf to equal the configured source root, and
rejects a home directory, tool configuration root, or parent broader than the
fixed `projects`/`sessions` tree. In-container
discovery applies the same no-symlink and stay-beneath-target rule to every file
it opens. A bind of `~`, `~/.claude`, `~/.codex`, or an equivalent broad parent
is invalid even if a nested include filter would later narrow it.

The release image declares a non-zero UID and GID. A deployment may map them to
different non-zero numeric IDs, but provisions `/data` for those IDs in
advance; the entrypoint never starts as root merely to change ownership.
Startup proves that sources cannot be written and that `/data` can be written.
The root filesystem is read-only, `/tmp` is an ephemeral `tmpfs`, all Linux
capabilities are dropped, `no-new-privileges` is set, and no port is exposed,
published, or listened on.

Local-ledger-only mode has no network interface or egress permission. A sink
mode has a deployment-enforced egress allowlist containing only configured
sink destinations and strictly necessary name-resolution endpoints. Disabled
sinks instantiate no client, exporter, task, credential reader, DNS lookup,
checkpoint, or dependency-specific runtime path. Enabling a sink never adds
inbound access.

Claude and Codex session stores are mixed-trust inputs: mounted files can carry
conversation content beside structural usage records. Read-only mounting does
not grant permission to inspect content. The streaming projection contract
below is the only permitted mixed-content parsing path.

Source collection uses no vendor credential. Sink credentials are injected at
runtime and never stored in TOML, the ledger, diagnostics, or image layers. The
concrete secret name and orchestration mechanism are deployment detail. Runtime
and build dependencies are resolved from committed locks or immutable digests;
floating image tags and unconstrained dependency resolution are not release
inputs.

**Doctrine trace:** **2. Content and Credentials Stay Outside**;
**6. The Runtime Boundary Is Portable and Narrow**;
**7. Simplicity Serves the Contract**.

### Configuration Contract

Non-secret collector configuration is TOML. It selects enabled canonical source
targets, human-facing aliases, polling interval, projection allowlists, and
enabled sinks. It also supplies immutable technical namespaces:

- `collector_namespace`: the collector installation;
- `ledger_namespace`: this ledger and its immutable epoch;
- one `source_namespace` per configured source; and
- for every enabled sink, `sink_id`, `destination_id`, and
  `projection_schema_id`.

These are opaque technical IDs, not labels. They are mandatory even when a
human alias is absent, are persisted on first use, and must match on restart.
Changing one creates a new identity/checkpoint domain; configuration never
relabels existing rows in place. An endpoint or database target may not change
while reusing its `destination_id`.

OTLP uses standard OpenTelemetry environment conventions for transport rather
than a project-specific parallel vocabulary. PostgreSQL uses a
runtime-injected DSN secret when enabled.

Configuration must not contain prompts, responses, auth tokens, or copied source
records. Both remote sinks may be disabled for a local-ledger-only deployment;
either remote sink may be enabled without the other.

Every release embeds the **release profile** defined above. The image, ledger,
health document, and diagnostics expose its ID and digest. A profile change is
a code change with a new ID, compatibility review, and migration/rescan
consequences declared under this RFC.

Startup fails closed before scanning or exporting when the embedded profile is
missing, its digest does not match, a selected adapter or projection schema is
not covered, or persisted state names an incompatible profile without an
approved migration. "Works on a local sample" is not profile evidence: each
source identity and accounting rule must be supported by version-pinned
structural fixtures, positive and negative canonical vectors, replay and
mutation cases, and the corresponding release tests on both target
architectures.

**Doctrine trace:** **2. Content and Credentials Stay Outside**;
**6. The Runtime Boundary Is Portable and Narrow**;
**7. Simplicity Serves the Contract**.

### Mixed-Content Streaming Field Projection

Mixed-content JSONL must not be passed to a general-purpose object
deserializer. The reader is a streaming syntax traverser coupled to an
adapter-owned, compile-time registry. Syntax traversal may recognize JSON
structure, record boundaries, object keys, and scalar types. For each record
kind the registry owns:

- the exact discriminator path and admitted discriminator values;
- every permitted JSON path, exact scalar/container type, maximum decoded
  size, and whether it is required, optional, context-setting, or accounting;
- the finite set of registered irrelevant kinds; and
- paths classified as content-bearing, plus a default-deny rule for every path
  not explicitly projected.

Only keys needed to navigate a registered path and values at permitted paths
may be decoded into application values. A value at a content-bearing or
unregistered path is syntax-scanned and skipped directly from the input buffer.
It is never decoded, materialized as an application string/object, copied into
another buffer, hashed, logged, persisted, included in an exception, or passed
to normalization. Reading a bounded chunk so the syntax scanner can find
escapes, nesting, and the end of the value is transport buffering, not
permission to copy or retain it. Once the scanner advances, forbidden bytes
have no application-owned representation.

The release profile fixes every parser ceiling and counting rule: raw bytes from
record start excluding the JSONL delimiter; container depth with the root
container counted as depth one; encoded object-key bytes; projected scalar
occurrences; and each projected path's encoded bytes, decoded UTF-8 bytes,
multiplicity, numeric range, precision, and scale. It also fixes the minimum
supported container memory used to justify those ceilings. No parser default,
environment variable, or operator configuration may widen them.

Byte, key, depth, and structural guards apply while bytes are scanned. Crossing
a ceiling is `record_limit` immediately, even when no terminating newline has
arrived and even if the record might otherwise have been irrelevant. Skip-only
values remain subject to raw-byte, key, depth, and structural bounds but are
never decoded merely to enforce them. The scanner uses bounded chunks and
linear work, with application-owned memory bounded independently of record
length. Numbers are bounded exact integers or decimals; non-finite or
implementation-specific numeric values are rejected.

The first OpenSpec changeset freezes the profile schema and executable evidence
gate. Each release profile then supplies exact values from measured worst-case
parser memory and supported synthetic records before an adapter is enabled.
Release tests exercise zero/minimum, exactly-at, and one-past each independently
enforced ceiling; combinations that hit the declared memory bound; a record
that crosses its byte cap without a newline; incomplete tails below that cap;
and oversized irrelevant records. A missing bound, an unmeasured combination,
arithmetic overflow while checking a bound, or inability to prove the active
profile causes startup or the affected stream to fail closed; it never falls
back to a library default.

The privacy suite uses synthetic sentinels in every unregistered and
content-bearing position, including escaped strings, nested arrays/objects,
oversized values, malformed data, and error paths. Parser instrumentation proves
that no forbidden path invokes a value decoder/materializer or fingerprint
input. Captured logs, exceptions, crash output, SQLite, OTLP, PostgreSQL, and
network traffic contain none of the sentinel bytes or their digests. Limit
tests cover exactly-at and one-past every ceiling. These are release gates on
both supported architectures.

**Doctrine trace:** **2. Content and Credentials Stay Outside**;
**4. Partial Failure Is Explicit**;
**6. The Runtime Boundary Is Portable and Narrow**.

### Adapter Contract

A `SourceAdapter` interprets one configured source family and yields zero or
more normalized `UsageEvent` and `QuotaSnapshot` facts. This is a conceptual
contract, not a plugin ABI or a prescribed Python method signature.

Every adapter must:

- read only its explicit source mount;
- use the field-projecting streaming reader and its code-owned path/type registry;
- distinguish complete records, incomplete trailing data, registered irrelevant records, unknown record kinds, and recognized malformed or schema-inconsistent records;
- assign stable logical event identities that survive rescans and file relocation where the source provides stable identity;
- normalize source timestamps and attribution without manufacturing unsupported semantics;
- emit only registered token categories and ledger-schema-admitted metadata;
- produce no raw-record passthrough and no prompt, response, tool-call, or credential fields;
- report enough source position state for an optimized resume while remaining correct after a full rescan.

V1 contains built-in Claude Code and Codex adapters. New adapters require code
review against this RFC; runtime loading of arbitrary third-party plugins is not
part of the v1 contract.

**Doctrine trace:** **5. Normalization Preserves Meaning**;
**6. The Runtime Boundary Is Portable and Narrow**;
**7. Simplicity Serves the Contract**.

### `UsageEvent`

`UsageEvent` is the normalized unit of token accounting. It contains:

| Field group | Contract |
|---|---|
| Stable identity | The immutable tuple `(collector_namespace, ledger_namespace, adapter_schema_id, source_namespace, fact_kind, native_identity)`. No member is a display alias, path, line number, byte offset, sink setting, or collection time. |
| Accounting fingerprint | SHA-256 of RFC 8785 canonical JSON with domain tag `aiut-accounting-fingerprint-v1`. The input contains only the adapter schema, fact kind, native identity, source-observed time, registered accounting values, and source-derived attribution required to interpret them. It excludes `ledger_seq`, `collected_at`, paths, display aliases, extension metadata, every export allowlist, and every sink setting. |
| Collector and source identity | The immutable technical namespaces, separate from optional human labels. |
| Source time | The event time supplied or unambiguously derived from the source record, preserved independently of collection and sink-delivery time. |
| Attribution | Tool, vendor, model, project, and logical request identity. Adapter-specific derivation must be documented and must not cross source-stream boundaries. |
| Amounts | Zero or more non-negative integer amounts keyed by registered token category. Categories present in one event are non-overlapping. |
| Metadata | Only keys admitted by the versioned ledger schema and selected from its closed registry. Metadata extends context; it cannot carry token amounts, identity, content, or credentials. |

Model and project attribution remain explicitly unknown when registry-admitted
structural fields cannot establish them. When project attribution is
unambiguous, its default normalized identity is the repository basename rather
than an absolute path; configuration may provide a stable alias.

Logical request identity is required for an accepted v1 `UsageEvent`. The
globally scoped request key is `(collector_namespace, ledger_namespace,
adapter_schema_id, source_namespace, native_request_identity)`. It names one
native usage-bearing request, remains stable across replay, and may be shared by
multiple usage events when the source represents one request in several facts.
No display alias participates. The ledger records the first-seen complete key
in the same transaction as its event and increments the request aggregate
exactly once. An adapter that cannot establish `native_request_identity` from
registry-admitted structural fields degrades and quarantines that source stream
rather than guessing or silently undercounting requests.

The exact fingerprint document and byte-level positive and negative vectors are
a pre-ship schema artifact. Source JSON field order, metadata configuration,
sink enablement, and alias changes must not alter the fingerprint.

Two observations of the same stable identity and fingerprint are the same fact.
They do not increment aggregates or enqueue duplicate sink work. The same stable
identity with a different fingerprint is a schema or identity inconsistency; it
is never silently overwritten.

**Doctrine trace:** **1. Local Facts Become User-Owned History**;
**2. Content and Credentials Stay Outside**;
**3. Accounting Is Eventually Exact**;
**5. Normalization Preserves Meaning**.

### Token Category Registry

The initial registry is:

| Category | Meaning |
|---|---|
| `input_unclassified` | An inclusive input total whose cache relationship has not been safely decomposed; it is emitted instead of, never alongside, overlapping input categories. |
| `input_uncached` | Input tokens the source identifies as neither cache reads nor cache writes. |
| `input_cache_read` | Input tokens served from an existing cache. |
| `input_cache_write` | Input tokens written to a cache. |
| `output_unclassified` | An inclusive output total whose reasoning relationship is not separately classified; it is emitted instead of, never alongside, overlapping output categories. |
| `output_non_reasoning` | Output tokens the source explicitly identifies as non-reasoning output. |
| `output_reasoning` | Output tokens the source identifies separately as reasoning output. |

An adapter may derive a category from an inclusive source total only when the
active release profile's official-source evidence and exact arithmetic vectors
make the subset relationship, subtraction, zero case, and malformed case
unambiguous. Until then it emits the applicable `*_unclassified` total alone or
holds the record when even the total's meaning is ambiguous. Missing detail is
not guessed or folded into a nearby category. Categories must not overlap
inside an event, and cache or reasoning detail is never emitted alongside an
inclusive total that contains it.

Category extensions are reviewed and registered before emission. A new category
must define a non-overlapping meaning, source mapping, and sink treatment. An
existing name is never reassigned or broadened silently. Historical categories
may stop receiving new values but remain interpretable indefinitely.

**Doctrine trace:** **3. Accounting Is Eventually Exact**;
**5. Normalization Preserves Meaning**;
**7. Simplicity Serves the Contract**.

### `QuotaSnapshot`

Quota is a point-in-time observation, not a token event. `QuotaSnapshot`
contains:

- the same immutable composite fact identity and versioned accounting
  fingerprint contract as `UsageEvent`;
- nullable `source_observed_at`, taken only from a registry-admitted source field;
- `collected_at`, the collector clock time of the successful ledger transaction;
- configured account alias;
- vendor;
- limit name;
- canonical utilization in the inclusive range `0.0` through `1.0`;
- optional window, reset, and scope;
- `freshness_state` in `fresh | stale | unknown` and a code-owned
  `freshness_evidence` enum naming which registry-admitted timestamp/window fields
  support that state; and
- allowlisted metadata.

Adapters convert source percentages or equivalent representations to the
canonical `0..1` utilization without claiming greater precision than the
source. Window and reset fields preserve source meaning rather than forcing
unlike quota models into one duration. The logical identity distinguishes one
source observation of one account, vendor, limit, window, and scope at its
source time. Its adapter-specific construction must be stable across replay.
Same-identity, same-fingerprint observations are duplicates; the same identity
with different normalized values is a source inconsistency and follows the
quarantine contract. A downstream schema may choose the physical column
representation, but it may not weaken the complete logical identity or its
mandatory uniqueness constraints.

`collected_at` is provenance, never a substitute for `source_observed_at` and
never a fingerprint input. A registry-owned maximum age determines freshness:
known source time at or before `collected_at` is `fresh` through its inclusive
deadline and `stale` afterwards; absent source time is `unknown`. A future time
beyond the registry's allowed clock-skew bound is malformed. Exact
source/limit maximum ages and skew bounds are fixed in the pre-ship source
schema, not operator-tunable claims.

The immutable quota-subject key is `(collector_namespace, ledger_namespace,
adapter_schema_id, source_namespace, vendor, native_limit_identity,
native_window_identity, native_scope_identity)`. A configured account alias is
projection-only and never part of subject or fact identity. Stable current-quota
selection within one subject key chooses the greatest `source_observed_at`,
with null times ineligible for a current claim, and then the lexicographically
least immutable fact identity as tie-breaker. If no eligible observation exists,
current state is `unknown`, not zero. Selection never uses `collected_at`, an
alias, scan order, or sink arrival order. The view recomputes fresh/stale against
current time while preserving the recorded evidence.

Codex rate-limit snapshots preserve the local record's freshness limitation.
Stale, unknown, absent, or null observations remain queryable as state where
applicable and do not block independent usage events. Claude quota is
`unavailable` in v1. V1 performs no credential-backed quota lookup.

**Doctrine trace:** **1. Local Facts Become User-Owned History**;
**2. Content and Credentials Stay Outside**;
**4. Partial Failure Is Explicit**;
**5. Normalization Preserves Meaning**.

### Source-Specific V1 Attribution

Each adapter ships a versioned extraction manifest inside the immutable release
profile. The fields below are the evidence-backed v1 surface; any additional
field is skipped, not opportunistically decoded. Native identities and counter
relationships described here are inferred from local structure rather than a
vendor compatibility promise. They become admissible only for source-build
families covered by the profile's fixture digests, identity vectors, arithmetic
vectors, replay cases, and mutation cases. An unrecognized build/shape or a
missing identity premise holds the affected stream rather than reusing a rule
that merely looks compatible.

#### Claude Code sessions

- **Discovery:** regular, non-symlink `*.jsonl` files beneath
  `/sources/claude/sessions`; directory entries are processed in canonical
  relative-path byte order, but the relative path is never a fact identity.
- **Schema:** `claude-code/session-jsonl@1`. The discriminator is `/type`.
  Usage-bearing records have the registered value `assistant`; every other
  advancing value must appear in the adapter's finite irrelevant-kind registry.
- **Permitted paths and types:** `/type`, `/sessionId`, `/requestId`,
  `/timestamp`, `/cwd`, `/message/id`, and `/message/model` are bounded strings;
  `/message/usage/input_tokens`, `cache_creation_input_tokens`,
  `cache_read_input_tokens`, and `output_tokens` are non-negative integers.
  `/message/content` and all unregistered descendants are skipped values.
- **Native usage identity:** `(sessionId, requestId)`. Both are required. The
  official API defines `request-id` as globally unique for a request, and the
  logical request identity is the same source tuple. `/message/id` is a
  mandatory consistency field, not a replacement when `requestId` is absent;
  any alternative requires a new evidence-backed adapter schema. Repeating an
  identical fully synthetic record across lines, files, and rescans is the valid
  replay vector; the deliberately invalid A/B/A server sequence is a collision
  vector because it reuses a vendor-unique request ID across API exchanges.
- **Accounting mapping:** `input_tokens` -> `input_uncached`,
  `cache_creation_input_tokens` -> `input_cache_write`,
  `cache_read_input_tokens` -> `input_cache_read`, and `output_tokens` ->
  `output_unclassified`; absent optional categories remain absent. Claude's
  `output_tokens` is treated as an inclusive/unclassified output total because
  the admitted structure does not establish a separate reasoning subset; it is
  not relabeled as visible/non-reasoning output.
- **Timestamp and context:** `/timestamp` is the profile-admitted source-record
  time and becomes `source_observed_at`. A valid replay repeats it exactly; same
  native identity with a different timestamp is an identity inconsistency.
  Model comes from `/message/model`. Project may be normalized from the basename
  of `/cwd` or an exact configured alias; the absolute path remains local
  sensitive context and is not a fingerprint input. Claude records do not
  inherit context across JSONL records.
- **Fingerprint:** adapter schema, fact kind, native identity, message ID,
  source-observed time, source model, and sorted registered amounts. Metadata
  and export configuration are excluded. Same identity with a different time,
  message, model, or amount is an identity inconsistency and quarantines the
  stream.

Repeated assistant records with the same identity and fingerprint are duplicate
observations. The same identity with a different accounting fingerprint holds
and quarantines the stream.

#### Claude Code quota capability

V1 admits no Claude quota file, schema, identity, or snapshot mapping. The
capability is explicitly `unavailable`; absence does not degrade Claude usage
ingestion. Adding a credential-free local source later requires an RFC
amendment, a new canonical mount review, and the same extraction, identity,
freshness, privacy, and vector gates as any new source contract.

#### Codex rollouts

- **Discovery:** regular, non-symlink `rollout-*.jsonl` files beneath
  `/sources/codex/sessions`, in canonical relative-path byte order.
- **Schema:** `codex/rollout-jsonl@1`. `/type` admits `session_meta`,
  `turn_context`, and `event_msg`; `/payload/type` further identifies
  `token_count`. Other advancing values require an exact irrelevant-kind
  registration.
- **Permitted envelope/context paths:** `/timestamp`, `/type`, `/payload/type`,
  `/payload/id` on `session_meta`, and `/payload/model` plus `/payload/cwd` on
  `turn_context`.
- **Permitted usage paths:** the non-negative integer fields `input_tokens`,
  `cached_input_tokens`, `cache_write_input_tokens`, `output_tokens`,
  `reasoning_output_tokens`, and `total_tokens` beneath both
  `/payload/info/total_token_usage` and
  `/payload/info/last_token_usage`.
- **Permitted quota paths:** `/payload/rate_limits/limit_id` and the exact
  `used_percent`, `window_minutes`, and `resets_at` fields under registered
  primary/secondary window objects. All other payload descendants are skipped.
- **Context:** a usage record uses the latest preceding `turn_context` in the
  same stream. The accepted context is its `/timestamp`, `/payload/model`, and
  `/payload/cwd`; it never looks ahead or crosses a stream. A rescan starts with
  empty context and reconstructs it from the beginning.
- **Native usage identity:** the profile-versioned candidate is
  `(session_meta.payload.id, canonical total_token_usage vector)`. The vector
  is a native cumulative landmark, not the emitted amount. The release profile
  must prove its componentwise monotonicity, reset behavior, and relationship
  to `last_token_usage`; otherwise the adapter does not accept the candidate as
  identity. An unchanged landmark is a duplicate usage observation, even when
  a rate-limit-only record re-emits the previous `last_token_usage`.
- **Logical request identity:** the native usage identity above. One accepted
  Codex delta represents one logical request for v1 request accounting; replay
  of the same landmark does not increment the request count.
- **Accounting mapping:** `cached_input_tokens` -> `input_cache_read` and
  `cache_write_input_tokens` -> `input_cache_write`. The profile must freeze,
  from official-source evidence plus exact synthetic arithmetic vectors,
  whether `input_tokens` includes either cache counter and whether
  `output_tokens` includes `reasoning_output_tokens`. This RFC does not itself
  authorize either subtraction. A releasable profile must select and vector-test
  one non-overlapping rule for each axis: direct mapping when a source counter
  is exclusive, proved non-negative subtraction when a total is inclusive, or
  the applicable `*_unclassified` total alone when detail cannot be safely
  separated. An unresolved relationship makes the profile unreleasable and
  holds the stream as `unsupported_accounting_profile`; it never guesses.
  A missing cache-write field remains absent, not zero.
- **Timestamp and fingerprint:** the applicable `turn_context` timestamp is the
  usage `source_observed_at`. The fingerprint contains the adapter schema,
  native identity, that timestamp, source model, and sorted emitted delta.
- **Quota identity:** each registered window in a token-count record is a
  separate snapshot with native identity `(session id, limit id, window name,
  record timestamp)`. Its source observation time is the record `/timestamp`;
  its fingerprint contains normalized utilization, window, reset, scope, and
  evidence. A usage duplicate caused by a re-emitted `last_token_usage` does
  not suppress a new, identity-distinct rate-limit snapshot from the same
  physical record.

Missing required context, a cumulative decrease, a delta/cumulative mismatch,
or ambiguous source identity is recognized malformed data and holds the stream.
These source rules do not permit Claude- or Codex-specific fields in shared
ledger or sink extension maps.

**Doctrine trace:** **3. Accounting Is Eventually Exact**;
**4. Partial Failure Is Explicit**;
**5. Normalization Preserves Meaning**.

### SQLite Ledger and Atomicity

SQLite under `/data` is the durable accounting authority. The ledger retains
normalized usage events, token-category amounts, quota snapshots, and the state
needed to reproduce aggregates and retry sinks indefinitely. Extraction
registries do not define storage columns: the ledger has its own versioned,
closed normalized schema. Likewise, neither the PostgreSQL allowlist nor the
OTLP vocabulary can add a ledger field.

Every newly accepted immutable event or snapshot receives one strictly
increasing `ledger_seq` in the transaction that accepts it. A duplicate receives
no new sequence. `ledger_seq` is ledger-local delivery order, not source time,
event identity, or evidence that source records remain present. The mandatory
logical constraints are:

- uniqueness of the complete composite fact identity;
- uniqueness of `ledger_seq` for accepted facts;
- uniqueness of `(usage fact identity, token category)` for amount rows;
- one cursor per `(source_namespace, native stream identity)`; and
- one sink checkpoint per `(sink_id, destination_id, projection_schema_id,
  ledger_epoch)`.

For each consumed record, one SQLite transaction coordinates:

1. insertion or same-fingerprint recognition of the normalized event or snapshot;
2. for a new fact, allocation of `ledger_seq` and insertion of all registered
   amount rows;
3. update of token aggregates only for a new event and request aggregates only
   for a first-seen logical request identity;
4. advancement of the complete source cursor, including parser context, only
   through the consumed record; and
5. exposure of the new sequence to each enabled sink's independent backlog.

A same-identity, same-fingerprint duplicate advances the source cursor without
changing history, aggregates, or sink obligations. A crash or database error
rolls the whole transaction back, so the cursor can never outrun the facts and
delivery state it represents. Successful sink delivery updates only that
sink's checkpoint atomically; it does not erase the underlying fact or satisfy
another sink's obligation.

Aggregates are an optimization derived from immutable normalized history. The
ledger can rebuild them and retry a sink from its checkpoint. A sink
acknowledgement advances only that sink's checkpoint in its own SQLite
transaction after durable destination acknowledgement; an ambiguous
acknowledgement retries at least once.

**Doctrine trace:** **1. Local Facts Become User-Owned History**;
**3. Accounting Is Eventually Exact**;
**4. Partial Failure Is Explicit**.

### Retention, Maintenance, and Storage Pressure

An accepted observation is a `UsageEvent` or `QuotaSnapshot` whose complete
ledger transaction committed. Every such fact, its amounts, source evidence,
and identity are retained indefinitely. Later source truncation, deletion,
rotation, or disappearance never retracts it and never decrements aggregates or
remote history.

Lossless physical maintenance is permitted: integrity checks, online backup,
index rebuild, `VACUUM`, and versioned migrations may rewrite bytes while
preserving every logical row, identity, amount, sequence, checkpoint, and stable
view result. Logical pruning, sampling, TTL deletion, aggregate-only
replacement, or checkpoint advancement that abandons retained work is not
maintenance and is absent from v1.

Before accepting one consumed-record transaction, the ledger applies the release profile's storage
admission guard in addition to SQLite's atomic commit behavior. The profile
fixes a maximum encoded record/fact transaction, an overflow-safe method for computing the
transaction's conservative encoded-row and index/WAL amplification charge, and a
post-commit free-space reserve. Admission requires a successful filesystem
capacity observation and `available_bytes >= charge_bytes + reserve_bytes`.
Every add and multiply in that calculation is checked; overflow, an unavailable
or nonsensical capacity result, an unpriced row/index/migration shape, or a
transaction above the profiled maximum denies admission before any cursor advances.
The calculation is a conservative gate, not a claim that free space cannot race
after inspection.

The first OpenSpec changeset freezes the storage-profile schema and executable
evidence gate. Each release profile supplies exact values from measured
worst-case transactions, WAL/journal behavior, checkpoints, migrations, and the
minimum supported volume. Tests cover exactly sufficient space, one byte below
the guard, maximum profiled record transaction, arithmetic overflow, capacity-inspection
failure, concurrent capacity loss, and SQLite `FULL`/I/O failures at each write
stage. Any denied or failed transaction rolls back facts, amounts, aggregates,
sink obligations, and all source cursors together, then places ingestion in
`ledger_storage_hold`. A `SQLITE_FULL`, `SQLITE_IOERR`, failed commit, or
ambiguous connection state requires read-only reopen plus transaction and
integrity verification before any write can resume. Already committed sink
delivery may continue only when its durable acknowledgement can pass the same
admission guard; it may not advance state in memory only. Backup, migration,
checkpoint, and `VACUUM` use separate operation-specific headroom derived from
current database and auxiliary-file size and never consume the normal ingestion
reserve. Recovery never auto-prunes: the operator restores capacity, the
profile's distinct resume threshold is met, verification succeeds, and the
identical input is retried.

If forbidden content or credentials are discovered in retained state, normal
collection and affected exports stop. A privacy repair is a special,
owner-authorized operation on an isolated backup: it removes only data that was
never contractually valid, rebuilds dependent aggregates/checkpoints, records a
content-free repair audit marker, and proves forbidden bytes are absent from
all live copies and destinations. The exact repair plan and blast radius require
owner approval before mutation. Privacy repair is not a general retention
waiver.

**Doctrine trace:** **1. Local Facts Become User-Owned History**;
**2. Content and Credentials Stay Outside**;
**3. Accounting Is Eventually Exact**;
**4. Partial Failure Is Explicit**.

### Incremental Reads, Rescans, and Quarantine

The cursor and quarantine unit is a **source stream**: one independently
ordered, cursor-bearing session file or equivalent configured input object.
An adapter is a source family and may own many source streams. A failure in one
stream does not quarantine its siblings.

Every source cursor is the indivisible tuple:

`(stream_generation, next_byte_offset, prefix_anchor, parser_context)`.

- `stream_generation` combines the adapter schema, native stream/session ID,
  and platform file-generation identity. It changes on replacement even when a
  pathname is reused.
- `next_byte_offset` points to the start of the next record and is never a fact
  identity.
- `prefix_anchor` is a versioned SHA-256 digest over RFC 8785 canonical safe
  descriptors for the release-profile-fixed number of trailing consumed
  records (or all records if fewer):
  registered kind ID, record end offset, native identity and accounting
  fingerprint when present, and normalized context changes. Raw record bytes
  and content values never enter the anchor. The anchor stores its window start.
- `parser_context` is the exact normalized state needed to interpret the next
  record. It is empty for Claude sessions and contains the applicable Codex
  session ID plus preceding `turn_context` fields and their safe anchor.

Resume is permitted only after the mount/path checks still pass, generation
matches, the file is at least `next_byte_offset` bytes, the anchor window
reprojects to the stored digest, and reconstructed context agrees with the
stored context. Otherwise the stream rescans from byte zero with empty parser
context. In particular, every Codex rescan discards remembered context before
reconstructing it; context never survives a generation or anchor failure.

The reader obeys these rules:

- only a complete JSONL record may be consumed;
- an incomplete trailing record below the active raw-byte cap is deferred, with
  no cursor advance past its start, and retried on a later poll; crossing the cap
  is an immediate `record_limit` even without a delimiter;
- detected truncation, replacement, generation mismatch, or anchor mismatch
  resets the scan and parser context to the beginning of the affected stream;
- a rescan relies on stable identity and fingerprint deduplication, not on remembered line positions;
- an explicitly adapter-registered irrelevant record kind may be consumed without emitting a fact;
- a genuinely unknown record kind holds the cursor at the record and
  quarantines the stream; it is never consumed under a compatibility waiver;
- a complete record of a recognized kind that is malformed, violates the supported schema, uses an unregistered category, or conflicts with an existing fingerprint quarantines the affected source and does not advance its cursor past that record.

Quarantine is source-scoped. Other source streams, source families, and sinks
continue. The quarantine state records the source and failing position without
copying raw content into logs or metadata. Recovery requires a supported parser
change or corrected source. V1 has no force-skip, kind-ignore override,
dead-letter copy, or cursor-advance waiver for unknown or recognized malformed
records. An operator may disable the whole source, but cannot mark the held
record consumed.

Every non-exempt stream performs a full reconciliation rescan after an
adapter-schema or compatible release-profile change and no later than the
maximum interval fixed by the active release profile. The deadline is measured
from the last successfully committed complete rescan using durable elapsed-time
evidence; restart, wall-clock rollback, scan failure, or incremental success
never pushes it forward. Once overdue, affected stream, family, and global
health become `reconciliation_overdue`. Safe incremental ingestion may continue,
but health cannot claim current reconciliation.

The first OpenSpec changeset freezes the reconciliation-profile schema and
executable evidence gate. Each release profile supplies the exact deadline plus
a supported envelope for stream count, aggregate bytes, maximum record size,
and sustained append rate from mutation-detection and worst-case scan-cost
measurements. Crossing any envelope dimension sets the affected stream, family,
and global state to `source_envelope_exceeded`. Bounded incremental ingestion may
continue while parser/storage profiles remain satisfied, but full-reconciliation
currency cannot be claimed. Recovery requires the source to return within the
same profile or a newly reviewed profile to cover it. Tests cover each envelope
dimension independently at exactly `N` and `N+1`, the exact deadline, the
smallest scheduler tick beyond it, process
restart, forward/backward wall-clock changes, interrupted rescans, repeatedly
changing files, continuous append without starvation, exactly-at/one-beyond the
supported envelope, and a rescan that discovers late-readable facts. Missing or
invalid profile timing marks reconciliation overdue; it never selects a library
or operator default. A source may earn an exemption only through a pre-ship,
source-specific append-only proof that tests in-place rewrite, truncation,
replacement, rotation, and resume validation on both architectures. No v1
source is presumed append-only merely because JSONL is normally appended.

Diagnostics use only fixed keys and code-owned enums: technical source ID,
adapter schema, stream generation, numeric offset, failure code, expected
registry path ID/type, capped observed size/depth, first/last-seen time, and
repeat count. Unknown discriminator text, paths, raw exception messages, and
record fragments are excluded. SQLite keeps one current diagnostic row per
held source and updates its counter in place; logs emit state transitions and
reminders no more frequently than the release-profile-fixed interval, so an
unrepaired record cannot create unbounded diagnostic storage. The profile also
fixes and tests the anchor-window count and reminder interval; missing or
invalid values fail closed.

**Doctrine trace:** **2. Content and Credentials Stay Outside**;
**3. Accounting Is Eventually Exact**;
**4. Partial Failure Is Explicit**;
**7. Simplicity Serves the Contract**.

### Failure-State Contract

| Condition | State and accounting behavior | Progress elsewhere |
|---|---|---|
| Incomplete trailing JSONL below the active record-byte cap | Deferred, not quarantined; cursor remains before the fragment. Crossing the cap without a delimiter is `record_limit`, not an indefinitely incomplete tail. | Other complete records, sources, and sinks continue. |
| Same identity and fingerprint observed again | Idempotent duplicate; no new event, amount, aggregate, or sink work; cursor may advance. | Normal progress continues. |
| Same identity with a different fingerprint | Affected source is quarantined; conflicting fact is not committed; cursor does not advance past it. | Other sources and sinks continue. |
| Recognized malformed or schema-inconsistent record | Affected source is quarantined with explicit degraded state; cursor does not advance past it. | Other sources and sinks continue. |
| Unknown record kind | Affected stream is quarantined with a sanitized `unknown_kind` diagnostic; cursor remains before the record and v1 has no skip waiver. | Other sources and sinks continue. |
| File truncation or replacement | Source restarts from the beginning; stable identities deduplicate already committed facts. | Other sources and sinks continue. |
| Coverage before source discovery | Coverage is `coverage_unknown`; no loss claim or exact historical coverage is fabricated. | Observable sources and sinks continue. |
| Discovered source disappears or truncates across its unconsumed cursor | Source health records a proven `retention_gap`; accepted history is not retracted. | Other sources and sinks continue. |
| Supported source envelope exceeded | Stream/family/global health is `source_envelope_exceeded`; bounded incremental ingestion may continue but reconciliation is not current. | Other sources and sinks continue. |
| Claude quota requested | Capability is `unavailable`; no source is mounted and no snapshot is fabricated. | Claude usage, Codex usage/rate limits, and sinks continue. |
| Codex rate limits absent, null, stale, or freshness-unknown | Availability/freshness is represented explicitly; no zero or live-quota claim is fabricated. | Usage ingestion and sinks continue. |
| SQLite transaction or process interruption | Transaction rolls back; event, aggregate, cursor, and sink checkpoints remain mutually consistent and retry on restart. If the ledger is unavailable, no source may safely advance. | Previously committed sink work may resume only when ledger access is safe. |
| Low disk or unprovable reserve | Accepting transaction rolls back; all source cursors hold in `ledger_storage_hold`; no automatic pruning occurs. | Read-only health remains available; committed delivery continues only when safe ledger state can still be recorded. |
| OTLP delivery failure | OTLP checkpoint remains pending and retries; no local fact is lost. | PostgreSQL and all sources continue. |
| PostgreSQL delivery failure | PostgreSQL checkpoint remains pending and retries; no local fact is lost. | OTLP and all sources continue. |

**Doctrine trace:** **3. Accounting Is Eventually Exact**;
**4. Partial Failure Is Explicit**.

### Health and Freshness State

Partial failure is discoverable state, not only a log line. SQLite and
content-free diagnostics preserve, at minimum:

- per source stream: technical identity, `healthy | trailing_deferred |
  quarantined | storage_hold | reconciliation_overdue |
  source_envelope_exceeded | retention_gap | coverage_unknown |
  disabled`, last successful scan, last accepted
  source time, durable cursor tuple, held failure code/position, and reconciliation
  due/last-completed times;
- ledger: namespace/epoch/schema, migration and integrity state, free-space
  reserve state, last committed `ledger_seq`, last successful transaction, and
  accepted/duplicate/held counts; and
- per sink: technical identity tuple, `disabled | idle | delivering | retrying |
  blocked`, acknowledged `ledger_seq`, backlog, lease holder/expiry, last
  attempt, last durable success, and failure code.

SQLite exposes stable, read-only query views named `usage_events`,
`usage_event_amounts`, `quota_snapshots`, `source_health`, `sink_health`, and
`ledger_health`. Migrations preserve those names and their declared v1 columns
for the life of v1; a later incompatible contract introduces separately named
views rather than mutating them. Consumers never query private base tables as a
stable contract. The exact column manifest and nullability are a required
pre-ship schema artifact.

Inspection recomputes the storage admission guard and database availability/
verification state directly; it does not require a successful health write. If
SQLite cannot persist a transition, the read-only command still exposes
`storage_hold` or `ledger_unavailable` from current evidence and marks persisted
health as stale. Restart repeats that computation before any source or sink
write, so an unwritten hold cannot be forgotten.

A non-networked, read-only inspection command renders the health views as a
versioned JSON document with `overall_state`, `sources[]`, `ledger`, `sinks[]`,
and `quota[]`. `overall_state=healthy` only when every enabled component is
healthy/current under its own contract; it cannot mask a degraded source or
sink. The command performs no migration, retry, cursor advance, or repair.
There is no inbound health server in v1.

**Doctrine trace:** **2. Content and Credentials Stay Outside**;
**4. Partial Failure Is Explicit**;
**7. Simplicity Serves the Contract**.

### Sink Independence

OTLP Metrics and PostgreSQL are separate, independently optional consumers of
the ledger. Every enabled instance has the mandatory checkpoint key
`(sink_id, destination_id, projection_schema_id, ledger_epoch)` and value
`acknowledged_ledger_seq`. Enabling, disabling, failing, or catching up one key
does not alter another. Reusing a key for a different endpoint, database,
attribute policy, schema, or ledger is a configuration error. A new key begins
at ledger origin. Technical IDs are required projection-envelope fields and are
not optional metadata governed by descriptive allowlists.

PostgreSQL delivery is idempotent by stable normalized keys. OTLP retry sends
the current cumulative ledger projection through the selected sequence, so
repeating a projection does not increment collector totals.

Failed delivery remains pending until acknowledged. Delivery is at least once;
the collector makes no exactly-once transport claim. The collector never advances
a sink checkpoint merely because a newer fact exists or another sink succeeded.
The indefinite local ledger is the source for catch-up and repair. Enabling a
sink after local history exists starts its checkpoint at ledger origin:
PostgreSQL backfills retained facts, while OTLP emits the complete current
cumulative projection. A later OTLP projection may satisfy older pending work
only by covering the complete aggregate through that pending checkpoint.

When that cumulative projection exceeds the serialized-request cap, OTLP splits
it into deterministic, profile-ordered batches, each independently within the
cap and identified by target `ledger_seq`, batch ordinal, and batch count. The
sink checkpoint advances only after durable acknowledgement of every batch for
the same target sequence. Failure or ambiguity after any batch retries the
complete target projection from its deterministic batch set; no partial set is
acknowledged as catch-up.

**Doctrine trace:** **1. Local Facts Become User-Owned History**;
**3. Accounting Is Eventually Exact**;
**4. Partial Failure Is Explicit**;
**7. Simplicity Serves the Contract**.

### OTLP Metrics Projection

The OTLP sink exports:

- cumulative monotonic sums for token counts, separated by registered category;
- cumulative monotonic sums for deduplicated logical request counts;
- gauges for canonical quota utilization;
- gauges for quota-snapshot freshness or age.

Token and request instruments are OTLP `Sum` instruments with cumulative
temporality and `is_monotonic=true`. They come from committed ledger aggregates
through an acknowledged `ledger_seq`, never an uncommitted scan batch. Each
ledger has an immutable `ledger_epoch` and creation timestamp; the timestamp is
the stable OTLP start time for every cumulative series derived from that ledger.
Process restart, lease turnover, retry, endpoint outage, or checkpoint replay
does not reset it.

The release profile defines one total projection function for each instrument.
For token sums, every retained amount at or below the projected `ledger_seq`
maps to exactly one series tuple containing the projection schema/ledger epoch
and the finite admitted values for collector, tool, vendor, model bucket,
project bucket, and token category. For request sums, every first-seen logical
request maps once to the corresponding tuple without category. Code-owned
`unknown` and, where explicitly approved, `other` buckets are part of the finite
vocabulary; an unknown source value is never silently omitted. At every
checkpoint, summing the token series by category must equal the corresponding
ledger aggregate, and summing request series must equal the ledger's
deduplicated request count.

Quota gauges use a profile-defined tuple whose finite dimensions include every
field needed to distinguish admitted current-quota subjects, including window
where the source distinguishes windows. The projection must be injective over
the configured subjects or define an RFC-reviewed aggregation; v1 uses the
injective form. A value that cannot map exactly once, a tuple collision, or a
conservation mismatch blocks that OTLP checkpoint with sanitized health state.
It never drops a fact, invents a label, or acknowledges a partial projection.

Exactly one process may export a given checkpoint tuple at a time. A
ledger-backed lease uses expiry plus a monotonically increasing fencing token;
only the current fenced holder may send or acknowledge. Lease loss cancels its
acknowledgement path. Ambiguous delivery is retried at least once from the
ledger aggregate, which is safe for cumulative values.

The projection has a closed, deny-by-default attribute policy distinct from
both extraction and PostgreSQL. Token and request series may distinguish
configured collector, tool, vendor, model, and canonical project identity;
token series may additionally distinguish registered category. Quota series
may distinguish configured account alias, vendor, limit name, window, and scope.
A value is admitted only from the finite release-profile vocabulary or its
explicit bounded bucket.

The release profile fixes the maximum UTF-8 size of every attribute value, the
exact allowed tuple set for each instrument, per-instrument series ceilings, a
process-total series ceiling, and a serialized-request size ceiling. A series is
identified by Resource, instrumentation Scope, metric name, and the complete
point-attribute set. Startup enumerates and counts the unique legal tuples,
rather than multiplying dimensions that cannot coexist, and rejects a
configuration whose possible tuple set exceeds any ceiling before creating an
exporter. Runtime tuple creation is checked atomically against the same limits.
Series are never admitted by eviction, first-seen order, omission, or an
unbounded fallback label. Project enforcement occurs before the SDK/exporter,
whose effective per-instrument cap must equal or exceed the project cap so a
hidden lower SDK overflow cannot replace project semantics. Every sum has a
mandatory accounting partition; token sums partition by registered category.
Within each instrument/partition, at most one reserved bounded `other` tuple may
conserve otherwise unprojectable values, and every reserved tuple counts inside
all caps. For non-mergeable gauges, a new unprojectable tuple blocks and visibly
degrades the sink checkpoint while the ledger retains it.

The first OpenSpec changeset freezes the projection-profile schema and
executable evidence gate. Each release profile supplies exact tuples and limits
from representative deployments, encoded metric payloads, collector memory,
and backend capacity. Release tests cover empty/minimum,
exactly-at, and one-past every vocabulary and series ceiling; duplicate tuples;
legal sparse combinations; attribute and request-size boundaries; effective
SDK/exporter configuration; unknown/other mapping; quota-subject collisions;
category-by-category token and request conservation through retry, deterministic
multi-request catch-up, profile change, and checkpoint
replay. A missing ceiling, count overflow, profile mismatch, or inability to
enumerate the legal tuple set fails closed before export.

Event identity, request identity, fingerprint, source filename or path, byte
offset, source timestamp, reset timestamp, and arbitrary metadata are never OTLP
attributes. New attributes require explicit review for boundedness and privacy;
they are not created automatically from metadata.

Metric names, units, instrument kind, temporality, attribute meanings, and
vocabularies are immutable within one `projection_schema_id`. Any incompatible
change uses a new projection ID and new metric identity, starts its checkpoint
at ledger origin, and reconstructs the complete cumulative value. A schema ID
is never reused to make an existing series reset. If history cannot reconstruct
the new semantics, the change requires a new RFC-backed metric rather than a
silent reset.

OTLP is an operational projection of the collector's current cumulative state.
It does not preserve per-event source time and is not the historical ledger.
Prometheus-compatible analysis may derive rates from the cumulative sums, but
the collector does not make Pushgateway a primary store.

**Doctrine trace:** **2. Content and Credentials Stay Outside**;
**4. Partial Failure Is Explicit**;
**5. Normalization Preserves Meaning**;
**7. Simplicity Serves the Contract**.

### PostgreSQL Historical Projection

The PostgreSQL sink uses three separate conceptual tables:

| Table | Contract |
|---|---|
| `usage_events` | One row per composite usage identity with mandatory technical namespaces, adapter schema, native identity, fingerprint, ledger sequence, and source time. A unique constraint covers the full composite identity and a second unique constraint covers `(ledger_namespace, ledger_seq)`. |
| `usage_event_amounts` | One row per usage identity/category, with a foreign key to `usage_events` and a unique constraint over the complete event identity plus category. |
| `quota_snapshots` | One row per composite snapshot identity with a full-identity unique constraint, fingerprint, source/collection times, canonical utilization, freshness evidence/state, and allowed quota fields. |
| `projection_checkpoints` | One row per `(sink_id, destination_id, projection_schema_id, ledger_epoch)` with that tuple unique and a monotonic acknowledged `ledger_seq`. |

The technical identity/checkpoint envelope is mandatory when PostgreSQL is
enabled and is not optional descriptive metadata. The PostgreSQL projection
allowlist separately governs model, project, account, request, and extension
metadata. Allowlisted extension metadata is stored as JSONB; unlisted fields are
dropped before the sink boundary. An idempotency conflict disagreeing with the
local fingerprint or normalized values is delivery failure, never overwrite.

For every delivered sequence batch, one PostgreSQL transaction inserts each
`usage_events` row and all of its `usage_event_amounts`, inserts quota rows, and
only then advances `projection_checkpoints`. No checkpoint may make a partially
inserted event visible as delivered. The local checkpoint advances only after
durable PostgreSQL commit acknowledgement. If PostgreSQL commits but the
acknowledgement is lost, at-least-once retry meets the mandatory unique
constraints and revalidates equality before advancing locally.

Column types, nullability, foreign keys, conflict comparisons, and migration
vectors are required pre-ship schema artifacts. Index tuning and migration tool
choice remain implementation details and cannot weaken the constraints.

**Doctrine trace:** **1. Local Facts Become User-Owned History**;
**3. Accounting Is Eventually Exact**;
**5. Normalization Preserves Meaning**;
**7. Simplicity Serves the Contract**.

### Event Time and Projection Time

SQLite and PostgreSQL preserve the source event or snapshot time independently
of collection, retry, and delivery time. A late rescan therefore repairs history
at its original time rather than pretending the fact occurred when discovered.

OTLP cumulative sums and gauges represent the operational state at export time.
They may catch up after an outage, but they are not a substitute for event-time
queries. Consumers needing event chronology use SQLite or PostgreSQL.

**Doctrine trace:** **1. Local Facts Become User-Owned History**;
**4. Partial Failure Is Explicit**;
**5. Normalization Preserves Meaning**.

### Privacy and Cardinality Budget

Four deny-by-default contracts are intentionally separate and ordered:

1. the code-owned extraction registry decides which mixed-content source values
   may be decoded at all;
2. the versioned ledger schema decides which normalized fields may be retained;
3. the PostgreSQL projection allowlist decides which descriptive ledger fields
   may accompany its mandatory technical envelope; and
4. the OTLP attribute/vocabulary policy decides which bounded dimensions may
   become metric attributes.

Permission at one layer grants no permission at another. In particular,
configuration cannot widen extraction or ledger schemas, PostgreSQL JSONB
cannot bypass its projection allowlist, and an OTLP allowlist entry without a
finite vocabulary emits nothing. The budget is enforced by these closed
contracts rather than by copying whatever a source happens to contain.

| Surface | Allowed | Excluded |
|---|---|---|
| Source mounts | Fixed-target mixed-content Claude sessions and mixed-content Codex sessions, both read-only and parsed through field-projecting syntax traversal. | Any speculative Claude quota/cache path, broad home/config mounts, auth stores, browser state, shell credentials, and decoding, materializing, copying, hashing, logging, or retaining content-bearing values. |
| Adapter output and SQLite | Normalized identities, timestamps, registered amounts, quota fields, and explicitly allowlisted metadata. | Prompts, responses, tool arguments/results, raw records, credentials, unregistered token fields. |
| PostgreSQL | The normalized conceptual tables and exact fields admitted by its sink-specific allowlist. | Raw source JSON and every unlisted descriptive or sensitive field. |
| OTLP | Exact fields admitted by its sink-specific allowlist whose values also belong to finite admitted vocabularies. | Per-request/event/source-file attributes, paths, timestamps as labels, fingerprints, arbitrary metadata, and unadmitted values. |
| Diagnostics | Opaque technical source identity, numeric position, adapter/version context, code-owned failure class, capped measures, and sink state. | Raw or canonical paths, discriminator text not in the registry, exception text, record bodies, content excerpts or digests, auth material, and PostgreSQL DSN. |

Project identity is a deliberate analytics dimension, but its metric form must
be a canonical, bounded identity rather than an event-specific path or request
value. Request identity remains in the historical accounting layer and is
reduced to a cumulative count for OTLP.

No adapter or sink may expand these surfaces through a generic "extra fields"
escape hatch. A new field or attribute consumes privacy and cardinality budget
only after explicit review.

**Doctrine trace:** **2. Content and Credentials Stay Outside**;
**5. Normalization Preserves Meaning**;
**7. Simplicity Serves the Contract**.

## Compatibility and Evolution

The following rules apply across collector versions:

1. Stable composite identities remain stable for the same logical source fact. An identity-rule change requires a new adapter-schema ID and explicit ledger migration or versioned backfill plan that cannot double-count existing history.
2. Fingerprint evolution uses a new fingerprint schema/domain and published canonical test vectors. A new normalizer cannot silently reinterpret committed facts or make metadata/export configuration part of accounting identity.
3. Existing token category meanings are immutable. Extensions are reviewed and registered; category names are never reused for different semantics.
4. Additive optional source fields may be ignored. A recognized record whose required fields, types, or accounting semantics drift is quarantined rather than coerced or silently skipped.
5. Additive allowlisted metadata does not change token or request identity, category meaning, or aggregates. Removing a key stops future export but does not rewrite retained history automatically.
6. SQLite and PostgreSQL schema changes use explicit migrations and preserve idempotency, event time, and category separation.
7. The OTLP attribute set and admitted value vocabularies are closed. Adding an attribute or value source requires privacy and cardinality review; removing or renaming one is a telemetry compatibility change.
8. A newly recognized formerly-unknown record kind triggers a full affected-stream rescan from the held record or byte zero; the old version never consumed it.
9. A new source adapter, including future OpenCode support, must satisfy the same rescan, identity, normalization, quarantine, and privacy contracts before it enters v1 or a later accepted scope.
10. A newly enabled sink receives an independent checkpoint at ledger origin and cannot make existing sinks mandatory. Historical catch-up is driven from the retained ledger.
11. Accepted changes to these load-bearing rules require an RFC amendment or successor RFC plus downstream spec updates; implementation discovery alone does not silently rewrite the contract.
12. `ledger_seq`, ledger epoch, stable v1 views, checkpoint tuples, and retained accepted facts are migrated losslessly; a process or schema restart never resets them silently.

**Doctrine trace:** **1. Local Facts Become User-Owned History**;
**2. Content and Credentials Stay Outside**;
**3. Accounting Is Eventually Exact**;
**4. Partial Failure Is Explicit**;
**5. Normalization Preserves Meaning**;
**6. The Runtime Boundary Is Portable and Narrow**;
**7. Simplicity Serves the Contract**.

## Integration

The collector consumes read-only host data from Claude Code and Codex, persists
its authority under `/data`, and initiates outbound delivery to zero, one, or
both optional sinks. It has no inbound API and does not mutate source files.

Topology documentation owns concrete component placement and deployment wiring.
OpenSpec owns testable requirements derived from this RFC. Craft-and-care owns
the implementation and verification bar. Once accepted, this RFC is
authoritative for adapter semantics, ledger atomicity, failure isolation,
privacy/cardinality boundaries, and sink behavior. Unmeasured adapter/resource
profiles remain explicit activation and release gates rather than accepted
implementation evidence.

V1 builds and publishes the same container image contract for `linux/amd64` and
`linux/arm64`. Architecture-specific builds must not diverge in their mount,
privilege, write, network, adapter, ledger, or sink behavior.

One OCI manifest list references immutable amd64 and arm64 image digests built
from the same source revision, dependency lock, adapter schema IDs, ledger
schema, and projection schemas. Before publishing the manifest, each image must
run natively on its target architecture through the same synthetic
parser/privacy sentinels, identity/fingerprint vectors,
replay and migration corpus, cursor/rescan cases, stable-view/health assertions,
OTLP descriptors/cardinality checks, PostgreSQL transaction/idempotency checks,
and non-root/read-only-root/no-port/network-mode smoke tests. The two runs must
produce equal normalized facts, fingerprints, view schemas, metric descriptors,
and health schema. Emulation may add evidence but cannot replace either native
gate. A v1 release requires both native-gated images in the manifest; if either
architecture lacks passing evidence, no v1 manifest or single-architecture v1
image is published.

## Specification and Doctrine Boundary

This RFC is the accepted design contract. It gates downstream work as follows.

### Required before implementation or release OpenSpec

The first OpenSpec changeset must freeze and test:

- both extraction manifests, including exact paths/types, irrelevant-kind
  registries, explicit Claude-quota unavailability, Codex cache-write and
  rate-limit fields, release-profile parser limits, and sentinel fixtures;
- composite identity/native-identity documents, fingerprint documents and test
  vectors, timestamp/context mappings, cursor tuple/anchor validation, full
  reconciliation, and every hold/recovery transition;
- ledger tables/constraints/migrations, `ledger_seq`, transaction boundaries,
  release-profile storage admission guard and failure vectors, lossless
  maintenance, stable v1 views, and structured health JSON;
- quota freshness thresholds/evidence and deterministic current selection;
- technical sink IDs, checkpoint and lease state machines, exact OTLP metric
  names/units/descriptors/vocabularies/budgets/schema evolution, and PostgreSQL
  columns/constraints/transactional checkpoint behavior;
- canonical mount and path preflight failures, UID/GID and filesystem checks,
  network modes/egress policy, disabled-sink non-instantiation, locked build
  inputs, and multi-architecture parity gates; and
- retention, source deletion/non-retraction, low-disk recovery, backup/
  migration behavior, and owner-authorized privacy-repair scenarios.

Each bullet is allocated to a separately reviewable capability delta inside
that initial changeset. The owner may accept or reject each capability
independently; accepting one preserves its decision and trace even when a
sibling is rejected. A rejected or still-unknown required capability keeps the
overall changeset, implementation, and release blocked, but it does not erase
the value or acceptance evidence of its siblings. The changeset becomes
archiveable only after every RFC-required capability has an explicit owner
acceptance.

One independently accepted Synthetic-to-SQLite Usage Spine may authorize a
disposable, synthetic-only thesis-test harness before sibling capabilities are
accepted. That harness reads no personal source mount, opens no network path,
ships no production package, and creates no reusable production shortcut. It
is implementation evidence for the accepted spine, not authorization for real
collection, sink delivery, or release. Every non-synthetic implementation path
remains blocked until the complete RFC-required capability set is accepted.

Implementation may not begin by filling these gaps ad hoc. In particular,
Claude quota remains `unavailable` throughout v1, and source identity or token
arithmetic may not advance from inferred candidate to accepted profile without
the required version-pinned evidence and vectors.

### Safe deployment and implementation detail

Within the fixed contract, downstream design may choose package/module layout,
SQLite pragmas and index tuning, retry/backoff timings, batch sizes at or below
the profiled maximum, the numeric
non-root UID/GID, `/tmp` size, image registry/name, host paths that map to the
canonical targets, TLS material placement, sink secret names/mechanism, and
endpoint-specific DNS/proxy wiring inside the egress allowlist. Those choices
must remain reproducible, observable, and testable and may not alter identity,
accounting, retention, privacy, or checkpoint semantics.

Shape owns why an authority, trust, privacy, retention, or runtime boundary is
load-bearing. OpenSpec owns the observable scenarios and exact accepted values
that prove a build honors it. A compound sentence that states both is
borderline and must be decomposed rather than assigned wholesale to either
layer. Mixed requirements must be split into their owning shape commitment and
observable acceptance scenario before sign-off.

### Forbidden without an owner-adopted doctrine amendment

The following are not deployment options or ordinary RFC refinements:

- decoding, materializing, copying, hashing, logging, retaining, or exporting
  content values; mounting credentials; or authenticating to a vendor to fill
  a local-source gap;
- broad or writable source mounts, source mutation, elevated/runtime-root
  operation, an inbound service, unrestricted egress, or a networked
  local-ledger-only mode;
- skipping/consuming an unknown or recognized malformed record, guessing
  attribution, or using offsets/collection order as fact identity;
- pruning, expiring, sampling, retracting, or replacing accepted normalized
  history with aggregates, including after source deletion;
- making either optional sink the accounting authority or coupling one sink's
  health to another's correctness; or
- expanding v1 into content auditing, billing/invoice claims, cloud collection,
  or unapproved source/plugin loading.

Other changes to load-bearing mechanics that still honor doctrine require an
RFC amendment/successor and updated OpenSpec, but not a doctrine amendment.

## Alternatives Considered

### Line or Byte Offsets as Event Identity

Rejected. Offsets change when a file is truncated, replaced, compacted, or
rewritten and cannot recognize duplicate logical records. Offsets remain useful
only as resume optimization; stable identity and fingerprint own correctness.

### One All-or-Nothing Pipeline

Rejected. Coupling every source and sink would let one malformed Claude record
block Codex ingestion, or an OTLP outage block durable local accounting and
PostgreSQL delivery. Source quarantine and per-sink checkpoints make the failing
boundary explicit without hiding it.

### Raw Passthrough Schema

Rejected. Raw tool records carry unrelated and potentially content-bearing
fields, make downstream consumers vendor-specific, and silently change meaning
when a tool updates its schema. Reviewed normalized contracts are smaller and
safer.

### Pushgateway as the Primary Sink

Rejected. Pushgateway is an operational metrics bridge, not an indefinite,
event-time, idempotent history. Making it primary would move cumulative
accounting responsibility into an unsuitable boundary and would not support
historical repair. OTLP Metrics is the optional operational projection; SQLite
and PostgreSQL preserve history.

### Credential-Backed Quota Lookup

Rejected. It would require mounting or provisioning vendor credentials and
would turn a local-facts collector into an authenticated vendor integration.
V1 reads the local quota evidence already available and exposes its freshness
limitations for Codex. It reports Claude quota unavailable rather than
inventing a source.

### Mandatory OTLP and PostgreSQL

Rejected. Requiring both would add deployment and credential dependencies that
are unrelated to local collection correctness. The ledger is always present;
each remote sink is independently optional.

### Dynamic Third-Party Plugins in V1

Rejected. A runtime plugin ABI would expand the execution and trust boundary
before the adapter contract is proven. V1 uses two built-in, reviewed adapters;
future sources can be added through reviewed code against the same contract.

## V1 Scope

V1 ships:

- one long-running, non-root Python/`uv` container with a configurable five-minute default polling loop, built and published for `linux/amd64` and `linux/arm64`;
- explicit read-only Claude Code and Codex session mounts, no Claude quota
  mount, no tool auth-store mount, and one writable `/data` volume;
- a built-in Claude Code adapter yielding `UsageEvent` facts and reporting quota
  unavailable, plus a built-in Codex adapter yielding `UsageEvent` and
  evidence-backed rate-limit `QuotaSnapshot` facts;
- the seven initial registered, non-overlapping token categories, including
  unclassified inclusive input/output totals;
- a durable SQLite ledger with stable identity, fingerprinting, indefinite normalized history, atomic aggregates/cursors/sink state, rescan-safe deduplication, and source quarantine;
- independently optional OTLP Metrics and PostgreSQL sinks with retryable pending delivery;
- valid local-ledger-only, OTLP-only, PostgreSQL-only, and both-sinks deployment modes;
- cumulative OTLP token/request sums and quota/freshness gauges with bounded attributes;
- idempotent PostgreSQL usage-event, amount, and quota-snapshot history with configurable allowlisted JSONB metadata;
- explicit per-source-stream and per-sink health, freshness, degradation, and last-success state;
- TOML non-secret configuration, standard OpenTelemetry environment configuration, and runtime-secret PostgreSQL DSN injection when that sink is enabled;
- outbound-only networking and event-time preservation in SQLite and PostgreSQL.

V1 deliberately defers:

- OpenCode and any adapter beyond Claude Code and Codex, including any partial
  OpenCode adapter without reviewed end-to-end identity, replay/mutation,
  privacy-projection, capability, and failure evidence;
- dynamic third-party plugin loading;
- Pushgateway as a primary delivery contract;
- dashboards, alerting policy, cost or invoice reconciliation, and billing claims;
- a public inbound API or control plane;
- the concrete PostgreSQL secret name/orchestration mechanism and other deployment-specific wiring not required to preserve this RFC's boundaries.

V1 constitutionally excludes unless the owner adopts a doctrine amendment:

- credential-backed vendor quota queries or tool auth-store mounts;
- prompt, response, tool-call, or raw-record collection; and
- automatic expiration, pruning, sampling, retraction, or aggregate-only
  replacement of accepted normalized history. Lossless SQLite maintenance and
  owner-authorized privacy repair remain governed by this RFC.
