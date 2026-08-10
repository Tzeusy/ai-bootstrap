## ADDED Requirements

### Requirement: [TARGET-STATE] Exact Stable V1 View Manifests
MUST expose exactly six read-only SQLite views with these ordered column manifests and nullability: `usage_events(ledger_seq INTEGER NOT NULL,fact_identity BLOB NOT NULL,collector_namespace TEXT NOT NULL,ledger_namespace TEXT NOT NULL,ledger_epoch TEXT NOT NULL,adapter_schema_id TEXT NOT NULL,source_namespace TEXT NOT NULL,native_identity_json TEXT NOT NULL,accounting_fingerprint BLOB NOT NULL,source_observed_at TEXT NOT NULL,collected_at TEXT NOT NULL,tool TEXT NOT NULL,vendor TEXT NOT NULL,model TEXT NULL,project TEXT NULL,request_identity BLOB NOT NULL)`; `usage_event_amounts(ledger_seq INTEGER NOT NULL,fact_identity BLOB NOT NULL,category TEXT NOT NULL,amount INTEGER NOT NULL)`; `quota_snapshots(row_kind TEXT NOT NULL,component_key BLOB NOT NULL,ledger_seq INTEGER NULL,fact_identity BLOB NULL,subject_identity BLOB NULL,is_current INTEGER NOT NULL,current_freshness_state TEXT NULL,age_seconds INTEGER NULL,availability TEXT NOT NULL,collector_namespace TEXT NULL,ledger_namespace TEXT NULL,ledger_epoch TEXT NULL,adapter_schema_id TEXT NOT NULL,source_namespace TEXT NOT NULL,native_identity_json TEXT NULL,accounting_fingerprint BLOB NULL,source_observed_at TEXT NULL,state_observed_at TEXT NOT NULL,collected_at TEXT NULL,account_alias TEXT NULL,vendor TEXT NOT NULL,limit_name TEXT NULL,native_limit_identity TEXT NULL,native_window_identity TEXT NULL,native_scope_identity TEXT NULL,utilization_decimal TEXT NULL,window_minutes INTEGER NULL,reset_at TEXT NULL,scope TEXT NULL,recorded_freshness_state TEXT NULL,freshness_evidence TEXT NULL,state_code TEXT NULL)`; `source_health(row_kind TEXT NOT NULL,component_key BLOB NOT NULL,source_namespace TEXT NOT NULL,native_stream_identity TEXT NULL,adapter_schema_id TEXT NOT NULL,stream_generation TEXT NULL,state TEXT NOT NULL,last_scan_at TEXT NULL,last_accepted_source_at TEXT NULL,next_byte_offset INTEGER NULL,prefix_anchor_json TEXT NULL,parser_context_json TEXT NULL,failure_code TEXT NULL,failure_offset INTEGER NULL,reconciliation_completed_at TEXT NULL,reconciliation_due_evidence_json TEXT NULL,coverage_state TEXT NOT NULL,family_state TEXT NOT NULL,global_state TEXT NOT NULL)`; `sink_health(sink_kind TEXT NOT NULL,component_key BLOB NOT NULL,registration_identity BLOB NULL,sink_id TEXT NULL,destination_id TEXT NULL,projection_schema_id TEXT NULL,ledger_epoch TEXT NULL,canonical_target_digest BLOB NULL,projection_policy_digest BLOB NULL,state TEXT NOT NULL,acknowledged_ledger_seq INTEGER NULL,backlog_facts INTEGER NULL,target_ledger_seq INTEGER NULL,target_export_time_unix_nano INTEGER NULL,target_batch_count INTEGER NULL,target_projection_digest BLOB NULL,lease_holder TEXT NULL,lease_expires_at TEXT NULL,last_attempt_at TEXT NULL,last_success_at TEXT NULL,failure_code TEXT NULL)`; and `ledger_health(ledger_namespace TEXT NOT NULL,ledger_epoch TEXT NOT NULL,schema_version INTEGER NOT NULL,profile_id TEXT NOT NULL,profile_digest BLOB NOT NULL,migration_state TEXT NOT NULL,integrity_state TEXT NOT NULL,availability_state TEXT NOT NULL,available_bytes INTEGER NULL,admission_charge_bytes INTEGER NULL,reserve_bytes INTEGER NULL,admission_state TEXT NOT NULL,persisted_health_stale INTEGER NOT NULL,last_ledger_seq INTEGER NOT NULL,last_transaction_at TEXT NULL,accepted_count INTEGER NOT NULL,duplicate_count INTEGER NOT NULL,held_count INTEGER NOT NULL)`; consumers MUST NOT require private tables. `quota_snapshots.row_kind='component_state'` MUST have null fact/subject/accounting fields and one of `disabled|coverage_unknown|unavailable|absent|null|state_only`, while `row_kind='snapshot'` MUST have those fact fields present, `availability='observed'`, and the exact quota-snapshot nullability; `source_health.row_kind='component'` MUST represent disabled, unsupported, or pre-discovery state without inventing a stream/cursor, while `row_kind='stream'` MUST carry the complete stream fields; `sink_health` MUST synthesize a never-bound disabled component row with all registration/checkpoint/lease fields null and MUST expose registration digests for every bound row. The quota component `vendor` MUST be derived solely by the closed v1 registration mapping `claude_quota -> anthropic` and `codex_quota -> openai`; no other mapping is valid.

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

