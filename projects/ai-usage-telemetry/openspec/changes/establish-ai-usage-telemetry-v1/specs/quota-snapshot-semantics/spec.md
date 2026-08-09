## ADDED Requirements

### Requirement: [TARGET-STATE] Explicit V1 Quota Capability Matrix
MUST report Claude usage `supported` with Claude quota `unavailable`, and Codex usage plus registered rate-limit snapshots `supported` only when an active source profile admits their structure; persist the latest closed quota component outcome atomically as exactly `disabled`, `coverage_unknown`, `unavailable`, `absent`, `null`, `state_only`, or `observed`; define `coverage_unknown` as an enabled quota-capable source before its first eligible admitted record in the active coverage namespace, define Codex `absent` as no `/payload/rate_limits` member, `null` as an explicit JSON null member, `state_only` as an admitted non-null rate-limits object with identity/context but no registered window carrying a complete utilization, and `observed` as at least one committed snapshot from the record; and keep those availability states distinct from snapshot freshness `fresh|stale|unknown` and from numeric zero.

ID: REQ-quota-snapshot-semantics-001
Source: RFC 0001 § Evidence Baseline; § QuotaSnapshot
Scope: v1-mandatory

#### Scenario: Structurally present Codex quota is represented
- **WHEN** an accepted Codex token-count record contains a registered primary or secondary rate-limit window
- **THEN** each window is eligible to produce its own normalized quota snapshot

#### Scenario: Missing capability is not zero
- **WHEN** Claude quota is requested or Codex `rate_limits` is absent or null
- **THEN** the result reports `unavailable`, `absent`, or `null` as applicable and emits no fabricated zero snapshot

#### Scenario: State-only rate-limit object remains fact-free
- **WHEN** a supported Codex record has an admitted non-null rate-limits object but no registered window with complete utilization
- **THEN** quota component state becomes `state_only` in the same transaction as cursor progress and no quota fact, utilization, sequence, or sink obligation is created

#### Scenario: Disabled and newly enabled quota registrations are explicit
- **WHEN** a configured source is disabled, or a quota-capable source is enabled before its first eligible record in the active namespace
- **THEN** the collector MUST persist quota availability `disabled` or `coverage_unknown` respectively, MUST emit no quota fact, and MUST transition from `disabled` through `coverage_unknown` to the exact first observed `absent|null|state_only|observed` outcome; `disabled` remains healthy-by-contract while `coverage_unknown` contributes unknown freshness wherever quota currency is required

### Requirement: [TARGET-STATE] Closed QuotaSnapshot and Fingerprint Shape
MUST admit a `QuotaSnapshot` only with canonical fact identity, SHA-256 fingerprint, nullable registry-derived source-observed time, collected time, nullable configured account alias, vendor, limit name, native limit, window, and scope identities, canonical utilization decimal in inclusive `0.0..1.0`, optional window minutes, reset time, and scope, recorded freshness state, one exact evidence enum, and empty v1 metadata; absent account alias MUST remain null without a default, is presentation-only, and is never a quota subject or fact-identity member; its fingerprint MUST be SHA-256 over `UTF-8("aiut-accounting-fingerprint-v1\n")` plus RFC 8785 canonical UTF-8 JSON of exactly `{"adapter_schema_id":string,"fact_kind":"quota_snapshot","native_identity":json,"source_observed_at":RFC3339-UTC-string-or-null,"quota":{"vendor":string,"native_limit_identity":string,"limit_name":string,"utilization":canonical-decimal-string,"native_window_identity":string,"window_minutes":non-negative-integer-or-null,"reset_at":RFC3339-UTC-string-or-null,"native_scope_identity":string,"scope":string-or-null,"freshness_evidence":enum}}`, excluding collected time, account alias, current freshness state, paths, metadata, and sinks.

ID: REQ-quota-snapshot-semantics-002
Source: RFC 0001 § QuotaSnapshot
Scope: v1-mandatory

#### Scenario: Source percentage normalizes without added precision
- **WHEN** a registered source value from `0` through `100` percent is admitted with its native precision
- **THEN** utilization is represented as the exact decimal divided by `100` in inclusive `0.0..1.0` without adding precision
- **AND** the canonical fingerprint document contains only the declared fields

#### Scenario: Invalid utilization is rejected
- **WHEN** conversion yields a value outside `0.0..1.0`, requires invented precision, or lacks a required identity or evidence enum
- **THEN** the snapshot is rejected rather than coerced

### Requirement: [TARGET-STATE] Immutable Quota Identity and Collision Handling
MUST define the immutable quota-subject key as RFC 8785 canonical JSON of `[collector_namespace,ledger_namespace,adapter_schema_id,source_namespace,vendor,native_limit_identity,native_window_identity,native_scope_identity]`, define each fact identity by the generic composite tuple whose source-native Codex value is `[session_id,limit_id,window_name,record_timestamp]`, enforce mandatory uniqueness, and treat same-identity and same-fingerprint as duplicate while quarantining different normalized values without overwrite.

ID: REQ-quota-snapshot-semantics-003
Source: RFC 0001 § QuotaSnapshot; § Source-Specific V1 Attribution → Codex rollouts
Scope: v1-mandatory

