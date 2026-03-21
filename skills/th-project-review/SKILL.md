---
name: th-project-review
description: Deep evidence-based audit of a repository's health, quality, maintainability, and long-term viability. Produces a structured report with scores, risks, and actionable recommendations. Use when asked to review, audit, or assess a project, codebase, or repository — or when asked about project health, tech debt, or code quality at a repo-wide level. Triggers on phrases like "review this project", "audit the codebase", "assess code quality", "project health check", "tech debt audit".
---

# Project Review

Perform a blunt, evidence-based audit of a repository across 15 categories. Every major claim must cite specific files/functions. Treat README as a claim to validate, not truth. Label assertions as [Observed], [Inferred], or [Unknown]. Every criticism must include a concrete remedy.

## Workflow

### Phase 0: Gather Context

Ask the user (or infer from the repo) before starting:

| Parameter | Values | Default |
|-----------|--------|---------|
| Project type | library, SDK, backend, SaaS, frontend, CLI, mobile, monorepo, ML/data, internal tool, IaC, serverless | Infer from scan |
| Intended users | developers, end users, internal team, enterprises | Infer from docs |
| Expected maturity | prototype, beta, production, mission-critical | Infer from signals |
| Team size | solo, small (2-5), medium (6-20), large (20+) | Infer or Unknown |
| Public/private | open-source, private/internal | Infer from LICENSE |
| Focus areas | Any subset of the 15 categories, or "all" | all |
| Scope | full, focused, quick | full |

**Inference heuristics**: Infer type from scan output (e.g., Dockerfile + API routes = backend; package.json `main`/`types` = library). Infer maturity from git age, tag count, CI presence, and doc completeness. If ambiguous, state assumption explicitly and proceed.

**Hybrid projects** (e.g., monorepo with frontend + backend): identify the **primary type** (where most value and risk lives), apply its elevated categories at full weight, and import 2-3 key concerns from secondary types. See `references/project-type-adaptations.md` for details.

### Phase 1: Automated Scan

Run the project scan script:

```bash
bash <skill_dir>/scripts/project-scan.sh <repo_root>
```

**Before proceeding**, read `references/project-type-adaptations.md` to determine which categories to elevate or lower for this project type.

#### Edge cases

| Situation | Handling |
|-----------|----------|
| <50 source files | Skip full subagent dispatch; single-agent review covering all domains |
| >50k LOC | Focus on entry points, churn hotspots (from scan), and public API surface |
| Monorepo with 10+ packages | Sample 3-5 representative packages + shared/core code |
| No README or docs | Infer goals from git history, comments, tests, and package metadata |
| Shallow git clone | Note in report; commit counts and churn data are unreliable |
| Generated code (protobuf, ORM output, bundles) | Exclude from quality scoring; note presence |

### Phase 2: Parallel Investigation

Read `references/investigation-guides.md` for per-domain checklists. Read `references/subagent-template.md` for the exact dispatch format.

Dispatch subagents per this plan:

| Agent | Domain | Scores | Key focus |
|-------|--------|--------|-----------|
| A | Project mapping & goals | — | Repo map, goals, doc contradictions |
| B | Code quality & architecture | 1-4 | Modularity, clarity, correctness |
| C | Reliability & tooling | 5-8 | Errors, observability, testing, hygiene |
| D | Security, perf & data | 9-12 | Deps, auth, performance, API design |
| E | Docs, ops & maintainability | 13-15 | Documentation, release, change safety |
| F | Gaps, scale & risk | — | Feature gaps, 10x/100x, risk register |

**Dispatch strategy**: Launch A-F all in parallel. Agent F can operate independently from B-E (it investigates the codebase directly). If time permits and F finishes early, supplement F's findings with risks surfaced by B-E during synthesis.

Each subagent receives: scan output, project context (Phase 0), its domain section from `investigation-guides.md`, relevant scoring rubric from `references/scoring-rubric.md`, and project-type calibration.

### Phase 3: Synthesis

Collect all subagent reports. Read `references/report-template.md` for the output structure.

1. **Merge scores**: When subagents disagree on a category, take the **lower** score (conservative). Note the disagreement with both evidence sets.
2. **Handle N/A categories**: If a category is not applicable (e.g., Observability for a static library), mark as "N/A" in the scorecard. Do not include N/A categories in the average.
3. **Build risk register**: Combine risks from all domains, deduplicate, prioritize by severity x likelihood.
4. **Generate roadmap**: Quick wins (1-3 days), medium (1-3 weeks), strategic (1-3 months+). Order by ROI.
5. **Write executive summary**: 3 paragraphs — overall health, goal fulfillment, biggest strengths and risks.
6. **Assign verdict** using this decision matrix:

| Verdict | Criteria |
|---------|----------|
| **Healthy** | No category below 3; no critical risks; average >= 3.5 |
| **Healthy but fragile** | No category below 2; <= 1 critical risk; average >= 3.0; but missing safety nets (tests, CI, types) |
| **Functional but accumulating debt** | 1-3 categories below 3; average 2.5-3.5; growing risk register; delivers value but trajectory is negative |
| **At risk** | 3+ categories below 3 OR any category at 1 OR 2+ critical risks; average < 3.0 |
| **Severely at risk** | 5+ categories below 3 OR multiple categories at 1 OR critical security/data risks; average < 2.0 |

### Phase 4: Deliver

Output the report per `references/report-template.md`.

## Adapting to Scope

**Full review** (default): All 6 subagents, all 15 categories, complete report.

**Focused review** (user specifies categories): Dispatch only relevant subagents. Still include executive summary, scorecard (scored categories only), and risk register.

**Quick health check** (fast answer): Run scan + dispatch Agent A only (with instructions to also spot-check 2-3 files per category). Output: compact scorecard, executive summary, top 5 risks. Skip detailed findings.

## References

| File | Read when | Content |
|------|-----------|---------|
| `references/scoring-rubric.md` | Phase 2 (pass to subagents B-E) | 1-5 criteria per category with evidence guidance |
| `references/investigation-guides.md` | Phase 2 (pass relevant domain to each subagent) | Per-domain checklists, search patterns, deliverables |
| `references/subagent-template.md` | Phase 2 (dispatch format) | Exact template for subagent prompts, depth limits, domain-specific additions |
| `references/report-template.md` | Phase 3 (synthesis) | Complete output format with scorecard, findings, risk register |
| `references/project-type-adaptations.md` | Phase 0-1 (calibration) | Category weighting by project type, maturity expectations, hybrid handling |

## Scripts

- `scripts/project-scan.sh <repo_root>` — Automated structural scan. Run first, always. Covers: languages, frameworks, deps, tests, CI, infra, API schemas, governance, git signals (including churn hotspots), repo size.
