# Valid Core

## Purpose
Proves a populated main spec cannot mask an empty delta during authoring.

## Requirements

### Requirement: Valid Baseline
ID: REQ-core-valid-001
Source: heart-and-soul/vision.md #1
Scope: post-v1

The system MAY expose a valid baseline capability.

#### Scenario: Baseline is visible
- **WHEN** the capability is inspected
- **THEN** the valid baseline is reported
