# Diagram Regeneration Specs

Load only when regenerating a shape-model diagram (source `.excalidraw` lost,
model changed, or new rendering requested). Each spec feeds `/th-engineering`
(excalidraw-diagram); render SVG next to the source in `assets/`.

## [DIAGRAM: traceability-chain] → `assets/pillar-traceability.svg`

Style: conceptual, simple.
Layout: horizontal assembly line (left-to-right) with a cross-cutting band beneath.
Elements:

- Top row: 5 nodes in a chain — "Doctrine principle" → "RFC design decision" → "Spec requirement" → "Code" → "Test"
  Connected by arrows. Each node is a rounded rectangle, color-coded by pillar.
- Bottom band: A wide, semi-transparent rectangle spanning the full width labeled "Topology map: where components live, how they connect, what boundaries exist"
  Connected to each top-row node with bidirectional dashed arrows (↕), showing topology cross-cuts every layer.
- The bottom band should visually "support" the chain, like a foundation or substrate.

Argument: Every implementation decision traces back through this chain. Topology is not a phase — it cross-cuts all others.

## [DIAGRAM: pillar-order] → `assets/five-pillars-load-bearing.svg`

Style: conceptual, simple.
Layout: horizontal chain of 5 nodes with a parallel bypass arrow.
Elements:

- 5 pillars as distinct shapes, left-to-right:
  1. "heart-and-soul" (WHY) — ellipse, warm color (origin/start)
  2. "craft-and-care" (WHO WE ARE WHEN WE BUILD) — rounded rectangle, distinct color (engineering character) — drafted immediately after doctrine is coherent
  3. "legends-and-lore" (HOW) — rectangle, cool color (process)
  4. "openspec" (WHAT) — diamond or hexagon, accent color (decision/spec)
  5. "lay-and-land" (WHERE) — rectangle, earth tone (structure)
- Sequential arrows connecting 1→2→3→4→5
- A dashed bypass arrow from node 3 to node 5, labeled "can start in parallel after architecture track"
- Below each node: the folder path (about/heart-and-soul/, about/craft-and-care/, about/legends-and-lore/, openspec/, about/lay-and-land/) as free-floating small text

Argument: Order matters — each pillar grounds the next. Craft-and-care follows doctrine directly; topology can start early.

## [DIAGRAM: idea-funnel] → `assets/idea-funnel.svg`

Style: conceptual, simple.
Layout: vertical funnel/timeline — wide at top, narrowing toward bottom.
Elements:

- Top: large cloud shape labeled "Idea / Insight" (abstract, fuzzy)
- 5 stages descending vertically, each with:
  - A gate question (free-floating italic text to the right): "Does this align with doctrine?", "Where does this live?", "How would this work?", "What exactly must be built?", "How must this be executed well?", "Plan the work"
  - The pillar that answers it (colored node matching the pillar's color): heart-and-soul, lay-and-land, legends-and-lore, openspec, craft-and-care, task planning
- Arrows between each stage, narrowing (funnel visual)
- Left side: a "reject" arrow branching off after the first gate, labeled "doctrine misalignment — idea dies early"
- Bottom: small precise rectangle labeled "Implementation tasks" (concrete, sharp)

Argument: Ideas enter fuzzy and exit precise. Each pillar sharpens them. Bad ideas are killed early by doctrine.
