# Report Template

Use this structure for the final project review report. Adapt depth to project size. A small CLI should not get the same verbosity as a large SaaS codebase.

For **quick health check** scope, output only: Normative Baseline, Executive Summary, Scorecard, Top 5 Risks, Verdict, Planning Handoff.

---

```markdown
# Project Review: {project_name}

**Date**: {date}
**Project type**: {type} | **Maturity**: {maturity} | **Users**: {users}

---

## 1. Normative Baseline

- **Doctrine maturity**: {absent | nascent | structured | mature}
- **Design-contract maturity**: {absent | nascent | structured | mature}
- **Spec maturity**: {absent | nascent | structured | mature}
- **Topology maturity**: {absent | nascent | structured | mature}
- **Source-of-truth order used**: {doctrine/law/spec/topology/README/code}
- **Normative artifacts reviewed**: {list of pillar files or "none"}
- **Missing or weak pillars**: {list}
- **Known contradictions before scoring**: {list or "none"}

### What this means for confidence
{How the presence or absence of shape artifacts affects confidence in alignment judgments}

---

## 2. Executive Summary

{3 concise paragraphs:}
{- Overall health and blunt verdict}
{- Whether doctrine/spec/README goals are met (with evidence)}
{- Biggest strengths and biggest risks}

---

## 3. Scorecard

| # | Area | Score | Conf. |
|---|------|-------|-------|
| 1 | Goal alignment | {1-5} | {H/M/L} |
| 2 | Architecture | {1-5} | {H/M/L} |
| 3 | Code clarity | {1-5} | {H/M/L} |
| 4 | Correctness | {1-5} | {H/M/L} |
| 5 | Error handling | {1-5} | {H/M/L} |
| 6 | Observability | {1-5} | {H/M/L} |
| 7 | Testing | {1-5} | {H/M/L} |
| 8 | Tooling/hygiene | {1-5} | {H/M/L} |
| 9 | Dependencies | {1-5} | {H/M/L} |
| 10 | Security | {1-5} | {H/M/L} |
| 11 | Performance | {1-5} | {H/M/L} |
| 12 | Data/API design | {1-5} | {H/M/L} |
| 13 | Documentation/DX | {1-5} | {H/M/L} |
| 14 | Release/ops | {1-5} | {H/M/L} |
| 15 | Maintainability | {1-5} | {H/M/L} |

**Average**: {score}/5 (excluding N/A categories)

{Note: Average is informational only. A single critical-severity score can override an otherwise healthy average.}

### Score scale
- **5** Exemplary
- **4** Strong
- **3** Adequate
- **2** Weak
- **1** Poor/risky
- **N/A** Not applicable

---

## 4. README, Shape, and Goal Fulfillment

### Explicit goals and normative requirements
- {goal}: **Achieved** / **Partially achieved** ({what's missing}) / **Unmet** ({evidence})

### Implicit goals
{Goals suggested by architecture and code but not documented}

### Documentation gaps
{Where shape/docs/README/code disagree, or where norms are missing entirely}

---

## 5. Detailed Findings

{One subsection per scored category. Skip N/A categories.}

### 5.{n} {Category Name}
**Score**: {1-5} | **Confidence**: {H/M/L}

**Strengths**:
- {what is good} — `{evidence: file:line}`

**Weaknesses**:
- {what is weak} — `{evidence: file:line}`
- **Remedy**: {concrete fix} (effort: {S/M/L/XL})

**Normative status**:
- {Aligned | Violates doctrine | Violates design contract | Spec drift | No explicit norm exists}

{Repeat for each category}

---

## 6. Feature Gap Analysis

### Blockers
| Gap | Why it matters | Who feels it | Evidence | Effort |
|-----|----------------|-------------|----------|--------|

### Enhancements
| Gap | Why it matters | Who feels it | Evidence | Effort |
|-----|----------------|-------------|----------|--------|

---

## 7. Scale & Long-Horizon Analysis

### At 10x
{First bottleneck on the critical path. Organizational scaling limits.}

### At 100x
{Breaking points. Fundamental architectural constraints.}

### 1-year risks
{Dependency drift, documentation decay, config sprawl}

### 3-year risks
{Tech debt trajectory, bus factor impact, ecosystem shifts}

### 5-year risks
{Lock-in, calcified areas, architectural ceilings}

---

## 8. Risk Register

| # | Risk | Sev. | Likelih. | Impact | Conf. | Fix | Effort |
|---|------|------|----------|--------|-------|-----|--------|
| 1 | {title} | {C/H/M/L} | {H/M/L} | {H/M/L} | {H/M/L} | {remedy} | {S/M/L/XL} |

{Ordered by severity x likelihood, descending.}

---

## 9. Recommendations & Roadmap

### Quick wins (1-3 days each)
1. **{action}** — {why} — `{evidence}`

### Medium improvements (1-3 weeks each)
1. **{action}** — {why} — `{evidence}`

### Strategic investments (1-3 months+)
1. **{action}** — {why} — `{evidence}`

**Dependencies**: {ordering constraints between recommendations}

---

## 10. Planning Handoff for `/project-direction`

### Required shape work before implementation planning
- {doctrine/law/topology gap or "none"}

### Required spec work before implementation planning
- {spec update, missing requirement, contract clarification, or "none"}

### Candidate workstreams
1. **{workstream}** — {goal} — `{evidence}`

### Sequencing constraints
- {dependency or ordering constraint}

### Explicit deprioritizations
- {item} — {reason it should not enter the plan yet}

---

## 11. Strengths Worth Preserving

{Call out 3-5 good patterns, architecture decisions, or practices that should be kept.}

---

## 12. Appendix

### A. Repository Map
{Languages, frameworks, services, entry points}

### B. Critical Execution Paths
{Key user flows traced through the system}

### C. Evidence Index
{Consolidated list of all files cited, grouped by category}

---

**Verdict**: {exactly one of: Healthy | Healthy but fragile | Functional but accumulating debt | At risk | Severely at risk}

**Justification**: {3-5 sentences explaining why this verdict, referencing specific scores and risks}
```
