# Evidence 0001: Synthetic Vector Contract

**Status:** Normative pre-implementation inventory for RFC 0001  
**Date:** 2026-08-10

These vectors define evidence that the first OpenSpec and implementation must
make executable. Every fixture is hand-authored or generated from a local mock;
real session, credential, or application-state bytes are prohibited. Each
vector records the adapter schema ID, release-profile IDs, canonical input
description, expected normalized facts, cursor/health transition, and forbidden
outputs.

## Cross-cutting assertions

Every applicable vector must prove:

- the expected fact identity and RFC 8785 accounting fingerprint;
- accepted, duplicate, deferred, quarantined, storage-held, and sink-checkpoint
  transitions as applicable;
- transaction all-old/all-new behavior across restart;
- no prompt, response, tool-call, credential, raw record, sentinel, or derived
  digest in normalized facts, diagnostics, SQLite, OTLP, PostgreSQL, or crash
  output; and
- sibling-stream and independent-sink progress when the affected boundary is
  scoped rather than global.

## Claude Code usage vectors

| ID | Synthetic case | Expected contract |
|---|---|---|
| `claude-minimal` | Assistant record with synthetic session/request/message IDs, model, timestamp, and four counters | One version-scoped usage fact; inclusive output category; content skipped |
| `claude-optional-zero` | Optional cache counters absent, then present as zero | Absence remains absent; explicit zero remains zero; identity rule unchanged |
| `claude-replay` | Repeat the exact fully synthetic assistant record across lines, files, and rescans | One fact and one request contribution; timestamp remains source time/fingerprint input |
| `claude-request-id-reuse` | Deliberately non-conforming mock header sequence A/B/A across separate exchanges, with changed record timestamps | Reused vendor-unique identity with changed fingerprint holds and quarantines the stream |
| `claude-collision` | Same native identity with changed accounting field, model, or source time | Hold and quarantine before conflicting record |
| `claude-missing-identity` | Missing session ID or request ID | Recognized malformed; no fallback to path, offset, or message content |
| `claude-multi-record` | Several physical records for one synthetic request | Evidence-backed native identity, not line count, controls accounting |
| `claude-output-inclusive` | Synthetic response with and without a structural thinking breakdown | Base output maps to inclusive/unclassified; non-reasoning derivation only when proven non-negative |
| `claude-quota-unavailable` | No admitted quota source | Capability and health report `unknown/unavailable`, never zero |
| `claude-global-state-rejected` | Credential-bearing global-state path offered as a source | Startup fails closed without opening or projecting it |

## Codex usage and quota vectors

| ID | Synthetic case | Expected contract |
|---|---|---|
| `codex-usage-advance` | Session metadata, preceding turn context, then componentwise cumulative increase | One normalized delta with same-stream attribution |
| `codex-rate-only-repeat` | Rate-limit-only event with unchanged total and repeated nonzero last usage | No usage fact or request increment; rate-limit snapshot may advance |
| `codex-info-null` | Token-count event with absent usage info and present/absent rate limits | No invented usage; available quota processed independently |
| `codex-context-change` | Two contexts and later usage | Latest preceding same-stream context applies; no look-ahead/cross-stream use |
| `codex-context-missing` | Usage advancement without required session/model context | Hold and quarantine rather than guess |
| `codex-cache-arithmetic` | Cache-write, cache-read, total input, reasoning, and total output at valid boundaries | Profile-frozen inclusive relationships derive non-overlapping categories exactly |
| `codex-arithmetic-invalid` | Cache or reasoning component exceeds its inclusive total | Hold and quarantine; no negative amount |
| `codex-total-unchanged` | Same cumulative vector with repeated or changed last usage | No new usage contribution; inconsistent payload follows profile error rule |
| `codex-total-decrease` | Any cumulative component decreases | Hold and quarantine as schema/stream inconsistency |
| `codex-delta-mismatch` | Cumulative difference disagrees with stored contribution | Hold until the adapter profile defines and validates the source case |
| `codex-non-request-emission` | Context-window fill, recomputation, compaction, or rate update without request advancement | No request contribution |
| `codex-quota-bounds` | Primary/secondary window at 0% and 100%, nullable reset/limit identity, repeated snapshot | Normalize `0..100` to `0..1`; preserve time/evidence; replay is idempotent |

## Parser and privacy vectors

- Generate exact `N-1`, `N`, and `N+1` cases for every parser-profile limit:
  record bytes excluding delimiter, root-counted depth, encoded key bytes,
  structural/projected scalar counts, and every path's encoded/decoded size,
  multiplicity, integer/decimal range, precision, and scale.
- Cross the raw record byte limit without a newline; quarantine immediately
  rather than buffering indefinitely or classifying it as an incomplete tail.
- Split input at every UTF-8 code-unit, JSON escape, numeric lexeme, key,
  delimiter, and chunk boundary while keeping semantic output invariant.
