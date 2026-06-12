---
name: project-direction
description: Analyze a software project's true direction, validate alignment between specs/docs and implementation, and produce a prioritized, spec-driven work plan with beads. Ensures every non-trivial epic includes a report-generation bead for human review. Use when deciding what to work on next, evaluating feature proposals, checking spec-to-code drift, sequencing roadmap items, or pushing back on misaligned requirements. Triggers on "what should we work on next", "prioritize features", "does the code match the spec", "is this roadmap aligned", "what's highest leverage", "should we build this", "is this tractable", "break this down into chunks".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
---

# Project Direction

Determine what a project should work on next. Ground decisions in specifications, repository evidence, and implementation reality. Optimize for spec alignment, tractability, leverage, and low-churn execution — not feature count.

## Core Rules

1. **Specifications are source of truth** — every work item must link to a spec section. If a feature lacks spec coverage, recommend spec work first.
2. **No coding before signoff** — spec must be written/updated and approved before implementation begins.
3. **Evidence over assumption** — cite files, functions, spec sections. Label claims: [Observed], [Inferred], [Unknown].
4. **Push back when needed** — flag misaligned, premature, unrealistic, or infeasible work directly.
5. **Minimize churn** — favor removing dead paths over backward-compatibility shims (`/th-engineering` cruft-cleanup is the bar); serialize work that would conflict.
6. **Rigor where truth changes** — deep reconciliation guards *changes to normative artifacts*; consuming them takes one verification pass, not four.

## Workflow

### Preflight: Gather Context

Ask the user (or infer from the repo):

| Parameter | Values | Default |
|-----------|--------|---------|
| Project type | library, SDK, backend, SaaS, frontend, CLI, mobile, monorepo, ML/data, internal tool, IaC | Infer |
| Primary user | developers, end users, internal team, enterprises | Infer |
| Maturity | prototype, beta, production, mission-critical | Infer |
| Spec location | openspec/, spec/, docs/design/, or "none" | Infer from scan |
| Focus | Full direction analysis, feature evaluation, spec-drift check, work decomposition | Full |
| Inputs on hand | project-review handoff packet, project-feature-request spec delta, or cold start | Cold start |

Then check for upstream inputs — they change how much of each phase runs (see Receiver Protocol below).

### Receiver Protocol: Consume Upstream Packets, Don't Re-Derive Them

**From `../project-review/` (handoff packet).** A packet is *fresh* when the repo HEAD matches the reviewed commit, or the user accepts the staleness. For a fresh packet:
- Adopt its Phase 0 baseline packet (pillar maturity, source-of-truth order, extracted normative requirements, contradictions) — Phase 1 becomes a doctrine *check*, not a re-derivation.
- Treat its confirmed findings as Phase 2 evidence. Agent C skips the dimensions the review already scored (test confidence, observability, delivery readiness) and narrows to architectural fitness *for the proposed direction*.
- Feed its sequencing constraints, dependency hints, and deprioritized items directly to Agent D and Phase 3.
- Findings the packet labels as requiring doctrine/spec updates enter Phase 1/2 as work items, not as questions to re-investigate.

**From `../project-feature-request/` (signed-off spec delta).** The funnel already did doctrine, topology, design, and spec work for that request. Do not re-run it. Phase 1 is skipped unless the delta itself changed doctrine; Phase 2 narrows to integrating the delta into the changeset; Phase 3 sequences it against existing work.

**Cold start.** No packet, no delta: run the phases as written below.

### Reconciliation Protocol: Proportional to Risk

Reconciliation passes are subagent-driven deep-dive reviews of generated artifacts. Use the unbiased reviewer persona for every pass (customize only phase context and artifact list):

```text
You are a lead software architect at a world-class software organization.
Perform an unbiased deep-dive reconciliation review of the provided artifacts.
Do not assume they are correct or incorrect.
Identify contradictions, omissions, requirement drift, weak assumptions, and unverifiable claims.
Map every finding to concrete evidence (file/section references) and to phase acceptance criteria.
Recommend the minimum precise changes required to reach acceptance.
```

Two tiers, chosen per phase by what the phase did:

