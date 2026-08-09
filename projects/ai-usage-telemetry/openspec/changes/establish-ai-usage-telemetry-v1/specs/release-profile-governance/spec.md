## ADDED Requirements

### Requirement: [TARGET-STATE] Embedded and Persisted Release-Profile Identity
MUST embed one immutable release-profile `profile_id` and SHA-256 content digest, persist both on first ledger use, and expose both in image metadata, ledger state, versioned health JSON, and sanitized diagnostics; restart MUST require byte-equal embedded and persisted values before scanning, source mounting, sink creation, or export.

ID: REQ-release-profile-governance-001
Source: RFC 0001 § Defined Terms; § Configuration Contract
Scope: v1-mandatory

#### Scenario: First use binds the ledger
- **WHEN** a new empty ledger starts with a valid embedded profile
- **THEN** its profile ID and digest persist before any source or sink activity and appear on every declared inspection surface

#### Scenario: Missing or mismatched profile blocks startup
- **WHEN** the embedded profile is missing, its digest is invalid, or persisted state names another profile or digest
- **THEN** startup fails before scanning, source mounting, credential access, client creation, or export

### Requirement: [TARGET-STATE] Exact Release-Profile Document and Digest
MUST encode the profile as RFC 8785 canonical JSON with exact top-level keys `schema="aiut.release-profile/v1"`, `profile_id`, `source_revision`, `dependency_lock_digest`, `adapter_profiles`, `identity_and_fingerprint_profile`, `parser_profile`, `reconciliation_profile`, `storage_profile`, `quota_freshness_profile`, `ledger_schema_digest`, `query_schema_digest`, `otlp_projection_profile`, `postgresql_projection_profile`, `runtime_profile`, `synthetic_evidence_inventory`, `capability_acceptance`, and `architecture_evidence`, with no extra keys, and compute its digest as SHA-256 over `UTF-8("aiut-release-profile-v1\n")` plus those canonical bytes; every nested member MUST include its schema ID, immutable values, evidence digests, and compatibility identifiers.

ID: REQ-release-profile-governance-002
Source: RFC 0001 § Defined Terms; § Specification and Doctrine Boundary → Required before implementation or release OpenSpec
Scope: v1-mandatory

#### Scenario: Complete profile has one canonical digest
- **WHEN** all required nested domain members, schema manifests, measured values, vectors, and evidence are present
- **THEN** semantically identical JSON serializations produce the same canonical bytes and profile digest

#### Scenario: Omitted member blocks its capability and release
- **WHEN** any required domain artifact, exact accepted value, evidence digest, or compatibility identifier is absent
- **THEN** the affected capability cannot activate and release fails closed

### Requirement: [TARGET-STATE] Runtime Configuration Can Only Select or Narrow
MUST allow operator configuration only to select a profile-supported capability, choose configured aliases and technical namespaces, set polling interval where permitted, and narrow declared PostgreSQL or OTLP allowlists; configuration MUST NOT raise, replace, patch, or widen source-build membership, extraction paths, ledger admission, identity, fingerprint, arithmetic, freshness, parser, storage, reconciliation, vocabulary, or sink-budget values.

ID: REQ-release-profile-governance-003
Source: RFC 0001 § Defined Terms; § Privacy and Cardinality Budget
Scope: v1-mandatory

#### Scenario: Supported narrowing is accepted
- **WHEN** configuration disables a supported source or sink or selects a strict subset of a declared projection allowlist
- **THEN** effective behavior is the immutable profile intersected with that narrower selection

#### Scenario: Widening configuration is rejected
- **WHEN** TOML or environment attempts to increase a ceiling, add an extraction path or attribute, change arithmetic, or replace a profile member
- **THEN** startup rejects configuration rather than changing the effective profile

### Requirement: [TARGET-STATE] Complete Canonical Evidence Corpus
MUST require every source identity and accounting rule and every bounded domain to carry version-pinned structural fixtures, positive and negative canonical vectors, replay, mutation, reset, malformed, privacy, and error cases, exactly-at and one-past boundary vectors, expected canonical bytes or semantic outputs, and applicable native amd64 and arm64 release results before activation.

ID: REQ-release-profile-governance-004
Source: RFC 0001 § Configuration Contract; § Mixed-Content Streaming Field Projection; § Integration
Scope: v1-mandatory

#### Scenario: Evidence-complete member activates
- **WHEN** every required vector is pinned, digest-covered, and passes its domain oracle natively on each applicable target
- **THEN** that domain member is eligible for independent acceptance and activation

#### Scenario: Local sample or partial evidence is insufficient
- **WHEN** a rule is supported only by a local sample, lacks a negative or mutation vector, omits canonical-byte semantics, or passes only under emulation
- **THEN** the member remains unaccepted and cannot enable real collection, export, or release

### Requirement: [TARGET-STATE] Measured Numeric Activation Inputs
MUST require exact immutable values and units from the owning domain schemas for every parser count and byte ceiling, minimum memory, reconciliation deadline and envelope, storage charge, reserve and headroom, quota age and skew, diagnostic interval, OTLP UTF-8, tuple, series, SDK, and request ceiling, and any other RFC-declared numeric threshold, together with measurement method, minimum supported resources, evidence digest, and native boundary results; no numeric value in this specification is a runtime default, and missing, unmeasured, inconsistent, or unproved values keep the affected member inactive.

