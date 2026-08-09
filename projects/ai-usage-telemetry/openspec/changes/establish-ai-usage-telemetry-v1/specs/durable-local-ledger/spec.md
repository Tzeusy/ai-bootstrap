## ADDED Requirements

### Requirement: [TARGET-STATE] Exact Closed SQLite V1 Schema
SHALL make SQLite under `/data` the durable accounting authority and define exactly these private v1 tables and columns: `ledger_state(singleton INTEGER PRIMARY KEY CHECK(singleton=1),ledger_namespace TEXT NOT NULL,ledger_epoch TEXT NOT NULL UNIQUE,created_at TEXT NOT NULL,schema_version INTEGER NOT NULL,last_ledger_seq INTEGER NOT NULL CHECK(last_ledger_seq>=0))`; `release_profile_state(singleton INTEGER PRIMARY KEY CHECK(singleton=1),profile_id TEXT NOT NULL,profile_digest BLOB NOT NULL CHECK(length(profile_digest)=32),accepted_at TEXT NOT NULL)`; `schema_migrations(version INTEGER PRIMARY KEY,artifact_digest BLOB NOT NULL CHECK(length(artifact_digest)=32),applied_at TEXT NOT NULL)`; `facts(fact_identity BLOB PRIMARY KEY,collector_namespace TEXT NOT NULL,ledger_namespace TEXT NOT NULL,adapter_schema_id TEXT NOT NULL,source_namespace TEXT NOT NULL,fact_kind TEXT NOT NULL CHECK(fact_kind IN ('usage_event','quota_snapshot')),native_identity_json TEXT NOT NULL,accounting_fingerprint BLOB NOT NULL CHECK(length(accounting_fingerprint)=32),ledger_epoch TEXT NOT NULL,ledger_seq INTEGER NOT NULL UNIQUE CHECK(ledger_seq>0),source_observed_at TEXT NULL,collected_at TEXT NOT NULL,UNIQUE(collector_namespace,ledger_namespace,adapter_schema_id,source_namespace,fact_kind,native_identity_json))`; `usage_events(fact_identity BLOB PRIMARY KEY REFERENCES facts(fact_identity),tool TEXT NOT NULL,vendor TEXT NOT NULL,model TEXT NULL,project TEXT NULL,request_identity BLOB NOT NULL,metadata_json TEXT NOT NULL CHECK(metadata_json='{}'))`; `usage_event_amounts(fact_identity BLOB NOT NULL REFERENCES usage_events(fact_identity),category TEXT NOT NULL,amount INTEGER NOT NULL CHECK(amount>=0),PRIMARY KEY(fact_identity,category))`; `quota_snapshots(fact_identity BLOB PRIMARY KEY REFERENCES facts(fact_identity),subject_identity BLOB NOT NULL,account_alias TEXT NOT NULL,vendor TEXT NOT NULL,limit_name TEXT NOT NULL,native_limit_identity TEXT NOT NULL,native_window_identity TEXT NOT NULL,native_scope_identity TEXT NOT NULL,utilization_decimal TEXT NOT NULL,window_minutes INTEGER NULL CHECK(window_minutes>=0),reset_at TEXT NULL,scope TEXT NULL,freshness_state TEXT NOT NULL CHECK(freshness_state IN ('fresh','stale','unknown')),freshness_evidence TEXT NOT NULL CHECK(freshness_evidence IN ('record_timestamp','record_timestamp_and_window','record_timestamp_and_reset','record_timestamp_window_and_reset','missing_source_timestamp')),metadata_json TEXT NOT NULL CHECK(metadata_json='{}'))`; `logical_requests(request_identity BLOB PRIMARY KEY,collector_namespace TEXT NOT NULL,ledger_namespace TEXT NOT NULL,adapter_schema_id TEXT NOT NULL,source_namespace TEXT NOT NULL,native_request_identity_json TEXT NOT NULL,first_fact_identity BLOB NOT NULL REFERENCES usage_events(fact_identity),first_ledger_seq INTEGER NOT NULL UNIQUE,UNIQUE(collector_namespace,ledger_namespace,adapter_schema_id,source_namespace,native_request_identity_json))`; `usage_aggregates(ledger_epoch TEXT NOT NULL,tool TEXT NOT NULL,vendor TEXT NOT NULL,model_bucket TEXT NOT NULL,project_bucket TEXT NOT NULL,category TEXT NOT NULL,total_amount INTEGER NOT NULL CHECK(total_amount>=0),PRIMARY KEY(ledger_epoch,tool,vendor,model_bucket,project_bucket,category))`; `request_aggregates(ledger_epoch TEXT NOT NULL,tool TEXT NOT NULL,vendor TEXT NOT NULL,model_bucket TEXT NOT NULL,project_bucket TEXT NOT NULL,total_requests INTEGER NOT NULL CHECK(total_requests>=0),PRIMARY KEY(ledger_epoch,tool,vendor,model_bucket,project_bucket))`; `source_streams(source_namespace TEXT NOT NULL,native_stream_identity TEXT NOT NULL,adapter_schema_id TEXT NOT NULL,stream_generation TEXT NOT NULL,next_byte_offset INTEGER NOT NULL CHECK(next_byte_offset>=0),prefix_anchor_json TEXT NOT NULL,parser_context_json TEXT NOT NULL,state TEXT NOT NULL CHECK(state IN ('healthy','trailing_deferred','quarantined','storage_hold','reconciliation_overdue','source_envelope_exceeded','retention_gap','coverage_unknown','disabled')),last_scan_at TEXT NULL,last_accepted_source_at TEXT NULL,reconciliation_completed_at TEXT NULL,reconciliation_due_evidence_json TEXT NULL,coverage_state TEXT NOT NULL CHECK(coverage_state IN ('current','coverage_unknown','retention_gap')),failure_code TEXT NULL,failure_offset INTEGER NULL,PRIMARY KEY(source_namespace,native_stream_identity))`; `source_diagnostics(source_namespace TEXT NOT NULL,native_stream_identity TEXT NOT NULL,failure_code TEXT NOT NULL,registry_path_id TEXT NULL,expected_type TEXT NULL,capped_measure INTEGER NULL,first_seen_at TEXT NOT NULL,last_seen_at TEXT NOT NULL,repeat_count INTEGER NOT NULL CHECK(repeat_count>0),PRIMARY KEY(source_namespace,native_stream_identity))`; `sink_checkpoints(sink_id TEXT NOT NULL,destination_id TEXT NOT NULL,projection_schema_id TEXT NOT NULL,ledger_epoch TEXT NOT NULL,acknowledged_ledger_seq INTEGER NOT NULL CHECK(acknowledged_ledger_seq>=0),target_ledger_seq INTEGER NULL,target_batch_count INTEGER NULL,attempt_id TEXT NULL,state TEXT NOT NULL CHECK(state IN ('disabled','idle','delivering','retrying','blocked')),last_attempt_at TEXT NULL,last_success_at TEXT NULL,failure_code TEXT NULL,PRIMARY KEY(sink_id,destination_id,projection_schema_id,ledger_epoch))`; `sink_leases(sink_id TEXT NOT NULL,destination_id TEXT NOT NULL,projection_schema_id TEXT NOT NULL,ledger_epoch TEXT NOT NULL,holder_id TEXT NOT NULL,fencing_token INTEGER NOT NULL CHECK(fencing_token>0),expires_at TEXT NOT NULL,PRIMARY KEY(sink_id,destination_id,projection_schema_id,ledger_epoch),FOREIGN KEY(sink_id,destination_id,projection_schema_id,ledger_epoch) REFERENCES sink_checkpoints(sink_id,destination_id,projection_schema_id,ledger_epoch))`; and `privacy_repair_audit(repair_id TEXT PRIMARY KEY,approved_plan_digest BLOB NOT NULL CHECK(length(approved_plan_digest)=32),completed_at TEXT NOT NULL,removed_invalid_fact_count INTEGER NOT NULL CHECK(removed_invalid_fact_count>=0),absence_evidence_digest BLOB NOT NULL CHECK(length(absence_evidence_digest)=32))`; extraction and projection registries MUST NOT add any column or table.

