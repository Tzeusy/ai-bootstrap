---
name: project-shape
description: >
  Analyze and bootstrap the five-pillar knowledge architecture of a software project:
  about/heart-and-soul (doctrine), about/legends-and-lore (RFCs/design contracts), about/lay-and-land
  (topology), about/craft-and-care (execution-quality standards), and openspec/ (capability specs
  at root). Use when: starting a new project's knowledge structure, auditing documentation health,
  onboarding, deciding where ideas should be documented, translating ideas into requirements, or
  mapping system topology. Triggers:
  "project shape", "bootstrap docs", "where should this go", "what's this project about",
  "project pillars", "heart and soul", "spec structure", "knowledge architecture", "system
  map", "topology", "lay of the land", "set up project structure".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-13"
---

# Project Shape

A project's **shape** = the knowledge architecture making it comprehensible to humans and LLMs. Not code — structured understanding of *what* a project is, *why* it exists, *how* it works, *where* it lives, *what* must be built, *who* you must be when you change it.

**Visualization**: prefer `/th-engineering` (excalidraw-diagram) + SVG render when supported and the diagram materially aids comprehension. Else fall back to Mermaid or prose. Never block shape work on diagram tooling.

## Sample triggers

- "Help me set up the docs structure for this project"
- "What's this project about / where should this idea be documented?"
- "Audit our documentation health — are the pillars coherent?"
- "Turn this idea into requirements"
- "Map this system's topology"

## The Five-Pillar Model

Five distinct knowledge layers, each answering a different question:

| Pillar | Folder | Local Skill | Question | Content |
|--------|--------|-------------|----------|---------|
| **Doctrine** | `about/heart-and-soul/` | `heart-and-soul` | **WHY** does this exist? | Vision, principles, non-negotiables, scope boundaries, what it is NOT |
| **Design Contracts** | `about/legends-and-lore/` | `legends-and-lore` | **HOW** will it work? | RFCs, design docs, wire contracts, state machines, reviews, trade-offs |
| **Capability Specs** | `openspec/` | `spec-and-spine` | **WHAT** exactly must be built? | Normative requirements, WHEN/THEN scenarios, testable acceptance criteria |
| **Topology** | `about/lay-and-land/` | `lay-and-land` | **WHERE** does everything live and connect? | Component diagrams, dependency boundaries, data flow, deployment topology, integration maps |
| **Engineering Standards** | `about/craft-and-care/` | `craft-and-care` | **WHO ARE WE WHEN WE BUILD?** | Implementation quality bar, testing discipline, review expectations, observability, dependency hygiene, documentation, maintainability |

Four pillars live under `about/` (project self-knowledge, poetic names). `openspec/` stays at root — a product with its own structure/conventions.

Pillars form a **traceability chain** — Doctrine principle → RFC decision → Spec requirement → Code → Test. Topology cross-cuts all: *where* doctrine is embodied, contracts apply, specs are implemented, work lands. `craft-and-care` is the engineering-character cross-cut: who an engineer must be when changing this repo — explicit, careful, reviewable, observable, maintainable.

<!-- [DIAGRAM: traceability-chain]
Style: conceptual, simple. Use /th-engineering (excalidraw-diagram).
Layout: horizontal assembly line (left-to-right) with a cross-cutting band beneath.
Elements:
  - Top row: 5 nodes in a chain — "Doctrine principle" → "RFC design decision" → "Spec requirement" → "Code" → "Test"
    Connected by arrows. Each node is a rounded rectangle, color-coded by pillar.
  - Bottom band: A wide, semi-transparent rectangle spanning the full width labeled "Topology map: where components live, how they connect, what boundaries exist"
    Connected to each top-row node with bidirectional dashed arrows (↕), showing topology cross-cuts every layer.
  - The bottom band should visually "support" the chain, like a foundation or substrate.
Argument: Every implementation decision traces back through this chain. Topology is not a phase — it cross-cuts all others.
-->

## Quick Start: Assess Shape

Run the scanner for a health report (which pillars exist, maturity, gaps):

```bash
bash <skill-path>/scripts/shape-scan.sh [project-root]
```

For scanner thresholds and conservative scoring rules, read [`references/maturity-rubric.md`](references/maturity-rubric.md) — load when interpreting a scan score or asked what counts as structured/shaped/mature.

If scanning is unavailable, check manually for each pillar:

