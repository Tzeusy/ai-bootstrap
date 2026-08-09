## ADDED Requirements

### Requirement: [TARGET-STATE] Independent PostgreSQL Checkpoint Identity
MUST identify every enabled PostgreSQL instance by exactly `(sink_id,destination_id,projection_schema_id,ledger_epoch)`, encode its content-safe canonical target document as exactly `{"kind":"postgresql","host_ascii":string,"port":unsigned-integer,"database":string,"schema":string}`, and encode its effective policy document as exactly `{"schema":"aiut.postgresql-policy/v1","projection_schema_id":"aiut-postgresql-history/v1","postgresql_projection_profile_digest":lowercase-hex-sha256,"fields":sorted-array,"project_aliases":sorted-array,"account_alias":string-or-null}`. V1 MUST accept one TCP host, lowercase its IDNA ASCII host, materialize the default or explicit port and exact database from the runtime DSN, take schema from validated TOML, reject multi-host and absent database input, and exclude username, password, secret parameters, and TLS material from both documents and every persisted surface. The ledger MUST persist SHA-256 over `UTF-8("aiut-sink-target-v1\n")` plus RFC 8785 target bytes and SHA-256 over `UTF-8("aiut-sink-policy-v1\n")` plus RFC 8785 policy bytes against the full tuple; the enabled sink MAY read and content-safely parse the local runtime-injected DSN solely to derive that target document; first enable MUST bind registration and a zero checkpoint, and restart MUST byte-compare the recomputed target and policy digests, before pool creation, authentication, DNS, or network connection; raw DSN and credential-bearing parse values MUST be discarded after derivation without persistence, diagnostics, or logging; any database/schema/policy/schema-id/ledger change under the tuple MUST block as `registration_mismatch`; a legitimate change MUST use a new tuple at origin; and migration MUST preserve both digests.

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

#### Scenario: Restart validates content-safe binding before network use
- **WHEN** restart reads the enabled sink's local runtime DSN and resolves the same canonical database, schema, and projection policy under the retained tuple
- **THEN** content-safe parsing derives only the target document, both persisted digests compare byte-equal before pool creation, authentication, DNS, or connection, and catch-up may resume
- **AND** the raw DSN, username, password, secret parameters, and TLS material are discarded without persistence, diagnostics, or logging

### Requirement: [TARGET-STATE] Exact PostgreSQL V1 Schema
MUST freeze `projection_schema_id="aiut-postgresql-history/v1"` and exactly these conceptual relations: `usage_events(fact_identity bytea PRIMARY KEY,collector_namespace text NOT NULL,ledger_namespace text NOT NULL,ledger_epoch text NOT NULL,adapter_schema_id text NOT NULL,source_namespace text NOT NULL,fact_kind text NOT NULL CHECK(fact_kind='usage_event'),native_identity_json text NOT NULL,accounting_fingerprint bytea NOT NULL CHECK(octet_length(accounting_fingerprint)=32),ledger_seq bigint NOT NULL CHECK(ledger_seq>0),source_observed_at timestamptz NOT NULL,collected_at timestamptz NOT NULL,tool text NOT NULL,vendor text NOT NULL,model text NULL,project text NULL,native_request_identity_json text NULL,request_identity bytea NOT NULL,metadata jsonb NOT NULL CHECK(metadata='{}'::jsonb),UNIQUE(collector_namespace,ledger_namespace,adapter_schema_id,source_namespace,fact_kind,native_identity_json),UNIQUE(ledger_namespace,ledger_epoch,ledger_seq))`; `usage_event_amounts(fact_identity bytea NOT NULL REFERENCES usage_events(fact_identity),category text NOT NULL,amount bigint NOT NULL CHECK(amount>=0),PRIMARY KEY(fact_identity,category))`; `quota_snapshots(fact_identity bytea PRIMARY KEY,collector_namespace text NOT NULL,ledger_namespace text NOT NULL,ledger_epoch text NOT NULL,adapter_schema_id text NOT NULL,source_namespace text NOT NULL,fact_kind text NOT NULL CHECK(fact_kind='quota_snapshot'),native_identity_json text NOT NULL,accounting_fingerprint bytea NOT NULL CHECK(octet_length(accounting_fingerprint)=32),ledger_seq bigint NOT NULL CHECK(ledger_seq>0),source_observed_at timestamptz NULL,collected_at timestamptz NOT NULL,account_alias text NULL,vendor text NOT NULL,limit_name text NOT NULL,native_limit_identity text NOT NULL,native_window_identity text NOT NULL,native_scope_identity text NOT NULL,utilization numeric NOT NULL CHECK(utilization>=0 AND utilization<=1),window_minutes bigint NULL CHECK(window_minutes>=0),reset_at timestamptz NULL,scope text NULL,freshness_state text NOT NULL CHECK(freshness_state IN ('fresh','stale','unknown')),freshness_evidence text NOT NULL CHECK(freshness_evidence IN ('record_timestamp','record_timestamp_and_window','record_timestamp_and_reset','record_timestamp_window_and_reset','missing_source_timestamp')),metadata jsonb NOT NULL CHECK(metadata='{}'::jsonb),UNIQUE(collector_namespace,ledger_namespace,adapter_schema_id,source_namespace,fact_kind,native_identity_json),UNIQUE(ledger_namespace,ledger_epoch,ledger_seq))`; and `projection_checkpoints(sink_id text NOT NULL,destination_id text NOT NULL,projection_schema_id text NOT NULL CHECK(projection_schema_id='aiut-postgresql-history/v1'),ledger_epoch text NOT NULL,acknowledged_ledger_seq bigint NOT NULL CHECK(acknowledged_ledger_seq>=0),updated_at timestamptz NOT NULL,PRIMARY KEY(sink_id,destination_id,projection_schema_id,ledger_epoch))`, with a database-enforced update guard that rejects any decrease of acknowledged sequence.

