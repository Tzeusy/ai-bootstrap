# V1 Capability Contract Acceptance

**Change:** `establish-ai-usage-telemetry-v1`
**Status:** Active change; contracts accepted; not implemented; not archived
**Owner decision:**
[Decision 0002](../../../about/heart-and-soul/decisions/0002-accept-v1-capability-contracts.md)

R5 reviewed exact HEAD `e2bb9ea78984878c6e06a9e37946f923032150f9`
and returned `APPROVED_FOR_PROMOTION` with findings `0 / 0 / 0`. Decision 0002
therefore records one independent contract row for each canonical capability:

- `synthetic-usage-spine`
- `source-adapter-profiles`
- `event-identity-and-normalization`
- `stream-reconciliation-and-health`
- `durable-local-ledger`
- `quota-snapshot-semantics`
- `local-query-contract`
- `otlp-metrics-projection`
- `postgresql-history-projection`
- `release-profile-governance`
- `portable-runtime-and-release`

The exact promoted review anchors are RFC 0001
`36c062fa81bfadb5e9b90c0386ae7529579648acf04a165e923adca5e9e03163`,
source/bounds evidence
`2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d`,
synthetic vectors
`8e5e512144e03d437aa0349b7d00b3600fae5dd24e2d613236d6c6e699953e8a`,
and provenance
`dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0`.
Decision 0002 contains each current `spec.md` SHA-256 binding; the durable
[R1-R5 ledger](../../../about/legends-and-lore/reviews/0001/2026-08-10-specification-reconciliation.md)
records how the candidate converged.

This file is only the active change's governance projection. It is not a
runtime or release profile and contains no profile member or value. It records
no implementation, real source, personal data, sink/destination, package,
image, archive, or release authorization. Later work remains governed by the
active tasks, evidence-backed domain profiles, and their subsequent gates.
