## ADDED Requirements

### Requirement: [TARGET-STATE] Independent PostgreSQL Checkpoint Identity
MUST identify every enabled PostgreSQL instance by exactly `(sink_id,destination_id,projection_schema_id,ledger_epoch)`, persist the database target, schema name, and narrowed projection-policy digest against that tuple, reject reuse for a different database, schema, policy, or ledger, and initialize a new tuple at acknowledged sequence zero to backfill every retained fact independently of OTLP.

ID: REQ-postgresql-history-projection-001
Source: RFC 0001 § Sink Independence
Scope: v1-mandatory

#### Scenario: New PostgreSQL destination backfills origin
- **WHEN** a new complete checkpoint tuple is enabled after retained history exists
- **THEN** delivery begins at ledger origin and projects every applicable retained sequence in order
- **AND** OTLP state is unchanged

#### Scenario: Reused destination identity is rejected
- **WHEN** a database target or schema changes under the same `destination_id` or a new sink is configured to skip old sequences
- **THEN** configuration or backfill fails before checkpoint advancement

### Requirement: [TARGET-STATE] Exact PostgreSQL V1 Schema
MUST freeze `projection_schema_id="aiut-postgresql-history/v1"` and exactly these conceptual relations: `usage_events(fact_identity bytea PRIMARY KEY,collector_namespace text NOT NULL,ledger_namespace text NOT NULL,ledger_epoch text NOT NULL,adapter_schema_id text NOT NULL,source_namespace text NOT NULL,fact_kind text NOT NULL CHECK(fact_kind='usage_event'),native_identity_json text NOT NULL,accounting_fingerprint bytea NOT NULL CHECK(octet_length(accounting_fingerprint)=32),ledger_seq bigint NOT NULL CHECK(ledger_seq>0),source_observed_at timestamptz NOT NULL,collected_at timestamptz NOT NULL,tool text NOT NULL,vendor text NOT NULL,model text NULL,project text NULL,native_request_identity_json text NULL,request_identity bytea NULL,metadata jsonb NOT NULL CHECK(metadata='{}'::jsonb),UNIQUE(collector_namespace,ledger_namespace,adapter_schema_id,source_namespace,fact_kind,native_identity_json),UNIQUE(ledger_namespace,ledger_epoch,ledger_seq))`; `usage_event_amounts(fact_identity bytea NOT NULL REFERENCES usage_events(fact_identity),category text NOT NULL,amount bigint NOT NULL CHECK(amount>=0),PRIMARY KEY(fact_identity,category))`; `quota_snapshots(fact_identity bytea PRIMARY KEY,collector_namespace text NOT NULL,ledger_namespace text NOT NULL,ledger_epoch text NOT NULL,adapter_schema_id text NOT NULL,source_namespace text NOT NULL,fact_kind text NOT NULL CHECK(fact_kind='quota_snapshot'),native_identity_json text NOT NULL,accounting_fingerprint bytea NOT NULL CHECK(octet_length(accounting_fingerprint)=32),ledger_seq bigint NOT NULL CHECK(ledger_seq>0),source_observed_at timestamptz NULL,collected_at timestamptz NOT NULL,account_alias text NULL,vendor text NOT NULL,limit_name text NOT NULL,native_limit_identity text NOT NULL,native_window_identity text NOT NULL,native_scope_identity text NOT NULL,utilization numeric NOT NULL CHECK(utilization>=0 AND utilization<=1),window_minutes bigint NULL CHECK(window_minutes>=0),reset_at timestamptz NULL,scope text NULL,freshness_state text NOT NULL CHECK(freshness_state IN ('fresh','stale','unknown')),freshness_evidence text NOT NULL,metadata jsonb NOT NULL CHECK(metadata='{}'::jsonb),UNIQUE(collector_namespace,ledger_namespace,adapter_schema_id,source_namespace,fact_kind,native_identity_json),UNIQUE(ledger_namespace,ledger_epoch,ledger_seq))`; and `projection_checkpoints(sink_id text NOT NULL,destination_id text NOT NULL,projection_schema_id text NOT NULL CHECK(projection_schema_id='aiut-postgresql-history/v1'),ledger_epoch text NOT NULL,acknowledged_ledger_seq bigint NOT NULL CHECK(acknowledged_ledger_seq>=0),updated_at timestamptz NOT NULL,PRIMARY KEY(sink_id,destination_id,projection_schema_id,ledger_epoch))`, with a database-enforced update guard that rejects any decrease of acknowledged sequence.

ID: REQ-postgresql-history-projection-002
Source: RFC 0001 § PostgreSQL Historical Projection; § Specification and Doctrine Boundary → Required before implementation or release OpenSpec
Scope: v1-mandatory

#### Scenario: Destination schema matches exactly
- **WHEN** the PostgreSQL projection is enabled
- **THEN** schema validation finds the exact relation names, columns, SQL types, nullability, checks, foreign key, primary keys, unique keys, and monotonic checkpoint guard

#### Scenario: Weakened schema blocks delivery
- **WHEN** any required identity component or constraint is missing, an amount can outlive its event, utilization is unbounded, or checkpoint sequence can decrease
- **THEN** schema validation fails and delivery is not enabled

### Requirement: [TARGET-STATE] Mandatory Envelope and Closed Metadata Allowlist
MUST always project every technical identity, fingerprint, epoch, sequence, and checkpoint field declared by the v1 schema; define the only configurable descriptive fields as the existing `model`, `project`, `account_alias`, and `native_request_identity_json` columns; define the v1 extension-metadata allowlist as empty so `metadata` is exactly `{}`; allow configuration only to replace a selected descriptive value with null where its column permits null or disable its nontechnical presentation; and prohibit raw records, content, credentials, paths, or unregistered fields before the sink boundary.

