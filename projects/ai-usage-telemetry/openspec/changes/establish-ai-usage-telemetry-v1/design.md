## Context

This change translates the adopted product doctrine and accepted
[RFC 0001](../../../about/legends-and-lore/rfcs/0001-adapter-ledger-and-sink-contract.md)
into the technical architecture that the capability specifications will make
testable. The [launch gate](../../../docs/launch-gate/2026-08-10-96ba99d.md)
recorded READY against commit
96ba99dda1503e2f278df9b76abd3c5872faa8fd, including an empty E3 list of
shape-level questions that would need to be reopened before specification.

[Observed] The project is still pre-implementation. This changeset adds
documentation only: no application package exists, no personal source is read,
no sink is contacted, and no release profile has earned activation evidence.
The proposal defines eleven independently reviewable capabilities whose
combined owner acceptance is required before archival and before any
non-synthetic implementation, real-source mount or fact acceptance, sink
delivery, or release. The Synthetic-to-SQLite Usage Spine is the one narrower
exception: after its own owner acceptance, it may authorize a disposable
synthetic-only thesis-test harness. That harness opens no real source mount,
accepts no non-synthetic fact, opens no network or sink path, ships no
production package, and creates no reusable production shortcut.

The architecture is constrained by the seven principles in
[the vision](../../../about/heart-and-soul/vision.md):

- accepted local facts become indefinitely retained, user-owned SQLite history;
- content values and tool credentials never enter the application boundary;
- supported observable facts converge to exactly one accounting contribution;
- partial failures are explicit, scoped, and non-masking;
- normalization preserves source identity, time, and category meaning;
- the runtime is one narrow, portable, non-root, no-inbound container; and
- complexity is admitted only to protect those contracts.

The primary stakeholder is the developer who operates and queries the local
ledger. The owner separately accepts each capability contract. Implementers and
reviewers need deterministic contracts for identity, replay, health, migration,
and release evidence without being allowed to fill evidence gaps by guesswork.

The term release profile means the immutable, code-owned contract embedded in a
release. Its ID and digest bind source-build support, extraction manifests,
identity and arithmetic rules, resource ceilings, reconciliation parameters,
sink vocabularies and budgets, and their executable evidence. Runtime
configuration may select or narrow profile-backed behavior; it cannot widen or
patch a release profile.

Capability ownership remains non-overlapping. The first OpenSpec changeset
freezes each domain member's schema and executable evidence gate. A later
immutable release profile supplies that member's exact measured values and
evidence before activation; release-profile governance composes those members
without redefining them. Unresolved profile values are therefore mandatory v1
pre-activation evidence, not permission to invent numbers in this changeset and
not optional work for a later product version.

Capability-contract acceptance and release-profile activation are separate
gates. The owner may accept or reject each capability independently, but this
changeset may be archived only after explicit owner acceptance of all eleven,
as required by the proposal. Except for a separately owner-accepted disposable
synthetic-only spine, no non-synthetic implementation starts until the complete
required capability set is accepted. The narrower synthetic exception owns no
production schema or profile and authorizes no real source, sink, or release.

## Goals / Non-Goals

**Goals:**

- Define one-way source-to-ledger-to-sink boundaries with SQLite as the only
  accounting authority.
- Keep source interpretation in two small built-in adapters behind one
  content-denying streaming projection contract.
- Define stable fact, request, stream, ledger, and sink identities so rescans,
  retries, relocation, and process restarts cannot create duplicate accounting.
- Make each complete record's deterministic ordered zero-or-more fact set atomic
  with all amount rows, first-seen requests and aggregates, source cursor and
  parser context, ledger sequences, and enabled-sink obligations.
- Define deterministic reconciliation, quota selection, and sink catch-up
  behavior without assigning accounting meaning to file order or collection
  time.
- Contain malformed input, storage pressure, and sink failure at the narrowest
  safe boundary while exposing non-masking local health.
- Separate immutable release evidence from operator configuration and fail
  closed whenever required evidence or compatibility is absent.
- Preserve a narrow privacy and runtime boundary in local-ledger-only, OTLP-only,
  PostgreSQL-only, and both-sinks modes.
- Provide a staged future rollout and a no-data-loss rollback posture.

**Non-Goals:**

- Implementing the collector, disposable harness, schemas, migrations, image,
  adapters, queries, or sinks in this changeset.
- Reading or validating any real Claude Code or Codex user mount.
- Activating a source profile, OTLP exporter, PostgreSQL connection, or network
  path.
- Claiming release evidence or choosing exact parser ceilings, storage reserves,
  reconciliation deadlines, freshness ages, vocabularies, cardinality limits,
  batch sizes, or other release-profile values before accepted measurements
  and vectors exist.
- Collecting prompts, responses, tool calls, raw records, credentials, or
  credential-backed quota.
- Supporting OpenCode, arbitrary plugins, an inbound API, dashboards, alerts,
  cost estimation, billing reconciliation, or hosted collection in v1.
