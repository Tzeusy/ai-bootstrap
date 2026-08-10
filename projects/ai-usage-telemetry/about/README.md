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
| Heart-and-soul doctrine | **[Observed] Adopted** | Owner Decision 0001 remains authoritative; the launch remediation does not amend doctrine |
| RFC 0001 | **[Observed] Accepted** | Owner Decision 0001 is the current authority; implementation remains absent |
| Lay-and-land topology | **[Observed] Accepted** | Current accepted map; implementation evidence remains absent |
| Craft-and-care standards | **[Observed] Adopted** | Governs specification and later implementation work |
| OpenSpec capability specifications | **[Observed] Active authored candidate** | `READY` is recorded and the active change is complete for authoring; four improvement cycles and conditional owner acceptance remain |

**Accepted shape anchor:** RFC
`4523cdc1fbc9cd3e80b04f4c08c098312dfd6cac2a4f472cd95cb8aeb496daef`;
source/bounds evidence
`5401c9fb0e621af6f35385f89f9cc2cc1d260a3a2119c457ba9e27784e787a1e`;
synthetic vectors
`1b284a304d604fb01d83cb1faab57a5f33a9e62749913abd9c5e93ab3193918e`;
provenance
`dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0`.
See [Owner Decision 0001](./heart-and-soul/decisions/0001-finalize-and-specify.md)
for the human authority record.
The pre-specification instrument is bound in
[`parameters.md`](../docs/launch-gate/parameters.md), and the named-commit
[`READY` administration](../docs/launch-gate/2026-08-10-96ba99d.md) has been
recorded. The active OpenSpec change is a complete authored candidate, not an
owner-accepted capability set: follow its
[`proposal`](../openspec/changes/establish-ai-usage-telemetry-v1/proposal.md) →
[`design`](../openspec/changes/establish-ai-usage-telemetry-v1/design.md) →
[`specifications`](../openspec/changes/establish-ai-usage-telemetry-v1/specs/) →
[`tasks`](../openspec/changes/establish-ai-usage-telemetry-v1/tasks.md) route.
Four required improvement cycles and conditional owner acceptance remain before
implementation authorization. Historical reviews and administrations are
deliberately kept off this default reading path.

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
specifications. They remain a candidate awaiting the required four improvement
cycles and conditional owner acceptance; their presence is not a claim that any
capability has already been owner-accepted or implemented.

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

## Authority and Change

- Heart-and-soul doctrine is owner-adopted through Decision 0001.
- RFC 0001 is accepted at the exact digests recorded in its formal review and
  Decision 0001; unmeasured implementation profiles remain release gates.
- Topology and craft-and-care derive authority from that doctrine and RFC; they
  do not override them.
- The launch gate has recorded `READY` and the active OpenSpec change is the
  authored candidate. Implementation work must still trace from adopted
  doctrine through the accepted RFC and conditionally owner-accepted
  requirements after the four required improvement cycles.
