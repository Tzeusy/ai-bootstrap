# Testing and Verification

Verification is risk-scaled, but every behavior change needs evidence at the
lowest boundary capable of proving it. Happy-path parser examples alone never
prove accounting, privacy, or recovery safety.

## Evidence by change risk

| Change class | Examples | Minimum evidence |
|---|---|---|
| Low | prose clarification, diagnostics wording, internal rename with no stored or emitted shape change | Link and terminology checks; cross-read the affected doctrine, RFC, spec, and standard |
| Medium | pure normalization logic, ledger-admitted metadata field, PostgreSQL projection field, bounded OTLP attribute/vocabulary, non-persistent refactor | Focused unit tests, negative cases, affected synthetic fixtures, and proof that emitted/storage shapes remain intentional |
| High | field-projecting parser or source identity, stream cursor/quarantine, checkpointing, SQLite schema/views/transaction, replay, privacy filter, sink retry/delivery state, container privileges, mount policy | All affected lower-level tests plus failure injection, restart/replay evidence, cross-component integration tests, and an explicit invariant-by-invariant review |
| Release | dependency lock/image change, supported-architecture change, first deployment or migration | High-risk evidence where applicable, deterministic clean build, vulnerability/provenance review, non-root runtime check, read-only mount check, and multi-architecture build verification |

When a change spans classes, apply the highest class. A reviewer may raise the
class when blast radius or uncertainty is greater than the diff suggests.

## Mandatory source fixture corpus

Source fixtures must be fully synthetic. They must contain
no copied prompt, response, credential, private path, account identifier, or
other user content. The maintained corpus must cover:

- repeated Claude assistant messages, proving stable identity and no duplicate
  accounting;
- Codex usage whose model must be attributed from the applicable context,
  including context changes and missing/ambiguous context;
- an incomplete JSONL tail, proving the source is not advanced past data that
  may become complete;
- source truncation and rotation, proving they are distinguished from ordinary
  append progress without loss or duplication;
- Codex primary/secondary rate-limit windows plus the explicit Claude
  `unknown/unavailable` capability, proving missing, stale, and current quota
  states cannot be confused with zero utilization;
- Codex rate-limit-only records that repeat a prior nonzero usage contribution,
  plus cache-write/read and inclusive-output arithmetic boundary vectors;
- replay and overlapping reads, proving accepted events remain exactly
  accounted;
- `registered_irrelevant`, `context_only`, and `quota_state_only` complete
  records, proving only those exact registered dispositions advance with zero
  facts and only with their permitted transition in the same cursor transaction;
  plus unknown-kind, unregistered, malformed complete, oversize, and over-depth
  records, proving every other zero-fact outcome holds and quarantines its
  stream; and
- independent sink retry, proving one sink's failure and recovery neither
  duplicates its delivery nor blocks the other sink.

Every adapter-format bug adds a minimal synthetic regression fixture before or
with its fix. Updating a fixture to match a new upstream schema must not erase
the previous drift case that proved the failure was visible.

## Invariant tests

### Accounting and checkpoints

- Test duplicate, reordered, replayed, and overlapping input.
- Inject failure before and after event insertion and source-progress update;
  after restart, the ledger must contain either the complete transaction or
  none of it.
- Prove an affected source does not advance on unknown schema, ambiguous
  attribution, malformed complete records, or incomplete tails.
- Prove a missing required profile member or parser bound yields
  `unsupported_profile` before traversal, a missing or wrongly typed required
  projected record value yields `recognized_malformed`, and only an observed
  measured-bound overflow yields `record_limit`.
- Prove configuration, alias, PostgreSQL projection, and OTLP attribute changes
  cannot change a committed fact's logical identity or accounting fingerprint.
- Test ledger migrations from every supported prior schema with representative
  history and the stable read-only views. A failed migration must leave the
  prior database usable.
- Inject low-space failure before commit; no fact, stream cursor, or sink
  checkpoint may advance, and existing history must not be silently pruned.

### Failure isolation

- Fail each adapter independently and show other adapters continue.
- Fail one stream within a source family and show sibling streams continue while
  family and global summaries still report degradation.
- Fail OTLP and PostgreSQL independently and together; show accepted events stay
  durable and each destination retains independent projection, retry state, and
  checkpoint ordered by committed ledger progress.
- Prove restart and backoff do not turn an unavailable dependency into silent
  data loss or double delivery.

### Privacy and metadata

- Exercise the real field-projecting streaming parser with high-entropy sentinel
  content and credential values at every unregistered path. An instrumented
  decoder/projector must prove those sentinel scalars are never decoded,
  allocated into the application object graph, copied, or hashed; output scans
  alone do not prove non-materialization.
- Scan normalized facts, accounting fingerprints, SQLite tables and all six
  read-only views—`usage_events`, `usage_event_amounts`, `quota_snapshots`,
  `source_health`, `sink_health`, and `ledger_health`—plus safe diagnostics,
  logs, OTLP capture, and PostgreSQL capture; no sentinel bytes or derived
  values may appear.
- Exercise every declared parser-profile limit at `N-1`, `N`, and `N+1`,
  including encoded versus decoded sizes and a non-terminated record that
  crosses its byte cap. Each breach must immediately produce a bounded safe
  error code, hold the affected stream cursor before the record, and quarantine
  only that stream without decoding skipped values or including raw values in
  diagnostics.
- Prove a field absent from the code-owned extraction registry is never
  materialized; a field absent from stable ledger admission is never stored;
  and fields absent from the PostgreSQL projection allowlist or OTLP
  attribute/vocabulary registry never reach that destination. Configuration
  cannot widen any registry.
- Exhaustively enumerate each OTLP profile's realizable allowed tuples and test
  its per-instrument, process-total, serialized-payload, and effective-SDK limits
  at their boundary. Sum overflow must conserve the ledger total; a gauge that
  cannot be represented safely must block and visibly degrade its projection.
- Verify PostgreSQL's JSONB payload contains only allowlisted metadata and that
  stable normalized fields remain columns.
- Verify PostgreSQL rejects any usage/quota cross-kind reuse of
  `(ledger_namespace,ledger_epoch,ledger_seq)`, enforces exactly one
  fact-kind-matching child per projected-fact envelope, and preserves those
  constraints across idempotent retry and every supported migration.
- Verify quota snapshots preserve source observation time, collection time, and
  fresh/stale/unknown state separately; missing source time never becomes a
  fabricated age.

### Runtime and supply chain

- Start the release image as its declared non-root user.
- Demonstrate resolved source leaves are mounted read-only; symlinked/broad/auth
  roots fail closed; the root filesystem is read-only; and only the deliberate
  state/scratch locations are writable.
- Prove there is no inbound listener or published port. With both sinks disabled,
  prove no sink client, DNS lookup, or other network activity occurs while all
  stable SQLite query/health views remain usable.
- Build from pinned dependency inputs in a clean environment.
- Before release, inspect one OCI image index and natively smoke-test both
  `linux/amd64` and `linux/arm64` for equivalent canonical normalization facts,
  ledger and view results, metric data, health schema, replay behavior, privacy
  checks, non-root/read-only runtime, and local-only mode. Cross-emulation may
  supplement but cannot replace either native gate; a missing gate blocks the
  v1 release tag.

## Evidence before claims

The change record must name the commands or harnesses run, the fixtures
exercised, and any unverified boundary. Evidence must distinguish component
health from end-to-end accounting and delivery. A green process, successful
HTTP call, or accepted database connection is not proof of **Accounting Is
Eventually Exact** or **Partial Failure Is Explicit**.
