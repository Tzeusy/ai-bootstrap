# Alignment & Tractability Review

How to evaluate proposed work against project direction. The synthesis dimension Agent D applies in SKILL.md Phase 2 after Agents A/B/C produce evidence; also the core of the **feature-evaluation** focus mode. Determines what to do, defer, reject. Output (alignment matrix, classification, push-back list, gaps, spec deltas) feeds the Phase 2 changeset + Phase 3 sequencing.

---

## Evaluation Framework

Evaluate every proposed feature/improvement/refactor/roadmap item across 8 dimensions:

### 1. Alignment with project spirit

| Rating | Definition |
|--------|-----------|
| **Core** | Directly serves the project's primary purpose |
| **Supporting** | Enables or improves core functionality |
| **Adjacent** | Useful but not central; could live in a separate package |
| **Misaligned** | Contradicts project direction, dilutes focus, or serves a different audience |

### 2. User value

| Rating | Definition |
|--------|-----------|
| **High** | Unblocks a primary user workflow or fixes a painful gap |
| **Medium** | Improves experience for common use cases |
| **Low** | Nice-to-have; affects edge cases or minor workflows |
| **None** | Internal improvement only; no user-visible impact |

### 3. Leverage

How much future work does this enable or simplify?
- **High leverage**: Unlocks multiple downstream features, removes a systemic bottleneck
- **Medium leverage**: Enables 1-2 future items
- **Low leverage**: Isolated improvement, no downstream benefit

### 4. Tractability

Can this actually be done well, right now?

| Assessment | Criteria |
|-----------|---------|
| **Ready** | Spec is clear, architecture supports it, dependencies are met |
| **Needs spec** | Implementation direction is unclear; spec work required first |
| **Needs architecture** | Current design doesn't support it; refactoring required first |
| **Blocked** | External dependency, missing tooling, or prerequisite not met |
| **Infeasible** | Beyond current state of art, or fundamentally incompatible with project |

### 5. Timing

| Assessment | Criteria |
|-----------|---------|
| **Now** | High value, ready, no blockers |
| **Soon** | High value but needs prep work first |
| **Later** | Medium value, or dependencies not yet resolved |
| **Never** | Misaligned, infeasible, or premature |

### 6. Dependencies

What must exist before this work can begin?
- Spec sections that must be written
- Architecture changes that must land first
- Other features that must be completed
- External factors (API availability, library release, etc.)

### 7. Implementation risk

| Level | Criteria |
|-------|---------|
| **Low** | Well-understood; similar patterns exist in codebase |
| **Medium** | Some unknowns; may require iteration |
| **High** | Novel approach; significant unknowns; may need to pivot |
| **Very high** | Experimental; success is uncertain |

### 8. Churn likelihood

Will this work need to be redone?
- **Low churn**: Requirements are stable, approach is proven
- **Medium churn**: Requirements may shift; design may need iteration
- **High churn**: Unstable requirements, immature architecture, or spec is still being debated

---

## Classification Buckets

Classify each item after evaluation:

### Aligned next steps
Score well across alignment, value, leverage, tractability. Go into the work plan.

### Misaligned ideas
Don't serve the project's core purpose. Be specific *why* — wrong audience, scope, or project?

### Premature work
Aligned but not yet tractable. Common reasons:
- Spec not written
- Architecture doesn't support it
- Dependencies not met
- Fundamentals not solid enough (e.g., observability before core workflows work)

### Deferred work
Aligned and tractable but lower priority. Include criteria for when to revisit.

### Rejected work
Should not be done. Reasons:
- Fundamentally misaligned with direction
- Infeasible with current state of art
- Contradicts hard requirements
- Introduces unsustainable complexity

Be blunt and explain why. This is a feature, not a bug.

---

## Push-back Checklist

Explicitly flag work that is:

- [ ] **Overreaching**: Scope exceeds what the project can deliver at its current maturity
- [ ] **Premature optimization**: Solving a scaling problem before the basic flow works
- [ ] **Feature creep**: Adding scope that dilutes the core purpose
- [ ] **Architecture avoidance**: Building features on top of a design that doesn't support them
- [ ] **Spec drift**: Implementing something that contradicts or isn't covered by specs
- [ ] **Wishful thinking**: Assuming capabilities that don't exist in the codebase or ecosystem
- [ ] **Churn-prone**: Likely to be rewritten when requirements crystallize

---

## Gap Analysis

Catalog remaining gaps after alignment review:

### Blockers
Prevent the project from fulfilling its stated purpose.

### Important enhancements
Significantly improve value but aren't blocking.

### Strategic gaps
Matter for long-term viability but aren't urgent.

Per gap:

| Field | Content |
|-------|---------|
| **Gap** | What's missing |
| **Why it matters** | Impact on users, operators, or contributors |
| **Who feels it** | Primary affected party |
| **Evidence** | Spec section, failed test, user report, missing code |
| **Recommended response** | Write spec / implement / defer / accept the gap |
| **Effort** | S (<1 day) / M (1-5 days) / L (1-3 weeks) / XL (>3 weeks) |

---

## Deliverable

1. **Alignment matrix**: Each proposed/discovered item rated across 8 dimensions
2. **Classification**: Items sorted into aligned/misaligned/premature/deferred/rejected buckets
3. **Push-back list**: Specific warnings about overreach, premature work, etc.
4. **Gap analysis**: Blockers, enhancements, strategic gaps with evidence and effort
