# V1 Capability Contract Acceptance

**Change:** `establish-ai-usage-telemetry-v1`
**Status:** Active change; seven current contract rows accepted; four corrected
rows pending exact-head review and successor owner acceptance; not implemented;
not archived
**Accepted predecessor decision:**
[Decision 0002](../../../about/heart-and-soul/decisions/0002-accept-v1-capability-contracts.md)

R5 reviewed exact HEAD `e2bb9ea78984878c6e06a9e37946f923032150f9`
and returned `APPROVED_FOR_PROMOTION` with findings `0 / 0 / 0`. Decision 0002
therefore remains the immutable authority for the exact bytes it names. A later
branch review found two numeric-representation gaps in four capability rows and
RFC/evidence support. Corrected current bytes are a candidate only; Decision
0002 explicitly requires a successor owner decision before replacements become
accepted.

## Current row state

| Canonical capability | Current state | Authority |
|---|---|---|
| `synthetic-usage-spine` | `accepted` | Decision 0002 binding remains exact |
| `source-adapter-profiles` | `unknown` | Corrected current bytes await exact-head review and successor decision |
| `event-identity-and-normalization` | `unknown` | Corrected current bytes await exact-head review and successor decision |
| `stream-reconciliation-and-health` | `accepted` | Decision 0002 binding remains exact |
| `durable-local-ledger` | `accepted` | Decision 0002 binding remains exact |
| `quota-snapshot-semantics` | `accepted` | Decision 0002 binding remains exact |
| `local-query-contract` | `accepted` | Decision 0002 binding remains exact |
| `otlp-metrics-projection` | `accepted` | Decision 0002 binding remains exact |
| `postgresql-history-projection` | `unknown` | Corrected current bytes await exact-head review and successor decision |
| `release-profile-governance` | `unknown` | Corrected current bytes await exact-head review and successor decision |
| `portable-runtime-and-release` | `accepted` | Decision 0002 binding remains exact |

Task 2.1 is therefore a hard stop for non-synthetic production work. The seven
unchanged accepted rows do not authorize the four corrected rows, and the four
unknown rows do not revoke or rewrite their accepted predecessors. A fresh
review must approve one exact candidate HEAD before a successor decision may
identify replacement RFC/evidence bytes and replacement bindings for only
those four capabilities.

The R5-accepted predecessor anchors remain RFC 0001
`36c062fa81bfadb5e9b90c0386ae7529579648acf04a165e923adca5e9e03163`,
source/bounds evidence
`2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d`,
synthetic vectors
`8e5e512144e03d437aa0349b7d00b3600fae5dd24e2d613236d6c6e699953e8a`,
and provenance
`dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0`.
The durable
[R1-R5 ledger](../../../about/legends-and-lore/reviews/0001/2026-08-10-specification-reconciliation.md)
records that historical convergence; the pending correction route is recorded
in the
[final-branch correction record](../../../about/legends-and-lore/reviews/0001/2026-08-10-final-branch-correction.md)
so its state cannot be mistaken for R5 acceptance.

This file is only the active change's governance projection. It is not a
runtime or release profile and contains no profile member or value. It records
no implementation, real source, personal data, sink/destination, package,
image, archive, or release authorization. Later work remains governed by the
active tasks, evidence-backed domain profiles, and their subsequent gates.
