# Heart and Soul

Doctrine for **AI Usage Telemetry**, the `ai-usage-telemetry` project nested in
`ai-bootstrap/`.

**Status:** Adopted through Owner Decision 0001. Decision 0002 independently
accepts the eleven downstream v1 capability contracts without amending this
doctrine. See the central [lifecycle matrix](../README.md#lifecycle-status).

Read this pillar first when deciding what the product may observe, retain, or
export; what its first release promises; and which shortcuts would violate its
purpose.

## Reading Order

1. [`vision.md`](./vision.md) — the product thesis, anti-thesis, seven numbered
   principles, and definition of success.
2. [`data-boundaries.md`](./data-boundaries.md) — the constitutional boundary
   between content, metadata, credentials, local history, and optional exports.
3. [`v1.md`](./v1.md) — what the first release ships, defers, targets, and must
   prove before it is considered successful.
4. [`decisions/0001-finalize-and-specify.md`](./decisions/0001-finalize-and-specify.md)
   — the owner's conditional direction and the evidence gates that must activate
   it before doctrine or RFC authority is claimed.
5. [`decisions/0002-accept-v1-capability-contracts.md`](./decisions/0002-accept-v1-capability-contracts.md)
   — the eleven independent exact contract decisions and the profile, runtime,
   archive, and release boundaries that remain.

## Evidence Labels

- **[Observed]** records a claim supported by a pinned client surface, official
  documentation, or public source. Personal session and credential records are
  not project evidence. An observed format is not a promise that an upstream
  tool will never change.
- **[Inferred]** records the evidentiary origin of a product/design conclusion.
  Inside this adopted pillar it is authoritative unless a later owner decision
  amends it; the label does not claim that implementation has proved it.
- **[Unknown]** records behavior that remains unresolved, especially for
  deferred or future tools. Unknown behavior must not be disguised as a stable
  contract.

Design contracts belong in `about/legends-and-lore/`; testable requirements
belong in `openspec/`; component and deployment maps belong in
`about/lay-and-land/`; implementation-quality standards belong in
`about/craft-and-care/`.
