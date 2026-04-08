# Repository Shape Spec

## Domain

This spec covers the repository-level structure and placement rules for shared AI-assistant knowledge in `genai/`.

### Requirement: Skills-First Shared Assets

The repository MUST keep reusable cross-tool workflow skills in `skills/`, treating that tree as the primary local source used for installation and mirroring across supported assistant runtimes.

Source: Doctrine rules 1, 3, and 7; RFC 0001 §Repository Layers, §Source-of-Truth Rules, §Distribution Model
Scope: v1-mandatory

#### Scenario: Shared skill placement

- **WHEN** a skill is intended for more than one assistant runtime
- **THEN** the authored source lives under `skills/` instead of only inside a tool-specific namespace

#### Scenario: Mirrored skill entrypoint

- **WHEN** a skill appears under `.claude/skills`, `.codex/skills`, `.gemini/skills`, or `.gemini/antigravity/skills`
- **THEN** that location is treated as a mirror or entrypoint surface rather than the authored source of truth

#### Scenario: Flattened mirrored name

- **WHEN** a mirrored skill name is flattened by basename in a tool-specific skills directory
- **THEN** provenance and ownership are still determined from the source directory under `skills/`

### Requirement: Provenance Visibility

The repository MUST preserve visible provenance for shared skills so contributors can distinguish locally authored workflow logic from upstream-derived material and intentional forks.

Source: Doctrine rules 1, 3, and 7; RFC 0001 §Repository Layers, §Source-of-Truth Rules
Scope: v1-mandatory

#### Scenario: Upstream-derived skill tree

- **WHEN** a non-`personal/` skill directory is mirrored locally for installation
- **THEN** the repository continues to identify it as upstream-derived, vendored, or intentionally forked rather than silently relabeling it as wholly local authorship

#### Scenario: Intentional fork

- **WHEN** upstream-derived content is adapted locally
- **THEN** the authoritative copy and reason for the fork are documented

### Requirement: Portable Installation and Distribution

The repository MUST preserve its standalone clone-or-submodule installation model and make clear that mirror layers do not supersede the source tree.

Source: Doctrine rules 4 and 7; RFC 0001 §Distribution Model, §Documentation Contract
Scope: v1-mandatory

#### Scenario: Standalone install path

- **WHEN** a contributor installs this repository directly
- **THEN** the documented config targets and skill-mirroring flow remain derivable from repository docs without relying on an enclosing parent repo

#### Scenario: Mirror layer is not authoritative

- **WHEN** tool-specific skill mirrors or entrypoints are created during installation
- **THEN** those mirrors remain distribution surfaces rather than replacing the source tree under `skills/`

### Requirement: Selective Agent Reuse

Agent definitions that remain useful across tools MAY live under `agents/`, but that layer MUST be treated as secondary reference material rather than the repository's primary workflow surface.

Source: Doctrine rules 1 and 7; RFC 0001 §Repository Layers, §Source-of-Truth Rules
Scope: v1-mandatory

#### Scenario: Shared reference prompt

- **WHEN** an older cross-tool prompt is retained for selective reuse
- **THEN** it may remain under `agents/` without changing the repo's skills-first operating model

### Requirement: Tool-Specific Adapters

Tool-specific prompts, settings, rules, and metadata MUST live in their platform namespace and may diverge from shared content only when platform syntax or runtime behavior requires it.

Source: Doctrine rules 2 and 4; RFC 0001 §Repository Layers, §Source-of-Truth Rules, §Distribution Model
Scope: v1-mandatory

#### Scenario: Platform-only metadata

- **WHEN** a file exists only to satisfy a platform-specific loader, config format, or prompt convention
- **THEN** it lives under that platform's namespace rather than the shared layer

#### Scenario: Avoid silent fork

- **WHEN** a contributor introduces both a shared artifact and a platform-specific counterpart
- **THEN** the authoritative source and reason for divergence are documented

### Requirement: Local-Only State Exclusion

Secrets, runtime IDs, caches, logs, session artifacts, and per-machine overrides MUST remain outside canonical versioned content or be explicitly ignored when runtime placement requires them under a tool namespace. Shared non-secret baseline settings MAY be versioned when they are intended as portable defaults.

Source: Doctrine rule 5; RFC 0001 §Runtime and Local-Only State
Scope: v1-mandatory

#### Scenario: Runtime cache under tool directory

- **WHEN** a tool writes caches or sessions under its own config root
- **THEN** those paths are not treated as canonical repository assets

#### Scenario: Machine-specific secret or ID

- **WHEN** a file contains local credentials, runtime identifiers, or machine-specific overrides
- **THEN** it is excluded from committed source

#### Scenario: Versioned non-secret default

- **WHEN** a tracked tool config file contains portable, non-secret baseline settings
- **THEN** that file may remain versioned without being treated as machine-private state

### Requirement: Reproducible Generated Assets

Vendored or generated artifacts MUST have a documented regeneration path checked into the repository.

Source: Doctrine rule 6; RFC 0001 §Distribution Model
Scope: v1-mandatory

#### Scenario: Vendored bundle refresh

- **WHEN** the repository keeps a generated bundle inside a skill directory
- **THEN** a checked-in script documents and performs the regeneration flow

### Requirement: Pillar Presence

The repository MUST maintain doctrine, topology, design-contract, and specification documents covering repository shape.

Source: Doctrine rule 7; RFC 0001 §Documentation Contract
Scope: v1-mandatory

#### Scenario: Pillar inventory

- **WHEN** the repository is inspected for shape coverage
- **THEN** each of the four pillars has an authored home with project-specific content

### Requirement: Traceable Navigation

The repository MUST make it possible for contributors and auditors to trace placement rules across doctrine, design contracts, topology, and specifications.

Source: Doctrine rule 7; RFC 0001 §Documentation Contract
Scope: v1-mandatory

#### Scenario: New contributor placement question

- **WHEN** a contributor needs to decide where a new shared or tool-specific artifact belongs
- **THEN** the answer can be derived from repository shape docs without relying on tribal knowledge

#### Scenario: Repository audit

- **WHEN** the repository is audited for structural drift
- **THEN** auditors can trace doctrine principles to RFC contracts and then to repository-level requirements
