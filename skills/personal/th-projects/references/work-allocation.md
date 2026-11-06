# Work Allocation Contract

Load when turning an owner request, reproduced defect, approved spec, confirmed
gap set, or milestone into beads and assignments. Allocate finite accepted owner
outcomes, then choose coherent delivery boundaries. Execution, branch, ownership, recovery, and evidence rules
live in the shared
[`Beads delivery model`](../../beads-orchestration/references/delivery-model.md).
This contract shapes its inputs; it does not add another execution preflight.

## Governing Contract

Use the smallest clear contract that establishes the authorized outcome. Within
an authorized fix or maintenance request, a precise owner instruction, a
reproduced regression, or settled existing behavior can govern a routine bug,
configuration, documentation, or maintenance change. Record the intended
observable result, owned surface, relevant constraints, and verification
proportional to the change. A broken alias or documentation typo does not need
a newly authored formal specification merely because none already exists.

Inspect the actual source and repository instructions before calling the
behavior settled; an old test or current implementation can itself be wrong.
Where an existing governing spec applies, follow it or resolve its contradiction
rather than silently substituting the observed behavior. A bug report describes
a problem; it does not grant authority for new product behavior, a shared
architecture decision, a trust change, deployment, or a broader scope amendment.

New or unresolved product behavior, shared architectural contracts, trust
boundaries, and authorization decisions follow their applicable shaping and
approval gates. A repository-mandated formal spec or sign-off remains required.
Route only that unresolved or gated work through its real boundary; absence of
a formal spec alone does not send a clear routine fix through the full planning
lifecycle. This is how the current packet is grounded, not another per-task
preflight or an alternative execution mode.

## Accepted Outcome, Tracking, and Delivery

Record the observable owner outcome, mandatory acceptance, activation or runtime
proof where required, and explicit exclusions on the existing outcome record.
Keep that accepted baseline visible until completed or explicitly amended by its
authority. A backend foundation, adopted specification, or dark implementation
may satisfy a member's acceptance while the accepted feature remains partial.
Do not close the feature and replace its remaining acceptance with a new
reconciliation hierarchy. Deliberate deferral names what was removed, why,
and who authorized the scope amendment.

Default to one bead per cohesive, independently verifiable outcome. A file,
scenario, review finding, or layer is not automatically a tracking boundary.
Tracking and delivery granularity can differ: several existing related beads
may share one delivery package, accountable implementation owner, branch, PR,
and independent review. Preserve each member's acceptance and closure state;
no new umbrella bead is needed just to batch existing work.

Use the existing anchor/member representation from the delivery model. Only
its anchor owns the canonical PR association and review relation. Independent
outcomes retain separate ownership and rollback paths. Do not combine unrelated
work merely to fill a package or session.

## Cohesion and Boundaries

Compare proposed work with open and recently closed beads, active PRs, and the
actual source. Bundle related corrections when shared modules/interfaces,
fixtures, migration/config, or review surface make one delivery cycle coherent.
Serialize overlapping implementation decisions under one owner. Similar names
or a common epic alone do not establish cohesion.

Split a delivery boundary when independent rollback, a different hard gate or
risk class, unstable shared inputs, or review complexity requires it. Do not
split only to satisfy child-count or line-count targets. Conversely, a large
diff is not proof that an entire programme belongs in one PR. Size packages so
an independent reviewer can judge the complete change and the owner can land
useful work without waiting for an optional tail.

Prefer additive **representation → propagation → enforcement** when tightening
stored or wire contracts across producers, retries, deferred paths, and
consumers. These can be separate packages when intermediate states are safe.
Keep one package when splitting would create an invalid intermediate protocol.
The default remains frequent integration to main; bounded integration branches
are chosen under the delivery model and the target repository's policies.

## Current Operative Packet

Give the owner one concise current packet. Put the outcome and exclusions in
`description`, current implementation decisions and references in `design`,
and member-level observable acceptance in `acceptance_criteria`. The package
packet identifies its members and the current shared work; members retain their
own criteria without repeating the whole package or programme archive.

A cold reader needs unambiguous authority and current instructions, including:

- the accepted outcome and its governing request, reproduction/existing-behavior
  evidence, or exact formal spec sections/decisions as applicable;
