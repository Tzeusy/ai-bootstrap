## ADDED Requirements

### Requirement: [TARGET-STATE] Closed UsageEvent Shape
SHALL admit a `UsageEvent` only when it has the immutable identity tuple, `accounting_fingerprint`, `collector_namespace`, `ledger_namespace`, `adapter_schema_id`, `source_namespace`, `fact_kind="usage_event"`, source-observed time and collected time each normalized through the common checked UTC Unix-nanosecond contract and rendered in its sole fixed-nine-digit RFC 3339 `Z` form, tool, vendor, nullable model and project, native logical-request identity, zero-or-more unique registered non-negative category amounts, and the closed ledger metadata object; no other field group is part of v1 normalization.

ID: REQ-event-identity-and-normalization-001
Source: RFC 0001 § UsageEvent
Scope: v1-mandatory

#### Scenario: Complete event is admitted
- **WHEN** an adapter supplies every required identity, time, attribution, request, fingerprint, and amount field under an accepted profile
- **THEN** normalization emits one closed `UsageEvent` whose absent model or project is explicitly null

#### Scenario: Invalid event is rejected
- **WHEN** normalization cannot establish a required field, repeats a category, or produces a negative or unregistered amount
- **THEN** no `UsageEvent` is admitted and the source receives the applicable sanitized hold

### Requirement: [TARGET-STATE] Immutable Fact Identity Encoding
MUST define fact identity as the RFC 8785 canonical UTF-8 encoding of the exact ordered JSON array `[collector_namespace,ledger_namespace,adapter_schema_id,source_namespace,fact_kind,native_identity]`, where `native_identity` is the source-profile-defined canonical JSON value, and MUST exclude aliases, paths, line or byte positions, sink settings, scan order, collection time, and projection policy.

ID: REQ-event-identity-and-normalization-002
Source: RFC 0001 § UsageEvent; § Compatibility and Evolution
Scope: v1-mandatory

#### Scenario: Identity survives relocation and configuration changes
- **WHEN** the same native fact is replayed after file relocation, alias change, sink enablement, or different scan interleaving
- **THEN** the canonical fact-identity bytes are unchanged

#### Scenario: Forbidden identity participant fails a vector
- **WHEN** changing a display alias, path, offset, collection time, or sink setting changes computed fact identity
- **THEN** the canonical identity vector fails and the build is not releasable

### Requirement: [TARGET-STATE] Exact Usage Accounting Fingerprint Document
MUST compute `accounting_fingerprint` as SHA-256 over `UTF-8("aiut-accounting-fingerprint-v1\n")` followed by RFC 8785 canonical UTF-8 JSON of exactly `{"adapter_schema_id":string,"fact_kind":"usage_event","native_identity":json,"source_observed_at":RFC3339-UTC-string,"source_attribution":{"tool":string,"vendor":string,"model":string-or-null,"project":string-or-null,"native_request_identity":json},"source_consistency":object,"amounts":[[category,non-negative-integer],...]}`, where `source_observed_at` is exactly `YYYY-MM-DDTHH:MM:SS.nnnnnnnnnZ` derived by checked conversion of an explicit-offset, non-leap-second RFC 3339 instant representable as non-negative signed-64-bit UTC Unix nanoseconds, with amount pairs in registry order, Claude `source_consistency` exactly `{"message_id":string}`, Codex `source_consistency` exactly `{}`, and no ledger sequence, collection time, path, alias, extension metadata, allowlist, or sink field.

ID: REQ-event-identity-and-normalization-003
Source: RFC 0001 § UsageEvent
Scope: v1-mandatory

#### Scenario: Canonical-equivalent inputs have one digest
- **WHEN** equivalent admitted source values differ only in JSON field order, whitespace, RFC 3339 offset spelling for the same nanosecond instant, source location, alias, metadata selection, or sink enablement
- **THEN** the canonical byte document and SHA-256 fingerprint are identical

#### Scenario: Accounting participant changes the digest
- **WHEN** native identity, source time, model, project identity, request identity, source-consistency value, category, or amount changes
- **THEN** the canonical byte document and fingerprint differ
- **AND** a profile lacking both positive and negative byte-vector evidence cannot activate

### Requirement: [TARGET-STATE] Duplicate and Collision Semantics
SHALL treat same-identity and same-fingerprint observations as duplicates with no new fact, amount, aggregate, request count, ledger sequence, or sink work, and MUST reject and quarantine a same-identity observation with a different fingerprint without overwriting the original history.

ID: REQ-event-identity-and-normalization-004
Source: RFC 0001 § UsageEvent; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: Duplicate is accounting-neutral
- **WHEN** an existing identity is observed again with the same fingerprint
- **THEN** only the source cursor may advance and every accounting and sink-obligation count remains unchanged

#### Scenario: Collision preserves original history
- **WHEN** an existing identity is observed with changed normalized accounting values
- **THEN** the prior fact remains immutable, the conflicting fact is not committed, and the affected source degrades

### Requirement: [TARGET-STATE] First-Seen Logical Request Accounting
MUST require every accepted `UsageEvent` to have a registry-established `native_request_identity`, encode the global request key as RFC 8785 canonical UTF-8 JSON of `[collector_namespace,ledger_namespace,adapter_schema_id,source_namespace,native_request_identity]`, record its first-seen contribution in the same transaction as the event, and increment the request aggregate exactly once across all facts and replays sharing that key.

ID: REQ-event-identity-and-normalization-005
Source: RFC 0001 § UsageEvent
Scope: v1-mandatory

