# Verified Workflow Improvement Notes for `th-projects`

Date: 2026-06-17  
Scope: `skills/personal/th-projects` on GitHub `main`  
Reviewer posture: evidence-first correction pass after an earlier overclaimed review

## Executive Summary

This replaces the earlier workflow-review draft. The earlier draft should not be used as planning input: its highest-priority findings about routing overlap, script path normalization, sign-off visibility, handoff contracts, and formatting did not survive verification against the actual files.

The `th-projects` workflow is already structurally strong. The root router clearly separates Shape, Feature Request, Review, and Direction. `project-review` classifies findings and hands confirmed findings to `project-direction`; `project-direction` decides sequencing and planning; `project-feature-request` handles one proposal through sign-off; `project-shape` owns the five-pillar baseline.

The highest-ROI improvement is not more process ceremony. It is adding a **review veracity gate** so future project-review outputs cannot promote unverified or contradicted claims into P0/P1 recommendations. A second useful improvement is expanding package-level regression fixtures beyond `project-shape`, especially around third-party reviews, ambiguous spec-drift routing, and overclaimed audit findings.

Confidence: Medium-high for text/documentation claims verified against GitHub `main`. Low for execution behavior because scripts were not run locally.

---

## Veracity Passes Performed

### Pass 1 — Root router and lifecycle

Read:

- `skills/personal/th-projects/SKILL.md`
- `subskills/project-shape/SKILL.md`
- `subskills/project-feature-request/SKILL.md`
- `subskills/project-review/SKILL.md`
- `subskills/project-direction/SKILL.md`

Verified:

- The root router defines the four-subskill lifecycle.
- It explicitly says review classifies and direction decides.
- It states subskills use stable relative paths.
- It requires major claims to cite evidence with `[Observed]`, `[Inferred]`, or `[Unknown]`.

### Pass 2 — Review/direction boundary

Read:

- `subskills/project-review/SKILL.md`
- `subskills/project-direction/SKILL.md`

Verified:

- `project-review` is explicitly not for deciding what to build next.
- `project-direction` is explicitly not for scoring repo health or confirming findings.
- `project-direction` has a receiver protocol for fresh review packets and feature-request deltas.
- Confirmed review findings feed direction; direction should not re-derive them when the packet is fresh.

### Pass 3 — Spec workflow and format

Read:

- `references/spec-format.md`
- `subskills/project-shape/references/pillar-spec-and-spine.md`
- `subskills/project-direction/references/openspec-changeset.md`

Verified:

- The shared root `spec-format.md` documents the base format with `Purpose`, `ADDED Requirements`, WHEN/THEN scenarios, and `[TARGET-STATE]`.
- The richer spec lifecycle is documented in `pillar-spec-and-spine.md`.
- Changeset creation is delegated to the OpenSpec CLI in `openspec-changeset.md`; agents are told not to hand-write changeset scaffolds.

### Pass 4 — Visible package structure

Read GitHub directory listings for:

- `skills/personal/th-projects/`
- `subskills/project-shape/`
- `subskills/project-review/`
- `subskills/project-direction/`
- `subskills/project-feature-request/`
- script and fixture subdirectories where visible

Verified:

- Root `th-projects/` visibly contains `agents/`, `references/`, `subskills/`, and `SKILL.md`; no root `scripts/` or `tests/` directory is visible on GitHub `main`.
- `project-shape` visibly has `scripts/` and `tests/fixtures/`.
- `project-review` visibly has `agents/`, `references/`, `scripts/`, and `SKILL.md`; no local `tests/fixtures/` directory is visible.
- `project-direction` visibly has `agents/`, `references/`, `scripts/`, and `SKILL.md`; no local `tests/fixtures/` directory is visible.
- `project-feature-request` visibly has `agents/`, `references/`, and `SKILL.md`; no local `scripts/` or `tests/fixtures/` directory is visible.

### Pass 5 — Prior-claim invalidation

Each earlier recommendation was reclassified as `[Confirmed]`, `[Overstated]`, `[Incorrect]`, or `[Unverifiable]`. Only confirmed or proportionally useful items are retained below.

---

## Invalidated Prior Recommendations

These should not enter planning.

