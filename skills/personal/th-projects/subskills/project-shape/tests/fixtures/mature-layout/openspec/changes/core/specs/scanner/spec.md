# Scanner Spec

## Requirement

The scanner MUST report a mature repo only when doctrine, RFC, spec, and topology traceability are present.

Source: RFC 0001 §Design
Scope: v1-mandatory

### Scenario: mature traceability
- **WHEN** a repo has authored doctrine, RFCs, specs, topology, and local skills
- **THEN** the scanner may report `MATURE`