1. **Doctrine?** — `about/heart-and-soul/`, `heart-and-soul/`, `vision.md`, `MANIFESTO.md`, `PHILOSOPHY.md`, or doctrine-like `README.md`
2. **Design contracts?** — `about/legends-and-lore/`, `docs/rfcs/`, `docs/adrs/`, numbered design docs, review rounds
3. **Specs?** — `openspec/`, `specs/`, `requirements/`, WHEN/THEN files, formal requirement IDs
4. **Topology?** — `about/lay-and-land/`, `maps/`, `architecture/`, component diagrams, deployment docs, `ARCHITECTURE.md`
5. **Engineering standards?** — `about/craft-and-care/`, `engineering-bar.md`, `testing-and-verification.md`, review/verification/observability standards, or quality doctrine scattered in contributor docs

Rate each: **absent** → **nascent** (scattered) → **structured** (dedicated folder, some coverage) → **mature** (comprehensive, traceable, maintained).

## Workflow 1: Bootstrap Shape (new project)

Bootstrapping is **consultative**, not template-filling. Extract shape from the human's head via structured dialogue, synthesis, adversarial review.

**Quality gates:**
- Most capable model, max thinking budget when available.
- Prefer one subagent per pillar for substantive generation/curation — keep each draft in a tighter context window when work partitions cleanly.
- Never self-review — independent review subagents when the environment supports them.
- Challenge the user — accept vague answers only to push deeper, never to ship.

**Fallback modes** (degrade presentation, not rigor):
- Full — highest model, independent review subagents, diagrams via `/th-engineering`.
- Lite — single agent + deliberate self-critique + user review when subagents unavailable.
- No-diagram — Mermaid or prose when diagram tooling unavailable.

**Process:**

1. **Interview** — Socratic extraction across five tracks (identity, boundaries, principles, architecture, contracts). Read [`references/consultative-bootstrapping.md`](references/consultative-bootstrapping.md) for question banks + challenge patterns.
2. **Synthesize** — distill answers into drafts. Use the human's own language. Make trade-offs explicit. Flag contradictions. Prefer one subagent per pillar.
3. **Independent review** — fresh subagents (no generation context) review each doc. Read [`references/review-protocol.md`](references/review-protocol.md) for the three review-agent specs (Coherence, Adversarial, Cross-Pillar).
4. **Revise + present** — incorporate findings, present for validation. If "not quite right" → return to interview, don't patch.
5. **Scaffold + install** — run `shape-init.sh` for structure, populate with reviewed docs, install local skills. Vet generated pillar skills with `/th-engineering` (skill-standards) before relying on them.

**Pillar order** (top-down, each grounds the next): heart-and-soul → craft-and-care → legends-and-lore → openspec → lay-and-land. Draft `craft-and-care` right after doctrine is coherent, before implementation planning — mandatory for all non-trivial work. Topology can start in parallel with design contracts once the architecture interview track is done.

Read [`references/bootstrapping.md`](references/bootstrapping.md) for the phase-by-phase guide, including the local-skill authoring and skill-standards review loop.

<!-- [DIAGRAM: pillar-order]
Style: conceptual, simple. Use /th-engineering (excalidraw-diagram).
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
-->

## Workflow 2: Translate Ideas into Requirements

The shape model funnels ideas into code. Idea → doctrine gate → topology placement → design sketch → WHEN/THEN spec scenarios → tasks. Ideas enter fuzzy, exit precise; each pillar sharpens them; bad ideas die early on doctrine misalignment.

To run this funnel end-to-end for one concrete feature request, use [`../project-feature-request/SKILL.md`](../project-feature-request/SKILL.md). This section is the model it implements.

**When ideas don't fit:**
- Contradicts doctrine → reject, or evolve doctrine (with full team alignment).
- No technical path → park; write exploratory RFC when a path emerges.
- Sound but not specifiable → too vague; break down further.

<!-- [DIAGRAM: idea-funnel]
Style: conceptual, simple. Use /th-engineering (excalidraw-diagram).
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
-->

## Workflow 3: Audit and Maintain Shape Health

For an existing project, assess cross-pillar coherence and keep docs current.

