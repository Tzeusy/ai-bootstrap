# Runtime Contract

Load this file when you need the exact worker bootstrap, guidance-discovery, or
handoff failure policy.

## Bootstrap Contract

Before reading the issue deeply or editing code:

1. `cd "${WORKTREE_PATH}"`.
2. Compute the current path and branch:

```bash
CURRENT_PATH=$(pwd -P)
ASSERT_WORKER_CONTEXT="<loaded beads-worker package>/scripts/assert_worker_context.py"
python3 "${ASSERT_WORKER_CONTEXT}" \
  --worktree-path "${WORKTREE_PATH}" \
  --repo-root "${REPO_ROOT}" \
  --issue-id "${ISSUE_ID}" \
  --current-path "${CURRENT_PATH}"
```

Resolve `ASSERT_WORKER_CONTEXT` from the absolute path of the loaded
`beads-worker/SKILL.md`; the skill package need not live in the target repo.

3. The worker is valid only if:
   - the helper's actual process cwd equals `CURRENT_PATH`
   - `CURRENT_PATH == WORKTREE_PATH`
   - `CURRENT_PATH != REPO_ROOT`
   - the helper-derived actual branch equals `agent/${ISSUE_ID}`
   - the branch is not `main` or `master`
   - `WORKTREE_PATH` and `REPO_ROOT` are Git worktree roots with the same
     canonical common Git directory

Run both the helper and every Git/worktree command with actual process cwd set
to the intended repository or worktree. `bd -C "${REPO_ROOT}"` selects the
tracker; it does not bind subsequent Git commands to that repository. The
helper removes inherited `GIT_*` repository overrides when deriving both
identity and branch, and reports only reason codes, never remote URLs or Git
command diagnostics.

If validation fails, stop immediately and report `invalid-runtime-context`.

## Guidance Discovery Order

Read project guidance in this order:

1. `AGENTS.md` in the worktree root.
2. `CLAUDE.md` in the worktree root.
3. Other project docs only if those files point to them or if commands remain
   unclear.

For project-local `craft-and-care`, search inside the worktree instead of
guessing product-specific install locations:

```bash
rg --files "${WORKTREE_PATH}" | rg '(^|/)craft-and-care/SKILL\.md$'
```

If multiple matches exist, prefer the repo-owned path over vendored mirrors or
fixtures. Read only the selected file.

## Quality Gate Discovery Order

Determine required verification in this order:

1. Explicit commands in `AGENTS.md` / `CLAUDE.md`.
2. Repo-native scripts such as `package.json`, `Makefile`, `justfile`,
   `pyproject.toml`, or language-specific task runners.
3. Existing CI config if local docs still leave ambiguity.

Do not invent lighter substitute gates when the repository already defines
stricter ones.

## Read-Only Helper Boundary

You may use the runtime's native delegation only for:
- codebase discovery,
- architecture reading,
- command lookup,
- test-plan review.

Do not use helpers for:
- code edits,
- commits,
- Beads lifecycle changes,
- splitting implementation into parallel writers.

## Push And PR Failure Routing

If `git push` or `gh pr create` fails:

1. Check whether the failure is a quick local fix, such as:
   - branch not yet set upstream,
   - stale remote refs,
   - malformed PR title/body command.
2. Retry once after the local fix.
3. If the failure is still present, or it is caused by auth, permissions,
   network, protected branch policy, or repository policy you cannot satisfy
   locally, stop and report `blocked-awaiting-coordinator`.

When blocked after useful code changes:
- keep commits,
- set `Recovery-State` truthfully,
- include the exact failing command and blocker rationale in `Blockers-JSON`.
