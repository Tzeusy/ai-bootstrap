---
name: project-review
description: Use when auditing a repository's overall health, tech debt, maintainability, architecture quality, or a third-party repo-wide audit. Use for repository-level assessment requests such as "review this project", "audit the codebase", or "assess project health", not for single-PR review or exhaustive spec-to-code reconciliation.
---

# Project Review

Perform a blunt, evidence-based audit of a repository across 15 categories. Start by establishing the project's normative baseline through `/project-shape`. End by handing confirmed findings to `/project-direction` for scheduling. Treat README as a claim to validate, not as the primary source of truth when shape artifacts exist.

Normative source order:
1. `about/heart-and-soul/` and `about/legends-and-lore/`
2. `openspec/`
3. `about/lay-and-land/`
4. README / docs / issue tracker
5. Repository inference from code and history

Every major claim must cite specific files or sections. Label assertions as [Observed], [Inferred], or [Unknown]. Every criticism must include a concrete remedy.

## Workflow

### Phase 0: Establish the Normative Baseline with `/project-shape`

Read `../project-shape/SKILL.md` first, then run the shape scan:

```bash
bash ../project-shape/scripts/shape-scan.sh <repo_root>
```

Use the result to classify each pillar using `project-shape`'s own maturity vocabulary: `absent`, `nascent`, `structured`, or `mature`.

Review behavior:
- If doctrine, design, specs, or topology are `structured` or `mature`, treat them as the primary normative baseline for their domains.
- If only some pillars exist, use those pillars normatively and fall back elsewhere.
- If all pillars are `absent` or effectively unusable, fall back to README/docs/code and lower confidence on alignment judgments.

If the scan finds relevant pillars:
- Read the actual doctrine/design/spec/topology files before reviewing code.
- Extract the project's explicit non-negotiables, scope boundaries, architectural claims, and normative requirements.
- Note contradictions between pillars. Do not silently resolve them.

If the scan reports weak or missing shape:
- Record the missing pillars in the report.
- Downgrade confidence on product-coherence and roadmap judgments.
- Use README/docs/code as provisional truth, but call out the absence of normative artifacts as a project risk.

Output of Phase 0: a short baseline packet containing:
- Per-pillar maturity and missing pillars
- Source-of-truth order used for this review
- Explicit doctrine/spec requirements that the code must satisfy
- Any unresolved contradictions across doctrine, law, spec, README, or code

### Phase 1: Automated Repository Scan

Run the review scan:

```bash
bash scripts/project-scan.sh <repo_root>
```

Before proceeding, read `references/project-type-adaptations.md` to calibrate scoring by project type and maturity.

Calibration rule: `project-shape` sets the project's normative requirements; `project-type-adaptations.md` adjusts emphasis and expectations. If generic project-type advice conflicts with doctrine, law, or spec, the shaped project artifacts win.

#### Edge cases

| Situation | Handling |
|-----------|----------|
| <50 source files | Skip full subagent fan-out; single-agent review is acceptable |
| >50k LOC | Focus on entry points, churn hotspots, public API surface, and normative requirements |
| Monorepo with 10+ packages | Sample 3-5 representative packages plus shared/core code |
| No README or docs | Infer goals from git history, tests, manifests, and code comments |
| Shallow git clone | Note in report; commit counts and churn data are unreliable |
| Generated code (protobuf, ORM output, bundles) | Exclude from quality scoring; note presence |
| Shape absent or weak | Treat missing pillars as a maintainability and planning risk, not just a documentation gap |

### Phase 2: Parallel Investigation

Read `references/investigation-guides.md` for per-domain checklists. Read `references/subagent-template.md` for the dispatch format.

Dispatch subagents per this plan:

| Agent | Domain | Scores | Key focus |
|-------|--------|--------|-----------|
| A | Project mapping & baseline reconciliation | — | Repo map, goals, doc contradictions, shape-vs-code contradictions |
| B | Code quality & architecture | 1-4 | Modularity, clarity, correctness, normative violations |
| C | Reliability & tooling | 5-8 | Errors, observability, testing, hygiene |
| D | Security, perf & data | 9-12 | Dependencies, auth, performance, API/data design |
| E | Docs, ops & maintainability | 13-15 | Documentation, release, change safety, missing shape artifacts |
| F | Gaps, scale & planning constraints | — | Feature gaps, 10x/100x, risk register, sequencing constraints |

