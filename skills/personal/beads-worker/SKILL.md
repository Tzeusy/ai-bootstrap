---
name: beads-worker
description: Use when implementing exactly one Beads issue in a dedicated worker worktree after a coordinator or operator provides ISSUE_ID and WORKTREE_PATH.
compatibility: Requires a Beads-backed git repository with git worktrees, git, bd, jq, and gh available, plus authenticated GitHub access and network access for push and PR operations.
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

This skill is typically invoked by [`../beads-coordinator/SKILL.md`](../beads-coordinator/SKILL.md), not directly by users.

## Context

| Variable | Description |
|---|---|
| `ISSUE_ID` | Assigned Beads issue ID |
| `ISSUE_JSON` | Full issue details from `bd show <id> --json` |
| `WORKTREE_PATH` | Dedicated isolated git worktree for this worker |
| `REPO_ROOT` | Main repository root for read-only orientation |

## Non-Negotiable Isolation Rule

All work must happen inside `WORKTREE_PATH`, never inside `REPO_ROOT`.

What that means:
1. First action: `cd "${WORKTREE_PATH}"`.
2. Every file read, edit, test run, commit, push, and PR command must run from
   `WORKTREE_PATH`.
3. If `pwd` does not equal `WORKTREE_PATH`, stop and report
   `invalid-runtime-context`.

Why this matters:
- workers run concurrently
- writing in the shared checkout corrupts other workers and breaks recovery

## Read-Only Helpers Only

You may use the current runtime's native delegation mechanism for read-only
research, planning, or codebase discovery when that is worth the overhead.

Do not:
- spawn code-writing helpers from `beads-worker`
- create hidden parallel implementation tracks under one claimed bead
- ask helpers to mutate Beads lifecycle state

If the issue truly needs multiple code-writing tracks, multiple branches, or
integration across several implementation tracks, stop and hand that back to
the coordinator instead of improvising local fan-out.

## Environment Setup

Bootstrap before reading the issue deeply or editing code:

```bash
cd "${WORKTREE_PATH}"
PWD_REAL=$(pwd -P)
BRANCH=$(git branch --show-current 2>/dev/null || true)

if [ "${PWD_REAL}" != "${WORKTREE_PATH}" ] || \
   [ "${PWD_REAL}" = "${REPO_ROOT}" ] || \
   [ -z "${BRANCH}" ] || \
   [ "${BRANCH}" = "main" ] || \
   [ "${BRANCH}" = "master" ]; then
  echo "invalid-runtime-context"
  exit 1
fi
```

Throughout the session:
- periodically verify you are still in `WORKTREE_PATH`
- if the runtime supports progress updates, keep them short and concrete
- do not commit `.beads/` changes on the worker branch

## Lifecycle Boundary

- You may read Beads state for context: `bd show`, `bd ready`, `bd list`
- You must **not** run `bd create`, `bd update`, `bd dep add`, or `bd close`
- The coordinator owns lease renewal, status changes, dependency wiring,
  blocker-bead creation, discovered-work bead creation, PR-review bead
  creation, and closure
- Your job is code delivery plus a machine-readable handoff report

Worker/coordinator contract:
- the coordinator reconciles from your explicit Worker Report first, then
  verifies branch or PR state
- use the exact status values and field names from `Output Format`
- `Discovered-Follow-Ups-JSON` and `Blockers-JSON` must be valid JSON arrays
- do not improvise synonyms such as `blocked`, `done`, `partial`, or
  `needs-review`

## Workflow

### Phase 1: Understand

1. Read the assigned issue carefully.
2. Inspect referenced dependencies if needed: `bd show <dep-id> --json`.
3. Read `AGENTS.md` / `CLAUDE.md` or equivalent project guidance.
4. Understand the relevant code before editing.
5. If the task needs research or design help, use read-only helpers only.
6. If the issue actually needs multiple code-writing tracks, stop and hand that
   need back to the coordinator as a blocker or decomposition request.
7. Form a concrete file/test plan, then start editing.

### Phase 2: Implement

1. Make focused incremental changes.
2. Follow local project conventions.
3. Add or update tests for behavioral changes.
4. Commit incrementally:

```bash
git add <files>
git commit -m "<type>: <summary> [<ISSUE_ID>]"
```

Commit types: `feat`, `fix`, `refactor`, `test`, `docs`, `chore`.

### Phase 3: Verify

Run all required quality gates from project docs. Typical gates:
- lint
- typecheck
- tests

Do not skip gates. If a gate fails, fix it and rerun.

### Phase 4: Handoff Preparation

Never call `bd close`. Only the coordinator closes or reclassifies beads.

