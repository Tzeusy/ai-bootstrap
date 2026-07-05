## ADDED Requirements

### Requirement: Hot Configuration Reload
ID: REQ-core-config-003
Source: RFC 0004 §1.2
Scope: v1-mandatory

The system SHALL reload configuration on SIGHUP without dropping connections.

#### Scenario: Reload applies new values
- **WHEN** SIGHUP arrives with a valid updated `config.toml`
- **THEN** new values take effect without restart
