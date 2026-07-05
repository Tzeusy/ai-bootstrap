# Core Auth

## Purpose
Authentication and session handling.

## ADDED Requirements

### Requirement: Session Tokens
ID: REQ-core-auth-001
Source: RFC 0002 §3
Scope: v1-mandatory

Sessions SHALL use signed tokens.

#### Scenario: Two WHENs is malformed
- **WHEN** a token is issued
- **WHEN** a token is validated
- **THEN** the signature is checked

### Requirement: Token Revocation
ID: REQ-core-auth-001
Scope: v1-mandatory

Duplicate ID above; also missing Source; also no scenario.

### Requirement: Password Hashing
ID: REQ-wrong-spec-002
Source: RFC 0002 §4
Scope: v1-mandatory

ID names the wrong spec directory.

#### Scenario: Hash on write
- **WHEN** a password is stored
- **THEN** only a salted hash is persisted
