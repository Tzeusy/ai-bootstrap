---
name: user-run-scripts
description: >
  Use whenever a task needs something the agent's own sandbox cannot do —
  an interactive sudo/root password, another TTY prompt, an action blocked
  by sandbox or permission policy, or any manual out-of-band step (e.g. a
  2FA code) — by handing the user a script to run themselves and reading
  its output back from disk instead of a copy/paste round-trip. Not for
  commands the agent can already run itself. Triggers: "I need sudo for
  this", "this needs your password", "run this yourself", "needs an
  interactive terminal", "sandbox won't let me do X".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Sonnet 5
  status: active
  last_reviewed: "2026-08-30"
compatibility: Linux/macOS, bash, coreutils (tee, ln -s, date); assumes an interactive sudo-capable user terminal separate from the agent's own shell.
---

# User-Run Scripts

The agent's shell often cannot do what a task needs: `sudo` prompts for a
password with no TTY, some actions are blocked by sandbox/permission
policy, or a step is inherently manual (type a 2FA code, click a browser
consent screen). The fix is never to work around the credential — it is to
write the user a script, have them run it in their own terminal, and read
the results back from disk.

## Do not use this skill for

Routine commands the agent's own tools can already run. Reach for this only
when a specific step is blocked — not as a default way to hand off work.

## Never obtain or type the user's password

No `sudo -S` with a piped password, no askpass workarounds, no asking the
user to paste a password into chat. If a step needs credentials, the script
goes to the user's terminal — always.

## The output convention (load-bearing part of this skill)

Every script writes into `~/.tmp/{slug}/`, where `{slug}` is a short
kebab-case name chosen for the task (e.g. `root-disk-audit`):

- a fresh timestamped subdirectory per run — `~/.tmp/{slug}/<YYYYmmdd-HHMMSS>/`
  — with every command's stdout/stderr `tee`'d into a file under it
- a `latest` symlink at `~/.tmp/{slug}/latest`, repointed with `ln -sfn` at
  the end of a successful run, so history survives but the newest run is
  always at a fixed, timestamp-free path

```bash
slug="CHANGE_ME"
real_home="$(getent passwd "${SUDO_USER:-$USER}" | cut -d: -f6)"  # see pitfall below
tmproot="$real_home/.tmp/$slug"
outdir="$tmproot/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$outdir"

echo "==> some diagnostic" | tee "$outdir/some-diagnostic.txt"
# ... more commands, each teed into its own file ...

ln -sfn "$outdir" "$tmproot/latest"   # always last, on success
[ "$(id -u)" -eq 0 ] && [ -n "${SUDO_USER:-}" ] && chown -R "$SUDO_USER" "$tmproot"
```

A ready-to-copy version of this scaffold is
[`scripts/template.sh`](./scripts/template.sh) — start from it rather than
retyping the boilerplate each time.

Once the user confirms the run finished, resolve `~/.tmp/{slug}/latest/`
yourself (`ls`, `readlink -f`, or `Read` the files under it directly).
**Never ask the user to paste output back into chat.**

## Mandatory pre-presentation risk summary

Before showing the script or telling the user to run it, always disclose,
in three labeled lines:

```
What it does: <plain-language summary>
Risk: <destructive ops, irreversible deletes, restarts, config changes — or "none">
State changes: <files/DBs/k8s resources touched, packages installed — or "none, read-only">
```

Never skip this step. A purely read-only script (`du`, `df`, `lsof`) still
gets the disclosure — say "none" / "none, read-only" explicitly rather than
omitting the section.

## Worked example

[`references/worked-example-root-disk-audit.md`](./references/worked-example-root-disk-audit.md)
walks a real case: auditing root filesystem usage that required `sudo du`
into root-owned `/var/lib/rancher` (containerd + Kubernetes PV storage),
with the full script, the disclosure given to the user, and how the results
were read back from `~/.tmp/root-disk-audit/latest/` with no paste-back.

## Pitfall: `sudo` resets `$HOME`

Handoffs commonly say "run `sudo ~/script.sh`" (whole-script sudo, simplest
for the user — one password prompt instead of one per line). But `sudo`
resets `$HOME` to the target user's home (`/root`) by default, so a bare
`$HOME/.tmp/...` inside the script silently writes into `/root/.tmp/`,
unreadable by the agent — and by the user without another sudo. This bit a
real run: `sudo ~/root-disk-audit.sh` wrote its whole output under
`/root/.tmp/root-disk-audit-*/` instead of `~/.tmp/`.

Always resolve the real invoking user's home explicitly, and hand ownership
back if the script ran as root — both are in the template and the scaffold
above (`real_home="$(getent passwd "${SUDO_USER:-$USER}" | cut -d: -f6)"`,
then `chown -R "$SUDO_USER" "$tmproot"` at the end when `id -u` is 0). Do
this even when individual commands also say `sudo` themselves — the whole
script may still be invoked under an outer `sudo`.

## Hard stops

- Never embed a password or secret in the generated script.
- Never attempt the privileged operation directly yourself, even if some
  sandbox permission would technically allow a piece of it — if the task
  fundamentally needs the user's own credentials or an interactive prompt,
  the whole thing goes in the script for them to run.
- Default to `set -uo pipefail` (not `-e`) so a diagnostic script keeps
  reporting later sections after one command fails. Use `set -euo pipefail`
  only for a sequence of dependent mutating steps where any failure must
  halt immediately — say so in the script when you do.
