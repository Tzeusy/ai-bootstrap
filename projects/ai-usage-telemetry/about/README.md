# AI Usage Telemetry Project Shape

This directory is the project-level source of truth for **AI Usage
Telemetry**, a portable local service that turns usage facts already written by
AI coding tools into a durable, content-free history.

The project is still pre-implementation. Statements about current tool file
formats are marked **[Observed]**; proposed architectural conclusions are marked
**[Inferred]**; unsupported future-tool behavior is marked **[Unknown]**. The
documents describe a proposed target shape, not a claim that the service already
exists or that the owner has adopted it.

## Lifecycle Status

This matrix is the central status record for the project-shape artifacts. A
lower-layer document cannot make a higher-layer draft authoritative.

| Artifact | Status | Next authority gate |
|---|---|---|
| Heart-and-soul doctrine | **Draft** | Pending explicit human-owner adoption |
| RFC 0001 | **Draft** | Project-shape review passed; pending RFC-local evidence, formal RFC review, and human-owner acceptance |
| Lay-and-land topology | **Proposed** | Must be reconciled after doctrine adoption and RFC acceptance |
| Craft-and-care standards | **Proposed** | Must be reconciled after doctrine adoption and RFC acceptance |
| OpenSpec capability specifications | **Absent** | Author only after doctrine is adopted and RFC 0001 is accepted |

## The Four `about/` Pillars

| Pillar | Question | Start here |
|---|---|---|
| [Heart and Soul](./heart-and-soul/README.md) | Why does this exist, and what must it never become? | `vision.md`, `data-boundaries.md`, then `v1.md` |
| [Craft and Care](./craft-and-care/README.md) | What evidence and engineering posture does a safe change require? | `engineering-bar.md` |
| [Legends and Lore](./legends-and-lore/README.md) | How do adapters, durable state, and sinks behave? | RFC 0001 |
| [Lay and Land](./lay-and-land/README.md) | Where do components, data, and trust boundaries live? | `components.md`, then `data-flow.md` |

Capability specifications are the fifth project-shape pillar, but are absent
from this first `about/` bootstrap. Observable requirements and WHEN/THEN
scenarios may be authored under this project's `openspec/` only after the owner
adopts the doctrine and accepts the reviewed RFC.

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

- Heart-and-soul doctrine remains Draft until the human owner adopts it.
- RFC 0001 remains Draft until independent review findings have recorded
  dispositions and the human owner accepts it.
- Topology and craft-and-care are proposals derived from those drafts; they do
  not override them or claim acceptance by association.
- OpenSpec remains absent until those two authority gates pass. After it exists,
  implementation work must trace from adopted doctrine through an accepted RFC
  and a signed-off requirement before code is written.
