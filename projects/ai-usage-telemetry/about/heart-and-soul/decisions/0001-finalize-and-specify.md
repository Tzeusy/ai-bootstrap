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
`90f85ab1e5c50ee28ad51f6efeae3245f9908187985c2a12e1ba237db49f3f11`
and adopts the governance-lifecycle standard at
`a825da14231c0863ca14b5bb2f5785c8c46cb6bc063120cced7d716dc053b2bc`.
It preserves the original privacy, retention, source, sink, and release gates.
Parameters v1.2 still require their own review, and OpenSpec remains blocked
until a later named-commit administration records `READY`.

## Specification-Authoring Erratum Acceptance

During first-spec authoring, the mount-contract crosswalk found that RFC 0001
still said `four` canonical filesystem targets after the accepted privacy
remediation had removed the rejected Claude quota-cache row. Repository history,
the current three-row source/state table, V1 scope, and deployment topology make
the intended contract unambiguous.

The reviewed correction says `three canonical source/state` targets and
clarifies that read-only TOML is a separate configuration surface while `/tmp`
is ephemeral scratch. It does not add a mount, authorize Claude quota, change
doctrine, or alter the READY decision. The durable review is
[`../../legends-and-lore/reviews/0001/2026-08-10-specification-erratum-review.md`](../../legends-and-lore/reviews/0001/2026-08-10-specification-erratum-review.md).

Under this decision's standing direction to apply reviewed quality-gate fixes
before publication, the accepted RFC 0001 digest is now
`126fc0214abb76f1a2f207bed1c3baf629757a3b281abf9d0e4a92b52b7e0117`.

## R1 Reconciliation Clarification

Under this decision's standing authorization for specification authoring and
quality-gate fixes, R1 reconciliation makes the existing atomic/no-skip rule
exact: only the code/profile-registered dispositions `registered_irrelevant`,
`context_only`, and `quota_state_only` may advance a complete record with zero
usage or quota facts, and only when their permitted parser-context or
quota-component transition and cursor commit atomically in the same ledger
transaction. Unknown, unregistered, malformed, collided, or failed records
still hold before the record. This clarification preserves the adopted thesis,
privacy and retention boundaries, and no-skip rule; it does not owner-accept any
capability, waive the four required improvement cycles, or authorize
implementation before the active change's conditional acceptance gates pass.

The reconciled RFC 0001 digest is
`4523cdc1fbc9cd3e80b04f4c08c098312dfd6cac2a4f472cd95cb8aeb496daef`.

## R2 Reconciliation Clarification

Under the same standing authorization, R2 reconciliation closes SQL-certain
PostgreSQL child linkage, persistent independent SQLite health latches and
`STRICT` storage typing, deterministic parser failure precedence, global source-
namespace uniqueness, exact working-directory-basename attribution, checked
Unix-nanosecond timestamp and age arithmetic, two-sided privacy/capture canary
evidence, clause-level executable traceability, and the complete three-way
zero-fact inventory. These corrections make existing safety and accounting
claims testable without changing doctrine, accepting a capability, waiving an
evidence gate, or authorizing personal mounts or real destinations.

The R2-reconciled RFC 0001 digest is
`d865e6971c5ab56af5791007cefc73f53cb4d15d57ff898f61745e4f479c7b30`.

## R3 Dependency-Hygiene Clarification

Under the same standing authorization, R3 reconciliation makes the accepted
dependency direction explicit without changing behavior. Source-independent
domain interfaces own normalized facts, identity, canonical instant and cwd-
basename primitives, categories, fingerprints, and age; adapters supply source
fields/evidence and depend on those interfaces. Runtime alone yields
`ValidatedSourceHandle`, storage alone yields `AdmissionDecision`, generic
stream discovery owns stay-beneath traversal/generation, stream health alone
owns pure `LatchSet`, and the ledger persists state and exposes
`LedgerProjectionReader` directly to sinks while public views remain a separate
local-query branch. The task graph now orders domain before adapters and stream-
health policy before ledger persistence, with fake lower-provider interfaces
keeping adapters testable before concrete providers. These corrections preserve
R2 privacy, SQL, latch, timestamp, canary, traceability, and zero-fact evidence
semantics; they do not accept a capability, waive an evidence gate, or authorize
personal mounts or real destinations.

