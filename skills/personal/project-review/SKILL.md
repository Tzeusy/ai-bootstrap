---
name: project-review
description: Deep evidence-based audit of a repository's health, quality, maintainability, and long-term viability. Produces a structured report with scores, risks, and actionable recommendations. Also handles third-party deep-dive reviews by fact-checking claims, filtering for project context, and synthesizing confirmed findings. Use when asked to review, audit, or assess a project, codebase, or repository — or when asked about project health, tech debt, code quality, or external review findings at a repo-wide level. Triggers on phrases like "review this project", "audit the codebase", "assess code quality", "project health check", "tech debt audit", "review feedback", "external audit", "deep dive review".
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

**Third-party deep-dive review synthesis** ("process this review/audit"): Use this workflow to fact-check external findings, filter for project context, and convert confirmed findings into actionable recommendations.

**OpenSpec reconciliation request** ("reconcile spec vs implementation", "what's implemented but undocumented", "what's specified but missing"): route to `$reconcile-spec-to-project`. That skill performs exhaustive bidirectional spec/code mapping and remediation (spec creation + beads creation), which is outside this skill's primary 15-category health-audit flow.

## Handling Third-Party Deep-Dive Reviews

When an external reviewer (human or AI) produces a comprehensive project review, the goal is to extract maximum value while filtering noise. The overarching standard: design and architecture should be as clean and optimized as possible, following best practices that leading software engineers in top firms would be proud of.

### Step 1: Fact-Check Before Synthesizing

External reviews operate on incomplete information. Before accepting any claim:

- **Verify quantitative claims** — line counts, file sizes, dependency counts. Reviewers frequently estimate or hallucinate metrics. A "3,597-line file" that's actually 944 lines changes the severity assessment entirely.
- **Verify referenced paths** — files cited as missing may exist at different paths; features called absent may be implemented under different names.
- **Test process claims against reality** — if the review says "CI doesn't enforce X", read the actual CI workflow. If it says "no tests for Y", grep for them.
- **Label each finding**: [Confirmed], [Overstated], [Incorrect], [Unverifiable]. Only act on [Confirmed].

### Step 2: Filter for the Project's Actual Context

Not all best-practice advice applies to every project. Explicitly deprioritize recommendations that don't fit:

| Filter | Example of what to deprioritize |
|--------|-------------------------------|
| Single-user project | Multi-tenant scaling, contributor onboarding docs, CODEOWNERS |
| Solo maintainer | Formal API versioning contracts, compatibility matrices for internal APIs |
| Early-stage | Comprehensive conformance harnesses before the interfaces stabilize |
| Self-hosted | SaaS-style auth hardening beyond proportional threat model |

State what you're deprioritizing and why. This prevents the review from inflating scope.

### Step 3: Synthesize Actionables by ROI

Sort confirmed findings into tiers:

**Tier 1 — High ROI, do soon:**
- Structural improvements with measurable before/after (e.g., splitting a 7k-line file)
- Test quality upgrades that change regression detection capability (e.g., replacing source-inspection tests with behavioral ones)
- One-line CI/docs fixes that close documented-vs-actual gaps

**Tier 2 — Good practice, medium effort:**
- CI coverage gaps for critical paths
- Operational improvements that make existing instrumentation usable
- Proportional security hardening (warnings, not architecture changes)

**Tier 3 — Deprioritized with reason:**
- Items filtered out by project context (Step 2)
- Recommendations framed in enterprise-scale terms that don't apply
- Speculative "strategic investments" without concrete first steps

### Step 4: Create Rigorous Beads for High-Risk Items

For structural refactors identified by the review (especially decomposition of large files or architectural changes):

1. **Baseline bead** (P0) — snapshot current behavior: tool surfaces, startup/shutdown sequences, test pass counts. This is the "before" picture.
2. **Extraction beads** — one per logical boundary, with explicit testing requirements in the description. Each must prove behavioral equivalence, not just "tests pass."
3. **Reconciliation bead** (P0) — runs last, depends on all extraction beads. Compares against the baseline on every measurable dimension. This is the quality gate that prevents the refactor from silently changing behavior.

Wire dependencies so baseline runs first and reconciliation runs last.

### Step 5: Handle Episodic Artifacts

The review document itself is transitory. After extracting actionables:

- Do NOT commit the review to the repo's permanent docs (or remove it if already committed)
- Create beads for all actionable findings — the beads are the durable artifact, not the review
- If the review surfaced genuinely new architectural insight, capture that in the project's doctrine docs (e.g., `heart-and-soul/`) rather than keeping the review as a reference

### Anti-Patterns

- **Accepting severity assessments at face value** — always verify the evidence behind the score
- **Treating all recommendations as equal** — a review may list 20 items; typically 3-5 are high-leverage
- **Enterprise-framing a personal project** — "bounded contexts" and "3-month strategic investments" for what is actually "split one file and tighten some imports"
- **Scope inflation** — reviews tend to recommend more work than is warranted. The correct response to "spend the next major cycle on X" is often "spend 3 days on the concrete subset of X that matters"
- **Preserving the review as canon** — the review is a snapshot opinion, not a living document. Extract value, then discard

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

## After Review: Schedule with /project-direction

Once review findings are confirmed, invoke `/project-direction` to schedule all necessary changes into a coherent, dependency-aware execution plan.

Handoff expectations:
- Feed `/project-direction` the confirmed findings and evidence.
- Require reconciliation against doctrine/spec artifacts before planning implementation.
- Materialize the resulting work as beads for execution tracking.
- Keep execution ownership separate from review; `project-review` audits, `/project-direction` schedules.
