## ADDED Requirements

### Requirement: [TARGET-STATE] Source-Stream Isolation Unit
MUST make one independently ordered source stream the indivisible cursor, parser-context, quarantine, freshness, reconciliation, coverage, and health unit, keep canonical discovery order out of fact identity, and prevent one stream failure from quarantining sibling streams or source families.

ID: REQ-stream-reconciliation-and-health-001
Source: RFC 0001 § Incremental Reads, Rescans, and Quarantine
Scope: v1-mandatory

#### Scenario: Independent streams progress
- **WHEN** all configured Claude and Codex streams contain complete supported records
- **THEN** each stream advances its own cursor and health independently while committed facts converge by stable identity

#### Scenario: One malformed stream is contained
- **WHEN** one Codex rollout stream encounters malformed data
- **THEN** only that stream is quarantined while healthy Claude and Codex streams and committed sink work continue

### Requirement: [TARGET-STATE] Exact Durable Cursor Tuple
MUST persist each source cursor as exactly `(stream_generation,next_byte_offset,prefix_anchor,parser_context)`, where `stream_generation` canonically combines adapter schema ID, native stream identity, and platform generation evidence; `next_byte_offset` is the unsigned start of the next record; `prefix_anchor` contains `algorithm="sha256"`, `schema_id`, profile-fixed `window_count`, `window_start_offset`, and the digest of RFC 8785 canonical arrays of registered kind ID, record-end offset, optional native identity and accounting fingerprint, and normalized context change; and `parser_context` is `{}` for Claude and for a newly created Codex byte-zero cursor before context, otherwise exact Codex session ID plus latest preceding turn timestamp, model, canonical project basename, and safe anchor, with no raw or content bytes.

ID: REQ-stream-reconciliation-and-health-002
Source: RFC 0001 § Incremental Reads, Rescans, and Quarantine
Scope: v1-mandatory

#### Scenario: Complete cursor resumes deterministically
- **WHEN** a stream transaction commits through a complete record
- **THEN** all four cursor members and the anchor window start are durably queryable as one versioned state

#### Scenario: Partial or content-bearing cursor is invalid
- **WHEN** cursor persistence omits context, stores members separately, or uses raw record or content bytes in its anchor
- **THEN** optimized resume is rejected and the cursor artifact fails privacy and validity checks

### Requirement: [TARGET-STATE] Validated Resume or Byte-Zero Rescan
SHALL permit optimized resume only when canonical mount and path checks pass, generation matches, file length reaches the offset, the stored anchor window reprojects to the same digest, and reconstructed context equals the stored context; any mismatch MUST atomically discard remembered context and reset only that stream to byte zero, relying on fact identity and fingerprint deduplication.

ID: REQ-stream-reconciliation-and-health-003
Source: RFC 0001 § Incremental Reads, Rescans, and Quarantine
Scope: v1-mandatory

#### Scenario: Validated resume continues at next record
- **WHEN** every generation, length, anchor, context, and path check matches durable state
- **THEN** scanning resumes exactly at `next_byte_offset` with the persisted parser context

#### Scenario: Replacement forces safe rescan
- **WHEN** a path is reused after replacement, the file is shorter, the anchor differs, or reconstructed context disagrees
- **THEN** the stream discards remembered context and rescans from byte zero
- **AND** already committed facts are deduplicated without duplicate accounting

#### Scenario: Safe invalidation has an exact recovery outcome
- **WHEN** generation or anchor mismatch does not prove loss across an unconsumed cursor
- **THEN** the stored cursor resets to byte zero with empty context, state remains `healthy` with null failure code during bounded rescan, and no fact is retracted
- **AND** proven unconsumed loss instead follows the `retention_gap` transition

### Requirement: [TARGET-STATE] Complete-Record and Tail Boundary
MUST consume only delimiter-terminated complete JSONL records; an incomplete tail at or below the inclusive raw-byte cap MUST store `state=trailing_deferred,failure_code=incomplete_tail` at the fragment start with no fact, component-state, parser-context, or cursor advance and degrade enabled family/global health until a later poll completes and atomically consumes the record; one byte beyond the cap MUST store `state=quarantined,failure_code=record_limit` at the record start with the same zero-effect boundary, and recover only when corrected input or a newly accepted covering parser profile makes the identical record admissible.

ID: REQ-stream-reconciliation-and-health-004
Source: RFC 0001 § Incremental Reads, Rescans, and Quarantine; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: Partial tail is retried
- **WHEN** a final record is incomplete and its bytes remain at or below the active cap
- **THEN** the stream reports `trailing_deferred`, leaves the cursor before the fragment, and retries it on a later poll

#### Scenario: Unterminated oversize tail holds
- **WHEN** that fragment reaches one byte past the raw-record cap without a delimiter
- **THEN** the stream reports `record_limit`, quarantines at the record start, and does not buffer indefinitely