- Place the discriminator before and after large skipped content; skip-only
  values remain subject to structural limits but never invoke a scalar decoder.
- Put high-entropy synthetic sentinels in content, tool arguments/results,
  attachments, unregistered keys, malformed values, nested arrays/objects,
  exceptions, and oversize fields. Instrumentation must show zero forbidden
  decoder/materializer/fingerprint calls.
- Cover registered irrelevant, unknown discriminator, recognized malformed,
  incomplete tail, truncation, replacement, rotation, and same-path new
  generation. Only registered irrelevant records may advance without a fact.

## Identity and reconciliation vectors

- Vary field order and JSON formatting while requiring the same canonical
  fingerprint; vary a fingerprint participant and require a different digest.
- Vary alias, absolute project path, scan path, byte offset, export selection,
  destination, retry, and collection time while requiring unchanged fact
  identity/fingerprint.
- Mutate a record before the resume anchor while preserving file size and mtime;
  scheduled full reconciliation must detect the change.
- Restart midway through reconciliation; only a successful completion resets
  the durable deadline.
- Exercise truncation, replacement, rotation, schema change, clock movement,
  continuous append at the supported rate, and exactly-at/one-beyond the
  supported source envelope.
- Cross each envelope dimension independently at `N+1`; require
  `source_envelope_exceeded` on stream/family/global health, bounded safe
  incremental progress, and no claim that reconciliation is current.
- When the profile deadline is missed, preserve safe incremental behavior but
  make stream, family, and global health `reconciliation_overdue`; never report
  the corpus as fully reconciled.
- Start with a source absent and prove coverage remains `coverage_unknown`;
  separately delete or truncate a previously discovered synthetic stream across
  its unconsumed cursor and require an explicit `retention_gap`.

## Ledger and storage vectors

- Inject `ENOSPC`, `SQLITE_FULL`, `SQLITE_IOERR`, failed sync/commit, and
  ambiguous connection state at journal/WAL creation, page write, commit,
  checkpoint, migration, and health update using both a VFS injector and a
  quota-limited filesystem.
- Fill the filesystem after admission precheck but before commit; prove the
  precheck is not trusted as a guarantee.
- Kill and restart at every transaction phase; fact, amounts, aggregate,
  `ledger_seq`, cursor, and sink obligation must be all old or all new.
- Preserve `ledger_storage_hold` across restart and resume only after the
  profile's higher threshold plus a successful integrity/transaction retry.
- Fail the health-state write itself; on inspection and restart, recompute the
  live admission/database state and expose `storage_hold` or
  `ledger_unavailable` without depending on the stale persisted health row.
- Prove no sink send begins when its acknowledgement cannot be durably recorded.
- Derive backup, migration, checkpoint, and `VACUUM` headroom from current
  database and auxiliary-file size; maintenance never consumes the ingestion
  reserve or prunes retained facts.

## OTLP and PostgreSQL vectors

- Enumerate the exact allowed attribute tuples for every instrument and compare
  them with startup's count of resource, scope, metric, and point-attribute
  series identity.
- Test `N` and `N+1` for each per-instrument cap, process-total cap, UTF-8 value
  cap, serialized-request cap, and effective SDK/exporter limit.
- Require deterministic startup rejection for a profile whose unrelated
  vocabulary cross-product exceeds the realizable tuple budget.
- For monotonic sums, prove ordinary plus the one reserved overflow series equals
  the complete ledger aggregate through the acknowledged sequence within every
  mandatory accounting partition, including each token category.
- For non-mergeable quota/freshness gauges, an unknown tuple blocks and visibly
  degrades that projection; it is neither silently dropped nor collapsed into an
  ambiguous label.
- Repeat ambiguous OTLP delivery and PostgreSQL upserts; local accounting and
  destination checkpoints remain idempotent and independent.
- Enable a sink after retained history exists: PostgreSQL backfills every
  retained fact and OTLP emits the complete current cumulative projection.
- Force OTLP catch-up across multiple deterministic request-size-bounded batches;
  fail after each boundary and prove the checkpoint advances only after every
  batch for one target sequence is durably acknowledged.
- Attempt to project prompt/content, path, session, raw identity, unbounded
  metadata, or unregistered JSONB; every destination rejects it before send.

## Architecture and release vectors

Run the same parser-limit, Unicode/numeric, privacy, identity, reconciliation,
ledger/storage, OTLP, PostgreSQL, mount, non-root, read-only-root, no-listener,
and local-only network corpus natively on `linux/amd64` and `linux/arm64`.
Record source revision, dependency/base-image resolution, native runner
architecture, child image digest, and profile IDs. Compare canonical facts,
fingerprints, logical SQLite schema/view results, metric descriptors/data
points, and health schema. Raw SQLite files, protobuf byte ordering, and runtime
timestamps are not parity targets. The v1 image index and release tag remain
blocked until both native gates pass.
