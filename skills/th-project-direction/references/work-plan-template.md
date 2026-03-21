# Work Plan Template

How to decompose aligned work into sequenced, modular chunks with reconciliation (Phase 4), and the complete output format.

---

## Work Plan Construction

### Linking to spec

Every work item must have one of:
- **Spec reference**: Specific section in a specification document that defines the expected behavior
- **Spec-first flag**: "Specification work is required before implementation" — in which case the first chunk IS writing/updating the spec

If a feature has no spec coverage, the work plan starts with writing the spec. Implementation chunks come after spec signoff.

### Signoff gates

Default: **user signoff is required before implementation begins**.

Signoff is NOT required for:
- Pure refactors that don't change behavior (but still need reconciliation)
- Bug fixes where spec already defines correct behavior
- Spec writing itself (but spec content needs signoff before implementation)

### Decomposing into chunks

Target: **3-10 hours per chunk**. Each chunk should be:
- Independently completable (can be committed and tested on its own)
- Clear objective (someone reading just the chunk description knows what to do)
- Verifiable (has acceptance criteria that can be checked)

#### Chunk template

```markdown
### Chunk {n}: {title}

**Objective**: {one sentence — what this chunk accomplishes}
**Spec reference**: {spec section} or "Spec work required"
**Dependencies**: {which prior chunks must be complete}
**Why ordered here**: {brief rationale for sequencing}
**Scope**: S / M / L / XL
**Parallelizable**: Yes / No — {reason}
**Serialize with**: {chunk IDs that would conflict}

**Acceptance criteria**:
- [ ] {concrete, testable criterion}
- [ ] {concrete, testable criterion}

**Notes**: {implementation hints, gotchas, or constraints}
```

### Parallelization guidance

Be conservative. Parallelization is safe when:
- Chunks touch different files/modules with no shared interfaces
- No shared test fixtures or config changes
- No database migrations in either chunk
- No architectural decisions that could change the other chunk's approach

Parallelization is unsafe when:
- Chunks modify the same module or shared interfaces
- One chunk introduces types/patterns the other depends on
- Either chunk involves schema changes
- Chunks touch the same config files (CI, build, env)

When in doubt, serialize. The cost of coordination failures (merge conflicts, repeated test runs, architecture churn) exceeds the benefit of parallelism.

### Reconciliation steps

After each completed chunk, add a reconciliation task:

```markdown
### Reconciliation: {chunk title}

Check:
- [ ] Implemented behavior matches spec section {ref}
- [ ] Tests cover the acceptance criteria from this chunk
- [ ] No drift was introduced to adjacent features
- [ ] No cleanup or follow-up edits needed
- [ ] Spec is still accurate (update if implementation revealed spec gaps)
```

Reconciliation applies regardless of who/what did the work — person, subagent, or automated pipeline.

For multi-chunk work blocks, also add a **block-level reconciliation** after the final chunk:

```markdown
### Block Reconciliation: {block title}

Check:
- [ ] All chunks' acceptance criteria are met
- [ ] End-to-end user flow works as spec describes
- [ ] No regression in adjacent features
- [ ] Spec sections referenced by this block are current
- [ ] Tech debt or follow-up work is documented (not left as TODO comments)
```

---

## Output Format

### 1. Executive summary

3 concise paragraphs:
- What the project is really trying to do (project spirit in one sentence)
- How aligned the current implementation is (cite the biggest gap and biggest strength)
- What the highest-priority next work should be (top 1-3 items with rationale)

### 2. Project spirit and requirements

```markdown
## Project Spirit

**Core problem**: {what this project exists to solve}
**Primary user**: {who it's for}
**Success looks like**: {concrete outcomes}
**Trying to be**: {aspirational identity}
**Not trying to be**: {explicit non-goals}

### Requirements

| # | Requirement | Class | Evidence | Status |
|---|------------|-------|---------|--------|
| 1 | {requirement} | Hard / Soft / Non-goal / Unknown | {file:line or spec:section} | Met / Partial / Unmet / N/A |

### Contradictions
{Where docs and code disagree, with evidence on both sides}
```

### 3. Current-state assessment

```markdown
## Current State

| Dimension | Status | Summary | Key Evidence |
|-----------|--------|---------|-------------|
| Spec adherence | Strong/Adequate/Weak/Missing | {one line} | {file:section} |
| Core workflows | Strong/Adequate/Weak/Missing | {one line} | {file:section} |
| Test confidence | Strong/Adequate/Weak/Missing | {one line} | {file:section} |
| Observability | Strong/Adequate/Weak/Missing | {one line} | {file:section} |
| Delivery readiness | Strong/Adequate/Weak/Missing | {one line} | {file:section} |
| Architectural fitness | Strong/Adequate/Weak/Missing | {one line} | {file:section} |
```

{Expand each dimension with evidence and "why it matters" paragraph.}

### 4. Alignment and tractability review

```markdown
## Alignment Review

### Aligned next steps
{Items going into the work plan, with alignment/value/leverage/tractability ratings}

### Misaligned directions
{Items that don't serve the project's purpose — with blunt explanation}

### Premature work
{Items that are aligned but not yet tractable — with what's needed first}

### Deferred
{Lower-priority items with criteria for when to revisit}

### Rejected
{Items that should not be done, with reasons}
```

### 5. Gap analysis

```markdown
## Gap Analysis

### Blockers
| Gap | Why it matters | Who | Evidence | Response | Effort |
|-----|---------------|-----|---------|----------|--------|

### Important Enhancements
| Gap | Why it matters | Who | Evidence | Response | Effort |
|-----|---------------|-----|---------|----------|--------|

### Strategic Gaps
| Gap | Why it matters | Who | Evidence | Response | Effort |
|-----|---------------|-----|---------|----------|--------|
```

### 6. Recommended work plan

```markdown
## Work Plan

### Immediate alignment work
{Spec updates, critical fixes, architecture prep — needed before feature work}

### Near-term delivery work
{Features and improvements that deliver user value}

### Strategic future work
{Investments that improve long-term viability}

{For each item, use the chunk template from above. Group chunks into logical blocks.}
```

### 7. Things not to do yet

```markdown
## Do Not Do Yet

| Item | Reason | Revisit when |
|------|--------|-------------|
| {feature/refactor} | {why not now} | {trigger for reconsideration} |
```

### 8. Appendix

```markdown
## Appendix

### A. Repository Map
{Languages, frameworks, entry points, major modules}

### B. Critical Workflows
{3-5 most important user journeys with component chain}

### C. Spec Inventory
{All specification documents with section count and coverage status}

### D. Evidence Index
{All files cited in the report}
```

### Blunt conclusion

End with exactly:

```markdown
---

## Conclusion

**Real direction**: {one sentence — what this project is actually becoming, based on evidence}

**Work on next**: {top 1-3 items, ordered}

**Stop pretending**: {what the project claims but can't yet deliver, if anything — or "Nothing to flag" if honest}
```