The R3-reconciled RFC 0001 digest is
`ca548d5cb5070c5e288e66d3fe97a3c0f662cd245bd7153ae640d2ed593dcbc2`.

## R4 Quality-Evidence Re-sweep and Candidate Corrections

Under this decision's explicit standing authorization for reviewed
specification-authoring and quality-gate fixes, an independent full R4 re-sweep
reviewed exact input HEAD
`4de3697c1d61d4bc3404105c7771ae0ce2336bfd`. It re-accepted the then-current
source/bounds evidence annex at
`219531d0f87145c6722d66ccb5de7abdaf3306daecd2fdd717a32a76b2d701df`
and synthetic-vector annex at
`c10308d1bbb75f52d5000f51b23f3cd4733bc38fe6d429a2fb7580292e743372`
as quality evidence for the reviewed R3 input. The initial formal-review hashes
above remain historical records; the later annex bytes incorporate the R1/R2
zero-fact, canary, parser, latch, timestamp, SQL, and traceability corrections,
plus R3 dependency-ownership clarification.

R4 found and bounded four corrections: safe cursor invalidation must preserve
the prior `LatchSet` and derive its highest active state; Codex `state_only`
requires no registered primary/secondary window while any malformed present
window holds the whole record; the capability legibility boundary is inclusive
`elapsed_time <= 10 minutes` and deliberately tighter than the immutable launch
instrument's 15-minute sitting ceiling; and current-versus-historical evidence
authority must remain explicit. The durable record is
[`../../legends-and-lore/reviews/0001/2026-08-10-r4-quality-evidence-resweep.md`](../../legends-and-lore/reviews/0001/2026-08-10-r4-quality-evidence-resweep.md).

Those corrections changed the reviewed bytes. Their current candidate digests
are RFC 0001
`36c062fa81bfadb5e9b90c0386ae7529579648acf04a165e923adca5e9e03163`,
source/bounds evidence
`2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d`,
and synthetic vectors
`8e5e512144e03d437aa0349b7d00b3600fae5dd24e2d613236d6c6e699953e8a`.
They are **pending a fresh independent R5 confirmation and are not yet
accepted**. Until R5 passes, the R3 RFC and R4-reviewed pre-fix annexes remain
the latest accepted authorities. This record does not accept a capability,
waive any improvement/evidence gate, authorize implementation, or permit real
mounts, sinks, packaging, or release.

## R5 Confirmation and Promotion

A fresh R5 pass reviewed exact HEAD
`e2bb9ea78984878c6e06a9e37946f923032150f9`, re-ran the full semantic and
mechanical gates against the R4-corrected bytes, and returned
`APPROVED_FOR_PROMOTION` with findings `0 / 0 / 0`. Under this decision's
standing explicit direction, the promoted accepted digests are now RFC 0001
`36c062fa81bfadb5e9b90c0386ae7529579648acf04a165e923adca5e9e03163`,
source/bounds evidence
`2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d`,
synthetic vectors
`8e5e512144e03d437aa0349b7d00b3600fae5dd24e2d613236d6c6e699953e8a`,
and unchanged provenance
`dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0`.

The durable R1-R5 trail is
[`../../legends-and-lore/reviews/0001/2026-08-10-specification-reconciliation.md`](../../legends-and-lore/reviews/0001/2026-08-10-specification-reconciliation.md).
The owner's independent acceptance of the eleven exact capability-contract
rows is recorded separately in
[Decision 0002](./0002-accept-v1-capability-contracts.md). Neither promotion
nor contract acceptance supplies unmeasured profile values or runtime/release
evidence, and neither authorizes real mounts, non-synthetic facts, real sinks,
production packaging, archival, or release outside the later active-task and
profile gates.
