# Core Auth

## Purpose
Defines authentication behavior.

## Requirements

### Requirement: Session Tokens
Sessions SHALL use signed tokens.

ID: REQ-core-auth-001
Source: RFC 0002 §3
Scope: v1-mandatory

#### Scenario: Token is signed
- **WHEN** a session token is issued
- **THEN** the token carries a valid signature