- Making file position, path, scan order, collection time, aliases, or sink
  configuration part of accounting identity.
- Defining package layout, library choices, SQLite tuning, deployment-specific
  secret names, endpoint wiring, or registry naming unless needed by an
  observable contract.

## Architecture

### Component boundaries

The future runtime is one long-running Python process in a uv-managed container.
Logical components remain separate even though they share the process:

| Component | Owns | Must not own |
|---|---|---|
| Startup and profile verifier | Configuration validation, persisted namespace checks, release-profile digest and compatibility checks, canonical mount and runtime preflight | Source interpretation or profile-value invention |
| Source discovery | Regular-file discovery beneath one canonical read-only source target, stay-beneath and no-symlink enforcement, source-stream generation evidence | Fact identity or accounting |
| Streaming field projector | JSON syntax traversal, registered path/type projection, bounded skip-only handling, parser ceilings | General object deserialization or content-value materialization |
| Claude Code adapter | Claude discriminator, permitted fields, native identity, source time, attribution, and category mapping for an activated profile | Codex context or unregistered fields |
| Codex adapter | Same-stream session/context reconstruction, cumulative-landmark interpretation, usage deltas, and rate-limit snapshots for an activated profile | Look-ahead, cross-stream context, or guessed arithmetic |
| Normalization core | UsageEvent, QuotaSnapshot, token-category, request-identity, and accounting-fingerprint contracts | Source-specific raw extension maps |
| SQLite ledger | Immutable history, amounts, request and token aggregates, ledger sequence, cursors, diagnostics, release/profile state, health state, and per-sink obligations | Raw source records or sink-defined schema |
| Local query and inspection surface | Stable read-only views and versioned content-free health JSON | Inbound networking, repair, migration, retry, or cursor advancement |
| OTLP projector | Bounded cumulative operational metrics, deterministic batching, fenced lease, and its own checkpoint | Event-time history or ledger authority |
| PostgreSQL projector | Idempotent event-time history, allowlisted metadata, transactional remote checkpoint, and its own local checkpoint | Ledger authority or OTLP progress |

Dependencies flow in one direction:

    explicit read-only source
      -> streaming field projection
      -> source adapter
      -> ordered normalized fact set plus parser-context transition
      -> atomic complete-record SQLite transaction
      -> stable local views
      -> independent OTLP and/or PostgreSQL projections

Sinks never feed facts, identity, or success back into source ingestion. Local
querying reads stable views rather than private tables. Health reads durable
state plus current read-only evidence and does not mutate the system.

### Capability ownership and composition

The eleven proposal capabilities divide ownership as follows. "Consumes" means
the capability relies on another capability's accepted contract; it does not
gain authority to redefine that contract.

| Capability | Owns | Consumes | Composes / boundary |
|---|---|---|---|
| `synthetic-usage-spine` | The qualified synthetic-only fixture-to-SQLite thesis and bounded human-legibility checkpoint | Only its accepted disposable-harness boundary and synthetic evidence | Composes no production member and owns no production extraction, parser, normalized-fact, ledger, query/health, sink, runtime, or release-profile schema or value |
| `source-adapter-profiles` | Claude and Codex extraction manifests, discriminator and irrelevant-kind registries, context transitions, deterministic per-record fact ordering, source-build activation evidence, and the parser-resource member schema and evidence gate | Canonical source targets from `portable-runtime-and-release` and normalized output contracts from `event-identity-and-normalization` and `quota-snapshot-semantics` | Composes projected fields and parser-context transitions into an ordered zero-or-more candidate-fact set; it does not accept or persist facts |
| `event-identity-and-normalization` | `UsageEvent`, composite and request identities, the exact accounting-fingerprint document, source-time and attribution rules, token-category semantics, and non-overlapping arithmetic requirements | Registry-admitted source fields and source-specific evidence from `source-adapter-profiles` | Composes source-faithful usage candidates; it owns no cursor, storage, view, or sink schema |
| `stream-reconciliation-and-health` | Discovery, stream generation, cursor/anchor/parser-context contract, resume and full-rescan rules, quarantine and coverage/retention states, reconciliation profile member, and source-health semantics | Adapter context transitions and the ledger's atomic record-commit result | Composes per-stream state into source-family/global source health for `local-query-contract`; it cannot advance a cursor independently |
| `durable-local-ledger` | Private SQLite base schema, tables and constraints, migrations, record-set transaction, ledger sequence, persisted cursors/context and sink obligations, storage admission, retention, maintenance, backup, ledger health, and privacy-repair boundary | Ordered candidate facts and request identities, the proposed cursor/context transition, and enabled sink identities | Atomically composes accepted facts and source progress into durable authority; it does not own stable query-view manifests or health JSON |
| `quota-snapshot-semantics` | `QuotaSnapshot`, quota fact/subject identity, canonical utilization, availability, source/collection-time distinction, freshness evidence, and deterministic current selection | Registered Codex quota fields and common fingerprint rules | Composes admitted snapshots and current-quota semantics; it owns neither source extraction nor their query rendering |
| `local-query-contract` | Exact stable read-only view names, columns, nullability and compatibility, plus the versioned non-networked structured-health JSON schema and inspection behavior | Ledger rows and ledger health, source health, sink health, and quota current-selection semantics | Composes the public local read model and non-masking overall health; it owns no private SQLite storage schema, migration, retry, repair, or write path |
| `otlp-metrics-projection` | Metric names, units, descriptors, finite tuples and vocabularies, budgets, conservation, batching, lease/checkpoint state machine, retry, and projection-schema evolution | Committed ledger aggregates/current quota, ledger sequence, and its independent sink obligation | Composes bounded cumulative operational metrics only; it never becomes accounting authority or historical storage |
| `postgresql-history-projection` | Remote event/amount/quota tables, types, nullability, keys and constraints, allowlisted metadata, event-time mapping, transactional remote checkpoint, retry, and projection-schema evolution | Committed ledger facts in ledger-sequence order and its independent sink obligation | Composes idempotent remote history; it does not own local ledger or OTLP state |
| `release-profile-governance` | The immutable release-profile envelope, member identity, ID/digest, compatibility rules, activation authorization, and fail-closed behavior | Explicitly owner-accepted capability contracts plus each owning domain's exact measured values and executable evidence | Composes accepted domain members into one immutable profile; it cannot invent, override, or become a second owner of a domain schema or value |
| `portable-runtime-and-release` | The three canonical host-backed source/state targets, the separate read-only TOML configuration surface and its fixed in-container path/preflight, secret boundary, privilege/filesystem/network isolation, disabled-sink non-instantiation, locked inputs, native architecture gates, and publish decision | An activatable immutable release profile, including parser minimum-memory evidence, plus the enabled capabilities' parity tests | Composes the native amd64/arm64 images and manifest only after all applicable gates pass; it does not choose adapter, accounting, ledger, query, or sink semantics |

