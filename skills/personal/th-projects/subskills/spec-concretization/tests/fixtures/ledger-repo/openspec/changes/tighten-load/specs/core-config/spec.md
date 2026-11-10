## MODIFIED Requirements

### Requirement: Configuration Loading and Validation
The system SHALL load `config.toml`, validate all required fields, and reject unknown keys before serving traffic.

ID: REQ-core-config-001
Source: RFC 0001 §2.2
Scope: v1-mandatory

#### Scenario: Unknown key blocks startup
- **WHEN** `config.toml` contains an unknown key
- **THEN** startup aborts naming the key
