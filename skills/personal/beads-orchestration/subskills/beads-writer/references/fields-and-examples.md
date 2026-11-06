# Beads Field Reference and Examples

Use current `bd <command> --help` for version-sensitive flags. These examples
show field selection, not authority to mutate a different project's backlog.

## Fields

| Field | Purpose |
|---|---|
| `title` | Specific imperative summary of observable work. |
| `issue_type` / `--type` | Actual work: task, bug, feature, chore, epic, or supported local type. |
| `priority` / `--priority` | Numeric 0–4; 0 is a genuine emergency, 2 is the ordinary default. |
| `description` | Current outcome, non-goals, why, and governing references. |
| `design` | Current source surface, relevant boundaries, sequencing/rollback, packet reference. |
| `acceptance_criteria` / `--acceptance` | Observable criteria owned by this member; include the needed behavior proof. |
| `notes` | Current status/recovery receipt and links to historical evidence; avoid a duplicate packet. |
| `parent` | Accepted outcome or epic when hierarchy helps. Hierarchy is not delivery packaging. |
| dependencies | Real blockers wired with `bd dep add <dependent> <prerequisite>`. |
| `spec_id` | Exact governing specification locator where supported. |
| `external_ref` | Globally unique canonical external association; a package PR belongs only to its anchor. |
| `metadata` | Delivery metadata defined by the shared delivery model; preserve unrelated keys. |

Do not preassign execution claims while merely authoring the plan. The owner
claims actual runnable scope under the execution contract.

## A Current Correction Packet

```bash
bd create --title "Preserve adapter failure signals across retry" --type bug -p 1 \
  --description "Preserve the accepted terminal-error behavior in the adapter retry path. Governing contract: docs/runtime.md#terminal-errors. No new provider or retry policy." \
  --design "Owned seam: runtime adapter response classification and retry caller. Extend the existing failover signal tests. Existing related zero-server and stderr corrections can share a delivery package if their source/review/rollback surface remains cohesive." \
  --acceptance "Terminal provider failure is surfaced once, retriable failures retain the existing retry behavior, and successful responses remain unchanged. Execute the relevant existing adapter failover cases plus regressions for each corrected path; update the runtime contract if its description was incorrect." \
  --labels complexity:medium --json
```

A fresh owner can follow the exact contract and source seams without the
creation chat. If its packet references an immutable historical artifact, name
that artifact and section; do not inline every discarded protocol alternative.
The writer identifies possible cohesion; the execution owner verifies membership,
claims, authority, and actual branch state before combining delivery.

## Accepted Outcome and Partial Source Delivery

An outcome such as “the owner can recover the service using a verified backup”
retains its mandatory restore/runtime proof. A foundation member may separately
accept “backup format and write path are implemented and seam tests pass.”
Merging that member does not close the accepted recovery outcome. Record the
remaining restore proof on the original outcome, with its actual gate/owner.
Do not create a residual recovery epic merely because the first slice merged.

An optional reporting bead can reuse the same finite closeout checklist. Its
acceptance is to record truthful complete/partial/missing evidence and remaining
criteria, not to declare the parent delivered regardless of proof. See
[`reconciliation-beads.md`](reconciliation-beads.md).

## Shared Prerequisites

Create or reuse one canonical shared-contract prerequisite, then link actual
dependents. For example:

```bash
bd dep add <feature-member> <shared-runtime-prerequisite>
```

Different features do not independently implement that runtime on their own
epic branches. Required adoption or owner-held activation remains a real gate;
other independently safe accepted scope can proceed.

## Labels

Reuse the project's taxonomy. Existing orchestration labels include:

- `complexity:low|medium|high|epic` for honest model-tier input;
- `no-dispatch` for tracking/meta records;
- `scope:local-state` for owner-named work in gitignored main-checkout state;
- `needs-shaping` when current scope is not executable;
- `reconciliation` for separately justified finite closeout work, not every PR.

PR/review labels and package metadata are maintained by execution consumers.
Do not stamp the same `gh-pr:N` external ref onto package members or review
beads; the unique canonical association stays on the implementation anchor.