#### Scenario: First fact creates one request contribution
- **WHEN** the first accepted event for a canonical request key commits
- **THEN** exactly one logical-request row and one request aggregate contribution commit at that event's sequence

#### Scenario: Request identity cannot be guessed
- **WHEN** the adapter cannot establish native request identity from registry-admitted structural fields
- **THEN** it quarantines the stream and does not undercount, fabricate, or derive a request from path, offset, content, or collection order

### Requirement: [TARGET-STATE] Source-Faithful Time and Attribution
SHALL preserve the source-observed meaning of event time and source-derived tool, vendor, model, and working-directory attribution; unknown model or project MUST remain null. The normalized `project` value MUST be exactly the final component of the registry-admitted cwd under the source profile's frozen `posix|windows` lexical path flavor, or null for a filesystem root or unavailable, invalid, or unparseable cwd; it MUST NOT claim repository identity, discover a repository root, select an ancestor, access the filesystem, or retain the absolute path, and no context may cross a source-stream boundary. Zero-or-more configuration mappings MAY assign different presentation aliases to distinct `(source,working-directory-basename)` pairs, but aliases MUST remain outside `UsageEvent`, fact/request identity, fingerprint, and aggregate bucket keys and enter only the affected sink policy and presentation.

ID: REQ-event-identity-and-normalization-006
Source: RFC 0001 § UsageEvent; about/heart-and-soul/vision.md § Non-Negotiable Principles → 5. Normalization Preserves Meaning
Scope: v1-mandatory

#### Scenario: Structural attribution is preserved
- **WHEN** admitted fixed-clock POSIX and Windows fixtures supply source time, model, and cwd values for a filesystem root, repository root, nested directory, non-repository directory, and invalid/unavailable path
- **THEN** the event preserves the exact nanosecond source time and model and maps project to null or the exact cwd final component, including the nested/non-repository basename rather than a repository ancestor, independently of collection time
- **AND** any configured alias is applied only by presentation or a digest-bound sink policy and never enters the event

#### Scenario: Unknown attribution stays unknown
- **WHEN** model or project cannot be established from registered same-stream structural context
- **THEN** the field remains null instead of being inferred from content, absolute path, a neighboring stream, or a sink default

#### Scenario: Project alias changes presentation only
- **WHEN** two source working-directory basenames have distinct configured aliases or one alias changes
- **THEN** retained events, fingerprints, request identity, and null-tagged aggregates remain unchanged while only the affected sink policy/presentation changes

### Requirement: [TARGET-STATE] Immutable V1 Token Registry
MUST define the v1 category registry as exactly `input_unclassified` for an undecomposed inclusive input total, `input_uncached` for input identified as neither cache read nor write, `input_cache_read` for input served from an existing cache, `input_cache_write` for input written to a cache, `output_unclassified` for an undecomposed inclusive output total, `output_non_reasoning` for explicitly non-reasoning output, and `output_reasoning` for separately identified reasoning output, with no silent reassignment or broadening.

ID: REQ-event-identity-and-normalization-007
Source: RFC 0001 § Token Category Registry
Scope: v1-mandatory

#### Scenario: Registered category remains interpretable
- **WHEN** an accepted profile emits one of the seven category names
- **THEN** its amount has exactly the declared meaning across ledger, query, OTLP, and PostgreSQL surfaces

#### Scenario: Unknown or redefined category is held
- **WHEN** an adapter emits an unregistered category or reuses an existing name for a different meaning
- **THEN** the record is held and the category is not persisted or exported

### Requirement: [TARGET-STATE] Non-Overlapping Category Arithmetic
MUST keep categories within an event non-overlapping, prohibit an inclusive total from coexisting with any contained detail, and permit subtraction or direct mapping only when accepted profile evidence covers subset, zero, malformed, overflow, and non-negative cases; otherwise normalization emits only the applicable unclassified total when its meaning is known or holds the record when it is not.

ID: REQ-event-identity-and-normalization-008
Source: RFC 0001 § Token Category Registry; § Source-Specific V1 Attribution → Codex rollouts
Scope: v1-mandatory

#### Scenario: Proven inclusive total is decomposed
- **WHEN** an active profile proves that cache or reasoning detail is a subset of an inclusive total and checked subtraction is non-negative
- **THEN** normalization emits the non-overlapping detail and remainder categories whose sum equals the source total

#### Scenario: Ambiguous overlap is never double counted
- **WHEN** an inclusive input or output total and overlapping detail cannot be safely decomposed
- **THEN** the adapter emits only the applicable unclassified total or holds the record
- **AND** it never emits both the inclusive total and overlapping values

### Requirement: [TARGET-STATE] Closed Ledger Metadata Registry
MUST define the initial v1 ledger metadata registry as the empty JSON object `{}`, require any future key to use an explicit schema amendment that only extends interpretation, prohibit amounts, identity, content, credentials, or source-specific escape fields in metadata, and leave already accepted facts and fingerprints unchanged when export configuration changes.

ID: REQ-event-identity-and-normalization-009
Source: RFC 0001 § UsageEvent; § Privacy and Cardinality Budget
Scope: v1-mandatory

#### Scenario: Empty metadata is admitted
- **WHEN** an accepted event has its required normalized fields and no extension metadata
- **THEN** the ledger stores the canonical empty metadata object without changing identity or accounting

#### Scenario: Unregistered metadata is denied
- **WHEN** configuration selects a metadata key or a proposed key contains accounting, identity, content, credentials, or source-specific raw structure
- **THEN** the key is denied and the admitted fact and fingerprint remain unchanged
