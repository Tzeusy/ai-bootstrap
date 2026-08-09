## ADDED Requirements

### Requirement: [TARGET-STATE] Exact Stable V1 View Manifests
MUST expose exactly six read-only SQLite views with these ordered column manifests and nullability: `usage_events(ledger_seq INTEGER NOT NULL,fact_identity BLOB NOT NULL,collector_namespace TEXT NOT NULL,ledger_namespace TEXT NOT NULL,ledger_epoch TEXT NOT NULL,adapter_schema_id TEXT NOT NULL,source_namespace TEXT NOT NULL,native_identity_json TEXT NOT NULL,accounting_fingerprint BLOB NOT NULL,source_observed_at TEXT NOT NULL,collected_at TEXT NOT NULL,tool TEXT NOT NULL,vendor TEXT NOT NULL,model TEXT NULL,project TEXT NULL,request_identity BLOB NOT NULL)`; `usage_event_amounts(ledger_seq INTEGER NOT NULL,fact_identity BLOB NOT NULL,category TEXT NOT NULL,amount INTEGER NOT NULL)`; `quota_snapshots(ledger_seq INTEGER NOT NULL,fact_identity BLOB NOT NULL,subject_identity BLOB NOT NULL,is_current INTEGER NOT NULL,current_freshness_state TEXT NOT NULL,age_seconds INTEGER NULL,availability TEXT NOT NULL,collector_namespace TEXT NOT NULL,ledger_namespace TEXT NOT NULL,ledger_epoch TEXT NOT NULL,adapter_schema_id TEXT NOT NULL,source_namespace TEXT NOT NULL,native_identity_json TEXT NOT NULL,accounting_fingerprint BLOB NOT NULL,source_observed_at TEXT NULL,collected_at TEXT NOT NULL,account_alias TEXT NOT NULL,vendor TEXT NOT NULL,limit_name TEXT NOT NULL,native_limit_identity TEXT NOT NULL,native_window_identity TEXT NOT NULL,native_scope_identity TEXT NOT NULL,utilization_decimal TEXT NOT NULL,window_minutes INTEGER NULL,reset_at TEXT NULL,scope TEXT NULL,recorded_freshness_state TEXT NOT NULL,freshness_evidence TEXT NOT NULL)`; `source_health(source_namespace TEXT NOT NULL,native_stream_identity TEXT NOT NULL,adapter_schema_id TEXT NOT NULL,stream_generation TEXT NOT NULL,state TEXT NOT NULL,last_scan_at TEXT NULL,last_accepted_source_at TEXT NULL,next_byte_offset INTEGER NOT NULL,prefix_anchor_json TEXT NOT NULL,parser_context_json TEXT NOT NULL,failure_code TEXT NULL,failure_offset INTEGER NULL,reconciliation_completed_at TEXT NULL,reconciliation_due_evidence_json TEXT NULL,coverage_state TEXT NOT NULL,family_state TEXT NOT NULL,global_state TEXT NOT NULL)`; `sink_health(sink_id TEXT NOT NULL,destination_id TEXT NOT NULL,projection_schema_id TEXT NOT NULL,ledger_epoch TEXT NOT NULL,state TEXT NOT NULL,acknowledged_ledger_seq INTEGER NOT NULL,backlog_facts INTEGER NOT NULL,lease_holder TEXT NULL,lease_expires_at TEXT NULL,last_attempt_at TEXT NULL,last_success_at TEXT NULL,failure_code TEXT NULL)`; and `ledger_health(ledger_namespace TEXT NOT NULL,ledger_epoch TEXT NOT NULL,schema_version INTEGER NOT NULL,profile_id TEXT NOT NULL,profile_digest BLOB NOT NULL,migration_state TEXT NOT NULL,integrity_state TEXT NOT NULL,availability_state TEXT NOT NULL,available_bytes INTEGER NULL,admission_charge_bytes INTEGER NULL,reserve_bytes INTEGER NULL,admission_state TEXT NOT NULL,persisted_health_stale INTEGER NOT NULL,last_ledger_seq INTEGER NOT NULL,last_transaction_at TEXT NULL,accepted_count INTEGER NOT NULL,duplicate_count INTEGER NOT NULL,held_count INTEGER NOT NULL)`; consumers MUST NOT require private tables.

