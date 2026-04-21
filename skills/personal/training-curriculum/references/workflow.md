# Workflow

Use this flow every time you build a repo-specific prerequisite curriculum.

## Goal

Produce a `curriculum/` directory that teaches the minimum technical background someone needs before the repository's own code and docs become legible.

The curriculum should move through three layers:

1. Foundation topics the learner may need before the repo makes sense
2. System-model topics that explain how the repo's main technical domain behaves
3. Repo-specific orientation that connects those concepts back to concrete files, subsystems, and contribution paths

Every curriculum path must stay within these pacing limits:

- maximum 100 hours estimated smart-human study time per curriculum path
- maximum 10 hours per module
- split into separate curriculum paths when the prerequisite surface exceeds those limits

## Phase 1: Survey The Repository

Start with evidence gathering, not curriculum writing.

Inspect at least:

- top-level README and contributor docs
- package manifests, dependency files, build scripts, and lockfiles
- deployment and CI configuration
- architecture docs, RFCs, specs, and diagrams
- top-level directories and subsystem names
- tests that reveal behavior, invariants, or domain vocabulary

If the repo already has architecture, RFC, or onboarding docs, treat them as evidence surfaces. Do not duplicate them into the curriculum unless a learner genuinely needs a prerequisite-focused rewrite.

Capture strong signals such as:

- protocol names
- concurrency models
- storage engines
- media or graphics pipelines
- cryptography or auth boundaries
- networking assumptions
- domain math or algorithms
- framework/runtime constraints

If the repo lacks docs, infer from code and configuration, but label that inference later in the curriculum.

## Phase 2: Build The Prerequisite Map

For each candidate topic, record:

- the topic name
- why it matters for this repo
- the repository evidence behind it
- the confidence level (`direct`, `strong-inference`, `weak-inference`)
- the required depth
- whether it is `must know before reading code`, `must know before changing code`, or `nice to know later`

Use the depth levels from `topic-discovery.md`:

- `glossary` — learn the terms well enough to follow discussion
- `working` — understand the mechanics well enough to reason through code paths
- `implementation` — understand the trade-offs deeply enough to modify the system safely

Delete any topic that does not materially improve comprehension or contribution readiness.
If a topic only survives on `weak-inference`, prefer surfacing it as an open question or deferable area instead of presenting it as a firm prerequisite.

## Phase 3: Sequence The Curriculum

Create the shortest learning path that respects dependency order.

Good ordering usually looks like:

1. core domain model
2. transport/runtime/storage fundamentals
3. failure modes and constraints
4. this repo's architecture and vocabulary
5. safe-first contribution guidance

Group closely related topics into modules rather than writing one file per buzzword. A strong curriculum usually lands around 4-8 modules.

Budget the sequence before writing:

- estimate hours per module
- ensure no module exceeds 10 hours
- ensure the full path stays at or below 100 hours
- if the path would exceed 100 hours, split it into multiple curricula with a shared index under `curriculum/`

Use splitting to preserve coherence, not to game the limits. Good split points include:

- protocol/networking foundations vs media pipeline internals
- runtime/concurrency foundations vs deployment/operations depth
- generic domain fundamentals vs repo-specific advanced architecture

## Phase 4: Write The Curriculum

Before writing, scaffold the output tree if needed:

```bash
uv run <skill-path>/scripts/scaffold_curriculum.py --target /path/to/repo
```

If you already know the first real path and module you are creating, scaffold them directly:

```bash
uv run <skill-path>/scripts/scaffold_curriculum.py \
  --target /path/to/repo \
  --path-slug foundations \
  --module-slug architecture-prereqs
```

Then fill the files defined in `curriculum-contract.md`.

Each module should explain:

- why the learner needs this before the repo will make sense
- what concepts they must understand
- where those concepts appear in the repository
- what misunderstandings will cause confusion or bad changes
- what this module unlocks next
- how long the module should take, staying within the 10-hour cap

Within each module, structure subsections so they all include:

- a short reason this subsection matters here
- the actual technical deep dive
- sample Q&A that challenges recall and reasoning
- an explicit progress checklist using Markdown checkboxes
- mastery criteria aligned with `references/mastery-rubric.md`

After writing or updating the curriculum, validate it:

```bash
uv run <skill-path>/scripts/validate_curriculum.py --target /path/to/repo
```

## Phase 5: Final Review

Check the finished curriculum against these questions:

- Does every module trace back to repo evidence?
- Is the sequence dependency-aware, or does it assume concepts before teaching them?
- Does it separate background learning from repo-specific onboarding?
- Are must-know topics distinguished from deferable topics?
- Is jargon defined before use or captured in `glossary.md`?
- Would a new contributor know what they can safely read or change after finishing the curriculum?
- Does the overview clearly enumerate sections, why they matter, and the study-time budget?
- Does every subsection end with sample Q&A and updateable `[ ]` or `[X]` progress markers?
- Do the progress markers reflect mastery criteria instead of mere reading completion?
- Do all budgets stay within 10 hours per module and 100 hours per curriculum path?
- Are weak inferences labeled clearly enough that the curriculum fails closed instead of fabricating certainty?
- Does `validate_curriculum.py` pass on the final output?

## Anti-Patterns

- Writing a generic textbook with weak repo ties
- Mirroring the source tree instead of teaching prerequisite concepts
- Listing tools and frameworks without explaining why they matter here
- Including every adjacent topic "just in case"
- Hiding inference behind overconfident prose
- Creating oversized mega-modules instead of splitting the learning path
- Treating progress tracking or Q&A as optional polish instead of part of the contract
