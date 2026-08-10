# Legends and Lore

Design contracts for AI Usage Telemetry.

**Status:** R5 confirmed and promoted predecessor RFC/evidence bytes under
Owner Decision 0001's standing direction. Current corrected RFC/synthetic
bytes and four affected capability rows are pending exact-head review and
successor owner acceptance; seven current spec rows still match Decision 0002.
See the central
[lifecycle matrix](../README.md#lifecycle-status), the current
[R1-R5 ledger](./reviews/0001/2026-08-10-specification-reconciliation.md),
and the preserved [`reviews/0001/`](./reviews/0001/) history. The OpenSpec
change remains active, unimplemented, and unarchived.

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
3. [`reviews/0001/2026-08-10-final-branch-correction.md`](./reviews/0001/2026-08-10-final-branch-correction.md)
   is the current route: it records the pending correction hashes, fail-closed
   authority state, and exact confirmation required before promotion.
4. [`reviews/0001/2026-08-10-specification-reconciliation.md`](./reviews/0001/2026-08-10-specification-reconciliation.md)
   records the exact R1-R5 reviewed heads, fix commits, accepted hashes, checks,
   and predecessor promotion boundary.
5. [`reviews/0001/2026-08-10-r4-quality-evidence-resweep.md`](./reviews/0001/2026-08-10-r4-quality-evidence-resweep.md)
   preserves the R4 input, predecessor hashes, bounded corrections, and R5
   confirmation append. Earlier records remain under [`reviews/0001/`](./reviews/0001/).

Relationship to the other pillars:

- [`heart-and-soul`](../heart-and-soul/README.md) defines why local facts must become user-owned history while content and credentials stay outside the collector.
- Legends-and-lore defines the load-bearing runtime, adapter, ledger, and sink contracts that preserve those principles.
- The `READY` launch-gate administration and R1-R5 convergence are recorded,
  and Decision 0002 preserves the R5 contract decisions independently. Four
  corrected current rows are unknown until successor acceptance, so task 2.1
  remains closed for non-synthetic work.
  Follow
  its [`proposal`](../../openspec/changes/establish-ai-usage-telemetry-v1/proposal.md)
  → [`design`](../../openspec/changes/establish-ai-usage-telemetry-v1/design.md)
  → [`specifications`](../../openspec/changes/establish-ai-usage-telemetry-v1/specs/)
  → [`acceptance`](../../openspec/changes/establish-ai-usage-telemetry-v1/acceptance.md)
  → [`tasks`](../../openspec/changes/establish-ai-usage-telemetry-v1/tasks.md)
  route; the later task, profile, runtime, archive, and release gates still
  apply.
- [`lay-and-land`](../lay-and-land/README.md) maps the components, mounts, data flow, and deployment boundary.
- [`craft-and-care`](../craft-and-care/README.md) governs implementation quality, verification, observability, and maintenance.

The historical R3 RFC anchor was
`ca548d5cb5070c5e288e66d3fe97a3c0f662cd245bd7153ae640d2ed593dcbc2`,
recorded by Owner Decision 0001. At exact R4 input HEAD, source/bounds
`219531d0f87145c6722d66ccb5de7abdaf3306daecd2fdd717a32a76b2d701df`
and synthetic vectors
`c10308d1bbb75f52d5000f51b23f3cd4733bc38fe6d429a2fb7580292e743372`
were re-accepted as quality-evidence annexes. Those predecessor hashes remain
historical records.

R5 reviewed exact HEAD `e2bb9ea78984878c6e06a9e37946f923032150f9`
and promoted the predecessor RFC
`36c062fa81bfadb5e9b90c0386ae7529579648acf04a165e923adca5e9e03163`,
source/bounds
`2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d`,
synthetic vectors
`8e5e512144e03d437aa0349b7d00b3600fae5dd24e2d613236d6c6e699953e8a`,
and unchanged provenance
`dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0`.
Those hashes remain accepted while the corrected current RFC/synthetic bytes
await a new exact-head review and successor decision. The formal review and
reconciliation entries preserve the full historical digest trail.
Source/resource profiles still require their downstream evidence gates before
real mounts, ingestion, exports, packaging, archival, or release.
