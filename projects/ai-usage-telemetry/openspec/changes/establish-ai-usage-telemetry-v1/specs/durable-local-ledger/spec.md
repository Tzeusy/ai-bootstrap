## ADDED Requirements

### Requirement: [TARGET-STATE] Exact Closed SQLite V1 Schema
SHALL make SQLite under `/data` the durable accounting authority and define exactly these private v1 tables and columns: `ledger_state(singleton INTEGER PRIMARY KEY CHECK(singleton=1),ledger_namespace TEXT NOT NULL,ledger_epoch TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL,schema_version INTEGER NOT NULL,last_ledger_seq INTEGER NOT NULL CHECK(last_ledger_seq>=0),last_transaction_at TEXT NULL,accepted_count INTEGER NOT NULL DEFAULT 0 CHECK(accepted_count>=0),duplicate_count INTEGER NOT NULL DEFAULT 0 CHECK(duplicate_count>=0),held_count INTEGER NOT NULL DEFAULT 0 CHECK(held_count>=0))`; `release_profile_state(singleton INTEGER PRIMARY KEY CHECK(singleton=1),profile_id TEXT NOT NULL,profile_digest BLOB NOT NULL CHECK(length(profile_digest)=32),accepted_at TEXT NOT NULL)`; `schema_migrations(version INTEGER PRIMARY KEY,artifact_digest BLOB NOT NULL CHECK(length(artifact_digest)=32),applied_at TEXT NOT NULL)`; `component_registrations(component_key BLOB PRIMARY KEY,component_kind TEXT NOT NULL CHECK(component_kind IN ('source','quota','sink')),component_name TEXT NOT NULL CHECK(component_name IN ('claude','codex','otlp','postgresql')),source_namespace TEXT NULL,adapter_schema_id TEXT NULL,configured_state TEXT NOT NULL CHECK(configured_state IN ('enabled','disabled')),runtime_state TEXT NOT NULL CHECK(runtime_state IN ('disabled','enabled','unsupported_profile','unsupported_accounting_profile','coverage_unknown','healthy','degraded','unavailable','absent','null','state_only','observed')),state_code TEXT NULL,state_observed_at TEXT NOT NULL,last_source_observed_at TEXT NULL,account_alias TEXT NULL,selected_sink_registration BLOB NULL,registered_at TEXT NOT NULL)`; `facts(fact_identity BLOB PRIMARY KEY,collector_namespace TEXT NOT NULL,ledger_namespace TEXT NOT NULL,adapter_schema_id TEXT NOT NULL,source_namespace TEXT NOT NULL,fact_kind TEXT NOT NULL CHECK(fact_kind IN ('usage_event','quota_snapshot')),native_identity_json TEXT NOT NULL,accounting_fingerprint BLOB NOT NULL CHECK(length(accounting_fingerprint)=32),ledger_epoch TEXT NOT NULL,ledger_seq INTEGER NOT NULL UNIQUE CHECK(ledger_seq>0),source_observed_at TEXT NULL,collected_at TEXT NOT NULL,UNIQUE(collector_namespace,ledger_namespace,adapter_schema_id,source_namespace,fact_kind,native_identity_json))`; `usage_events(fact_identity BLOB PRIMARY KEY REFERENCES facts(fact_identity),tool TEXT NOT NULL,vendor TEXT NOT NULL,model TEXT NULL,project TEXT NULL,request_identity BLOB NOT NULL,metadata_json TEXT NOT NULL CHECK(metadata_json='{}'))`; `usage_event_amounts(fact_identity BLOB NOT NULL REFERENCES usage_events(fact_identity),category TEXT NOT NULL,amount INTEGER NOT NULL CHECK(amount>=0),PRIMARY KEY(fact_identity,category))`; `quota_snapshots(fact_identity BLOB PRIMARY KEY REFERENCES facts(fact_identity),subject_identity BLOB NOT NULL,account_alias TEXT NULL,vendor TEXT NOT NULL,limit_name TEXT NOT NULL,native_limit_identity TEXT NOT NULL,native_window_identity TEXT NOT NULL,native_scope_identity TEXT NOT NULL,utilization_decimal TEXT NOT NULL,window_minutes INTEGER NULL CHECK(window_minutes>=0),reset_at TEXT NULL,scope TEXT NULL,freshness_state TEXT NOT NULL CHECK(freshness_state IN ('fresh','stale','unknown')),freshness_evidence TEXT NOT NULL CHECK(freshness_evidence IN ('record_timestamp','record_timestamp_and_window','record_timestamp_and_reset','record_timestamp_window_and_reset','missing_source_timestamp')),metadata_json TEXT NOT NULL CHECK(metadata_json='{}'))`; `logical_requests(request_identity BLOB PRIMARY KEY,collector_namespace TEXT NOT NULL,ledger_namespace TEXT NOT NULL,adapter_schema_id TEXT NOT NULL,source_namespace TEXT NOT NULL,native_request_identity_json TEXT NOT NULL,first_fact_identity BLOB NOT NULL REFERENCES usage_events(fact_identity),first_ledger_seq INTEGER NOT NULL UNIQUE,UNIQUE(collector_namespace,ledger_namespace,adapter_schema_id,source_namespace,native_request_identity_json))`; `usage_aggregates(ledger_epoch TEXT NOT NULL,tool TEXT NOT NULL,vendor TEXT NOT NULL,model_bucket_json TEXT NOT NULL,project_bucket_json TEXT NOT NULL,category TEXT NOT NULL,total_amount INTEGER NOT NULL CHECK(total_amount>=0),PRIMARY KEY(ledger_epoch,tool,vendor,model_bucket_json,project_bucket_json,category))`; `request_aggregates(ledger_epoch TEXT NOT NULL,tool TEXT NOT NULL,vendor TEXT NOT NULL,model_bucket_json TEXT NOT NULL,project_bucket_json TEXT NOT NULL,total_requests INTEGER NOT NULL CHECK(total_requests>=0),PRIMARY KEY(ledger_epoch,tool,vendor,model_bucket_json,project_bucket_json))`; `source_streams(source_namespace TEXT NOT NULL,native_stream_identity TEXT NOT NULL,adapter_schema_id TEXT NOT NULL,stream_generation TEXT NOT NULL,next_byte_offset INTEGER NOT NULL CHECK(next_byte_offset>=0),prefix_anchor_json TEXT NOT NULL,parser_context_json TEXT NOT NULL,state TEXT NOT NULL CHECK(state IN ('healthy','trailing_deferred','quarantined','storage_hold','reconciliation_overdue','source_envelope_exceeded','retention_gap','coverage_unknown')),last_scan_at TEXT NULL,last_accepted_source_at TEXT NULL,reconciliation_completed_at TEXT NULL,reconciliation_due_evidence_json TEXT NULL,coverage_state TEXT NOT NULL CHECK(coverage_state IN ('current','coverage_unknown','retention_gap')),failure_code TEXT NULL CHECK(failure_code IS NULL OR failure_code IN ('incomplete_tail','record_limit','unknown_kind','recognized_malformed','schema_inconsistent','unregistered_category','identity_collision','unsupported_accounting_profile','ledger_storage_hold','reconciliation_overdue','source_envelope_exceeded','coverage_unknown','retention_gap')),failure_offset INTEGER NULL,PRIMARY KEY(source_namespace,native_stream_identity))`; `source_diagnostics(source_namespace TEXT NOT NULL,native_stream_identity TEXT NOT NULL,failure_code TEXT NOT NULL,registry_path_id TEXT NULL,expected_type TEXT NULL,capped_measure INTEGER NULL,first_seen_at TEXT NOT NULL,last_seen_at TEXT NOT NULL,repeat_count INTEGER NOT NULL CHECK(repeat_count>0),PRIMARY KEY(source_namespace,native_stream_identity))`; `sink_registrations(registration_identity BLOB NOT NULL UNIQUE,sink_id TEXT NOT NULL,destination_id TEXT NOT NULL,projection_schema_id TEXT NOT NULL,ledger_epoch TEXT NOT NULL,sink_kind TEXT NOT NULL CHECK(sink_kind IN ('otlp','postgresql')),canonical_target_digest BLOB NOT NULL CHECK(length(canonical_target_digest)=32),projection_policy_digest BLOB NOT NULL CHECK(length(projection_policy_digest)=32),bound_at TEXT NOT NULL,PRIMARY KEY(sink_id,destination_id,projection_schema_id,ledger_epoch))`; `sink_checkpoints(sink_id TEXT NOT NULL,destination_id TEXT NOT NULL,projection_schema_id TEXT NOT NULL,ledger_epoch TEXT NOT NULL,acknowledged_ledger_seq INTEGER NOT NULL CHECK(acknowledged_ledger_seq>=0),target_ledger_seq INTEGER NULL CHECK(target_ledger_seq>0),target_export_time_unix_nano INTEGER NULL CHECK(target_export_time_unix_nano>=0),target_batch_count INTEGER NULL CHECK(target_batch_count>0),target_projection_digest BLOB NULL CHECK(target_projection_digest IS NULL OR length(target_projection_digest)=32),attempt_id TEXT NULL,state TEXT NOT NULL CHECK(state IN ('idle','delivering','retrying','blocked')),last_attempt_at TEXT NULL,last_success_at TEXT NULL,failure_code TEXT NULL,PRIMARY KEY(sink_id,destination_id,projection_schema_id,ledger_epoch),FOREIGN KEY(sink_id,destination_id,projection_schema_id,ledger_epoch) REFERENCES sink_registrations(sink_id,destination_id,projection_schema_id,ledger_epoch))`; `sink_leases(sink_id TEXT NOT NULL,destination_id TEXT NOT NULL,projection_schema_id TEXT NOT NULL,ledger_epoch TEXT NOT NULL,holder_id TEXT NOT NULL,fencing_token INTEGER NOT NULL CHECK(fencing_token>0),expires_at TEXT NOT NULL,PRIMARY KEY(sink_id,destination_id,projection_schema_id,ledger_epoch),FOREIGN KEY(sink_id,destination_id,projection_schema_id,ledger_epoch) REFERENCES sink_checkpoints(sink_id,destination_id,projection_schema_id,ledger_epoch))`; and `privacy_repair_audit(repair_id TEXT PRIMARY KEY,approved_plan_digest BLOB NOT NULL CHECK(length(approved_plan_digest)=32),completed_at TEXT NOT NULL,removed_invalid_fact_count INTEGER NOT NULL CHECK(removed_invalid_fact_count>=0),absence_evidence_digest BLOB NOT NULL CHECK(length(absence_evidence_digest)=32))`. `component_key` MUST be the RFC 8785 canonical UTF-8 bytes of `["source",component_name,source_namespace]`, `["quota",component_name,source_namespace]`, or `["sink",component_name]`; `registration_identity` MUST be the canonical full checkpoint-tuple bytes. Source and quota rows MUST use `component_name=claude|codex`, require source namespace/schema, and keep sink selection null; source rows permit only `disabled|unsupported_profile|unsupported_accounting_profile|coverage_unknown|healthy|degraded`, while quota rows permit only `disabled|coverage_unknown|unavailable|absent|null|state_only|observed` and keep `account_alias` nullable. Sink rows MUST use `component_name=otlp|postgresql`, permit only `disabled|enabled`, require source/schema/alias fields null, and may select a registration only after it exists. `state_code` MUST be null for healthy/enabled/disabled states and otherwise equal the closed runtime-state/failure enum being reported. Extraction and projection registries MUST NOT add any column or table.
Normative continuation: the exact closed table set above additionally includes
`stream_health_latches(source_namespace TEXT NOT NULL,native_stream_identity
TEXT NOT NULL,dimension TEXT NOT NULL CHECK(dimension IN
('storage','quarantine','retention','envelope','reconciliation','tail','coverage')),
latch_state TEXT NOT NULL CHECK(latch_state IN ('clear','latched')),failure_code
TEXT NULL,failure_offset INTEGER NULL CHECK(failure_offset IS NULL OR
failure_offset>=0),failure_evidence_json TEXT NULL,recovery_evidence_json TEXT
NULL,state_observed_at TEXT NOT NULL,PRIMARY KEY(source_namespace,
native_stream_identity,dimension),FOREIGN KEY(source_namespace,
native_stream_identity) REFERENCES source_streams(source_namespace,
native_stream_identity),CHECK((latch_state='latched' AND failure_code IS NOT
NULL AND failure_evidence_json IS NOT NULL AND recovery_evidence_json IS NULL)
OR (latch_state='clear' AND failure_code IS NULL AND failure_offset IS NULL AND
failure_evidence_json IS NULL AND recovery_evidence_json IS NOT NULL)),CHECK(
(dimension='storage' AND (failure_code IS NULL OR failure_code=
'ledger_storage_hold')) OR (dimension='quarantine' AND (failure_code IS NULL OR
failure_code IN ('record_limit','unknown_kind','recognized_malformed',
'schema_inconsistent','unregistered_category','identity_collision',
'unsupported_accounting_profile'))) OR (dimension='retention' AND
(failure_code IS NULL OR failure_code='retention_gap')) OR (dimension=
'envelope' AND (failure_code IS NULL OR failure_code=
'source_envelope_exceeded')) OR (dimension='reconciliation' AND (failure_code
IS NULL OR failure_code='reconciliation_overdue')) OR (dimension='tail' AND
(failure_code IS NULL OR failure_code='incomplete_tail')) OR (dimension=
'coverage' AND (failure_code IS NULL OR failure_code='coverage_unknown'))))`.
Every table declared by this requirement, including
`stream_health_latches`, MUST be created with SQLite `STRICT`; no affinity-only
exception exists. Every new stream MUST receive the exact stream-owned
`LatchSet` initialization proposal as all seven latch rows in its creation
transaction with code-owned initialization recovery evidence.
`source_streams.state`, `failure_code`, and `failure_offset` MUST be a
transactionally maintained cache checked against that same proposed `LatchSet`
result and MUST NOT replace or delete another dimension's row. The ledger owns
table shape, persistence, and cache agreement; it MUST NOT implement latch
transition legality, precedence, sibling preservation, or recovery policy.
Extraction and projection registries cannot add any table beyond this corrected
exact set.