ID: REQ-local-query-contract-001
Source: RFC 0001 § Health and Freshness State; about/heart-and-soul/v1.md § V1 Ships
Scope: v1-mandatory

#### Scenario: All stable views expose the declared shape
- **WHEN** a compatible v1 ledger is opened read-only
- **THEN** schema inspection returns all six exact view names, ordered columns, declared SQLite types, and nullability semantics
- **AND** every promised normalized and health value is obtainable without a private-table join

#### Scenario: Missing or writable view blocks release
- **WHEN** any required view or declared column is missing, reordered, writable, differently typed, more nullable, or requires private-table access
- **THEN** the local query contract fails release validation

### Requirement: [TARGET-STATE] Stable V1 View Compatibility
MUST preserve the six v1 view names, column order, declared types, nullability, enum meanings, and value semantics for the life of v1, and MUST introduce a separately named versioned view rather than remove, rename, reorder, weaken, or silently reinterpret a v1 field.

ID: REQ-local-query-contract-002
Source: RFC 0001 § Health and Freshness State; § Compatibility and Evolution
Scope: v1-mandatory

#### Scenario: Additive private migration preserves v1
- **WHEN** a migration adds private implementation state without changing the stable contract
- **THEN** queries against all six v1 views return the same columns and meanings

#### Scenario: Incompatible view change requires a new name
- **WHEN** a migration would remove, rename, reorder, reinterpret, or change nullability of a v1 column
- **THEN** migration fails unless the old view remains intact and the incompatible contract uses a separately named versioned view

### Requirement: [TARGET-STATE] Source Health View Semantics
MUST restrict `source_health.state` to `healthy`, `trailing_deferred`, `quarantined`, `storage_hold`, `reconciliation_overdue`, `source_envelope_exceeded`, `retention_gap`, `coverage_unknown`, or `disabled`, expose the declared per-stream technical, cursor, failure, reconciliation, and coverage fields, derive `family_state` and `global_state` as `healthy`, `degraded`, or `disabled`, and prohibit either summary from masking a non-healthy enabled stream.

ID: REQ-local-query-contract-003
Source: RFC 0001 § Health and Freshness State
Scope: v1-mandatory

#### Scenario: Healthy source is fully inspectable
- **WHEN** a stream is within bounds, current, unheld, scanned successfully, and has no coverage gap
- **THEN** its row reports `healthy` with the complete durable cursor and reconciliation evidence

#### Scenario: Degraded stream propagates upward
- **WHEN** one stream is stale, overdue, held, envelope-exceeded, or lost
- **THEN** its exact state and failure boundary are visible and no family or global row reports `healthy`

### Requirement: [TARGET-STATE] Ledger Health View Semantics
MUST restrict ledger migration state to `current`, `pending`, or `failed`; integrity state to `verified`, `unverified`, or `failed`; availability state to `available`, `storage_hold`, or `ledger_unavailable`; and admission state to `admissible`, `insufficient_capacity`, or `unknown`; expose namespace, epoch, schema, profile ID and digest, recomputed capacity and reserve evidence, last sequence and transaction, and accepted, duplicate, and held counts; and compute a current read-only hold or unavailable result even when persisted health is stale.

ID: REQ-local-query-contract-004
Source: RFC 0001 § Health and Freshness State; § Configuration Contract
Scope: v1-mandatory

#### Scenario: Current ledger health includes admission evidence
- **WHEN** the ledger is readable and capacity inspection succeeds
- **THEN** `ledger_health` exposes the exact active profile, schema, counts, capacity, charge, reserve, and derived admission state

