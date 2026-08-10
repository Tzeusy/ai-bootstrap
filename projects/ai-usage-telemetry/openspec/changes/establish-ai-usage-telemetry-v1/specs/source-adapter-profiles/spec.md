## ADDED Requirements

### Requirement: [TARGET-STATE] Fail-Closed Source Profile Activation
MUST initialize every enabled Claude or Codex source component as `runtime_state=unsupported_profile,state_code=unsupported_profile`, request no `ValidatedSourceHandle`, create no stream cursor, and accept no fact until one immutable release-profile member covers the exact source-build family, extraction manifest, native and logical identity evidence, arithmetic strategy evidence, replay and mutation behavior, finite irrelevant-kind table, every required parser bound, and positive and negative error vectors; any missing member or bound MUST remain `unsupported_profile` before traversal, recovery MUST require an accepted matching complete profile and transition the component to `runtime_state=coverage_unknown,state_code=coverage_unknown` before requesting runtime validation and generic discovery, and enabled unsupported state MUST degrade family/global health while disabled sources remain excluded. The adapter capability owns no mount validation, discovery traversal, domain identity/fingerprint/time/path/age implementation, or storage-admission implementation.

ID: REQ-source-adapter-profiles-001
Source: RFC 0001 § Evidence Baseline; § Configuration Contract
Scope: v1-mandatory

#### Scenario: Covered source activates
- **WHEN** the selected source build, adapter schema, manifest digest, rules, limits, and vectors exactly match one accepted release-profile member
- **THEN** startup may request that source's runtime-owned `ValidatedSourceHandle` and classify generic-discovery results under that member

#### Scenario: Uncovered build fails before traversal
- **WHEN** the configured source build, selected source member, or any required member bound is absent from the active profile
- **THEN** startup or that source remains `unsupported_profile` before mount traversal
- **AND** no fact is accepted and no similar-looking rule is substituted

#### Scenario: Supported profile recovery begins without a cursor
- **WHEN** a later accepted profile exactly covers an enabled unsupported source
- **THEN** the source component transitions atomically to `runtime_state=coverage_unknown,state_code=coverage_unknown` before discovery and still has no invented stream, cursor, or accepted fact

### Requirement: [TARGET-STATE] Streaming Deny-by-Default Manifest
MUST use a streaming syntax traverser with a compile-time manifest whose exact schema is `schema_id`, `build_families[]`, `discriminators[{path,type,admitted_value,disposition}]`, `projected_paths[{record_kind,path,type,requiredness,multiplicity,role}]`, `content_paths[]`, `irrelevant_kinds[{discriminator_path,value}]`, and `limits_ref`; every list is closed and digest-covered, every unlisted path is skip-only, every unlisted discriminator holds, and neither runtime configuration nor a general-purpose mixed-content deserializer may add or decode a value.

ID: REQ-source-adapter-profiles-002
Source: RFC 0001 § Mixed-Content Streaming Field Projection
Scope: v1-mandatory

#### Scenario: Registered projection decodes only admitted scalars
- **WHEN** a complete record matches one exact discriminator and all required projected paths have their declared types and multiplicities
- **THEN** only projected scalar values are decoded into application values
- **AND** syntax traversal skips all content and unregistered descendants directly from bounded input chunks

#### Scenario: Runtime cannot widen the manifest
- **WHEN** member/chunk permutations contain an unlisted descendant, an unregistered discriminator, or configuration that attempts to add a path, kind, or type
- **THEN** the descendant is always skipped without decoding, configuration widening is rejected, and only the unregistered discriminator holds the stream as `unknown_kind`
- **AND** no member or chunk order can turn a descendant into a kind or a kind into `registered_irrelevant`

