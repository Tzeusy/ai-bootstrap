---
name: th-project-shape
description: >
  Analyze and bootstrap the four-pillar knowledge architecture of a software project:
  docs/heart-and-soul (doctrine), docs/law-and-lore (RFCs/design contracts), docs/lay-and-land
  (topology), and openspec/ (capability specs at root). Use when: starting a new project's
  knowledge structure, auditing documentation health, onboarding, deciding where ideas should
  be documented, translating ideas into requirements, or mapping system topology. Triggers:
  "project shape", "bootstrap docs", "where should this go", "what's this project about",
  "project pillars", "heart and soul", "spec structure", "knowledge architecture", "system
  map", "topology", "lay of the land", "set up project structure".
---

# Project Shape

A project's **shape** is the knowledge architecture that makes it comprehensible to both humans and LLMs. Shape is not code — it's the structured understanding that tells you *what* a project is, *why* it exists, *how* it works, and *what* must be built.

## The Four-Pillar Model

Every well-shaped project has four distinct knowledge layers, each answering a different question:

| Pillar | Folder | Local Skill | Question | Content |
|--------|--------|-------------|----------|---------|
| **Doctrine** | `docs/heart-and-soul/` | `heart-and-soul` | **WHY** does this exist? | Vision, principles, non-negotiables, scope boundaries, what it is NOT |
| **Design Contracts** | `docs/law-and-lore/` | `law-and-lore` | **HOW** will it work? | RFCs, design docs, wire contracts, state machines, reviews, trade-offs |
| **Capability Specs** | `openspec/` | `spec-and-spine` | **WHAT** exactly must be built? | Normative requirements, WHEN/THEN scenarios, testable acceptance criteria |
| **Topology** | `docs/lay-and-land/` | `lay-and-land` | **WHERE** does everything live and connect? | Component diagrams, dependency boundaries, data flow, deployment topology, integration maps |

Three pillars live under `docs/` — human-authored knowledge with poetic names. `openspec/` stays at root because it's a product with its own structure and conventions.

The pillars form a **traceability chain**:

```
Doctrine principle → RFC design decision → Spec requirement → Code → Test
          ↕                  ↕                    ↕              ↕
      Topology map: where components live, how they connect, what boundaries exist
```

Every implementation decision should trace back through this chain. The topology layer cross-cuts all others — it shows *where* the doctrine is embodied, *where* the design contracts apply, and *where* the specs are implemented.

## Quick Start: Assess a Project's Shape

Run the scan script to discover existing shape artifacts:

```bash
bash <skill-path>/scripts/shape-scan.sh [project-root]
```

This produces a health report showing which pillars exist, their maturity, and gaps.

### Manual Assessment

If scanning isn't available, check for these signals:

1. **Doctrine exists?** — Look for: `docs/heart-and-soul/`, `heart-and-soul/`, `vision.md`, `MANIFESTO.md`, `PHILOSOPHY.md`, or doctrine-like content in `README.md`
2. **Design contracts exist?** — Look for: `docs/law-and-lore/`, `docs/rfcs/`, `docs/adrs/`, numbered design docs, review rounds
3. **Specs exist?** — Look for: `openspec/`, `specs/`, `requirements/`, files with WHEN/THEN scenarios, formal requirement IDs
4. **Topology exists?** — Look for: `docs/lay-and-land/`, `maps/`, `architecture/`, component diagrams, deployment docs, `ARCHITECTURE.md`

Rate each pillar: **absent** → **nascent** (scattered, informal) → **structured** (dedicated folder, some coverage) → **mature** (comprehensive, traceable, maintained)

## Workflow 1: Bootstrap Shape for a New Project

Bootstrapping is a **consultative process**, not a template-filling exercise. The LLM must extract shape from the human's head through structured dialogue, synthesis, and adversarial review.

### Quality Requirements

- **Use the most capable model available** with maximum thinking/reasoning budget
- **Never self-review** — use independent subagents for review (see below)
- **Challenge the user** — accept vague answers only to push deeper, never to ship

### The Process

1. **Consultative interview** — Structured Socratic extraction across five tracks (identity, boundaries, principles, architecture, contracts). Read `references/consultative-bootstrapping.md` for the full protocol with question banks and challenge patterns.

2. **Synthesize** — Distill interview answers into draft documents. Use the human's own language. Make implicit trade-offs explicit. Flag contradictions.

