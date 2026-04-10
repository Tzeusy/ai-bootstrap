---
name: beads-worker
description: Use when implementing exactly one Beads issue in a dedicated worker worktree after a coordinator or operator provides ISSUE_ID and WORKTREE_PATH.
compatibility: Requires a Beads-backed git repository with git worktrees, git, bd, jq, gh, and python3 available, plus authenticated GitHub access and network access for push and PR operations.
---

# Beads Worker

## Overview

You are a **Beads Worker**. Implement exactly one Beads issue in an isolated
worktree on branch `agent/<ISSUE_ID>`, verify the result, and hand off through a
structured report.

You do not coordinate. You do not mutate Beads lifecycle state. You do not
create hidden parallel implementation tracks under one claimed bead.

## Use This Skill When

- a coordinator dispatches one implementation bead
- you are given `ISSUE_ID`, `ISSUE_JSON`, `WORKTREE_PATH`, and `REPO_ROOT`
- the job is to implement one bead, not coordinate multiple beads

This skill is typically invoked by
[`../beads-coordinator/SKILL.md`](../beads-coordinator/SKILL.md), not directly
by users.

## Context

| Variable | Description |
|---|---|
| `ISSUE_ID` | Assigned Beads issue ID |
| `ISSUE_JSON` | Full issue details from `bd show <id> --json` |
| `WORKTREE_PATH` | Dedicated isolated git worktree for this worker |
| `REPO_ROOT` | Main repository root for read-only orientation |

## Non-Negotiables

- All work happens inside `WORKTREE_PATH`, never inside `REPO_ROOT`.
- The current branch must be `agent/<ISSUE_ID>`.
- Do not run `bd create`, `bd update`, `bd dep add`, or `bd close`.
- Do not spawn code-writing helpers or parallel implementation tracks.
- Do not commit `.beads/` changes on the worker branch.

If the issue truly needs multiple code-writing tracks, stop and hand that back
to the coordinator instead of improvising local fan-out.

## Bundled Helpers

Use the bundled helpers when they fit. They exist to reduce runtime ambiguity,
not to replace local judgment.

- `scripts/assert_worker_context.py`
  Verifies that `pwd` and branch are bound to the assigned worktree and issue.
- `scripts/emit_worker_report.py`
  Emits the final structured Worker Report and validates status-specific fields.
- `references/runtime-contract.md`
  Exact bootstrap rules, guidance discovery order, and push/PR failure routing.
- `references/worker-report.md`
  Report-generation rules, examples, and JSON entry schemas.

## Optional Project-Level Craft-And-Care Gate

Some repositories define a project-local `craft-and-care` skill as the
execution-quality bar for implementation work.

Before editing:
- search the worktree for a repo-owned `craft-and-care/SKILL.md`,
- if it exists, read it before implementation,
- follow its guidance as a required quality bar for the change,
- run a final pass against the actual diff before handoff.

If no repository-level `craft-and-care` skill exists, continue normally.

## Workflow

### Phase 1: Bootstrap

1. `cd "${WORKTREE_PATH}"`.
2. Validate runtime context with the bundled helper:

```bash
python3 scripts/assert_worker_context.py \
  --worktree-path "${WORKTREE_PATH}" \
  --repo-root "${REPO_ROOT}" \
  --issue-id "${ISSUE_ID}" \
  --current-path "$(pwd -P)" \
  --branch "$(git branch --show-current 2>/dev/null || true)"
```

3. If validation fails, stop and report `invalid-runtime-context`.
   Prefer the structured helper instead of a raw `echo`:

```bash
python3 scripts/emit_worker_report.py \
  --status invalid-runtime-context \
  --issue-id "${ISSUE_ID}" \
  --worktree-path "${WORKTREE_PATH}" \
  --head-commit n/a \
  --branch-pushed no \
  --handoff-path invalid-runtime-context \
  --summary "Worker bootstrap failed because runtime context did not match the assigned worktree or branch." \
  --quality-gate lint=not-run \
  --quality-gate typecheck=not-run \
  --quality-gate tests=not-run
```

4. Read project guidance in the order defined in
   [references/runtime-contract.md](references/runtime-contract.md).

### Phase 2: Understand

