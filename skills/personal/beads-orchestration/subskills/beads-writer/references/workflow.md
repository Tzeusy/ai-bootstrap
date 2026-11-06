# Beads Writer Workflow

## Understand and Reuse

Inspect the target repository's instructions and the affected source. Take
scope, priority, and authority from the owner and applicable governing contract; ask only for
material information those sources cannot supply. Search open and recently
closed beads, active PRs, and concrete symbols/files before creating work.
Attach provenance to existing outcomes instead of duplicating symptom beads.

Apply the shared
[`work-allocation contract`](../../../../th-projects/references/work-allocation.md)
for proportional governing contracts, accepted outcomes, cohesion, semantic
readiness, and current packet shape. Use its Governing Contract section to
decide whether existing evidence suffices or a formal spec/approval is required.
The execution representation is defined by the
[`delivery model`](../../../references/delivery-model.md).

## Choose Tracking and Delivery Boundaries

| Situation | Action |
|---|---|
| One cohesive outcome with no existing tracking | Write one bead. |
| Several related corrections already have beads | Retain their criteria and propose one delivery package under an existing anchor. |
| Independent outcomes or different hard gates/rollback paths | Keep separate packages and clear ownership. |
| Shared prerequisite used by competing features | Link one canonical prerequisite and owner; do not clone implementation scope. |
| A foundation or dark slice can land before activation | Track the slice truthfully and retain the larger accepted outcome as partial. |

A file, layer, scenario, or review specialty is not automatically a boundary.
Compare module/interface, fixtures, migration/config, and review surface for
cohesion. Split when doing so reduces actual implementation/review risk or
provides independent safe landing, not to hit a child-count quota. There is
no required milestone hierarchy. Existing related beads can share a delivery
cycle without being rewritten or replaced by a new umbrella bead.

Use dependencies for real prerequisites. Record preferred package order and
context locality as guidance; do not manufacture blockers solely to steer a
queue. For cross-cutting persisted contracts, consider representation →
propagation → enforcement when each state is safe to land and roll back.

## Write the Current Packet

Use [`fields-and-examples.md`](fields-and-examples.md) for field selection.
Keep one operative packet with the current outcome, exclusions, source surface,
relevant failure behavior, documentation impact, named seam checks, actual
prerequisites, and exact governing references. Fill `acceptance_criteria` with
observable member acceptance; a description-only checklist is insufficient.

Cold-start self-containment means a fresh owner can resolve the current
instructions and authority. Link the governing request or behavior evidence,
applicable spec sections, and relevant immutable historical artifacts. Do not inline the archive, repeat full contracts in every member,
or preserve superseded alternatives as competing current instructions.

For work that changes product or architectural contracts, distinguish approved
direction from adopted behavior and executable scope. For a newly changing shared
architectural contract, record the settled interface and a
focused source feasibility check once before releasing its dependents. Stable
existing contracts need no new review ritual. `packet-complete` describes
unambiguous current scope; `runnable-now` also requires real dependencies,
ownership, and sign-off to permit execution. Mechanical lint alone proves
neither semantic readiness nor authority.

## Preserve the Accepted Outcome

Keep the original outcome and mandatory acceptance visible until completion or
an authorized scope amendment. Foundation merges and dark implementations can
close their own member acceptance; they do not prove user-facing activation or
runtime acceptance. Record remaining criteria on the same outcome rather than
creating a new residual programme after each slice.

When cross-child/end-to-end proof is needed, use one finite closeout path under
[`reconciliation-beads.md`](reconciliation-beads.md). An outcome checklist or
existing report may serve; do not add a new bead when the existing path suffices.
Routine correctness repairs stay with the active owner/package/PR. Route only
actual new scope or governing-boundary changes out through their real gate.

## Create and Verify

Use `bd` in the target repository. Preserve existing foreign claims. Create
parents and genuinely new prerequisites first, capture returned IDs, then
wire dependencies explicitly with `bd dep add`. Use `bd create` with real
descriptions instead of title-only quick capture for executable work.

Read back the created or amended records, check graph acyclicity and actual
ready state, and run `bd lint` where supported. Verify accepted requirement
coverage, no duplicate ownership, and current packet references against the
source. Tracker failure stops writes; diagnose it through known-error guidance
without destructive tracker repair. Follow the target repository's own Beads
persistence/session-close process.

Report IDs, titles, priorities, proposed package boundaries, real waits, and
the next completion proof. Authoring hands allocation to an outcome owner
(looper) or coordinator; it does not launch execution.
