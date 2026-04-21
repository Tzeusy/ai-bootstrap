# Curriculum Contract

Write the curriculum into the target repository's `curriculum/` path.

Use this contract unless the user explicitly asks for a different shape.

## Required Output Tree

```text
curriculum/
  README.md
  repository-thesis.md
  evidence-map.md
  research-ledger.md
  glossary.md
  mastery-rubric.md
  contribution-readiness.md
  open-questions.md
  paths/
    README.md
    NN-path-slug/
      README.md
      modules/
        NN-topic-slug.md
```

Use a single path when the whole curriculum fits cleanly under 100 hours. Use multiple path directories under `curriculum/paths/` when the prerequisite surface must be split into separate curricula to respect the 100-hour cap.

`modules/` should contain the actual learning sequence. Use zero-padded numeric prefixes such as `01-`, `02-`, `03-`.

## Time Budget Rules

- Each curriculum path must be at most 100 hours of estimated smart-human study time.
- Each module must be at most 10 hours.
- If a topic cluster would exceed 10 hours, split it into multiple modules.
- If the path would exceed 100 hours, split it into multiple curricula and document the split in `curriculum/paths/README.md`.

## Required Files

### `curriculum/README.md`

The landing page.

Include:

- who the curriculum is for
- the shortest-path learning order
- estimated effort or rough difficulty
- which topics are mandatory before reading code
- which topics can wait until first contribution work
- an overview table of curriculum paths or sections with:
  - why each path or section matters
  - estimated hours
  - a progress checklist using Markdown checkboxes

### `curriculum/repository-thesis.md`

Explain what the repository appears to do and why this curriculum exists.

Include:

- one-paragraph thesis of the project
- the major technical domains the learner will encounter
- the key mental-model gaps that would block comprehension without preparation
- clear statements of uncertainty when the repo is underdocumented
- a brief note on whether the curriculum is mostly evidence-backed or inference-heavy

### `curriculum/evidence-map.md`

A table that ties repository evidence to prerequisite topics.

Recommended columns:

- topic
- class (`foundation`, `system-model`, `repo-orientation`)
- required depth
- confidence (`direct`, `strong-inference`, `weak-inference`)
- why it matters here
- repo evidence
- when it becomes necessary

### `curriculum/research-ledger.md`

The audit trail for comprehensive prerequisite discovery.

Include:

- a short summary of pass 1, pass 2, and pass 3
- the angle each pass used
- the major concept clusters each pass surfaced
- concepts that appeared across multiple passes
- concepts that surfaced late and changed the curriculum
- whether additional passes were needed beyond the hard minimum of 3

### `curriculum/glossary.md`

Define essential terms, acronyms, and project vocabulary that appear in the curriculum or repository.

Prefer concise explanations that help a learner keep reading.

### `curriculum/open-questions.md`

Capture unresolved uncertainty instead of inventing confident curriculum claims.

Include:

- topics that are only weakly inferred
- evidence gaps that blocked stronger recommendations
- questions a maintainer or experienced contributor could answer
- any curriculum areas that should be revisited after those answers land

### `curriculum/mastery-rubric.md`

The learner-facing rubric for what counts as completion.

Include:

- the mastery levels used in this curriculum
- what `[ ]` vs `[X]` means in practical terms
- when a topic only needs `exposed` familiarity versus `working` or `contribution-ready`
- path-level guidance for when the learner is ready to move from study into real repo exploration

### `curriculum/contribution-readiness.md`

Turn the curriculum into a practical handoff for first contributions.

Include:

- what the learner should now be able to reason about
- which parts of the repo are safer first reading targets
- suggested first contribution categories
- hazard areas where incomplete understanding would be risky

### `curriculum/paths/README.md`

The curriculum planner and split-path index.

Include:

- whether this repo needs one curriculum path or multiple
- the rationale for each split if multiple paths exist
- total estimated hours per path
- a path-level progress checklist
- any path-level caveats driven by weak evidence or unresolved questions

### `curriculum/paths/NN-path-slug/README.md`

The overview for a single curriculum path.

Include:

- the path goal
- the learner profile this path targets
- total estimated hours, capped at 100
- an ordered section or module table with:
  - why the learner needs it
  - estimated hours
  - prerequisite dependencies
  - progress checkboxes
- a short "stop here if" note for learners who do not need deeper material

## Module Contract

Each `modules/NN-topic-slug.md` file should include:

- module title
- estimated smart-human study time, capped at 10 hours
- why this module matters before the repo makes sense
- learning goals
- core concepts to learn
- where those concepts show up in the repository
- common misunderstandings or failure modes
- explicit subsections for the actual technical deep dive
- sample Q&A at the end of every subsection
- explicit subsection progress checklists using Markdown checkboxes
- explicit subsection mastery checks grounded in the shared rubric
- self-check questions or small exercises
- a module-level mastery gate that defines what completion means
- what this module unlocks next

## Subsection Template

Every substantive subsection inside a module should follow this shape:

1. `Why This Matters Here`
2. `Technical Deep Dive`
3. `Where It Appears In The Repo`
4. `Sample Q&A`
5. `Progress`
6. `Mastery Check`

The `Progress` block should use updateable checkboxes, for example:

```markdown
### Progress
- [ ] Exposed: I can define the key terms in this subsection
- [ ] Working: I can explain the core idea in my own words
- [ ] Working: I can answer the sample Q&A without looking
```

The `Mastery Check` block should state the target level and what observable capability satisfies it, for example:

```markdown
### Mastery Check
Target level: `working`

You should be able to explain why this concept exists in the repository and answer the sample Q&A without notes.
```

## Validation

Before calling a generated curriculum done, it should pass:

```bash
uv run <skill-path>/scripts/validate_curriculum.py --target /path/to/repo
```

## Quality Bar

The completed `curriculum/` should:

- read as a learning path, not a dump of repo notes
- preserve a clear line from fundamentals to this repo
- distinguish required knowledge from deferable depth
- stay specific enough that a learner can return from the curriculum to the codebase with purpose
- avoid pretending the repo demands broader mastery than the evidence supports
- begin with a clear overview of sections and why they matter
- include deep-dive technical treatment rather than shallow glossaries alone
- include sample Q&A at the end of every subsection
- include explicit progress checkboxes throughout
- include a learner-facing mastery rubric plus concrete mastery checks at subsection and module level
- label weak evidence and unresolved questions instead of inventing certainty
- show that prerequisite discovery used at least 3 independent deep-dive passes and a reconciliation artifact
- respect the 10-hour module cap and 100-hour path cap
