---
name: craft-and-care
description: >
  MANDATORY for non-trivial AI Usage Telemetry changes. Load the relevant
  project-specific execution standards before implementation, review, testing,
  dependency or interface changes, observability work, security-sensitive
  handling, documentation updates, or completion claims.
---

# AI Usage Telemetry Engineering Standards

Start with the project engineering bar, then load only the narrower standard
needed. The project bar adopts the repository-wide `/th-engineering`
engineering bar by reference and records project-specific additions. Do not
copy the canonical default biases into this skill.

Trigger examples: "what evidence is required?", "is this safe to merge?", "how
must this failure path be observed?"

| Document | Read when... |
|---|---|
| [Pillar index](../../../about/craft-and-care/README.md) | Orienting to scope, status, and reading order |
| [Engineering bar](../../../about/craft-and-care/engineering-bar.md) | Any non-trivial change or completion judgment |
| [Testing and verification](../../../about/craft-and-care/testing-and-verification.md) | Planning regression, failure, replay, privacy, or release evidence |
| [Security and privacy](../../../about/craft-and-care/security-and-privacy.md) | Touching source records, content, credentials, metadata, mounts, or privileges |
| [Interfaces and dependencies](../../../about/craft-and-care/interfaces-and-dependencies.md) | Changing APIs, ownership boundaries, schemas, or dependencies |
| [Observability and operations](../../../about/craft-and-care/observability-and-operations.md) | Changing health, diagnostics, recovery, or partial-failure behavior |
| [Review and documentation](../../../about/craft-and-care/review-and-documentation.md) | Preparing review, dispositions, handoff, or same-change documentation |

When these standards conflict with the repository-wide default bar, the
project-specific standards govern.