Before handoff:
1. ensure changes are committed
2. ensure verification is complete
3. choose exactly one handoff path below

## Handoff Paths

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

4. Stop. Report:
- `Status: completed-pr-opened`
- `Handoff-Path: pr-required`

The coordinator will block the original bead, write `external_ref=gh-pr:<N>`,
create the dedicated `pr-review-task` bead, and prioritize review dispatch.

### Direct-merge-candidate path

If no PR is needed:

```bash
git push -u origin agent/${ISSUE_ID}
```

Report:
- `Status: completed-direct-merge-candidate`
- `Handoff-Path: direct-merge-candidate`

The coordinator will attempt the fast-forward merge and close the bead if that
succeeds.

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
8. do not describe this as a stall

The coordinator will preserve recovery state, create blocker beads, wire
dependencies, and mark the original issue blocked.

## Scope Rules

| Do | Don't |
|---|---|
| Finish the assigned issue | Refactor unrelated code |
| Stay inside `WORKTREE_PATH` | Work in `REPO_ROOT` |
| Use read-only helpers only | Spawn code-writing helpers |
| Report discovered work clearly | Fix unrelated bugs inline |
| Run all quality gates | Skip verification |
| Handoff via the structured Worker Report | Run `bd create/update/dep/close` |

## Commit Convention

```text
<type>: <imperative summary, <=72 chars> [<ISSUE_ID>]

<optional body: what changed and why>
```

Examples:

```text
feat: add PSF scoring to analyst agent [bd-42]
fix: handle missing bedroom count in curator [bd-17]
test: add dedup edge cases for cross-portal listings [bd-88]
```

## Output Format

When you finish, produce exactly this high-level structure. The scalar fields
are plain text. The follow-up and blocker collections are JSON arrays.

Machine-safe reporting rules:
- `Discovered-Follow-Ups-JSON` must be valid JSON
- `Blockers-JSON` must be valid JSON
- use compact valid JSON only: no comments, trailing commas, or prose outside
  the JSON structure
- use exactly the keys shown below

````text
## Worker Report: <ISSUE_ID>

Status: completed-pr-opened | completed-direct-merge-candidate | blocked-awaiting-coordinator | invalid-runtime-context
Issue: <ISSUE_ID>
Branch: agent/<ISSUE_ID>
Worktree: <WORKTREE_PATH>
Head-Commit: <git rev-parse HEAD or n/a>
Branch-Pushed: yes | no
Handoff-Path: pr-required | direct-merge-candidate | blocked-awaiting-coordinator | invalid-runtime-context
PR-URL: <url or n/a>
PR-Number: <number or n/a>
Base-Branch: <branch or n/a>
Review-Reason: <why PR review is needed or n/a>
Recovery-State: branch-pushed | local-only | no-code-changes
Resume-Condition: <what must happen before another worker should resume or n/a>
Summary: <1-2 sentence description of what was done>

Quality-Gates:
- lint: pass | fail | not-run
- typecheck: pass | fail | not-run
- tests: pass | fail | not-run

Changes:
- <file>: <what changed>

Tests:
- <test file or command>: <coverage or result>

Discovered-Follow-Ups-JSON:
```json
[]
```

Blockers-JSON:
```json
[]
```
````

Rules:
- use exactly one `Status` value
- if `Status` is `completed-pr-opened`, populate `PR-URL`, `PR-Number`, and
  `Branch-Pushed: yes`
- if `Status` is `completed-direct-merge-candidate`, use `Branch-Pushed: yes`
  and `PR-URL: n/a`
- if `Status` is `blocked-awaiting-coordinator`, include at least one blocker
  object and set `Recovery-State` truthfully
- if bootstrap failed, report `Status: invalid-runtime-context` and stop without
  touching code or Beads lifecycle state
- if there are no discovered follow-ups or blockers, use `[]`

JSON object schemas:

`Discovered-Follow-Ups-JSON` entries:

```json
{
  "title": "Short follow-up title",
  "type": "bug",
  "priority": 2,
  "depends_on": "bd-42",
  "rationale": "Why this should be tracked separately"
}
```

`Blockers-JSON` entries:

```json
{
  "title": "Concrete blocker title",
  "type": "task",
  "priority": 1,
  "depends_on": "bd-42",
  "rationale": "What is blocked and why",
  "unblock_condition": "What must happen before work can resume"
}
```

## bd Quick Reference

| Action | Command |
|---|---|
| Show issue | `bd show <id> --json` |
| List ready work (read-only) | `bd ready --json` |
| Create PR | `gh pr create --base <base> --head <branch> --title "<title>" --body "<body>"` |
| View PR | `gh pr view <number> --json state,mergedAt,url` |
