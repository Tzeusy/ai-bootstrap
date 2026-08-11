# V1 Capability Contract Acceptance

**Change:** `establish-ai-usage-telemetry-v1`
**Status:** Active change; all eleven current contract rows accepted; not
implemented; not archived
**Owner decisions:**
[Decision 0002](../../../about/heart-and-soul/decisions/0002-accept-v1-capability-contracts.md)
and
[Decision 0003](../../../about/heart-and-soul/decisions/0003-accept-final-branch-contract-corrections.md),
and
[Decision 0004](../../../about/heart-and-soul/decisions/0004-accept-health-summary-contract-correction.md)

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

The current artifact anchors are RFC 0001
`f17a85ddd20c7c3c7998ea2a8d0d2f425b84cc57363ec942f5ea554b8cefaab8`,
source/bounds evidence
`2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d`,
synthetic vectors
`4808a21a78997c7886b220c29f7bb477b6ca6bd604dcb1afd0a8bf95eacc19f6`,
and provenance
`dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0`.
The supporting active OpenSpec design is
`13229d7e540f41dbf23ff8ae741983cbf4af7feebe15aa48391bba4e78afa21f`.
The durable
[R1-R5 ledger](../../../about/legends-and-lore/reviews/0001/2026-08-10-specification-reconciliation.md)
preserves predecessor convergence, while the
[final-branch correction record](../../../about/legends-and-lore/reviews/0001/2026-08-10-final-branch-correction.md)
records the correction and exact-head confirmation; the
[health-summary authority re-sweep](../../../about/legends-and-lore/reviews/0001/2026-08-11-health-summary-authority-resweep.md)
records the later bounded correction.

Decision 0004 accepts the bounded health-summary RFC/evidence/design correction
after independent exact-head semantic and authority review. It does not amend
or replace any of the eleven capability-row bindings above.

The all-accepted composition satisfies one input to task 2.1; it does not mark
that unchecked task complete or authorize later work. This file is only the
active change's governance projection. It is not a runtime or release profile
and contains no profile member or value. It records no implementation, real
source, personal data, sink/destination, package, image, archive, or release
authorization. Later work remains governed by the active tasks, evidence-
backed domain profiles, and their subsequent privacy, runtime, sink, native-
parity, packaging, archive, and release gates.
