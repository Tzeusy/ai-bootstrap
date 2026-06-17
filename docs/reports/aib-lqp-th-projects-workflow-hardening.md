# Epic Report: th-projects Workflow Hardening (Veracity Gate + Regression Fixtures)

**Epic ID**: `aib-lqp`
**Date**: 2026-06-17
**Status**: Children aib-lqp.1–.5 complete; this report (aib-lqp.7) is the capstone reconciliation + veracity self-audit for human review.
**Spec coverage**: No `openspec/` spec governs the `th-projects` skill package itself; the normative contract for this epic is the design document `about/craft-and-care/th-projects-workflow-review-verified.md` (the verified workflow review that seeded each child bead).

> **Worker contract note:** This report was authored without running any `bd`
> command (coordinator owns lifecycle state). The bundled
> `epic-report-scaffold.sh` requires `bd`, so its structure was reproduced
> manually. Child enumeration below is sourced from the git history of this
> worktree (commits referencing `aib-lqp.*`), not from `bd children`.

---

## Summary

Epic `aib-lqp` hardens the `th-projects` skill package against the exact failure
mode that produced an earlier overclaimed workflow review: plausible-but-false
findings being promoted into P0/P1 planning input. The seeding design doc
(`about/craft-and-care/th-projects-workflow-review-verified.md`) ran an
evidence-first correction pass over the package on GitHub `main`, invalidated
its own prior review's top findings, and proposed five improvement cycles. This
epic implemented Cycles 1–4 (Cycle 5, an optional human README, was correctly
left as defer/not-a-defect).

What was built: a required **Phase 3.5 Veracity Gate** in `project-review`
(with a standalone procedure reference, a "Veracity Ledger" report appendix, and
a worked overclaim fixture); **cross-subskill regression fixtures** for
`project-direction` and `project-feature-request`; a root
**`validate-th-projects.sh`** entrypoint that runs shell syntax checks,
project-shape self-tests, and fixture-structural checks (51/51 passing in this
worktree); a **"Scope of This File"** section disambiguating `spec-format.md`
from changeset/lifecycle docs; and **default rejected/parked decision-record
paths** in `project-feature-request`.