ID: REQ-durable-local-ledger-001
Source: RFC 0001 § SQLite Ledger and Atomicity; § Privacy and Cardinality Budget
Scope: v1-mandatory

#### Scenario: Fresh ledger has the exact schema
- **WHEN** the initial migration creates a new v1 ledger
- **THEN** schema inspection reports exactly the declared `STRICT` tables, columns, declared types, nullability, keys, checks, and foreign keys, including all seven initialized stream-latch dimensions
- **AND** foreign-key enforcement and integrity checking are enabled before collection, and negative introspection attempts every incompatible SQLite storage class against every typed column, including wrong-class non-null values for nullable columns, with every attempt rejected atomically

#### Scenario: Registry cannot mutate storage shape
- **WHEN** a source or sink configuration names an unregistered ledger field or table
- **THEN** the field is not stored and the closed ledger schema remains unchanged

#### Scenario: Component outcomes are closed and content-safe
- **WHEN** startup registers an enabled or disabled source, quota capability, or sink
- **THEN** exactly one canonical component row records only its technical key, closed state, safe code, timestamps, and nullable presentation alias
- **AND** quota `unavailable`, `absent`, `null`, and `state_only` remain distinct without creating a fact or numeric utilization
- **AND** overlapping source degradation writes persist only the stream-owned `LatchSet` proposal and matching checked cache, which expose the fixed highest active state across restart and every clear order without ledger-owned precedence logic