**Assessment dimensions:**
1. **Coverage** — specs trace to RFC sections? RFCs align with doctrine?
2. **Freshness** — specs current with code? RFCs updated after implementation reveals design flaws?
3. **Gaps** — code with no spec? Specs with no doctrine? Design docs that never became specs?
4. **Orphans** — doctrine principles no RFC references; RFC sections no spec covers.
5. **Execution drift** — testing/observability/review/compatibility/documentation/dependency/maintenance standards out of sync with how the project is actually changed?

**Maintenance protocol** when code diverges from docs:
1. **Detect** — compare implementation against spec requirements, RFC contracts, doctrine.
2. **Update** — generate updated sections, preferring one subagent per affected pillar.
3. **Review the delta** — independent review agents on changed sections only.
4. **Cross-check** — cross-pillar review if changes affect multiple pillars.
5. **Present** — show diff + review summary before committing.

**Related:** [`../project-direction/SKILL.md`](../project-direction/SKILL.md) for full direction analysis with priority-weighted plans; [`../project-review/SKILL.md`](../project-review/SKILL.md) (spec-reconciliation mode) for detailed spec-code divergence; [`../project-feature-request/SKILL.md`](../project-feature-request/SKILL.md) for a single idea through the funnel.

## Workflow 4: Generate Project Overview

Synthesize pillars into a visual, layman-friendly `about/README.md` with embedded Excalidraw SVG diagrams — the public face of the project's shape.

**Requirements:** ≥2 pillars exist (heart-and-soul + one other); prefer `/th-engineering` (excalidraw-diagram), fall back to Mermaid/prose; independent review subagents when available, else explicit accessibility/adversarial self-check + user validation.

**Process:** extract layman-relevant essence per pillar → design 3-5 diagrams arguing the project's story → generate via excalidraw-diagram + render SVG (render-view-fix loop) → write structured markdown (thesis → what it's not → how it works → v1 delivers → principles → navigating docs) → review (accessibility + adversarial subagents) → commit to `about/README.md`, sources in `about/assets/`.

Read [`references/generate-overview.md`](references/generate-overview.md) for diagram specs, document skeleton, review-agent prompts, and writing guidelines.

## Reference Index

### Diagrams

