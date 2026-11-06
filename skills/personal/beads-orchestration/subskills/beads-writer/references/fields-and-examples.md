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
| `spec_id` | Exact governing specification locator when applicable; routine fixes may instead cite their governing request or behavior evidence. |
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

## Proportional Decision Walkthroughs

These examples apply the shared
[`Governing Contract`](../../../../th-projects/references/work-allocation.md#governing-contract)
rule to actual authoring choices. Read the target source and repository rules
before making the stated determination; examples do not authorize live changes.

**Broken alias.** The owner requests repair of `gs`; its definition invokes
`git statsu`, and the shell reports that this subcommand does not exist. The
owned surface is that alias, the expected result is ordinary `git status`, and
verification is shell syntax plus resolving/invoking the alias in a disposable
repository. The request, source, and reproduction give a clear packet without
a new formal spec. This repair grants no authority to change other aliases or
run destructive Git operations.

**Documentation typo.** The owner requests correction of “instalation” in an
existing installation guide. Inspect its context and docs rules, correct the
word, and verify the rendered/text diff and any required docs checks. The
request and local acceptance establish scope; no specification lifecycle or
new behavior test is needed. If the purported typo would change an operational
instruction rather than spelling, resolve that meaning before changing it.

**Reproduced regression.** An authorized bug-fix request says a filename with
spaces used to round-trip through an export/import helper. Reproduce the loss,
read the affected helper/callers and any existing contract, then define acceptance
as preserving the complete filename while existing ordinary-name behavior still
passes. Own that helper seam and extend its nearest suitable round-trip test.
The reproduced regression and established behavior suffice if repository rules
do not require more. A report alone does not justify redesigning the export
format or changing access checks; such a discovery returns to its real gate.

**New shared trust protocol.** A request proposes that several services exchange
new delegation tokens across a trust boundary. Existing code and a failing test
do not settle who may delegate which authority. Capture the proposed outcome,
owned interfaces, unresolved authority/replay/revocation decisions, and their
applicable architecture/specification/approval gate. Do not dispatch dependent
implementation as a routine bug fix or infer security authority from a request
to make it work. After the governing contract is adopted and required sign-off
exists, give the implementation owner a current bounded packet and seam checks.

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