ID: REQ-durable-local-ledger-001
Source: RFC 0001 § SQLite Ledger and Atomicity; § Privacy and Cardinality Budget
Scope: v1-mandatory

#### Scenario: Fresh ledger has the exact schema
- **WHEN** the initial migration creates a new v1 ledger
- **THEN** schema inspection reports exactly the declared tables, columns, declared types, nullability, keys, checks, and foreign keys
- **AND** foreign-key enforcement and integrity checking are enabled before collection

#### Scenario: Registry cannot mutate storage shape
- **WHEN** a source or sink configuration names an unregistered ledger field or table
- **THEN** the field is not stored and the closed ledger schema remains unchanged

### Requirement: [TARGET-STATE] Identity, Sequence, Cursor, and Checkpoint Constraints
MUST enforce complete composite fact-identity uniqueness through the `facts` unique key, exact canonical `fact_identity` bytes as the primary key, globally unique strictly increasing `ledger_seq` allocated only to new facts in the source-adapter-owned candidate order, unique event-category amounts, one source row per source namespace and native stream identity, one first-seen logical request row per complete request key, and one checkpoint and at most one lease per complete sink tuple and ledger epoch.

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

### Requirement: [TARGET-STATE] Atomic Consumed-Record Transaction
MUST use one SQLite transaction per consumed complete record to classify and deduplicate its deterministic zero-or-more fact set, allocate sequences and insert all new facts and amounts, update usage aggregates and first-seen request rows only for new contributions, persist the complete cursor and parser context exactly once, and expose every new sequence to each enabled sink's backlog through the same authoritative sequence domain.

ID: REQ-durable-local-ledger-003
Source: RFC 0001 § SQLite Ledger and Atomicity
Scope: v1-mandatory

#### Scenario: Context-only record commits cursor only
- **WHEN** a complete registered context-setting or irrelevant record yields no facts
- **THEN** one transaction commits only its complete cursor and parser-context outcome
- **AND** no sequence, aggregate, request, or sink work is created

