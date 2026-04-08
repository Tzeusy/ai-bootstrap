# Subagent Dispatch Template

Use this template when dispatching investigation subagents. Fill in the placeholders per domain.

---

```text
You are investigating domain {LETTER} ({DOMAIN_NAME}) of a project review.

Project: {project_name}
Type: {type} | Maturity: {maturity} | Users: {users}
Shape maturity summary: doctrine={absent|nascent|structured|mature}, design={...}, specs={...}, topology={...}

## Normative baseline
{Paste the Phase 0 baseline packet from project-review. Include doctrine/law/spec/topology sources, missing pillars, and contradictions.}

## Scan output
{Paste the full scan output from project-scan.sh}

## Your task
{Paste the relevant domain section from investigation-guides.md}

## Scoring
{For agents B-E only: paste the relevant category sections from scoring-rubric.md}

Calibrate for project type using these adjustments:
{Paste the relevant section from project-type-adaptations.md}

## Investigation rules
- If shaped artifacts exist, treat doctrine/law/spec/topology as more authoritative than README marketing copy.
- Use repository search tools (Glob/Grep/rg or equivalent), not ad-hoc broad scans, for file/content discovery.
- Cite specific files and line numbers for every claim: `path/to/file.ts:42`
- Label each claim: [Observed], [Inferred], or [Unknown]
- For each weakness, give at least one concrete remedy with effort estimate (S/M/L/XL)
- Do not hallucinate architecture, team size, or processes not evidenced in the repo
- Skip categories that are N/A for this project type (explain why in one line)
- If a category is not applicable, score it as `N/A` rather than forcing a 1-5
- Distinguish between normative violations, generic health risks, and missing norms

## Depth limits
- Examine at most 30 files in detail per domain
- For monorepos: sample 3-5 representative packages, plus shared/core code
- For codebases >50k LOC: focus on entry points, hotspot files, and public API surface
- Target 500-1000 words of output per scored category

## Output format
Return a structured report with:
1. One section per assigned category (or deliverable for non-scoring agents)
2. Score (1-5) and Confidence (High/Medium/Low) per category
3. Evidence list (files cited)
4. Top 3 risks found in this domain
5. Top 3 strengths found in this domain
6. Any planning constraints or sequencing notes that `/project-direction` should inherit
```

---

## Domain-specific additions

### Agent A (Project Mapping & Baseline Reconciliation)
- Does not score categories.
- Produces the repo map, explicit and implicit goals, and baseline contradictions.
- Focus on doctrine/spec/README/code disagreements and undocumented features.

### Agent B (Code Quality & Architecture, Categories 1-4)
- Start with the largest or most central files to understand architecture.
- Use churn data from the scan to identify hotspots.
- Check for generated code and exclude it from quality assessment.

### Agent C (Reliability & Tooling, Categories 5-8)
- Check CI for test steps, coverage gates, and required checks.
- Assess test quality, not just quantity.
- Look for flaky test indicators (`skip`, retry logic, xfail).

### Agent D (Security, Performance & Data, Categories 9-12)
- Check secrets, credentials, and auth boundaries first.
- For performance, focus on query patterns and hot paths.
- For API design, check consistency and contract clarity.

### Agent E (Docs, Ops & Maintainability, Categories 13-15)
- Mentally walk through README setup instructions.
- Check how much change safety comes from types, tests, CI, and review configuration.
- Treat missing shape artifacts as maintainability/planning signals when the repo would benefit from them.

### Agent F (Gaps, Scale & Planning Constraints)
- Runs independently.
- Compare missing capabilities against both project-type expectations and the Phase 0 normative baseline.
- Produce an advisory roadmap only. Do not create execution artifacts.
