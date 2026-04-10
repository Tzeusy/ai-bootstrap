# Runtime Contract

Load this file when you need the exact worker bootstrap, guidance-discovery, or
handoff failure policy.

## Bootstrap Contract

Before reading the issue deeply or editing code:

1. `cd "${WORKTREE_PATH}"`.
2. Compute the current path and branch:

```bash
CURRENT_PATH=$(pwd -P)
CURRENT_BRANCH=$(git branch --show-current 2>/dev/null || true)
python3 scripts/assert_worker_context.py \
  --worktree-path "${WORKTREE_PATH}" \
  --repo-root "${REPO_ROOT}" \
  --issue-id "${ISSUE_ID}" \
  --current-path "${CURRENT_PATH}" \
  --branch "${CURRENT_BRANCH}"
```

3. The worker is valid only if:
   - `CURRENT_PATH == WORKTREE_PATH`
   - `CURRENT_PATH != REPO_ROOT`
   - `CURRENT_BRANCH == agent/${ISSUE_ID}`
   - the branch is not `main` or `master`

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