In particular, SQLite location does not collapse ownership: the durable-ledger
capability owns private storage and persistence, while `local-query-contract`
owns the stable SQL views and structured-health JSON read contract. Parser
resource ceilings and their measurement gate belong to
`source-adapter-profiles`; runtime/release consumes their minimum-memory and
native-parity evidence but cannot set it.

### Source-to-ledger flow

1. Startup validates the embedded release-profile digest, selected capability
   membership, persisted technical namespaces, schema compatibility, mount
   boundary, non-root runtime, source non-writability, and data-volume
   writability. A failed prerequisite stops scanning and exporting.
2. Each enabled adapter begins as unsupported until its exact source-build
   family, extraction manifest, identity rule, arithmetic rule, limits, and
   fixtures have passed the profile evidence gate. Synthetic fixtures may be
   exercised under candidate test bounds without opening a real mount.
3. Discovery enumerates only regular non-symlink JSONL files beneath the
   adapter's canonical target. Relative-path byte order makes discovery and
   rescan reproducible, but a path is never a fact identity.
4. The streaming projector syntax-scans each complete record. It decodes only
   the discriminator, context, accounting, and identity values named by the
   activated compile-time registry. Content-bearing and unregistered values are
   skipped without decoding, copying, hashing, logging, or retaining them.
5. The adapter classifies incomplete trailing data, unknown kinds, and
   recognized malformed data before consumption. For each complete consumable
   record it deterministically produces an ordered set of zero or more fact
   candidates plus exactly one resulting parser-context transition. The active
   profile fixes candidate order; Codex token-count order is usage first, then
   registered quota windows in registry order. Codex context is rebuilt only
   from preceding records in the same stream; Claude context remains empty.
6. Every candidate is normalized before commit to a stable composite identity
   and the canonical accounting fingerprint. Unknown attribution remains
   unknown. Token amounts use registered non-overlapping categories; quota
   remains a distinct snapshot type.
7. The ledger resolves every candidate in the ordered set as new,
   same-identity/same-fingerprint duplicate, or
   same-identity/different-fingerprint collision, then commits the complete
   record outcome in one SQLite transaction. New facts receive ledger sequences
   in candidate order, all amount rows, first-seen request rows and aggregates,
   and one obligation for every enabled sink. Duplicates receive none of those
   new contributions. The proposed parser context and complete source cursor
   advance exactly once, after the whole set succeeds. Any collision, admission
   denial, write failure, or ambiguous commit rolls back every new contribution,
   parser-context change, and cursor advance for that record; the affected
   stream holds before it.
8. Stable local views expose committed history and health. Optional sink workers
   independently project committed sequences and advance only their own
   checkpoints after durable destination acknowledgement.

The two v1 adapter projections are intentionally asymmetric:

