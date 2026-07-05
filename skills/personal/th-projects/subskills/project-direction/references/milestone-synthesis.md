# Milestone Synthesis: Deriving Work From Vision

Load for the vision-generative focus mode: "what should we work on next" when
no proposals, packets, or spec deltas are on hand — or after a milestone
closes. Instead of aligning *proposed* work against doctrine (the reactive
default), this mode makes doctrine *produce* the candidates.

Proposes; never sequences. Output is a milestone brief the user selects from;
selected candidates then flow through the normal machinery
(feature-request funnel for fuzzy candidates, Phase 2 changeset for concrete
ones, Phase 3 for the graph).

## Inputs

| Input | Source | Absent → |
|-------|--------|----------|
| Vision + scope mandates | `about/heart-and-soul/` (`vision.md` non-negotiables + success criteria, `v1.md` ship/defer lists) | Stop — this mode requires doctrine; recommend `../../project-shape/` bootstrap |
| Spec coverage state | `uv run <th-projects>/scripts/spec-trace-check.py <repo-root>` + `scripts/spec-scan.sh` | Treat all mandates as uncovered [Inferred] |
| Parked/rejected ideas | `about/legends-and-lore/ideas-ledger.md` | Note ledger absent; skip step 3 |
| Fresh review packet | `docs/reviews/` (see receiver protocol) | Skip packet-derived candidates |

## Procedure

1. **Extract mandates.** Convert doctrine into a capability checklist: each
   `v1.md` ship item, each success criterion, each non-negotiable that implies
   a capability. Cite file + rule number per mandate.
2. **Build the mandate coverage matrix.** For each mandate: spec coverage
   (Full / Partial / None — reuse the coverage vocabulary from
   `../../project-review/references/spec-reconciliation.md`) and
   implementation state from the scan. A mandate with no spec is spec work
   first (Core Rule 1), never a straight-to-code candidate.
3. **Scan the ideas ledger.** Any parked entry whose "what would need to
   become true" condition is now true gets unparked into the candidate pool;
   cite the condition and the evidence it's met. Rejected entries stay
   rejected unless doctrine has since been amended
   (`../../project-shape/references/doctrine-amendment.md`).
4. **Assemble candidates.** Uncovered/partial mandates + unparked ideas +
   strategic findings from a fresh packet. Every candidate carries a doctrine
   citation — a candidate that cannot cite a mandate does not enter the brief.
5. **Rank.** Score each candidate on: **proximity** (how directly it
   discharges a v1 success criterion), **leverage** (how many other mandates
   it unblocks), **tractability** (design/spec maturity — is there an RFC? a
   partial spec?). One line of evidence per score; no weighted-sum theater —
   the scores order the shortlist, the user decides.
6. **Present the milestone brief** and stop for selection.

## Milestone Brief Format

```
## Milestone candidates — {date}
Doctrine baseline: {vision.md, v1.md — commit SHA}

| # | Candidate | Mandate (citation) | Coverage | Proximity | Leverage | Tractability |
|---|-----------|--------------------|----------|-----------|----------|--------------|

Unparked from ledger: {entries + evidence conditions are met}
Deliberately excluded: {mandates deferred + why (post-v1 scope, blocked, …)}
Recommended next step per candidate: {feature-request funnel | Phase 2 changeset}
```

## Boundaries

- This mode replaces Phase 1's *inputs* (mandates come from doctrine directly,
  not from proposals) — it does not skip reconciliation: any doctrine/lore
  edits it surfaces are change-tier as usual.
- Verify-tier applies to the brief itself (one pass: does every candidate's
  citation hold?).
- No beads, no changesets, no sequencing until the user picks — then the
  chosen candidates re-enter the normal phase flow.
