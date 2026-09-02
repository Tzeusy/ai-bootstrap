# Commands

Use this file for quick lookup. It is not required reading before every run.

## Claim And Heartbeat Checklist

Repeat this during the run:

Before any `bd` mutation: confirm you are the bead's `assignee`, renew the stall
heartbeat if near expiry, then mutate.

Coordinator responsibilities:
- claim atomically with `bd update <id> --claim` (sets `assignee` + `in_progress`)
- check `assignee` (not a lease token) to decide whether a bead is yours
- renew the stall heartbeat at least every 5 minutes while active
- renew at every mutation checkpoint (`bd create/update/dep add/close`) and
  after long `gh`, test, rebase, or merge steps — but skip the renewal when the
  heartbeat was already renewed within the last 5 minutes (one renewal can
  cover a burst of consecutive mutations; the TTL is 20 minutes)
- replace the canonical heartbeat block in notes; never append a second one

## Session Completion Checklist

```bash
# 1. Verify all workers finished or cleaned up
bd worktree list

# 2. Release stale claims only after verifying the heartbeat is expired (assignee idle)
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

Pipe every listing through a `jq` field projection per
`../../../references/token-efficiency.md`; the projections below are the
default coordinator views.

| Action | Command |
|---|---|
| Ready work | `bd ready --json \| jq -c '[.[] \| {id, title, priority, type, labels, assignee, created_at}]'` (prefix with `bd -C /path/to/rig` if outside target rig) |
| All open | `bd list --status=open --json \| jq -c '[.[] \| {id, title, priority, type, labels, assignee}]'` (prefix with `bd -C /path/to/rig` if outside target rig) |
| PR-review issues | `bd list --status=blocked --label pr-review --json \| jq -c '[.[] \| {id, title, labels, assignee, external_ref}]'` |
| PR-review-task issues | `bd list --status=blocked --label pr-review-task --json \| jq -c '[.[] \| {id, title, labels, assignee, external_ref}]'` |
| Issue detail | `bd show <id> --json \| jq '{id, title, status, assignee, labels, external_ref}'` (workers add `description`, `acceptance_criteria`, `notes`, `design`) |
| Check PR state | `gh pr view <number> --json state,mergedAt,createdAt` |
| Find PR by worker branch | `gh pr list --state open --head "agent/<id>" --json number,url,createdAt` |
| Create issue | `bd create "<title>" --description "<desc>" -t <type> -p <priority> --json` |
| Claim issue | `bd update <id> --claim --json` (atomic; sets `assignee` + `in_progress`), then write the stall heartbeat note |
| Release issue | `bd update <id> --status open --json` |
| Stamp readiness rejection | `bd update <id> --add-label needs-shaping --append-notes "dispatch-readiness <date> <session>: missing <fields>"` (see the readiness gate in `coordinator-loop.md`) |
| Shaped beads awaiting re-check | `bd list --label needs-shaping --json \| jq -c '[.[] \| {id, title, labels}]'` |
| Block review issue | `bd update <id> --status blocked --json` |
| Close issue | `bd close <id> --reason "<reason>"` |
| Add dependency | `bd dep add <issue> <depends-on>` |
| Children | `bd children <id> --json` |
| Blocked | `bd blocked --json` (cross-rig: `bd -C /path/to/rig list --status=blocked`) |
| Dolt server status | `bd dolt status` |
| Dolt version control | `bd vc status` |