#### Scenario: Every view column has one exact source
- **WHEN** the six views are materialized
- **THEN** usage columns MUST come from the same-sequence `facts`, `usage_events`, and `usage_event_amounts` rows; quota snapshot columns MUST come from `facts` plus `quota_snapshots`, with `recorded_freshness_state` sourced from stored `freshness_state`, `state_observed_at=collected_at`, `availability='observed'`, and current-only fields derived by REQ-quota-snapshot-semantics-005 and REQ-quota-snapshot-semantics-006; quota component rows MUST come from `component_registrations`, use `is_current=0`, and keep current/fact-only fields null
- **AND** source component columns MUST come from `component_registrations`; each stream's `state`, `failure_code`, and `failure_offset` MUST be the checked derived cache of `stream_health_latches` under the fixed precedence and all other stream columns come from `source_streams`; sink registration/checkpoint columns come from `component_registrations`, `sink_registrations`, and `sink_checkpoints`, and ledger identity/counter columns from `ledger_state` plus active `release_profile_state`; each synthetic `row_kind`, summary, capacity, backlog, or renamed lease field MUST use only the derivations closed below

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
MUST restrict stream rows' `source_health.state` to `healthy`, `trailing_deferred`, `quarantined`, `storage_hold`, `reconciliation_overdue`, `source_envelope_exceeded`, `retention_gap`, or `coverage_unknown`; restrict source-component rows to `disabled`, `unsupported_profile`, `unsupported_accounting_profile`, `coverage_unknown`, `healthy`, or `degraded`; derive each stream state and winning failure solely from the seven persistent latch rows in exact `storage|quarantine|retention|envelope|reconciliation|tail|coverage` precedence, reveal the next active lower latch when the winner clears, expose the declared component or per-stream fields under their exact null rules, derive `family_state` and `global_state` as `healthy`, `degraded`, or `disabled`, and prohibit either summary from masking any enabled unsupported, held, overdue, envelope-exceeded, or coverage-degraded component.

ID: REQ-local-query-contract-003
Source: RFC 0001 § Health and Freshness State
Scope: v1-mandatory

#### Scenario: Healthy source is fully inspectable
- **WHEN** a stream is within bounds, current, unheld, scanned successfully, and has no coverage gap
- **THEN** its row reports `healthy` with the complete durable cursor and reconciliation evidence

#### Scenario: Degraded stream propagates upward
- **WHEN** all arrival/clear permutations of two or more stream latches are inspected before and after restart
- **THEN** the same highest active state and winning failure are visible, clearing it reveals the next active lower state, and no family or global row reports `healthy` until all owning recoveries clear

