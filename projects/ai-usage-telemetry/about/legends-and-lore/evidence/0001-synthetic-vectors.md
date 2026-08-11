# Evidence 0001: Synthetic Vector Contract

**Status:** Exact-byte authority is external to this normative
pre-implementation inventory; see the central
[lifecycle matrix](../../README.md#lifecycle-status)
**Date:** 2026-08-10

These vectors define evidence that the first OpenSpec and implementation must
make executable. Every fixture is hand-authored or generated from a local mock;
real session, credential, or application-state bytes are prohibited. Each
vector records the adapter schema ID, release-profile IDs, canonical input
description, expected normalized facts, cursor/health transition, and forbidden
outputs.

## Cross-cutting assertions

Every applicable vector must prove:

- the expected fact identity and RFC 8785 accounting fingerprint, with every
  amount/cumulative-counter leaf represented by the domain-owned canonical
  non-negative signed-64-bit decimal string rather than a JSON number;
- accepted, duplicate, deferred, quarantined, storage-held, and sink-checkpoint
  transitions as applicable;
- transaction all-old/all-new behavior across restart;
- no prompt, response, tool-call, credential, raw record, sentinel, or derived
  digest in normalized facts, diagnostics, SQLite, OTLP, PostgreSQL, or crash
  output; and
- sibling-stream and independent-sink progress when the affected boundary is
  scoped rather than global.

Every privacy oracle is two-sided. Each application-value, parser-
instrumentation, log, exception, crash-output, SQLite, OTLP, PostgreSQL, image-
filesystem/layer, environment, and packet/network capture receives a distinct
harmless content-free positive-control canary and must prove it was observed.
Separate deliberate test-only sentinel-leak, forbidden-decoder/materializer/
fingerprint-call, and unexpected-network-event mutations must make the harness
fail. Canary and mutation values are synthetic and contain no real content,
credential, identifier, or path.

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
| `codex-quota-absent` | Supported token-count record omits `/payload/rate_limits` | Quota component becomes `absent`; no quota fact or zero utilization is fabricated |
| `codex-quota-identity-only` | Admitted non-null rate-limits object contains only exact profile-allowed identity/context members and no registered primary/secondary window object | Exact `state_only` zero-fact quota transition and cursor commit atomically |
| `codex-quota-window-missing-utilization` | A registered primary or secondary window object is present without required `used_percent` | Whole record is `recognized_malformed`; usage/quota/component/cursor effects all roll back |
| `codex-quota-window-mistyped-utilization` | A registered window's `used_percent` has the wrong JSON type | Whole record is `recognized_malformed`; it is not `state_only` or `record_limit` |
| `codex-quota-window-out-of-range-utilization` | A registered window's decimal `used_percent` is below 0 or above 100 | Whole record is `recognized_malformed`; no clamp, zero, snapshot, or cursor effect is permitted |

## Parser and privacy vectors

- Generate exact `N-1`, `N`, and `N+1` cases for every parser-profile limit:
  record bytes excluding delimiter, root-counted depth, encoded key bytes,
  structural/projected scalar counts, and every path's encoded/decoded size,
  multiplicity, integer/decimal range, precision, and scale.
- For every token amount and cumulative-counter path, parse exact integers at
  `9007199254740991` (`2^53-1`), `9007199254740992` (`2^53`),
  `9007199254740993` (`2^53+1`), and `9223372036854775807`; require distinct
  domain-owned decimal-string bytes in fingerprints, Codex native fact/request
  identities, and release-profile bounds. Reject JSON-number use at those RFC
  8785 boundaries, signed or leading-zero strings, `9223372036854775808`, and
  parser/arithmetic overflow while keeping admitted internal and SQL values as
  exact integers.
- Cross the raw record byte limit without a newline; quarantine immediately
  rather than buffering indefinitely or classifying it as an incomplete tail.
- Split input at every UTF-8 code-unit, JSON escape, numeric lexeme, key,
  delimiter, and chunk boundary while keeping semantic output invariant.
- Place the discriminator before and after large skipped content; skip-only
  values remain subject to structural limits but never invoke a scalar decoder.
- Permute JSON member order and transport chunk boundaries across compound
  records containing an unregistered discriminator, unlisted descendants,
  invalid UTF-8, invalid JSON structure, one or more exceeded ceilings, missing
  or mistyped projected fields, an unregistered category, and an identity
  collision. The exact phase/failure precedence must be byte- and chunk-order
  independent: unsupported profile and runtime/storage preflight occur before
  traversal; then `record_limit` outranks structural/UTF-8
  `schema_inconsistent`, which outranks `unknown_kind`,
  `recognized_malformed`, and `unregistered_category`; only a parser-successful
  candidate set can reach `identity_collision`. An unregistered discriminator
  holds, while an unlisted descendant remains skip-only.
- Put high-entropy synthetic sentinels in content, tool arguments/results,
  attachments, unregistered keys, malformed values, nested arrays/objects,
  exceptions, and oversize fields. Instrumentation must show zero forbidden
  decoder/materializer/fingerprint calls.
- Cover unknown discriminator, recognized malformed, incomplete tail,
  truncation, replacement, rotation, and same-path new generation. Inventory
  all three complete zero-fact dispositions independently:
  `registered_irrelevant` commits unchanged parser context plus cursor;
  `context_only` commits its exact parser-context transition plus cursor; and
  `quota_state_only` commits its exact quota-component transition plus cursor.
  Each transition is all-old or all-new across injected failure and restart and
  creates no fact, sequence, amount, aggregate, request, or sink obligation.

## Identity and reconciliation vectors

- Vary field order and JSON formatting while requiring the same canonical
  fingerprint; vary a fingerprint participant and require a different digest.
- Pair otherwise-equal events and Codex cumulative landmarks across the
  `2^53-1`, `2^53`, `2^53+1`, and signed-64-bit-maximum boundaries; each
  distinct integer must produce distinct canonical fact/request identity or
  fingerprint bytes without IEEE-754 coercion, while equal integers from
  different source JSON spellings converge on the one decimal-string form.
- Vary alias, absolute project path, scan path, byte offset, export selection,
  destination, retry, and collection time while requiring unchanged fact
  identity/fingerprint.
- Freeze POSIX and Windows lexical path-flavor vectors for source working-
  directory attribution: filesystem roots map to null; nested working
  directories map to the nested final component rather than an ancestor;
  non-repository directories map to their own final component; invalid or
  unavailable cwd maps to null; and presentation aliases never enter the fact.
- Configure Claude and Codex with equal `source_namespace` values and, in a
  second compound vector, equal native stream identities. TOML validation must
  reject the namespace collision before component registration, traversal, or
  fixed-clock health serialization. The valid distinct-namespace control must
  produce byte-identical ordered health JSON at a fixed clock across restart.
- Mutate a record before the resume anchor while preserving file size and mtime;
  scheduled full reconciliation must detect the change.
- With coverage, reconciliation, and storage already latched, trigger a
  generation/anchor mismatch that proves no unconsumed loss. Safe invalidation
  must reset only cursor/context to byte zero, add no latch or degradation,
  preserve every prior latch and evidence byte, derive `storage_hold` as the
  highest active state, reveal reconciliation then coverage as their owning
  clears occur, and report `healthy` only after all latches are clear.
- Exercise an independently implemented source-health summary oracle for every
  individual and overlapping stream latch (`quarantine`, `storage`,
  `retention`, `envelope`, `reconciliation`, `tail`, and `coverage`), enabled
  `unsupported_profile` and `unsupported_accounting_profile` components, and
  disabled components. Every enabled non-healthy component must make its
  family/global summary `degraded`; a disabled component must create no stream,
  cursor, or fact and is excluded from enabled aggregation; a summary with only
  disabled components must report `disabled`.
- Restart midway through reconciliation; only a successful completion resets
  the durable deadline.
- Exercise truncation, replacement, rotation, schema change, clock movement,
  continuous append at the supported rate, and exactly-at/one-beyond the
  supported source envelope.
- Cross each envelope dimension independently at `N+1`; require
  `source_envelope_exceeded` on the affected stream and `degraded` family/global
  summaries, bounded safe incremental progress, and no claim that reconciliation
  is current.
- When the profile deadline is missed, preserve safe incremental behavior but
  make the affected stream `reconciliation_overdue` and family/global summaries
  `degraded`; never report the corpus as fully reconciled.
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
- For PostgreSQL schema creation, idempotent retry, and every supported prior-
  schema migration, commit-time negative fixtures separately attempt a
  `projected_facts` envelope with both child pointers null, both pointers set,
  the selected pointer under the wrong fact kind, an orphaned envelope or
  child, and usage/quota reuse of one `(ledger_namespace,ledger_epoch,
  ledger_seq)`. Every case must fail all-old-or-all-new without checkpoint
  movement; the matching positive control must commit exactly one deferred
  envelope/child pair.
- Project source, collection, and nullable reset instants whose checked Unix-
  nanosecond values are equal, adjacent by `1ns`, zero, and signed-64-bit
  maximum. Require exact `bigint` round trips and retry equality; reject a
  semantic `timestamptz` column, negative/overflow input, any microsecond
  rounding or adjacent-instant collapse, and any migration/backfill that cannot
  preserve every bit. Operational `projection_checkpoints.updated_at` remains
  outside fact equality.

## Timestamp and age vectors

- Parse offset-bearing RFC 3339 values into checked non-negative signed-64-bit
  UTC Unix nanoseconds, reject leap seconds and out-of-range instants, and render
  the one canonical fixed-nine-digit `Z` form. Equivalent offsets must produce
  byte-identical fingerprint input.
- Round-trip pairs of valid RFC 3339 instants one nanosecond apart through the
  PostgreSQL projector's checked `bigint` source, collection, and reset columns;
  they must remain distinct through insert, retry, migration, and backfill, with
  no host-datetime or `timestamptz` conversion on the authoritative path.
- At a fixed collection/export clock, cover source time at `+skew`,
  `+skew+1ns`, `+1ns`, equal time, `-1ns`, exact freshness deadline,
  deadline `+1ns`, and export ages immediately below/at/above each whole-second
  boundary. Tolerated future time is fresh with age zero; beyond-skew time is
  malformed; nonnegative age seconds is floor of clamped nanosecond age.

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

## Human-legibility vector

Starting from the qualified empty harness after the one documented setup
command, an eligible developer may use no more than six stable-view or health
commands. The run passes the time boundary at exactly
`elapsed_time <= 10 minutes`; exactly ten minutes is admitted and any greater
elapsed time fails visibly. The oracle must also prove every required answer,
replay-neutral counts, and no private-table query. This capability target
deliberately tightens the immutable launch instrument's one 15-minute sitting
ceiling; it does not contradict or rewrite that historical parameter or its
administration record.