Current state: all five child acceptance criteria are met and verified against
committed files in this worktree (matrix below). The validator passes. The
epic's own seeding claims were re-audited through the new veracity gate; no
seeding claim is `[Incorrect]`. The only nuance is that several point-in-time
structural observations in the seeding doc ("no `scripts/`/`tests/fixtures/`
visible") were accurate at review time and have since been *superseded by this
very epic* — these are ledgered below as `[Overstated if read present-tense]`,
not defects.

---

## Implementation

### Children

| Bead ID | Title | Commit | Status |
|---------|-------|--------|--------|
| aib-lqp.1 | Phase 3.5 Veracity Gate in project-review | c749855 (#3) | Done |
| aib-lqp.2 | Regression fixtures (direction + feature-request) | ac10bd8 (#8) | Done |
| aib-lqp.3 | `validate-th-projects.sh` package validator | ea02373 (#11) | Done |
| aib-lqp.4 | "Scope of This File" in `spec-format.md` | 2781ca1 (#6) | Done |
| aib-lqp.5 | Default rejected/parked decision-record paths | de46986 (#10) | Done |
| aib-lqp.7 | Capstone reconciliation + veracity self-audit (this report) | — | In progress |

> The `project-review/tests/fixtures/third-party-overclaims/` fixture landed with
> aib-lqp.1 (c749855), not aib-lqp.2; aib-lqp.2 added the `project-direction`
> and `project-feature-request` fixtures (ac10bd8).

---

## Spec-Compliance Matrix

Each completed child mapped to its acceptance criteria, verified against the
committed files in this worktree. Citations are `path:line` or `path§section`.

### aib-lqp.1 — Phase 3.5 Veracity Gate — **[Confirmed]**

| Acceptance criterion | Evidence | Verdict |
|---|---|---|
| `project-review/SKILL.md` references the veracity gate before Phase 4 delivery | `subskills/project-review/SKILL.md:111-126` (Phase 3.5 section, ordered before Phase 4 at line 128); references table row at `:162` | [Confirmed] |
| `report-template.md` includes a "Veracity Ledger" appendix | `subskills/project-review/references/report-template.md:204` (`### D. Veracity Ledger`), entry-format table + empty-ledger instruction at `:208-215` | [Confirmed] |
| Risk register only includes `[Confirmed]` findings | `report-template.md:143` ("_Only [Confirmed] findings from Phase 3.5 appear here..._") | [Confirmed] |
| A fixture review with false path/routing claims is rejected/demoted | `subskills/project-review/tests/fixtures/third-party-overclaims/` (README.md, input-review.md with P0 claims, expected-gate-output.md classifying Findings 1 & 2 `[Incorrect]`); validator enforces "no P0/Critical rows survived into Revised Risk Register" | [Confirmed] |
| Any P0/P1 must cite supporting **and** checked contradictory evidence | `SKILL.md:126`; full rule in `references/review-veracity-gate.md:104-112` (P0/P1 survivability requirement) | [Confirmed] |
| (Bonus) Standalone gate procedure exists | `references/review-veracity-gate.md` — six-step per-claim procedure (`:24-86`), special evidence rules (`:89-112`), ledger format (`:116-136`) | [Confirmed] |

### aib-lqp.2 — Cross-subskill regression fixtures — **[Confirmed]**

| Acceptance criterion | Evidence | Verdict |
|---|---|---|
| `project-direction` ambiguous-spec-drift fixtures | `subskills/project-direction/tests/fixtures/ambiguous-spec-drift/{read-only-audit,action-after-confirmed-drift,decompose-approved-spec}/FIXTURE.md`; read-only routes to `project-review` (`read-only-audit/FIXTURE.md:16`), action routes to `project-direction` (`action-after-confirmed-drift/FIXTURE.md:18`), approved-spec decomposition routes to Phase 3 beads (`decompose-approved-spec/FIXTURE.md:18`) | [Confirmed] |
| `project-feature-request` funnel-decisions fixtures (doctrine conflict, parked, too-vague, small inline, large cross-boundary) | `subskills/project-feature-request/tests/fixtures/funnel-decisions/{doctrine-conflict,parked,too-vague-to-specify,small-inline,large-cross-boundary}/FIXTURE.md`; parked → "write exploratory RFC stub, stop" (`parked/FIXTURE.md:23`) | [Confirmed] |
| At least one fixture catches the prior-review failure class | `project-review/tests/fixtures/third-party-overclaims/` (overclaimed routing + nonexistent paths → `[Incorrect]`) | [Confirmed] |

### aib-lqp.3 — `validate-th-projects.sh` — **[Confirmed]**

| Acceptance criterion | Evidence | Verdict |
|---|---|---|
| Root package has a validation entrypoint | `skills/personal/th-projects/scripts/validate-th-projects.sh` exists | [Confirmed] |
| Existing `project-shape` self-tests still run through it | Validator output: "project-shape self-tests" section runs `self-test.sh` (8 cases PASS) and `eval-fallbacks.sh` (10 checks PASS) | [Confirmed] |
| Validator runs without agent context and passes | `bash skills/personal/th-projects/scripts/validate-th-projects.sh` → **`Results: 51/51 checks passed`**, exit 0 (run in this worktree) | [Confirmed] |
| Catches the bad-prior-review failure class | Validator asserts "overclaim check — P0 claims appear in Veracity Ledger as [Incorrect]/[Unverifiable]" and "no P0/Critical rows survived into Revised Risk Register" — both PASS | [Confirmed] |

### aib-lqp.4 — "Scope of This File" in `spec-format.md` — **[Confirmed]**

| Acceptance criterion | Evidence | Verdict |
|---|---|---|
| `spec-format.md` no longer reads as the whole contract | `references/spec-format.md:3-20` ("Scope of This File"): explicitly "minimal shared syntax… not how changesets are structured or how specs evolve" | [Confirmed] |
| Points to changeset + lifecycle authorities | `spec-format.md:12-20` links `openspec-changeset.md` (changeset scaffolding) and `pillar-spec-and-spine.md` (lifecycle/traceability) | [Confirmed] |
| `openspec-changeset.md` remains changeset authority | `spec-format.md:12-15` explicitly defers changeset structure to the OpenSpec CLI + that reference | [Confirmed] |

### aib-lqp.5 — Default rejected/parked decision-record paths — **[Confirmed]**

| Acceptance criterion | Evidence | Verdict |
|---|---|---|
| Default subordinate to project-local conventions | `subskills/project-feature-request/SKILL.md:113-118` ("Default when the project has no decision home"); `references/decision-record-template.md:3-5` ("**Project conventions always take precedence**") | [Confirmed] |
| Rejected requests do not become backlog items | `SKILL.md:113` ("do not soften into a backlog item"); rejected path `about/legends-and-lore/decisions/YYYY-MM-DD-rejected-{slug}.md` (`:115`) | [Confirmed] |
| Parked requests do not masquerade as approved work | `SKILL.md:116-118` (parked → exploratory RFC stub at `about/legends-and-lore/rfcs/YYYY-MM-DD-parked-{slug}.md`); parked fixture confirms "no implementation/sequencing leakage" | [Confirmed] |
| (Bonus) Template provided | `references/decision-record-template.md` — minimal sections for both record types | [Confirmed] |

**Matrix result: 5/5 children [Confirmed]. No [Overstated] or [Incorrect] child criteria.**

---

## META Veracity Self-Audit

The new Cycle-1 veracity gate
(`subskills/project-review/references/review-veracity-gate.md`) is applied here to
the epic's **own seeding claims** — the claims in
`about/craft-and-care/th-projects-workflow-review-verified.md` that motivated each
bead. Each is re-verified against the *live* files in this worktree.

### Confirmed seeding claims

| Seeding claim (source line) | Verification | Verdict |
|---|---|---|
| Cycle 1: "project-review… does not currently require an explicit adversarial pass over its own highest-severity findings before delivery" (review doc §Cycle 1 Problem) | Git history: `review-veracity-gate.md` and Phase 3.5 first appear in commit c749855 (aib-lqp.1). No earlier veracity-gate artifact exists. | [Confirmed] (accurate at seeding time) |
| Cycle 1: "`third-party-review.md` has a stronger fact-checking protocol" | `subskills/project-review/references/third-party-review.md` exists and is cited from `SKILL.md:137,161` | [Confirmed] |
| Cycle 3: "`spec-format.md`… currently says H2 headings are 'Purpose' and 'ADDED Requirements'" | `references/spec-format.md:46` ("H2: Always 'Purpose' and 'ADDED Requirements'") | [Confirmed] |
| Cycle 4: "project-feature-request already says doctrine conflicts should be recorded… and parked ideas should become exploratory RFC stubs" | `subskills/project-feature-request/SKILL.md:113-118` | [Confirmed] |
| Strength #3: five-pillar model maps to `about/heart-and-soul`, `about/legends-and-lore`, `openspec/`, `about/lay-and-land`, `about/craft-and-care` | All five pillars present in this repo (`about/craft-and-care/` listed; `openspec/` present) | [Confirmed] |

### Veracity Ledger (seeding claims that do not survive present-tense reading)

These were `[Confirmed]` at review time but are **superseded by this epic**. Per
the gate, present-tense structural claims that no longer hold are ledgered rather
than treated as planning inputs. None is a defect; each is the precise gap the
epic closed.

| Prior seeding claim | Classification | Invalidating evidence / reason |
|---|---|---|
| Pass 4: "no root `scripts/` or `tests/` directory is visible" for `th-projects/` (review doc:79) | [Overstated if read present-tense] | `skills/personal/th-projects/scripts/validate-th-projects.sh` now exists (aib-lqp.3, ea02373). Claim was accurate on GitHub `main` at review time; epic created the entrypoint. |
| Pass 4: "`project-review` visibly has… no local `tests/fixtures/` directory" (review doc:81) | [Overstated if read present-tense] | `subskills/project-review/tests/fixtures/third-party-overclaims/` now exists (aib-lqp.1, c749855). |
| Pass 4: "`project-direction` visibly has… no local `tests/fixtures/` directory" (review doc:82) | [Overstated if read present-tense] | `subskills/project-direction/tests/fixtures/ambiguous-spec-drift/` now exists (aib-lqp.2, ac10bd8). |
| Pass 4: "`project-feature-request` visibly has… no local `scripts/` or `tests/fixtures/` directory" (review doc:83) | [Overstated if read present-tense] | `subskills/project-feature-request/tests/fixtures/funnel-decisions/` now exists (aib-lqp.2, ac10bd8). |

**Self-audit result:** No seeding claim is `[Incorrect]` or `[Unverifiable]`. The
five motivating claims are `[Confirmed]`. Four point-in-time structural
observations are `[Overstated if read present-tense]` solely because the epic
delivered the missing artifacts — the expected, healthy outcome.

### Self-application of the gate to *this report*

Per the P0/P1 survivability rule, this report makes no P0/P1 risk claims. Every
matrix row cites a concrete `path:line`/`§section` opened in this worktree (Step
1) and, for the gate's own self-consistency, contradictory evidence was sought
(e.g., confirming no pre-aib-lqp.1 veracity gate existed via git history). The
validator result (51/51) is local-checkout evidence, satisfying the special rule
for script-invocation claims.

---

## Spec / openspec Drift

`openspec/changes/` contains only `bootstrap-project-shape/` (specs for
`repository-shape` — the project-shape pillar bootstrap), which predates and is
unrelated to this epic. **No openspec change governs the `th-projects` skill
package**, and this epic introduced no openspec drift. The governing artifact for
this epic remains the design doc in `about/craft-and-care/`.

---

## craft-and-care Update Decision

**No update made — and that is the correct outcome.** The task contract says to
update `about/craft-and-care/` *only if the workflow contract changed*. This epic
*implemented* the recommendations already documented in
`about/craft-and-care/th-projects-workflow-review-verified.md`; it did not change
the contract that document defines. The verified review doc already records the
five cycles, their acceptance criteria, and the "Do Not Do" guardrails. Editing
it now would be inventing a change that did not occur. The doc stands as the
accurate design contract; this report is the implementation/verification record.

---

## Quality Gate

- **Validator**: `bash skills/personal/th-projects/scripts/validate-th-projects.sh`
  → **`Results: 51/51 checks passed`** (exit 0), run in this worktree. Covers:
  shell syntax (8 scripts), project-shape self-tests (8 cases) + fallback checks
  (10), and fixture-structural checks for all three new fixture sets including the
  overclaim-gate assertions.
- **Veracity discipline applied to this report**: every claim cites a file
  opened in this worktree; no P0/P1 overclaims; superseded seeding claims
  ledgered rather than asserted as current.

---

## Risks & Notes for Reviewer

### Known risks

| Risk | Severity | Mitigation | Evidence |
|------|----------|-----------|----------|
| Fixtures are *structural* (presence/section/routing-string checks), not LLM-behavioral — they cannot prove an agent actually classifies correctly at runtime | L | Intentional per seeding doc ("validates routing/claim classification behavior, not full LLM output", review doc:288); structural assertions still catch the prior failure class | `validate-th-projects.sh` fixture checks; review doc:286-288 |
| The veracity gate is prose guidance in a SKILL/reference, enforced only by agent compliance | L | Worked fixture + validator assertion ("no P0/Critical rows survived into Revised Risk Register") give a concrete calibration target | `expected-gate-output.md`; validator overclaim checks |

### What to look at first

1. `subskills/project-review/references/review-veracity-gate.md` — the core new contract.
2. `subskills/project-review/tests/fixtures/third-party-overclaims/expected-gate-output.md` — the worked calibration example.
3. Validator output (51/51) — single command reproducing the quality gate.

### Questions for reviewer

- Confirm Cycle 5 (optional human README) should remain deferred (epic correctly did not implement it; it was flagged "Not a defect / defer").

---

## Subsequent Work

No new follow-up beads are required for epic completion. Optional/deferred items:

| Item | Type | Rationale |
|------|------|-----------|
| Cycle 5: tiny human `README.md` for `th-projects/` | defer | Seeding doc classifies it "Not a defect"; add only if browsing friction is reported. |
| Behavioral (LLM-in-the-loop) fixture harness | defer | Current structural fixtures are deliberately light; upgrade only if routing regressions are observed in practice. |

---

## Appendix

### A. Commits referencing this epic

```
ea02373 feat: add validate-th-projects.sh package validator [aib-lqp.3] (#11)
de46986 feat: add default decision/RFC paths for project-feature-request [aib-lqp.5] (#10)
ac10bd8 Add regression fixtures for project-direction and project-feature-request (#8) [aib-lqp.2]
2781ca1 docs: add Scope of This File to spec-format.md [aib-lqp.4] (#6)
c749855 feat: add Phase 3.5 veracity gate to project-review [aib-lqp.1] (#3)
84da147 Add verified th-projects workflow review (design contract for epic aib-lqp)
```

### B. Key files delivered by this epic

```
skills/personal/th-projects/scripts/validate-th-projects.sh
skills/personal/th-projects/references/spec-format.md  (Scope of This File)
skills/personal/th-projects/subskills/project-review/SKILL.md  (Phase 3.5)
skills/personal/th-projects/subskills/project-review/references/review-veracity-gate.md
skills/personal/th-projects/subskills/project-review/references/report-template.md  (Veracity Ledger / Appendix D)
skills/personal/th-projects/subskills/project-review/tests/fixtures/third-party-overclaims/
skills/personal/th-projects/subskills/project-direction/tests/fixtures/ambiguous-spec-drift/
skills/personal/th-projects/subskills/project-feature-request/SKILL.md  (default decision paths)
skills/personal/th-projects/subskills/project-feature-request/references/decision-record-template.md
skills/personal/th-projects/subskills/project-feature-request/tests/fixtures/funnel-decisions/
```

### C. Verification environment

```
Worktree: .worktrees/parallel-agents/aib-lqp.7  (branch agent/aib-lqp.7)
Base: origin/main @ ea02373
Validator: 51/51 checks passed (exit 0)
Date: 2026-06-17
```
