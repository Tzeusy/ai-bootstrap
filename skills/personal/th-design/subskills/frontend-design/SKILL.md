---
name: frontend-design
description: Create distinctive, production-grade frontend interfaces with high design quality. Use this skill when the user asks to build web components, pages, artifacts, posters, or applications (examples include websites, landing pages, dashboards, React components, HTML/CSS layouts, or when styling/beautifying any web UI). Generates creative, polished code and UI design that avoids generic AI aesthetics.
license: Apache-2.0; complete terms in LICENSE.txt
metadata:
  owner: tze
  authors:
    - Anthropic (upstream)
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-08-31"
  provenance:
    source: https://github.com/anthropics/skills
    revision: fa0fa64bdc967915dc8399e803be67759e1e62b8
    source_path: skills/frontend-design
    relationship: Intentional local fork tuned as the frontend execution subskill under th-design.
---

This skill guides creation of distinctive, production-grade frontend interfaces that avoid generic "AI slop" aesthetics. Implement real working code with exceptional attention to aesthetic details and creative choices.

The user provides frontend requirements: a component, page, application, or interface to build. They may include context about the purpose, audience, or technical constraints.

## Use This Skill When

- Building a new web page, component, artifact, or app shell that needs a
  committed aesthetic direction
- Restyling or beautifying an existing web UI that reads as generic
- The ask is execution ("build/style this"), not judgment ("review this")

Example trigger phrasings: "build this page", "style this component", "make
this look less generic", "design a landing page", "beautify this dashboard".

## Do Not Use This Skill For

- Judging whether a design is good — [design-bar](../design-bar/SKILL.md) and
  the sibling bar subskills
- Deep iterative polish in a project wired for `impeccable` — the router's
  "External craft skills" section
- Chart and data-graphic construction — `/dataviz`

## Bar Precedence (Local Hard Stop)

This subskill executes under the package's design bar; aesthetic ambition
never overrides it. Wherever the exhortations below ("surprise", staggered
reveals, custom cursors, grain overlays) conflict with these, the bar wins:

- Motion communicates state or spatial continuity — decorative animation and
  effects the user waits through are defects; transitions ~100–200ms,
  ease-out, instant-state fallback loses nothing
  ([visual-language](../visual-language/SKILL.md)).
- Accessibility floor holds from the first draft: AA contrast in every theme,
  keyboard operability, visible focus, `prefers-reduced-motion` honored
  ([accessibility](../accessibility/SKILL.md)).
- Input is never blocked; layout never shifts under a pending click; hot
  paths stay inside latency budgets
  ([interaction-speed](../interaction-speed/SKILL.md)).
- Custom cursors, scroll-jacking, and autoplaying attention effects need a
  communicative justification or they don't ship.

## Design Thinking

Before coding, understand the context and commit to a BOLD aesthetic direction:
- **Purpose**: What problem does this interface solve? Who uses it?
- **Tone**: Pick an extreme: brutally minimal, maximalist chaos, retro-futuristic, organic/natural, luxury/refined, playful/toy-like, editorial/magazine, brutalist/raw, art deco/geometric, soft/pastel, industrial/utilitarian, etc. There are so many flavors to choose from. Use these for inspiration but design one that is true to the aesthetic direction.
- **Constraints**: Technical requirements (framework, performance, accessibility).
- **Differentiation**: What makes this UNFORGETTABLE? What's the one thing someone will remember?

**CRITICAL**: Choose a clear conceptual direction and execute it with precision. Bold maximalism and refined minimalism both work - the key is intentionality, not intensity.

Then implement working code (HTML/CSS/JS, React, Vue, etc.) that is:
- Production-grade and functional
- Visually striking and memorable
- Cohesive with a clear aesthetic point-of-view
- Meticulously refined in every detail

## Frontend Aesthetics Guidelines

Focus on:
- **Typography**: Choose fonts that are beautiful, unique, and interesting. Avoid generic fonts like Arial and Inter; opt instead for distinctive choices that elevate the frontend's aesthetics; unexpected, characterful font choices. Pair a distinctive display font with a refined body font.
- **Color & Theme**: Commit to a cohesive aesthetic. Use CSS variables for consistency. Dominant colors with sharp accents outperform timid, evenly-distributed palettes.
- **Motion**: Use animations for effects and micro-interactions. Prioritize CSS-only solutions for HTML. Use Motion library for React when available. Focus on high-impact moments: one well-orchestrated page load with staggered reveals (animation-delay) creates more delight than scattered micro-interactions. Use scroll-triggering and hover states that surprise.
- **Spatial Composition**: Unexpected layouts. Asymmetry. Overlap. Diagonal flow. Grid-breaking elements. Generous negative space OR controlled density.
- **Backgrounds & Visual Details**: Create atmosphere and depth rather than defaulting to solid colors. Add contextual effects and textures that match the overall aesthetic. Apply creative forms like gradient meshes, noise textures, geometric patterns, layered transparencies, dramatic shadows, decorative borders, custom cursors, and grain overlays.

NEVER use generic AI-generated aesthetics like overused font families (Inter, Roboto, Arial, system fonts), cliched color schemes (particularly purple gradients on white backgrounds), predictable layouts and component patterns, and cookie-cutter design that lacks context-specific character.

Interpret creatively and make unexpected choices that feel genuinely designed for the context. No design should be the same. Vary between light and dark themes, different fonts, different aesthetics. NEVER converge on common choices (Space Grotesk, for example) across generations.

**IMPORTANT**: Match implementation complexity to the aesthetic vision. Maximalist designs need elaborate code with extensive animations and effects. Minimalist or refined designs need restraint, precision, and careful attention to spacing, typography, and subtle details. Elegance comes from executing the vision well.

Remember: Claude is capable of extraordinary creative work. Don't hold back, show what can truly be created when thinking outside the box and committing fully to a distinctive vision.
