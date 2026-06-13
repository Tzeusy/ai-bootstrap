# Handling Third-Party Deep-Dive Reviews

Read when the input is an external reviewer's comprehensive project review ("process this review/audit"), not one you run yourself. Goal: extract value without inheriting the reviewer's mistakes, then route planning to `/project-direction`.

## Step 1: Fact-check before synthesizing

Before accepting any external claim:
- Verify quantitative claims: line/dependency/file-size/test counts
- Verify referenced paths and named features
- Verify process claims against actual CI, docs, code
- Label each finding [Confirmed] / [Overstated] / [Incorrect] / [Unverifiable]

Only [Confirmed] findings enter the handoff packet.

## Step 2: Filter for the project's actual context

Not all best-practice advice applies equally. Explicitly deprioritize recommendations that don't fit:

| Filter | Example to deprioritize |
|--------|-------------------------|
| Single-user project | Multi-tenant scaling, contributor governance overhead |
| Solo maintainer | Formal compatibility matrices for internal APIs |
| Early-stage project | Heavy conformance harnesses before interfaces stabilize |
| Self-hosted/internal tool | SaaS-style auth hardening beyond the real threat model |

Doctrine/lore artifacts exist → use them to justify deprioritization. Absent → say the filter is inferential, not explicit.

## Step 3: Synthesize actionables by ROI

- **Tier 1 — high ROI, do soon**: structural improvements with measurable before/after evidence · test upgrades that materially change regression detection · small CI/docs fixes closing documented-vs-actual gaps.
- **Tier 2 — good practice, medium effort**: coverage + observability for critical paths · proportional security hardening · operability improvements unlocking debugging + safer releases.
- **Tier 3 — deprioritized with reason**: items filtered out by context · enterprise-scale recommendations that don't fit · strategic suggestions with no concrete first step.

## Step 4: Prepare planning inputs, not execution artifacts

For structural refactors or major risks, prepare a `/project-direction` packet:
1. Baseline evidence to preserve: public interfaces, startup/shutdown behavior, critical-path tests, current constraints
2. Logical workstream boundaries: what could split into separate epics/tasks
3. Required reconciliation gates: how to prove behavior stayed equivalent after changes

Do NOT create beads directly from `project-review`. `/project-direction` owns dependency + planning graph generation.

## Step 5: Handle episodic artifacts

The review document is transitory. After extracting actionables:
- Don't commit the review as permanent doctrine
- Genuine doctrine/design insight → update the relevant `project-shape` pillar instead
- Durable artifacts = updated shape/spec docs + the `/project-direction` handoff packet
