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

`~` below is **`/home/orca`**, the Claude session's home. Always write the
absolute path; never `~`, which expands to `/home/tze` inside the payload.

```
/home/orca/.tmp/<slug>/
  run.sh                 harness + PAYLOAD heredoc (chmod +x, group orca)
  payload.<RUN_ID>.sh    the payload exactly as executed, kept per run
  <YYYYmmddHHMMSS>.log   full stdout+stderr of one run
  latest.log -> newest log
  latest.exit            payload exit code (absent while running / if killed)
  artifacts/             $ARTIFACTS: tags, reports, small outputs
```

The directory is mode 2770 and group `orca`. tze is in group `orca`, and the
payload runs with umask 002, so both users can read and write everything.

## Procedure

1. **Pick the slug once per session**: `<topic>-<YYYYmmdd>`, e.g.
   `dev-rollout-20261009`. Reuse it for every later step in the session;
   don't make a new slug for each step.
2. **Scaffold** (it's idempotent and never overwrites):
   `bash <skill-dir>/scripts/scaffold.sh <slug>`
   ([`scripts/scaffold.sh`](scripts/scaffold.sh)).
3. **Write the payload.** Edit only the `PAYLOAD` heredoc in `run.sh`:
   - Keep `set -euo pipefail`. Add `set -o pipefail` before any `$(… | tail)`.
   - Use absolute paths, `cd` explicitly, and use `/home/tze/...` for tze's
     checkouts.
   - Write machine-readable results (tags, SHAs, JSON) to `"$ARTIFACTS/…"`, and
     `echo` a one-line `RESULT key=value` summary at the end.
   - Never print secrets. Load them with `set -a; . <envfile>; set +a` or
     `bws run`, and never echo them. The log is read back into Claude's context.
   - Make it rerunnable. On later steps, replace or extend the payload; earlier
     payloads stay as `payload.<RUN_ID>.sh`.
4. **Validate**: `bash -n run.sh`, `chmod +x run.sh`, and re-read the payload once.
5. **Present it** to the owner using the brief below, then stop and wait.
6. **When the owner says it ran**, read `latest.exit` and `latest.log` (tail
   first, then grep for `RESULT`/errors) and `artifacts/`. Then continue the
   task on your own. On failure, diagnose from the log, fix the payload, and
   present the delta. Re-present the whole brief only if the risk changed.

## Presentation brief (every time)

Lead with the command, then:

- **Command**: `bash /home/orca/.tmp/<slug>/run.sh`. Use `! bash …` only if
  it's known to work: `su` needs a real terminal, and Claude Code's `!` may not
  provide one ("su: must be run from a terminal"). If it doesn't, run it from
  your own terminal. Running it as tze directly skips the password prompt.
- **What it does, end to end**: each step in order, in plain words.
- **Side effects**: what changes outside `/home/orca/.tmp/<slug>`: git state,
  registry pushes, cluster or DB writes, files in tze's home.
- **Risk**: low / medium / high, with one reason. Low means read-only or
  rerunnable and local. High means anything destructive, outward-facing or
  hard to undo.
- **Time**: an estimate, plus what dominates it.
- **Rollback**: how to undo it, or "nothing to undo".
- **What I'll do next**: what Claude reads from the log and does after.

## Harness behaviour

- It impersonates `${USER_TO_IMPERSONATE:-tze}`. If the invoking user already
  is that user, it runs directly without a prompt. Otherwise it runs
  `su - <user>`, which prompts on the terminal; Claude never sees the password.
- The payload runs under that user's interactive shell (`$SHELL -ic`), so PATH
  from `~/.zshrc` applies. A plain `su -c` misses it, which is how `bws` went
  missing on 2026-10-09.
- One `tee` captures everything, including the payload's stderr, with start
  and end markers and the exit code.

## Template

[`assets/run.sh.template`](assets/run.sh.template) is the harness. Change the
template, not individual run scripts, when the harness itself needs to change.