| Tier | When it applies | Protocol |
|------|-----------------|----------|
| **Change-tier** | The phase *modified normative artifacts*: doctrine/lore edits, OpenSpec changeset creation or modification | At least 4 dedicated passes (`R1`-`R4`), fresh subagent each, fixes applied between passes; continue while acceptance criteria are unmet |
| **Verify-tier** | The phase only *consumed* normative artifacts: doctrine checks, drift analysis, graph generation from an approved changeset | One dedicated verification pass; escalate to change-tier only if it finds the consumed artifacts themselves need modification |

Mechanical validations (dependency cycle checks, spec-link coverage, mandate coverage) are scripts-and-checklists work — run them directly; they do not count as passes and do not require subagents.

**Convergence ceiling**: if any artifact set still fails acceptance criteria after 6 passes, stop. Summarize the unresolved findings with evidence, present the disagreement to the user, and do not proceed to the next phase on an unconverged artifact.

**Commit discipline**: commit normative changes when their phase converges (so later phases build on a fixed base). Read-only runs — where no normative artifact changed — make no commits and need no push gates. Pushing follows the repository's own convention, at the end of the run.

### Phase 1: Doctrine Alignment (project-shape Baseline)

Establish that proposed work is judged against the project's actual doctrine.

Execution:
1. Obtain the shape baseline: adopt a fresh review packet's baseline, or run `../project-shape/scripts/shape-scan.sh` and read `about/heart-and-soul/` + `about/legends-and-lore/`.
2. Map each proposed feature/initiative to that baseline; flag doctrine conflicts.
3. If doctrine/lore documents themselves need editing (contradictions, gaps that block judgment) — make the edits and run **change-tier** reconciliation on them.
4. If the docs are sound and merely consumed — run **verify-tier** (one pass over the feature-to-doctrine mapping).

Acceptance criteria:
- Every proposed feature is explicitly aligned, rejected, or escalated against doctrine, with citations.
- Any doctrine/lore edits are reconciled (change-tier) and committed before Phase 2 builds on them.

### Phase 2: Specification Scan + Fitness/Gap Synthesis

Steps:
1. Run the spec-focused scan:
   ```bash
   bash <skill_dir>/scripts/spec-scan.sh <repo_root>
   ```
2. Run parallel investigation (A, B, C), then synthesis (D) — roles and dispatch format in `references/subagent-template.md`:

| Agent | Role | Input | Output |
|-------|------|-------|--------|
| A | Doctrine/spec intent validation | Phase 1 baseline + scan + specs | Intent model, mandate checks, requirement fidelity |
| B | Spec adherence & workflows | Scan + specs | Spec drift inventory, workflow completeness |
| C | Implementation fitness | Scan + code (minus dimensions covered by a fresh review packet) | Test confidence, observability, delivery readiness, architectural fitness |
| D | Alignment & gap synthesis | A + B + C (+ review packet constraints) | Alignment matrix, gaps, push-back list, spec deltas |

3. Synthesize findings into an OpenSpec changeset per `references/openspec-changeset.md` (tool-agnostic `openspec` CLI loop; `/opsx:ff` is a Codex accelerator for the same procedure).
4. Run **change-tier** reconciliation on the changeset (it is a normative artifact). If the run produced no changeset — pure analysis, no spec changes — run **verify-tier** on the analysis instead.

Acceptance criteria:
- Spec intent, implemented spine, and gap analysis are coherent and actionable.
- Any changeset is complete, internally consistent, traceable to doctrine + implementation evidence, reconciled, and committed before Phase 3 sequences it.

### Phase 3: Beads Generation (Planning Graph Only)

Call `/beads-orchestration` (beads-writer) to create a full, acyclic dependency graph of work from the approved changeset.

Execution:
1. Generate epics/tasks with explicit dependencies and no cycles.
2. Ensure each bead traces back to doctrine/lore/spec mandates and acceptance criteria.
3. Include required reconciliation/report structural beads per beads-writer conventions (report beads use `scripts/epic-report-scaffold.sh`; see `references/epic-report.md`).
4. Run mechanical graph validations (cycle check, mandate coverage, spec-link coverage), then **verify-tier** reconciliation (the graph consumes the approved changeset; it does not modify it).

Acceptance criteria:
- Graph is acyclic, prioritized, execution-ready, and every bead is spec-traceable.
- Delivery/execution is NOT handled here — that is owned by `/beads-orchestration` (beads-coordinator).