| Source | Usage interpretation | Quota interpretation |
|---|---|---|
| Claude Code sessions | Activated assistant records use the profile-backed session/request identity and registered input, cache-read, cache-write, and unclassified-output mapping. They inherit no cross-record context. | Unavailable in v1. No quota source is mounted and no zero snapshot is fabricated. |
| Codex rollouts | Activated token-count records use the latest preceding same-stream session/turn context and an evidence-backed cumulative landmark plus delta rule. Unproved counter overlap or reset behavior holds the stream. | Each registered rate-limit window becomes an identity-distinct snapshot when present. A repeated usage landmark does not suppress a new quota observation. |

Complete-record outcomes are therefore explicit:

| Complete record outcome | Atomic ledger effect |
|---|---|
| Context-only Codex `session_meta` or `turn_context` | Commit the normalized parser-context transition and advance the cursor exactly once; emit no fact, sequence, amount, request contribution, aggregate update, or sink obligation |
| Registered irrelevant record | Advance the cursor exactly once with unchanged parser context; emit no fact or accounting/delivery state |
| All candidates are duplicates | Advance cursor and resulting parser context exactly once; add no history, amount, request, aggregate, sequence, or sink obligation |
| Mixed new and duplicate candidates | Commit every new fact in deterministic candidate order with all of its amounts, first-seen-request effect, aggregates, sequence, and enabled-sink obligations; leave duplicates neutral; commit parser context and advance the cursor once after the whole set commits |
| Codex duplicate usage plus new quota windows | Treat the repeated usage landmark as a duplicate while accepting each identity-distinct new quota snapshot in registered window order, then advance the cursor once; duplicate usage never suppresses quota output |
| Any candidate collides, or record-set admission/write/commit fails | Commit none of the record's new candidates or side effects, preserve the prior parser context and cursor, and hold the stream before the record even if other candidates were new or duplicate |

An incomplete trailing fragment is not a complete-record outcome: it remains
deferred before its start with no parser-context or cursor change. The ordered
fact set, rather than any individual candidate, is the unit of record
acceptance.

### Identity and deterministic ordering

Correctness uses several deliberately separate orders and identities:

| Concern | Contract |
|---|---|
| Fact identity | Immutable tuple of collector namespace, ledger namespace, adapter schema ID, source namespace, fact kind, and native identity |
| Accounting equality | SHA-256 over RFC 8785 canonical JSON with domain tag `aiut-accounting-fingerprint-v1`; inputs are only `adapter_schema_id`, `fact_kind`, `native_identity`, `source_observed_at`, registered accounting values, and source-derived attribution necessary to interpret them. `collector_namespace`, `ledger_namespace`, `source_namespace`, `ledger_seq`, `collected_at`, paths, display aliases, extension metadata, every export allowlist, and every sink setting are excluded |
| Logical request | Source-backed request identity recorded once so multiple facts or replay cannot increment request totals twice |
| Source resume | Stream generation, next byte offset, safe prefix anchor, and parser context; this is an optimization validated before use, never fact identity |
| Acceptance order | Strictly increasing ledger sequence allocated only to newly committed facts; it is durable delivery order, not event time or logical identity |
| Historical order | Source-observed time preserved independently of collection, acceptance, retry, and delivery time |
| Current quota | Greatest eligible source-observed time within one immutable subject key, then lexicographically least immutable fact identity; collection time and scan order are excluded |
| Sink order | Committed ledger sequence; OTLP catch-up batches additionally use profile order, target sequence, batch ordinal, and batch count |

Discovery is deterministic within each source family. Cross-source scan
interleaving is not an accounting contract: once transactions commit, ledger
sequence is the durable serialization, while stable identity and fingerprints
make the final facts independent of traversal order. A same-identity,
same-fingerprint observation is a duplicate. A same-identity,
different-fingerprint observation is a collision that holds the affected stream
instead of overwriting history.

### Ledger and sink flow

SQLite under /data is the accounting authority and the only component permitted
to coordinate complete-record acceptance with source progress. It retains
normalized facts, amounts, source evidence, identities, sequences, cursors,
aggregates, diagnostics, and sink obligations indefinitely. Aggregates are
rebuildable optimizations; accepted facts are not.

Each enabled sink instance is identified by sink ID, destination ID, projection
schema ID, and ledger epoch. Its checkpoint is independent:

- PostgreSQL reads facts in ledger-sequence order, inserts an event and all
  amount rows or a quota snapshot under mandatory uniqueness constraints, and
  advances its remote checkpoint in the same database transaction. The local
  checkpoint advances only after durable commit acknowledgement. Ambiguous
  acknowledgement causes idempotent retry and equality revalidation.
- OTLP derives complete cumulative sums and current quota gauges from the
  committed ledger through a target sequence. One fenced lease holder exports a
  checkpoint tuple. If one request cannot hold the complete projection, the
  profile orders deterministic batches; every batch for the target must be
  acknowledged before the checkpoint advances. Ambiguity retries the complete
  target projection.