ID: REQ-postgresql-history-projection-002
Source: RFC 0001 § PostgreSQL Historical Projection; § Specification and Doctrine Boundary → Required before implementation or release OpenSpec
Scope: v1-mandatory

#### Scenario: Destination schema matches exactly
- **WHEN** the PostgreSQL projection is enabled
- **THEN** schema validation finds the exact relation names, columns, SQL types, nullability, checks, foreign key, primary keys, unique keys, and monotonic checkpoint guard

#### Scenario: Weakened schema blocks delivery
- **WHEN** any required identity component or constraint is missing, an amount can outlive its event, utilization is unbounded, or checkpoint sequence can decrease
- **THEN** schema validation fails and delivery is not enabled

#### Scenario: Freshness evidence is database-closed
- **WHEN** a quota row uses any freshness evidence outside the five ledger enums
- **THEN** PostgreSQL rejects the row, the destination transaction rolls back, and neither remote nor local checkpoint advances

### Requirement: [TARGET-STATE] Mandatory Envelope and Closed Metadata Allowlist
MUST always project every technical identity, fingerprint, epoch, sequence, and checkpoint field declared by the v1 schema, including non-null `request_identity` for every usage event; define the configurable descriptive-field allowlist as exactly `model|project|account_alias|native_request_identity_json`, default it to the empty set, and keep the v1 extension-metadata allowlist empty so `metadata` is exactly `{}`. If selected, `model`, `project`, and `account_alias` MUST preserve the normalized nullable value, while selected `native_request_identity_json` MUST preserve the normalized event's non-null canonical JSON; if unselected each corresponding destination column MUST be null. Configuration MUST NOT null or omit `request_identity` or any other mandatory envelope field and MUST prohibit raw records, content, credentials, paths, or unregistered fields before serialization.

ID: REQ-postgresql-history-projection-003
Source: RFC 0001 § PostgreSQL Historical Projection; § Privacy and Cardinality Budget
Scope: v1-mandatory

#### Scenario: Technical envelope is always complete
- **WHEN** an enabled destination narrows every optional descriptive selection
- **THEN** fact identity, source namespaces, fingerprint, ledger epoch and sequence, source and collection times, categories, and checkpoint identity remain present

#### Scenario: Unlisted JSONB or raw field is rejected
- **WHEN** configuration selects an unlisted JSONB key, path, raw source field, content value, or credential
- **THEN** the value is denied before destination serialization and does not alter the mandatory envelope

#### Scenario: Request columns follow normalized event semantics
- **WHEN** an event is delivered with `native_request_identity_json` excluded by the descriptive allowlist
- **THEN** `request_identity` remains non-null and byte-exact while `native_request_identity_json` is null
- **AND** selecting the native field instead requires its non-null canonical source value

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
MUST leave delivery failure as `state=retrying,failure_code=postgresql_delivery_failure` and ambiguous commit as `state=retrying,failure_code=postgresql_ack_ambiguous` at the prior local and remote sequence, clearing the code and returning to `idle` only after equality-validated durable catch-up; registration mismatch, destination schema mismatch, idempotency conflict, or failed migration MUST store `state=blocked` with respectively `registration_mismatch`, `schema_mismatch`, `idempotency_conflict`, or `migration_failed` and recover only after the exact cause is repaired under the immutable registration or a new tuple starts at origin. Every local fact remains retained, source collection and OTLP continue independently, and another sink's success never advances PostgreSQL.

ID: REQ-postgresql-history-projection-008
Source: RFC 0001 § Sink Independence; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: Recovered destination catches up
- **WHEN** a retrying PostgreSQL destination becomes available with its schema and identity unchanged
- **THEN** it resumes from the prior acknowledged sequence and catches up retained history in ascending sequence batches

#### Scenario: PostgreSQL outage is isolated
- **WHEN** PostgreSQL is unavailable while OTLP succeeds
- **THEN** PostgreSQL remains `retrying` at its prior sequence and OTLP and source progress continue independently
