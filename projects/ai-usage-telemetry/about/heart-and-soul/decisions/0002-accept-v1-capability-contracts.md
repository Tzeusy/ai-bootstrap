# Decision 0002: Accept the V1 Capability Contracts

**Status:** Activated owner decision
**Owner:** Tze, repository owner
**Date:** 2026-08-10

## Authority and reviewed basis

Owner Decision 0001 records the owner's standing explicit direction to proceed
from a named-commit `READY` launch gate through task-plan review, at least four
improvement cycles, and convergence before promotion. The launch gate recorded
`READY`; the task-plan review concluded separately; R1 through R4 applied bounded
corrections; and R5 reviewed exact HEAD
`e2bb9ea78984878c6e06a9e37946f923032150f9` with result
`APPROVED_FOR_PROMOTION` and findings `0 / 0 / 0`.

The promoted reviewed artifact set is:

| Artifact | SHA-256 |
|---|---|
| RFC 0001 | `36c062fa81bfadb5e9b90c0386ae7529579648acf04a165e923adca5e9e03163` |
| Source/bounds evidence | `2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d` |
| Synthetic vector contract | `8e5e512144e03d437aa0349b7d00b3600fae5dd24e2d613236d6c6e699953e8a` |
| Content-safe provenance | `dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0` |

The durable R1-R5 evidence trail is the
[specification-reconciliation ledger](../../legends-and-lore/reviews/0001/2026-08-10-specification-reconciliation.md).

## Independent capability decisions

Each row is an independent decision about only the named capability contract.
The SHA-256 column binds that row to the current `spec.md` bytes reviewed at the
exact R5 HEAD; it is not a digest of this external decision record.

| Canonical capability | State | Current `spec.md` SHA-256 binding |
|---|---|---|
| `synthetic-usage-spine` | `accepted` | `fc05078b0f616954b090ba24b1e272646bc6f8cae0f1752745885687eccd3584` |
| `source-adapter-profiles` | `accepted` | `4674c0e8c2abd7b4bb3d57f1d4b9978081b56f32a524855cef055908b5027c16` |
| `event-identity-and-normalization` | `accepted` | `36903a868d9f842b1dc959d30518d2834d2c1d50b317f7e3a2bb53fe2f54c5be` |
| `stream-reconciliation-and-health` | `accepted` | `9ab1d97d3f25418bb2954495ba55443c36a0ca9d609d1d0274162d123d8a0af9` |
| `durable-local-ledger` | `accepted` | `89de679c4983d0b48cc85c11d212b8383f2cc658a762328c58a6b1ef91fab988` |
| `quota-snapshot-semantics` | `accepted` | `c18379dea24116144f837f7873b4ecca6bdc40377796c19de10686b793c9c464` |
| `local-query-contract` | `accepted` | `f1f5ebcae0a0c29c4dbdec0f98c6afa0da8d65ac2d27cf1b79a380ca0e14f22a` |
| `otlp-metrics-projection` | `accepted` | `2356bd1d02b19ce9ec88ccc99e6debdbffcf64c05aa58fe2816697fa25f74359` |
| `postgresql-history-projection` | `accepted` | `6480a3b2d2dd73036e2e602cce616e1e57064113a12c77de717c147adcb91e4d` |
| `release-profile-governance` | `accepted` | `0702f0a1295840cfd553158030c6b2d5c491a8ce5d7a8d6ad4079f10614b9e8b` |
| `portable-runtime-and-release` | `accepted` | `71c524a319a58d2f94b76e0c206bf997c92a832ec115c74b4c342fee413c9aad` |

Each row remains independently amendable or rejectable only by a successor
owner decision that identifies the affected capability and replacement bytes.
No change to one row changes a sibling row implicitly.

## Acceptance boundary

This decision accepts the eleven testable contracts, not their collapse into
one all-or-nothing row and not evidence that any contract has been implemented.
It permits later implementation planning and execution only through the active
OpenSpec tasks and the evidence-backed profiles and gates those tasks require.

It does not accept or invent any unmeasured release-profile member or value,
activate a profile, authorize a real source mount, admit a non-synthetic or
personal-data fact, open a real sink or destination, create a production
package or image, archive the active change, or authorize a release or
publication.

Before any non-synthetic runtime path may operate, all eleven exact decision
entries above must remain present and digest-valid, every applicable domain
profile must be active and backed by its required measured evidence, and every
later task, privacy, runtime, sink, native-parity, and release-evidence gate must
pass. Configuration and profile composition cannot waive those conditions.
