# Requirement Ordering

## Purpose
Exercises invalid requirement block ordering.

## Requirements

### Requirement: Metadata First
ID: REQ-core-ordering-001
Source: RFC 0001 §1
Scope: post-v1

The system MUST reject metadata before the normative paragraph.

#### Scenario: Metadata-first ordering is inspected
- **WHEN** the requirement is validated
- **THEN** the ordering is rejected

### Requirement: Metadata First With Missing Scope
ID: REQ-core-ordering-006
Source: RFC 0001 §6

The system MUST reject metadata before the normative paragraph even when a field is missing.

#### Scenario: Incomplete metadata-first ordering is inspected
- **WHEN** the requirement is validated
- **THEN** the ordering is rejected

### Requirement: Split Metadata
The system MUST keep requirement metadata contiguous.

ID: REQ-core-ordering-002

Source: RFC 0001 §2
Scope: post-v1

#### Scenario: Split metadata is inspected
- **WHEN** the requirement is validated
- **THEN** the ordering is rejected

### Requirement: Scenario Before Metadata
The system MUST place metadata before scenarios.

#### Scenario: Early scenario is inspected
- **WHEN** the requirement is validated
- **THEN** the ordering is rejected

ID: REQ-core-ordering-003
Source: RFC 0001 §3
Scope: post-v1

### Requirement: Non-Normative First Paragraph
The system documents requirement ordering.

ID: REQ-core-ordering-004
Source: RFC 0001 §4
Scope: post-v1

#### Scenario: Non-normative paragraph is inspected
- **WHEN** the requirement is validated
- **THEN** the ordering is rejected

### Requirement: Prose Before Scenario
The system MUST place scenarios directly after requirement metadata.

ID: REQ-core-ordering-005
Source: RFC 0001 §5
Scope: post-v1

This displaced prose breaks the canonical ordering.

#### Scenario: Displaced prose is inspected
- **WHEN** the requirement is validated
- **THEN** the ordering is rejected
