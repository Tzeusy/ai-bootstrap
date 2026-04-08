---
name: excalidraw-diagram
description: Use when the user wants a workflow, architecture, protocol, concept, or Mermaid diagram converted into or out of Excalidraw, especially when the result should teach through structure, flow, and concrete evidence.
compatibility: Requires Python 3.11+, uv, and Playwright Chromium setup on first render. The Excalidraw browser bundle is vendored into the skill, so rendering stays local after setup. Refresh that bundle from the repo-level scripts/refresh.sh when needed.
---

# Excalidraw Diagram Creator

Generate `.excalidraw` files that argue visually rather than turning prose into labeled boxes.

## Setup

If the renderer has not been initialized in this environment, run:

```bash
uv run scripts/render_excalidraw.py --install-browser
```

The Excalidraw browser bundle is vendored locally, and the renderer serves it from a local HTTP endpoint during export so Chromium can load the packaged module correctly. Refresh it from the repo root with `scripts/refresh.sh` when you want the latest upstream JS state from npm.

## Theme Selection

1. Read `references/theme-catalog.md`.
2. If the user does not request a theme, use the catalog default theme: `default` (dark).
3. Read the selected theme file from `references/themes/`.
4. Use only colors from that theme. Do not invent hex values.
5. Set both of these in the `.excalidraw` file:
   - `appState.viewBackgroundColor` = theme background
   - `appState.excalidrawDiagramTheme` = selected theme name

Theme implies mode. Do not use a separate dark-mode switch.

## Core Principles

- Diagrams should show relationships, causality, and flow that would be weaker in prose.
- Shape should match meaning. If removing the text destroys the idea, redesign the structure.
- Technical diagrams should teach with concrete evidence: real event names, payloads, API calls, or UI states.
- Default to free-floating text. Use containers only when they carry meaning or need bindings.
- Mermaid interoperability is semantic, not literal. Preserve the graph meaning, but do not blindly mimic Mermaid's layout when Excalidraw can teach it better.
- When the user wants a quick structural Mermaid derivation from an existing `.excalidraw` scene, you can use `uv run scripts/excalidraw_to_mermaid.py path/to/file.excalidraw` as a starting point and then refine the result if needed.

## Decide The Depth

Use a simple conceptual diagram when:

- Explaining a mental model
- Giving a fast overview
- The audience does not need implementation details

Use a comprehensive technical diagram when:

- Explaining a real system, protocol, or architecture
- The audience needs to learn how parts actually connect
- The diagram should stand on its own as a teaching artifact

For technical diagrams, research the real spec first and include evidence artifacts.

## Workflow

### 1. Understand The System

- Identify the key transformation, decision points, and outputs.
- For technical topics, look up the real data shape, event names, methods, or API surface.
- Decide what the viewer must see, not just what they must read.
- If the input or output is Mermaid, read `references/mermaid-interoperability.md` and choose the Mermaid form that best matches the diagram semantics.

### 2. Pick A Theme And A Visual Plan

- Choose the theme before generating any colors.
- Choose a different visual pattern for each major concept.
- Prefer lines, clusters, timelines, trees, fan-outs, or comparisons over uniform card grids.
- Use `references/design-patterns.md` for the pattern library.

### 3. Plan Multi-Zoom Structure

For comprehensive diagrams, include:

- A summary flow
- Section boundaries
- Detail inside each section

This keeps the diagram readable from far away and useful up close.

### 4. Build Large Diagrams Section By Section

For larger diagrams:

1. Create the file wrapper and first section.
2. Add one section per edit.
3. Use descriptive IDs.
4. Keep section spacing balanced.
5. Update cross-section bindings when arrows connect across sections.

Do not try to generate a large technical diagram in one pass.

### 5. Generate The JSON

Required document shape:

```json
{
  "type": "excalidraw",
  "version": 2,
  "source": "https://excalidraw.com",
  "elements": [],
  "appState": {
    "viewBackgroundColor": "#ffffff",
    "gridSize": 20,
    "excalidrawDiagramTheme": "default"
  },
  "files": {}
}
```

Rules:

- `text` and `originalText` contain only readable text.
- Use `fontFamily: 3`.
- Prefer `roughness: 0` and `opacity: 100`.
- Every real relationship gets an arrow or structural line.
- If using a container, keep bound text under about 70-75% of the container width and under about 60-65% of the container height.
- For boxed labels, aim for at least 24px horizontal padding and 14px vertical padding.
- If a boxed label is too tight, shorten the wording first, then add a better line break, then widen the container. Reduce font size only as a last resort.
- Pull element shapes and field structure from `references/element-templates.md` and `references/json-schema.md`.

### 6. Render And Iterate

Render after generating or editing the diagram:

```bash
uv run scripts/render_excalidraw.py path/to/file.excalidraw
```

To render with a non-default theme:

```bash
uv run scripts/render_excalidraw.py path/to/file.excalidraw --theme midnight
```

Then inspect the exported image and fix:

- clipping
- overlap
- ambiguous labels
- boxed labels that feel edge-to-edge
- weak hierarchy
- awkward whitespace
- bad arrow routing
- unreadable evidence artifacts

The renderer emits layout warnings before export when bound text is likely too tight inside a container. Treat those warnings as fix-me items, not ignorable noise.

Use `references/render-checklist.md` for the full loop.

## Common Mistakes

- Using generic placeholders for technical systems instead of real formats or event names
- Putting every label inside a box
- Using the same visual structure for every concept
- Skipping theme selection and inventing colors ad hoc
- Forgetting `appState.excalidrawDiagramTheme`
- Treating render as a final export instead of an iterative design check

## Required References

- `references/theme-catalog.md`: theme selection and authoring
- `references/themes/catalog.json`: available themes
- `references/design-patterns.md`: visual pattern library
- `references/mermaid-interoperability.md`: Mermaid to/from Excalidraw prompting workflow
- `references/element-templates.md`: Excalidraw element scaffolds
- `references/json-schema.md`: JSON shape notes
- `references/render-checklist.md`: render-view-fix loop