Enabling a new sink starts its new checkpoint domain at ledger origin.
PostgreSQL backfills retained history; OTLP emits the complete current cumulative
projection. Disabling or failing one sink changes neither local history nor
another sink's progress. Reusing a checkpoint identity for a different
destination, schema, attribute policy, or ledger is rejected.

## Decisions

### 1. One process with explicit internal boundaries

V1 uses one long-running process and one SQLite writer. This minimizes moving
parts and keeps the fact/cursor/sink-obligation transaction local.

Alternative: separate adapter, ledger, and exporter services. Rejected because
it introduces inter-process delivery and recovery protocols without improving
the v1 trust or accounting boundary.

Trade-off: one process shares a failure domain. The mitigation is durable
transactions, restart-safe replay, component-scoped state, and source/sink
failure containment rather than distributed availability.

### 2. Immutable release profile beside narrow runtime configuration

Evidence-backed limits and semantics live in the embedded release profile.
Operator TOML selects canonical sources, aliases, cadence, projection
allowlists, and sinks; sink secrets use runtime injection. Configuration cannot
add extraction paths, change identity, alter arithmetic, raise limits, or reuse
technical namespaces for a new domain.

Alternative: runtime-tunable profiles. Rejected because a convenient override
could turn unreviewed input, resource, or cardinality behavior into a production
claim and make two installations with the same release behave incompatibly.

Trade-off: upstream drift or an unusual deployment may remain unsupported until
a new measured profile ships. That delay is preferred to silent misaccounting.

### 3. Streaming deny-by-default field projection

Mixed-content JSONL is traversed by a bounded syntax scanner coupled to an
adapter-owned path/type registry. A general-purpose deserialized record never
exists in application memory.

Alternative: deserialize then delete or redact content fields. Rejected because
content would already have been materialized and could escape through
exceptions, logging, hashing, or generic metadata.

Trade-off: the projector and its limit tests are more specialized than ordinary
JSON loading. That complexity directly protects the constitutional privacy
boundary.

### 4. Normalized immutable facts, not raw passthrough

Adapters emit only UsageEvent and QuotaSnapshot values admitted by the closed
ledger schema. Token categories are registered and non-overlapping. Source
unknowns remain unknown, and quota is never converted into a token event.

Alternative: retain raw records and normalize in each sink. Rejected because it
duplicates semantics, leaks source-specific content risk downstream, and makes
history change when consumers change.

Trade-off: adding a legitimate source field requires coordinated extraction,
ledger, and sink review. Permission at one layer intentionally grants none at
another.

### 5. Stable identity plus accounting fingerprint

Native identity says which logical fact is being observed; the canonical
fingerprint says whether a repeated observation carries the same accounting
meaning. It is SHA-256 over RFC 8785 canonical JSON with domain tag
`aiut-accounting-fingerprint-v1`, containing only adapter schema, fact kind,
native identity, source-observed time, registered accounting values, and the
source-derived attribution necessary to interpret them. Collector, ledger, and
source namespaces remain members of the separate composite fact identity; they
are not fingerprint inputs. Ledger sequence, collection time, paths, offsets,
aliases, extension metadata, export allowlists, and sink settings are also
excluded.

Alternative: line number, byte offset, timestamp, or full-record hash as
identity. Rejected because rewrites and relocation change positions, timestamps
can collide or drift, and a full-record hash would include irrelevant or
content-bearing values.

Trade-off: source profiles must prove native identity and fingerprint inputs
before activation. An ambiguous source cannot be accepted merely because it
parses.

### 6. Incremental cursors validated by reconciliation

Per-stream cursors accelerate ordinary polling, while generation and safe
prefix-anchor validation decide whether resume is trustworthy. Failed
validation resets the affected stream to byte zero with empty parser context;
stable identities deduplicate accepted history. Full rescans run after relevant
schema/profile changes and within the active profile's measured deadline and
source envelope.

Alternative: trust offsets forever or rescan everything every poll. The former
can miss mutation; the latter is needlessly expensive and still requires stable
identity. The chosen design makes offsets an optimization and reconciliation
the completeness mechanism.

Trade-off: rescans consume bounded work and can become overdue. Health exposes
that state without falsely declaring loss or blocking otherwise safe
incremental ingestion.

### 7. SQLite is authoritative; sinks are independent projections

Fact acceptance and cursor progress commit locally before any remote delivery.
Each sink retains its own pending checkpoint. OTLP is bounded cumulative
operational state; PostgreSQL is idempotent event-time history.

Alternative: write directly to sinks, use a metrics gateway as the store, or
couple both sinks into one pipeline. Rejected because remote outage would then
erase or block local ownership and one destination would determine another's
correctness.

Trade-off: /data capacity and backup become first-class operational concerns.
The storage-admission profile and no-pruning recovery posture make that cost
explicit.

### 8. Health is local, structured, and non-masking

Per-stream, ledger, sink, and quota state is retained in SQLite and rendered by
a non-networked read-only inspection command. Overall healthy requires every
enabled component to satisfy its own current contract. If health cannot be
persisted, inspection combines stale persisted state with direct read-only
evidence.

