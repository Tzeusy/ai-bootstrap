# Flow B — Spec Ahead of Code

Input: `spec-ahead`, `divergent`, and `unknown` rows, flow A's defect rows,
and the ledger. Output: a coverage matrix in which every in-scope requirement
ID has exactly one owner, and a backlog that holds all the work to close the
gap — with nothing filed twice and no other owner's work disturbed.

The failure this flow prevents: re-filing what the backlog already holds,
planning only the obvious half, rewriting someone else's packet, or leaving
the gap as a report nobody owns.

## 1. Divergence decision (per divergent row)

Spec is the source of truth (router invariant). Default: the code is wrong;
the row becomes `spec-ahead` (a defect against a requirement).

The spec may be wrong only on named evidence — one of:

- doctrine, an RFC, or a recorded decision supports the code's behavior over
  the spec's;
- the spec is internally inconsistent or unimplementable as written;
- an owner decision (bead notes, decision record) changed the intent and the
  spec never absorbed it;
- a verified external consumer depends on the code's behavior.

With such evidence, draft the amendment per `../project-feature-request/`
amendment mode, but keep the drafted delta text **only in the dossier item**
`concretize:diverge:<REQ-ID>` (fix code to spec / amend spec to code) — do
not scaffold an OpenSpec change for it. An unsigned delta that already
matches the code would make the next run read the row as `concrete` before
the owner decided. Until answered, plan nothing for that row; it is excluded
in the coverage matrix as "pending `concretize:diverge:<REQ-ID>`".

A pure ambiguity — the spec admits both readings — is a clarification you
may make directly, recording why (spec-format routing table); it is not a
license to pick the code's reading when the spec is clear.

## 2. Scope and active changes

In scope: `v1-mandatory` rows (including `[TARGET-STATE]`-tagged ones —
dropping the tag when the requirement becomes concrete is bookkeeping), and
`v1-reserved` rows whose declared stub or schema is missing. Out of scope,
listed in the report: `post-v1`.

