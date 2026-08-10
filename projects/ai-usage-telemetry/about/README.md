# AI Usage Telemetry Project Shape

This directory is the project-level source of truth for **AI Usage
Telemetry**, a portable local service that turns usage facts already written by
AI coding tools into a durable, content-free history.

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
| Heart-and-soul doctrine | **[Observed] Adopted** | Owner Decision 0001 remains authoritative; Decision 0002 accepts downstream contracts without amending doctrine |
| RFC 0001 | **[Unknown] Corrected current bytes pending exact-head review** | The R5-accepted predecessor remains authoritative until a successor owner decision binds the replacement |
| Lay-and-land topology | **[Observed] Accepted** | Current accepted map; implementation evidence remains absent |
| Craft-and-care standards | **[Observed] Adopted** | Governs specification and later implementation work |
| OpenSpec capability specifications | **[Unknown] Seven current rows accepted; four corrected rows pending** | Decision 0002 remains exact for unchanged rows and predecessor bytes; task 2.1 stops non-synthetic work until a successor decision binds the four replacements |

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

**Current correction state:** a final branch review found numeric serialization
and PostgreSQL timestamp-precision gaps after Decision 0002. The current RFC,
synthetic vectors, and four affected capability specifications contain bounded
candidate corrections, but they are `[Unknown]` until a fresh exact-head review
passes and a successor owner decision binds their hashes. The other seven
current specifications still match Decision 0002 exactly. No non-synthetic
production task may pass task 2.1 while any current row is unknown.

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
for the current pending hashes and required confirmation. See
[Owner Decision 0001](./heart-and-soul/decisions/0001-finalize-and-specify.md)
for the standing direction and
[Owner Decision 0002](./heart-and-soul/decisions/0002-accept-v1-capability-contracts.md)
for the eleven independent contract decisions.
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
and current final-branch correction record.

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
row; seven current rows still match it, while four corrected current rows now
await successor acceptance. Neither the prior acceptance nor the candidate
corrections claim that any capability has been implemented or that an
unmeasured release profile, real resource, archive, or release is valid.

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
7. [`heart-and-soul/decisions/0002-accept-v1-capability-contracts.md`](./heart-and-soul/decisions/0002-accept-v1-capability-contracts.md)
   and the active change's
   [`acceptance.md`](../openspec/changes/establish-ai-usage-telemetry-v1/acceptance.md)
   for the exact contract decisions and their remaining boundary.

## Authority and Change

- Heart-and-soul doctrine is owner-adopted through Decision 0001.
- R5 promoted the predecessor RFC/evidence bytes under Decision 0001's standing
  direction; those accepted digests remain the authority while corrected
  current bytes await an exact-head review and successor decision.
- Topology and craft-and-care derive authority from that doctrine and RFC; they
  do not override them.
- Decision 0002 independently accepts the eleven exact R5 capability contracts.
  Seven current rows still match; four corrected current rows are unknown, so
  task 2.1 blocks non-synthetic implementation until successor acceptance. The
  OpenSpec change remains active, and archival/release retain their later
  explicit gates.