- the owned modules/interfaces and any relevant trust, persistence, caller,
  compatibility, sequencing, and rollback boundaries;
- relevant happy-path and failure behavior, including concurrency, idempotence,
  and retry/replay when the change touches them;
- documentation impact and named verification at the actual behavior seam,
  extending the nearest suitable tests under the existing test-growth policy;
- dependencies, required authorization, and the next concrete completion proof.

Link authoritative documents and immutable history rather than copying full
before/after contracts, superseded alternatives, hash inventories, or transcripts.
Rewrite an active stale packet in place, preserving its references and accepted
intent. Leave closed history alone. There is no arbitrary packet-size cap.
An acceptance checklist hidden only in `description` does not replace the
structured `acceptance_criteria` field.

## Semantic Readiness

Distinguish approved direction, adopted behavior, packet-complete scope, and
runnable-now implementation. Approval of a programme is not adoption of every
proposed interface and is not proof that every child can execute now.

For a new or changed shared architectural contract, settle its authoritative
interface and check its source assumptions with a focused feasibility walk before releasing
its dependents. Record the result once at that contract; do not repeat it for
every child. Existing stable contracts need no new ceremony. A packet is
complete when its current scope and acceptance are unambiguous and source-grounded.
It is runnable-now only when actual prerequisites, ownership, and required
sign-off permit work. `bd lint` verifies structure, not these semantic facts.

A hard gate blocks only the work that requires it. Other accepted runnable
scope can proceed when it has an independent safe landing and rollback story.
Owner-held authority remains owner-held; do not silently reinterpret a dependency
to manufacture ready work.

## Ownership and Scheduling Inputs

One accountable implementation owner retains a bounded accepted outcome through
implementation, diagnosis, ordinary test/review repairs, and landing or explicit
handoff. Specialists advise that owner; they do not independently implement the
same contract. A shared runtime prerequisite has one canonical owner/package
with downstream dependents, rather than a copy on each epic branch.

Map mandatory requirements to member acceptance and a verification path. Order
work by actual prerequisites and context locality, and record the next useful
landing point. Dependencies represent real gates, not artificial sequencing to
force a queue order. A second session requires a separate coherent outcome and
non-overlapping inputs; capacity alone does not justify opening another epic.
Distinguish runnable prerequisites, technical waits, and genuine owner holds.

Keep requirement-level reconciliation in member acceptance. Use one finite
cross-child/end-to-end closeout path where the outcome needs it: the outcome
record's checklist, an existing report, or one closeout bead. Reuse that path
when gaps remain; neither every slice nor every review correction needs a new
tracking record or generation of reconciliation.

## Discovery and Correction Triage

| Discovery | Route |
|---|---|
| Ordinary implementation, test, or review repair within accepted scope | Existing owner fixes it in the same package/PR. |
| Current-spec correction with no behavior change | Amend the relevant current notes/spec, then continue. |
| Changed scope, architecture, trust, or authorization | Return to the actual governing boundary; resume affected work after its decision. |
| Evidence unknown that prevents implementation | Bounded investigation with an evidence target, owner, and exit condition. |
| New behavior or adjacent idea | Capture separately after deduplication; do not expand accepted scope silently. |
| Local debt required for current acceptance | Keep it with the current owner when cohesive; otherwise link the real prerequisite. |

Search existing work and concrete symbols before materializing a discovery.
Do not make every TODO or finding a bead. Repeated substantive corrections on
the same invariant are a reason to refresh its behavior matrix in place with
the same owner and independent reviewer. A new trust/subsystem/risk boundary
follows its governing gate. Reviewer-authored semantic fixes require fresh
independent review; ordinary author corrections normally retain the reviewer.

## Handoff Check

Before handing off the allocation, confirm that accepted scope remains finite,
mandatory coverage and governing/source references are explicit, and no two
owners make the same implementation decision. Identify coherent packages among existing
beads without duplicating tracking. Confirm current packets distinguish planning,
partial source delivery, activation, and runtime acceptance. Name genuine waits
and the next useful landing or completion proof. Reuse current evidence according
to what it proves; worker replacement or a coordinator wake alone changes none
of these facts.
