# Subagent Dispatch Template

Use this template when dispatching investigation subagents. Fill in the placeholders per domain.

---

```
You are investigating domain {LETTER} ({DOMAIN_NAME}) of a project review.

Project: {project_name}
Type: {type} | Maturity: {maturity} | Users: {users}

## Scan output
{paste full scan output from project-scan.sh}

## Your task
{Paste the relevant Domain section from investigation-guides.md}

## Scoring
{For agents B-E only: paste the relevant category sections from scoring-rubric.md}

Calibrate for project type using these adjustments:
{Paste the relevant section from project-type-adaptations.md}

## Investigation rules
- Use Glob and Grep tools for file/content search (not bash grep/find)
- Cite specific files and line numbers for every claim: `path/to/file.ts:42`
- Label each claim: [Observed], [Inferred], or [Unknown]
- For each weakness, give at least one concrete remedy with effort estimate (S/M/L/XL)
- Do NOT hallucinate architecture, team size, or processes not evidenced in the repo
- Skip categories that are N/A for this project type (explain why in one line)
- If a category is not applicable, score it as "N/A" rather than forcing a 1-5

## Depth limits
- Examine at most 30 files in detail per domain
- For monorepos: sample 3-5 representative packages, plus shared/core code
- For codebases >50k LOC: focus on entry points, hotspot files (highest churn), and public API surface
- Target 500-1000 words of output per scored category

## Output format
Return a structured report with:
1. One section per assigned category (or deliverable for non-scoring agents)
2. Score (1-5) and Confidence (High/Medium/Low) per category
3. Evidence list (files cited)
4. Top 3 risks found in this domain
5. Top 3 strengths found in this domain
```

---

## Domain-specific additions

### Agent A (Project Mapping & Goals)
- Does NOT score categories. Produces the project map and goal analysis.
- Output feeds into all other agents and the final report appendix.
- Focus on: contradictions between README and code, undocumented features, dead code for abandoned features.

### Agent B (Code Quality & Architecture, Categories 1-4)
- Start with the largest/most-imported files to understand architecture.
- Use `git log --oneline -500 --name-only` churn data from the scan to identify hotspots.
- Check for generated code (protobuf output, ORM migrations, bundled assets) and exclude from quality assessment.

### Agent C (Reliability & Tooling, Categories 5-8)
- Check CI pipeline for test steps, coverage gates, and required checks.
- Assess test quality, not just quantity — are tests testing behavior or implementation?
- Look for flaky test indicators (retry logic, `skip`/`xfail` annotations).

### Agent D (Security, Performance & Data, Categories 9-12)
- Check `.env` files, hardcoded secrets, credential patterns first (high-impact, fast to find).
- For performance: focus on database query patterns and algorithm complexity in hot paths.
- For API design: check consistency across endpoints, versioning strategy, error response format.

### Agent E (Docs, Ops & Maintainability, Categories 13-15)
- Try to follow the README setup instructions mentally — would they work for a new contributor?
- Check if type system is used strictly (TypeScript `strict`, mypy, etc.) or loosely (`any` everywhere).
- Look for CODEOWNERS, required reviewers, branch protection signals.

### Agent F (Gaps, Scale & Risk)
- Run independently (does not need B-E output, though it benefits from it).
- For feature gaps: compare against standard expectations for the project type (see `project-type-adaptations.md`).
- For scale analysis: trace the critical path (request → handler → DB → response) and identify the first bottleneck at 10x and 100x.
- For risk register: synthesize from your own findings; the orchestrator will merge with risks from B-E.