#### Scenario: Administrative fields have closed provenance
- **WHEN** a ledger, release, migration, component, request, diagnostic, sink binding, attempt, or approved privacy repair row is committed
- **THEN** `ledger_state.created_at`, `release_profile_state.accepted_at`, `schema_migrations.applied_at`, `component_registrations.registered_at`, `sink_registrations.bound_at`, and `privacy_repair_audit.completed_at` MUST come from the successful owning transaction's UTC clock; `component_registrations.last_source_observed_at` MUST be the greatest committed source-observed time for that component or null; and `selected_sink_registration` MUST be the exact active registration identity while enabled, retain that same identity when a previously bound sink is disabled, and be null only for a never-bound disabled sink
- **AND** `logical_requests.first_fact_identity` and `first_ledger_seq` MUST identify the lowest-sequence committed usage fact for that request; diagnostic path/type/measure fields MUST come only from the rejected profile member and its capped measurement while first/last-seen times come from the first/current diagnostic transactions; `sink_checkpoints.attempt_id` MUST be the stable attempt identity persisted before delivery and reused for the identical pending target; and repair ID/completion fields MUST come only from the signed approved repair plan and its successful transaction

### Requirement: [TARGET-STATE] Identity, Sequence, Cursor, and Checkpoint Constraints
MUST enforce complete composite fact-identity uniqueness through the `facts` unique key, exact canonical `fact_identity` bytes as the primary key, globally unique strictly increasing `ledger_seq` allocated only to new facts in the source-adapter-owned candidate order, unique event-category amounts, one source row per source namespace and native stream identity, one first-seen logical request row per complete request key, and one content-safe registration, checkpoint, and at most one OTLP lease per complete sink tuple and ledger epoch. An enabled sink's first bind MUST atomically insert its immutable registration and zero checkpoint before client or lease creation; restart MUST recompute and byte-compare both digests; reuse with either digest changed MUST fail before client creation or progress; a legitimate target or policy change MUST use a new tuple at origin; and migrations MUST preserve registration identity and both digests byte-for-byte. PostgreSQL MUST never create a lease.

