# Direction Model

Analysis dimensions Phase 2 agents apply when building the project's direction model — the foundation all alignment review, gap analysis, and work planning depend on. These are document sections, not workflow phases: everything here happens inside SKILL.md Phase 2 (Specification Scan + Fitness/Gap Synthesis).

Agents A/B/C each apply a disjoint slice (see Phase 2 table in SKILL.md + `subagent-template.md`):
- **Agent A** — doctrine/spec intent: Section 1 (spirit, requirement classification, reality check) + Section 2.1 (spec-intent fidelity).
- **Agent B** — spec adherence & workflows: Sections 2.1-2.2.
- **Agent C** — implementation fitness: Sections 2.3-2.6.

---

## Section 1: Project Spirit & Requirements

### 1.1 Determine project spirit

Answer with evidence:

| Question | Where to look |
|----------|--------------|
| What core problem does this project solve? | README first paragraph, package description, spec overview |
| Who is the primary user? | README, examples, API surface, UI flows |
| What does success look like? | Spec acceptance criteria, benchmarks, examples, tests |
| What is it trying to be? | Architecture choices, abstractions, scope of features |
| What is it explicitly NOT trying to be? | Non-goals sections, limitations docs, rejected RFCs |

Spirit unclear from docs → infer from what was actually built. Note the inference.

### 1.2 Classify requirements

| Classification | Definition | Evidence sources |
|---------------|-----------|-----------------|
| **Hard requirements** | Must-have for the project to fulfill its purpose | Spec "MUST" / "SHALL", core test assertions, CI gates |
| **Soft requirements** | Preferred but negotiable | Spec "SHOULD", open issues, TODO comments |
| **Non-goals** | Explicitly out of scope | Non-goals sections, rejected PRs/RFCs, architecture constraints |
| **Unknowns** | Not addressed, unclear intent | Missing spec sections, ambiguous code, no tests |

### 1.3 Separate explicit from implicit goals

**Explicit goals**: stated in README, specs, docs, package metadata, roadmap.

**Implicit goals**: undocumented but suggested by:
- Architecture patterns (plugin system → extensibility is a goal)
- Abstraction choices (provider interface → multi-backend support)
- Test coverage patterns (heavy integration tests → reliability priority)
- CI/CD sophistication (canary deploys → production-grade ambitions)
- Dependency choices (a specific framework → its ecosystem's patterns)

**Important**: implicit goals are inferences — label them. May be accidental complexity, not intentional design.

### 1.4 Reality check

Assess tractability honestly:

| Dimension | Question | Red flags |
|-----------|----------|-----------|
| **Scope** | Is the stated scope achievable for this team/maturity? | >20 open "core" features, README promises more than code delivers |
| **Architecture** | Does the current design support the stated direction? | Major features require architectural rewrites |
| **Maturity** | Is the project trying to be production-grade before it has basic correctness? | Security hardening with no tests, observability with broken core flows |
| **State of art** | Are any proposed features beyond what's currently feasible? | Custom ML models for niche tasks, real-time at impossible scale |

Project overreaching → say so directly with evidence.

---

## Section 2: Current State Assessment

Evaluate each dimension. For each, assign:
- **Strong**: Reliable, well-implemented, supports future work
- **Adequate**: Works but has gaps; doesn't block near-term progress
- **Weak**: Significant issues; may block or destabilize future work
- **Missing**: Not addressed at all

### 2.1 Specification adherence

If specs exist (openspec/, spec/, design docs):

**Step 1**: Inventory all spec documents and sections.
```
# Glob tool (Claude Code/Codex): openspec/**/*.md, spec/**/*.md, docs/design/**/*.md
# or shell-side: find openspec spec docs/design -name '*.md' 2>/dev/null
```

**Step 2**: For each spec section, determine status:

| Status | Definition |
|--------|-----------|
| **Implemented** | Code matches spec; tests validate behavior |
| **Partially implemented** | Some aspects work, others missing or diverged |
| **Contradicted** | Code does something different than spec states |
| **Missing** | Spec requires it, code doesn't address it |
| **Exceeds spec** | Code does more than spec requires (may indicate spec drift) |

**Step 3**: Note drift direction:
- Code ahead of spec → spec needs updating
- Spec ahead of code → implementation needed
- Diverging → realignment needed

### 2.2 Core workflow completeness

Identify the 3-5 most important user journeys. Per journey:

| Aspect | Check |
|--------|-------|
| End-to-end path | Does it work from entry point to completion? |
| Error paths | Are failures handled gracefully? |
| Edge cases | Are known edge cases covered? |
| Demo vs real | Is this a demo-quality path or production-quality? |
| Seams | Where are the brittle connections between components? |

### 2.3 Test confidence

For core workflows:
```
Grep: pattern="describe\(|test\(|it\(|def test_|func Test" glob="*.{ts,py,go,rs}" output_mode="count"
Glob: "**/tests/**/*", "**/__tests__/**/*", "**/*_test.*", "**/*_spec.*"
```

Assess:
- Are critical paths covered by tests?
- Do tests validate behavior (what) or implementation (how)?
- Are there integration tests that exercise real dependencies?
- What would break silently if someone changed core logic?

### 2.4 Observability and diagnosability

Appropriate for maturity level:

| Maturity | Minimum expectation |
|----------|-------------------|
| Prototype | Console logging, error messages |
| Beta | Structured logging, basic error reporting |
| Production | Structured logs + metrics + tracing + health checks |
| Mission-critical | Full observability + alerting + runbooks + correlation IDs |

### 2.5 Delivery readiness

| Aspect | Check |
|--------|-------|
| CI protection | Do tests run on every PR? Do they block merge? |
| Release process | Is it automated? Repeatable? Safe to rollback? |
| Migration safety | Can schema/data changes be rolled back? |
| Environment parity | Do dev/staging/prod use the same infra patterns? |

### 2.6 Architectural fitness

Critical question: **Does the current architecture support the intended direction?**

Look for:
- Features requiring architectural changes to implement
- Abstractions that fight intended use patterns
- Coupling that makes intended changes expensive
- Missing extension points for planned features
- Tech debt that compounds with each new feature

Architecture doesn't support the direction → blocker; must appear early in the work plan.

---

## Deliverable

A structured direction model containing:

1. **Project spirit summary** (2-3 paragraphs)
2. **Requirements classification** (hard/soft/non-goals/unknowns table)
3. **Explicit vs implicit goals** (with evidence and inference labels)
4. **Reality check** (tractability assessment, overreach warnings)
5. **Current state assessment** (6 dimensions, each with status/evidence/why-it-matters)
6. **Key contradictions** between docs/specs and implementation
7. **Architectural fitness verdict** — does the architecture support the direction?