Only a **signed** active change governs; the marker is defined once in
[spec-format.md § Sign-off marker](../../../references/spec-format.md#sign-off-marker)
and the ledger prints `signed` when it finds it. `UNSIGNED` means no marker: look for sign-off evidence elsewhere (decision
record, bead notes, a merged PR approving the change); if found, cite it and
recommend the owner add the marker — never add it yourself. Then:

| Change state | Action |
|---|---|
| Unsigned (no evidence) | Report only; judge code against the main text; plan nothing from it |
| Signed, has a plan (open `tasks.md` items or linked live beads) | Check only — its rows are `spec-ahead/in-flight`, owned by the change |
| Signed, no plan | One finding for the change (one bead or note on its owning bead), not per-row beads |
| All tasks checked, requirements still unmet | `tasks.md` is wrong: note it on the change's bead; rows return to normal flow B |
| Implemented and verified | Recommend `openspec archive`; report it |

## 3. Reconcile against the ledger

The ledger joins beads to requirement IDs. **Owners** cite the ID on a
`Requirements:` line; **mentions** cite it anywhere else and are candidates,
not owners. An epic never counts as the owning bead; a `spec:closeout` bead
verifies, it does not own. Match in this order: owner → mention → audit-key
→ `spec_id` capability → title and surface similarity in the "other live"
and "recently closed" lists. Read a candidate before counting it:

```bash
bd show <id> --json | jq -r '.[0] | "\(.id) \(.status) \(.issue_type) \(.assignee // "-")\n\(.description // "")\n-- AC --\n\(.acceptance_criteria // "")"'
bd search "<surface terms>" --status closed --limit 20     # older regressions beyond the ledger's closed window
```

**Foreign beads.** Treat every `in_progress` or assigned bead as owned by
someone else unless its assignee equals an actor set explicitly for this run
(`BEADS_ACTOR`); the default actor is usually the owner's git name, which
proves nothing. A foreign bead only ever gets a note.

**Notes are idempotent.** Skip a note when the bead already carries a
spec-concretization note at the same SHA (the ledger shows `noted@<sha>`) or
with unchanged evidence; otherwise a same-head re-run is never zero-action.

Requirement side — one state per row, in preference order:

| State | Condition | Action |
|---|---|---|
| attach | A live owner's acceptance covers the requirement | Note: `bd update <id> --append-notes "<date> spec-concretization @<sha>: REQ-… still unmet at <file:line>"` |
| extend | An unassigned open bead's *stated outcome* already implies this requirement (its governing spec covers it) but its acceptance misses it | Read the field (`bd show <id> --json \| jq -r '.[0].acceptance_criteria'`), append, write back guarded: `bd update <id> --if-assignee '' --if-status open --acceptance "<full text>"`. Exit 13 → it was claimed: fall back to `new` plus a note |
| new, same package | A bead owns the seam but its outcome does not imply this requirement, or it is foreign | New bead proposed as a member of that bead's delivery package (work-allocation § Accepted Outcome); foreign seam owner → also `bd dep add <new> <claimed>` to serialize, and a note to its owner |
| supersede | An unassigned live bead's *outcome* is wrong for the current spec (a stale packet is rewritten in place instead — see drifted) | New bead with `Supersedes: <id>` in design, `bd dep add <new> <old> --type supersedes`, close the old with that reason |
| reopen | A closed bead claimed it and closed **without** meeting the requirement | `bd reopen <id> --reason "<evidence @sha>"` |
| regressed | A closed bead met it (verified landing) and later code broke it | New `spec:defect` bead plus `bd dep add <new> <closed> --type caused-by`; closed history stays closed |
| held | The covering bead is blocked on an owner gate, or deferred with a named authority | Note only; planned-but-held. Deferred **without** a named authority → owner item |
| new | No match | Create per step 5 |

Backlog side — every live bead the ledger linked to a spec:

| State | Condition | Action |
|---|---|---|
| close | The audited SHA is on the delivery base, **every** acceptance criterion holds (not only the cited requirement), no activation or runtime proof is outstanding, and the bead is neither a delivery-package anchor with an open PR (`external_ref gh-pr:*`) nor a member of an unreleased package | `bd close <id> --reason "verified by spec-concretization <date> @<sha>: <REQ-IDs>"`. Any condition unmet → a note for its owner instead |
| orphan | Cites a requirement ID that no longer exists | Removed or never existed? `git log -S '<ID>' --oneline -- openspec/`. Removed → close as obsolete (foreign → note). Never specified → it is new scope: note it and route the idea to `../project-feature-request/` |
| drifted | Its acceptance contradicts the current spec | Unassigned: rewrite the packet in place (work-allocation § Current Operative Packet). Foreign: note to its owner with the contradiction |
| overlap | The ledger lists the ID under "owned by more than one live bead" | Merge into one owner: unassigned duplicates are superseded; foreign ones get a note |

## 4. Coverage matrix (the "all of it" check)

Before creating anything, build it:

| REQ-ID | Sub-kind | State | Owning bead | Notes |
|---|---|---|---|---|

Complete when every in-scope requirement ID has exactly one owning bead
(existing or to-be-created), or an explicit exclusion naming its authority:
owner decision, pending owner gate `<decision-id>`, signed active change,
escalation handoff, or `post-v1`. Two owners for one ID is an overlap — merge
or supersede. An ID with no owner is the bug this skill exists to catch.

## 5. Plan the remaining work

Load [`work-allocation.md`](../../../references/work-allocation.md); bead
form (fields, `complexity:` label, packet shape) is
`/beads-orchestration` beads-writer's contract — file through it. Unowned
rows become cohesive beads, never one bead per row:

- **Group by seam.** Requirements touching one module or interface, one test
  seam, one migration, or one review surface are one bead. Verification-only
  rows (`unverified`) of one capability are one bead at that capability's
  test seam.
- **Fold into existing work** where step 3 allows it; otherwise propose the
  new bead into the existing delivery package rather than a parallel one.
- **Epic when several outcomes.** More than one independent outcome → one
  parent epic per capability (or for the run when capabilities interlock).
  Reuse an open epic or closeout path the ledger lists before creating one.
- **Large gap sets** (more than a handful of beads): write the graph as a
  plan and preview it — `bd create --graph plan.json --dry-run`, then the
  real create — so creation is one reviewable step; otherwise create
  sequentially and `bd dep add` for real prerequisites only.

Ordering is prerequisites, not priority — dependencies reflect real gates:

1. Bounded investigations for `unknown` rows that gate others — evidence
   target, owner, exit criterion.
2. Shared contracts and representation changes (schemas, wire formats, core
   infrastructure) — representation → propagation → enforcement when
   tightening a stored or wire contract.
3. Domain behavior (`missing`, `partial`) and defects against requirements.
4. User-facing surfaces and cosmetic behavior.
5. Verification-only beads — independent; may run alongside the above.

Priority is separate: defects in shipped behavior rank at least as high as
missing behavior; core infrastructure > domain logic > UI/cosmetic.

Bead packet (adds traceability to beads-writer's form):

- `description`: the outcome and exclusions in complete sentences; the
  governing requirement IDs and spec paths.
- `design`: current implementation evidence (`file:line` at the audited
  SHA), seam and boundary notes,
  `Audit-key: spec:<sub-kind>:<capability>[:<surface-id>]`, and a
  `Requirements:` line listing every REQ-ID it owns — the line is the join
  key; the audit-key only groups.
- `acceptance_criteria`: per requirement, the observable scenarios that must
  hold, and "a test citing <REQ-ID> exists at the behavior seam;
  `spec-trace-check.py --strict` reports no uncovered ID among these".
- `--spec-id openspec/specs/<capability>/spec.md`.

Closeout path: one per capability or run, reused across runs — the epic, or
one closeout bead when there is no epic, carrying
`Audit-key: spec:closeout:<capability|all>` and a `Verifies:` line (never
`Requirements:`, so it is not counted as an owner). Acceptance: "re-run
spec-concretization on the merged head: zero spec-ahead rows for these IDs;
`spec-trace-check.py --strict` clean for them". Not a reconciliation bead
per child.

## 6. Escalate instead of filing

Hand to `../project-direction/` — the run report's Escalations section is the
packet, consumed under direction's receiver protocol — when a gap needs an
architecture, trust-boundary, migration, or concurrency-model decision not
already in a design contract. Those rows are owned by the handoff in the
coverage matrix; no beads until direction decides.

Sequencing questions (several milestones of work, capacity trade-offs) are
handed off *after* the beads are filed: the backlog holds the work,
direction decides the order.

A requirement that itself conflicts with doctrine is not a planning problem:
raise `concretize:diverge:<REQ-ID>` with feature-request amendment as the
proposed path.

## 7. Confirm

Re-run the ledger. Every in-scope ID shows exactly one live owner, a signed
change, or a recorded exclusion; the overlap section is empty; orphans and
drifted beads are resolved or noted.
