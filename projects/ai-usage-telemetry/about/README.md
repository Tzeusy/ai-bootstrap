# AI Usage Telemetry Project Shape

This directory is the project-level source of truth for **AI Usage
Telemetry**, a portable local service that turns usage facts already written by
AI coding tools into a durable, content-free history.

It lives in the parent repository's `projects/` layer. The parent
[`about/README.md`](../../../about/README.md) governs the surrounding
`ai-bootstrap` harness; this product's own `about/` and active child OpenSpec
change govern AI Usage Telemetry behavior.

The project is still pre-implementation. Statements about current tool file
formats are marked **[Observed]**; proposed architectural conclusions are marked
**[Inferred]**; unsupported future-tool behavior is marked **[Unknown]**. The
documents distinguish the adopted pre-implementation baseline from any
explicitly labeled amendment under review; neither is a claim that the service
already exists or that its release evidence is complete.

## Lifecycle Status

This matrix is the central status record for the project-shape artifacts. A
lower-layer document cannot make a higher-layer draft authoritative. Every
state claim carries the project's epistemic label: `[Observed]` requires a
named-commit tree sweep, accepted digest, or linked decision/review; when
state-bearing bytes change without that evidence, the claim becomes `[Unknown]`
until it is reswept.

| Artifact | Status | Next authority gate |
|---|---|---|
| Heart-and-soul doctrine | **[Observed] Adopted** | Owner Decision 0001 remains authoritative; Decisions 0002 and 0003 accept downstream contracts without amending doctrine |
| RFC 0001 | **[Observed] Accepted corrected bytes** | Decision 0003 binds the exact current RFC; implementation and release evidence remain absent |
| Lay-and-land topology | **[Observed] Accepted** | Current accepted map; implementation evidence remains absent |
| Craft-and-care standards | **[Observed] Adopted** | Governs specification and later implementation work |
| OpenSpec capability specifications | **[Observed] All eleven current rows accepted** | Seven exact Decision 0002 bindings plus four Decision 0003 replacements; active tasks and every later evidence gate remain |

**R5-accepted predecessor shape/evidence anchor:** R5 reviewed exact HEAD
`e2bb9ea78984878c6e06a9e37946f923032150f9` and returned
`APPROVED_FOR_PROMOTION` with findings `0 / 0 / 0`. The accepted RFC is
`36c062fa81bfadb5e9b90c0386ae7529579648acf04a165e923adca5e9e03163`;
source/bounds evidence is
`2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d`;
synthetic vectors are
`8e5e512144e03d437aa0349b7d00b3600fae5dd24e2d613236d6c6e699953e8a`;
and provenance is
`dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0`.

**Final correction promotion:** a final branch review found numeric
serialization and PostgreSQL timestamp-precision gaps after Decision 0002. A
fresh confirmation reviewed exact clean HEAD
`5ec37f50de23c4eb36177ba8742ae9db54cdaf94` and returned
`APPROVED_FOR_PROMOTION` with findings `0 / 0 / 0`. Decision 0003 binds the
corrected RFC at
`1ffe8e796372ff56bdd7e81be4c25fdbf726fb51585cf53041e027857b6a5593`,
synthetic vectors at
`f78ece2be675b40ea0b0ae7efe20add6c3ab5036e419fa2d5ccc656842a94871`,
and exactly four corrected capability rows. The other seven current
specifications still match Decision 0002 exactly.

**Historical predecessor anchor:** R3 RFC
`ca548d5cb5070c5e288e66d3fe97a3c0f662cd245bd7153ae640d2ed593dcbc2`;
R4-reviewed pre-fix source/bounds evidence
`219531d0f87145c6722d66ccb5de7abdaf3306daecd2fdd717a32a76b2d701df`;
R4-reviewed pre-fix synthetic vectors
`c10308d1bbb75f52d5000f51b23f3cd4733bc38fe6d429a2fb7580292e743372`;
and unchanged provenance
`dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0`.
See the
[R4 quality-evidence re-sweep](./legends-and-lore/reviews/0001/2026-08-10-r4-quality-evidence-resweep.md)
for the pre-R5 history and confirmation append, and the
[R1-R5 reconciliation ledger](./legends-and-lore/reviews/0001/2026-08-10-specification-reconciliation.md)
for the complete convergence trail and the
[final-branch correction record](./legends-and-lore/reviews/0001/2026-08-10-final-branch-correction.md)
for the correction hashes and exact-head confirmation. See
[Owner Decision 0001](./heart-and-soul/decisions/0001-finalize-and-specify.md)
for the standing direction and
[Owner Decision 0002](./heart-and-soul/decisions/0002-accept-v1-capability-contracts.md)
for the original eleven independent contract decisions and
[Owner Decision 0003](./heart-and-soul/decisions/0003-accept-final-branch-contract-corrections.md)
for the four exact replacements.
The pre-specification instrument is bound in
[`parameters.md`](../docs/launch-gate/parameters.md), and the named-commit
[`READY` administration](../docs/launch-gate/2026-08-10-96ba99d.md) has been
recorded. R1-R4 improvement and R5 confirmation are complete. The active
OpenSpec change remains the implementation route: follow its
[`proposal`](../openspec/changes/establish-ai-usage-telemetry-v1/proposal.md) →
[`design`](../openspec/changes/establish-ai-usage-telemetry-v1/design.md) →
[`specifications`](../openspec/changes/establish-ai-usage-telemetry-v1/specs/) →
[`acceptance`](../openspec/changes/establish-ai-usage-telemetry-v1/acceptance.md) →
[`tasks`](../openspec/changes/establish-ai-usage-telemetry-v1/tasks.md) route.
Contract acceptance permits later implementation planning and execution only
through those active tasks and their evidence-backed domain profiles. It does
not mark implementation complete, activate a profile, archive the change, or
authorize real mounts, sinks, packaging, or release. Historical reviews and
administrations remain off the default reading path except for the R1-R5 ledger
and final-branch correction record.