#### Scenario: Unsupported and disabled sources need no invented stream
- **WHEN** one enabled source is `unsupported_profile` or `unsupported_accounting_profile` and another source is disabled before discovery
- **THEN** component rows expose the exact enabled failure and disabled state with null stream/cursor fields
- **AND** enabled unsupported state degrades upward while disabled state is excluded

#### Scenario: Coverage vocabulary has exact component and stream sources
- **WHEN** a source-health row is rendered
- **THEN** `coverage_state` MUST be `not_applicable` for a disabled component; `coverage_unknown` for an enabled component with no admitted coverage evidence or an unsupported profile/accounting failure; and `current`, `coverage_unknown`, or `retention_gap` for a stream exactly as persisted by reconciliation
- **AND** component freshness MUST be derived from its streams without erasing any stream-level gap

### Requirement: [TARGET-STATE] Ledger Health View Semantics
MUST restrict ledger migration state to `current`, `pending`, or `failed`; integrity state to `verified`, `unverified`, or `failed`; availability state to `available`, `storage_hold`, or `ledger_unavailable`; and admission state to `admissible`, `insufficient_capacity`, or `unknown`; expose namespace, epoch, schema, profile ID and digest, recomputed capacity and reserve evidence, last sequence and transaction, and the durable accepted-fact, duplicate-candidate, and distinct-hold-episode counts owned by the ledger transaction contract; and compute a current read-only hold or unavailable result even when persisted health is stale.

ID: REQ-local-query-contract-004
Source: RFC 0001 § Health and Freshness State; § Configuration Contract
Scope: v1-mandatory

#### Scenario: Current ledger health includes admission evidence
- **WHEN** the ledger is readable and capacity inspection succeeds
- **THEN** `ledger_health` exposes the exact active profile, schema, counts, capacity, charge, reserve, and derived admission state

#### Scenario: Failed health write cannot mask outage
- **WHEN** SQLite cannot persist a health transition or cannot be opened for writes
- **THEN** read-only inspection computes `storage_hold` or `ledger_unavailable` directly and sets `persisted_health_stale=1`

#### Scenario: Derived ledger-health evidence is closed
- **WHEN** ledger health is inspected
- **THEN** `migration_state` MUST be `current` only when `ledger_state.schema_version` and every required `schema_migrations.artifact_digest` match the active profile, `pending` only while an approved migration has not started, and `failed` after a failed migration or digest mismatch; `integrity_state` MUST come only from the declared read-only SQLite integrity procedure; and `availability_state` MUST come only from the current open/read result plus the durable storage-hold transition
- **AND** `available_bytes` MUST be the checked product of filesystem available blocks and fragment size for the ledger volume; `admission_charge_bytes` MUST be the active storage profile's computed worst-case charge for one maximum admitted record transaction; `reserve_bytes` MUST equal its `post_commit_reserve_bytes`; `admission_state` MUST apply the exact capacity inequality from REQ-durable-local-ledger-008; and `persisted_health_stale` MUST be `1` only when direct inspection evidence is newer than or cannot be written to persisted state, otherwise `0`

### Requirement: [TARGET-STATE] Independent Sink Health View
MUST restrict each `sink_health.state` to `disabled`, `idle`, `delivering`, `retrying`, or `blocked`, expose component and registration identities, both immutable registration digests, the complete technical checkpoint tuple, monotonically acknowledged sequence, non-negative backlog, pending target metadata, nullable OTLP lease holder and expiry, attempt and durable-success times, and code-owned sanitized failure code, and derive every row independently. The view MUST render exactly one row per configured sink component, binding it only through `component_registrations.selected_sink_registration`; historical unselected registrations and checkpoints remain private and render no additional row. A never-bound disabled sink row MUST have only `sink_kind`, `component_key`, and `state=disabled` non-null. A previously bound disabled sink row MUST have `sink_kind`, `component_key`, selected `registration_identity`, the complete tuple, both registration digests, `state=disabled`, retained `acknowledged_ledger_seq`, computed `backlog_facts`, and any historically present `last_attempt_at`/`last_success_at` non-null, while every pending-target field, lease field, and `failure_code` is null; it MUST have no client, worker, task, credential reader, authentication, DNS, pool, or connection. Health JSON MUST order these rows by `sink_kind` and then null-first registration-identity bytes.