### Requirement: [TARGET-STATE] No-Skip Record State Machine
MUST allow only `registered_irrelevant` to advance a cursor with an empty fact set; `unknown_kind`, `recognized_malformed`, `schema_inconsistent`, `unregistered_category`, and `identity_collision` MUST each store `state=quarantined` with the identically named `failure_code`, failure offset at the record start, prior cursor/context unchanged, no candidate fact or quota-component transition committed, and enabled family/global health degraded. `unknown_kind`, `schema_inconsistent`, and `unregistered_category` recover only through a newly accepted supporting parser/profile or corrected source; `recognized_malformed` and `identity_collision` recover only when corrected source makes the held identity valid or an RFC-compatible schema/profile migration explicitly resolves it; successful retry atomically consumes the identical held record before later progress and clears the current diagnostic. No force-skip, ignore override, dead-letter copy, or consumption waiver exists.

ID: REQ-stream-reconciliation-and-health-005
Source: RFC 0001 § Incremental Reads, Rescans, and Quarantine
Scope: v1-mandatory

#### Scenario: Registered irrelevant record advances atomically
- **WHEN** a complete record matches one exact profile-listed irrelevant discriminator
- **THEN** one cursor-only ledger transaction advances through it with no fact, aggregate, sequence, or sink obligation

#### Scenario: Unknown record cannot be waived
- **WHEN** an operator attempts to force-skip an unknown or recognized malformed record
- **THEN** the record remains unconsumed, the stream remains quarantined, and no raw dead-letter copy is created

#### Scenario: Unregistered category has its own closed code
- **WHEN** normalization produces a category outside the seven-name registry
- **THEN** the stream stores `quarantined/unregistered_category`, commits no record-set or cursor effect, and remains degraded until a reviewed profile/schema change or corrected source admits the identical record

### Requirement: [TARGET-STATE] Bounded Sanitized Quarantine Diagnostics
MUST restrict quarantine diagnostics to technical source ID, adapter schema ID, stream generation, numeric offset, code-owned failure code, expected registry path ID and type, capped observed size or depth, first-seen time, last-seen time, and repeat count; maintain one current row per held source; rate-limit transition reminders by an exact active-profile interval in seconds; and recover only after a supported parser or profile change or corrected source makes the held record valid.

ID: REQ-stream-reconciliation-and-health-006
Source: RFC 0001 § Incremental Reads, Rescans, and Quarantine
Scope: v1-mandatory

#### Scenario: Repeated hold remains bounded
- **WHEN** the same unrepaired record is encountered across repeated polls
- **THEN** one diagnostic row increments its repeat count and reminders do not exceed the profile interval

#### Scenario: Unsafe exception content is removed
- **WHEN** a parser exception includes raw text, a path, an unknown discriminator string, or source bytes
- **THEN** diagnostics emit only the sanitized failure code, registry path ID, capped measure, and numeric position
- **AND** recovery remains blocked until a supported change or corrected source is observed

### Requirement: [TARGET-STATE] Durable Full-Reconciliation Deadline
MUST complete a byte-zero reconciliation for every non-exempt stream after an adapter-schema or compatible profile change and by the active profile's inclusive `max_reconciliation_interval_seconds`, measured from the last successfully committed complete rescan using a profile-declared durable monotonic-elapsed evidence method; restart, wall-clock rollback, failed scan, or incremental success MUST NOT postpone it; and the first scheduler tick afterward MUST store `state=reconciliation_overdue,failure_code=reconciliation_overdue` without moving the cursor or changing facts, degrade stream/family/global health while bounded incremental ingestion may continue, and recover to the applicable coverage state only after one complete byte-zero rescan commits.

ID: REQ-stream-reconciliation-and-health-007
Source: RFC 0001 § Incremental Reads, Rescans, and Quarantine
Scope: v1-mandatory

#### Scenario: Complete rescan resets the deadline
- **WHEN** a full supported-stream scan commits successfully within the exact interval
- **THEN** its completion evidence becomes the sole new deadline origin and health records reconciliation current

#### Scenario: Restart cannot hide overdue state
- **WHEN** the deadline passes during restart, backward wall-clock movement, interrupted scan, or repeated incremental success
- **THEN** health becomes `reconciliation_overdue` and cannot claim current reconciliation

### Requirement: [TARGET-STATE] Exact Reconciliation-Profile Schema
MUST require every active source profile to provide inclusive unsigned `max_stream_count`, `max_aggregate_source_bytes`, `max_record_bytes`, `max_sustained_append_bytes_per_second`, `max_full_scan_structural_steps`, `anchor_window_record_count`, `max_reconciliation_interval_seconds`, and `diagnostic_reminder_interval_seconds`, plus the durable elapsed method, source-specific exemption flag and proof digest, minimum resource assumptions, native architecture measurements, and executable boundary evidence; exactly `N` is covered, while any envelope `N+1` or checked overflow MUST store `state=source_envelope_exceeded,failure_code=source_envelope_exceeded` without changing facts or cursor, degrade stream/family/global health while independently bounded incremental ingestion may continue, and recover only after the source returns within the same measured profile or a newly accepted profile covers it; missing timing or an unproved exemption instead follows exact `reconciliation_overdue` semantics without a default.

ID: REQ-stream-reconciliation-and-health-008
Source: RFC 0001 § Incremental Reads, Rescans, and Quarantine
Scope: v1-mandatory

