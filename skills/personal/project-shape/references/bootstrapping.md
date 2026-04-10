# Bootstrapping Project Shape

Step-by-step guide for establishing the five-pillar knowledge architecture from scratch.

## Prerequisites

- A project with a clear purpose (even if only in the founder's head)
- Willingness to write before coding

## Phase 1: Doctrine (about/heart-and-soul/)

**Goal**: Capture what the project believes before anyone writes code.

### Step 1: Write vision.md

Answer these questions in ~75-150 lines:

1. **What is this?** — One paragraph thesis statement
2. **What is this NOT?** — Equally important. Prevents scope creep. List 3-5 explicit non-goals.
3. **Non-negotiable rules** — 5-7 numbered principles the code must embody. These become the north star for all design decisions.
4. **Success criteria** — How do you know this project is working?

### Step 2: Write v1.md

Define the scope boundary:

1. **V1 ships** — Explicit list of what the first version includes
2. **V1 defers** — Explicit list with rationale for each deferral
3. **Platform targets** — Where does v1 run?
4. **Quality bar** — Performance, reliability, UX thresholds

### Step 3: Add domain files as needed

Only when a domain has principles worth codifying. Common early additions:
- `security.md` — If the project handles sensitive data or multi-tenant access
- `failure.md` — If reliability/degradation matters

### Step 4: Write README.md

An index file with one-line descriptions and a recommended reading order. Not doctrine itself — a map to doctrine.

## Phase 2: Engineering Standards (about/craft-and-care/)

**Goal**: Make the execution-quality bar explicit before implementation planning begins.

This pillar is mandatory for all non-trivial implementation work. Keep it stack-neutral: define
what evidence, hygiene, review quality, operability, and maintainability are expected, not which
libraries or tools to use.

### Step 1: Write engineering-bar.md

Capture the baseline standards that apply broadly:

1. **Definition of done** — What must be true before a change is considered complete?
2. **Clarity and maintainability bar** — What makes a change readable, reviewable, and safe to extend?
3. **Change hygiene** — What kinds of hidden coupling, dead code, unclear naming, or partial rollouts are unacceptable?

### Step 2: Write testing-and-verification.md

Define how the project earns confidence:

1. **Evidence expectations** — What forms of verification are expected for different change types?
2. **Regression discipline** — What does a good bug fix or risky refactor require?
3. **Verification before merge** — What must the author prove?

### Step 3: Add domain standards as needed

Only when the project's risk profile warrants them. Common additions:
- `observability-and-operations.md`
- `interfaces-and-dependencies.md`
- `review-and-documentation.md`
- `security-and-secrets.md`
- `performance-discipline.md`

### Step 4: Keep it standards-level

`craft-and-care` should define enduring engineering principles and reviewable expectations.
Detailed runbooks, CI recipes, and tool-specific instructions belong elsewhere and may be linked.

## Phase 3: Design Contracts (about/law-and-lore/)

**Goal**: Capture technical decisions in reviewable, numbered documents.

### When to start

Start writing RFCs when you're making technical decisions that:
- Affect multiple parts of the system
- Define wire formats or protocols
- Establish performance budgets
- Will be hard to change later

### Step 1: Create about/law-and-lore/rfcs/

Write your first RFC for the most foundational subsystem. Number it `0001`.

### Step 2: Establish review discipline

Even solo projects benefit from review rounds — your future self (or an LLM agent) reviewing past decisions and their rationale.

### Step 3: Cross-reference doctrine

Every RFC should reference the doctrine principles it implements. This creates the traceability chain.

## Phase 4: Capability Specs (openspec/)

**Goal**: Extract testable requirements from design contracts.

### When to start

Start writing specs when:
- Design contracts are stable enough to extract requirements
- You're about to begin implementation
- You need clear acceptance criteria for tasks or implementation planning

### Step 1: Set up openspec/

Create the folder structure with a config and your first change.

### Step 2: Write specs by domain

One spec file per subsystem/domain. Each requirement must have:
- Normative text (SHALL/MUST)
- Source traceability (RFC section)
- Scope tag (v1-mandatory, v1-reserved, post-v1)
- WHEN/THEN scenarios

### Step 3: Generate tasks

Use the spec requirements to create implementation tasks or work items. Each v1-mandatory requirement generates one or more tasks.

## Phase 5: Topology (about/lay-and-land/)

**Goal**: Document where components live, how they connect, and what boundaries exist.

### When to start

Start mapping topology when:
- The project has more than one major component or subsystem
- You're making deployment or infrastructure decisions
- New contributors (human or LLM) struggle to find where things live
- Integration between subsystems becomes non-trivial

### Step 1: Create about/lay-and-land/

Start with `components.md` — an inventory of what exists and who owns what.

### Step 2: Add data flow and deployment

As the system grows, document how data moves (`data-flow.md`) and where things run (`deployment.md`).

### Step 3: Include diagrams

Visual maps are more effective than prose. Use Mermaid (version-controllable) or Excalidraw (hand-drawn feel). Store sources in `about/lay-and-land/assets/`.

### Step 4: Cross-reference other pillars

Annotate the topology with which RFCs govern which boundaries, and which doctrine principles justify the structure.

## Phase 6: Local Skills

**Goal**: Make the knowledge navigable by LLM agents.

### Step 1: Create skill directories

```bash
mkdir -p .claude/skills/{heart-and-soul,law-and-lore,spec-and-spine,lay-and-land}
# Repeat for .codex/skills/ and .gemini/skills/ if needed
# Note: docs/ pillars use poetic names as folder names; local skills match
```

### Step 2: Write SKILL.md for each

**Preferred:** Run `shape-init.sh --skills-only` which generates correctly-formatted skills automatically.

**If writing manually:** Every SKILL.md **MUST** start with YAML frontmatter (`---` delimiters with `name` and `description` fields). Without frontmatter, skill loaders silently reject the file. Use the templates from `references/local-skill-templates.md` and customize the index tables with your actual files and domains.

### Step 3: Validate format

Run `shape-scan.sh` and check that all five skills show `[VALID]` frontmatter. Fix any `[INVALID]` warnings before committing.

### Step 4: Run package self-checks

Before relying on the scaffold, run:

```bash
bash <skill-path>/scripts/shape-scan.sh [project-root]
bash <skill-path>/scripts/self-test.sh
```

Interpret the scan using `references/maturity-rubric.md`. A fully scaffolded project should not be considered mature until authored content and traceability are in place.

### Step 5: Test navigation

Start a new LLM session and try tasks that should trigger each skill. Verify the agent finds the right files.

## Timeline Guidance

| Project stage | Pillars to prioritize |
|--------------|----------------------|
| Idea / exploration | Doctrine only (vision.md, v1.md) |
| Design / pre-implementation | Doctrine + Craft and Care + Design Contracts |
| Implementation starting | All five pillars + local skills |
| Mature / multiple contributors | All five, plus regular shape health audits |

## Common Mistakes

- **Starting with specs** — Specs without doctrine get challenged endlessly. Write vision first.
- **Skipping craft-and-care** — Projects then smuggle engineering standards into doctrine, RFCs, PR comments, or tribal habit. Make the execution bar explicit.
- **Skipping RFCs** — Going straight from vision to spec misses the "how." Design contracts capture trade-offs.
- **Writing all doctrine at once** — Start with vision + v1. Add domain files as those domains become active.
- **Copying templates verbatim** — The templates are starting points. Heavy customization is expected.
