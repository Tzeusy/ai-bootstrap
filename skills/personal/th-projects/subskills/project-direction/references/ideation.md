# Ideation: Doctrine-Grounded Feature Brainstorming

Load for the divergent vision-generative focus mode: "brainstorm what we
could build", "what features would fit this project". Generates *new* fuzzy
candidates, where milestone synthesis derives work doctrine already implies.
Same contract as that convergent twin: proposes, never sequences or
specifies; the user triages before anything enters the machinery.

The gate difference: milestone synthesis rejects any candidate that cannot
cite a mandate. Ideation relaxes that to a **fit trace** — every candidate
must trace to a specific doctrine element (persona pain, shipped motif,
scope boundary, capability pair) — and classes its relation to doctrine:

- **Mandate-grounded** — an unstated instance of what doctrine already
  wants; cite the principle or success criterion it serves.
- **Vision-extending** — would require doctrine to grow; name the boundary
  or principle it stretches. Routes through doctrine amendment or the
  feature-request funnel's Gate 2 escalation — never straight to spec.

## Inputs

| Input | Source | Absent → |
|-------|--------|----------|
| Personas, success criteria, non-negotiables, "what this is NOT" | `about/heart-and-soul/` | Stop — this mode requires doctrine to ground against; recommend `../../project-shape/` bootstrap |
| Shipped motifs + capability inventory | `openspec/` specs (`Source:` lines, capability list); `scripts/spec-scan.sh` | Lenses 1 and 4 degrade to [Inferred] from code |
| Ideas ledger | `about/legends-and-lore/ideas-ledger.md` | Skip the ledger half of lens 5 |
| Fresh coverage matrix | Latest milestone-synthesis brief or review packet | Dedupe manually against `openspec/` |

## Procedure

1. **Extract the grounding set.** Personas and their pains, success
   criteria, non-negotiables, explicit NOT-boundaries — each with file
   citation — plus shipped motifs from spec `Source:` lines and the
   capability inventory.
2. **Run the divergence lenses.** Every lens runs; an empty lens is
   reported empty, never padded:
   - **Motif extrapolation** — each shipped motif names a recurring need.
     What other instances of that need exist that no spec covers?
   - **Persona journey walk** — walk each persona's journey end to end;
     name the steps doctrine claims to care about that nothing addresses.
   - **Boundary probe** — for each "what this is NOT" line: have the
     conditions that justified it changed? The one lens where questioning
     doctrine is the point; hits are vision-extending by definition.
   - **Capability composition** — which pairs of existing capabilities
     compose into value neither delivers alone?
   - **Adjacency transplant** — dormant ledger entries and analogous
     projects or domains as seeds. A transplant still needs a fit trace.
3. **Dedupe.** Drop candidates that are really uncovered mandates (route
   to milestone synthesis) or already parked/rejected in the ledger (cite
   the entry instead of re-proposing; rejected stays rejected unless
   doctrine has since been amended).
4. **Assemble the brief.** 5–12 candidates, quality over coverage; each
   with lens, fit trace, class, and a one-line recommended route. Carry a
   recommendation per candidate — the user reacts to concrete proposals,
   not a blank.
5. **Present and stop.** User triages each candidate:
   - **Pursue** → `../../project-feature-request/SKILL.md` funnel as fuzzy
     input; vision-extending candidates enter knowing Gate 2 requires
     doctrine amendment or rejection.
   - **Park** → decision-record contract as usual: RFC stub + ledger line
     in the same change
     (`../../project-feature-request/references/decision-record-template.md`).
   - **Discard** → dropped without ceremony; no record, no ledger line.

## Ideation Brief Format

```
## Ideation brief — {date}
Doctrine baseline: {vision.md et al — commit SHA}
Grounding set: {N personas, N motifs, N boundaries, N capabilities}

| # | Candidate | Lens | Fit trace (citation) | Class | Recommended route |
|---|-----------|------|----------------------|-------|-------------------|

Empty lenses: {lens — why nothing surfaced}
Near-misses routed elsewhere: {uncovered mandates → milestone synthesis;
ledger duplicates → cited entry}
```

## Boundaries

- Proposes fuzzy candidates only — no specs, no changesets, no beads, no
  sequencing. A pursued candidate enters the feature-request funnel exactly
  as a human-originated fuzzy request would.
- Coverage gaps are milestone synthesis's job; a candidate that merely
  discharges an existing mandate is a near-miss routed there, not brief
  filler.
- Vision-extending candidates never reach specification without doctrine
  amendment (`../../project-shape/references/doctrine-amendment.md`) or
  explicit Gate 2 escalation.
- No untraceable candidates: an idea with no persona, motif, boundary, or
  composition trace does not enter the brief — grounded divergence, not
  blue-sky.
- Verify-tier applies to the brief itself (one pass: does every fit trace
  hold, is every class label honest?). Parks follow the ledger maintenance
  contract.
