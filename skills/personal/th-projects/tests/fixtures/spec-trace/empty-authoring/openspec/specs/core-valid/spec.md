# Valid Core

## Purpose
Proves a populated main spec cannot mask an empty delta during authoring.

## Requirements

### Requirement: Valid Baseline
In post-v1 scope, the system SHALL expose the baseline capability.

ID: REQ-core-valid-001
Source: heart-and-soul/vision.md #1
Scope: post-v1

#### Scenario: Baseline is visible
- **WHEN** the capability is inspected
- **THEN** the valid baseline is reported
