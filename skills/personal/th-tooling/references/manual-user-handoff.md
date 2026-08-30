# Manual User Handoff

Authors: tze, Claude Sonnet 5

Use this cross-tool policy only when a step genuinely requires the user's own
sudo password, TTY, 2FA, browser consent, or another action the agent cannot
perform. It is a direct base-policy reference, not a th-tooling workflow.

## Safety contract

- Never request, receive, store, or type the user's password or secret. Do not
  use `sudo -S`, askpass, or a pasted credential.
- Do not hand off commands the agent can safely run itself.
- Before presenting a script, disclose exactly three labeled lines:

  ```text
  What it does: <plain-language summary>
  Risk: <destructive operations, restarts, or none>
  State changes: <changed resources, or none, read-only>
  ```

- Put each run under `~/.tmp/<slug>/<YYYYmmdd-HHMMSS>/`; repoint `latest` only
  after success. Read results from `~/.tmp/<slug>/latest/` yourself rather
  than asking for paste-back.
- Whole-script sudo resets `$HOME`. Resolve the invoking user's home through
  `${SUDO_USER:-$USER}` and return output ownership after a root run.
- Default diagnostic scripts to `set -uo pipefail`; use `-e` only when a
  dependent mutating sequence must stop at the first failure.

Start from [the canonical template](./manual-user-script-template.sh). It
preserves the output and ownership conventions while leaving task commands
explicit.

For a concrete read-only sudo diagnostic, see the
[root-disk-audit example](./manual-user-handoff-example.md). It demonstrates
the disclosure, whole-script sudo ownership fix, and disk-based result return.

## Handoff sequence

1. Create a narrowly named script from the template and inspect it for secrets
   and unintended mutation.
2. Present the three-line disclosure and the exact command the user should run
   in their terminal.
3. Wait for confirmation, then resolve and read the `latest` output files.
4. Remove the task script only when requested; retained run output belongs to
   the user.
