# Core Configuration

## Purpose
Loads and validates application configuration at startup.

## Requirements

### Requirement: Configuration Loading and Validation
ID: REQ-core-config-001
Source: RFC 0001 §2.1
Scope: v1-mandatory

The system SHALL load `config.toml` and validate all required fields before serving traffic.

#### Scenario: Valid config loads successfully
- **WHEN** a well-formed `config.toml` exists
- **THEN** the application starts and serves traffic

#### Scenario: Missing required field blocks startup
- **WHEN** `config.toml` omits a required field
- **THEN** startup aborts with a named-field error
- **AND** the process exits non-zero

### Requirement: Environment Variable Expansion
ID: REQ-core-config-002
Source: heart-and-soul/vision.md #2
Scope: post-v1

Config values MAY reference environment variables for expansion.

#### Scenario: Env var expands
- **WHEN** a config value contains `${VAR}` and `VAR` is set
- **THEN** the resolved value replaces the reference
