# Generate Project Overview

Synthesize all four pillars into a visual, layman-friendly markdown document that serves as `about/README.md`. This is the public face of the project's shape — it should make someone who knows nothing about the project understand what it is, why it exists, how it works, and where everything lives.

## Output

A single markdown file at `about/README.md` containing:
- Embedded SVG diagrams (rendered from Excalidraw)
- Prose written for a non-technical reader
- Links into the four pillars for readers who want depth

## Prerequisites

- At least two pillars must exist (heart-and-soul + one other)
- `/excalidraw-diagram` skill must be available for visualization
- Excalidraw renderer must be set up (see `/excalidraw-diagram` for setup)

## Process

### Phase 1: Extract the Narrative

Read each pillar and extract the layman-relevant essence. Not every technical detail belongs in the overview — only what helps someone *understand* the project.

| Pillar | Extract... | Skip... |
|--------|-----------|---------|
| **heart-and-soul** | Core thesis, what it IS and IS NOT, non-negotiable principles (in plain language), v1 scope | Internal workflow rules, development process |
| **law-and-lore** | Key architectural decisions and *why* they were made, major trade-offs | Wire formats, field numbers, protobuf schemas |
| **spec-and-spine** | Feature areas and what they do (from requirement names), v1 coverage | WHEN/THEN scenarios, requirement IDs, scope tags |
| **lay-and-land** | Component names and what each one does, how data flows, deployment | Internal dependency details, infrastructure specifics |

### Phase 2: Design the Diagrams

Plan 3-5 Excalidraw diagrams that visually argue the project's story. Each diagram should teach something that prose alone can't convey.

#### Diagram 1: The Vision (required)

**What it argues**: What this project IS — its core thesis in visual form.

Source: `about/heart-and-soul/vision.md`

Approach:
- Use the `/excalidraw-diagram` skill's conceptual/simple mode
- Show the core transformation or value proposition
- Include what the project IS NOT as a visual contrast (crossed-out or dimmed alternatives)
- This should be the hero image at the top of the document

#### Diagram 2: The Architecture (required)

**What it argues**: How the major pieces fit together.

Source: `about/lay-and-land/components.md`, `about/heart-and-soul/architecture.md`

Approach:
- Use `/excalidraw-diagram` at the comprehensive level
- Show components as distinct shapes reflecting their roles
- Show data flow with labeled arrows
- Mark boundaries (trust, ownership, deployment)
- A layman should see "these are the parts and here's how they connect"

#### Diagram 3: The Scope (recommended)

**What it argues**: What v1 delivers vs what comes later.

Source: `about/heart-and-soul/v1.md`

Approach:
- Side-by-side or inside/outside visual
- v1 features in solid colors, deferred features dimmed or outlined
- Makes the scope boundary viscerally clear

#### Diagram 4: The Pillar Model (recommended)

**What it argues**: How the project's knowledge is structured.

Source: The four-pillar model itself

Approach:
- Show the four pillars with the traceability chain
- WHY → HOW → WHAT → WHERE with representative content from each
- This is meta — it explains how to navigate the docs themselves

#### Diagram 5: Domain-Specific (optional)

**What it argues**: Whatever concept is most unique or hardest to explain about this project.

Source: Varies — the most distinctive RFC, the core protocol, the key innovation

Approach:
- Use comprehensive mode with evidence artifacts
- This is where the project's personality shines

### Phase 3: Generate

For each diagram:

1. **Design** using `/excalidraw-diagram` methodology (depth assessment → concept mapping → pattern selection → sketch → JSON)
2. **Render to PNG** using the excalidraw render script
3. **Convert to SVG** for clean markdown embedding (or use PNG with relative path)
4. **Validate** through the render-view-fix loop until the diagram passes quality checks
5. **Store** diagram sources in `about/assets/` (or `about/lay-and-land/assets/`)

### Phase 4: Write the Document

Structure the markdown document with this skeleton:

```markdown
# [Project Name]

> [One-sentence thesis from heart-and-soul/vision.md — the "elevator pitch"]

![Vision diagram](assets/vision.svg)

[2-3 paragraphs expanding the thesis in plain language. What problem does this
solve? For whom? What changes in the world when this project succeeds?]

## What This Is Not

[Explicit non-goals from vision.md, rewritten for a general audience.
This section prevents misunderstanding and scope creep.]

## How It Works

![Architecture diagram](assets/architecture.svg)

[Walk through the architecture diagram in prose. Name each component,
explain what it does in one sentence, explain how data flows between them.
Write as if the reader has never seen a system diagram before.]

## What V1 Delivers

![Scope diagram](assets/scope.svg)

[List what ships and what's deferred, with brief rationale for each deferral.
Frame positively — what users GET, not what's missing.]

## Core Principles

[The non-negotiable rules from doctrine, rewritten in plain language.
Each principle should be one sentence with a brief "which means..." explanation.
A reader should understand WHY each principle exists, not just WHAT it says.]

## Navigating the Documentation

![Pillar model diagram](assets/pillars.svg)

This project's documentation follows a four-pillar knowledge architecture:

| Pillar | Location | What You'll Find |
|--------|----------|-----------------|
| **Heart and Soul** | `about/heart-and-soul/` | Vision, principles, scope boundaries |
| **Law and Lore** | `about/law-and-lore/` | Technical design decisions and contracts |
| **Spec and Spine** | `openspec/` | Detailed feature requirements |
| **Lay and Land** | `about/lay-and-land/` | System maps and component topology |

[Brief guidance: "Start with heart-and-soul/vision.md for the full thesis.
Read law-and-lore/ when you need to understand a technical decision.
Check openspec/ for the exact requirements before implementing.
Consult lay-and-land/ when you need to find where something lives."]

## [Optional: Domain-Specific Section]

![Domain diagram](assets/domain.svg)

[If Diagram 5 exists, explain the project's most distinctive concept here.]
```

### Phase 5: Review

Use the review protocol from `references/review-protocol.md` but with modified review agents:

#### Overview Coherence Review

```
You are reviewing a project overview document intended for a layman audience.
Evaluate:
1. ACCESSIBILITY — Would a non-technical person understand this?
   Flag jargon, unexplained acronyms, and assumed knowledge.
2. ACCURACY — Does the overview faithfully represent the project?
   Cross-check claims against the source pillar documents.
3. COMPLETENESS — Are all four pillars represented?
   Is anything important missing?
4. NARRATIVE — Does it tell a coherent story?
   Is there a clear thread from "why this exists" to "how to navigate"?
5. DIAGRAMS — Do the diagram descriptions match what the diagrams show?
   Are diagrams referenced at the right point in the narrative?
```

#### Overview Adversarial Review

```
You are a skeptical first-time reader who knows nothing about this project.
After reading the overview:
1. What questions do you still have?
2. What confused you?
3. What claims seem unsubstantiated?
4. Where did the writing assume you already knew something?
5. Is there anything that sounds like marketing rather than substance?
```

## Writing Guidelines

- **No jargon without explanation** — If you must use a technical term, define it inline
- **Concrete over abstract** — "processes 10,000 events per second" not "high throughput"
- **Active voice** — "The runtime composites the scene" not "The scene is composited by the runtime"
- **Short paragraphs** — 2-4 sentences max. The document should be scannable.
- **Diagrams do the heavy lifting** — Prose explains the diagram, not the other way around
- **Link, don't duplicate** — Point readers into the pillars for depth rather than reproducing content
- **The "explain it to a friend" test** — Read each section aloud. If it sounds like documentation, rewrite it.

## Anti-Patterns

- **Internal README** — Writing for the team instead of for someone who just found the project. The overview is external-facing.
- **Feature list** — Listing what the project does without explaining why or how. Features belong in specs.
- **Diagram dump** — Including diagrams without prose that walks through them. Every diagram needs a narrative companion.
- **Copy-paste from doctrine** — Doctrine is written for implementors. The overview must be rewritten for laypeople.
- **Stale overview** — The overview must be updated when pillars change. Include it in the maintenance protocol.