| Prior claim | Verdict | Evidence |
|---|---|---|
| P0: routing overlap between review and direction | Incorrect / already solved | `th-projects/SKILL.md` has explicit “Audit vs. plan” routing. `project-review/SKILL.md` says not for deciding what to build next. `project-direction/SKILL.md` says not for scoring repo health or confirming findings. |
| P0: normalize script paths because docs use `/scripts/...` | Incorrect | Root router says relative paths such as `../project-shape/...` are package-internal and stable. `project-review/SKILL.md` uses `../project-shape/scripts/shape-scan.sh` and `scripts/project-scan.sh`. `project-direction/SKILL.md` uses `<skill_dir>/scripts/spec-scan.sh`. |
| P1: formatting/long-line files | Unverifiable / likely tooling artifact | GitHub blob views report normal file sizes and line counts. The earlier finding came from parser/raw rendering behavior, not a local formatting check. |
| P1: handoff contracts are merely prose and therefore weak | Overstated | `project-review` defines a baseline packet and direction handoff packet. `project-direction` defines a receiver protocol. Prose contracts are acceptable for agent skills unless drift is observed. |
| P1: sign-off is not visible | Incorrect | `project-feature-request` defines a signed-off spec delta and says sign-off belongs to the user. `project-direction` says no coding before signoff. |
| P2: spec lifecycle is missing | Overstated | `pillar-spec-and-spine.md` documents spec lifecycle and divergence patterns. The smaller issue is that root `references/spec-format.md` does not clearly point to that richer lifecycle. |
| P2: lifecycle state machine required | Not justified | The router already defines lifecycle and direction has a reconciliation protocol. A full state machine would be extra ceremony unless misrouting is observed. |
| P1: README required | Not justified | `SKILL.md` intentionally acts as a thin router. A human README may help browsing, but it is not a workflow defect. |
| P3: GPT instruction length | Out of scope | That applied to external ChatGPT configuration, not this repo. |

---

## Confirmed Strengths to Preserve

### 1. Thin router, complete subskills

`th-projects/SKILL.md` is a concise router that loads at most one subskill body per task and treats subskills as complete standard packages. Preserve this. Do not bloat the router with duplicated subskill logic.

### 2. Clear review/direction boundary

The root router and subskill files already separate audit/classification from planning/sequencing. Preserve this boundary:

- `project-review`: classify, score, confirm findings, prepare handoff.
- `project-direction`: decide sequencing, synthesize changesets, produce beads graph handoff.
- `project-feature-request`: run one idea through the funnel to a signed-off spec delta.
- `project-shape`: establish and maintain the normative baseline.

### 3. Five-pillar project-shape model

The five-pillar model is coherent and useful:

- doctrine: `about/heart-and-soul/`
- design contracts: `about/legends-and-lore/`
- specs: `openspec/`
- topology: `about/lay-and-land/`
- engineering standards: `about/craft-and-care/`

The traceability chain from doctrine to RFC to spec to code to tests is the right backbone.

### 4. Proportionality principle

`project-feature-request` and `project-direction` both avoid unnecessary ceremony by scaling rigor to blast radius and whether normative truth changes. Preserve that bias.

### 5. Existing deep reconciliation model

`project-direction` already has a strong reconciliation protocol: change-tier for normative artifact changes, verify-tier for read-only consumption, convergence ceilings, and mechanical validations. Reuse that concept instead of inventing unrelated process.

---

# Recommended Improvement Cycles

## Cycle 1 — Add a Project Review Veracity Gate

Priority: P0  
Effort: S/M  
Status: Confirmed useful, not currently explicit enough  
Target files:

- `subskills/project-review/SKILL.md`
- `subskills/project-review/references/report-template.md`
- new: `subskills/project-review/references/review-veracity-gate.md`

### Problem

`project-review` requires evidence labels and citations, but it does not currently require an explicit adversarial pass over its own highest-severity findings before delivery. The prior failed review demonstrates the failure mode: plausible-sounding recommendations were promoted to P0 without contradiction-hunting against the actual files.

`third-party-review.md` has a stronger fact-checking protocol for external audits, but the same discipline should apply to any high-impact review output before it becomes planning input.

### Recommended change

Add a required Phase 3.5 before report delivery:

```md
### Phase 3.5 — Veracity Gate

Before delivering the report, challenge every Critical/High/P0/P1 finding and the top roadmap items.

For each claim:
1. Re-open the named file/path directly.
2. Search for contradictory evidence using exact terms from the claim.
3. Verify referenced paths exist.
4. Verify process claims against actual SKILL/docs/scripts/config.
5. Classify the claim:
   - [Confirmed]
   - [Overstated]
   - [Incorrect]
   - [Unverifiable]
6. Delete or demote anything not [Confirmed].
7. Include an appendix ledger of invalidated claims, but do not include them in the risk register or roadmap.
```

