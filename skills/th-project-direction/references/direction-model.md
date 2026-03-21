# Direction Model

How to build the project's direction model (Phases 1-2). This is the foundation — all alignment review, gap analysis, and work planning depend on it.

---

## Phase 1: Project Spirit & Requirements

### 1.1 Determine project spirit

Answer these questions with evidence:

| Question | Where to look |
|----------|--------------|
| What core problem does this project solve? | README first paragraph, package description, spec overview |
| Who is the primary user? | README, examples, API surface, UI flows |
| What does success look like? | Spec acceptance criteria, benchmarks, examples, tests |
| What is it trying to be? | Architecture choices, abstractions, scope of features |
| What is it explicitly NOT trying to be? | Non-goals sections, limitations docs, rejected RFCs |

If the project spirit is unclear from docs, infer it from what was actually built. Note the inference.

### 1.2 Classify requirements

| Classification | Definition | Evidence sources |
|---------------|-----------|-----------------|
| **Hard requirements** | Must-have for the project to fulfill its purpose | Spec "MUST" / "SHALL", core test assertions, CI gates |
| **Soft requirements** | Preferred but negotiable | Spec "SHOULD", open issues, TODO comments |
| **Non-goals** | Explicitly out of scope | Non-goals sections, rejected PRs/RFCs, architecture constraints |
| **Unknowns** | Not addressed, unclear intent | Missing spec sections, ambiguous code, no tests |

### 1.3 Separate explicit from implicit goals

**Explicit goals**: Stated in README, specs, docs, package metadata, roadmap.

**Implicit goals**: Not documented but suggested by:
- Architecture patterns (e.g., plugin system implies extensibility is a goal)
- Abstraction choices (e.g., provider interface implies multi-backend support)
- Test coverage patterns (e.g., heavy integration tests imply reliability priority)
- CI/CD sophistication (e.g., canary deploys imply production-grade ambitions)
- Dependency choices (e.g., using a specific framework implies its ecosystem's patterns)

**Important**: Implicit goals are inferences. Label them as such. They may be accidental complexity rather than intentional design.

### 1.4 Reality check

Assess tractability honestly:

| Dimension | Question | Red flags |
|-----------|----------|-----------|
| **Scope** | Is the stated scope achievable for this team/maturity? | >20 open "core" features, README promises more than code delivers |
| **Architecture** | Does the current design support the stated direction? | Major features require architectural rewrites |
| **Maturity** | Is the project trying to be production-grade before it has basic correctness? | Security hardening with no tests, observability with broken core flows |
| **State of art** | Are any proposed features beyond what's currently feasible? | Custom ML models for niche tasks, real-time at impossible scale |

If the project is overreaching, say so directly with evidence.

---

## Phase 2: Current State Assessment

Evaluate each dimension. For each, assign:
- **Strong**: Reliable, well-implemented, supports future work
- **Adequate**: Works but has gaps; doesn't block near-term progress
- **Weak**: Significant issues; may block or destabilize future work
- **Missing**: Not addressed at all

### 2.1 Specification adherence

If the project has specs (openspec/, spec/, design docs):

**Step 1**: Inventory all spec documents and their sections.
```
Glob: "openspec/**/*.md", "spec/**/*.md", "docs/design/**/*.md"
```

**Step 2**: For each spec section, determine status:

| Status | Definition |
|--------|-----------|
| **Implemented** | Code matches spec; tests validate behavior |
| **Partially implemented** | Some aspects work, others missing or diverged |
| **Contradicted** | Code does something different than spec states |
| **Missing** | Spec requires it, code doesn't address it |
| **Exceeds spec** | Code does more than spec requires (may indicate spec drift) |

**Step 3**: Note which direction the drift goes:
- Is the code ahead of the spec? (Spec needs updating)
- Is the spec ahead of the code? (Implementation needed)
- Are they diverging? (Realignment needed)

### 2.2 Core workflow completeness

Identify the 3-5 most important user journeys. For each:

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

The critical question: **Does the current architecture support the intended direction?**

Look for:
- Features that require architectural changes to implement
- Abstractions that fight the intended use patterns
- Coupling that makes intended changes expensive
- Missing extension points for planned features
- Technical debt that compounds with each new feature

If the architecture doesn't support the direction, this is a blocker that must appear early in the work plan.

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