### Requirement: [TARGET-STATE] Exact Parser-Limit Profile Schema
MUST require every active adapter member to provide unsigned inclusive `max_record_bytes` measured from record start excluding the delimiter, `max_depth` with the root at one, `max_keys_per_record`, `max_encoded_key_bytes`, `max_projected_occurrences`, `max_application_memory_bytes`, and `max_structural_steps`, plus for every projected path inclusive `max_encoded_bytes`, `max_decoded_utf8_bytes`, `max_multiplicity`, integer `min_value` and `max_value` or decimal `min_value`, `max_value`, `max_precision`, and `max_scale`; all values, the minimum supported memory in bytes, counting algorithms, measurement evidence digests, and architecture results are immutable profile inputs. Before traversal the exact phase order MUST be complete profile validation, receipt of an injected runtime-owned `ValidatedSourceHandle`, and receipt of an injected ledger/storage-owned `AdmissionDecision=permitted`. Parser and adapter modules MUST consume those interfaces, remain testable with fake handles and fake permitted/denied decisions, and MUST NOT implement or import concrete runtime/storage preflight. After traversal begins, compound failures MUST use the JSON-member-order and chunk-order independent precedence `record_limit` for any measured/checked overflow, `schema_inconsistent` for invalid UTF-8 or JSON structure, `unknown_kind` for a valid unregistered discriminator, `recognized_malformed` for a registered kind's missing/wrong projected value or multiplicity, then `unregistered_category`; only parser success may reach later `identity_collision`. A missing required profile member, handle, permitted decision, bound, counting rule, or evidence result MUST keep or hold the source before traversal. Every exact `N` is admitted and no library or operator default is substituted.

ID: REQ-source-adapter-profiles-003
Source: RFC 0001 § Mixed-Content Streaming Field Projection
Scope: v1-mandatory

#### Scenario: Exact boundary is admitted
- **WHEN** a record and its projected values equal every applicable active-profile ceiling without exceeding the combined memory and work bounds
- **THEN** limit validation permits semantic classification
- **AND** measured memory remains within the profile's minimum-resource claim

#### Scenario: One-past unterminated record fails immediately
- **WHEN** a record crosses its raw-byte cap without a JSONL delimiter, any other measured bound reaches `N+1`, or a checked record counter exceeds its representable profiled bound
- **THEN** the stream fails closed as `record_limit` at the offending record
- **AND** its cursor remains before that record without falling back to library or operator defaults

#### Scenario: Missing profile bound blocks before traversal
- **WHEN** an enabled source's selected profile member omits any required bound, counting rule, measurement digest, architecture result, or minimum-resource claim, or an injected handle/decision is absent or denied
- **THEN** the source remains `unsupported_profile` and no source byte is traversed

#### Scenario: Missing projected record value is malformed
- **WHEN** permutations of one complete record combine invalid UTF-8/structure, an exceeded limit, an unregistered discriminator, missing/wrong projected values, an unregistered category, and a would-be identity collision
- **THEN** every permutation selects the exact precedence winner, holds before the record, and never reaches collision unless all parser phases succeed

### Requirement: [TARGET-STATE] Profile Fixture and Privacy Corpus
SHALL require each supported profile member to include version-pinned zero or minimum, exactly-at, one-past, combined-memory-bound, incomplete-tail, oversized-irrelevant, malformed, replay, mutation, escaped and nested sentinel, and error-path fixtures with canonical expected classifications and content-free outputs on native amd64 and arm64.
Every application-value, permitted-decoder instrumentation, log, exception,
crash-output, SQLite, OTLP, PostgreSQL, image-layer/filesystem, environment, and
packet/network capture MUST observe its own harmless content-free positive-
control canary, and separate deliberate test-only sentinel-leak, forbidden-
decoder/materializer/fingerprint, and unexpected-network mutations MUST fail
the harness without using actual sensitive data.

ID: REQ-source-adapter-profiles-004
Source: RFC 0001 § Mixed-Content Streaming Field Projection; § Integration
Scope: v1-mandatory

#### Scenario: Complete native corpus passes
- **WHEN** every named fixture and independent boundary vector produces the declared fact, cursor, health, and privacy outcome on both target architectures
- **THEN** that evidence component is eligible for domain acceptance