Add a special rule:

```md
Formatting, line-length, and script-invocation claims require either local checkout evidence or GitHub blob evidence. Raw/parser rendering alone is not sufficient.
```

### Acceptance criteria

- `project-review/SKILL.md` references the veracity gate before Phase 4 delivery.
- `report-template.md` includes a “Veracity Ledger” appendix.
- The risk register only includes `[Confirmed]` findings.
- A fixture review containing false path/routing claims is rejected or demoted.
- Any P0/P1 recommendation must cite both supporting evidence and checked contradictory evidence.

---

## Cycle 2 — Add Cross-Subskill Regression Fixtures

Priority: P1  
Effort: M  
Status: Confirmed useful from visible package asymmetry  
Target files/directories:

- new: `skills/personal/th-projects/scripts/validate-th-projects.sh`
- new: `subskills/project-review/tests/fixtures/`
- new: `subskills/project-direction/tests/fixtures/`
- new: `subskills/project-feature-request/tests/fixtures/`
- existing: `subskills/project-shape/tests/fixtures/`

### Problem

`project-shape` visibly has `tests/fixtures/` and self-test/evaluation scripts. The other subskills do not visibly have comparable local fixtures on GitHub `main`.

That does not prove they are untested elsewhere, and it should not be scored as a defect. But for a package whose job is routing, review discipline, and workflow correctness, local regression fixtures would be high leverage.

### Recommended fixtures

#### `project-review/tests/fixtures/third-party-overclaims/`

Include a deliberately flawed external review with:

- nonexistent paths
- overclaimed routing conflicts
- formatting claims based only on raw rendering
- missing-signoff claims contradicted by files
- recommended P0s that should be demoted

Expected outcome:

- false claims marked `[Incorrect]`
- unsupported claims marked `[Unverifiable]`
- no invalid claim enters the planning handoff

#### `project-direction/tests/fixtures/ambiguous-spec-drift/`

Include prompts like:

- “Does code match spec?”
- “What do we do about this confirmed spec/code drift?”
- “Break this approved spec into work.”

Expected outcome:

- read-only audit routes to `project-review`
- action/sequencing routes to `project-direction`
- approved-spec decomposition proceeds to beads planning

#### `project-feature-request/tests/fixtures/funnel-decisions/`

Include cases for:

- doctrine conflict
- parked idea
- too-vague-to-specify request
- small inline request
- large cross-boundary request

Expected outcome:

- correct gate outcome
- one request per run
- no implementation or sequencing leakage

### Suggested validator

```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Shell syntax checks for visible scripts.
find "$ROOT" -path '*/scripts/*.sh' -type f -print0 | xargs -0 -r bash -n

# Existing project-shape checks if present.
bash "$ROOT/subskills/project-shape/scripts/self-test.sh"
bash "$ROOT/subskills/project-shape/scripts/eval-fallbacks.sh"

# Future: fixture expectations for review/direction/feature-request.
# Keep this light: it validates routing/claim classification behavior, not full LLM output.
```

### Acceptance criteria

- Root package has a validation entrypoint.
- Existing `project-shape` self-tests still run through it.
- At least one fixture catches the exact class of failure that caused the bad prior review.
- CI or local maintainer workflow can run the validator without agent context.

---

## Cycle 3 — Clarify the Relationship Between Shared Spec Format and Spec Lifecycle

Priority: P2  
Effort: S  
Status: Confirmed documentation consistency improvement  
Target files:

- `references/spec-format.md`
- optional: `subskills/project-shape/references/pillar-spec-and-spine.md`
- optional: `subskills/project-direction/references/openspec-changeset.md`

### Problem

The root shared `spec-format.md` is intentionally small, but it currently says H2 headings are “Purpose” and “ADDED Requirements.” Elsewhere, `pillar-spec-and-spine.md` describes a broader lifecycle with additions/modifications in deltas, and `openspec-changeset.md` says the OpenSpec CLI owns changeset structure.

The issue is not that lifecycle semantics are missing from the package. They exist. The issue is that the shared format file may be read as the whole contract when it is actually the minimal base spec format plus a pointer to lifecycle/change tooling.

### Recommended change

Add a short “Scope of This File” section:

