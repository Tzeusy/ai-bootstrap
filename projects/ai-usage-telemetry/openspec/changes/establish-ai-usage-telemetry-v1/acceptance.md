# V1 Capability Contract Acceptance

**Change:** `establish-ai-usage-telemetry-v1`
**Status:** Active change; all eleven current contract rows accepted; not
implemented; not archived
**Owner decisions:**
[Decision 0002](../../../about/heart-and-soul/decisions/0002-accept-v1-capability-contracts.md)
and
[Decision 0003](../../../about/heart-and-soul/decisions/0003-accept-final-branch-contract-corrections.md)

R5 approved the Decision 0002 contract set at exact HEAD
`e2bb9ea78984878c6e06a9e37946f923032150f9`. A later final-branch review found
bounded numeric/time representation gaps in four rows. The corrected candidate
was reviewed at exact clean HEAD
`5ec37f50de23c4eb36177ba8742ae9db54cdaf94` and returned
`APPROVED_FOR_PROMOTION` with findings `0 / 0 / 0`. Decision 0003 replaces only
those four bindings and promotes the corrected RFC/synthetic bytes.

## Current row state

| Canonical capability | Current state | Authority |
|---|---|---|
| `synthetic-usage-spine` | `accepted` | Decision 0002 exact binding |
| `source-adapter-profiles` | `accepted` | Decision 0003 corrected binding |
| `event-identity-and-normalization` | `accepted` | Decision 0003 corrected binding |
| `stream-reconciliation-and-health` | `accepted` | Decision 0002 exact binding |
| `durable-local-ledger` | `accepted` | Decision 0002 exact binding |
| `quota-snapshot-semantics` | `accepted` | Decision 0002 exact binding |
| `local-query-contract` | `accepted` | Decision 0002 exact binding |
| `otlp-metrics-projection` | `accepted` | Decision 0002 exact binding |
| `postgresql-history-projection` | `accepted` | Decision 0003 corrected binding |
| `release-profile-governance` | `accepted` | Decision 0003 corrected binding |
| `portable-runtime-and-release` | `accepted` | Decision 0002 exact binding |

The composed current set is seven unchanged Decision 0002 rows plus four
Decision 0003 replacements. Every row remains independent and exact-byte
bound. No sibling was implicitly amended, and a later replacement still
requires a successor owner decision naming that row and its new bytes.

The last accepted artifact anchors are RFC 0001
`1ffe8e796372ff56bdd7e81be4c25fdbf726fb51585cf53041e027857b6a5593`,
source/bounds evidence
`2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d`,
synthetic vectors
`f78ece2be675b40ea0b0ae7efe20add6c3ab5036e419fa2d5ccc656842a94871`,
and provenance
`dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0`.
The durable
[R1-R5 ledger](../../../about/legends-and-lore/reviews/0001/2026-08-10-specification-reconciliation.md)
preserves predecessor convergence, while the
[final-branch correction record](../../../about/legends-and-lore/reviews/0001/2026-08-10-final-branch-correction.md)
records the correction and exact-head confirmation.

The bounded health-summary RFC/evidence candidate is **[Unknown]** until a
fresh independent exact-head review and successor owner decision bind its new
bytes. It does not amend or replace any of the eleven capability-row bindings
above.

The all-accepted composition satisfies one input to task 2.1; it does not mark
that unchecked task complete or authorize later work. This file is only the
active change's governance projection. It is not a runtime or release profile
and contains no profile member or value. It records no implementation, real
source, personal data, sink/destination, package, image, archive, or release
authorization. Later work remains governed by the active tasks, evidence-
backed domain profiles, and their subsequent privacy, runtime, sink, native-
parity, packaging, archive, and release gates.
