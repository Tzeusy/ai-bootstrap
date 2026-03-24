# Lay and Land — Topology Layer Guide

## Purpose

The topology layer answers **WHERE**: where components live, how they connect, what boundaries exist, and how the system is deployed. It's the spatial understanding of the project — the map you'd draw on a whiteboard to orient a new contributor.

Topology cross-cuts the other three pillars. Doctrine says *why* a boundary exists, RFCs say *how* it communicates, specs say *what* it must do — but topology shows *where* it sits in relation to everything else.

## Recommended Structure

```
about/lay-and-land/
├── README.md              # Index: what maps exist and when to consult them
├── components.md          # Component inventory with ownership and boundaries
├── data-flow.md           # How data moves through the system
├── dependencies.md        # Internal and external dependency map
├── deployment.md          # Where things run (environments, targets, infra)
├── integration.md         # How subsystems connect (APIs, protocols, shared state)
└── assets/                # Diagrams (SVG, Excalidraw, Mermaid sources)
    ├── system-overview.svg
    └── data-flow.svg
```

### Core Maps (most projects need these)

**components.md** — The component inventory. Must answer:
- What are the major components/crates/packages/services?
- What does each one own (its responsibility boundary)?
- What are the dependencies between them?
- Which components are stable vs actively evolving?

**data-flow.md** — How data moves. Must answer:
- What are the primary data paths (happy path, error path)?
- Where does data enter the system? Where does it leave?
- What transformations happen along the way?
- Where are the trust boundaries (validated vs unvalidated data)?

**deployment.md** — Where things run. Must answer:
- What environments exist (dev, staging, prod)?
- What are the platform targets?
- How is the system packaged and delivered?
- What infrastructure does it depend on?

### Situational Maps (add as needed)

| Map | Add when... |
|-----|-------------|
| `integration.md` | Multiple services or external APIs interact |
| `dependencies.md` | Complex dependency graph (internal + external) |
| `boundaries.md` | Security, trust, or organizational boundaries matter |
| `scaling.md` | System has distinct scaling dimensions or bottlenecks |
| `migration.md` | Active migration between old and new architecture |

## Diagram Conventions

Maps should include visual diagrams wherever possible. Prefer:

1. **Mermaid** — Renders in GitHub/GitLab markdown, version-controllable
2. **Excalidraw** — Hand-drawn feel, good for whiteboards, `.excalidraw` files are JSON
3. **SVG** — For polished diagrams, store sources alongside rendered output

Store diagram sources in `about/lay-and-land/assets/` so they can be updated.

### Diagram Principles

- Label every arrow (what flows, what protocol)
- Show boundaries explicitly (dashed boxes for trust boundaries, solid for ownership)
- Include a legend if using non-obvious conventions
- Date the diagram — topology changes; readers need to know when it was current

## Relationship to Other Pillars

| Other pillar | Topology's role |
|-------------|-----------------|
| **Doctrine** (heart-and-soul) | Topology shows *where* doctrine principles are embodied. A non-negotiable rule like "agents never sit in the frame loop" implies a boundary on the topology map. |
| **Design Contracts** (docs) | Each RFC governs a region of the topology. The component map shows which RFC applies where. |
| **Specs** (openspec) | Spec domains map to components. The topology shows which specs govern which parts of the system. |

## Writing Topology Docs

### Do

- Start with the highest-level view (system context) and zoom in
- Show both static structure (what exists) and dynamic flow (how it moves)
- Mark what's stable vs what's actively changing
- Include external systems the project depends on
- Keep maps current — stale topology is worse than no topology

### Don't

- Duplicate RFC-level protocol details (link to the RFC instead)
- Include implementation details (file paths, function names) — those change too fast
- Create one giant diagram — prefer multiple focused maps
- Forget external dependencies (databases, APIs, cloud services)

## Maturity Levels

| Level | Signal |
|-------|--------|
| Absent | No architecture docs, topology is tribal knowledge |
| Nascent | README has a rough architecture section or a single diagram |
| Structured | `about/lay-and-land/` exists with component and data-flow docs |
| Mature | Complete topology with diagrams, boundary annotations, cross-references to RFCs/specs, actively maintained |

## Evolution

Topology evolves at a moderate pace — faster than doctrine, slower than code. When updating:
1. Update the affected map(s) when components are added, removed, or restructured
2. Re-render diagrams from sources (don't hand-edit SVGs)
3. Check that RFC and spec cross-references still hold
4. Mark deprecated components clearly rather than silently removing them