#### Scenario: Failed health write cannot mask outage
- **WHEN** SQLite cannot persist a health transition or cannot be opened for writes
- **THEN** read-only inspection computes `storage_hold` or `ledger_unavailable` directly and sets `persisted_health_stale=1`

### Requirement: [TARGET-STATE] Independent Sink Health View
MUST restrict each `sink_health.state` to `disabled`, `idle`, `delivering`, `retrying`, or `blocked`, expose the complete technical checkpoint tuple, monotonically acknowledged sequence, non-negative backlog, nullable OTLP lease holder and expiry, attempt and durable-success times, and code-owned sanitized failure code, and derive every row independently.

ID: REQ-local-query-contract-005
Source: RFC 0001 § Health and Freshness State
Scope: v1-mandatory

#### Scenario: Independent healthy sinks are visible
- **WHEN** both sinks are enabled and current at their own checkpoints
- **THEN** each row independently reports `idle`, its acknowledged sequence, zero backlog, and its own last success

#### Scenario: One retry does not mask or infect another
- **WHEN** OTLP retries while PostgreSQL is current
- **THEN** `sink_health` reports OTLP `retrying` and PostgreSQL independently `idle` without sharing checkpoints or failure codes

### Requirement: [TARGET-STATE] Exact Versioned Health JSON
MUST provide a non-networked read-only inspection command whose deterministic UTF-8 JSON document has exactly top-level keys `schema`, `generated_at`, `overall_state`, `profile`, `sources`, `ledger`, `sinks`, and `quota`; `schema` is `aiut.health/v1`; `generated_at` is RFC 3339 UTC; `overall_state` is `healthy`, `degraded`, or `unavailable`; `profile` is `{id,digest_sha256}`; `sources[]` contains exactly the `source_health` columns with BLOBs hex-encoded and rows ordered by source namespace then native stream identity; `ledger` contains exactly the `ledger_health` columns with BLOBs hex-encoded; `sinks[]` contains exactly the `sink_health` columns ordered by the four checkpoint-key fields; and `quota[]` contains `{source_namespace,subject_identity,current_fact_identity,availability,freshness_state,source_observed_at,age_seconds,freshness_evidence}` ordered by source namespace then subject identity, with null only where the owning view declares it.

ID: REQ-local-query-contract-006
Source: RFC 0001 § Health and Freshness State
Scope: v1-mandatory

#### Scenario: Inspection output matches the exact schema
- **WHEN** the command inspects a readable compatible ledger
- **THEN** it emits one deterministic `aiut.health/v1` document with the exact keys, enum values, null rules, hex encoding, and array ordering
- **AND** repeated inspection without state changes differs only in `generated_at`

#### Scenario: Inspection is side-effect free
- **WHEN** the ledger is degraded or a migration or sink retry is pending
- **THEN** inspection reports it without migration, retry, cursor advance, repair, DNS lookup, listener creation, or any state mutation

### Requirement: [TARGET-STATE] Non-Masking Overall Health
SHALL report `overall_state="healthy"` only when every enabled source is healthy and reconciliation-current, the ledger is available, verified, current, and admissible, every applicable quota subject satisfies its currency rule or is explicitly capability-unavailable by contract, and every enabled sink is idle and current; any other enabled-member degradation yields `degraded`, while an unreadable ledger yields `unavailable`.

ID: REQ-local-query-contract-007
Source: RFC 0001 § Health and Freshness State; about/heart-and-soul/vision.md § Non-Negotiable Principles → 4. Partial Failure Is Explicit
Scope: v1-mandatory

#### Scenario: All enabled components are healthy
- **WHEN** every enabled member satisfies its own healthy or current contract and the ledger is available
- **THEN** `overall_state` is `healthy`

#### Scenario: Majority success cannot hide degradation
- **WHEN** any enabled component is quarantined, stale, overdue, held, blocked, or retrying
- **THEN** `overall_state` is `degraded` and the affected source, ledger, quota, or sink boundary is identifiable
