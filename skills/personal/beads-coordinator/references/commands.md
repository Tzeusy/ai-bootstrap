# Commands

Use this file for quick lookup. It is not required reading before every run.

## Lease Checklist

Repeat this during the run:

Before any `bd` mutation: verify lease ownership, renew if near expiry, then
mutate.

Coordinator lease responsibilities:
- claim with session ID + lease token
- renew at least every 5 minutes while active
- renew before every `bd create`, `bd update`, `bd dep add`, `bd close`
- renew after long `gh`, test, rebase, or merge steps
- replace the canonical lease block; never append a second one

## Session Completion Checklist

```bash
# 1. Verify all workers finished or cleaned up
bd worktree list

# 2. Release stale claims only after verifying the lease is dead or expired
bd list --status=in_progress --json

# 3. Verify Dolt DB is healthy
bd dolt status

# 4. Push everything
git pull --rebase && git push
git status
```

Codex add-on:
- close completed or unused subagents so thread limits do not block future
  dispatches

## bd Quick Reference

| Action | Command |
|---|---|
| Ready work | `bd ready --json` (add `--rig <rig>` if outside target rig) |
| All open | `bd list --status=open --json` (add `--rig <rig>` if outside target rig) |
| PR-review issues | `bd list --status=blocked --label pr-review --json` |
| PR-review-task issues | `bd list --status=blocked --label pr-review-task --json` |
| Issue detail | `bd show <id> --json` |
| Check PR state | `gh pr view <number> --json state,mergedAt,createdAt` |
| Find PR by worker branch | `gh pr list --state open --head "agent/<id>" --json number,url,createdAt` |
| Create issue | `bd create "<title>" --description "<desc>" -t <type> -p <priority> --json` |
| Claim issue | `bd update <id> --status in_progress --json` plus lease write/verify |
| Release issue | `bd update <id> --status open --json` |
| Block review issue | `bd update <id> --status blocked --json` |
| Close issue | `bd close <id> --reason "<reason>"` |
| Add dependency | `bd dep add <issue> <depends-on>` |
| Children | `bd children <id> --json` |
| Blocked | `bd blocked --json` (no `--rig` support; use `bd list --rig <rig> --status=blocked` cross-rig) |
| Dolt server status | `bd dolt status` |
| Dolt version control | `bd vc status` |