#### Scenario: Replayed snapshot is idempotent
- **WHEN** the same source observation of the same vendor, limit, window, scope, and source time is replayed unchanged
- **THEN** one quota fact remains and no new ledger sequence or sink work is created

#### Scenario: Mutated quota identity quarantines
- **WHEN** the same native quota identity reappears with different utilization, window, reset, scope, or freshness evidence
- **THEN** no replacement row is committed and the source stream is quarantined

### Requirement: [TARGET-STATE] Exact Freshness Profile and Evidence Semantics
MUST require each accepted source-and-limit member to provide immutable unsigned `maximum_age_seconds` and `allowed_future_skew_seconds` with measurement digest and native evidence, and MUST restrict `freshness_evidence` to exactly `record_timestamp`, `record_timestamp_and_window`, `record_timestamp_and_reset`, `record_timestamp_window_and_reset`, or `missing_source_timestamp`; freshness is `fresh` through the inclusive maximum-age deadline, `stale` on the first later instant, `unknown` when source time is absent, and malformed when source time exceeds collected time by more than the inclusive skew, while collected time never substitutes for source time or enters the fingerprint.

ID: REQ-quota-snapshot-semantics-004
Source: RFC 0001 § QuotaSnapshot
Scope: v1-mandatory

#### Scenario: Exact freshness boundary is deterministic
- **WHEN** source time is known and age equals the active member's `maximum_age_seconds`
- **THEN** recorded freshness is `fresh`
- **AND** the first representable later instant is `stale`

#### Scenario: Missing or future source time cannot look fresh
- **WHEN** source time is absent or lies beyond the accepted future-skew bound
- **THEN** state is respectively `unknown` or malformed and never made fresh by collection time
- **AND** a missing measured threshold keeps that quota member inactive

### Requirement: [TARGET-STATE] Deterministic Current-Quota Selection
MUST group current quota by the immutable quota-subject key, exclude null source times from a current claim, choose the eligible snapshot with greatest source-observed time, break exact time ties by lexicographically least canonical fact-identity bytes, and return `unknown` when no eligible observation exists, without using collected time, aliases, scan order, or sink arrival order.

ID: REQ-quota-snapshot-semantics-005
Source: RFC 0001 § QuotaSnapshot
Scope: v1-mandatory

#### Scenario: Latest source observation wins
- **WHEN** a subject has multiple eligible snapshots with different source-observed times
- **THEN** the greatest source-observed time is selected regardless of collection or scan order

#### Scenario: Tie and null handling are stable
- **WHEN** two source times tie or every observation has null source time
- **THEN** the lexicographically least fact identity wins the tie or current state is `unknown`, respectively

### Requirement: [TARGET-STATE] Query-Time Freshness Recalculation
SHALL make the read-only quota view emit one `component_state` row for each registered quota component and one `snapshot` row per retained fact, recompute current snapshot `fresh` or `stale` and `age_seconds` against inspection time using the immutable source-and-limit threshold while preserving recorded evidence, source time, collection time, and observation state, and keep `unavailable`, `absent`, `null`, `state_only`, stale, and unknown queryable under their exact fact/null rules without making a live-vendor-quota claim.

ID: REQ-quota-snapshot-semantics-006
Source: RFC 0001 § QuotaSnapshot; § Event Time and Projection Time
Scope: v1-mandatory

#### Scenario: Fresh snapshot ages without mutation
- **WHEN** a formerly fresh snapshot passes its threshold without a new record
- **THEN** read-only inspection reports it `stale` while preserving its original evidence and timestamps
- **AND** no retained fact is rewritten

#### Scenario: Unknown observation remains queryable
- **WHEN** a snapshot lacks eligible source time
- **THEN** inspection exposes its recorded values and `unknown` state without selecting it as current

#### Scenario: Fact-free quota outcomes remain distinguishable
- **WHEN** fixed-clock inspection covers Claude unavailable and Codex absent, null, and state-only component fixtures
- **THEN** each emits a separate component-state row with null fact, subject, utilization, and freshness fields and its exact availability enum

### Requirement: [TARGET-STATE] Quota Failure Isolation
MUST keep a previously committed independent usage event, another source stream, and either optional sink unaffected by later quota failure, stale evidence, or capability unavailability; a malformed quota candidate in the same complete record-set transaction MUST still roll back that record's otherwise-new usage candidate and hold before the record; and every quota component and health summary MUST expose the exact availability/freshness state without masking it. Quota semantics own only quota component transitions and snapshot selection; source quarantine and cursor recovery remain owned by the stream contract.

ID: REQ-quota-snapshot-semantics-007
Source: RFC 0001 § QuotaSnapshot; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: Usage and quota facts coexist independently
- **WHEN** one Codex record contains a valid new usage contribution and valid registered quota windows
- **THEN** all facts commit atomically while later quota staleness does not alter the usage contribution

#### Scenario: Malformed quota does not affect an independent usage record
- **WHEN** one Codex rate-limit record is malformed after an independent supported usage record has committed
- **THEN** the affected stream holds before the malformed record without fabricating quota or retracting the committed usage contribution

#### Scenario: Same-record malformed quota rolls back the record set
- **WHEN** one complete Codex record contains a new usage candidate and a malformed quota candidate
- **THEN** neither candidate nor the component-state change or cursor commits, and stream reconciliation owns the exact held state and recovery
