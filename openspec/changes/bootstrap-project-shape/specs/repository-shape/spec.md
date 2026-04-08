# Repository Shape Spec

## Domain

This spec covers the repository-level structure and placement rules for shared AI-assistant knowledge in `genai/`.

### Requirement: Skills-First Shared Assets

The repository MUST keep reusable cross-tool workflow skills in `skills/`, treating that tree as the primary local source used for installation and mirroring across supported assistant runtimes.

Source: Doctrine rules 1, 3, and 7; RFC 0001 §3.1, §3.2, §3.3
Scope: v1-mandatory

#### Scenario: Shared skill placement

- **WHEN** a skill is intended for more than one assistant runtime
- **THEN** the authored source lives under `skills/` instead of only inside a tool-specific namespace

#### Scenario: Mirrored skill entrypoint

- **WHEN** a skill appears under `.claude/skills`, `.codex/skills`, `.gemini/skills`, or `.gemini/antigravity/skills`
- **THEN** that location is treated as a mirror or entrypoint surface rather than the authored source of truth

### Requirement: Selective Agent Reuse

Agent definitions that remain useful across tools MAY live under `agents/`, but that layer MUST be treated as secondary reference material rather than the repository's primary workflow surface.

Source: Doctrine rules 1 and 7; RFC 0001 §3.1, §3.2
Scope: v1-mandatory

#### Scenario: Shared reference prompt

- **WHEN** an older cross-tool prompt is retained for selective reuse
- **THEN** it may remain under `agents/` without changing the repo's skills-first operating model

### Requirement: Tool-Specific Adapters

Tool-specific prompts, settings, rules, and metadata MUST live in their platform namespace and may diverge from shared content only when platform syntax or runtime behavior requires it.

Source: Doctrine rules 2 and 4; RFC 0001 §3.1, §3.2, §3.3
Scope: v1-mandatory

#### Scenario: Platform-only metadata

- **WHEN** a file exists only to satisfy a platform-specific loader, config format, or prompt convention
- **THEN** it lives under that platform's namespace rather than the shared layer

#### Scenario: Avoid silent fork

- **WHEN** a contributor introduces both a shared artifact and a platform-specific counterpart
- **THEN** the authoritative source and reason for divergence are documented

### Requirement: Local-Only State Exclusion

Secrets, runtime IDs, caches, logs, session artifacts, and per-machine overrides MUST remain outside canonical versioned content or be explicitly ignored when runtime placement requires them under a tool namespace. Shared non-secret baseline settings MAY be versioned when they are intended as portable defaults.

Source: Doctrine rule 5; RFC 0001 §3.4
Scope: v1-mandatory

#### Scenario: Runtime cache under tool directory

- **WHEN** a tool writes caches or sessions under its own config root
- **THEN** those paths are not treated as canonical repository assets

#### Scenario: Machine-specific secret or ID

- **WHEN** a file contains local credentials, runtime identifiers, or machine-specific overrides
- **THEN** it is excluded from committed source

### Requirement: Reproducible Generated Assets

Vendored or generated artifacts MUST have a documented regeneration path checked into the repository.

Source: Doctrine rule 6; RFC 0001 §3.3
Scope: v1-mandatory

#### Scenario: Vendored bundle refresh

- **WHEN** the repository keeps a generated bundle inside a skill directory
- **THEN** a checked-in script documents and performs the regeneration flow

### Requirement: Shape Documentation

The repository MUST maintain doctrine, topology, design-contract, and specification documents that explain where shared assets belong and how repository rules trace across those layers.

Source: Doctrine rule 7; RFC 0001 §3.5
Scope: v1-mandatory

#### Scenario: New contributor placement question

- **WHEN** a contributor needs to decide where a new shared or tool-specific artifact belongs
- **THEN** the answer can be derived from repository shape docs without relying on tribal knowledge

#### Scenario: Repository audit

- **WHEN** the repository is audited for structural drift
- **THEN** auditors can trace doctrine principles to RFC contracts and then to repository-level requirements
