# Engineering Bar

**Status:** Adopted project-specific additions through the lifecycle recorded
in [`../README.md`](../README.md#lifecycle-status).

## Adopted default

This project adopts the repository-wide
[`ai-bootstrap` engineering bar](../../../../about/craft-and-care/engineering-bar.md)
by reference. Its default biases and definition of done apply without being
copied here. There are currently **no project-specific deviations**.

The obligations below are additive. If a future exception to the root bar is
needed, record the exact exception, affected surface, rationale, and removal or
review condition here before relying on it.

## Project-specific definition of done

A non-trivial change is complete only when its evidence shows that:

- no raw source record, prompt, response, credential, or content-derived value
  is decoded into an application value or can enter fingerprints, the ledger,
  views, logs, diagnostics, OTLP output, or PostgreSQL output;
- every source mount remains explicitly read-only and the long-running
  container still runs as a non-root user with a read-only root filesystem,
  write access limited to its state boundary, and no inbound API or port;
- stable identities make every accepted usage event contribute exactly once to
  eventual accounting, and event persistence plus source progress remain one
  transactional SQLite decision;
- replay, overlap, restart, and sink retry cannot double-count an event or lose
  an accepted event;
- source-family adapters keep cursor, quarantine, and health per source stream;
  only exact code/profile dispositions `registered_irrelevant`, `context_only`,
  and `quota_state_only` advance a complete record without a fact, and only with
  their permitted transition and cursor in the same ledger transaction, while
  unknown, unregistered, malformed, collided, or failed records hold before the
  record and quarantine that stream;
- missing profile members or bounds yield `unsupported_profile` before
  traversal, missing or wrongly typed required projected record values yield
  `recognized_malformed`, and only measured bound overflow yields
  `record_limit`;
- incomplete tails hold their stream cursor pending completion, while unrelated
  healthy streams and sinks continue and aggregate health never masks the held
  or quarantined stream;
- normalization preserves the source's accounting meaning rather than
  inventing precision or flattening materially different counters;
- field handling keeps four controls separate: code-owned extraction, stable
  ledger admission/schema, PostgreSQL projection allowlist, and OTLP
  attribute/vocabulary registry; configuration may narrow but never widen them;
- export/configuration changes do not alter logical fact identity or the
  accounting fingerprint, and cursor position is never itself identity;
- OTLP attributes remain bounded and low-cardinality, and PostgreSQL receives
  normalized columns plus only projection-allowlisted metadata in JSONB;
- OTLP and PostgreSQL projection, delivery, and destination-scoped checkpoints
  are independently retryable and observable;
- PostgreSQL database constraints enforce one globally unique ledger sequence
  across usage and quota and exactly one fact-kind-matching child for each
  projected-fact envelope through retry and migration;
- the stable read-only `usage_events`, `usage_event_amounts`, `quota_snapshots`,
  `source_health`, `sink_health`, and `ledger_health` views remain
  sink-independent and compatible;
- ledger schema changes preserve the indefinite local history through a tested,
  transactional migration rather than a silent reset; and
- behavior, contract, or topology changes update the governing spec when one
  exists, the
  [`RFC 0001`](../legends-and-lore/rfcs/0001-adapter-ledger-and-sink-contract.md),
  and topology documentation in the same change.

These obligations operationalize **Local Facts Become User-Owned History**,
**Content and Credentials Stay Outside**, **Accounting Is Eventually Exact**,
**Partial Failure Is Explicit**, **Normalization Preserves Meaning**, and **The
Runtime Boundary Is Portable and Narrow**.

## Review posture

The following are merge blockers, even if happy-path tests pass:

- a parser accepts an unknown shape through a permissive fallback;
- an unknown or malformed record is consumed or the stream cursor advances past
  it;
- a zero-fact cursor commits separately from its permitted parser-context or
  quota-component transition, or a duplicate success clears another active
  health degradation;
- source progress can commit separately from newly accepted events;
- one unhealthy adapter or sink stops healthy, independent work without a
  contract reason;
- a raw source record or unrestricted metadata map crosses an adapter boundary;
- delivery success is inferred from an attempted send rather than durable
  acknowledgement;
- ledger state is discarded to make an upgrade or recovery succeed;
- fixture evidence contains real user content, paths, identifiers, or
  credentials; or
- a dependency or image input is floating, untraceable, or not reproducible.

The author/reviewer evidence and disposition protocol is defined in
[`review-and-documentation.md`](./review-and-documentation.md).

Prefer the smallest design that proves the contract. **Simplicity Serves the
Contract** does not justify weakening accounting, privacy, isolation, or
failure visibility to remove necessary state or tests.
