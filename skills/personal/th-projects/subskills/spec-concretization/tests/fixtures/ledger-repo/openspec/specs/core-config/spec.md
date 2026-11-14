# Core Configuration

## Purpose
Loads and validates application configuration at startup.

## Requirements

### Requirement: Configuration Loading and Validation
The system SHALL load `config.toml` and validate all required fields before serving traffic.

ID: REQ-core-config-001
Source: RFC 0001 §2.1
Scope: v1-mandatory

#### Scenario: Valid config loads successfully
- **WHEN** a well-formed `config.toml` exists
- **THEN** the application starts and serves traffic

#### Scenario: Missing required field blocks startup
- **WHEN** `config.toml` omits a required field
- **THEN** startup aborts with a named-field error
- **AND** the process exits non-zero

### Requirement: Environment Variable Expansion
In post-v1 scope, config values SHALL support environment variable expansion.

ID: REQ-core-config-002
Source: heart-and-soul/vision.md #2
Scope: post-v1

#### Scenario: Env var expands
- **WHEN** a config value contains `${VAR}` and `VAR` is set
- **THEN** the resolved value replaces the reference

### Requirement: Configuration Error Reporting
The system SHALL report every invalid field in one startup error rather than stopping at the first.

ID: REQ-core-config-004
Source: [Observed] src/config/loader.py
Scope: v1-mandatory

#### Scenario: Several invalid fields reported together
- **WHEN** `config.toml` contains two invalid fields
- **THEN** the startup error names both fields