ID: REQ-durable-local-ledger-002
Source: RFC 0001 § SQLite Ledger and Atomicity
Scope: v1-mandatory

#### Scenario: Multi-fact record receives deterministic sequences
- **WHEN** one complete record yields a new usage fact and multiple new quota facts
- **THEN** their new sequences are contiguous and allocated in the adapter's declared candidate order
- **AND** retry observes the same identities without allocating new sequences

#### Scenario: Constraint violation is atomic
- **WHEN** an insert violates any mandatory identity, sequence, amount, request, cursor, checkpoint, or lease constraint
- **THEN** the transaction fails without partial state

#### Scenario: Sink registration mismatch cannot reuse progress
- **WHEN** restart resolves a different canonical target or effective projection policy under an existing checkpoint tuple
- **THEN** digest comparison fails, the prior registration and checkpoint remain unchanged, and no client, lease, send, or acknowledgement occurs

#### Scenario: Disabling a previously bound sink retains inert progress
- **WHEN** configuration disables a sink whose component selects a bound registration
- **THEN** one local transaction sets its component to `configured_state=disabled,runtime_state=disabled,state_code=NULL`, retains `selected_sink_registration`, its immutable registration, acknowledged sequence, and historical attempt/success times, resets the retained checkpoint to `state=idle`, clears `target_ledger_seq`, `target_export_time_unix_nano`, `target_batch_count`, `target_projection_digest`, `attempt_id`, and `failure_code`, and deletes any matching lease
- **AND** after that transaction no exporter, pool, client, credential reader, worker, task, DNS, authentication, or connection exists; re-enable MUST validate the retained registration before any such runtime object is created

