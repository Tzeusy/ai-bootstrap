---
name: project-direction
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

### Preflight: Gather Context

Ask the user (or infer from the repo):

| Parameter | Values | Default |
|-----------|--------|---------|
| Project type | library, SDK, backend, SaaS, frontend, CLI, mobile, monorepo, ML/data, internal tool, IaC | Infer |
| Primary user | developers, end users, internal team, enterprises | Infer |
| Maturity | prototype, beta, production, mission-critical | Infer |
| Spec location | openspec/, spec/, docs/design/, or "none" | Infer from scan |
| Focus | Full direction analysis, specific feature evaluation, spec-drift check | Full |

### Reconciliation Protocol (Mandatory for Phases 1-3)

Each phase below MUST include at least 4 reconciliation passes (`R1`-`R4` minimum). A pass is a subagent-driven deep-dive review of the latest generated artifacts and diffs for that phase.

Pass requirements:
- Use a dedicated subagent for each pass.
- Feed the subagent the latest changed files, relevant specs/docs, and acceptance criteria.
- Apply fixes from the pass before launching the next pass.
- Continue beyond 4 passes if acceptance criteria are not met.

Use this unbiased prompt persona for every reconciliation pass (customize only the phase context and artifact list):

```text
You are a lead software architect at a world-class software organization.
Perform an unbiased deep-dive reconciliation review of the provided artifacts.
Do not assume they are correct or incorrect.
Identify contradictions, omissions, requirement drift, weak assumptions, and unverifiable claims.
Map every finding to concrete evidence (file/section references) and to phase acceptance criteria.
Recommend the minimum precise changes required to reach acceptance.
```

### Phase 1: /project-shape Reconciliation (Doctrine First)

Run a `/project-shape` reconciliation pass to ensure all proposed/new features align with the project's central doctrine.

Execution:
1. Reconcile `about/heart-and-soul/` and `about/legends-and-lore/` so they form one coherent doctrine-and-policy baseline.
2. Map each proposed feature/initiative to this baseline; flag and resolve doctrine conflicts.
3. Run mandatory reconciliation passes (`R1`-`R4+`) using the protocol above.
4. Finalize shape docs.

Acceptance criteria:
- Full synthesis between "heart-and-soul" and "legends-and-lore".
- New/proposed features are explicitly aligned (or explicitly rejected/escalated) against doctrine.
- Shape docs are committed and pushed before Phase 2 begins.

### Phase 2: Specification Scan + Fitness/Gap Synthesis ("Spec-and-Spine")

Run the specification and implementation reconciliation workflow, then synthesize an OpenSpec changeset through `/opsx:ff`.

Steps:
1. Run the spec-focused scan:
   ```bash
   bash <skill_dir>/scripts/spec-scan.sh <repo_root>
   ```
2. Run parallel investigation (A, B, C), then synthesis (D):

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| A | Doctrine/spec intent validation | Shape docs + scan + specs | Intent model, mandate checks, requirement fidelity |
| B | Spec adherence & workflows | Scan + specs | Spec drift inventory, workflow completeness |
| C | Implementation fitness | Scan + code | Test confidence, observability, delivery readiness, architectural fitness |
| D | Alignment & gap synthesis | A + B + C | Alignment matrix, gaps, push-back list, spec deltas |

3. Use `/opsx:ff` to synthesize all findings into an OpenSpec changeset.
4. Run mandatory reconciliation passes (`R1`-`R4+`) over the OpenSpec changeset and supporting analysis.
5. Finalize spec updates.

Acceptance criteria:
- Full readiness of "spec-and-spine" (spec intent, implemented spine, and gap analysis are coherent and actionable).
- OpenSpec changeset is complete, internally consistent, and traceable to doctrine + implementation evidence.
- Spec changes are committed and pushed before Phase 3 begins.

### Phase 3: Beads Generation (Planning Graph Only)

Call `/beads-writer` to create a full, acyclic dependency graph of work from the approved OpenSpec changeset.

Execution:
1. Generate epics/tasks with explicit dependencies and no cycles.
2. Ensure each bead traces back to doctrine/lore/spec mandates and acceptance criteria.
3. Include required reconciliation/report structural beads per `/beads-writer` conventions.
4. Run mandatory reconciliation passes (`R1`-`R4+`) on the graph (cycle checks, mandate coverage checks, dependency sanity).

Acceptance criteria:
- Full coherence between generated beads and `/project-shape` doctrine/lore plus OpenSpec mandates.
- Dependency graph is acyclic, prioritized, and execution-ready.
- Delivery/execution is NOT handled by `project-direction`; this is separately owned by `beads-coordinator` runs.

### Handoff Output (No Delivery Ownership)

Output the direction report per `references/work-plan-template.md`, including:
- What is the project's real direction?
- What should it work on next?
- What should it stop pretending it can do?
- Which beads graph was generated and why it is coherent with doctrine/lore/spec.

Do not execute or deliver the beads plan here; hand off explicitly to `beads-coordinator`.

## Adapting to Focus

All focus modes MUST preserve Phases 1-3 and the mandatory `R1`-`R4+` reconciliation passes for each phase. Focus changes depth/scope within a phase, not phase existence.

**Full direction analysis** (default): Full scope in Phases 1-3 plus handoff output.

**Feature evaluation** ("should we build X?"): Narrow all phases to feature X. In Phase 2, keep the 8-dimension evaluation from `references/alignment-review.md`.

**Spec-drift check** ("does code match spec?"): Phase 2 emphasizes B + C + D outputs, but still requires doctrine reconciliation in Phase 1 and bead graph updates in Phase 3 for confirmed gaps.

**Work decomposition** ("break this down"): Run all phases with minimal breadth. Phase 3 output is the primary artifact.

## Edge Cases

| Situation | Handling |
|-----------|----------|
| No specs exist | Phase 2 creates initial OpenSpec through `/opsx:ff`; do not skip doctrine reconciliation in Phase 1. |
| Specs exist but are outdated | Agent B catalogs drift; Phase 2 must produce a corrective OpenSpec changeset before Phase 3. |
| No clear project direction | State this directly. Recommend a direction-setting workshop or spec sprint before any feature work. |
| Conflicting specs | Flag each contradiction with evidence from both sides. Do not resolve — escalate to user. |
| Massive spec surface (>50 sections) | Agent B samples: fully audit core features, spot-check secondary features. |

## References

| File | Read when | Content |
|------|-----------|---------|
| `references/direction-model.md` | Phase 1 and Phase 2 (agents A, B, C) | Project spirit, requirement classification, current-state assessment |
| `references/alignment-review.md` | Phase 2 (agent D) | 8-dimension evaluation framework, classification buckets, push-back checklist, gap analysis |
| `references/work-plan-template.md` | Handoff output | Output format, sequencing presentation, reconciliation reporting |
| `references/subagent-template.md` | Phases 1-3 (reconciliation and dispatch) | Agent roles, dispatch template, depth limits, per-agent notes |
| `references/epic-report.md` | Phase 3 (beads structure) | Report bead structure, `/excalidraw-diagram` integration, spec compliance matrix |

## Scripts

- `scripts/spec-scan.sh <repo_root>` — Discovers specs, design docs, roadmap, agent context, issue tracking, git activity by area. Required in Phase 2.
- `scripts/epic-report-scaffold.sh <epic-id> [repo_root]` — Used by report bead executors created in Phase 3. Bootstraps report markdown from beads epic data, creates `docs/reports/` with metadata pre-filled.
