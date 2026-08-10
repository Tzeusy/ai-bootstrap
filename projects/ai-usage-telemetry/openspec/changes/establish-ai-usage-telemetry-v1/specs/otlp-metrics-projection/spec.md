## ADDED Requirements

### Requirement: [TARGET-STATE] Independent OTLP Checkpoint Identity
MUST identify every enabled OTLP instance by exactly `(sink_id,destination_id,projection_schema_id,ledger_epoch)`, encode its content-safe canonical target document as exactly `{"kind":"otlp","protocol":"http/protobuf","endpoint":{"scheme":string,"host_ascii":string,"port":unsigned-integer,"path":string}}`, and encode its effective policy document as exactly `{"schema":"aiut.otlp-policy/v1","projection_schema_id":"aiut-otlp-metrics/v1","otlp_projection_profile_digest":lowercase-hex-sha256,"narrowed_vocabularies":{"models":sorted-string-array,"projects":sorted-string-array,"accounts":sorted-string-array,"limits":sorted-string-array,"windows":sorted-string-array,"scopes":sorted-string-array},"project_aliases":sorted-array,"account_alias":string-or-null}`. The final effective metrics endpoint MUST use standard OTLP metrics-over-base precedence, require `http|https`, lowercase scheme and IDNA ASCII host, materialize the default or explicit port, normalize percent-encoding and path, and reject userinfo, query, fragment, and multi-endpoint input. The ledger MUST persist SHA-256 over `UTF-8("aiut-sink-target-v1\n")` plus RFC 8785 target bytes and SHA-256 over `UTF-8("aiut-sink-policy-v1\n")` plus RFC 8785 policy bytes against the full key; first enable MUST bind registration and a zero checkpoint before exporter or lease creation, restart MUST byte-compare recomputed digests, any endpoint/policy/schema/ledger change under the key MUST block as `registration_mismatch`, a legitimate change MUST use a new key at origin, and migration MUST preserve both digests.

ID: REQ-otlp-metrics-projection-001
Source: RFC 0001 § Sink Independence
Scope: v1-mandatory

#### Scenario: Newly enabled OTLP catches up from origin
- **WHEN** a new technical checkpoint tuple is enabled after retained facts exist
- **THEN** its first target derives the complete cumulative projection from ledger origin through the chosen sequence
- **AND** PostgreSQL state is unchanged

#### Scenario: Reused identity with changed target is rejected
- **WHEN** an endpoint or policy changes while reusing `destination_id` or a new sink is configured to start at the latest sequence
- **THEN** configuration fails before client creation or export and no checkpoint advances

#### Scenario: Restart revalidates the exact binding
- **WHEN** restart resolves the same normalized endpoint and policy document under the same full tuple
- **THEN** both digests compare byte-equal before exporter or lease creation and the retained checkpoint may resume

### Requirement: [TARGET-STATE] Exact OTLP V1 Descriptor Manifest
MUST freeze `projection_schema_id="aiut-otlp-metrics/v1"` with one Resource having exact attributes `service.name="ai-usage-telemetry"`, `service.namespace="aiut"`, `service.instance.id=<collector_namespace>`, `aiut.ledger.namespace=<ledger_namespace>`, `aiut.ledger.epoch=<ledger_epoch>`, and `aiut.projection.schema_id="aiut-otlp-metrics/v1"`; one instrumentation Scope named `ai-usage-telemetry` with version `1` and no scope attributes; and exactly four metric descriptors: `ai.usage.tokens`, unit `{token}`, description `Cumulative number of normalized AI tokens accepted by the local ledger.`, monotonic cumulative integer Sum; `ai.usage.requests`, unit `{request}`, description `Cumulative number of first-seen logical AI requests accepted by the local ledger.`, monotonic cumulative integer Sum; `ai.quota.utilization`, unit `1`, description `Latest observed local quota utilization ratio from zero through one.`, double Gauge; and `ai.quota.age`, unit `s`, description `Age in seconds of the selected local quota observation at export time.`, non-negative integer Gauge.

ID: REQ-otlp-metrics-projection-002
Source: RFC 0001 § OTLP Metrics Projection; § Specification and Doctrine Boundary → Required before implementation or release OpenSpec
Scope: v1-mandatory

#### Scenario: Descriptor set matches v1 exactly
- **WHEN** an OTLP exporter is created for `aiut-otlp-metrics/v1`
- **THEN** Resource, Scope, metric names, units, exact description text, number kinds, temporality, and monotonic flags equal the declared manifest

