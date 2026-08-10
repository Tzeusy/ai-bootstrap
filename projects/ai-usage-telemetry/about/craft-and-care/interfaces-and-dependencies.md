# Interfaces and Dependencies

The project's stable seams are adapters, normalized events, the transactional
SQLite ledger, independent sink delivery, and the narrow container boundary.
Keep those seams small enough to reason about and strict enough to protect
accounting and privacy.

The exact adapter, event identity, checkpoint, ledger, and sink contracts belong
in
[`RFC 0001`](../legends-and-lore/rfcs/0001-adapter-ledger-and-sink-contract.md).
This file defines how changes to those contracts must be engineered.

## Adapter interface

A source family adapter interprets one tool-format domain. Runtime owns
canonical mount validation and returns `ValidatedSourceHandle`; generic stream
discovery owns stay-beneath traversal/generation; the adapter owns its filename
predicate, extraction manifest, source fields/evidence, and parser context.
Source-independent domain interfaces own `UsageEvent`, `QuotaSnapshot`,
identity, canonical instant, cwd basename, categories, fingerprints, and age.
An adapter change must preserve these reviewable properties:

- it consumes an injected `ValidatedSourceHandle`, generic discovery results,
  and ledger/storage-owned `AdmissionDecision=permitted`; tests use fakes and
  adapter code imports no concrete runtime/storage preflight;
- it supplies registered fields/evidence to domain interfaces and emits their
  normalized values, never raw records or adapter-local identity/time/path/
  category/fingerprint/age implementations;
- it distinguishes admitted records, the exact zero-fact dispositions
  `registered_irrelevant`, `context_only`, and `quota_state_only`, incomplete
  tails, duplicates, unknown kinds, unregistered kinds, and malformed complete
  records;
- only those three registered zero-fact dispositions may advance a complete
  record without a fact, and only when the permitted parser-context or
  quota-component transition and cursor commit in the same ledger transaction;
  unknown, unregistered, malformed, collided, or failed records hold before the
  record and quarantine that stream;
- a missing required profile member or bound leaves the source
  `unsupported_profile` before traversal, a missing or wrongly typed required
  projected record value is `recognized_malformed`, and only a measured bound
  overflow is `record_limit`;
- it does not advance source progress until accepted events and progress can be
  committed transactionally;
- it owns a typed, code-owned extraction registry and field-projecting parser
  that cannot be widened by configuration; and
- schema uncertainty stops that adapter at the last durable position rather
  than invoking a permissive best-effort parser.

New adapters must fit this interface without adding source-specific branches to
the core ledger or sinks. If a source genuinely cannot satisfy the contract,
change the RFC and specs explicitly instead of hiding a bespoke bypass. This is
how **Normalization Preserves Meaning** and **Simplicity Serves the Contract**
reinforce rather than weaken each other.

## Ledger and persistence interface

SQLite is the local accounting authority. Stable fact identity and stream
progress share a transaction; identity and the accounting fingerprint exclude
cursor position and export/configuration choices. Sink state is durable and
independent per destination. The local ledger is retained indefinitely; source
rotation/deletion does not retract admitted facts.

The ledger/storage provider alone returns `AdmissionDecision`; the stream-health
domain alone owns pure `LatchSet` transition/precedence/recovery. SQLite stores
proposed latch rows and a checked cache without recreating that policy. The
ledger also owns `LedgerProjectionReader`, the only sink-facing read/checkpoint
seam.

- Schema changes require versioned, transactional, restart-safe migrations and
  representative migration fixtures.
- Migration failure leaves existing history intact and visibly blocks the
  affected operation.
- No compatibility shim may reinterpret old counters silently. Preserve their
  meaning or migrate them explicitly.
- The local-query-owned stable read-only `usage_events`,
  `usage_event_amounts`, `quota_snapshots`,
  `source_health`, `sink_health`, and `ledger_health` views are part of the v1
  local interface;
  migrations preserve their documented meaning without requiring an inbound API.
- PostgreSQL is an output, not a replacement checkpoint or source of truth.
  Its stable query fields are normalized columns; extension metadata is
  allowlisted JSONB.

## Sink interface

OTLP and PostgreSQL projection/delivery are separate consumers of committed
ledger facts through `LedgerProjectionReader`. They never import or query the
public stable views or private ledger tables.

- Each destination records its own attempt, durable acknowledgement, ledger-order
  checkpoint, and retry state; a destination change cannot silently inherit a
  different destination's checkpoint.
- One sink's outage cannot block collection or the other sink's progress while
  the ledger remains writable.
- Retry is safe under timeout and ambiguous acknowledgement; tests must prove
  the chosen idempotency behavior.
- OTLP uses its own intentionally bounded attribute/vocabulary registry and
  cumulative projection semantics. Adding a dimension or value requires
  cardinality, reset/continuity, and privacy review.
- PostgreSQL uses a separate projection allowlist; schema changes keep stable
  normalized columns and allowlisted JSONB semantics explicit and
  migration-tested. Its shared projected-fact envelope must database-enforce one
  globally unique `(ledger_namespace,ledger_epoch,ledger_seq)` across usage and
  quota plus exactly one fact-kind-matching child row.
- Configuration may narrow either projection but never changes extraction,
  ledger admission, fact identity, or the accounting fingerprint.

## Format drift and compatibility

Upstream local-file formats are dependencies even when they are not libraries.
Treat a schema change as an interface change:

1. recreate the minimum failing shape as a fully synthetic fixture without
   copying source values;
2. prove the old adapter quarantines the affected stream visibly without
   advancing its cursor;
3. update parsing and normalization without weakening unknown-field handling;
4. prove replay from the held stream cursor accounts every event once; and
5. update the RFC/spec when event meaning or attribution changed.

Backward compatibility is mandatory for persisted ledger history, stable local
views, active stream cursors, and sink checkpoints. Internal code paths with no
external or persisted consumer should migrate atomically and be removed rather
than maintained in parallel.

## Dependency and image discipline

- Runtime and build dependencies are pinned through deterministic lock or
  digest inputs; floating tags and unconstrained resolver results are not
  release inputs.
- Every dependency has a named purpose and provenance. Prefer standard-library
  or already-governed capabilities when they satisfy the contract.
- Upgrades include focused contract tests and a review of transitive, security,
  image-size, and supported-architecture effects.
- Generated clients, schemas, or artifacts keep their generator and
  regeneration command alongside the source contract.
- The release image builds reproducibly for every supported architecture and
  runs equivalent normalization, schema/view, privacy, replay, and local-only
  smoke tests as the declared non-root user on `linux/amd64` and `linux/arm64`.

These requirements implement **The Runtime Boundary Is Portable and Narrow**;
they do not require a particular build system or registry, only reproducible
and reviewable results.