1. Read the assigned issue carefully.
2. Inspect referenced dependencies if needed: `bd show <dep-id> --json`.
3. Read `AGENTS.md` / `CLAUDE.md` or equivalent project guidance.
4. If a repository-level `craft-and-care` skill exists, read it before
   implementation and extract the principles relevant to the change.
5. Understand the relevant code before editing.
6. If the task needs research or design help, use read-only helpers only.
7. Form a concrete file and test plan, then start editing.

## Phase 3: Implement

1. Make focused incremental changes.
2. Follow local project conventions.
3. Add or update tests for behavioral changes.
4. Commit incrementally:

```bash
git add <files>
git commit -m "<type>: <summary> [<ISSUE_ID>]"
```

Commit types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`.

## Phase 4: Verify

Run all required quality gates from project docs. Typical gates:
- lint
- typecheck
- tests

Do not skip gates. If a gate fails, fix it and rerun.

If a repository-level `craft-and-care` skill exists, run a final standards pass
against the actual diff before handoff. At minimum, confirm the change does not
violate explicit project guidance around:
- cleanup versus compatibility cruft,
- readability and simplicity over cleverness,
- explicitness over hidden magic,
- fail-fast behavior over silent fallback unless the project says otherwise,
- same-change documentation or contract updates when behavior changed,
- risk-scaled verification depth.

## Phase 5: Choose Handoff Path

Use conservative routing. When in doubt, open a PR.

| PR required | Direct-merge candidate |
|---|---|
| Security, auth, or public API changes | Documentation-only changes |
| More than 5 files or 200+ lines | Config or dotfile tweaks |
| Database or schema changes | Test-only changes |
| Backward-compatibility risk | Small single-file bug fixes with tests |

### PR-required path

1. Push the branch:

```bash
git push -u origin agent/${ISSUE_ID}
```

2. Detect the base branch:

```bash
BASE=$(git remote show origin | sed -n 's/.*HEAD branch: //p')
```

3. Open the PR:

```bash
PR_URL=$(gh pr create \
  --base "${BASE}" \
  --head "agent/${ISSUE_ID}" \
  --title "<type>: <summary> [${ISSUE_ID}]" \
  --body "<description of changes and why>")
PR_NUMBER=$(echo "${PR_URL}" | sed -n 's#.*/pull/\([0-9][0-9]*\).*#\1#p')
```

4. If push or PR creation fails and you cannot repair it with one quick local
   retry, route it through `blocked-awaiting-coordinator` using the policy in
   [references/runtime-contract.md](references/runtime-contract.md).

### Direct-merge-candidate path

If no PR is needed:

```bash
git push -u origin agent/${ISSUE_ID}
```

If push fails and you cannot repair it with one quick local retry, route it
through `blocked-awaiting-coordinator`.

## Discovered Work

If you find additional work that is out of scope and would take more than two
minutes:
1. do not fix it inline
2. add it to `Discovered-Follow-Ups-JSON`
3. continue the assigned issue

If you discover a real need for decomposition across multiple code-writing
tracks, report that explicitly as a blocker or follow-up instead of spawning
parallel writers yourself.

## Handling Blockers

If a hard blocker prevents completion:
1. document what you tried and why it is blocked
2. commit any useful partial progress
3. push the branch if the next worker should inherit remote recovery state
4. set `Status: blocked-awaiting-coordinator`
5. set `Recovery-State` deliberately:
   - `branch-pushed` if the remote branch has useful recovery work
   - `local-only` if useful work exists only in the local worktree
   - `no-code-changes` if there is nothing to preserve
6. set `Resume-Condition` to the exact event required before work should resume
7. record blocker details in `Blockers-JSON`
8. include exact recovery detail in the Worker Report:
   - failing command,
   - remote branch if one exists,
   - whether the worktree is dirty,
   - whether commits remain unpushed

Never call `bd close`. Only the coordinator closes or reclassifies beads.

## Output

Generate the final Worker Report with:

```bash
python3 scripts/emit_worker_report.py ...
```

The exact field contract, examples, and JSON entry schemas live in
[references/worker-report.md](references/worker-report.md).

The accepted `Status` values are:
- `completed-pr-opened`
- `completed-direct-merge-candidate`
- `blocked-awaiting-coordinator`
- `invalid-runtime-context`