#### Scenario: Supported envelope reconciles
- **WHEN** every source dimension is at or below its immutable measured ceiling and the full scan completes by its deadline on both native architectures
- **THEN** the profile may claim reconciliation coverage for that envelope

#### Scenario: One-past envelope degrades explicitly
- **WHEN** any envelope dimension reaches one beyond its limit, arithmetic overflows, required timing is missing, or an append-only exemption lacks its mutation corpus
- **THEN** affected stream, family, and global health degrades without substituting a default
- **AND** bounded incremental ingestion may continue only where parser and ledger contracts still permit it

### Requirement: [TARGET-STATE] Coverage and Retention-Gap Semantics
MUST register an enabled supported source component at `component_registrations.runtime_state=coverage_unknown,state_code=coverage_unknown` before first positive discovery with no invented stream/cursor/fact, recover that state only after discovery and one complete reconciliation establishes current coverage, report `state=retention_gap,failure_code=retention_gap` only when disappearance, truncation, or equivalent durable evidence crosses a previously discovered unconsumed cursor, retain every previously accepted fact and aggregate, and never fabricate exact historical coverage. A proven retention gap has no in-place healthy recovery for that ledger epoch: restored source may resume from the held boundary only where safe, but the gap and degraded upward health remain durable; a new technical namespace/epoch begins separately at `coverage_unknown` and does not erase the old gap.

ID: REQ-stream-reconciliation-and-health-009
Source: RFC 0001 § Motivation; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: Undiscovered history remains unknown
- **WHEN** a configured source has not yet been discovered or observable
- **THEN** its component remains `runtime_state=coverage_unknown,state_code=coverage_unknown` without a stream and without claiming loss or completeness

#### Scenario: First discovered stream starts in one exact cursor transaction
- **WHEN** canonical discovery first identifies a supported regular source stream
- **THEN** one transaction creates its `source_streams` row with the profile-derived `stream_generation`, `next_byte_offset=0`, the REQ-stream-reconciliation-and-health-002 prefix-anchor object at `window_start_offset=0` with the SHA-256 digest of RFC 8785 canonical `[]`, `parser_context_json='{}'`, `state=coverage_unknown`, `coverage_state=coverage_unknown`, `failure_code=coverage_unknown`, null failure offset and observation/reconciliation times, and no fact, aggregate, sequence, quota transition, or sink obligation
- **AND** the source component remains `runtime_state=coverage_unknown,state_code=coverage_unknown` until a complete reconciliation commits the cursor and atomically changes stream and component coverage to `healthy` with null failure/state code and `coverage_state=current`

#### Scenario: Proven unconsumed loss records a gap
- **WHEN** a discovered source disappears or truncates across its durable unconsumed cursor
- **THEN** health records `retention_gap` and existing facts and aggregates are not retracted

### Requirement: [TARGET-STATE] Non-Masking Stream and Family Health
MUST expose one source-component row before stream existence and one row for every stream with its technical identity, enumerated current and recovery state, last successful scan, last accepted source time, complete durable cursor, held failure code and position, reconciliation last-completed and due evidence, and coverage or retention state; family and global summaries MUST remain degraded whenever any enabled member is `unsupported_profile`, `unsupported_accounting_profile`, `trailing_deferred`, `quarantined`, `storage_hold`, `reconciliation_overdue`, `source_envelope_exceeded`, `retention_gap`, or `coverage_unknown`. Disabled source components MUST store `configured_state=disabled,runtime_state=disabled` with no stream/cursor/fact; enabling them re-enters source-profile activation and then `coverage_unknown`. Ledger storage interruption owns `storage_hold/ledger_storage_hold` and identical-input recovery; this capability only reflects it on every affected stream. Duplicate observations store `healthy` with null failure code after their atomic cursor/count commit. Quota capability states and sink retry/blocked states are owned by their respective capabilities and only composed upward by local query.

ID: REQ-stream-reconciliation-and-health-010
Source: RFC 0001 § Health and Freshness State; about/heart-and-soul/vision.md § Non-Negotiable Principles → 4. Partial Failure Is Explicit
Scope: v1-mandatory

#### Scenario: Fully healthy family reports healthy
- **WHEN** every enabled stream is scanned, current, within envelope, unheld, and free of coverage or retention gaps
- **THEN** stream and family summaries may report `healthy`

#### Scenario: Successful majority cannot mask failure
- **WHEN** one enabled stream is quarantined while others succeed
- **THEN** family and global health remains degraded with that boundary identifiable
- **AND** safe progress elsewhere continues only as its own state permits

#### Scenario: Ledger hold and recovery remain globally coordinated
- **WHEN** durable-ledger admission stores all source streams as `storage_hold/ledger_storage_hold`
- **THEN** source health shows no cursor or fact effect and remains degraded until ledger-owned verification retries the identical input and clears the hold

#### Scenario: Disabled source has no runtime artifacts
- **WHEN** a configured source is disabled
- **THEN** only its source component row reports `disabled`; no mount traversal, source stream, cursor, parser, fact, or diagnostic row is created
