---
name: th-project-direction
description: Analyze a software project's true direction, validate alignment between specs/docs and implementation, and produce a prioritized, spec-driven work plan with beads. Ensures every non-trivial epic includes a report-generation bead for human review. Use when deciding what to work on next, evaluating feature proposals, checking spec-to-code drift, sequencing roadmap items, or pushing back on misaligned requirements. Triggers on "what should we work on next", "prioritize features", "does the code match the spec", "is this roadmap aligned", "what's highest leverage", "should we build this", "is this tractable", "break this down into chunks".
---

# Project Direction

Determine what a project should work on next. Ground decisions in specifications, repository evidence, and implementation reality. Optimize for spec alignment, tractability, leverage, and low-churn execution — not feature count.

## Core Rules

1. **Specifications are source of truth** — every work item must link to a spec section. If a feature lacks spec coverage, recommend spec work first.
2. **No coding before signoff** — spec must be written/updated and approved before implementation begins.
3. **Evidence over assumption** — cite files, functions, spec sections. Label claims: [Observed], [Inferred], [Unknown].
4. **Push back when needed** — flag misaligned, premature, unrealistic, or infeasible work directly.
5. **Minimize churn** — favor removing dead paths over backward-compatibility shims; serialize work that would conflict.

## Workflow

### Phase 0: Gather Context

Ask the user (or infer from the repo):

| Parameter | Values | Default |
|-----------|--------|---------|
| Project type | library, SDK, backend, SaaS, frontend, CLI, mobile, monorepo, ML/data, internal tool, IaC | Infer |
| Primary user | developers, end users, internal team, enterprises | Infer |
| Maturity | prototype, beta, production, mission-critical | Infer |
| Spec location | openspec/, spec/, docs/design/, or "none" | Infer from scan |
| Focus | Full direction analysis, specific feature evaluation, spec-drift check | Full |

### Phase 1: Spec Scan

Run the spec-focused scan:

```bash
bash <skill_dir>/scripts/spec-scan.sh <repo_root>
```

This discovers specification artifacts, design docs, roadmap files, agent context, issue tracking, and recent spec/doc changes. Use the output to inform all investigation.

### Phase 2: Parallel Investigation

Read `references/subagent-template.md` for the dispatch format.

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| A | Project spirit & requirements | Scan + specs | Direction model, requirements, reality check |
| B | Spec adherence & workflows | Scan + specs | Spec drift report, workflow completeness |
| C | Implementation fitness | Scan + code | Test confidence, observability, delivery readiness, architectural fitness |
| D | Alignment & gap analysis | A + B + C | Alignment matrix, gaps, push-back list |

**Dispatch strategy**: Launch A, B, C in parallel. Launch D after they complete (it synthesizes their findings).

Each agent receives its domain-specific guide:
- A, B: `references/direction-model.md`
- C: `references/direction-model.md` Phase 2 sections 2.3-2.6
- D: `references/alignment-review.md`

### Phase 3: Work Plan

Done by the orchestrator (not a subagent). Read `references/work-plan-template.md` for the decomposition rules and output format.

Steps:
1. **Prioritize** aligned items by: user value > leverage > tractability > timing
2. **Sequence** respecting dependencies and serialization constraints
3. **Decompose** each item into 3-10 hour chunks with acceptance criteria
4. **Link** every chunk to its spec section (or flag "spec work required first")
5. **Add reconciliation** after each chunk and each logical block
6. **List what NOT to do** with reasons and revisit triggers

### Phase 4: Materialize as Beads

Call `/beads-writer` to create epics and children from the work plan. For every non-trivial epic (>=3 children or >100 lines expected), include these mandatory structural beads:

1. **Reconciliation bead** (standard — see `/beads-writer` patterns)
2. **Epic report bead** — a child that generates a human-readable report after all implementation and reconciliation children close

The epic report bead must:
- Depend on ALL implementation children AND the reconciliation bead (it runs last)
- Have type `task` and a title like `"Generate epic report for: {epic title}"`
- Reference `references/epic-report.md` from this skill as its execution guide
- Include in its description: the epic ID, spec sections covered, and the scaffold script invocation

See `references/epic-report.md` for the report bead's content template and `scripts/epic-report-scaffold.sh` for the scaffold tool it should use.

### Phase 5: Deliver

Output the direction report per `references/work-plan-template.md`. End with the blunt conclusion:
- What is the project's real direction?
- What should it work on next?
- What should it stop pretending it can do?

## Adapting to Focus

**Full direction analysis** (default): All 4 agents, complete report, beads materialization.

**Feature evaluation** ("should we build X?"): Run A + C only. Evaluate the specific feature against the 8-dimension framework in `references/alignment-review.md`. Output: alignment assessment, tractability verdict, recommended next step.

**Spec-drift check** ("does code match spec?"): Run B only. Output: spec adherence inventory with implemented/partial/contradicted/missing status per section.

**Work decomposition** ("break this down"): Skip Phases 1-2. Read the spec and code for the specific feature. Decompose directly into chunks per `references/work-plan-template.md`.

## Edge Cases

| Situation | Handling |
|-----------|----------|
| No specs exist | Phase 2A infers goals from code/docs. First work item: write specs for core features. |
| Specs exist but are outdated | Agent B catalogs drift. Work plan starts with spec reconciliation. |
| No clear project direction | State this directly. Recommend a direction-setting workshop or spec sprint before any feature work. |
| Conflicting specs | Flag each contradiction with evidence from both sides. Do not resolve — escalate to user. |
| Massive spec surface (>50 sections) | Agent B samples: fully audit core features, spot-check secondary features. |

## References

| File | Read when | Content |
|------|-----------|---------|
| `references/direction-model.md` | Phase 2 (agents A, B, C) | How to determine project spirit, classify requirements, and assess current state |
| `references/alignment-review.md` | Phase 2 (agent D) | 8-dimension evaluation framework, classification buckets, push-back checklist, gap analysis |
| `references/work-plan-template.md` | Phase 3 (orchestrator) | Chunk decomposition rules, reconciliation patterns, complete output format |
| `references/subagent-template.md` | Phase 2 (dispatch) | Agent roles, dispatch template, depth limits, per-agent notes |
| `references/epic-report.md` | Phase 4 (report bead content) | Report structure, `/excalidraw-diagram` integration, beads follow-up, spec compliance matrix |

## Scripts

- `scripts/spec-scan.sh <repo_root>` — Discovers specs, design docs, roadmap, agent context, issue tracking, git activity by area. Run first, always.
- `scripts/epic-report-scaffold.sh <epic-id> [repo_root]` — Used by the report bead executor. Bootstraps report markdown from beads epic data, creates `docs/reports/` with metadata pre-filled.
