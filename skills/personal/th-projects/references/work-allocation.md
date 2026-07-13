# Work Allocation Contract

Load when turning an approved spec, confirmed gap set, or milestone into beads
and agent assignments. The objective is reliable ownership with minimum context,
worktree, CI, and review overhead.

## Unit of Work

Default to **one bead per cohesive, independently verifiable outcome**, with one
accountable primary agent. A requirement, scenario, file, TODO, or review
finding is evidence for a bead; it is not automatically a bead boundary.

A bead is correctly sized when one worker can:

- understand its spec slice without loading unrelated project context;
- implement, test, review, and roll back the outcome independently;
- own a bounded file/interface surface without another bead making the same
  decisions; and
- finish in one focused agent session, usually several hours rather than a few
  mechanical minutes.

## Merge or Split

**Merge** candidate tasks when they share setup, the same module or interface,
fixtures, migration, quality gate, or review surface. Merge whenever repeated
context loading, worktree setup, CI, and review overhead is material compared
with the implementation. Keep distinct acceptance criteria inside the bead.

**Split** only when each outcome can land, test, review, and roll back without
the other; separate owners reduce cognitive load or unlock safe parallelism;
or one outcome has a different hard dependency, risk class, or sign-off gate.

Never split by file, layer, requirement, scenario, TODO, or subagent specialty
alone. Never merge unrelated outcomes merely to fill a worker session.

## Ownership and Dependencies

- Give each bead one accountable primary agent. Specialists advise that owner;
  they do not create overlapping implementation ownership.
- Map every in-scope `v1-mandatory` requirement to at least one implementation
  bead and one verification path. One bead may cover several adjacent
  requirements when the implementation seam is shared.
- Serialize beads that touch the same contract, migration, fixture, config, or
  architecture decision. Parallelize only disjoint surfaces with stable inputs.
- Put requirement-level reconciliation inside the implementation bead's
  acceptance criteria. Add one epic-level reconciliation bead only for
  cross-child and end-to-end behavior; do not create a reconciliation bead per
  implementation bead.

## Discovery Triage

Classify every gap, TODO, unknown, or expanded idea before assigning work:

| Discovery | Required route |
|---|---|
| Current-spec correction; no behavior change | Amend the governing spec/task notes, then continue. |
| Boundary, contract, topology, or user-experience change | Return to the earliest affected feature-request gate; resume only after the delta converges and is signed off. |
| Evidence unknown | Create a bounded investigation outcome with evidence target, owner, blocking status, and exit criterion. |
| New behavior or adjacent idea | Capture durably in the ideas ledger or a separate spec-first bead; do not expand the active bead silently. |
| Local debt required to meet current acceptance | Keep inside the active bead when cohesive; otherwise create a linked blocker using this allocation contract. |

Do not leave actionable TODO comments as the only record. Do not create a bead
for every discovered line item before doctrine, spec, and cohesion triage.

## Handoff Check

Before materializing the graph, verify:

1. Every bead cites VISION/doctrine, exact spec requirements, and observable
   acceptance criteria.
2. No two beads own the same implementation decision or review surface.
3. No bead is mostly setup, context loading, or duplicated verification.
4. Mandatory requirement coverage is complete; deferred/new ideas are explicit
   and cannot masquerade as completion.
5. The graph ends with one cross-child reconciliation/closeout path and a next-
   milestone callback when doctrine mandates remain uncovered.
