# Reporting And Quick Reference

Load this file for the cleanup report shape, rig-routing note, and read-only
command quick reference.

## Rig Routing Note

When running outside the target rig, use `bd -C <rig-path>` for read queries so
the correct project database is inspected.

```bash
bd -C <rig-path> list --status=in_progress --json --limit 0
bd -C <rig-path> ready
```

## Report-Only Scan Envelope

**The coordinator is the sole mutation authority.** Before rendering a cleanup
report or handing a finding to the coordinator, run
[`cleanup_scan.py`](../scripts/cleanup_scan.py):

```bash
# from the beads-cleanup package directory
uv run scripts/cleanup_scan.py --repo-root "${REPO_ROOT}"
```

It emits one compact `beads-cleanup-scan/v1` JSON envelope. `claims`,
`blockers`, `dolt`, `worktrees`, and `review_locks` are deterministic findings;
`pr_review` embeds canonical `beads-pr-review-normalization/v1` findings.
`success`, `empty`, `partial`, and `fatal` are reporting states, not mutation
permissions. Never include raw command stderr, notes, descriptions, paths, or
tracebacks in the human report. Preserve any indicated unpublished work.

```text
## Beads Cleanup Report

Timestamp: <ISO 8601>
Scan status: <success|empty|partial|fatal>

### Pass 1: Stale in_progress
- <id>: preserve live claim
- <id>: recommend manual triage (incomplete Git evidence)

### Pass 2-3: PR-review findings
- <id>: PR #N MERGED; recommend coordinator Step 0 verification
- <id>: unresolved canonical context; recommend manual triage

### Pass 4: Dependencies
- <id>: recommend coordinator verification for unblock

### Pass 5: Dolt and worktrees
- Dolt: healthy
- <worktree-id>: preserve unpublished work

### Pass 6: Review locks
- <id>: recommend coordinator verification for stale lock

### Summary
| Metric | Count |
|---|---|
| Release candidates | N |
| Unblock candidates | N |
| Cleanup candidates | N |
| Manual-triage findings | N |
| Unpublished-work findings | N |
```

## Constraints

- Never implement code or perform lifecycle changes from cleanup.
- Never create new Beads from cleanup.
- Never change a branch or worktree from cleanup.
- Never mutate `.beads/dolt/` manually.
- Treat transient command failures as non-authoritative and report manual
  triage instead of guessing.

## Read-Only Command Quick Reference

| Evidence | Command |
|---|---|
| All `in_progress` Beads | `bd list --status=in_progress --json --limit 0` |
| All blocked Beads | `bd list --status=blocked --json --limit 0` |
| By label | `bd list --label <label> --json --limit 0` |
| Show Bead | `bd show <id> --json` |
| List dependencies | `bd dep list <id> --json` |
| Check PR state | `gh pr view <N> --json state,mergedAt` |
| List worktrees | `bd worktree list` |
| Dolt status | `bd dolt status` |
| Repository health | `bd doctor` |