#### Scenario: Descriptor drift fails before export
- **WHEN** any Resource or Scope identity, descriptor, name, unit, description, kind, temporality, or monotonic flag is missing or differs
- **THEN** export fails closed before client creation or checkpoint progress

### Requirement: [TARGET-STATE] Stable Cumulative Sum Semantics
MUST derive token and request Sums only from committed ledger facts through the target `ledger_seq`, use the immutable ledger creation timestamp as every cumulative series start and export time as point time, and retain cumulative monotonic values across restart, lease turnover, retry, outage, replay, and source deletion.

ID: REQ-otlp-metrics-projection-003
Source: RFC 0001 § OTLP Metrics Projection
Scope: v1-mandatory

#### Scenario: Cumulative sums grow from ledger origin
- **WHEN** new committed token amounts and first-seen requests enter the target sequence
- **THEN** their exact series increase from the unchanged ledger start time through the new export time

#### Scenario: Restart cannot reset a series
- **WHEN** the exporter restarts after an outage or lease turnover
- **THEN** the next cumulative points retain the ledger start time and complete values rather than restarting from zero

### Requirement: [TARGET-STATE] Exact Sum Tuples and Conservation
MUST give `ai.usage.tokens` exactly point attributes `ai.tool`, `ai.vendor`, `ai.model`, `ai.project`, and `ai.token.category`, give `ai.usage.requests` exactly the first four, map every retained amount and first-seen request at or below the target sequence to exactly one complete tuple, partition token conservation by each of the seven registered categories and request conservation by the complete non-category tuple, and require every projected sum to equal the corresponding SQLite aggregate.

ID: REQ-otlp-metrics-projection-004
Source: RFC 0001 § OTLP Metrics Projection
Scope: v1-mandatory

#### Scenario: Complete tuples conserve ledger accounting
- **WHEN** a target sequence contains facts across multiple tools, models, projects, and categories
- **THEN** every contribution maps once and summing each mandatory partition equals the SQLite aggregate through that sequence

#### Scenario: Omission collision or mismatch blocks checkpoint
- **WHEN** a tuple is omitted, duplicated, collides, or totals differ from SQLite
- **THEN** the target checkpoint is blocked with sanitized health and no batch or partial target is acknowledged

### Requirement: [TARGET-STATE] Exact Quota Gauge Tuples
MUST give both quota gauges exactly point attributes `ai.account`, `ai.vendor`, `ai.quota.limit`, `ai.quota.window`, `ai.quota.scope`, and `ai.quota.freshness`; emit utilization for every selected current subject with an admitted value; emit age only when source time is non-null as the non-negative integer `floor(max(0,target_export_time_unix_nano-source_unix_nano)/1_000_000_000)` using checked signed-64-bit nanosecond subtraction; distinguish every subject injectively without aggregation; and block a target for any unrepresentable subject, arithmetic overflow, or tuple collision.

ID: REQ-otlp-metrics-projection-005
Source: RFC 0001 § OTLP Metrics Projection
Scope: v1-mandatory

#### Scenario: Current quota subject has injective gauges
- **WHEN** fixed-clock selected subjects place source time at tolerated future, equal, one-nanosecond past, and immediately below/at/above a whole export-age second
- **THEN** one utilization point and one age point share each complete tuple, future age clamps to zero, and integer age floors only the checked final nanosecond delta while preserving current freshness

#### Scenario: Quota tuple collision is non-mergeable
- **WHEN** two admitted quota subjects map to the same complete series tuple or one dimension lacks a legal value
- **THEN** OTLP degrades and acknowledges no projection for that target sequence

### Requirement: [TARGET-STATE] Closed OTLP Attribute Vocabularies
MUST admit no point attributes beyond the exact sets above; fix `ai.tool` to `claude_code|codex`, `ai.vendor` to `anthropic|openai`, `ai.token.category` to the seven ledger categories, and `ai.quota.freshness` to `fresh|stale|unknown`; require profile-enumerated finite values plus the code-owned `unknown` value for model, project, account, limit, window, and scope; permit `other` only for model or project Sum dimensions when a profile explicitly enables one counted conservation bucket; prohibit `other` for quota gauges; and never expose event or request identity, fingerprint, path, file, offset, source or reset timestamp, arbitrary metadata, or unbounded source values.

ID: REQ-otlp-metrics-projection-006
Source: RFC 0001 § OTLP Metrics Projection; § Privacy and Cardinality Budget
Scope: v1-mandatory

