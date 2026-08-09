## ADDED Requirements

### Requirement: [TARGET-STATE] One Portable Polling Process
SHALL run v1 as one long-running non-root Python process in a `uv`-managed container, poll all configured sources and advance enabled sinks on a TOML-configurable positive integral number of seconds, and use exactly `300` seconds when the interval is omitted.

ID: REQ-portable-runtime-and-release-001
Source: RFC 0001 § Runtime and Trust Boundary; about/heart-and-soul/vision.md § Non-Negotiable Principles → 6. The Runtime Boundary Is Portable and Narrow
Scope: v1-mandatory

#### Scenario: Default polling loop is five minutes
- **WHEN** valid TOML omits the polling interval
- **THEN** one process polls at exactly `300`-second intervals without a host scheduler

#### Scenario: Invalid interval fails validation
- **WHEN** the configured interval is zero, negative, fractional, nonnumeric, or duplicated
- **THEN** startup fails before source or sink activity and never substitutes an undocumented default

### Requirement: [TARGET-STATE] Exact Read-Only TOML Configuration Surface
MUST read non-secret configuration only from the regular non-symlink read-only file `/etc/ai-usage-telemetry/config.toml` under this exact grammar and no implicit type coercion: required `[collector]` has required string `collector_namespace`, required string `ledger_namespace`, and optional positive integer `poll_interval_seconds` defaulting to `300`; required `[sources.claude]` has required boolean `enabled` and required string `source_namespace`; required `[sources.codex]` has those keys plus optional string `account_alias`, whose absence is null and which is presentation-only; zero-or-more `[[project_aliases]]` entries each have exactly string `source` in `claude|codex`, string `source_project`, and string `alias`, with `(source,source_project)` and `(source,alias)` each unique; required `[sinks.otlp]` and `[sinks.postgresql]` each have required boolean `enabled`, require string `sink_id`, `destination_id`, and `projection_schema_id` only when enabled, and forbid them when disabled; enabled PostgreSQL additionally requires string `schema_name`; optional `[sinks.otlp.allowlist]` has only `models`, `projects`, `accounts`, `limits`, `windows`, and `scopes`, each an array of unique strings that defaults by omitted key to the complete profile vocabulary; optional `[sinks.postgresql.allowlist]` has only `fields`, a unique array drawn from `model|project|account_alias|native_request_identity_json` that defaults to empty. Allowlist tables are forbidden for disabled sinks. `collector_namespace`, `ledger_namespace`, every `source_namespace`, `sink_id`, and `destination_id` MUST match ASCII `^[a-z0-9](?:[a-z0-9._-]*[a-z0-9])?$`; each enabled sink's `projection_schema_id` MUST equal its capability's exact v1 constant; `schema_name` MUST match `^[a-z_][a-z0-9_]*$`; alias strings MUST be non-empty NFC Unicode without control characters or leading/trailing whitespace; and `source_project` MUST additionally contain no slash and not equal `.` or `..`. Project aliases map distinct canonical repository basenames to presentation only, never alter normalized project identity, fingerprint, or aggregate buckets, and become part of each affected sink's projection-policy digest; `account_alias` is separate, never a project alias or identity default, is null when absent, and becomes part of quota presentation and sink policy. Duplicate or unrecognized tables/keys, wrong types, invalid enums, duplicate mappings, and values outside the immutable profile subset MUST fail before component initialization. OTLP transport MUST use only the standard environment surface admitted by its fixed protocol profile, PostgreSQL MUST read a runtime-injected DSN only when enabled, and prompts, responses, raw records, auth tokens, DSNs, or secret environment values MUST NOT enter TOML, ledger, diagnostics, environment dumps, target/policy documents, or image layers.

ID: REQ-portable-runtime-and-release-002
Source: RFC 0001 § Configuration Contract; § Runtime and Trust Boundary
Scope: v1-mandatory

#### Scenario: Valid non-secret configuration loads
- **WHEN** the exact read-only config file contains only declared tables and keys and every technical namespace matches persisted state
- **THEN** startup validates selections and narrowed allowlists before initializing enabled components

#### Scenario: Multiple project aliases remain non-identifying
- **WHEN** Claude and Codex configure distinct aliases for multiple canonical repository basenames
- **THEN** every mapping validates independently, canonical project identity and null-tagged aggregates remain unchanged, and only the affected sink policy digest and presentation change

