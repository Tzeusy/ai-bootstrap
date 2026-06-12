# Beads Writer Workflow

Use this reference for the actual step-by-step issue-writing flow.

## Phase 1: Understand The Ask

Before writing any bead, gather enough context to write it well:

1. Clarify scope. A vague ask like "improve auth" produces vague beads. Push for the desired outcome, affected users, constraints, and why it matters.
2. Survey the codebase. Read the relevant files so the bead uses the repo's real terms, modules, and current behavior.
3. Check existing issues. Run `bd list --status open` and `bd search "<keywords>"` before creating anything new.
4. Identify dependencies. Determine what blocks the work, what it blocks, and whether the work belongs under an existing epic.
5. Work from the target project workspace. Run Beads commands from the repository whose backlog you are editing.
6. Write for a cold start. Do not stop at "enough context for me right now." Capture enough background that a future independent session can execute the bead without the creator session's hidden context.

## Phase 2: Decompose

Choose the right granularity:

| Signal | Action |
|--------|--------|
| Work fits a single focused session | Write one bead |
| Work has 2-5 distinct deliverables | Write separate beads, optionally under an epic |
| Work spans multiple components or more than a day | Write an epic with child beads |
| Related open issues already exist | Link or extend those issues instead of duplicating scope |

Single-responsibility rule: each bead should produce one testable outcome.

### Overhead Budget

Every subbead adds real cost:

- Worktree creation and teardown
- CI and test runs per branch or PR
- Review and merge coordination
- Context loading for the next worker

That is why 10 tiny subbeads can be worse than 3 focused ones. The sweet spot is usually 3-7 children per epic.

Each child should usually:

- Take 30-120 minutes of focused implementation
- Touch a bounded set of files, ideally no more than 8-10
- Produce a diff a reviewer can evaluate in one pass
- Carry enough task framing and context to act as a standalone prompt for a fresh session

When tempted to split further, ask whether the split reduces review complexity or just creates more reviews.

When tempted to merge, ask whether a reviewer can still hold the full change in their head.

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
4. Run `bd lint`.
5. For each epic, confirm there is exactly one terminal reconciliation child depending on every other child.

Present created beads with at least ID, title, type, and priority.