3. **Independent review** — Spawn fresh subagents (no generation context) to review each document. Read `references/review-protocol.md` for the three review agent specs (Coherence, Adversarial, Cross-Pillar).

4. **Revise and present** — Incorporate review findings, present to user for validation. If the user says "not quite right," return to the interview — don't patch.

5. **Scaffold and install** — Run `shape-init.sh` for directory structure, populate with reviewed documents, install local skills.

### Pillar Order

Work top-down — each pillar grounds the next:

```
docs/heart-and-soul/  →  docs/law-and-lore/  →  openspec/  →  docs/lay-and-land/
     (WHY)                    (HOW)               (WHAT)          (WHERE)
```

Topology (lay-and-land) can be started in parallel with design contracts once the architecture interview track is complete.

Read `references/bootstrapping.md` for phase-by-phase details.

## Workflow 2: Translate Ideas into Requirements

The shape model provides a natural funnel for turning ideas into code:

```
Idea/Insight
  ↓  "Does this align with doctrine?"
docs/heart-and-soul/ review
  ↓  "Where does this live in the system?"
docs/lay-and-land/ topology check
  ↓  "How would this work technically?"
docs/law-and-lore/ RFC draft
  ↓  "What exactly must be built and tested?"
openspec/ capability spec
  ↓  "Create beads for implementation"
bd create ...
```

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

### Maintenance Protocol

When code changes diverge from documentation:

1. **Detect** — Compare implementation against spec requirements, RFC contracts, and doctrine
2. **Update** — Generate updated sections for affected documents
3. **Review the delta** — Spawn independent review agents on changed sections (not the full doc)
4. **Cross-check** — Run cross-pillar review if changes affect multiple pillars
5. **Present to user** — Show diff with review summary before committing

### Related Skills

Use `/th-project-direction` for a full direction analysis including priority-weighted work plans. Use `/th-reconcile-spec-to-project` for detailed spec-code divergence detection.

## Reference Index

### Pillar Guides

| Pillar | Reference | Read when... |
|--------|-----------|-------------|
| Doctrine | `references/pillar-heart-and-soul.md` | Bootstrapping vision, writing non-negotiables, scoping v1 |
| Design Contracts | `references/pillar-law-and-lore.md` | Structuring RFCs, running reviews, capturing trade-offs |
| Capability Specs | `references/pillar-spec-and-spine.md` | Writing requirements, WHEN/THEN scenarios, spec lifecycle |
| Topology | `references/pillar-lay-and-land.md` | Mapping components, boundaries, data flow, deployment |

### Process Guides

| Guide | Reference | Read when... |
|-------|-----------|-------------|
| Consultative Bootstrapping | `references/consultative-bootstrapping.md` | Extracting shape from a human for a new project — interview tracks, challenge patterns, synthesis rules |
| Review Protocol | `references/review-protocol.md` | Reviewing generated docs with independent subagents — agent specs, iteration rules, anti-patterns |
| Bootstrapping Phases | `references/bootstrapping.md` | Step-by-step phase guide for establishing shape from scratch |
| Local Skill Templates | `references/local-skill-templates.md` | Installing agent navigation skills for each pillar |

## Local Skill Installation

Each pillar should have a corresponding local skill in `.claude/skills/` (and equivalent for other tools). These skills teach LLM agents how to navigate and use each pillar.

Read `references/local-skill-templates.md` for templates. The key principle: local skills are **indexes with selection guidance**, not duplicates of the content. They tell the agent *which file to read* for a given task, not *what the file says*.

All four pillars should have a corresponding local skill: `heart-and-soul`, `law-and-lore`, `spec-and-spine`, `lay-and-land`.

## Anti-Patterns

- **README-as-doctrine** — A README describes the project to users. Doctrine defines what the project *believes*. Don't conflate them.
- **Monolith docs** — One giant ARCHITECTURE.md mixing vision, design, and specs. Split into pillars.
- **Specs without doctrine** — Requirements with no philosophical grounding get challenged endlessly. Doctrine ends debates.
- **Doctrine without specs** — Beautiful principles that never become testable requirements. Specs make doctrine actionable.
- **Stale middle** — Doctrine and code are current, but RFCs are from six months ago. Design contracts must evolve.
- **Pillar without skill** — The knowledge exists but agents can't find it. Install local skills.
- **Self-reviewed docs** — The LLM that wrote the doc reviews it in the same context. Use independent subagents.
- **Template-filling** — Handing templates to the user instead of extracting shape through dialogue. Produces bureaucratic docs, not doctrine.