#### Scenario: Secret or namespace mutation fails safely
- **WHEN** TOML contains a DSN, token, raw record, unknown key, or a required technical namespace changes on restart
- **THEN** startup fails before scanning, credential access, export, or logging the value

#### Scenario: Disabled sink grammar has no technical tuple
- **WHEN** a sink has `enabled=false` and omits every tuple and allowlist key
- **THEN** its component health registers as disabled without creating a sink registration, checkpoint, lease, client, secret read, or DNS lookup

### Requirement: [TARGET-STATE] Exactly Three Canonical Source and State Targets
MUST recognize exactly `/sources/claude/sessions` and `/sources/codex/sessions` as separate optional read-only source-directory mounts and `/data` as the only persistent read-write state target, require every enabled source to be a distinct mount at its exact target, and reject any broad home, tool-configuration, auth-store, writable, overlapping, or symlink-expanded source; the TOML file is a separate read-only configuration surface and `/tmp` is ephemeral scratch, not a fourth source or state target.

ID: REQ-portable-runtime-and-release-003
Source: RFC 0001 § Runtime and Trust Boundary; § V1 Scope
Scope: v1-mandatory

#### Scenario: Canonical three-target deployment passes
- **WHEN** each enabled source is mounted distinctly and read-only at its exact canonical target and `/data` is the sole persistent writable volume
- **THEN** filesystem target validation passes without treating config or `/tmp` as source or state storage

#### Scenario: Broad or writable source fails before opening
- **WHEN** a deployment binds home, `.claude`, `.codex`, a broad parent, auth store, overlapping mount, writable source, or symlinked leaf
- **THEN** preflight fails before the collector opens source data

### Requirement: [TARGET-STATE] Host and Container Path Preflight
MUST inspect every host-side source and config path component without following symlinks, require each canonical source leaf to equal the configured source root, require the config path to be one regular read-only file mounted exactly at `/etc/ai-usage-telemetry/config.toml`, reject roots broader than the fixed projects or sessions tree, and enforce no-symlink and stay-beneath-target checks for every in-container source file open.

ID: REQ-portable-runtime-and-release-004
Source: RFC 0001 § Runtime and Trust Boundary
Scope: v1-mandatory

#### Scenario: Exact host and container paths pass
- **WHEN** every component is non-symlinked, each source root is the fixed narrow tree, the config is one exact regular file, and every discovered file stays beneath its target
- **THEN** preflight permits later profile and parser checks

#### Scenario: Symlink escape or include filter cannot narrow a broad bind
- **WHEN** a nested symlink escapes a canonical target or a host include filter attempts to narrow a broad bind
- **THEN** startup or discovery rejects it and opens no escaped file

### Requirement: [TARGET-STATE] Non-Root Read-Only-Root Runtime
MUST declare non-zero UID and GID, never start as root to change `/data` ownership, prove both source mounts and config non-writable and `/data` writable, run with read-only root, use only ephemeral `tmpfs` at `/tmp`, drop every Linux capability, set `no-new-privileges`, and expose, publish, bind, or listen on no port.

ID: REQ-portable-runtime-and-release-005
Source: RFC 0001 § Runtime and Trust Boundary
Scope: v1-mandatory

#### Scenario: Hardened runtime smoke test passes
- **WHEN** the container starts with nonzero IDs, pre-provisioned `/data`, read-only sources and root, tmpfs scratch, empty capabilities, no-new-privileges, and no port
- **THEN** startup completes its filesystem and privilege checks without elevation

#### Scenario: Any widened runtime property fails closed
- **WHEN** UID or GID is zero, a source or config is writable, `/data` is not writable, rootfs is writable, `/tmp` is host-persistent, a capability remains, privileges can be gained, or a port listens
- **THEN** startup or release smoke validation fails before collection

### Requirement: [TARGET-STATE] Deployment-Enforced Network Modes
MUST give local-ledger-only mode no network interface, DNS, or egress; require every sink mode's deployment policy to allow outbound traffic only to the selected destination endpoints and strictly necessary configured resolution endpoints; prohibit inbound access in every mode; and reject absent or unrestricted egress enforcement.

ID: REQ-portable-runtime-and-release-006
Source: RFC 0001 § Runtime and Trust Boundary; about/heart-and-soul/v1.md § Quality Bar
Scope: v1-mandatory

