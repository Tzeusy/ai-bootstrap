---
name: th-projects
description: >
  Use for project-level engineering governance in any repository — bootstrap
  or audit the knowledge architecture (doctrine, specs, topology,
  standards), concretize a feature request into a spec delta, amend a spec
  found wrong mid-implementation, reconcile specs against implementation,
  run a repo-wide health audit, or decide what to work on next via
  spec-driven planning, milestone synthesis, and doctrine-grounded feature
  ideation. Route to exactly one subskill per task. Triggers: "project
  shape", "bootstrap docs", "what should we work on next", "should we build
  this", "I want to add X", "spec this feature", "the spec is wrong",
  "break this down", "review this project", "audit the codebase", "does the
  code match the spec", "what's the next milestone", "brainstorm features".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-07-26"
compatibility: Subskill scripts require bash, git, grep, find. project-direction additionally assumes the bd (beads) CLI and an OpenSpec-capable environment for changeset synthesis.
---

# TH Projects

Superskill router for spec-driven project governance. Four subskills under
`subskills/`; each a complete standard package (own `SKILL.md`, `references/`,
`scripts/`). Subskills **not** in global catalog — discover lazily here, load
**at most one** subskill body per task. A subskill may route you to a sibling
(e.g. project-review runs project-shape's scanner); follow that link from the
subskill, not here.

Four subskills, one lifecycle:

1. **Shape** — set normative baseline: what project believes, how designed,
   what must be built, where things live, engineering bar for changing it.
2. **Feature request** — run one concrete proposal through idea funnel against
   baseline → signed-off spec delta.
3. **Review** — audit implementation vs baseline + generic health criteria
   (incl. exhaustive spec↔code reconciliation) → confirmed findings.
4. **Direction** — baseline + spec deltas + findings → prioritized, spec-linked
   work plan; hand execution to beads.

VISION is a **continuous constraint**, not a one-time gate: proposal, spec,
allocation, implementation discovery, reconciliation, and milestone closeout
must still serve cited doctrine. Implementation discoveries re-enter at the
earliest affected feature-request gate; milestone closeout returns uncovered
mandates to direction's **milestone synthesis**. The lifecycle stops only at a
hard human gate or when the approved spec is achieved and verified.

## Discover subskills

```bash
PKG="$(dirname "$SKILL_PATH")"
find "$PKG/subskills" -maxdepth 2 -name SKILL.md
rg -n "^name:|^description:" "$PKG"/subskills/*/SKILL.md
```

## Routing table

| Task intent | Subskill | Typical trigger |
|---|---|---|
| Bootstrap or audit the project's knowledge architecture (five pillars: heart-and-soul, legends-and-lore, openspec, lay-and-land, craft-and-care); decide where an idea should be documented; generate a layman overview. | [subskills/project-shape/SKILL.md](subskills/project-shape/SKILL.md) | "set up project structure", "bootstrap docs", "where should this go", "audit documentation health" |
| Concretize ONE fuzzy feature/project request into a signed-off spec delta: motif, doctrine gate, topology placement, design sketch, WHEN/THEN scenarios. Also amendment mode: fix a spec found wrong/ambiguous mid-implementation. | [subskills/project-feature-request/SKILL.md](subskills/project-feature-request/SKILL.md) | "I want to add X", "spec this feature", "turn this idea into requirements", "what would it take to build X", "the spec is wrong" |
| Decide what to work on next; evaluate competing priorities; check roadmap alignment; turn approved specs into a prioritized beads work plan. Also the vision-generative modes when nothing is proposed: milestone synthesis (derive work doctrine already implies) and ideation (brainstorm new feature candidates grounded in doctrine). | [subskills/project-direction/SKILL.md](subskills/project-direction/SKILL.md) | "what's highest leverage", "what should we work on next", "break this down", "is this roadmap aligned", "what's the next milestone", "brainstorm features for this project" |
| Repo-wide health audit: code quality, reliability, security, docs, maintainability — scored, evidence-based, with a planning handoff packet. Includes the exhaustive spec-reconciliation mode (bidirectional spec↔code gap audit + remediation). | [subskills/project-review/SKILL.md](subskills/project-review/SKILL.md) | "review this project", "audit the codebase", "assess project health", "reconcile spec vs implementation", "what's implemented but undocumented" |

## Routing rules

- **Baseline before judgment**: review and direction both consume the shape
  baseline. No shape artifacts at all + real ask is "make this project legible"
  → project-shape, even if user said "review".
- **Audit vs. plan**: review *classifies* (scores, risks, confirmed findings);
  direction *decides* (sequencing, specs, beads). "What's wrong with this repo"
  → review. "What to do about it / next" → direction. Full review hands off to
  direction inside the subskills.
- **Feature vs. direction**: one concrete proposal → feature-request; many
  competing priorities or "what next" → direction; no proposal at all and the
  ask is to *invent* candidates → direction (ideation), whose pursued picks
  feed the funnel. A feature request surviving its funnel hands its spec delta
  to direction for sequencing.
- **Scope guard**: single-PR/diff review → `/code-review`, not here.
  Change-level engineering-quality judgment (engineering bar, readability, test
  rigor, dependency hygiene, cruft cleanup, skill reviews, diagrams) →
  `/th-engineering` (project-shape's craft-and-care adopts that bar by
  reference). Backlog mechanics without direction analysis →
  `/beads-orchestration` (beads-writer). AI-tooling harness hygiene (installed
  skills, dotfiles, snapshot state) → `/th-tooling`.
- **Design and engineering bars**: user-facing behavior or interaction contracts
  → `/th-design`; implementation quality, tests, dependencies, diagnosis, docs,
  or diagrams → `/th-engineering`. Load the router only when the concern exists,
  then its one relevant subskill; carry conclusions into the spec or bead rather
  than copying whole skill bodies.
- **Fallback**: project-adjacent but no row fits → answer from router context or
  ask. Do not load a subskill to browse.

## Shared invariants (all subskills)

- Five-pillar shape model (`about/heart-and-soul`, `about/legends-and-lore`,
  `openspec/`, `about/lay-and-land`, `about/craft-and-care`) is the single
  normative vocabulary; subskills must not redefine it.
- Specs are source of truth for work planning; implementation without spec
  coverage is a finding, not a baseline. The OpenSpec file format subskills
  read/write is one shared contract,
  [`references/spec-format.md`](references/spec-format.md) at package root, not
  owned by any single subskill. Its mechanical validator,
  [`scripts/spec-trace-check.py`](scripts/spec-trace-check.py), runs before any
  subagent spends tokens on semantic spec review.
- Per-change spec sync: an implementation task that changes observable behavior
  amends its governing spec in the same task (feature-request amendment mode).
  Episodic reconciliation is the backstop, never the mechanism.
- VISION/doctrine remains binding after sign-off. Record the baseline commit in
  spec handoffs; if it changed, revalidate affected mandates before allocation
  or resumption.
- Gap, TODO, unknown, and adjacent idea discovery is proactive but never silent
  scope expansion. Classify it as current-spec correction, boundary/design
  change, evidence unknown, new scope, or local debt; route to the earliest
  governing gate and record it durably.
- Work graphs follow
  [`references/work-allocation.md`](references/work-allocation.md): one bead and
  primary agent per cohesive independently verifiable outcome, with enough work
  to amortize context/worktree/CI/review overhead and no overlapping ownership.
- Autonomy contract — what agents may do without the human:

  | Artifact | Agent may | Human must |
  |---|---|---|
  | Doctrine (`about/heart-and-soul/`) | draft, review, blast-radius sweep | adopt every amendment |
  | Spec delta (proposed behavior) | draft + reconcile changeset | sign off before implementation |
  | Main-spec bookkeeping of [Observed] behavior | edit directly | — |
  | Beads/planning graph | generate from approved changeset | approve the changeset it derives from |

- Every major claim cites evidence, labeled [Observed], [Inferred], or
  [Unknown].
- Subskills cross-reference by relative path (`../project-shape/…`) inside this
  package; those paths are package-internal and stable.

## Package maintenance

After changing any subskill, script, or fixture in this package, run
[`scripts/validate-th-projects.sh`](scripts/validate-th-projects.sh) — shell
syntax, project-shape self-tests, fixture invariants, and the spec-trace
fixtures — and fix every FAIL before committing.