#### Scenario: Missing vector or leaked sentinel blocks activation
- **WHEN** any sentinel byte or digest is observed on a forbidden surface or a ceiling lacks a boundary vector on either native architecture
- **THEN** the profile member is not activatable and release fails

### Requirement: [TARGET-STATE] Exact Claude Extraction Manifest
MUST define `claude-code/session-jsonl@1` with canonical target `/sources/claude/sessions` and adapter-owned filename predicate `*.jsonl`; generic stream discovery alone owns regular-file, non-symlink, stay-beneath traversal and generation. The adapter MUST classify `/type="assistant"` as usage-bearing; project bounded strings at `/type`, `/sessionId`, `/requestId`, `/timestamp`, `/cwd`, `/message/id`, and `/message/model`; project non-negative integers at `/message/usage/input_tokens`, `/message/usage/cache_creation_input_tokens`, `/message/usage/cache_read_input_tokens`, and `/message/usage/output_tokens`; classify `/message/content` as content-bearing; and require each accepted source-build member to digest-cover its complete finite non-wildcard set of non-`assistant` irrelevant `/type` values before activation.

ID: REQ-source-adapter-profiles-005
Source: RFC 0001 § Source-Specific V1 Attribution → Claude Code sessions
Scope: v1-mandatory

#### Scenario: Valid assistant record projects the exact fields
- **WHEN** generic discovery supplies an in-root regular-file result matching the Claude filename predicate and it contains a complete `assistant` record whose required paths and types match the manifest
- **THEN** the adapter projects only the listed structural and accounting fields and skips `/message/content` and every other descendant

#### Scenario: Invalid discovery or type holds safely
- **WHEN** generic discovery rejects a symlink/out-of-root file or the adapter encounters an unprofiled non-`assistant` kind or a projected value with the wrong type
- **THEN** it opens nothing outside the root and holds the affected stream before the record
- **AND** a wrong projected type is `recognized_malformed`, an unprofiled kind remains unregistered, and no wildcard irrelevant-kind rule is applied

### Requirement: [TARGET-STATE] Claude Identity, Attribution, and Arithmetic
MUST supply Claude native/logical request identity evidence `(sessionId,requestId)` and mandatory `message.id` consistency evidence to the source-independent domain interfaces; map source amount fields to the exact registered categories; preserve absent optional amounts as absent; and invoke the domain-owned canonical instant, cwd-basename, identity, request, category, and fingerprint functions rather than reimplementing them. The adapter MUST use the record's own timestamp/model/cwd fields, never perform repository discovery or ancestor selection, keep every project alias outside the normalized event, fact/request identity, accounting fingerprint, and aggregate keys, expose aliases only through presentation and digest-bound sink policy, and quarantine same-identity changes in time, message identity, model, or amount.

ID: REQ-source-adapter-profiles-006
Source: RFC 0001 § Source-Specific V1 Attribution → Claude Code sessions
Scope: v1-mandatory

#### Scenario: Claude record normalizes faithfully
- **WHEN** qualified assistant fixtures use a filesystem root, a repository root, a nested directory inside it, a non-repository directory, an unavailable/invalid cwd, and both profile-supported POSIX and Windows lexical path forms
- **THEN** it yields the exact non-overlapping category mapping and one source-backed logical request identity
- **AND** project is respectively null or the exact cwd final component, including the nested/non-repository basename rather than a repository ancestor; no configured alias or neighboring record supplies event context, and aliases remain presentation/sink-policy only

#### Scenario: Missing or mutated identity quarantines
- **WHEN** `requestId` is missing or an identical identity arrives with a different timestamp, message ID, model, or amount
- **THEN** no replacement fact is accepted and the Claude stream is quarantined

### Requirement: [TARGET-STATE] Claude Quota Source Prohibition
MUST define Claude quota as `unavailable`, mount or parse no Claude quota, cache, global-state, or authentication source, and keep Claude usage ingestion independently healthy when quota is requested, absent, or unavailable.

ID: REQ-source-adapter-profiles-007
Source: RFC 0001 § Source-Specific V1 Attribution → Claude Code quota capability
Scope: v1-mandatory