Rendered visuals for the shape model (each `.svg` has an editable `.excalidraw` source; regenerate via the `<!-- [DIAGRAM: ...] -->` specs with /th-engineering's excalidraw-diagram):

| Diagram | Shows |
|---------|-------|
| [`assets/five-pillars-load-bearing.svg`](assets/five-pillars-load-bearing.svg) ([source](assets/five-pillars-load-bearing.excalidraw)) | How the five pillars bear load, and in what order |
| [`assets/five-pillars-health-risks.svg`](assets/five-pillars-health-risks.svg) ([source](assets/five-pillars-health-risks.excalidraw)) | Failure modes when a pillar is missing or weak |
| [`assets/pillar-traceability.svg`](assets/pillar-traceability.svg) ([source](assets/pillar-traceability.excalidraw)) | Traceability chain from doctrine down to execution |
| [`assets/idea-funnel.svg`](assets/idea-funnel.svg) ([source](assets/idea-funnel.excalidraw)) | Idea-to-spec funnel and the gate each pillar answers |
| [`assets/review-fanout.svg`](assets/review-fanout.svg) ([source](assets/review-fanout.excalidraw)) | Audit fan-out across pillars in Workflow 3 |
| [`assets/coordinator-workflow.svg`](assets/coordinator-workflow.svg) ([source](assets/coordinator-workflow.excalidraw)) | End-to-end coordinator workflow across shape phases |

### Pillar Guides

| Pillar | Reference | Read when... |
|--------|-----------|-------------|
| Doctrine | [`references/pillar-heart-and-soul.md`](references/pillar-heart-and-soul.md) | Bootstrapping vision, writing non-negotiables, scoping v1 |
| Design Contracts | [`references/pillar-legends-and-lore.md`](references/pillar-legends-and-lore.md) | Structuring RFCs, running reviews, capturing trade-offs |
| Capability Specs | [`references/pillar-spec-and-spine.md`](references/pillar-spec-and-spine.md) | Writing requirements, WHEN/THEN scenarios, spec lifecycle |
| Topology | [`references/pillar-lay-and-land.md`](references/pillar-lay-and-land.md) | Mapping components, boundaries, data flow, deployment |
| Engineering Standards | [`references/pillar-craft-and-care.md`](references/pillar-craft-and-care.md) | Defining the implementation quality bar, review standards, verification, observability, maintainability |

### Process Guides

| Guide | Reference | Read when... |
|-------|-----------|-------------|
| Consultative Bootstrapping | [`references/consultative-bootstrapping.md`](references/consultative-bootstrapping.md) | Extracting shape from a human for a new project — interview tracks, challenge patterns, synthesis rules |
| Review Protocol | [`references/review-protocol.md`](references/review-protocol.md) | Reviewing generated docs with independent subagents — agent specs, iteration rules, anti-patterns |
| Bootstrapping Phases | [`references/bootstrapping.md`](references/bootstrapping.md) | Step-by-step phase guide for establishing shape from scratch |
| Local Skill Templates | [`references/local-skill-templates.md`](references/local-skill-templates.md) | Installing agent navigation skills for each pillar |
| Generate Project Overview | [`references/generate-overview.md`](references/generate-overview.md) | Creating a layman-friendly about/README.md with Excalidraw diagrams |
| Maturity Rubric | [`references/maturity-rubric.md`](references/maturity-rubric.md) | Understanding scanner thresholds and what qualifies as structured/shaped/mature |
| Evaluation Scenarios | [`references/evaluation-scenarios.md`](references/evaluation-scenarios.md) | Testing the skill package itself across strong/weak environments and legacy/scaffolded repos |

### Scripts

| Script | Run when... |
|--------|-------------|
| [`scripts/shape-scan.sh`](scripts/shape-scan.sh) `[project-root]` | Assessing an existing project's shape — reports which pillars exist, their maturity, and gaps |
| [`scripts/shape-init.sh`](scripts/shape-init.sh) `[project-root] [--skills-only] [--tools=...]` | Scaffolding pillar directories and generating correctly-formatted local skills |
| [`scripts/self-test.sh`](scripts/self-test.sh) | Verifying the scanner/scaffolder against fixtures after changing `SKILL.md`, `shape-scan.sh`, or `shape-init.sh` |
| [`scripts/eval-fallbacks.sh`](scripts/eval-fallbacks.sh) | Confirming constrained-environment fallback behavior is still documented after changing fallback guidance |

## Local Skill Installation

Each pillar gets a local navigation skill in `.claude/skills/` (and equivalents) — an **index with selection guidance**, not a copy of pillar content. It says *which file to read* for a task, not *what the file says*. Preferred path generates correctly-formatted skills:

```bash
bash <skill-path>/scripts/shape-init.sh [project-root] --skills-only --tools=claude,codex
```

All five pillars need one: `heart-and-soul`, `legends-and-lore`, `spec-and-spine`, `lay-and-land`, `craft-and-care`. For the manual path — per-pillar templates, the mandatory `name`/`description`-only frontmatter (scanner rejects extra keys), required progressive-discovery structure — read [`references/local-skill-templates.md`](references/local-skill-templates.md). After writing, validate with `scripts/shape-scan.sh` + `scripts/self-test.sh` + `scripts/eval-fallbacks.sh` and fix every reported issue before committing.

## Maintenance Expectations

- Keep metadata, scripts, and references consistent. If the model says "five pillars," adapters and companion files must too.
- Treat `shape-scan.sh` as an auditor, not a brochure — prefer conservative assessments.
- Re-run `scripts/self-test.sh` after changing `SKILL.md`, `shape-scan.sh`, or `shape-init.sh`.
- Re-run `scripts/eval-fallbacks.sh` after changing fallback-mode guidance or references.
- Keep `tests/fixtures/` aligned with real scanner behavior — they are package contract, not throwaway data.

## Anti-Patterns

- **README-as-doctrine** — README describes the project to users; doctrine defines what it *believes*. Don't conflate.
- **Monolith docs** — one giant ARCHITECTURE.md mixing vision/design/specs. Split into pillars.
- **Specs without doctrine** — requirements with no grounding get challenged endlessly. Doctrine ends debates.
- **Doctrine without specs** — principles that never become testable requirements. Specs make doctrine actionable.
- **Stale middle** — doctrine and code current, RFCs six months old. Design contracts must evolve.
- **Pillar without skill** — knowledge exists but agents can't find it. Install local skills.
- **Self-reviewed docs** — the LLM that wrote the doc reviews it in the same context. Use independent subagents.
- **Template-filling** — handing templates to the user instead of extracting shape through dialogue. Produces bureaucracy, not doctrine.
