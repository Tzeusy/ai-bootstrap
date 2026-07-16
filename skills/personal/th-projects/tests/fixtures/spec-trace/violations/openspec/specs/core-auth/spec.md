# Core Auth

## Purpose
Authentication and session handling.

## ADDED Requirements

### Requirement: Session Tokens
Sessions SHALL use signed tokens.

ID: REQ-core-auth-001
Source: RFC 0002 §3
Scope: v1-mandatory

#### Scenario: Two WHENs is malformed
- **WHEN** a token is issued
- **WHEN** a token is validated
- **THEN** the signature is checked

### Requirement: Token Revocation
The system SHALL revoke active tokens on demand.

ID: REQ-core-auth-001
Scope: v1-mandatory

### Requirement: Password Hashing
The system SHALL store only salted password hashes.

ID: REQ-wrong-spec-002
Source: RFC 0002 §4
Scope: v1-mandatory

#### Scenario: Hash on write
- **WHEN** a password is stored
- **THEN** only a salted hash is persisted

## Notes

Arbitrary main-spec H2 headings are not part of the shared format.
