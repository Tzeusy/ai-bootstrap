# Legends and Lore

Design contracts for AI Usage Telemetry.

**Status:** RFC 0001 remains accepted at its R3 anchor through Owner Decision
0001. R4 independently re-swept the later evidence annexes and applied bounded
corrections whose current hashes are pending fresh R5 confirmation. See the central
[lifecycle matrix](../README.md#lifecycle-status) and the
[`reviews/0001/`](./reviews/0001/) record. The launch gate has recorded `READY`;
the active OpenSpec change is a complete authored candidate awaiting four
improvement cycles and conditional owner acceptance, not an owner-accepted
capability set.

This pillar answers how local usage facts cross tool-specific session formats,
the durable normalized ledger, and optional telemetry sinks without exposing
conversation content or depending on vendor credentials.

Reading order:

1. [`rfcs/0001-adapter-ledger-and-sink-contract.md`](./rfcs/0001-adapter-ledger-and-sink-contract.md): the v1 contracts for source adapters, normalized usage and quota facts, exact local accounting, failure isolation, and optional OTLP Metrics and PostgreSQL sinks.
2. [`evidence/0001-source-and-bounds.md`](./evidence/0001-source-and-bounds.md)
   records the content-safe source evidence and bounded release-profile decision;
   [`evidence/0001-synthetic-vectors.md`](./evidence/0001-synthetic-vectors.md)
   defines the pre-implementation evidence inventory; and
   [`evidence/0001-provenance.md`](./evidence/0001-provenance.md) pins reviewed
   clients, public source, safe commands, and unresolved structural claims.
3. [`reviews/0001/2026-08-10-r4-quality-evidence-resweep.md`](./reviews/0001/2026-08-10-r4-quality-evidence-resweep.md)
   is the current route: it records the exact R4 input HEAD, accepted pre-fix
   evidence hashes, bounded corrections, candidate hashes, and mandatory R5
   confirmation. Earlier review rounds remain under [`reviews/0001/`](./reviews/0001/).

Relationship to the other pillars:

- [`heart-and-soul`](../heart-and-soul/README.md) defines why local facts must become user-owned history while content and credentials stay outside the collector.
- Legends-and-lore defines the load-bearing runtime, adapter, ledger, and sink contracts that preserve those principles.
- The `READY` launch-gate administration is recorded, and the active OpenSpec
  candidate turns this contract into testable capability requirements. Follow
  its [`proposal`](../../openspec/changes/establish-ai-usage-telemetry-v1/proposal.md)
  → [`design`](../../openspec/changes/establish-ai-usage-telemetry-v1/design.md)
  → [`specifications`](../../openspec/changes/establish-ai-usage-telemetry-v1/specs/)
  → [`tasks`](../../openspec/changes/establish-ai-usage-telemetry-v1/tasks.md)
  route; four improvement cycles and conditional owner acceptance still remain.
- [`lay-and-land`](../lay-and-land/README.md) maps the components, mounts, data flow, and deployment boundary.
- [`craft-and-care`](../craft-and-care/README.md) governs implementation quality, verification, observability, and maintenance.

RFC 0001 is accepted project law through the R3 artifact digest
`ca548d5cb5070c5e288e66d3fe97a3c0f662cd245bd7153ae640d2ed593dcbc2`,
recorded by Owner Decision 0001. At exact R4 input HEAD, source/bounds
`219531d0f87145c6722d66ccb5de7abdaf3306daecd2fdd717a32a76b2d701df`
and synthetic vectors
`c10308d1bbb75f52d5000f51b23f3cd4733bc38fe6d429a2fb7580292e743372`
were re-accepted as quality-evidence annexes. The current corrected candidate
hashes are RFC
`36c062fa81bfadb5e9b90c0386ae7529579648acf04a165e923adca5e9e03163`,
source/bounds
`2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d`,
and synthetic vectors
`8e5e512144e03d437aa0349b7d00b3600fae5dd24e2d613236d6c6e699953e8a`;
they remain pending fresh R5 and are not accepted authority. The formal review
and prior reconciliation entries preserve the historical digest trail.
Source/resource profiles still require their downstream evidence gates before
real mounts, ingestion, exports, or a release claim are enabled.
