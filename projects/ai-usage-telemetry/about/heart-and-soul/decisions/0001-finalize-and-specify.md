# Decision 0001: Finalize the Shape and Proceed to Specifications

**Status:** Activated owner decision  
**Owner:** Tze, repository owner  
**Date:** 2026-08-10

## Direction

The owner directed the project to finish and finalize the AI Usage Telemetry
project shape, then use `th-projects` project-direction to create specifications,
run at least four `th-projects`/`th-engineering` improvement cycles, and merge
the converged result into `ai-bootstrap` `main`.

This is a standing conditional direction, not a claim that the initial Draft was
already adopted or technically correct. It authorizes evidence gathering,
revision, independent formal review, launch-gate administration, specification
authoring, quality-gate fixes, and publication within that scope.

## Activation conditions

The direction activates doctrine adoption and RFC acceptance only when all of
the following are recorded against the same candidate shape:

1. source and resource-bound evidence is content-safe and has no unresolved
   acceptance blocker;
2. formal privacy, accounting, operations, and lifecycle review records every
   finding and disposition;
3. all blocking findings are fixed or explicitly returned to the owner rather
   than waived by an agent; and
4. the final accepted digest/commit is recorded in this decision and the central
   lifecycle matrix.

After activation, project-direction may administer its launch gate and author
OpenSpec. A gate verdict still cannot be invented or waived by this decision.
Implementation is outside this documentation/specification decision unless a
later signed-off plan authorizes it.

## Reopen conditions

Return to the owner instead of activating this decision if review requires any
of the following:

- prompt, response, tool-call, or credential collection;
- credential-backed vendor quota access;
- automatic deletion or aggregate-only replacement of accepted local history;
- removal of one of the two stated v1 architecture targets; or
- a product thesis materially different from durable, content-free local usage
  history.

## Activation record

The conditions were satisfied on 2026-08-10. Formal privacy/source,
accounting/operations, and lifecycle/documentation lanes recorded all findings,
applied fixes, and passed confirming review. The durable review is
[`../../legends-and-lore/reviews/0001/2026-08-10-formal-rfc-review.md`](../../legends-and-lore/reviews/0001/2026-08-10-formal-rfc-review.md).

Accepted artifact digests:

| Artifact | SHA-256 |
|---|---|
| RFC 0001 | `f2ad18746a60db8cc9435aabca6c81a62017e0fd7e86275bc564c57731d88526` |
| Source/bounds evidence | `5401c9fb0e621af6f35385f89f9cc2cc1d260a3a2119c457ba9e27784e787a1e` |
| Synthetic vector contract | `1b284a304d604fb01d83cb1faab57a5f33a9e62749913abd9c5e93ab3193918e` |
| Content-safe provenance | `dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0` |

This activation adopts the heart-and-soul doctrine, accepts RFC 0001 and its
reconciled topology/craft standards, and authorizes project-direction launch-
gate administration. It does not claim the service exists, accept an unmeasured
release profile, declare the launch gate `READY`, authorize implementation
without signed-off specifications, or waive any release evidence.

## Launch-Gate Remediation Acceptance

The first administration at `389c4aa` returned `NOT READY`. Under the owner's
standing direction to revise, review, and converge the shape before
specification, the project corrected only the design/governance boundaries; it
did not amend doctrine. An initial repair was rejected, followed by a fresh
`PASS` and separate confirming `PASS` at `6f70949`. The durable review is
[`../../legends-and-lore/reviews/0001/2026-08-10-launch-gate-remediation-review.md`](../../legends-and-lore/reviews/0001/2026-08-10-launch-gate-remediation-review.md).

This decision accepts the clarified RFC 0001 at
`9982a289e20555b8abaf668a1832ae378fa14d23f006bb27efcc25bb5c88e52e`
and adopts the governance-lifecycle standard at
`a825da14231c0863ca14b5bb2f5785c8c46cb6bc063120cced7d716dc053b2bc`.
It preserves the original privacy, retention, source, sink, and release gates.
Parameters v1.2 still require their own review, and OpenSpec remains blocked
until a later named-commit administration records `READY`.