ID: REQ-local-query-contract-005
Source: RFC 0001 § Health and Freshness State
Scope: v1-mandatory

#### Scenario: Independent healthy sinks are visible
- **WHEN** both sinks are enabled and current at their own checkpoints
- **THEN** each row independently reports `idle`, its acknowledged sequence, zero backlog, and its own last success

#### Scenario: One retry does not mask or infect another
- **WHEN** OTLP retries while PostgreSQL is current
- **THEN** `sink_health` reports OTLP `retrying` and PostgreSQL independently `idle` without sharing checkpoints or failure codes

#### Scenario: Disabled sink health creates no delivery state
- **WHEN** OTLP is configured disabled and has never been enabled
- **THEN** `sink_health` reports one OTLP component row as `disabled` with null registration, tuple, checkpoint, target, attempt, and lease fields

#### Scenario: Previously bound disabled sink renders one inert bound row
- **WHEN** a sink with a selected retained registration and checkpoint is disabled
- **THEN** `sink_health` renders exactly one component-bound row, sources its registration solely from `selected_sink_registration`, reports `state=disabled`, retains the tuple, digests, acknowledged sequence, computed backlog, and nullable historical attempt/success times, and renders pending-target, lease, and failure fields null
- **AND** no historical unselected registration renders another row and JSON ordering remains sink kind then null-first registration identity

#### Scenario: Blocked binding exposes its safe cause
- **WHEN** a bound sink detects registration mismatch, schema mismatch, tuple collision, conservation mismatch, idempotency conflict, or failed migration
- **THEN** its row remains `blocked` at the prior acknowledged sequence with the exact code-owned failure code and both registration digests

#### Scenario: Derived sink-health fields are closed
- **WHEN** an enabled bound sink-health row is rendered
- **THEN** `backlog_facts` MUST equal the count of retained `facts` in the registered ledger epoch whose sequence is greater than `acknowledged_ledger_seq`; `lease_holder` and `lease_expires_at` MUST map only from the matching OTLP `sink_leases.holder_id` and `expires_at`; pending target fields MUST map only from `sink_checkpoints`; and PostgreSQL lease fields MUST always be null
- **AND** a component-only never-bound disabled row MUST source `sink_kind` and `component_key` from `component_registrations` and leave every field owned by registration, checkpoint, lease, or attempt state null

### Requirement: [TARGET-STATE] Exact Versioned Health JSON
MUST provide a non-networked read-only inspection command that writes RFC 8785 canonical UTF-8 JSON followed by one LF with exactly top-level keys `schema`, `generated_at`, `overall_state`, `profile`, `sources`, `ledger`, `sinks`, and `quota`; `schema` is `aiut.health/v1`; `generated_at` is RFC 3339 UTC; `overall_state` is `healthy`, `degraded`, or `unavailable`; `profile` is `{id,digest_sha256}`; for a readable compatible ledger, `sources[]` contains exactly the `source_health` columns with BLOBs lowercase-hex encoded and rows ordered by source namespace, component before stream, then native stream identity, `ledger` contains exactly the `ledger_health` columns with BLOBs lowercase-hex encoded, `sinks[]` contains exactly the `sink_health` columns ordered by sink kind then null-first registration identity, and `quota[]` contains exactly the `quota_snapshots` columns for every component-state row plus only snapshot rows with `is_current=1`, ordered by source namespace, component before snapshot, then null-first subject and fact identity, with null only where the owning view declares it. If the ledger cannot be opened or read, the command MUST instead emit one out-of-band unavailable-ledger variant with the same exact top-level keys, `overall_state="unavailable"`, empty `sources`, `sinks`, and `quota` arrays, `profile` containing exactly `id` and `digest_sha256` from the independently validated embedded profile or null when that value cannot be independently validated, and `ledger` containing exactly `availability_state="ledger_unavailable"`, `configured_ledger_namespace` from independently validated configuration or null, `failure_code="ledger_unavailable"`, `ledger_epoch=null`, `persisted_health_stale=1`, and `schema_version=null`; this variant MUST NOT claim any member came from a SQLite view and MUST perform no write, migration, retry, repair, DNS lookup, listener creation, or network activity. For identical ledger or unavailable-ledger evidence, configuration, profile, clock, and direct read-only filesystem evidence, bytes MUST be identical; between otherwise identical inspections only `generated_at`, each readable-ledger `age_seconds`, and readable-ledger freshness values derived solely from that age MAY change with inspection time.
Normative continuation: for this exact contract, every RFC 3339 timestamp is
the fixed-nine-digit UTC `Z` rendering of a checked non-negative signed-64-bit
Unix-nanosecond instant, and every `age_seconds` value is
`floor(max(0,inspection_unix_nano-source_unix_nano)/1_000_000_000)` after
checked subtraction. Tolerated future timestamps therefore have age zero; an
out-of-range instant, leap second, or arithmetic overflow fails closed rather
than using host datetime or floating-point rounding.

