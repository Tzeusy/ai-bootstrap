---
name: project-shape
description: >
  Analyze and bootstrap the five-pillar knowledge architecture of a software project:
  about/heart-and-soul (doctrine), about/law-and-lore (RFCs/design contracts), about/lay-and-land
  (topology), about/craft-and-care (execution-quality standards), and openspec/ (capability specs
  at root). Use when: starting a new project's knowledge structure, auditing documentation health,
  onboarding, deciding where ideas should be documented, translating ideas into requirements, or
  mapping system topology. Triggers:
  "project shape", "bootstrap docs", "where should this go", "what's this project about",
  "project pillars", "heart and soul", "spec structure", "knowledge architecture", "system
  map", "topology", "lay of the land", "set up project structure".
---

# Project Shape

A project's **shape** is the knowledge architecture that makes it comprehensible to both humans and LLMs. Shape is not code — it's the structured understanding that tells you *what* a project is, *why* it exists, *how* it works, *where* it lives, *what* must be built, and *how work should be executed well*.

**Visualization directive**: Prefer `/excalidraw-diagram` plus SVG rendering when the environment supports it and the diagram materially improves comprehension. If that skill or renderer is unavailable, fall back to Mermaid or concise prose. Do not block shape work on diagram tooling.

## The Five-Pillar Model

Every well-shaped project has five distinct knowledge layers, each answering a different question:

| Pillar | Folder | Local Skill | Question | Content |
|--------|--------|-------------|----------|---------|
| **Doctrine** | `about/heart-and-soul/` | `heart-and-soul` | **WHY** does this exist? | Vision, principles, non-negotiables, scope boundaries, what it is NOT |
| **Design Contracts** | `about/law-and-lore/` | `law-and-lore` | **HOW** will it work? | RFCs, design docs, wire contracts, state machines, reviews, trade-offs |
| **Capability Specs** | `openspec/` | `spec-and-spine` | **WHAT** exactly must be built? | Normative requirements, WHEN/THEN scenarios, testable acceptance criteria |
| **Topology** | `about/lay-and-land/` | `lay-and-land` | **WHERE** does everything live and connect? | Component diagrams, dependency boundaries, data flow, deployment topology, integration maps |
| **Engineering Standards** | `about/craft-and-care/` | `craft-and-care` | **HOW SHOULD WORK BE EXECUTED WELL?** | Implementation quality bar, testing discipline, review expectations, observability, dependency hygiene, documentation, maintainability |

Four pillars live under `about/` — the project's self-knowledge with poetic names. `openspec/` stays at root because it's a product with its own structure and conventions.

The pillars form a **traceability chain**:

<!-- [DIAGRAM: traceability-chain]
Style: conceptual, simple. Use /excalidraw-diagram.
Layout: horizontal assembly line (left-to-right) with a cross-cutting band beneath.
Elements:
  - Top row: 5 nodes in a chain — "Doctrine principle" → "RFC design decision" → "Spec requirement" → "Code" → "Test"
    Connected by arrows. Each node is a rounded rectangle, color-coded by pillar.
  - Bottom band: A wide, semi-transparent rectangle spanning the full width labeled "Topology map: where components live, how they connect, what boundaries exist"
    Connected to each top-row node with bidirectional dashed arrows (↕), showing topology cross-cuts every layer.
  - The bottom band should visually "support" the chain, like a foundation or substrate.
Argument: Every implementation decision traces back through this chain. Topology is not a phase — it cross-cuts all others.
-->

Every implementation decision should trace back through this chain. The topology layer cross-cuts all others — it shows *where* the doctrine is embodied, *where* the design contracts apply, and *where* the specs are implemented. The `craft-and-care` layer is the execution-quality cross-cut — it defines how changes touching any part of the chain are implemented, verified, reviewed, documented, and operated.

## Quick Start: Assess a Project's Shape

Run the scan script to discover existing shape artifacts:

```bash
bash <skill-path>/scripts/shape-scan.sh [project-root]
```

This produces a health report showing which pillars exist, their maturity, and gaps.

For the scanner's intended thresholds and conservative scoring rules, read `references/maturity-rubric.md`.

### Manual Assessment

If scanning isn't available, check for these signals:

