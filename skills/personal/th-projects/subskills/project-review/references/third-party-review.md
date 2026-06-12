# Handling Third-Party Deep-Dive Reviews

Read this when the input is an external reviewer's comprehensive project review
("process this review/audit") rather than a review you run yourself. The goal is
to extract value without inheriting the external reviewer's mistakes, then route
execution planning to `/project-direction`.

## Step 1: Fact-check before synthesizing

Before accepting any external claim:
- Verify quantitative claims: line counts, dependency counts, file sizes, test counts
- Verify referenced paths and named features
- Verify process claims against actual CI, docs, and code
- Label each finding: [Confirmed], [Overstated], [Incorrect], or [Unverifiable]

Only [Confirmed] findings enter the planning handoff packet.

## Step 2: Filter for the project's actual context

Not all best-practice advice applies equally. Explicitly deprioritize recommendations that do not fit the project:

| Filter | Example of what to deprioritize |
|--------|---------------------------------|
| Single-user project | Multi-tenant scaling, contributor governance overhead |
| Solo maintainer | Formal compatibility matrices for internal APIs |
| Early-stage project | Heavy conformance harnesses before interfaces stabilize |
| Self-hosted/internal tool | SaaS-style auth hardening beyond the real threat model |

If doctrine or lore artifacts exist, use them to justify deprioritization. If they do not exist, say that the filter is inferential rather than explicit.

## Step 3: Synthesize actionables by ROI

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

## Step 4: Prepare planning inputs, not execution artifacts

For structural refactors or major risks identified by the review, prepare a packet for `/project-direction` that includes:
1. Baseline evidence to preserve: public interfaces, startup/shutdown behavior, critical-path tests, current constraints
2. Logical workstream boundaries: what could be split into separate epics/tasks
3. Required reconciliation gates: how to prove behavior stayed equivalent after changes

Do not create beads directly from `project-review`. `project-direction` owns the dependency graph and planning graph generation.

## Step 5: Handle episodic artifacts

The review document itself is transitory. After extracting actionables:
- Do not commit the review as permanent doctrine
- If the review surfaces genuine doctrine or design insight, update the relevant `project-shape` pillar instead
- Keep the durable artifacts as updated shape/spec docs plus the `/project-direction` handoff packet