ID: REQ-local-query-contract-006
Source: RFC 0001 § Health and Freshness State
Scope: v1-mandatory

#### Scenario: Inspection output matches the exact schema
- **WHEN** the command inspects a readable compatible ledger
- **THEN** it emits one deterministic `aiut.health/v1` document with the exact keys, enum values, null rules, hex encoding, and array ordering
- **AND** repeated inspection with advancing time differs only in `generated_at`, `age_seconds`, and age-derived freshness

#### Scenario: Fixed-clock vectors are byte deterministic
- **WHEN** repeated inspections and restarts use the same fixed nanosecond clock, distinct valid source namespaces, all stream-latch overlap/clear permutations, and identical ledger, configuration, and direct evidence
- **THEN** their complete UTF-8 output including the terminal LF is byte-for-byte identical, with lower-latch reveal independent of arrival order
- **AND** an equal Claude/Codex namespace plus same-native-stream fixture is rejected before serialization, while each JSON/database/log capture must observe its harmless positive-control canary and a deliberate test-only leak makes the harness fail

#### Scenario: Unreadable ledger has one exact out-of-band variant
- **WHEN** SQLite cannot be opened or read under otherwise identical validated configuration, embedded profile, direct filesystem evidence, and fixed clock
- **THEN** the command emits byte-identical canonical `aiut.health/v1` output with empty source, sink, and quota arrays and exactly the unavailable-ledger `profile` and `ledger` keys and values declared above
- **AND** no field is represented as a result from `source_health`, `ledger_health`, `sink_health`, `quota_snapshots`, or any private SQLite table

#### Scenario: Inspection is side-effect free
- **WHEN** the ledger is degraded, unreadable, or a migration or sink retry is pending
- **THEN** inspection reports it without migration, retry, cursor advance, repair, DNS lookup, listener creation, or any state mutation

### Requirement: [TARGET-STATE] Non-Masking Overall Health
SHALL report `overall_state="healthy"` only when every enabled source is healthy and reconciliation-current, the ledger is available, verified, current, and admissible, every applicable quota subject satisfies its currency rule or is explicitly capability-unavailable by contract, and every enabled sink is registered with matching digests, idle, and current; `unsupported_profile`, `unsupported_accounting_profile`, every held/coverage state, stale or unknown quota where currency is required, and sink `retrying|blocked` yield `degraded`; disabled components are excluded, while an unreadable ledger yields `unavailable`.

ID: REQ-local-query-contract-007
Source: RFC 0001 § Health and Freshness State; about/heart-and-soul/vision.md § Non-Negotiable Principles → 4. Partial Failure Is Explicit
Scope: v1-mandatory

#### Scenario: All enabled components are healthy
- **WHEN** every enabled member satisfies its own healthy or current contract and the ledger is available
- **THEN** `overall_state` is `healthy`

#### Scenario: Majority success cannot hide degradation
- **WHEN** any enabled component is quarantined, stale, overdue, held, blocked, or retrying
- **THEN** `overall_state` is `degraded` and the affected source, ledger, quota, or sink boundary is identifiable
