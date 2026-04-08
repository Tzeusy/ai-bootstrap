# Runtime Spec

## Requirement

The scanner MUST recognize legacy pillar locations.

Source: RFC 0001 §Design
Scope: v1-mandatory

### Scenario: legacy paths
- **WHEN** a project uses `docs/rfcs/` and `ARCHITECTURE.md`
- **THEN** the scanner reports design contracts and topology as present
