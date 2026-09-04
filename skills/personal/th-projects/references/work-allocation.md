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

Run a **cohesion scan** across proposed, ready, and recently completed work
before materializing or dispatching the graph. The cohesion threshold is two or more shared signals; treat those candidates as one bundle or serialize them:

- primary module, interface, or state machine;
- focused tests, fixtures, or failure-injection harness;
- migration, checkpoint, config, or persisted contract;
- expected PR and reviewer decision surface; or
- individually micro-sized implementation whose setup/CI/review cost rivals
  the change itself.

Override that threshold only when the outcomes have independent rollback and
verification paths **and** a different dependency, risk class, or sign-off
gate. Record the reason. Large diffs are not automatically over-sized: keep a
single protocol, vertical user outcome, or exhaustive sweep cohesive when
splitting would create an unstable intermediate contract.

For tightened required contracts spanning stored data, producers, retries, or
consumers, prefer the additive sequence **representation → propagation → enforcement**:

1. **representation** — add the optional persisted/wire shape and compatibility;
2. **propagation** — update every producer, replay, deferred, and round-trip
   path while the field remains optional; then
3. **enforcement** — activate fail-closed requirements only after propagation
   coverage is proven.

Each phase may be a bead when it has an independent rollback and verification
story. Do not split merely by frontend/backend or language.

## Dispatch Readiness Packet

Do not dispatch an implementation bead until its structured fields make these
items explicit. Use `description`, `design`, and `acceptance_criteria`; prose
hidden in creator-session context does not count.

- **Outcome and non-goals** — observable result plus explicit exclusions.
- **Governing intent** — doctrine/VISION mandate, exact spec requirement, and
  baseline commit when the project uses them.
- **Surface map** — owned modules/interfaces plus trust boundaries, schemas,
  runtimes, persistence/deferred paths, and callers affected.
- **Behavior matrix** — happy path and relevant failure, concurrency,
  idempotence, retry/replay, compatibility, and rollback semantics. Omit an
  axis only when demonstrably irrelevant.
- **Documentation impact** — docs/spec/RFC updates required in this change, or
  an explicit "none" with reason.
- **Verification** — named behavior-executing checks at the real seam; for
  each invariant exactly one gate species (behavior test, source-scan guard,
  or type/lint rule); the nearest existing test to extend; and the expected
  net test delta. "Add tests for X" without a named seam is not a packet.

An empty structured `acceptance_criteria` field is not dispatch-ready even when
the description contains an informal checklist.

Use two distinct states:

- **packet-complete** — the structured packet above is semantically complete;
- **runnable-now** — packet-complete, dependencies clear, no ownership overlap,
  required sign-off present, and an appropriate worker/reviewer lane available.

Only runnable-now work dispatches. A blocked bead can be packet-complete without
being runnable-now.

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

Before creating a discovery bead, search open and recently closed beads, active
PRs/branches, and concrete symbols/files. Link provenance to an existing item
or close as duplicate when the outcome already exists.

Apply a **two-correction checkpoint** after two substantive review reopenings:

- Same seam or invariant: retain the active bead/PR, rewrite its behavior
  matrix and acceptance criteria, then continue with the current owner.
- New subsystem, trust boundary, security decision, architecture prerequisite,
  or risk class: split a linked prerequisite blocker and return to the earliest
  affected spec/design gate before resuming.
- Reviewer-authored semantic correction: require a fresh independent reviewer
  on the resulting exact head. Otherwise prefer the same independent reviewer
  for recheck so context is reused.

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
6. Every implementation bead has a complete Dispatch Readiness Packet, and the
   cohesion scan found no duplicate or overhead-dominated boundary.
7. No requirement is pinned by two gate species, no bead exists only to add
   tests for behavior an existing test executes, and no epic exceeds 7
   children without a recorded override.