ID: REQ-postgresql-history-projection-003
Source: RFC 0001 § PostgreSQL Historical Projection; § Privacy and Cardinality Budget
Scope: v1-mandatory

#### Scenario: Technical envelope is always complete
- **WHEN** an enabled destination narrows every optional descriptive selection
- **THEN** fact identity, source namespaces, fingerprint, ledger epoch and sequence, source and collection times, categories, and checkpoint identity remain present

#### Scenario: Unlisted JSONB or raw field is rejected
- **WHEN** configuration selects an unlisted JSONB key, path, raw source field, content value, or credential
- **THEN** the value is denied before destination serialization and does not alter the mandatory envelope

### Requirement: [TARGET-STATE] Transactional Sequence-Batch Delivery
MUST use one PostgreSQL transaction for a contiguous ascending ledger-sequence batch, insert each usage event before all its amount rows, insert each quota snapshot, compare any pre-existing idempotency rows, and advance `projection_checkpoints` only after every fact in the batch is present and equal; the local checkpoint MUST wait for durable PostgreSQL commit acknowledgement.

ID: REQ-postgresql-history-projection-004
Source: RFC 0001 § PostgreSQL Historical Projection
Scope: v1-mandatory

#### Scenario: Complete batch commits atomically
- **WHEN** all event, amount, quota, equality, and checkpoint operations succeed for a contiguous batch
- **THEN** one destination transaction exposes the complete rows and advances its remote checkpoint to the batch end
- **AND** local acknowledgement follows only after durable commit confirmation

#### Scenario: Partial insert rolls back
- **WHEN** quota or amount insertion, equality comparison, or checkpoint advancement fails after an event insert
- **THEN** the entire destination transaction rolls back and neither destination nor local checkpoint advances

### Requirement: [TARGET-STATE] Exact Idempotency Equality and Conflict Behavior
MUST treat a retry row as equal only when every projected column other than `projection_checkpoints.updated_at` compares equal under PostgreSQL value equality, bytea identity and fingerprint compare byte-for-byte, canonical identity JSON text compares byte-for-byte, timestamps identify the same instant, numeric utilization compares exactly, amount rows match as a complete category-to-value set, and metadata equals `{}`; an unequal pre-existing row MUST block delivery and MUST never be overwritten.

ID: REQ-postgresql-history-projection-005
Source: RFC 0001 § PostgreSQL Historical Projection
Scope: v1-mandatory

#### Scenario: Lost acknowledgement retries safely
- **WHEN** PostgreSQL committed an equal batch but local acknowledgement was lost
- **THEN** retry recognizes all equal rows, leaves them unchanged, and may advance the remote and then local checkpoint monotonically

#### Scenario: Conflicting idempotency row blocks
- **WHEN** any existing identity row differs in fingerprint, normalized value, amount set, time, metadata, or technical envelope
- **THEN** delivery enters `blocked`, no row is overwritten, and no checkpoint advances

### Requirement: [TARGET-STATE] Historical Source-Time Preservation
MUST preserve source-observed event or snapshot time independently of collection, retry, batch, destination commit, and delivery time, keep null only where quota source time is contractually unavailable, and never substitute a later timestamp for source chronology.

ID: REQ-postgresql-history-projection-006
Source: RFC 0001 § Event Time and Projection Time
Scope: v1-mandatory

#### Scenario: Current delivery retains source chronology
- **WHEN** a newly accepted fact is projected promptly
- **THEN** its source and collection timestamps remain distinct destination columns with their original meanings

#### Scenario: Late rescan repairs old history
- **WHEN** an old source fact is discovered after a sink outage or later reconciliation
- **THEN** its destination row keeps source time and does not substitute delivery or collection time

### Requirement: [TARGET-STATE] Lossless PostgreSQL Schema Evolution
MUST use explicit ordered migrations with immutable artifact digests and executable pre/post vectors, apply each migration transactionally, preserve every projected row and value, full identity uniqueness, amount foreign-key completeness, event time, category separation, exact idempotency comparisons, and monotonic checkpoints, and keep tuning, indexes, and tool choice from weakening those constraints.

ID: REQ-postgresql-history-projection-007
Source: RFC 0001 § PostgreSQL Historical Projection; § Compatibility and Evolution
Scope: v1-mandatory

#### Scenario: Compatible migration preserves all rows
- **WHEN** a versioned migration runs against every supported prior destination fixture
- **THEN** post-migration logical rows, uniqueness, equality behavior, event times, categories, and checkpoints match the declared oracle

#### Scenario: Constraint-weakening migration fails
- **WHEN** a migration would relax a unique or foreign key, merge categories, reset a checkpoint, rewrite source time, or change equality semantics
- **THEN** migration fails transactionally and projection remains blocked

### Requirement: [TARGET-STATE] PostgreSQL Failure Isolation and Catch-Up
MUST leave failed or unavailable PostgreSQL work pending at its prior local and remote sequence, degrade only that sink, retain every local fact for later catch-up, and never stop source collection or OTLP or advance because another sink succeeded.

ID: REQ-postgresql-history-projection-008
Source: RFC 0001 § Sink Independence; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: Recovered destination catches up
- **WHEN** a retrying PostgreSQL destination becomes available with its schema and identity unchanged
- **THEN** it resumes from the prior acknowledged sequence and catches up retained history in ascending sequence batches

#### Scenario: PostgreSQL outage is isolated
- **WHEN** PostgreSQL is unavailable while OTLP succeeds
- **THEN** PostgreSQL remains `retrying` at its prior sequence and OTLP and source progress continue independently