Alternative: log-only health or an inbound health server. Rejected because logs
do not provide durable component state and a server expands the runtime boundary.

Trade-off: operators invoke a local command rather than scrape an endpoint.
That is consistent with a personal, no-inbound service.

### 9. Release only with native multi-architecture evidence

The same locked source revision, dependencies, schemas, and profile build both
amd64 and arm64 images. Native runs must agree on normalized facts,
fingerprints, view and health schemas, and metric descriptors before one
immutable manifest list is published.

Alternative: publish one architecture first or rely only on emulation.
Rejected because the v1 portability claim is part of the contract, not a later
packaging enhancement.

Trade-off: release waits for both native gates. A missing architecture result
blocks the v1 manifest rather than weakening the claim.

## Health, Reconciliation, and Failure Containment

The source-stream state machine distinguishes healthy, trailing deferred,
quarantined, storage hold, reconciliation overdue, source envelope exceeded,
retention gap, coverage unknown, and disabled states. Family and global health
must reflect the most severe enabled child state; they cannot mask a degraded
stream because a sibling advanced.

Coverage is deliberately asymmetric:

- before a stream is first discovered, historical coverage is unknown;
- a supported late-readable fact found by rescan is accepted at its source time;
- later source deletion never retracts committed history; and
- disappearance or truncation across a previously discovered stream's
  unconsumed cursor is a proven retention gap.

Failure containment follows the narrowest safe boundary:

| Condition | Containment and recovery |
|---|---|
| Incomplete trailing record below the active byte cap | Defer at its start and retry later; other complete work continues |
| Unknown kind, recognized malformed record, unregistered category, or identity collision | Hold before the record and quarantine only that stream; recovery requires supported parser/profile change or corrected source |
| Truncation, replacement, generation mismatch, or prefix-anchor mismatch | Reset that stream and parser context to the beginning; deduplicate by fact identity and fingerprint |
| Missing or incompatible release profile | Fail startup before source or sink activity |
| Reconciliation deadline missed | Mark stream, family, and global state overdue; safe incremental ingestion may continue but current reconciliation cannot be claimed |
| Supported source envelope exceeded | Degrade the stream, family, and global state; continue only work still bounded by parser and storage profiles |
| Storage admission denied, SQLite full/I/O failure, failed commit, or ambiguous ledger state | Roll back the whole record transaction and hold all source cursors; reopen read-only and verify before writes resume |
| OTLP or PostgreSQL failure | Keep only that sink pending; sources, ledger, and the other sink continue |
| Ambiguous sink acknowledgement | Retry idempotently; never advance a checkpoint from assumption |
| Missing, null, stale, or freshness-unknown quota | Preserve unavailable or freshness state; never substitute zero; independent usage continues |
| Forbidden content or credentials found in retained state | Stop normal collection and affected exports; require an owner-authorized isolated privacy-repair plan and proof |

No v1 override may force-skip a held record, consume an unknown kind, advance a
cursor without its complete-record transaction, abandon pending sink work, or
auto-prune history to recover capacity.

## Release-Profile Evidence Gates

The first OpenSpec changeset freezes every owning domain's profile-member schema
and executable evidence gate; it does not invent exact values that have not yet
been measured. Subject to the proposal's acceptance semantics, the changeset is
archiveable only after the owner explicitly accepts all eleven capability
contracts. Except for a separately accepted disposable synthetic-only spine, no
non-synthetic implementation begins before that complete acceptance.

Each later immutable release profile must supply every applicable domain's exact
measured values and named evidence before that member can activate in v1.
Release-profile governance composes only those accepted domain members and
verifies identity, compatibility, activation, and fail-closed authorization; it
does not become a second owner of domain values. The unresolved values below are
mandatory v1 pre-activation evidence, not optional post-v1 work and not values
this documentation changeset may guess:

| Owning capability / domain | Required evidence before activation | Fail-closed result |
|---|---|---|
| `source-adapter-profiles` / source build, extraction, and parser resources | Pinned upstream/structural evidence and fixture digests for the capability-owned manifests; positive/negative, mutation, replay, record-expansion, and privacy cases; measured parser ceilings and minimum memory with independent and combined-limit vectors on both architectures | Source remains unsupported, or startup/affected stream refuses the profile |
| `event-identity-and-normalization` / identity and arithmetic | Canonical identity/fingerprint and request-identity vectors; evidence selecting the exact permitted Codex arithmetic rule; monotonicity/reset, zero/subtraction, malformed, and ordered mixed-outcome cases | Stream holds as unsupported identity or accounting profile |
| `stream-reconciliation-and-health` / reconciliation | Mutation-detection evidence, measured worst-case scan cost, exact stream-count/bytes/record/append envelope, deadline, anchor/reminder values, and scheduler/clock cases | Reconciliation cannot claim current |
| `durable-local-ledger` / ledger schema and storage admission | Conformance to the capability-owned private tables, constraints, transactions and migration corpus; measured row/index/WAL amplification, reserve/recovery/headroom values, and full/I/O failure injection for whole record sets | Ingestion enters storage hold without any record-set effect or cursor advance |
| `quota-snapshot-semantics` / quota freshness | Source timestamp/window evidence, exact maximum ages and skew values, duplicate-usage/new-quota vectors, and deterministic-selection vectors | Freshness remains unknown or the source profile stays unsupported |
| `local-query-contract` / local views and inspection | Conformance fixtures for the capability-owned stable-view column manifests and health JSON schema, compatibility/migration vectors, and non-masking/read-only failure cases | Query/profile compatibility fails and activation is refused; no alternate private-table contract is exposed |
| `otlp-metrics-projection` / OTLP | Conformance to the capability-owned metric descriptors and vocabulary shape; exact measured tuple set, attribute/series/request ceilings, SDK cap behavior, conservation, collision, retry, and deterministic-batch vectors | Exporter is not instantiated or checkpoint is blocked |
| `postgresql-history-projection` / PostgreSQL | Conformance to the capability-owned columns, types, nullability, constraints, comparisons, and transaction shape; migration, idempotency, ambiguous-acknowledgement, and retry vectors | Checkpoint remains pending |
| `release-profile-governance` / profile composition | Complete member manifests and evidence digests, deterministic profile ID/digest vectors, compatibility cases, and proof that no missing or rejected member can activate | Startup fails before source or sink activity |
| `portable-runtime-and-release` / runtime and release | Locked inputs, measured operation-specific runtime headroom, mount/network/privilege tests, disabled-sink absence, and native amd64/arm64 parity over every applicable domain artifact | No v1 image or manifest is published |

Candidate values in synthetic development are not accepted release values.
Missing bounds, overflow, unmeasured combinations, unknown source semantics, or
profile digest mismatch never fall back to library defaults or operator input.
The capability contracts close the required schemas and evidence gates now;
only the measured values and evidence that instantiate a later immutable v1
release profile remain open.

## Privacy and Operations

Four allowlists remain independent and ordered: source extraction, ledger
admission, PostgreSQL projection, and OTLP attributes/vocabularies. A value
permitted upstream is not automatically permitted downstream. Diagnostics use
only code-owned failure enums, opaque technical IDs, numeric positions, capped
measurements, and state-transition counters. They exclude raw paths, unknown
discriminator text, exception text, source fragments, fingerprints of forbidden
values, and credentials.

The future container has exactly three canonical host-backed source/state
targets: the read-only Claude and Codex session targets and writable `/data`.
The read-only TOML file is a separate configuration surface whose fixed
in-container path and mount preflight belong to `portable-runtime-and-release`;
`/tmp` is ephemeral container scratch, not a canonical host-backed source/state
target. Broad home or tool-configuration mounts, symlinked parents, auth stores,
and writable sources fail preflight. The image runs with a non-zero UID/GID,
read-only root, ephemeral temporary storage, dropped capabilities,
no-new-privileges, and no port.

Local-ledger-only mode has no network. Sink modes allow outbound traffic only
to the configured destination and necessary name resolution. Disabled sinks
instantiate no client, task, credential reader, DNS lookup, checkpoint, or
dependency-specific execution path. Secrets never enter TOML, the ledger,
diagnostics, or image layers.

Accepted normalized history is retained indefinitely. Integrity checks, online
backup, index rebuild, vacuum, and lossless versioned migrations are permitted;
TTL, sampling, logical pruning, aggregate-only replacement, and source-deletion
retraction are not. Backup, migration, checkpoint, and vacuum require their own
profile-backed headroom and may not consume the normal ingestion reserve.

Privacy release tests place synthetic sentinels in every content-bearing and
unregistered location, including malformed and oversized cases, and prove that
no forbidden bytes or digests reach application values, logs, exceptions,
crash output, SQLite, either sink, or network traffic.

## Risks / Trade-offs

- [Upstream formats drift after release] → Unrecognized shapes remain
  unsupported or quarantine the affected stream; a new profile requires pinned
  evidence and replay/mutation vectors.
- [Strict activation gates delay useful collection] → Allow the separately
  accepted synthetic spine to test legibility without real mounts,
  non-synthetic facts, networking, sinks, a production package, or a reusable
  production shortcut.
- [Indefinite retention exhausts /data] → Measure a conservative storage charge
  and reserve, fail admission atomically, expose storage hold, and require
  capacity restoration rather than automatic deletion.
- [A long reconciliation scan consumes excessive resources or starves appends]
  → Profile a supported envelope and deadline, test continuous append and
  interruption, and degrade explicitly when the envelope is exceeded.
- [One-process architecture increases shared crash impact] → Keep source facts,
  cursors, and sink obligations transactional and replay-safe; isolate semantic
  failures by stream and delivery failures by sink.