#### Scenario: Each bounded deployment mode reaches only its destinations
- **WHEN** local-only, OTLP-only, PostgreSQL-only, and both-sinks configurations run under their declared policies
- **THEN** local-only has zero network access and each sink mode reaches only its enabled destination and necessary resolution endpoints with no inbound path

#### Scenario: DNS or unallowlisted egress is blocked
- **WHEN** local-only mode attempts DNS or connection, or a sink mode attempts an unallowlisted endpoint
- **THEN** network policy blocks it and release validation fails

### Requirement: [TARGET-STATE] Disabled Sink Non-Instantiation
MUST ensure a disabled sink imports or instantiates no dependency-specific client, exporter, worker, credential reader, environment-secret reader, DNS lookup, connection pool, checkpoint, lease, task, or runtime path, while permitting exactly one content-safe component-registration row for local health; a never-bound disabled sink MUST have no registration or checkpoint, disabling a previously bound sink MUST retain but not advance its durable registration/checkpoint and remove any lease, and re-enabling it MUST pass exact target/policy digest validation before resuming. Either sink may be enabled independently without enabling the other or adding inbound access.

ID: REQ-portable-runtime-and-release-007
Source: RFC 0001 § Runtime and Trust Boundary; § Configuration Contract
Scope: v1-mandatory

#### Scenario: One sink operates independently
- **WHEN** exactly one optional sink is enabled
- **THEN** only that sink's dependencies, secret surface, worker, checkpoint, and outbound destination exist

#### Scenario: Both sinks disabled leave no sink footprint
- **WHEN** both sinks are disabled
- **THEN** process and network inspection finds no sink clients, credentials reads, DNS activity, checkpoints, leases, dependency imports, or sink tasks

### Requirement: [TARGET-STATE] Immutable Build and Runtime Inputs
MUST resolve Python and system dependencies from committed lockfiles, base images and fetched artifacts from immutable content digests, and generated artifacts from the bound source revision, and MUST reject floating image tags, mutable downloads, or unconstrained dependency resolution as release inputs.

ID: REQ-portable-runtime-and-release-008
Source: RFC 0001 § Runtime and Trust Boundary; § Integration
Scope: v1-mandatory

#### Scenario: Locked inputs reproduce membership
- **WHEN** each architecture builds from the same source revision, committed locks, and immutable base and artifact digests
- **THEN** release evidence records those exact inputs and resulting child image digest

#### Scenario: Floating input blocks publication
- **WHEN** a base image or dependency is floating, unlocked, or resolves outside its declared digest
- **THEN** the build is rejected and no release artifact is published

### Requirement: [TARGET-STATE] Native Dual-Architecture Release Gate
MUST build amd64 and arm64 images for one OCI manifest from the same source revision, dependency lock, adapter schemas, ledger and query schemas, projection schemas, and release profile, and require each image to run natively through the complete parser and privacy, identity and fingerprint, replay and migration, cursor and rescan, query and health, sink, mount, privilege, write, port, and network-isolation gates.

ID: REQ-portable-runtime-and-release-009
Source: RFC 0001 § Integration
Scope: v1-mandatory

#### Scenario: Both native gates pass
- **WHEN** amd64 and arm64 child images each complete the same gate corpus on native hosts from identical bound inputs
- **THEN** their immutable child digests are eligible for the same OCI manifest

#### Scenario: Emulation or partial gate is insufficient
- **WHEN** one architecture is tested only under emulation or omits any common native gate
- **THEN** neither a v1 manifest nor a single-architecture v1 image is published

### Requirement: [TARGET-STATE] Cross-Architecture Semantic Parity
MUST require native amd64 and arm64 runs to produce equal canonical normalized facts, accounting fingerprints, logical SQLite schema and stable-view results, OTLP descriptors and semantic points, PostgreSQL schema and rows, structured-health schema, adapter classifications, mount and privilege results, write boundaries, network behavior, and sink semantics; raw SQLite files, protobuf byte ordering, image digests, and runtime timestamps are not parity targets.

ID: REQ-portable-runtime-and-release-010
Source: RFC 0001 § Integration
Scope: v1-mandatory

#### Scenario: Canonical outputs match across architectures
- **WHEN** both native gates process the same fixtures under the same profile
- **THEN** every declared semantic parity target compares equal

#### Scenario: Architecture-specific divergence blocks publication
- **WHEN** any canonical output, security posture, network behavior, adapter result, or sink semantic differs across architectures
- **THEN** the parity gate fails and publication is denied
