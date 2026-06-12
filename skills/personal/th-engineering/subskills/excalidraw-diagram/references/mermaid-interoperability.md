# Mermaid Interoperability

Use this reference when the user wants Mermaid converted into Excalidraw, Excalidraw converted into Mermaid, or a workflow that can be represented in either form.

## Core Rule

Convert semantics, not pixels.

- Mermaid is a compact graph description language.
- Excalidraw is a freeform visual explanation medium.
- A good conversion preserves nodes, edges, ordering, hierarchy, and decisions even when the layout changes.

## Mermaid To Excalidraw

1. Read the Mermaid source and identify the diagram family:
   - `flowchart` or `graph`
   - `sequenceDiagram`
   - `stateDiagram`
   - `erDiagram`
   - `classDiagram`
   - `journey`, `gitGraph`, or other specialized forms
2. Extract the semantic structure:
   - nodes
   - edges
   - direction
   - groups or subgraphs
   - labels and conditions
3. Re-express that structure using the Excalidraw visual language:
   - timelines for sequences
   - trees for hierarchy
   - fan-out or convergence for branching graphs
   - section boundaries for Mermaid subgraphs
4. Preserve important labels verbatim unless the user asks for editorial cleanup.
5. When Mermaid is too sparse to teach well, add concrete evidence artifacts if the surrounding task is technical.

Do not force the Excalidraw output into a Mermaid-style left-to-right box grid unless that is actually the clearest explanation.

## Excalidraw To Mermaid

1. Infer the dominant structure from the Excalidraw scene:
   - graph / flow
   - sequence
   - hierarchy
   - state machine
   - entity relationship
2. Pick the Mermaid syntax that loses the least meaning.
3. Convert shapes and arrows into Mermaid nodes and edges.
4. Flatten purely visual styling and decorative annotations unless Mermaid has a meaningful equivalent.
5. If the Excalidraw contains evidence artifacts or rich annotations that Mermaid cannot express, keep the core graph in Mermaid and note the lossy parts briefly.

## Mapping Heuristics

- Excalidraw ellipse start/end nodes usually map to Mermaid rounded nodes or labeled states.
- Decision diamonds usually map to Mermaid decision branches with labeled edges.
- Section boundaries often map to Mermaid `subgraph`.
- Timeline diagrams usually map best to `sequenceDiagram`.
- Trees and dependency graphs usually map best to `flowchart` or `graph`.

## Output Expectations

### When Producing Excalidraw From Mermaid

- Output a proper `.excalidraw` JSON document.
- Keep the selected theme metadata in `appState`.
- Preserve the Mermaid semantics even if the layout becomes more expressive than the source.

### When Producing Mermaid From Excalidraw

- Output valid Mermaid code in a fenced `mermaid` block unless the user requests another format.
- Prefer readable node IDs and stable labels.
- Mention any major information that was visually present but not representable in Mermaid.

## Round-Trip Guidance

If the user wants both versions:

1. Pick one representation as the semantic source of truth.
2. Convert once carefully.
3. Avoid repeated lossy round-trips.

Mermaid is best for compact, editable graph syntax. Excalidraw is best for explanation, emphasis, and spatial teaching.