1. **Doctrine exists?** — Look for: `about/heart-and-soul/`, `heart-and-soul/`, `vision.md`, `MANIFESTO.md`, `PHILOSOPHY.md`, or doctrine-like content in `README.md`
2. **Design contracts exist?** — Look for: `about/law-and-lore/`, `docs/rfcs/`, `docs/adrs/`, numbered design docs, review rounds
3. **Specs exist?** — Look for: `openspec/`, `specs/`, `requirements/`, files with WHEN/THEN scenarios, formal requirement IDs
4. **Topology exists?** — Look for: `about/lay-and-land/`, `maps/`, `architecture/`, component diagrams, deployment docs, `ARCHITECTURE.md`
5. **Engineering standards exist?** — Look for: `about/craft-and-care/`, `engineering-bar.md`, `testing-and-verification.md`, review standards, verification expectations, observability/operability guidance, or implementation-quality doctrine currently scattered through contributor docs

Rate each pillar: **absent** → **nascent** (scattered, informal) → **structured** (dedicated folder, some coverage) → **mature** (comprehensive, traceable, maintained)

## Workflow 1: Bootstrap Shape for a New Project

Bootstrapping is a **consultative process**, not a template-filling exercise. The LLM must extract shape from the human's head through structured dialogue, synthesis, and adversarial review.

### Quality Requirements

- **Use the most capable model available** with maximum thinking/reasoning budget when available
- **Prefer distinct subagents per pillar for substantive document generation or curation** — keep doctrine, contracts, specs, topology, and engineering standards in tighter, task-specific context windows whenever the work can be partitioned cleanly
- **Never self-review** — use independent subagents for review when the environment supports them (see below)
- **Challenge the user** — accept vague answers only to push deeper, never to ship

### Fallback Modes

- **Full mode** — Highest-capability model, independent review subagents, diagrams rendered via `/excalidraw-diagram`
- **Lite mode** — Single agent plus deliberate self-critique and user review when subagents are unavailable
- **No-diagram mode** — Use Mermaid or prose when diagram tooling is unavailable

The skill still applies in constrained environments. Degrade the presentation, not the rigor.

### The Process

1. **Consultative interview** — Structured Socratic extraction across five tracks (identity, boundaries, principles, architecture, contracts). Read `references/consultative-bootstrapping.md` for the full protocol with question banks and challenge patterns.

2. **Synthesize** — Distill interview answers into draft documents. Use the human's own language. Make implicit trade-offs explicit. Flag contradictions. For substantive shape work, prefer one subagent per pillar or per major pillar document cluster so each draft is generated and refined in a tighter context window.

3. **Independent review** — Spawn fresh subagents (no generation context) to review each document. Read `references/review-protocol.md` for the three review agent specs (Coherence, Adversarial, Cross-Pillar).

4. **Revise and present** — Incorporate review findings, present to user for validation. If the user says "not quite right," return to the interview — don't patch.

5. **Scaffold and install** — Run `shape-init.sh` for directory structure, populate with reviewed documents, install local skills.

### Pillar Order

Work top-down — each pillar grounds the next:

<!-- [DIAGRAM: pillar-order]
Style: conceptual, simple. Use /excalidraw-diagram.
Layout: horizontal chain of 4 nodes with a parallel bypass arrow.
Elements:
  - 4 pillars as distinct shapes, left-to-right:
    1. "heart-and-soul" (WHY) — ellipse, warm color (origin/start)
    2. "law-and-lore" (HOW) — rectangle, cool color (process)
    3. "openspec" (WHAT) — diamond or hexagon, accent color (decision/spec)
    4. "lay-and-land" (WHERE) — rectangle, earth tone (structure)
  - Sequential arrows connecting 1→2→3→4
  - A dashed bypass arrow from node 2 to node 4, labeled "can start in parallel after architecture track"
  - Below each node: the folder path (about/heart-and-soul/, about/law-and-lore/, openspec/, about/lay-and-land/) as free-floating small text
Argument: Order matters — each pillar grounds the next. But topology can start early.
-->

Topology (lay-and-land) can be started in parallel with design contracts once the architecture interview track is complete. `craft-and-care` should be drafted immediately after doctrine is coherent and before implementation planning begins; it is mandatory for all non-trivial implementation work.

Read `references/bootstrapping.md` for phase-by-phase details.

## Workflow 2: Translate Ideas into Requirements

The shape model provides a natural funnel for turning ideas into code:

<!-- [DIAGRAM: idea-funnel]
Style: conceptual, simple. Use /excalidraw-diagram.
Layout: vertical funnel/timeline — wide at top, narrowing toward bottom.
Elements:
  - Top: large cloud shape labeled "Idea / Insight" (abstract, fuzzy)
  - 5 stages descending vertically, each with:
    - A gate question (free-floating italic text to the right): "Does this align with doctrine?", "Where does this live?", "How would this work?", "What exactly must be built?", "How must this be executed well?", "Plan the work"
    - The pillar that answers it (colored node matching the pillar's color): heart-and-soul, lay-and-land, law-and-lore, openspec, craft-and-care, task planning
  - Arrows between each stage, narrowing (funnel visual)
  - Left side: a "reject" arrow branching off after the first gate, labeled "doctrine misalignment — idea dies early"
  - Bottom: small precise rectangle labeled "Implementation tasks" (concrete, sharp)
Argument: Ideas enter fuzzy and exit precise. Each pillar sharpens them. Bad ideas are killed early by doctrine.
-->

At each stage, ideas get sharper and more concrete. Bad ideas die early (doctrine misalignment). Good ideas gain precision (spec scenarios).

### When Ideas Don't Fit

- **Idea contradicts doctrine** → Either reject the idea or evolve the doctrine (with full team alignment)
- **Idea has no technical path** → Park it; write an exploratory RFC when a path emerges
- **Idea is technically sound but not specifiable** → It's too vague. Break it down further.

## Workflow 3: Audit and Maintain Shape Health

For an existing project, assess coherence across pillars and keep docs current.

### Assessment Dimensions

1. **Coverage** — Do all spec requirements trace to RFC sections? Do all RFCs align with doctrine?
2. **Freshness** — Are specs current with the code? Are RFCs updated after implementation reveals design flaws?
3. **Gaps** — Is there code with no spec coverage? Specs with no doctrine backing? Design docs that never became specs?
4. **Orphans** — Doctrine principles that no RFC references. RFC sections that no spec covers.
5. **Execution drift** — Have testing, observability, review, compatibility, documentation, dependency, or maintenance standards fallen out of sync with how the project is actually changed?

### Maintenance Protocol

When code changes diverge from documentation:

1. **Detect** — Compare implementation against spec requirements, RFC contracts, and doctrine
2. **Update** — Generate updated sections for affected documents, preferring distinct subagents per affected pillar so each curation pass stays narrow and pillar-specific
3. **Review the delta** — Spawn independent review agents on changed sections (not the full doc)
4. **Cross-check** — Run cross-pillar review if changes affect multiple pillars
5. **Present to user** — Show diff with review summary before committing

### Related Skills

Use `/project-direction` for a full direction analysis including priority-weighted work plans. Use `/reconcile-spec-to-project` for detailed spec-code divergence detection.

## Workflow 4: Generate Project Overview

Synthesize the project pillars into a visual, layman-friendly `about/README.md` with embedded Excalidraw SVG diagrams. This is the public face of the project's shape — it makes someone who knows nothing understand what the project is, why it exists, and how it works.

### Requirements

- At least two pillars must exist (heart-and-soul + one other)
- Prefer `/excalidraw-diagram` for visualizations; fall back to Mermaid or prose when unavailable
- Use independent review subagents when available; otherwise do an explicit accessibility/adversarial self-check and ask the user to validate

### The Process

1. **Extract** — Read each pillar, pull out only what a layman needs to understand
2. **Design diagrams** — Plan 3-5 Excalidraw diagrams that visually argue the project's story (vision, architecture, scope, pillar model, domain-specific)
3. **Generate** — Build each diagram via `/excalidraw-diagram`, render to SVG, validate through render-view-fix loop
4. **Write** — Structured markdown: thesis → what it's not → how it works → what v1 delivers → principles → navigating the docs
5. **Review** — Spawn accessibility + adversarial review subagents targeting layman comprehension
6. **Commit** — Place at `about/README.md`, store diagram sources in `about/assets/`

Read `references/generate-overview.md` for the full guide: diagram specs, document skeleton, review agent prompts, and writing guidelines.

## Reference Index

### Pillar Guides

| Pillar | Reference | Read when... |
|--------|-----------|-------------|
| Doctrine | `references/pillar-heart-and-soul.md` | Bootstrapping vision, writing non-negotiables, scoping v1 |
| Design Contracts | `references/pillar-law-and-lore.md` | Structuring RFCs, running reviews, capturing trade-offs |
| Capability Specs | `references/pillar-spec-and-spine.md` | Writing requirements, WHEN/THEN scenarios, spec lifecycle |
| Topology | `references/pillar-lay-and-land.md` | Mapping components, boundaries, data flow, deployment |
| Engineering Standards | `references/pillar-craft-and-care.md` | Defining the implementation quality bar, review standards, verification discipline, observability, and maintainability expectations |

### Process Guides

| Guide | Reference | Read when... |
|-------|-----------|-------------|
| Consultative Bootstrapping | `references/consultative-bootstrapping.md` | Extracting shape from a human for a new project — interview tracks, challenge patterns, synthesis rules |
| Review Protocol | `references/review-protocol.md` | Reviewing generated docs with independent subagents — agent specs, iteration rules, anti-patterns |
| Bootstrapping Phases | `references/bootstrapping.md` | Step-by-step phase guide for establishing shape from scratch |
| Local Skill Templates | `references/local-skill-templates.md` | Installing agent navigation skills for each pillar |
| Generate Project Overview | `references/generate-overview.md` | Creating a layman-friendly about/README.md with Excalidraw diagrams |
| Maturity Rubric | `references/maturity-rubric.md` | Understanding scanner thresholds and what qualifies as structured/shaped/mature |
| Evaluation Scenarios | `references/evaluation-scenarios.md` | Testing the skill package itself across strong/weak environments and legacy/scaffolded repos |

## Local Skill Installation

Each pillar should have a corresponding local skill in `.claude/skills/` (and equivalent for other tools). These skills teach LLM agents how to navigate and use each pillar.

**Skill-generation mandate:** Generated local skills **MUST** follow current `agentskills.io` expectations and `/skill-creator` best practices. Keep frontmatter valid, keep descriptions focused on triggering conditions, and keep the SKILL body lean enough to act as a routing/index layer rather than a monolith.

**Progressive discovery mandate:** Local skills should optimize for targeted context retrieval. Treat `SKILL.md` as the discovery surface, then fan detailed guidance out into narrower files such as `references/*.md`, deterministic helpers in `scripts/`, and only the output-facing resources in `assets/`. Every supporting file that an agent may need should be linked from `SKILL.md` with explicit "read when..." guidance so the agent can load only the relevant slice.

**Preferred method:** Run `shape-init.sh` which generates correctly-formatted skills automatically:

```bash
bash <skill-path>/scripts/shape-init.sh [project-root] --skills-only --tools=claude,codex
```

**If writing skills manually**, every SKILL.md **MUST** start with YAML frontmatter. Without it, skill loaders reject the file silently. Use only the currently supported metadata keys:

```yaml
---
name: <pillar-name>
description: >
  Multi-line description of when this skill should be used.
  This is the triggering mechanism — be specific about contexts.
---

# Skill Title

Markdown body follows...
```

- The `---` delimiters on lines 1 and N are mandatory — without them the file is invalid
- `name` and `description` are the supported fields; do not add extra frontmatter keys unless the target platform explicitly documents them
- Read `references/local-skill-templates.md` for full customizable templates per pillar plus the required progressive-discovery structure

The key principle: local skills are **indexes with selection guidance**, not duplicates of the content. They tell the agent *which file to read* for a given task, not *what the file says*. If a pillar is accumulating large inline guidance, split it into targeted sub-docs or utilities and keep the skill as the router.

All five pillars should have a corresponding local skill: `heart-and-soul`, `law-and-lore`, `spec-and-spine`, `lay-and-land`, `craft-and-care`.

**After writing skills, validate them:**

```bash
bash <skill-path>/scripts/shape-scan.sh [project-root]
bash <skill-path>/scripts/self-test.sh
bash <skill-path>/scripts/eval-fallbacks.sh
```

The scan checks structural integrity plus common scaffold/template drift. The self-test script exercises the scanner and scaffolder against known scenarios. The fallback eval script checks that constrained-environment behavior is still explicitly supported in the package docs. Fix any reported issues before committing.

## Maintenance Expectations

- Keep package metadata, scripts, and references consistent. If the model says "five pillars," adapters and companion files must say the same.
- Treat `shape-scan.sh` as an auditor, not a brochure. Prefer conservative assessments over flattering ones.
- Re-run `scripts/self-test.sh` whenever changing `SKILL.md`, `shape-scan.sh`, or `shape-init.sh`.
- Re-run `scripts/eval-fallbacks.sh` whenever changing fallback-mode guidance or references.
- Keep `tests/fixtures/` aligned with real scanner behavior. Fixtures are part of the package contract, not throwaway test data.

## Anti-Patterns

- **README-as-doctrine** — A README describes the project to users. Doctrine defines what the project *believes*. Don't conflate them.
- **Monolith docs** — One giant ARCHITECTURE.md mixing vision, design, and specs. Split into pillars.
- **Specs without doctrine** — Requirements with no philosophical grounding get challenged endlessly. Doctrine ends debates.
- **Doctrine without specs** — Beautiful principles that never become testable requirements. Specs make doctrine actionable.
- **Stale middle** — Doctrine and code are current, but RFCs are from six months ago. Design contracts must evolve.
- **Pillar without skill** — The knowledge exists but agents can't find it. Install local skills.
- **Self-reviewed docs** — The LLM that wrote the doc reviews it in the same context. Use independent subagents.
- **Template-filling** — Handing templates to the user instead of extracting shape through dialogue. Produces bureaucratic docs, not doctrine.