Dispatch strategy:
- Launch A-F in parallel for a full review.
- Pass both the Phase 0 baseline packet and the Phase 1 scan output to every subagent.
- Agent F can work independently, but during synthesis its roadmap draft remains advisory only. It does not create beads or own scheduling.

Each subagent receives:
- Phase 0 baseline packet
- Shape-scan output
- Project-scan output
- Project context (type, users, maturity, scope)
- Its domain section from `references/investigation-guides.md`
- Relevant rubric sections from `references/scoring-rubric.md`
- Relevant project-type calibration from `references/project-type-adaptations.md`

### Phase 3: Synthesis

Collect all subagent reports. Read `references/report-template.md` for the output structure.

1. Merge scores conservatively. When subagents disagree on a category, take the lower score and record the disagreement.
2. Mark genuinely inapplicable categories as `N/A`; exclude them from the average.
3. Classify findings into four buckets:
   - Normative violations: doctrine/law/spec/topology contradicted by implementation
   - Generic health risks: code quality, reliability, tooling, security, performance, DX
   - Shape gaps: missing or stale pillars that weaken review confidence or decision quality
   - Deprioritized items: theoretically good ideas that do not fit the project's actual context
4. Build the risk register by severity x likelihood.
5. Generate an advisory roadmap: quick wins, medium improvements, strategic investments. This roadmap is for synthesis only and must not create execution artifacts.
6. Assign the verdict:

| Verdict | Criteria |
|---------|----------|
| **Healthy** | No category below 3; no critical risks; average >= 3.5 |
| **Healthy but fragile** | No category below 2; <= 1 critical risk; average >= 3.0; but missing safety nets |
| **Functional but accumulating debt** | 1-3 categories below 3; average 2.5-3.5; growing risk register |
| **At risk** | 3+ categories below 3 OR any category at 1 OR 2+ critical risks; average < 3.0 |
| **Severely at risk** | 5+ categories below 3 OR multiple categories at 1 OR critical security/data risks; average < 2.0 |

7. Prepare the `/project-direction` handoff packet:
   - Confirmed findings only
   - Phase 0 baseline packet
   - Required doctrine/law/spec updates before implementation planning
   - Recommended sequencing constraints and dependency hints
   - Deprioritized items with reasons
   - Evidence index

### Phase 4: Deliver

Output the report per `references/report-template.md`.

The report must make the boundary explicit:
- `project-review` audits and classifies
- `project-direction` decides sequencing, specs, and beads

## Adapting to Scope

**Full review** (default): All 6 subagents, all 15 categories, complete report plus planning handoff packet.

**Focused review** (user specifies categories): Dispatch only relevant subagents. Still include the normative baseline, scorecard for scoped categories, risk register, and planning handoff packet.

**Quick health check** (fast answer): Run shape scan + project scan + Agent A, then do a brief orchestrator sweep of obvious high-risk areas (tests, CI, auth/secrets, docs). Output: executive summary, provisional scorecard, top 5 risks, explicit low-confidence markers where evidence is thin. Do not pretend this is equivalent to a full review.

**Third-party deep-dive review synthesis** ("process this review/audit"): Fact-check external findings, filter them through the project's actual context, convert confirmed findings into a planning handoff packet, and route execution planning to `/project-direction`.

**OpenSpec reconciliation request** ("reconcile spec vs implementation", "what's implemented but undocumented", "what's specified but missing"): Route to `$reconcile-spec-to-project`. That skill performs exhaustive bidirectional spec/code mapping and remediation, which is outside this skill's primary health-audit flow.

## Handling Third-Party Deep-Dive Reviews

When an external reviewer produces a comprehensive project review, extract value without inheriting its mistakes.

### Step 1: Fact-check before synthesizing

Before accepting any external claim:
- Verify quantitative claims: line counts, dependency counts, file sizes, test counts
- Verify referenced paths and named features
- Verify process claims against actual CI, docs, and code
- Label each finding: [Confirmed], [Overstated], [Incorrect], or [Unverifiable]

