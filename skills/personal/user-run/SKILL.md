---
name: user-run
description: 'Use when a step needs privileges this session lacks (docker, sudo, another user''s checkout or secrets, host access) and the owner must run it as tze. Writes a reviewable /home/orca/.tmp/<slug>/run.sh that impersonates tze (USER_TO_IMPERSONATE overrides), tees timestamped logs plus latest.log and collects artifacts there; Claude presents it with a risk and time brief, then continues from the logs. Triggers: "I''ll run it for you", "permission denied on docker.sock", "needs sudo", "sudo: a password is required", "run as tze", "/user-run".'
metadata:
  owner: tze
  authors:
    - tze
    - Claude Opus 5.5
  status: active
  last_reviewed: "2026-10-09"
---

# User Run

A handoff protocol for commands only the owner can run. Claude writes one
script per session, the owner runs it, and Claude reads its logs and carries
on without being told what happened.

## Use When

- A command fails for lack of privilege the session does not have: the
  docker socket, `/secrets/*`, another user's home, sudo.
- The owner offers to run something as `tze`, or asks for a `/user-run`.

Do not use it to get around a permission rule or a denied tool call. If the
owner did not offer to run it, ask first.

## Layout (fixed)

`<base>` is `$HOME/.tmp` of the Claude session user (`$USER_RUN_BASE`
overrides): **`/home/orca/.tmp`** for orca. Always write absolute paths in
the payload; never `~`, which expands to `/home/tze` there.

```
<base>/<slug>/
  run.sh                   harness + PAYLOAD heredoc
  .lock                    held while a run is in progress (one run at a time)
  <RUN_ID>.log             full stdout+stderr of one run (RUN_ID = YYYYmmddHHMMSS)
  <RUN_ID>.exit            payload exit code; absent if the run died
  payload.<RUN_ID>.sh      the payload exactly as executed
  latest.log, latest.exit  symlinks to the newest run (latest.exit absent while running)
  artifacts/<RUN_ID>/      $ARTIFACTS for that run; artifacts/latest -> newest
```

The slug dir is mode 2770 and shares the session user's group (`orca`); tze
is in that group and the payload runs with umask 002, so both users can read
and write everything. Earlier runs' artifacts stay readable under
`artifacts/<RUN_ID>/` for a later payload to use.

## Procedure

1. **Pick the slug once per session**: `<topic>-<YYYYmmdd>`, e.g.
   `dev-rollout-20261009`. Reuse it for every later step in the session.
2. **Scaffold**: `bash <skill-dir>/scripts/scaffold.sh <slug>`. It is
   idempotent, never overwrites `run.sh`, and first prunes user-run state
   older than 7 days ([cleanup](#cleanup)).
3. **Write the payload.** Edit only the `PAYLOAD` heredoc in `run.sh`:
   - Keep `set -euo pipefail`. Add `set -o pipefail` before any `$(… | tail)`.
   - Use absolute paths, `cd` explicitly, and use `/home/tze/...` for tze's
     checkouts. No line may be exactly `PAYLOAD`; it ends the heredoc.
   - Stdin is `/dev/null`: nothing may wait for typed input except `sudo`,
     which prompts on the terminal. Use `--yes`/`-y` style flags.
   - Write machine-readable results (tags, SHAs, JSON) to `"$ARTIFACTS/…"`, and
     `echo` a one-line `RESULT key=value` summary at the end.
   - Never print secrets. Load them with `set -a; . <envfile>; set +a` or
     `bws run`, and never echo them. The log is read back into Claude's context.
   - Don't leave background jobs attached to the output: the run does not end
     until they close it. Detach them with redirected output (`nohup … >file 2>&1 &`).
   - Make it rerunnable. On later steps, replace or extend the payload; earlier
     payloads stay as `payload.<RUN_ID>.sh`.
4. **Validate**: `bash -n run.sh`, and re-read the payload once.
5. **Present it** to the owner using the brief below, then stop and wait.
6. **When the owner says it ran**, run `bash <skill-dir>/scripts/status.sh <slug>`:
   it reports `running`, `done exit=N` or `died`, the `RESULT` lines, the
   artifacts and the log tail. Read more of the log only if that is not
   enough. Then continue the task on your own. On failure, diagnose from the
   log, fix the payload, and present the delta. Re-present the whole brief
   only if the risk changed. `exit=130`/`143` means it was interrupted or killed.

## Presentation brief (every time)

Lead with the command, then:

- **Command**: `bash <base>/<slug>/run.sh`, from the owner's own terminal.
  Running it as tze directly needs no password. Run as anyone else, it calls
  `su`, which needs a real terminal (the harness refuses without one).
  Claude Code's `!` prefix won't work: it runs as the session user, with no terminal.
  Mention when the payload calls `sudo`: expect a sudo password prompt too.
- **What it does, end to end**: each step in order, in plain words.
- **Side effects**: what changes outside `<base>/<slug>`: git state,
  registry pushes, cluster or DB writes, files in tze's home, system changes
  via sudo.
- **Risk**: low / medium / high, with one reason. Low means read-only or
  rerunnable and local. High means anything destructive, outward-facing or
  hard to undo; most `sudo` changes to the system are at least medium.
- **Time**: an estimate, plus what dominates it.
- **Rollback**: how to undo it, or "nothing to undo".
- **What I'll do next**: what Claude reads from the log and does after.

## Harness behaviour

- It impersonates `${USER_TO_IMPERSONATE:-tze}`. If the invoking user already
  is that user, it runs directly without a prompt. Otherwise it runs
  `su --pty - <user>`, which prompts on the terminal; Claude never sees the
  password. `--pty` matters: plain `su -c` starts a session without a
  controlling terminal, so `sudo` inside the payload could not prompt.
- The payload runs under that user's interactive shell (`$SHELL -ic`), so PATH
  from `~/.zshrc` applies (`(eval): can't change option: zle` lines in the log
  are harmless). A plain `su -c` misses it, which is how `bws` went missing on
  2026-10-09.
- One `tee` captures everything, including the payload's stderr, with start
  and end markers and the exit code. Ctrl-C still records `exit=130` and keeps
  the log tail. A second run of the same slug while one is in progress is
  refused.
- It refuses early, with a reason, when the slug dir is not writable by the
  invoker, the target user does not exist, or `su` would have no terminal.

## Cleanup

`scripts/cleanup.sh [--days N] [--dry-run]` (scaffold runs it with the
default 7 days) removes, under `<base>`, slug dirs with no file modified in N
days, and older runs (log, exit, payload copy, artifacts) inside live slug
dirs, always keeping the latest run. It touches only dirs whose `run.sh`
carries the `# user-run:` header, and skips slugs with a run in progress.
Files the payload left without group write permission can't be removed; it
reports them and carries on.

## Template

[`assets/run.sh.template`](assets/run.sh.template) is the harness. Change the
template, not individual run scripts, when the harness itself needs to change.
Existing `run.sh` files keep the harness they were scaffolded with.