### Requirement: [TARGET-STATE] Atomic Consumed-Record Transaction
MUST use one SQLite transaction per consumed complete record, only after a ledger/storage-owned `AdmissionDecision=permitted` is revalidated and consumed, to classify and deduplicate its deterministic zero-or-more domain-fact set, allocate sequences and insert all new facts and amounts, update usage aggregates and first-seen request rows only for new contributions, persist every permitted quota/component-state transition plus the complete cursor/parser context and any stream-owned `LatchSet` proposal with its matching checked cache exactly once, update `last_transaction_at` and the exact counters, and expose every new sequence to each enabled sink's backlog through the same authoritative sequence domain. The ledger MUST validate/persist but MUST NOT recreate domain identity/fingerprint/category/age or `LatchSet` policy. A zero-fact complete record may commit only with the exact code/profile-registered disposition `registered_irrelevant`, `context_only`, or `quota_state_only`, and its permitted unchanged/context or quota-component transition MUST commit atomically with its cursor; unknown, unregistered, malformed, collided, or failed records MUST hold before the record with none of those effects. `accepted_count` counts newly committed facts, `duplicate_count` counts duplicate fact candidates in committed record outcomes, and `held_count` counts a new `(source_namespace,native_stream_identity,failure_code,failure_offset)` hold episode once rather than reminder retries. `model_bucket_json` and `project_bucket_json` MUST be RFC 8785 canonical JSON exactly `["null"]` for a null dimension or `["value",value]` for a known string, so null cannot collide with any literal value including `unknown`.

ID: REQ-durable-local-ledger-003
Source: RFC 0001 § SQLite Ledger and Atomicity
Scope: v1-mandatory

#### Scenario: Registered irrelevant or context-only record commits atomically
- **WHEN** a complete record has disposition `registered_irrelevant` or `context_only` and yields no facts
- **THEN** one transaction commits its complete cursor, permitted unchanged or changed parser context, applicable component state, transaction time, and counters
- **AND** no sequence, aggregate, request, or sink work is created

