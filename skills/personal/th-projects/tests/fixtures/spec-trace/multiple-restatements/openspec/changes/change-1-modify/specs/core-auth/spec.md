## MODIFIED Requirements

### Requirement: Session Tokens
ID: REQ-core-auth-001
Source: RFC 0003 §1
Scope: v1-mandatory

Sessions SHALL use signed tokens with key rotation.

#### Scenario: Rotated key signs token
- **WHEN** a session token is issued after key rotation
- **THEN** the active key signs the token