- [Closed sink vocabularies reduce analytical detail] → Retain full admitted
  normalized history locally, use explicit bounded unknown/other behavior only
  where conservation permits it, and block non-mergeable collisions.
- [Cumulative OTLP delivery is ambiguously acknowledged] → Use a fenced lease,
  deterministic complete-target batches, cumulative replay, and checkpoint
  advancement only after all acknowledgements.
- [PostgreSQL commits but the acknowledgement is lost] → Retry against mandatory
  uniqueness constraints, compare normalized equality, and advance locally only
  after durable confirmation.
- [A migration or downgrade would reinterpret accepted history] → Preserve
  explicit schema/profile IDs, require lossless migrations, and stop for a
  forward repair when rollback compatibility cannot be proved.
- [A privacy defect reaches retained history] → Stop affected activity, preserve
  evidence safely, and require an owner-approved isolated repair with rebuilt
  derivatives and absence proof; privacy repair is not ordinary retention
  policy.
- [Source order differs across installations] → Keep accounting independent of
  traversal order; use stable identities for convergence, source time for
  history, and ledger sequence only for each ledger's durable delivery order.

## Migration Plan

This changeset itself has no deployment migration. Its rollout is an authority
and evidence sequence:

1. Review and accept or reject each capability specification independently.
   Any rejected or unknown required capability blocks archival, every
   non-synthetic implementation path, real-source mounting or fact acceptance,
   sink delivery, and release. Archival requires explicit owner acceptance of
   all eleven capabilities.
2. If the Synthetic-to-SQLite capability is separately accepted, optionally
   build only the disposable synthetic harness and run the bounded human
   legibility exercise. It opens no real source mount, accepts no non-synthetic
   fact, opens no network or sink path, ships no production package, and creates
   no reusable production shortcut.
3. After the complete required capability set is accepted, implement against
   synthetic fixtures with every real adapter profile and sink disabled by
   default.
4. Admit exact release-profile values only through their measured evidence,
   vectors, privacy tests, schema tests, and compatibility review. Profile
   acceptance is domain-specific; an unproved source or sink remains inactive.
5. Exercise local-ledger-only behavior first with explicit read-only mounts only
   after its source profile is activated. Preserve the source-disabled path for
   any unsupported build or shape.
6. Enable OTLP and PostgreSQL independently. Each new checkpoint identity starts
   from ledger origin and proves catch-up, retry, and failure isolation before
   broader operation.
7. Run the same native release gates on amd64 and arm64. Publish no v1 manifest
   until both images pass and parity evidence matches.

Rollback never deletes or rewrites accepted history merely to run older code.
The safe order is:

- stop source ingestion before changing executable, profile, or schema;
- preserve and verify /data and any required backup;
- run an older version only when its profile and schema compatibility with the
  persisted ledger are explicitly proved;
- otherwise keep the ledger read-only and deploy a forward-compatible repair or
  migration;
- disable a failed sink without changing its checkpoint, then resume the same
  identity after repair; use a new identity and origin replay for a changed
  destination or projection schema; and
- return an unsupported adapter to held/disabled state rather than skipping
  input or rolling back facts.

A privacy repair is a separate owner-authorized operation, not a rollback
mechanism.

## Open Questions

No doctrine-, architecture-, or RFC-mandated structural question remains open.
The capability contracts close the extraction-registry and ordered record-set
shapes; normalized identity, fingerprint, request, amount, and quota shapes;
cursor/context and reconciliation state machine; private ledger
tables/constraints/transaction boundary; stable view manifests and structured
health JSON; OTLP descriptor/vocabulary and checkpoint shapes; PostgreSQL
columns/constraints/transaction shape; release-profile envelope; and portable
runtime/release gates. Their owner acceptance approves those testable contracts,
not evidence that an unmeasured release profile has already passed them.

Only two classes of question remain:

- **Measured immutable v1 release-profile evidence:** Which pinned Claude Code
  and Codex build-family and fixture digests prove the closed extraction
  manifests; which official-source and synthetic evidence selects a permitted
  Codex arithmetic rule; and what measured parser ceilings/minimum memory,
  storage charges/reserves/headroom, reconciliation envelope/deadlines/anchor
  and reminder values, quota ages/skew, OTLP tuple and numeric budgets, and
  operation/native-parity evidence instantiate the first activatable profile?
  These values and evidence are mandatory before their domain activates, but
  they are not to be fabricated during capability specification.
- **Safe implementation detail inside the closed contracts:** Which package
  layout, retry timing, SQLite pragmas/indexes, numeric UID/GID, temporary-storage
  size, image registry/name, secret injection, and endpoint-specific DNS/proxy
  wiring provide the simplest reproducible implementation without changing an
  observable requirement?

Each measured answer belongs to its owning domain member; release-profile
governance may only compose accepted answers and their evidence. Each
implementation-detail answer remains subordinate to the accepted contracts.
Neither class authorizes a real source mount, non-synthetic fact, sink contact,
scope expansion, or plausible-value substitution before its gates pass.