#### Scenario: Quota state-only record advances atomically
- **WHEN** a complete supported record has disposition `quota_state_only` because the registered quota member is absent, explicitly null, or state-only
- **THEN** the matching distinct quota component state and the cursor commit in one transaction with no fact, sequence, amount, aggregate, or sink obligation

#### Scenario: Null aggregate buckets cannot collide
- **WHEN** committed events contain a null model or project and other events contain the literal string `unknown`
- **THEN** the canonical tagged bucket keys remain distinct and both token and request aggregates conserve their separate contributions

#### Scenario: Coordinated write failure rolls back
- **WHEN** any fact, amount, aggregate, logical-request, cursor, or obligation write fails for a multi-fact record
- **THEN** every change from that record rolls back together and retry begins before the record

### Requirement: [TARGET-STATE] Duplicate-Only Cursor Advancement
SHALL allow a record whose complete fact set consists only of same-identity and same-fingerprint duplicates to advance its complete source cursor and parser context and increment only the durable duplicate outcome count and transaction time, with no new fact, amount, accounting aggregate, sequence, logical-request contribution, or sink work, while interruption leaves cursor and accounting mutually consistent for retry.

ID: REQ-durable-local-ledger-004
Source: RFC 0001 § SQLite Ledger and Atomicity; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: Duplicate-only record advances safely
- **WHEN** every fact emitted by a complete record already exists with equal fingerprint and normalized values
- **THEN** one cursor-and-health transaction commits, duplicate count increases by the number of duplicate candidates, and all accepted-fact and accounting-contribution counts remain unchanged

#### Scenario: Crash before duplicate commit is replay-safe
- **WHEN** the process crashes after observing duplicates but before the cursor transaction commits
- **THEN** restart reprocesses the same record without duplicate accounting or cursor outrun

### Requirement: [TARGET-STATE] Independent Durable Sink Acknowledgement
MUST expose one ledger-owned `LedgerProjectionReader` over committed normalized facts, aggregates, selected quota, sequence targets, and guarded checkpoint operations, and MUST advance only one registered complete sink tuple's `acknowledged_ledger_seq` in its own guarded SQLite transaction after durable destination acknowledgement. OTLP and PostgreSQL MUST consume only this interface and MUST NOT import or query the stable public views or private tables. The ledger MUST require canonical target and projection-policy digests still to match, keep target sequence, persisted OTLP export time, batch count, projection digest, and attempt state pending for failed or ambiguous acknowledgement, and never satisfy another sink, erase a retained fact, or advance state solely in memory.

ID: REQ-durable-local-ledger-005
Source: RFC 0001 § SQLite Ledger and Atomicity; § Sink Independence
Scope: v1-mandatory

#### Scenario: Durable acknowledgement advances one checkpoint
- **WHEN** one destination durably acknowledges all work through a target sequence and local admission succeeds
- **THEN** only its checkpoint advances monotonically to that sequence

#### Scenario: Lost acknowledgement remains pending
- **WHEN** destination commit succeeds but acknowledgement is lost or local checkpoint persistence fails
- **THEN** the local checkpoint stays pending and retry validates destination idempotency before advancing
- **AND** no other checkpoint changes

#### Scenario: Bound target changes before acknowledgement
- **WHEN** the effective endpoint, database, schema, or projection policy no longer hashes to the registration while a target is pending
- **THEN** the checkpoint becomes `blocked` with `registration_mismatch`, preserves all pending target fields, and performs no delivery or acknowledgement

### Requirement: [TARGET-STATE] Indefinite Accepted-History Retention
MUST retain every committed usage event, quota snapshot, amount, logical request, source evidence, identity, accounting fingerprint, ledger sequence, and reconstructable aggregate indefinitely, and MUST NOT retract it, decrement aggregates, or delete remote history after source truncation, rotation, deletion, or disappearance.

ID: REQ-durable-local-ledger-006
Source: RFC 0001 § Retention, Maintenance, and Storage Pressure; about/heart-and-soul/vision.md § Non-Negotiable Principles → 1. Local Facts Become User-Owned History
Scope: v1-mandatory

