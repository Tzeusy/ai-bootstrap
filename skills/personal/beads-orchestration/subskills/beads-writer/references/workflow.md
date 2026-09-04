# Beads Writer Workflow

Use this reference for the actual step-by-step issue-writing flow.

## Phase 1: Understand The Ask

Before writing any bead, gather enough context to write it well:

1. Clarify scope. A vague ask like "improve auth" produces vague beads. Push for the desired outcome, affected users, constraints, and why it matters.
2. Survey the codebase. Read the relevant files so the bead uses the repo's real terms, modules, and current behavior.
3. Check existing and recently completed delivery. Search open and recently closed beads, open PRs/branches, and the concrete symbols and files involved;
   keyword-only title matching is insufficient. Link or supersede an existing
   outcome rather than creating a parallel symptom bead.
4. Identify dependencies. Determine what blocks the work, what it blocks, and whether the work belongs under an existing epic.
5. Work from the target project workspace. Run Beads commands from the repository whose backlog you are editing.
6. Write for a cold start. Do not stop at "enough context for me right now." Capture enough background that a future independent session can execute the bead without the creator session's hidden context.

## Phase 2: Decompose

Load and apply the shared
[`th-projects` work-allocation contract](../../../../th-projects/references/work-allocation.md),
then choose the right granularity:

| Signal | Action |
|--------|--------|
| Work fits a single focused session | Write one bead |
| Work has distinct independently reversible outcomes | Write separate beads, optionally under an epic |
| Work spans risk classes or requires an additive contract rollout | Sequence children under an epic |
| Related open issues already exist | Link or extend those issues instead of duplicating scope |

Single-responsibility rule: each bead should produce one cohesive independently
verifiable outcome. A layer, file, scenario, or review specialty is not itself
a boundary.

Before splitting, run the contract's **cohesion scan**. Sharing two or more of
module/interface, tests/fixtures, migration/config/persisted contract, review
surface, or micro-sized implementation means bundle or serialize unless
independent rollback plus a different risk/dependency/sign-off gate justifies
the split. Record any override.

### Overhead Budget

Every subbead adds real cost:

- Worktree creation and teardown
- CI and test runs per branch or PR
- Review and merge coordination
- Context loading for the next worker

That is why 10 tiny subbeads can be worse than 3 focused ones. The rule is
3-7 children per epic; more than 9 needs a recorded override in the epic's
`design` field, and the usual fix is milestone sub-epics. Each child also pays
one CI run per push plus a full re-run whenever it rebases, so N children
merging in sequence cost O(N^2) CI without a merge queue.

Each child should usually:

- Fill a focused session with implementation and verification rather than a
  few mechanical minutes
- Touch a bounded, coherent ownership surface
- Produce a diff a reviewer can evaluate in one pass
- Carry enough task framing and context to act as a standalone prompt for a fresh session

When tempted to split further, ask whether the split reduces review complexity or just creates more reviews.

When tempted to merge, ask whether a reviewer can still hold the full change in their head.

For a tightened required contract crossing stored representation, producers,
deferred/retry paths, and enforcement, prefer representation → propagation →
enforcement. Keep one cohesive bead instead when the protocol or vertical user
outcome cannot produce a safe intermediate state.

### OpenSpec-Anchored Epics

When an epic is driven by an OpenSpec change:

1. List the specific OpenSpec section paths each child bead covers.
2. Add an acceptance item telling the worker to verify behavior against those section paths.
3. Avoid vague phrases like "per the spec." Cite the exact section path.

## Phase 3: Craft Each Issue

Use [`fields-and-examples.md`](./fields-and-examples.md) for the field-by-field bar. The minimum writing standard is:

- Title: imperative, specific, under 72 characters
- Description: explains what, why, and context
- Acceptance: testable, enumerated, and outcome-based
- Dependencies: explicit and wired intentionally

### Structured Dispatch Packet

Populate structured fields so the bead is dispatch-ready:

- **Description**: outcome, non-goals, governing spec/doctrine, and why now.
- **Design**: owned surface map, trust boundaries, schemas/runtimes, callers,
  persistence/deferred paths, and rollback or sequencing decisions.
- **Acceptance criteria**: happy path plus relevant failure, concurrency,
  idempotence, retry/replay, compatibility, documentation impact, and named
  behavior-executing verification. State "not applicable" only with a reason.

An acceptance checklist embedded only in `description` does not replace the
structured `acceptance_criteria` field.

Mark the handoff **packet-complete** only after those fields pass review.
**Runnable-now** additionally means dependencies/sign-off are clear and no
active owner or PR overlaps the surface. Only runnable-now work is dispatch-ready.
Record cohesion exceptions in `design` as `Cohesion override: <reason>` and
dedupe outcomes as `Supersedes: <bead/PR>`.

Hard rule: the description must be comprehensive enough for an independent future session to execute the bead without relying on unstated creator-session context. For subbeads, that means the bead should read like a full standalone prompt.

Avoid references like "as discussed", "same as before", or "use the usual approach" unless the referenced artifact is linked and unambiguous.

## Phase 4: Pre-Flight

Before creating beads in bulk:

1. Run `bd doctor`.
2. Check `bd vc status` for unresolved Dolt conflicts.
3. Confirm `.beads/` is not leaking into code diffs.

## Phase 5: Create

Creation rules:

- Create in dependency order: parents and blockers first.
- Use `bd create --json` and capture the returned `id`.
- Use `bd create`, not `bd q`, whenever a real description is required.
- Do not use `--deps` flags in `bd create`; create the bead first, then run `bd dep add`.
- Re-run `bd doctor` after large create/update batches.

## Phase 6: Verify

After creation:

1. Run `bd show <id>` for each new bead.
2. Run `bd dep tree <epic-id>` for epics.
3. Run `bd ready` to make sure the intended work is unblocked.
4. Run `bd lint`; use `bd create --validate` during creation where supported so
   empty structured fields fail before dispatch.
5. For each epic, confirm there is exactly one terminal reconciliation child, carrying the `reconciliation` label, depending on every other child.
6. Re-run the dedupe and cohesion checks against the IDs just created and any
   open PRs that appeared during authoring.

Present created beads with at least ID, title, type, and priority.