ID: REQ-release-profile-governance-005
Source: RFC 0001 § Mixed-Content Streaming Field Projection; § Retention, Maintenance, and Storage Pressure; § Incremental Reads, Rescans, and Quarantine; § OTLP Metrics Projection
Scope: v1-mandatory

#### Scenario: Measured values satisfy the declared resource claim
- **WHEN** every owning schema has exact accepted values and `N` and `N+1` evidence under the declared minimum resources on both native architectures
- **THEN** the profile may bind and enforce those immutable values

#### Scenario: Missing measurement never becomes a default
- **WHEN** a required bound is absent, unmeasured, internally inconsistent, overflows, or cannot be proved under the declared minimum resources
- **THEN** startup or the affected boundary fails closed without a library, operator, or specification-placeholder value

### Requirement: [TARGET-STATE] Fail-Closed Membership and Compatibility
MUST fail before source scan, source mount opening, sink instantiation, or export when the profile is missing or mismatched, selected adapter or projection membership is uncovered, exact build-family membership cannot be proved, or persisted schema and profile state is incompatible without an approved migration, and MUST never promote an inferred candidate identity or arithmetic rule ad hoc.

ID: REQ-release-profile-governance-006
Source: RFC 0001 § Configuration Contract; § Specification and Doctrine Boundary → Required before implementation or release OpenSpec
Scope: v1-mandatory

#### Scenario: Covered compatible member starts
- **WHEN** selected source, sink, ledger, and runtime members exactly match the embedded profile and persisted compatibility state
- **THEN** only those selected members may initialize

#### Scenario: Similar-looking source remains unsupported
- **WHEN** Codex arithmetic remains inferred or an unrecognized source build merely resembles a covered family
- **THEN** it remains `unsupported_accounting_profile` or `unsupported_profile` and accepts no fact

### Requirement: [TARGET-STATE] Profile Change and Migration Contract
MUST give every changed profile new ID and digest, bind a compatibility review result, declare all schema migration, full-rescan, origin-backfill, identity, fingerprint, category, stable-view, and checkpoint consequences, preserve accepted facts and meanings, and trigger every required recovery operation without double counting or silently resetting state.

ID: REQ-release-profile-governance-007
Source: RFC 0001 § Configuration Contract; § Compatibility and Evolution
Scope: v1-mandatory

#### Scenario: Compatible profile upgrade performs declared work
- **WHEN** a new accepted profile preserves existing identity semantics and declares a required rescan or sink backfill
- **THEN** startup performs or holds for that work and deduplicates retained facts without resetting stable state

#### Scenario: Undeclared incompatible change fails
- **WHEN** a new profile changes identity or fingerprint semantics without a migration or backfill plan and new schema or domain identifiers
- **THEN** restart fails closed on existing state

### Requirement: [TARGET-STATE] Per-Capability Runtime Authorization
MUST make `capability_acceptance` an exact map containing all eleven capability names, each with state `accepted`, `rejected`, or `unknown` and an immutable external decision-record digest; allow each domain's accepted state and trace to remain independent; authorize non-synthetic source mounting, fact acceptance, sink creation, production packaging, and release only when all eleven entries are `accepted` and every selected domain profile is active; and authorize only the restricted disposable synthetic harness when `synthetic-usage-spine` alone is accepted, leaving owner checklist, reviewer identity, decision procedure, and archival mechanics to the separate governance artifact referenced by each digest.

ID: REQ-release-profile-governance-008
Source: RFC 0001 § Specification and Doctrine Boundary → Required before implementation or release OpenSpec
Scope: v1-mandatory

#### Scenario: Independently accepted sibling keeps its trace
- **WHEN** one capability is `accepted` and another is `rejected` or `unknown`
- **THEN** both decisions and digests remain intact while every non-synthetic authorization path stays disabled
- **AND** no runtime invents or edits the process-level owner checklist

#### Scenario: Synthetic exception is narrow and fail closed
- **WHEN** only `synthetic-usage-spine` is accepted
- **THEN** only its disposable synthetic-only harness is authorized
- **AND** any real mount, non-synthetic fact, remote export, production package, or release attempt fails before side effects

### Requirement: [TARGET-STATE] Multi-Architecture Artifact Binding
MUST bind one release profile and OCI manifest to the same source revision, dependency-lock digest, base-image digests, adapter schema IDs, ledger and query schema digests, projection schemas, runtime profile, and synthetic vectors for native amd64 and arm64, and MUST reject publication when either artifact membership or canonical native results diverge.

ID: REQ-release-profile-governance-009
Source: RFC 0001 § Integration
Scope: v1-mandatory

#### Scenario: Matching native artifacts are eligible
- **WHEN** both native images bind identical profile inputs and pass the complete common gate with equal canonical semantic outputs
- **THEN** their immutable digests may be referenced by one v1 OCI manifest

#### Scenario: Architecture drift blocks every publication form
- **WHEN** amd64 and arm64 artifacts reference different locks or schema IDs or produce unequal normalized facts, descriptors, views, or health schemas
- **THEN** no v1 image, release tag, or manifest is published