## Tooling Scope

Run OpenSpec commands from `projects/ai-usage-telemetry`; root-level OpenSpec
commands intentionally discover the `ai-bootstrap` repository-shape change
instead. For this product's active change, use:

```bash
cd projects/ai-usage-telemetry
openspec validate --all --strict
```

The current implementation sequence and Tokscale comparative-evidence
disposition are recorded in the
[`2026-08-10 Tokscale-informed project direction`](../docs/direction/2026-08-10-tokscale-informed.md).
That planning record changes no accepted RFC, evidence, decision, or capability
bytes; its bounded source-semantics gate must return through the amendment and
successor-decision route if producer evidence contradicts the current contract.

## The Four `about/` Pillars

| Pillar | Question | Start here |
|---|---|---|
| [Heart and Soul](./heart-and-soul/README.md) | Why does this exist, and what must it never become? | `vision.md`, `data-boundaries.md`, then `v1.md` |
| [Craft and Care](./craft-and-care/README.md) | What evidence and engineering posture does a safe change require? | `engineering-bar.md` |
| [Legends and Lore](./legends-and-lore/README.md) | How do adapters, durable state, and sinks behave? | RFC 0001 |
| [Lay and Land](./lay-and-land/README.md) | Where do components, data, and trust boundaries live? | `components.md`, then `data-flow.md` |

[Observed] Capability specifications are the fifth project-shape pillar. The
project-direction launch gate recorded `READY` at a named commit, and the active
`establish-ai-usage-telemetry-v1` change now contains eleven authored capability
specifications. Decision 0002 independently accepted each exact R5 contract
row; seven current rows still match it, while Decision 0003 accepts the four
corrected replacements. Neither contract decision claims that any capability
has been implemented or that an unmeasured release profile, real resource,
archive, or release is valid.

## Recommended Reading Order

1. [`heart-and-soul/vision.md`](./heart-and-soul/vision.md) for the thesis,
   non-goals, and seven non-negotiable principles.
2. [`heart-and-soul/data-boundaries.md`](./heart-and-soul/data-boundaries.md)
   before making any collection, metadata, or export decision.
3. [`heart-and-soul/v1.md`](./heart-and-soul/v1.md) for the first-release
   boundary.
4. [`craft-and-care/engineering-bar.md`](./craft-and-care/engineering-bar.md)
   before planning implementation.
5. [`legends-and-lore/rfcs/0001-adapter-ledger-and-sink-contract.md`](./legends-and-lore/rfcs/0001-adapter-ledger-and-sink-contract.md)
   for the foundational design contract.
6. [`lay-and-land/data-flow.md`](./lay-and-land/data-flow.md) and
   [`lay-and-land/deployment.md`](./lay-and-land/deployment.md) to see the
   contract spatially.
7. [`heart-and-soul/decisions/0002-accept-v1-capability-contracts.md`](./heart-and-soul/decisions/0002-accept-v1-capability-contracts.md),
   [`heart-and-soul/decisions/0003-accept-final-branch-contract-corrections.md`](./heart-and-soul/decisions/0003-accept-final-branch-contract-corrections.md),
   and the active change's
   [`acceptance.md`](../openspec/changes/establish-ai-usage-telemetry-v1/acceptance.md)
   for the exact contract decisions and their remaining boundary.

## Authority and Change

- Heart-and-soul doctrine is owner-adopted through Decision 0001.
- R5 promoted the predecessor RFC/evidence bytes under Decision 0001's standing
  direction; Decision 0003 promotes the reviewed corrected RFC and synthetic-
  vector bytes while retaining unchanged source/provenance authority.
- Topology and craft-and-care derive authority from that doctrine and RFC; they
  do not override them.
- Decision 0002 independently accepts the eleven exact R5 capability contracts;
  Decision 0003 replaces exactly four corrected rows. All eleven current rows
  are accepted, but task 2.1 remains unchecked, the OpenSpec change remains
  active, and implementation, archival, and release retain their later gates.
