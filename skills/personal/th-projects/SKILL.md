---
name: th-projects
description: >
  Use for project-level engineering governance: bootstrap or audit the
  doctrine/spec/topology/standards shape; concretize or amend one feature
  spec; reconcile specs and implementation; audit repo health; prioritize
  work; synthesize milestones; ideate from doctrine; run a recurring
  vision-pursuit; or accumulate and walk through independently vetted owner
  decisions. Route to exactly one subskill. Triggers: "project shape",
  "bootstrap docs", "what should we work on next", "should we build this",
  "spec this feature", "the spec is wrong", "review this project", "audit the
  codebase", "does code match the spec", "what's the next milestone",
  "brainstorm features", "run the vision pursuit", "relentlessly improve this
  project", "prepare decisions for me to review", "walk me through the blocked
  decisions", "collect owner signoffs".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
compatibility: Subskill scripts require bash, git, grep, find, and uv; project-shape uses uv for fail-closed YAML validation. project-direction additionally assumes the bd (beads) CLI and an OpenSpec-capable environment for changeset synthesis.
---

# TH Projects

Select one project-governance workflow. Internal subskills are package-local
and load lazily; do not read unrelated subskill bodies.

## Select a subskill

| Intent | Load | Distinguishing signal |
|---|---|---|
| Establish, place, audit, or explain the five-pillar project knowledge architecture | [`subskills/project-shape/SKILL.md`](subskills/project-shape/SKILL.md) | "bootstrap docs", "where should this live", "audit project shape" |
| Turn one proposal into a signed-off spec delta, or correct its governing spec | [`subskills/project-feature-request/SKILL.md`](subskills/project-feature-request/SKILL.md) | "spec this feature", "the spec is wrong" |
| Audit repo health or reconcile specs and implementation | [`subskills/project-review/SKILL.md`](subskills/project-review/SKILL.md) | "what is wrong", "does code match spec" |
| Choose, prioritize, or decompose approved work; derive a milestone; ideate from doctrine; administer the first-spec launch gate | [`subskills/project-direction/SKILL.md`](subskills/project-direction/SKILL.md) | "what next", "are we ready to specify", "break this approved spec down" |
| Run a recurring, generative gap-to-ideal loop across the whole project | [`subskills/relentless-vision-pursuit/SKILL.md`](subskills/relentless-vision-pursuit/SKILL.md) | "relentlessly improve", "run the vision pursuit" |
| Prepare, independently vet, walk through, or record genuine owner decisions | [`subskills/user-questionnaire/SKILL.md`](subskills/user-questionnaire/SKILL.md) | "prepare decisions", "collect owner signoffs" |

## Disambiguation

- Missing shape + "make this project legible" -> project-shape. Existing
  doctrine + "ready for our first spec?" -> project-direction launch gate.
- "What is wrong?" -> project-review. "What should we do about confirmed
  findings?" -> project-direction. "Keep generating moves toward the ideal"
  -> relentless-vision-pursuit.
- One proposed feature -> project-feature-request. Competing priorities or no
  proposal and a request for candidates -> project-direction.
- Questionnaire transports an already identified hard human gate; it never
  creates doctrine, specs, priorities, or implementation authority.
- Single-diff engineering review -> `/th-engineering`; user-surface design ->
  `/th-design`; tracker mechanics without direction analysis ->
  `/beads-orchestration`; AI-harness hygiene -> `/th-tooling`.
- No row fits -> answer from this router or ask one clarifying question. Do not
  load subskills speculatively.

## Shared authority and evidence

- The five-pillar vocabulary is fixed: `about/heart-and-soul`,
  `about/legends-and-lore`, `openspec/`, `about/lay-and-land`, and
  `about/craft-and-care`. A project exposes them through one local `doctrine`
  superskill, not five global entries.
- VISION is a continuous constraint through proposal, specification,
  allocation, implementation discovery, reconciliation, and milestone
  closeout. Revalidate affected mandates when the recorded baseline changes.
- Specs are planning truth. Observable behavior needs a signed-off spec delta
  before implementation; implementation without coverage is a finding.
  [`references/spec-format.md`](references/spec-format.md) is the shared format,
  and [`scripts/spec-trace-check.py`](scripts/spec-trace-check.py) is its
  mechanical gate.
- Doctrine amendments and proposed behavior require owner adoption/signoff.
  Recording observed behavior may update bookkeeping directly. A questionnaire
  records the granted decision; it never broadens it.
- A questionnaire item is not review-ready until independent review passes
  both its problem scope and recommendation against the target project's shape
  and engineering bar.
- Label major claims `[Observed]`, `[Inferred]`, or `[Unknown]`. Independent
  semantic review protects normative changes and high-severity findings;
  mechanical validation is necessary but not a substitute.
- Discover gaps, TODOs, unknowns, and adjacent ideas proactively, but do not
  expand scope silently. Route each to its earliest governing gate.
- Work graphs follow [`references/work-allocation.md`](references/work-allocation.md):
  one primary owner per cohesive, independently verifiable outcome; complete
  dispatch packets; no overlapping ownership. Direction may plan Beads work,
  but `/beads-orchestration` owns lifecycle and execution.

## Maintenance

After changing this package, run
[`scripts/validate-th-projects.sh`](scripts/validate-th-projects.sh) and the
strict skill-package audit. Keep unloaded routing cases under `evals/`; they
validate selection without adding runtime context.
