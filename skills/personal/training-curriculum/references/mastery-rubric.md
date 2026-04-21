# Mastery Rubric

Use this rubric so curriculum progress means demonstrated understanding, not passive reading.

## Rule

Do not let a section imply mastery unless the learner can explain the idea, answer challenge questions, and connect the concept back to the repository.

Mark `[X]` only when the checkbox statement is observably true, not merely because the learner skimmed the prose.

## Recommended Levels

Use these levels when writing module or subsection completion criteria:

| Level | Meaning | Typical evidence |
|-------|---------|------------------|
| `exposed` | The learner has read the material and recognizes the vocabulary | Can define the main terms and identify where they appear |
| `working` | The learner can reason with the concept in this repo's context | Can answer sample Q&A and explain repo relevance without notes |
| `contribution-ready` | The learner can use the concept to make or review safe changes | Can predict failure modes, trade-offs, or implementation risks in this repo |

Most prerequisite subsections should target `working`. Escalate to `contribution-ready` only when the concept is directly relevant to safe modification of the repository.

## Converting Levels Into Checkboxes

Prefer checkboxes that describe observable capability:

```markdown
### Progress
- [ ] Exposed: I can define the key terms in this subsection
- [ ] Working: I can answer the sample Q&A without notes
- [ ] Working: I can explain where this concept appears in the repository
```

For high-risk or implementation-heavy topics, extend the block:

```markdown
### Progress
- [ ] Exposed: I can define the key terms in this subsection
- [ ] Working: I can answer the sample Q&A without notes
- [ ] Working: I can explain where this concept appears in the repository
- [ ] Contribution-ready: I can explain at least one failure mode or trade-off this repo faces here
```

## Module-Level Completion Criteria

Every module should end with a mastery gate stating what "done" means.

A good module mastery gate usually includes:

- can summarize the module's core concepts in plain language
- can answer the hardest subsection Q&A without notes
- can point to the relevant files, systems, or architecture surfaces in the repo
- can explain at least one common misunderstanding or hazard

## Path-Level Completion Criteria

A path is complete when the learner can:

- explain why each module exists
- trace the core prerequisite topics into this repository's architecture
- identify which areas of the repo are now safe to read or change
- identify which advanced areas still need deeper study

## Anti-Patterns

- checkbox items like "read this section" as the only completion signal
- vague statements like "understand networking"
- contribution-ready labels on topics that only need vocabulary familiarity
- making the rubric so strict that every subsection becomes a mini exam