#### Scenario: Finite admitted attributes create a known tuple
- **WHEN** every normalized dimension belongs to its closed active vocabulary
- **THEN** the projector emits exactly the declared point attributes and no source-specific extension

#### Scenario: Requested sensitive or unbounded attribute is denied
- **WHEN** configuration requests an absolute path, request ID, fingerprint, timestamp, arbitrary model string, or unregistered metadata field
- **THEN** it is not emitted and cannot create a series
- **AND** a non-mergeable quota value blocks rather than entering `other`
- **AND** the OTLP payload/network capture must first observe its harmless positive-control canary, while a deliberate test-only sentinel leak or unexpected endpoint event makes the harness fail

### Requirement: [TARGET-STATE] Exact OTLP Budget Profile Schema
MUST require immutable byte-valued `max_attribute_utf8_bytes` per attribute, explicit legal tuple arrays per instrument, unsigned `max_series` per instrument and `max_process_series`, unsigned `max_serialized_request_bytes`, named accounting partitions, an optional single reserved `other` tuple for each allowed Sum partition, and effective SDK/exporter caps and evidence digests. The encoded-size domain MUST be exactly the uncompressed deterministic protobuf message bytes of `opentelemetry.proto.collector.metrics.v1.ExportMetricsServiceRequest` sent as the OTLP/HTTP `application/x-protobuf` body, with protocol `http/protobuf`, compression `none`, schema-descriptor digest, encoder artifact digest, deterministic serialization enabled, Resource/Scope/metric/data-point/attribute ordering fixed by this spec, and HTTP headers, HTTP framing, TLS, and transport compression excluded; these settings and digests MUST be members of `otlp_projection_profile_digest` and therefore of the persisted projection-policy digest. Startup MUST enumerate realizable complete series identities and require every project cap at or below its SDK cap, while runtime atomically rejects `N+1`, invalid UTF-8, checked-arithmetic overflow, or an unlisted tuple without eviction, omission, or first-seen semantics.

ID: REQ-otlp-metrics-projection-007
Source: RFC 0001 § OTLP Metrics Projection
Scope: v1-mandatory

#### Scenario: Exact budget boundary is accepted
- **WHEN** legal tuple enumeration and encoded request size equal every applicable accepted profile cap and SDK caps are no lower
- **THEN** exporter creation and the target projection are permitted
- **AND** every reserved `other` tuple counts inside all caps

#### Scenario: One-past or hidden lower cap fails closed
- **WHEN** legal tuple enumeration exceeds a ceiling, count arithmetic overflows, a value exceeds its UTF-8 cap, serialized output is one byte over, or the SDK cap is lower than the project cap
- **THEN** exporter creation or tuple admission fails closed and no checkpoint advances

#### Scenario: Size is counted in one frozen domain
- **WHEN** the same semantic request is encoded with a different protocol, protobuf schema descriptor, encoder artifact, deterministic setting, or compression mode
- **THEN** its OTLP profile and projection-policy digest differ and the existing registration cannot be reused

### Requirement: [TARGET-STATE] Fenced Single-Exporter Lease
SHALL allow exactly one process to export a checkpoint tuple under the ledger-backed lease row, allocate a strictly increasing fencing token on each acquisition, require unexpired holder and matching token before every send and acknowledgement, and cancel an acknowledgement path immediately upon lease loss.

ID: REQ-otlp-metrics-projection-008
Source: RFC 0001 § OTLP Metrics Projection
Scope: v1-mandatory

#### Scenario: Current holder exports
- **WHEN** one process holds an unexpired lease and current fencing token for the complete checkpoint tuple
- **THEN** it may send and acknowledge only that tuple's deterministic target batches

#### Scenario: Stale holder cannot acknowledge
- **WHEN** a stale exporter attempts acknowledgement after lease expiry and turnover
- **THEN** fencing rejects it and the current holder's checkpoint remains authoritative

### Requirement: [TARGET-STATE] Deterministic Request-Bounded Batching
MUST order a target projection by metric order `ai.usage.tokens`, `ai.usage.requests`, `ai.quota.utilization`, `ai.quota.age` and then lexicographically by the RFC 8785 canonical JSON array of its complete point attributes; in one ledger transaction before sending, persist the target sequence, one fixed `target_export_time_unix_nano` used as every point time, one-based batch count, and SHA-256 target-projection digest; greedily place the longest contiguous prefix whose exact encoded request body is at or below the active byte cap; identify each batch by `(target_ledger_seq,batch_ordinal,batch_count)`; and advance the checkpoint only after durable acknowledgement of every batch for that target. Every release vector MUST declare the fixed clock, ordered canonical point documents, exact per-batch point membership, exact encoded-body byte length and SHA-256 digest, and target projection digest; restart, lease turnover, failure, or ambiguity MUST reconstruct byte-identical bodies and retry the complete same batch set, while an individually oversized point blocks with `request_oversize`.