### Handoff Output (No Delivery Ownership)

Output the direction report per `references/work-plan-template.md`, including:
- What is the project's real direction?
- What should it work on next?
- What should it stop pretending it can do?
- Which beads graph was generated and why it is coherent with doctrine/lore/spec.

Do not execute or deliver the beads plan here; hand off explicitly to the beads coordinator.

## Adapting to Focus

Focus modes change which phases do real work and which tier applies — the phase *questions* are always answered, even if the answer is one line backed by a citation.

**Full direction analysis** (default): All phases as written. Change-tier wherever normative artifacts change.

**Feature evaluation** ("should we build X?"): For a *new, single* request, route to `../project-feature-request/SKILL.md` — its funnel is the right tool, and its output comes back here as a spec delta. Run this mode only for portfolio questions (X against competing priorities): Phase 1 verify-tier doctrine check on X, Phase 2 narrowed to the 8-dimension evaluation from `references/alignment-review.md`, Phase 3 only if X is approved for scheduling. No commits unless specs changed.

**Spec-drift check** ("does code match spec?"): Phase 1 verify-tier (doctrine is consumed, not edited). Phase 2 emphasizes B + C + D; produce a corrective changeset (change-tier) only for confirmed drift the user wants fixed — otherwise deliver the drift inventory as a read-only report. Phase 3 only when a changeset was produced.

**Work decomposition** ("break this down"): Assumes an approved spec (from feature-request or a prior run). Phase 1 skipped unless the spec lacks any doctrine link. Phase 2 is one verify-tier pass confirming the spec is implementable as written. Phase 3 is the primary artifact, with its mechanical validations + verify-tier pass.

## Edge Cases

| Situation | Handling |
|-----------|----------|
| No specs exist | Phase 2 creates the initial changeset via `references/openspec-changeset.md`; doctrine check in Phase 1 still runs. |
| `openspec` CLI unavailable | Stop changeset synthesis and report it; deliver analysis + drift inventory, and recommend installing the CLI. Do not hand-write changeset scaffolds. |
| Specs exist but are outdated | Agent B catalogs drift; Phase 2 must produce a corrective changeset before Phase 3. |
| No clear project direction | State this directly. Recommend a direction-setting workshop or `../project-shape/` bootstrap before any feature work. |
| Conflicting specs | Flag each contradiction with evidence from both sides. Do not resolve — escalate to user. |
| Reconciliation won't converge | Convergence ceiling (6 passes): stop, present unresolved findings, await user judgment. |
| Massive spec surface (>50 sections) | Agent B samples: fully audit core features, spot-check secondary features. |

## References

| File | Read when | Content |
|------|-----------|---------|
| [`references/direction-model.md`](references/direction-model.md) | Phase 2 (agents A, B, C) | Project spirit, requirement classification, current-state assessment |
| [`references/alignment-review.md`](references/alignment-review.md) | Phase 2 (agent D); feature evaluation | 8-dimension evaluation framework, classification buckets, push-back checklist, gap analysis |
| [`references/openspec-changeset.md`](references/openspec-changeset.md) | Phase 2 step 3 | Tool-agnostic OpenSpec changeset synthesis via the `openspec` CLI |
| [`references/work-plan-template.md`](references/work-plan-template.md) | Handoff output | Output format, sequencing presentation, reconciliation reporting |
| [`references/subagent-template.md`](references/subagent-template.md) | Phases 1-3 (reconciliation and dispatch) | Agent roles, dispatch template, depth limits, per-agent notes |
| [`references/epic-report.md`](references/epic-report.md) | Phase 3 (beads structure) | Report bead structure, diagram integration, spec compliance matrix |

## Scripts

- [`scripts/spec-scan.sh`](scripts/spec-scan.sh) `<repo_root>` — Discovers specs, design docs, roadmap, agent context, issue tracking, git activity by area. Required in Phase 2.
- [`scripts/epic-report-scaffold.sh`](scripts/epic-report-scaffold.sh) `<epic-id> [repo_root]` — Used by report bead executors created in Phase 3. Bootstraps report markdown from beads epic data, creates `docs/reports/` with metadata pre-filled.