#### Scenario: Source deletion does not retract history
- **WHEN** a source file is deleted after its facts commit
- **THEN** ledger rows, logical requests, and aggregates remain unchanged and health records only the applicable source state

#### Scenario: Retained history remains available to a later sink
- **WHEN** a new optional sink is enabled after source files have disappeared
- **THEN** its origin catch-up is driven from every retained applicable ledger fact

### Requirement: [TARGET-STATE] Lossless Migration and Maintenance
SHALL require every schema migration to have a unique integer version, immutable artifact digest, all-old or all-new transaction outcome, forward compatibility declaration, and executable pre/post logical snapshot vectors; integrity checks, backup, index rebuild, `VACUUM`, and migrations MUST preserve every logical row, identity, amount, sequence, component and quota state, sink registration and both digests, pending target metadata, checkpoint, epoch, ledger-health counter/time, tagged aggregate bucket, and stable-v1-view result, and TTL, pruning, sampling, aggregate-only replacement, fabricated disabled-sink checkpoint, or abandoned checkpoint work MUST remain absent.

ID: REQ-durable-local-ledger-007
Source: RFC 0001 § Retention, Maintenance, and Storage Pressure; § Compatibility and Evolution
Scope: v1-mandatory

#### Scenario: Lossless migration preserves the logical snapshot
- **WHEN** a versioned migration is applied to every supported prior schema fixture
- **THEN** all identities, facts, amounts, requests, sequences, epochs, checkpoints, aggregates, every independent latch and its failure/recovery evidence, and stable v1 view rows match the declared post-migration oracle

#### Scenario: Lossy migration is rejected
- **WHEN** a migration would drop a retained row, reset sequence or epoch, weaken a constraint, or change a stable v1 view result
- **THEN** migration fails and collection does not resume on the changed state

#### Scenario: Migration preserves registrations and state-only evidence
- **WHEN** a supported prior v1 fixture contains sink bindings, a disabled never-bound sink, null-tagged aggregates, and quota component states without facts
- **THEN** the post-migration oracle preserves every binding digest, keeps the never-bound sink checkpoint-free, preserves every `STRICT` declaration and per-column storage-class rejection, and returns byte-equal component, latch, aggregate, health, and view semantics

### Requirement: [TARGET-STATE] Exact Storage-Admission Profile Schema
MUST own the storage-admission provider and exact result type `AdmissionDecision`, whose closed outcome is `permitted|denied` plus content-free capacity/profile evidence. The active storage profile MUST provide byte-valued unsigned `minimum_volume_bytes`, `max_consumed_record_transaction_bytes`, `fixed_transaction_charge_bytes`, per-table `row_charge_bytes`, per-index `entry_charge_bytes`, `wal_page_bytes`, `max_wal_pages_per_transaction`, `post_commit_reserve_bytes`, and a strictly greater `resume_available_bytes`, with evidence digests and native results; the provider MUST compute `charge_bytes=fixed_transaction_charge_bytes+Σ(new_rows×row_charge_bytes)+Σ(new_index_entries×entry_charge_bytes)+(max_wal_pages_per_transaction×wal_page_bytes)` using checked arithmetic. A permitted decision covering the maximum admitted record transaction MUST exist before record traversal, and the ledger MUST revalidate/consume a permitted decision before commit; denial at either gate has no parser/application value or record-set effect. Parser/adapters consume the injected decision and may use fakes in their own tests, but MUST NOT implement or import this provider.

ID: REQ-durable-local-ledger-008
Source: RFC 0001 § Retention, Maintenance, and Storage Pressure
Scope: v1-mandatory

#### Scenario: Exact guard boundary admits
- **WHEN** the transaction is within its immutable profiled shape and available bytes exactly equal charge plus post-commit reserve
- **THEN** the provider returns `AdmissionDecision=permitted`, traversal may begin, and revalidation permits the transaction to attempt atomically

#### Scenario: Unprovable capacity denies before cursor advance
- **WHEN** free space is one byte below the guard, capacity cannot be inspected, a coefficient is absent, transaction size exceeds its maximum, or charge arithmetic overflows
- **THEN** the provider returns `AdmissionDecision=denied`, no record byte is parsed at the pre-traversal gate, all source cursors hold in `ledger_storage_hold`, and no partial write remains

