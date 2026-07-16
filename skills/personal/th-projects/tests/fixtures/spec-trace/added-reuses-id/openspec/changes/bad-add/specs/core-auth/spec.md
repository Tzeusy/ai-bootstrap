## ADDED Requirements

### Requirement: Session Tokens
Sessions SHALL use signed tokens.

ID: REQ-core-auth-001
Source: RFC 0003 §1
Scope: v1-mandatory

#### Scenario: Added token is signed
- **WHEN** a session token is issued
- **THEN** the token carries a valid signature