#### Scenario: Quota unavailability is explicit
- **WHEN** Claude usage is enabled under an accepted profile
- **THEN** capability inspection reports Claude usage supported and Claude quota `unavailable`
- **AND** no zero quota snapshot is fabricated

#### Scenario: Candidate global state is never opened
- **WHEN** an operator requests Claude quota or supplies a cache, auth, or global-state path
- **THEN** quota remains `unavailable`, the candidate path is not opened, and Claude usage collection continues independently

### Requirement: [TARGET-STATE] Exact Codex Extraction Manifest
MUST define `codex/rollout-jsonl@1` with canonical target `/sources/codex/sessions` and adapter-owned filename predicate `rollout-*.jsonl`; generic stream discovery alone owns regular-file, non-symlink, stay-beneath traversal and generation. The adapter MUST admit exact top-level discriminator values `session_meta`, `turn_context`, and `event_msg`; classify only `/type="event_msg"` plus `/payload/type="token_count"` as fact-bearing; project strings at `/timestamp`, `/type`, `/payload/type`, `/payload/id` for `session_meta`, and `/payload/model` and `/payload/cwd` for `turn_context`; project non-negative integers named `input_tokens`, `cached_input_tokens`, `cache_write_input_tokens`, `output_tokens`, `reasoning_output_tokens`, and `total_tokens` beneath both `/payload/info/total_token_usage` and `/payload/info/last_token_usage`; register `/payload/rate_limits` itself as an optional `object|null` presence path, project its `/limit_id` as a bounded string and each registered `primary` or `secondary` window's `used_percent` as an exact decimal in `0..100` and optional `window_minutes` and `resets_at` as non-negative integers; classify missing member, explicit null, admitted object without a complete registered window, and at least one complete window as the quota outcomes `absent`, `null`, `state_only`, and `observed`; and require each source-build member to digest-cover its complete finite non-wildcard irrelevant envelope and payload-value table before activation.

ID: REQ-source-adapter-profiles-008
Source: RFC 0001 § Source-Specific V1 Attribution → Codex rollouts
Scope: v1-mandatory

#### Scenario: Token-count record projects usage and quota independently
- **WHEN** a complete token-count record matches the exact envelope, context, usage, and rate-limit types of an accepted build member
- **THEN** only the listed values are projected and usage and each present primary or secondary quota window are classified independently

#### Scenario: Unknown advancing kind holds
- **WHEN** a rollout contains an unprofiled envelope discriminator, an unprofiled `event_msg` payload kind, and arbitrary unlisted quota descendants in permuted member/chunk order
- **THEN** the unregistered discriminator or payload kind is not consumed and holds as `unknown_kind`, while unlisted descendants remain skip-only without decoding and cannot independently hold the record

#### Scenario: Quota presence classes are structural
- **WHEN** otherwise-equal supported records omit `rate_limits`, set it to JSON null, provide only its admitted identity/context, or provide a complete primary window
- **THEN** their quota candidate outcomes are respectively `absent`, `null`, `state_only`, and `observed` without treating any as zero

### Requirement: [TARGET-STATE] Same-Stream Codex Context
MUST interpret Codex usage using only the latest preceding `turn_context` from the same source stream, never look ahead or cross streams, begin every byte-zero scan with empty session and turn context, and hold the stream when required session, timestamp, model, or project context is missing.

ID: REQ-source-adapter-profiles-009
Source: RFC 0001 § Source-Specific V1 Attribution → Codex rollouts
Scope: v1-mandatory

#### Scenario: Latest preceding context applies
- **WHEN** a token-count record follows two valid turn contexts in the same stream
- **THEN** only the later preceding context supplies source time, model, and project attribution

#### Scenario: Missing local context quarantines
- **WHEN** a token-count record precedes valid same-stream context or only another stream has context
- **THEN** the adapter accepts no usage fact and quarantines the affected stream