### Requirement: [TARGET-STATE] Storage-Failure Hold and Recovery
MUST roll back coordinated state after process interruption, `SQLITE_FULL`, `SQLITE_IOERR`, failed or ambiguous commit, or concurrent capacity loss; when read-only reopen cannot immediately prove a clean rollback and declared integrity, ledger health MUST report `availability_state=storage_hold`, every source stream MUST report `state=storage_hold,failure_code=ledger_storage_hold` at its prior cursor, no fact/checkpoint may advance, and overall health MUST be `degraded` while readable or `unavailable` when the ledger cannot be read. Writes may resume only after read-only reopen, transaction and declared integrity verification, valid capacity at or above `resume_available_bytes`, and retry of the identical input, without automatic pruning; a cleanly verified ordinary interruption may retry directly from the prior cursor without fabricating a hold episode.

ID: REQ-durable-local-ledger-009
Source: RFC 0001 § Retention, Maintenance, and Storage Pressure; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: Verified recovery resumes identical input
- **WHEN** a held ledger reopens read-only, passes transaction and integrity checks, and capacity reaches the distinct resume threshold
- **THEN** the collector retries the identical held record before accepting later source progress

#### Scenario: SQLite full remains held across restart
- **WHEN** SQLite reports `FULL` at any write stage or restart occurs before all recovery gates pass
- **THEN** no source cursor advances and the ledger remains `ledger_storage_hold` without pruning retained history

#### Scenario: Process interruption has one evidence-based branch
- **WHEN** restart follows an interrupted SQLite transaction
- **THEN** verified clean rollback retries from the prior cursor, while ambiguous or failed verification stores `storage_hold/ledger_storage_hold` and exposes degraded or unavailable health until every recovery gate passes

#### Scenario: Unreadable ledger uses out-of-band health only
- **WHEN** the ledger cannot be opened or read
- **THEN** no SQLite view result is claimed and the local inspection command emits only REQ-local-query-contract-006's exact out-of-band `aiut.health/v1` unavailable-ledger variant
- **AND** the inspection performs no write, migration, repair, retry, DNS lookup, listener creation, or other network activity

### Requirement: [TARGET-STATE] Operation-Specific Maintenance Headroom
MUST require each `backup`, `migration`, `checkpoint`, and `vacuum` profile member to supply byte-valued unsigned `base_headroom_bytes` and rational `size_multiplier_numerator/size_multiplier_denominator` with a nonzero denominator, compute required headroom as `base_headroom_bytes+ceil((database_bytes+auxiliary_bytes)×numerator/denominator)` using checked arithmetic, and prohibit the operation from consuming the ingestion reserve or acknowledging state only in memory.

ID: REQ-durable-local-ledger-010
Source: RFC 0001 § Retention, Maintenance, and Storage Pressure
Scope: v1-mandatory

#### Scenario: Measured headroom permits lossless maintenance
- **WHEN** current database and auxiliary sizes yield a valid operation charge and available capacity covers both that charge and the ingestion reserve
- **THEN** the selected lossless operation may begin and records its durable outcome

#### Scenario: Insufficient headroom preserves reserve
- **WHEN** a backup, migration, checkpoint, or `VACUUM` lacks its required headroom or checked arithmetic fails
- **THEN** the operation does not start or advance and the normal ingestion reserve is preserved

### Requirement: [TARGET-STATE] Owner-Authorized Privacy Repair
MUST stop normal collection and affected exports when forbidden content or credentials are discovered in retained state, require an explicit owner-approved plan digest before mutation, operate on an isolated verified backup, remove only contract-invalid data, rebuild every dependent aggregate and checkpoint, record one content-free repair audit row, and prove forbidden bytes and digests absent from all live copies and destinations before resumption.

ID: REQ-durable-local-ledger-011
Source: RFC 0001 § Retention, Maintenance, and Storage Pressure
Scope: v1-mandatory

#### Scenario: Approved repair proves absence and consistency
- **WHEN** the owner approves an exact repair plan and the isolated repair removes only invalid data
- **THEN** rebuilt aggregates and checkpoints match the remaining valid facts and the audit stores only plan and absence-evidence digests plus counts
- **AND** normal activity resumes only after every affected live copy and destination passes the absence proof

#### Scenario: Unapproved repair cannot mutate history
- **WHEN** forbidden sentinel content is found in a live ledger without an approved repair plan
- **THEN** collection and affected export remain stopped and no mutation occurs
