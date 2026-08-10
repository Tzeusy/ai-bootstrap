---
name: spec-and-spine
description: >
  Ground AI Usage Telemetry implementation, testing, planning, and behavior
  changes in its accepted OpenSpec capability contracts. Use to locate an
  owning requirement, check spec-code divergence, amend behavior, or trace work
  through the active v1 change.
---

# AI Usage Telemetry Capability Specs

The active change is unimplemented and unarchived. Seven current capability
rows retain Decision 0002 acceptance; four corrected rows are unknown pending
exact-head review and successor acceptance. Load the smallest owner, and never
treat accepted or candidate contract bytes as runtime or release evidence.

Trigger examples: "what requirement owns this?", "does this behavior match the
spec?", "which acceptance scenarios must this task prove?"

## Change route

| Document | Read when... |
|---|---|
| [Proposal](../../../openspec/changes/establish-ai-usage-telemetry-v1/proposal.md) | Checking motivation, scope, or capability inventory |
| [Design](../../../openspec/changes/establish-ai-usage-telemetry-v1/design.md) | Checking cross-capability ownership and sequencing |
| [Acceptance](../../../openspec/changes/establish-ai-usage-telemetry-v1/acceptance.md) | Checking accepted-contract authority and remaining gates |
| [Tasks](../../../openspec/changes/establish-ai-usage-telemetry-v1/tasks.md) | Mapping implementation and verification work |

## Capability lookup

| Concern | Specification |
|---|---|
| Synthetic end-to-end proof | [synthetic-usage-spine](../../../openspec/changes/establish-ai-usage-telemetry-v1/specs/synthetic-usage-spine/spec.md) |
| Source profiles and parsing | [source-adapter-profiles](../../../openspec/changes/establish-ai-usage-telemetry-v1/specs/source-adapter-profiles/spec.md) |
| Identity and normalization | [event-identity-and-normalization](../../../openspec/changes/establish-ai-usage-telemetry-v1/specs/event-identity-and-normalization/spec.md) |
| Reconciliation and health | [stream-reconciliation-and-health](../../../openspec/changes/establish-ai-usage-telemetry-v1/specs/stream-reconciliation-and-health/spec.md) |
| Durable accounting | [durable-local-ledger](../../../openspec/changes/establish-ai-usage-telemetry-v1/specs/durable-local-ledger/spec.md) |
| Quota state | [quota-snapshot-semantics](../../../openspec/changes/establish-ai-usage-telemetry-v1/specs/quota-snapshot-semantics/spec.md) |
| Local inspection | [local-query-contract](../../../openspec/changes/establish-ai-usage-telemetry-v1/specs/local-query-contract/spec.md) |
| OTLP export | [otlp-metrics-projection](../../../openspec/changes/establish-ai-usage-telemetry-v1/specs/otlp-metrics-projection/spec.md) |
| PostgreSQL export | [postgresql-history-projection](../../../openspec/changes/establish-ai-usage-telemetry-v1/specs/postgresql-history-projection/spec.md) |
| Profile admission | [release-profile-governance](../../../openspec/changes/establish-ai-usage-telemetry-v1/specs/release-profile-governance/spec.md) |
| Runtime and release | [portable-runtime-and-release](../../../openspec/changes/establish-ai-usage-telemetry-v1/specs/portable-runtime-and-release/spec.md) |

No governing requirement means spec amendment before implementation.