ID: REQ-otlp-metrics-projection-009
Source: RFC 0001 § Sink Independence
Scope: v1-mandatory

#### Scenario: Oversized target splits deterministically
- **WHEN** the complete ordered target exceeds one request but every individual point fits the accepted cap
- **THEN** repeated construction yields the same ordered batch contents, ordinals, and count

#### Scenario: Ambiguous middle batch restarts the set
- **WHEN** batch two of three is ambiguous
- **THEN** no partial target is acknowledged and retry restarts the full same three-batch set

#### Scenario: Restart preserves exact batch bytes
- **WHEN** a process restarts after persisting a target and before its final acknowledgement
- **THEN** the fixed-clock vector yields the same batch membership, byte lengths, body digests, projection digest, ordinals, and count

### Requirement: [TARGET-STATE] At-Least-Once OTLP Recovery and Isolation
MUST leave OTLP work pending after delivery failure as `state=retrying,failure_code=otlp_delivery_failure` and after ambiguous acknowledgement as `state=retrying,failure_code=otlp_ack_ambiguous`, retain the complete persisted target and retry it at least once under a valid lease, clear the code and return to `idle` only after every batch is durably acknowledged and the local checkpoint commits, preserve local facts, continue independent source and PostgreSQL progress, and make no exactly-once transport claim. Registration mismatch, descriptor/schema mismatch, tuple collision, conservation mismatch, request oversize, or failed projection migration MUST store `state=blocked` with respectively `registration_mismatch`, `schema_mismatch`, `tuple_collision`, `conservation_mismatch`, `request_oversize`, or `migration_failed`; recovery requires the exact cause to be repaired under the same immutable registration or a new tuple at origin, never a skipped target.

ID: REQ-otlp-metrics-projection-010
Source: RFC 0001 § Sink Independence; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: Retry converges cumulatively
- **WHEN** an ambiguous export is accepted more than once by the destination
- **THEN** each transmission carries the same cumulative values and collector accounting is not incremented by retry

#### Scenario: Endpoint outage is isolated
- **WHEN** the endpoint is unavailable after local commit
- **THEN** OTLP remains `retrying` with unchanged checkpoint while SQLite, sources, and PostgreSQL continue

### Requirement: [TARGET-STATE] Immutable OTLP Schema Evolution
MUST keep metric Resource, Scope, identity, descriptor text, unit, kind, temporality, monotonicity, attribute meanings, and vocabularies immutable within `aiut-otlp-metrics/v1`; an incompatible change MUST use a new projection schema ID and metric identity, start at ledger origin, and reconstruct full history, or require a new RFC-backed metric when retained history cannot reconstruct the semantics.

ID: REQ-otlp-metrics-projection-011
Source: RFC 0001 § OTLP Metrics Projection; § Compatibility and Evolution
Scope: v1-mandatory

#### Scenario: Compatible release preserves series identity
- **WHEN** implementation changes without altering any descriptor, vocabulary, tuple, or meaning
- **THEN** the existing projection schema and cumulative series continue without reset

#### Scenario: Incompatible reuse is rejected
- **WHEN** a release renames an attribute, changes a unit or description, or reinterprets a value while reusing `aiut-otlp-metrics/v1`
- **THEN** startup rejects the profile and no existing series is reset

### Requirement: [TARGET-STATE] Operational Rather Than Historical Time
SHALL represent the ledger's cumulative and current quota state at export time and MUST NOT claim per-event source chronology, attach source or collection timestamps as attributes, or present OTLP as historical retained-event storage.

ID: REQ-otlp-metrics-projection-012
Source: RFC 0001 § Event Time and Projection Time; § OTLP Metrics Projection
Scope: v1-mandatory

#### Scenario: Current projection reflects committed state
- **WHEN** all facts through a target sequence are committed
- **THEN** OTLP represents their current cumulative sums and selected quota gauges at export time

#### Scenario: Late fact does not fabricate chronology
- **WHEN** a late rescan adds an old source event
- **THEN** OTLP updates the current cumulative value without emitting collection time or source time as historical event time