Only [Confirmed] findings enter the planning handoff packet.

### Step 2: Filter for the project's actual context

Not all best-practice advice applies equally. Explicitly deprioritize recommendations that do not fit the project:

| Filter | Example of what to deprioritize |
|--------|---------------------------------|
| Single-user project | Multi-tenant scaling, contributor governance overhead |
| Solo maintainer | Formal compatibility matrices for internal APIs |
| Early-stage project | Heavy conformance harnesses before interfaces stabilize |
| Self-hosted/internal tool | SaaS-style auth hardening beyond the real threat model |

If doctrine or law artifacts exist, use them to justify deprioritization. If they do not exist, say that the filter is inferential rather than explicit.

### Step 3: Synthesize actionables by ROI

Sort confirmed findings into tiers:

**Tier 1 — High ROI, do soon**
- Structural improvements with measurable before/after evidence
- Test upgrades that materially change regression detection
- Small CI/docs fixes that close documented-vs-actual gaps

**Tier 2 — Good practice, medium effort**
- Coverage and observability improvements for critical paths
- Proportional security hardening
- Operability improvements that unlock debugging and safer releases

**Tier 3 — Deprioritized with reason**
- Items filtered out by project context
- Enterprise-scale recommendations that do not fit
- Strategic suggestions without a concrete first step

### Step 4: Prepare planning inputs, not execution artifacts

For structural refactors or major risks identified by the review, prepare a packet for `/project-direction` that includes:
1. Baseline evidence to preserve: public interfaces, startup/shutdown behavior, critical-path tests, current constraints
2. Logical workstream boundaries: what could be split into separate epics/tasks
3. Required reconciliation gates: how to prove behavior stayed equivalent after changes

Do not create beads directly from `project-review`. `project-direction` owns the dependency graph and planning graph generation.

### Step 5: Handle episodic artifacts

The review document itself is transitory. After extracting actionables:
- Do not commit the review as permanent doctrine
- If the review surfaces genuine doctrine or design insight, update the relevant `project-shape` pillar instead
- Keep the durable artifacts as updated shape/spec docs plus the `/project-direction` handoff packet

## Anti-Patterns

- Skipping `/project-shape` and treating README as sufficient when doctrine/spec artifacts exist
- Accepting severity assessments from an external review at face value
- Treating all recommendations as equally important
- Enterprise-framing a personal project
- Creating beads or other execution artifacts directly from `project-review`
- Preserving the review as canon instead of extracting durable doctrine/spec/planning updates

## References

| File | Read when | Content |
|------|-----------|---------|
| `../project-shape/SKILL.md` | Phase 0 | Four-pillar model, shape assessment workflow, normative source hierarchy |
| `../project-direction/SKILL.md` | Phase 3-4 | Planning contract, sequencing expectations, and handoff target |
| `references/scoring-rubric.md` | Phase 2 | 1-5 criteria per category with evidence guidance |
| `references/investigation-guides.md` | Phase 2 | Per-domain checklists, search patterns, deliverables |
| `references/subagent-template.md` | Phase 2 | Dispatch template and required prompt fields |
| `references/report-template.md` | Phase 3-4 | Output structure, scorecard, handoff packet layout |
| `references/project-type-adaptations.md` | Phase 1-3 | Category weighting by project type, maturity expectations, hybrid handling |

## Scripts

- `../project-shape/scripts/shape-scan.sh <repo_root>` — Establishes the normative baseline and shape maturity. Run first.
- `scripts/project-scan.sh <repo_root>` — Structural repository scan covering languages, deps, tests, CI, infra, governance, git signals, and size.

## After Review: Schedule with `/project-direction`

Once findings are confirmed, invoke `/project-direction`.

Handoff contract:
- Feed it the Phase 0 baseline packet, not just the scorecard
- Separate normative violations from generic health risks
- Identify which findings require doctrine/law/spec updates before any implementation planning
- Include sequencing constraints, dependency hints, and explicit deprioritized items
- Keep execution ownership separate: `project-review` audits, `/project-direction` plans