### Requirement: [TARGET-STATE] Evidence-Gated Codex Accounting
MUST require an accepted build member to declare and vector-prove the componentwise-monotonic cumulative landmark, reset disposition, relation to `last_token_usage`, cache-write presence, one of exactly `exclusive_direct`, `inclusive_subtract`, or `unclassified_total` for each input-cache and output-reasoning axis, source evidence for exact non-negative delta calculation, and the mapping of one advancing landmark to one logical request. The adapter MUST select the proved strategy and invoke the domain-owned checked category/identity functions; it MUST NOT implement a parallel arithmetic, identity, fingerprint, canonical-instant, cwd, or age primitive. An unresolved relationship MUST keep the enabled Codex source component at `runtime_state=unsupported_accounting_profile,state_code=unsupported_accounting_profile` before fact acceptance or cursor creation, degrade upward health, and recover only through an accepted accounting member into `coverage_unknown`; decreases, impossible subtraction, or declared-relation mismatches after activation are recognized malformed stream records.

ID: REQ-source-adapter-profiles-010
Source: RFC 0001 § Source-Specific V1 Attribution → Codex rollouts
Scope: v1-mandatory

#### Scenario: Proven cumulative advancement emits one request
- **WHEN** every cumulative component advances according to an accepted rule and the computed delta agrees with the declared last-usage relation
- **THEN** the adapter emits the exact non-overlapping delta and one logical-request contribution
- **AND** an unchanged landmark emits no usage fact even when quota facts are present

#### Scenario: Unresolved or decreasing counters fail closed
- **WHEN** cache inclusion or reasoning inclusion is unresolved, a cumulative vector decreases, subtraction would be negative, or delta and cumulative values disagree
- **THEN** no usage fact is accepted and the stream reports `unsupported_accounting_profile` or the applicable malformed hold

### Requirement: [TARGET-STATE] Closed Record Outcome Set
MUST classify each complete or partial input as exactly one pre-ledger record disposition with a deterministic ordered candidate-fact set produced by invoking the source-independent domain interfaces, zero-or-one quota component-state transition, and one parser-context transition: `incomplete_tail`, `context_only`, `registered_irrelevant`, `quota_state_only`, `candidate_set`, `unknown_kind`, `recognized_malformed`, `schema_inconsistent`, `unregistered_category`, or `record_limit`; only `context_only`, `registered_irrelevant`, and `quota_state_only` are complete zero-fact advancing dispositions, each MUST be explicitly code/profile-registered and commit its permitted parser-context or quota-component transition atomically with the cursor in the later ledger transaction, and `candidate_set` MUST contain one or more domain values. Order a Claude candidate set as its single usage event and a Codex token-count candidate set as usage first when present followed by `primary` then `secondary` quota windows when present; accept the ledger's later `duplicate_only`, `mixed_new_and_duplicate`, or `identity_collision` record-set outcome without reordering; unknown, unregistered, malformed, collided, or failed records MUST hold before the record; leave exact stored stream state, failure code, cursor/fact effect, recovery, and upward-health propagation to stream reconciliation; and emit no raw-record passthrough, content, credentials, or unregistered categories or metadata.

ID: REQ-source-adapter-profiles-011
Source: RFC 0001 § Adapter Contract; § Failure-State Contract
Scope: v1-mandatory

#### Scenario: One record yields a deterministic fact set
- **WHEN** a complete Codex token-count record repeats its usage landmark but contains two new registered quota windows
- **THEN** its record result contains no new usage fact, exactly two quota facts, and one atomic cursor outcome
- **AND** retry produces the same fact set and classifications

#### Scenario: Registered zero-fact dispositions advance atomically
- **WHEN** complete records classify respectively as `registered_irrelevant`, `context_only`, and `quota_state_only`
- **THEN** each advances only through one ledger transaction that also commits its permitted unchanged/context or quota-component transition
- **AND** none creates a fact, amount, sequence, aggregate, request, or sink obligation

#### Scenario: Malformed record advances nothing
- **WHEN** a complete recognized record has malformed accounting data
- **THEN** the cursor does not advance, only the affected stream is quarantined, and no raw record or exception text is copied to diagnostics