#### Scenario: Coordinated write failure rolls back
- **WHEN** any fact, amount, aggregate, logical-request, cursor, or obligation write fails for a multi-fact record
- **THEN** every change from that record rolls back together and retry begins before the record

### Requirement: [TARGET-STATE] Duplicate-Only Cursor Advancement
SHALL allow a record whose complete fact set consists only of same-identity and same-fingerprint duplicates to advance only its complete source cursor and parser context, with no new fact, amount, aggregate, sequence, logical-request contribution, or sink work, while interruption leaves cursor and accounting mutually consistent for retry.

ID: REQ-durable-local-ledger-004
Source: RFC 0001 § SQLite Ledger and Atomicity; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: Duplicate-only record advances safely
- **WHEN** every fact emitted by a complete record already exists with equal fingerprint and normalized values
- **THEN** one cursor-only transaction commits and all accounting counts remain unchanged

#### Scenario: Crash before duplicate commit is replay-safe
- **WHEN** the process crashes after observing duplicates but before the cursor transaction commits
- **THEN** restart reprocesses the same record without duplicate accounting or cursor outrun

### Requirement: [TARGET-STATE] Independent Durable Sink Acknowledgement
MUST advance only one complete sink tuple's `acknowledged_ledger_seq` in its own guarded SQLite transaction after durable destination acknowledgement, keep target and attempt state pending for failed or ambiguous acknowledgement, and never satisfy another sink, erase a retained fact, or advance state solely in memory.

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
SHALL require every schema migration to have a unique integer version, immutable artifact digest, all-old or all-new transaction outcome, forward compatibility declaration, and executable pre/post logical snapshot vectors; integrity checks, backup, index rebuild, `VACUUM`, and migrations MUST preserve every logical row, identity, amount, sequence, checkpoint, epoch, and stable-v1-view result, and TTL, pruning, sampling, aggregate-only replacement, or abandoned checkpoint work MUST remain absent.

ID: REQ-durable-local-ledger-007
Source: RFC 0001 § Retention, Maintenance, and Storage Pressure; § Compatibility and Evolution
Scope: v1-mandatory

#### Scenario: Lossless migration preserves the logical snapshot
- **WHEN** a versioned migration is applied to every supported prior schema fixture
- **THEN** all identities, facts, amounts, requests, sequences, epochs, checkpoints, aggregates, and stable v1 view rows match the declared post-migration oracle

#### Scenario: Lossy migration is rejected
- **WHEN** a migration would drop a retained row, reset sequence or epoch, weaken a constraint, or change a stable v1 view result
- **THEN** migration fails and collection does not resume on the changed state

### Requirement: [TARGET-STATE] Exact Storage-Admission Profile Schema
MUST require the active storage profile to provide byte-valued unsigned `minimum_volume_bytes`, `max_consumed_record_transaction_bytes`, `fixed_transaction_charge_bytes`, per-table `row_charge_bytes`, per-index `entry_charge_bytes`, `wal_page_bytes`, `max_wal_pages_per_transaction`, `post_commit_reserve_bytes`, and a strictly greater `resume_available_bytes`, with evidence digests and native results; compute `charge_bytes=fixed_transaction_charge_bytes+Σ(new_rows×row_charge_bytes)+Σ(new_index_entries×entry_charge_bytes)+(max_wal_pages_per_transaction×wal_page_bytes)` using checked arithmetic; and admit every state-changing transaction only when capacity is valid, input is within the profiled maximum, and `available_bytes>=charge_bytes+post_commit_reserve_bytes`.

ID: REQ-durable-local-ledger-008
Source: RFC 0001 § Retention, Maintenance, and Storage Pressure
Scope: v1-mandatory

#### Scenario: Exact guard boundary admits
- **WHEN** the transaction is within its immutable profiled shape and available bytes exactly equal charge plus post-commit reserve
- **THEN** storage admission permits the transaction to attempt atomically

#### Scenario: Unprovable capacity denies before cursor advance
- **WHEN** free space is one byte below the guard, capacity cannot be inspected, a coefficient is absent, transaction size exceeds its maximum, or charge arithmetic overflows
- **THEN** admission is denied, all source cursors hold in `ledger_storage_hold`, and no partial write remains

### Requirement: [TARGET-STATE] Storage-Failure Hold and Recovery
MUST roll back coordinated state and enter `ledger_storage_hold` after `SQLITE_FULL`, `SQLITE_IOERR`, failed or ambiguous commit, or concurrent capacity loss, and MUST resume writes only after read-only reopen, transaction and declared integrity verification, valid capacity at or above `resume_available_bytes`, and retry of the identical input, without automatic pruning.

ID: REQ-durable-local-ledger-009
Source: RFC 0001 § Retention, Maintenance, and Storage Pressure; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: Verified recovery resumes identical input
- **WHEN** a held ledger reopens read-only, passes transaction and integrity checks, and capacity reaches the distinct resume threshold
- **THEN** the collector retries the identical held record before accepting later source progress

#### Scenario: SQLite full remains held across restart
- **WHEN** SQLite reports `FULL` at any write stage or restart occurs before all recovery gates pass
- **THEN** no source cursor advances and the ledger remains `ledger_storage_hold` without pruning retained history

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
