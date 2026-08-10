# RFC 0001 R4 Quality-Evidence Re-sweep

**Date:** 2026-08-10
**Exact input commit:** `4de3697c1d61d4bc3404105c7771ae0ce2336bfd`
**Authority:** Owner Decision 0001 standing authorization for reviewed
specification-authoring and quality-gate fixes
**Result:** Pre-fix evidence annexes re-accepted for the reviewed input;
bounded corrections applied as a candidate requiring fresh R5 confirmation

## Scope and authority boundary

An independent full R4 re-sweep reviewed the exact input HEAD above, including
the current RFC, evidence annexes, design, all eleven capability specifications,
and the task graph. The sweep operated under
[Owner Decision 0001](../../../heart-and-soul/decisions/0001-finalize-and-specify.md),
which already authorizes reviewed quality-gate corrections in the adopted
documentation/specification scope. Recording this review is authority
bookkeeping, not a new user policy.

R4 does not owner-accept any capability, satisfy the remaining improvement
cycles, authorize implementation, activate a source/profile, permit a personal
mount or real sink, or claim runtime/release evidence.

## Evidence digest trail

The original formal-review digests remain historical acceptance records. R4
re-read the later pre-fix annex bytes at the exact input commit and re-accepted
them as bounded RFC quality-evidence annexes:

| Artifact state | RFC 0001 SHA-256 | Source/bounds SHA-256 | Synthetic vectors SHA-256 | Authority |
|---|---|---|---|---|
| Original formal-review set | `f2ad18746a60db8cc9435aabca6c81a62017e0fd7e86275bc564c57731d88526` | `5401c9fb0e621af6f35385f89f9cc2cc1d260a3a2119c457ba9e27784e787a1e` | `1b284a304d604fb01d83cb1faab57a5f33a9e62749913abd9c5e93ab3193918e` | Historical formal acceptance |
| Exact R4 reviewed input | `ca548d5cb5070c5e288e66d3fe97a3c0f662cd245bd7153ae640d2ed593dcbc2` | `219531d0f87145c6722d66ccb5de7abdaf3306daecd2fdd717a32a76b2d701df` | `c10308d1bbb75f52d5000f51b23f3cd4733bc38fe6d429a2fb7580292e743372` | Source/bounds and synthetic annexes re-accepted under standing owner authority; RFC remains the accepted R3 input anchor |
| R4-corrected candidate | `36c062fa81bfadb5e9b90c0386ae7529579648acf04a165e923adca5e9e03163` | `2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d` | `8e5e512144e03d437aa0349b7d00b3600fae5dd24e2d613236d6c6e699953e8a` | **Pending fresh R5 confirmation; not yet accepted** |

The later pre-fix annex hashes differ from the original formal-review set
because the intervening reconciliations made prior rules executable rather than
changing doctrine: R1 closed the three atomic zero-fact/no-skip dispositions;
R2 added two-sided canaries and mutation controls, deterministic parser
precedence and limits, persistent independent latches, exact timestamp and SQL
constraint evidence, and clause-level traceability; R3 clarified dependency
ownership without changing those behaviors. R4 reviewed those accumulated
bytes rather than silently replacing their historical trail.

## Bounded findings and corrections

| R4 finding | Candidate correction |
|---|---|
| Safe cursor invalidation said it added no degradation but could incorrectly report healthy while coverage, reconciliation, or storage was already latched. | RFC/design/spec/vector/task now say invalidation adds no latch, clears none, preserves the prior `LatchSet` and sibling evidence, derives the highest active state, and reports healthy only when no latch remains; the overlap vector fixes coverage + reconciliation + storage as the proof case. |
| Codex `state_only` admitted an object whenever no window had complete utilization, allowing a malformed present window to be consumed. | `state_only` now requires no registered primary/secondary window object (apart from exact allowed identity/context members); any present registered window with missing, mistyped, or out-of-range utilization is whole-record `recognized_malformed` with same-record rollback. Separate absent, identity-only, missing, mistyped, and out-of-range vectors/tasks close the boundary. |
| The legibility task said “under ten minutes,” while the capability spec used “within ten minutes,” and neither explained the launch instrument's 15-minute ceiling. | RFC/design/spec/evidence/task now use inclusive `elapsed_time <= 10 minutes` and state that this capability target deliberately tightens, rather than contradicts or amends, the immutable 15-minute sitting ceiling. |
| The current lifecycle route did not distinguish accepted historical/pre-fix evidence from newly corrected bytes awaiting confirmation. | This record plus the central and legends-and-lore navigation preserve every historical digest, identify the exact R4 input, and mark the corrected hashes as pending R5. |

## Required R5 confirmation

The bounded corrections changed the RFC and both evidence-annex byte streams,
so R4 cannot pre-accept their new digests. A fresh independent R5 pass must
review the exact candidate bytes, re-run the full semantic and mechanical gates,
and report no remaining blocker before Owner Decision 0001 and the central
lifecycle anchor may promote the candidate hashes to accepted. Until then the
R3 RFC remains the last accepted RFC anchor, the R4-reviewed pre-fix annexes
remain the last accepted evidence bytes, and current corrected bytes are
explicitly pending.

## R5 confirmation and promotion

A fresh R5 pass reviewed exact HEAD
`e2bb9ea78984878c6e06a9e37946f923032150f9`, including the exact corrected RFC,
evidence annexes, design, eleven capability specifications, and task graph. It
re-ran the semantic and mechanical gates and returned
`APPROVED_FOR_PROMOTION` with findings `0 / 0 / 0`.

The R4-corrected candidate row above is therefore promoted without rewriting
its pre-R5 history: RFC 0001
`36c062fa81bfadb5e9b90c0386ae7529579648acf04a165e923adca5e9e03163`,
source/bounds evidence
`2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d`,
synthetic vectors
`8e5e512144e03d437aa0349b7d00b3600fae5dd24e2d613236d6c6e699953e8a`,
and unchanged provenance
`dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0`
are the current accepted review anchors. The complete cycle ledger is
[`2026-08-10-specification-reconciliation.md`](./2026-08-10-specification-reconciliation.md),
and the eleven independent capability-contract decisions are recorded in
[Owner Decision 0002](../../../heart-and-soul/decisions/0002-accept-v1-capability-contracts.md).

This confirmation changes only the authority state of the exact reviewed
bytes. It does not implement a capability, activate or invent a release-profile
member, permit a real mount or destination, archive the active change, or
authorize packaging, publication, or release.
