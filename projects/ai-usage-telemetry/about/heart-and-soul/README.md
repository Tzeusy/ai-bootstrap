# Heart and Soul

Doctrine for **AI Usage Telemetry**, the `ai-usage-telemetry` project nested in
`ai-bootstrap/`.

**Status:** Draft, pending explicit human-owner adoption. See the central
[lifecycle matrix](../README.md#lifecycle-status).

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

## Evidence Labels

- **[Observed]** records a claim supported by formats inspected on a real local
  installation. An observed format is evidence, not a promise that an upstream
  tool will never change.
- **[Inferred]** records a proposed product or design conclusion drawn from the
  observed evidence and owner interview. It is not adopted doctrine.
- **[Unknown]** records behavior that remains unresolved, especially for
  deferred or future tools. Unknown behavior must not be disguised as a stable
  contract.

Design contracts belong in `about/legends-and-lore/`; testable requirements
belong in `openspec/`; component and deployment maps belong in
`about/lay-and-land/`; implementation-quality standards belong in
`about/craft-and-care/`.