```md
## Scope of This File

This file defines the minimal shared requirement/scenario shape that all
`th-projects` subskills can rely on.

For active changesets, use the OpenSpec CLI-generated structure. Do not
hand-write `openspec/changes/` scaffolds. Delta lifecycle semantics live in:

- `subskills/project-shape/references/pillar-spec-and-spine.md`
- `subskills/project-direction/references/openspec-changeset.md`

Main specs commonly use `ADDED Requirements`; active changes may introduce
tool-provided delta headings. Follow the CLI template when it is present.
```

### Acceptance criteria

- `spec-format.md` no longer appears to contradict richer lifecycle docs.
- `project-feature-request` and `project-review` can cite `spec-format.md` for requirement/scenario syntax without accidentally constraining changeset semantics.
- `openspec-changeset.md` remains the authority for actual changeset generation.

---

## Cycle 4 — Add a Default Decision-Recording Convention for Rejected/Parked Feature Requests

Priority: P3  
Effort: S  
Status: Optional but useful  
Target files:

- `subskills/project-feature-request/SKILL.md`
- optional new template: `subskills/project-feature-request/references/decision-record-template.md`

### Problem

`project-feature-request` already says doctrine conflicts should be recorded where the project keeps decisions, and parked ideas should become exploratory RFC stubs. That is good. The only possible improvement is a default location when the target project has no existing convention.

### Recommended change

Add one proportional default:

```md
If the project has no established decision home, default to:

- rejected requests: `about/legends-and-lore/decisions/YYYY-MM-DD-rejected-{slug}.md`
- parked requests: `about/legends-and-lore/rfcs/YYYY-MM-DD-parked-{slug}.md`

If the project already has ADR/RFC/decision conventions, use those instead.
```

### Acceptance criteria

- The default is explicitly subordinate to project-local conventions.
- Rejected feature requests do not become backlog items.
- Parked feature requests do not masquerade as approved work.

---

## Cycle 5 — Optional Human README Only If Browsing Friction Exists

Priority: P3 / defer  
Effort: S  
Status: Not a defect  
Target file:

- optional: `skills/personal/th-projects/README.md`

### Problem

The root directory does not visibly contain `README.md`, but `SKILL.md` already acts as a thin router and lifecycle summary. Adding a README could help humans browsing GitHub, but it is not required for the agent workflow.

### Recommended change

Only add this if maintainers or users are getting lost in the directory.

Keep it tiny:

```md
# TH Projects

Use this package for spec-driven project governance.

Lifecycle:
1. Shape — establish project knowledge architecture.
2. Feature Request — turn one idea into a signed-off spec delta.
3. Review — audit implementation vs baseline and health criteria.
4. Direction — decide sequencing and produce spec-linked work plan.

For agent execution, start with `SKILL.md`.
```

### Acceptance criteria

- README does not duplicate subskill rubrics.
- README links to `SKILL.md`.
- README stays human-facing, not another routing authority.

---

# Do Not Do

These would add ceremony or reintroduce false positives.

1. Do not rewrite routing unless a real misrouting fixture fails.
2. Do not replace prose handoff contracts with JSON schemas by default.
3. Do not add a full lifecycle state machine unless actual automation needs it.
4. Do not treat the earlier bad review as canon.
5. Do not preserve any review finding that fails the veracity gate.
6. Do not make local formatting claims from raw web/parser rendering.
7. Do not create beads or execution artifacts from `project-review` except the existing scoped spec-reconciliation exception.

---

# Suggested Improvement Backlog

| Priority | Item | Effort | Why |
|---|---:|---:|---|
| P0 | Add Project Review Veracity Gate | S/M | Directly prevents recurrence of false P0/P1 findings. |
| P1 | Add cross-subskill regression fixtures | M | Protects routing and review semantics across all four subskills. |
| P1 | Add root `validate-th-projects.sh` | S/M | Gives maintainers one command to run visible package checks. |
| P2 | Clarify `spec-format.md` vs spec lifecycle/change semantics | S | Removes a real documentation ambiguity without changing architecture. |
| P3 | Add default rejected/parked decision-record path | S | Useful fallback, subordinate to project-local conventions. |
| P3 | Add tiny human README only if needed | S | Helpful for browsing, but not necessary for agent workflow. |

---

# Final Verdict

Healthy, with one important process-hardening gap.

The conceptual workflow is sound and the prior review was wrong to call routing, paths, handoff prose, and signoff discipline broken. The real improvement opportunity is to make the project-review process robust against overconfident external or agent-generated audits. Add a veracity gate and regression fixtures, and the workflow becomes much harder to poison with plausible but false recommendations.
