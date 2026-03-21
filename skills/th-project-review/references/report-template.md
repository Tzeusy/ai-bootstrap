# Report Template

Use this structure for the final project review report. Adapt depth to project size — a 500-line CLI needs less detail than a 50k-line SaaS backend.

For **quick health check** scope, output only: Executive Summary, Scorecard, Top 5 Risks, Verdict.

---

```markdown
# Project Review: {project_name}

**Date**: {date}
**Project type**: {type} | **Maturity**: {maturity} | **Users**: {users}

---

## 1. Executive Summary

{3 concise paragraphs:}
{- Overall health and blunt verdict}
{- Whether README goals are met (with evidence)}
{- Biggest strengths and biggest risks}

---

## 2. Scorecard

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

{Note: Average is informational only. A single critical-severity score (1 on security, data integrity, or correctness) can override an otherwise healthy average. The verdict reflects overall risk, not the average.}

### Score scale
- **5** Exemplary — best-in-class for project type/maturity
- **4** Strong — minor gaps, good trajectory
- **3** Adequate — functional but with meaningful issues
- **2** Weak — significant gaps affecting reliability or velocity
- **1** Poor/risky — critical issues requiring immediate attention
- **N/A** — Category not applicable to this project type

---

## 3. README & Goal Fulfillment

### Explicit goals
{Bulleted list from README/docs, each with status:}
- {goal}: **Achieved** / **Partially achieved** ({what's missing}) / **Unmet** ({evidence})

### Implicit goals
{Goals suggested by architecture and code but not documented}

### Documentation gaps
{Where docs and code disagree, or where docs are missing for implemented features}

---

## 4. Detailed Findings

{One subsection per scored category. Skip N/A categories.}

### 4.{n} {Category Name}
**Score**: {1-5} | **Confidence**: {H/M/L}

**Strengths**:
- {what is good} — `{evidence: file:line}`

**Weaknesses**:
- {what is weak} — `{evidence: file:line}`
- **Remedy**: {concrete fix} (effort: {S/M/L/XL})

{Repeat for each category}

---

## 5. Feature Gap Analysis

### Blockers
| Gap | Why it matters | Who feels it | Evidence | Effort |
|-----|---------------|-------------|----------|--------|

### Enhancements
| Gap | Why it matters | Who feels it | Evidence | Effort |
|-----|---------------|-------------|----------|--------|

---

## 6. Scale & Long-Horizon Analysis

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

## 7. Risk Register

| # | Risk | Sev. | Likelih. | Impact | Conf. | Fix | Effort |
|---|------|------|----------|--------|-------|-----|--------|
| 1 | {title} | {C/H/M/L} | {H/M/L} | {H/M/L} | {H/M/L} | {remedy} | {S/M/L/XL} |

{Ordered by severity × likelihood, descending.}

---

## 8. Recommendations & Roadmap

### Quick wins (1-3 days each)
1. **{action}** — {why} — `{evidence}`
2. ...

### Medium improvements (1-3 weeks each)
1. **{action}** — {why} — `{evidence}`
2. ...

### Strategic investments (1-3 months+)
1. **{action}** — {why} — `{evidence}`
2. ...

**Dependencies**: {note ordering constraints between recommendations}

---

## 9. Strengths Worth Preserving

{Call out 3-5 good patterns, architecture decisions, or practices that should be kept. Concrete evidence for each.}

---

## 10. Appendix

### A. Repository Map
{Languages, frameworks, services, entry points — from Agent A's deliverable}

### B. Critical Execution Paths
{Key user flows traced through the system}

### C. Evidence Index
{Consolidated list of all files cited, grouped by category}

---

**Verdict**: {exactly one of: Healthy | Healthy but fragile | Functional but accumulating debt | At risk | Severely at risk}

**Justification**: {3-5 sentences explaining why this verdict, referencing specific scores and risks}
```
