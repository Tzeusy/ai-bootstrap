# Observability and Operations

Operational reporting must distinguish "the process is alive" from "each
source stream is current, the ledger is durable, and each sink is caught up."
**Partial Failure Is Explicit**: degraded work continues where safe, but no
degradation is hidden behind an overall healthy status.

## Required health model

Expose independently inspectable state for:

- each source stream: source family, safe stream alias, last successful read,
  last visible failure category, cursor lag, quarantine state, and whether
  progress is blocked by unknown kind, malformed data, ambiguity, incomplete
  tail, truncation, or rotation;
- each source family and the global collector: non-masking summaries that remain
  degraded while any member stream is degraded or quarantined;
- the SQLite ledger: schema/migration state, last successful transaction, and
  rejected/duplicate/accepted event counts sufficient to investigate
  accounting behavior;
- each sink: last attempt, last durable success, retry/backoff state, pending
  delivery position or backlog, and failure category; and
- optional cached observations such as quota state: separate source observation
  and collection time plus explicit fresh/stale/unknown/unavailable status.

With a readable compatible ledger, these states remain inspectable without
either remote sink through the stable read-only SQLite views `usage_events`,
`usage_event_amounts`, `quota_snapshots`, `source_health`, `sink_health`, and
`ledger_health`. When the ledger cannot be opened or read, the non-networked
inspection command instead emits the exact out-of-band `aiut.health/v1`
unavailable-ledger variant without claiming any SQLite-view result, performing a
write, or opening a network path. V1 does not add an inbound health API.

Metric and log labels come only from their code-owned safe registries; they do
not inherit PostgreSQL projection permission. OTLP attributes and values remain
within their separate bounded registry and vocabulary.
Do not put raw paths, source lines, exception payload dumps, credentials, or
unbounded event identities into metric labels.

## Failure behavior

- Only exact dispositions `registered_irrelevant`, `context_only`, and
  `quota_state_only` may advance a complete record without a fact, and only when
  their permitted parser-context or quota-component transition and cursor commit
  atomically in the same ledger transaction. Unknown, unregistered, malformed,
  collided, or failed records quarantine only the affected stream and hold its
  cursor before the record.
- An incomplete JSONL tail remains pending rather than becoming a parse success
  or a discarded error.
- Healthy streams continue committing facts when another stream is degraded,
  but family and global summaries do not report healthy overall.
- Storage hold, quarantine, retention gap, envelope excess, reconciliation
  overdue, trailing tail, and coverage-unknown dimensions remain independently
  latched in their specified precedence until the owning recovery clears; a
  duplicate success cannot overwrite any of them.
- OTLP and PostgreSQL have independent delivery progress and retry. Failure of
  one does not suppress the other or roll back already accepted ledger events.
- A durable sink acknowledgement advances only that destination's ledger-order
  checkpoint.
- Backoff is bounded and observable; recovery drains durable work without
  duplicate accounting.
- A corrupt or incompatible ledger fails explicitly. The service never
  silently deletes, recreates, prunes, or skips indefinite local history to
  regain a healthy status. Unsafe low-space state stops before fact/cursor
  commit and remains explicit.

## Logging and diagnosis

Logs are structured around safe identifiers and actionable state transitions:
stream entered/recovered from quarantine, cursor/checkpoint held/advanced, ledger
transaction failed/committed, sink retry scheduled/recovered, and cached data
became stale. Repeated failures should be rate-limited or aggregated without
erasing first occurrence, current status, or recovery evidence.

Diagnostics must answer:

1. Which component is affected?
2. What safe category of failure occurred?
3. What progress was last durable?
4. What work continues independently?
5. What will retry automatically, and what requires a code/configuration fix?

## Recovery and release evidence

For changes to parsing, persistence, or delivery, demonstrate a failure and
recovery cycle rather than only a clean start. Restart the process across an
in-flight ledger transaction and each sink's retry state; then reconcile source
records, ledger facts, and acknowledged deliveries by stable identity and
sink-independent accounting fingerprint.

Operational readiness for the long-running non-root container includes clean
shutdown, restart, bounded retry, readable per-component health, read-only
source mounts, persistent ledger state, and no forbidden data in logs or
telemetry. This is the operational evidence for **Local Facts Become User-Owned
History** and **Accounting Is Eventually Exact**.
