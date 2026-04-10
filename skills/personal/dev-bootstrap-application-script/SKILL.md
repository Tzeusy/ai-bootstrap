---
name: dev-bootstrap-application-script
description: Use this skill when the user asks for a `dev.sh`, tmux launcher, local stack bootstrap, or one-command way to start a multi-service application stack in tmux, especially when the script should be idempotent, session-aware, and easy to rerun.
compatibility: Requires a shell environment with bash, tmux, python3, perl, curl, and nc. Optional remote-HTTPS flows also require tailscale.
---

# Dev Bootstrap Application Script

## Overview

Generate a `dev.sh`-style bash script that boots a project's development stack inside tmux with stable pane targeting, per-run logs, and explicit readiness checks.

Default to a local-first script. Only wire in remote HTTPS or path-prefix proxying when the user or project actually needs it.

## When To Use

- The user asks for `dev.sh`, `run-dev`, "bootstrap this app in tmux", or "one command to start the stack"
- The project has multiple long-running services: web, API, worker, database, cache, broker
- An existing launcher script needs to be rewritten to be idempotent, session-aware, or easier to rerun

Do not use this skill for a single short-lived command or for projects that already have a working launcher the user only wants explained.

## Deliverables

Produce all of the following:

1. A bash bootstrap script tailored to the repo
2. An ASCII layout comment at the top showing panes/windows
3. Readiness checks for critical dependencies
4. Per-run log capture under `logs/<timestamp>/` plus `logs/latest`
5. Validation evidence: syntax check plus `scripts/validate_dev_bootstrap.py`

## Available Files

- `assets/dev.sh.template`: local-first single-window starter
- `assets/dev.multi-window.sh.template`: two-window starter for 5+ services
- `assets/dev.three-window.sh.template`: three-window starter for 9+ services
- `references/patterns.md`: pane layouts, grouping heuristics, proxy-prefix checklist
- `scripts/validate_dev_bootstrap.py`: static validator for generated scripts
- `evals/evals.json`: baseline-vs-skill eval prompts
- `evals/trigger-queries.json`: should-trigger and should-not-trigger description tests

## Workflow

### 1. Inventory The Stack

Read the repo before writing anything. Build a service inventory from the files that actually exist:

- `docker-compose.yml`, `compose.yaml`: infra services
- `package.json`, `pnpm-workspace.yaml`, `turbo.json`: frontend/app commands and monorepo layout
- `Makefile`, `Justfile`, `Procfile`, `Procfile.dev`: existing launch targets
- `pyproject.toml`, `Pipfile`, `go.mod`, `Cargo.toml`: backend entry points
- `.env`, `.env.example`: env requirements
- `README.md`: dev setup instructions

Write the inventory in this form before generating the script:

```text
1. service-name - command - working-directory - depends on
```

### 2. Choose The Scaffold

Pick the smallest asset that matches the stack:

- `assets/dev.sh.template` for up to 4 long-running services in one window
- `assets/dev.multi-window.sh.template` for 5+ services or when infra/app separation improves readability
- `assets/dev.three-window.sh.template` for 9+ services or when frontend/docs tooling deserves its own window

Do not force a multi-window script for a small stack. Do not force proxy/Tailscale setup for a local-only request.

### 3. Apply The Non-Negotiables

Every generated script must preserve these invariants:

- Capture pane IDs with `-P -F '#{pane_id}'`; never address panes by numeric index
- Kill and recreate the target window(s) before launching services
- Handle both inside-tmux and outside-tmux entry paths
- Create timestamped logs and refresh `logs/latest`
- Use `tmux pipe-pane -o` with log sanitization so reruns stay readable
- Start services in dependency order and add readiness gates where they matter
- Print operator-facing local URLs; print remote URLs only when remote access is configured
- Keep local-only bootstraps local-only by default

### 4. Add Optional Remote Access Only When Needed

Remote HTTPS, Tailscale Serve, and path-prefix routing are opt-in. If you enable them:

- gate them behind an explicit flag such as `--enable-tailscale-serve`
- inspect current serve status before changing it
- verify the mapping after apply
- keep frontend base path, router parsing, API prefixing, proxy rewrites, and health-check URLs coherent end-to-end

Use `references/patterns.md` for the exact prefix checklist and pane layout snippets.

### 5. Validate Before Delivering

Run both checks against the generated script:

```bash
INSTALLED_SKILL_DIR="${HOME}/.codex/skills/dev-bootstrap-application-script" # adjust client dir if needed
bash -n ./dev.sh
python3 "${INSTALLED_SKILL_DIR}/scripts/validate_dev_bootstrap.py" ./dev.sh
```

If the script uses multi-window layout or remote access, pass the matching validator flags:

```bash
python3 "${INSTALLED_SKILL_DIR}/scripts/validate_dev_bootstrap.py" --expect-multi-window ./dev.sh
python3 "${INSTALLED_SKILL_DIR}/scripts/validate_dev_bootstrap.py" --expect-tailscale ./dev.sh
```

When validating bundled starter assets rather than a generated project script, allow placeholders explicitly:

```bash
python3 "${INSTALLED_SKILL_DIR}/scripts/validate_dev_bootstrap.py" --allow-placeholders assets/dev.sh.template
```

## Authoring Rules

- Prefer established project commands over inventing new ones
- Keep the script idempotent and rerunnable
- Use comments sparingly; reserve them for layout, layers, or non-obvious decisions
- Keep placeholders or TODO markers out of the final generated script
- If the stack is ambiguous, inspect more repo files instead of guessing

## Common Failure Modes

| Failure | Correction |
| --- | --- |
| Tailscale logic added to a local-only request | Remove it or gate it behind an explicit opt-in flag |
| Pane indices like `-t 0` or `-t 1` | Capture pane IDs and use variables |
| More than 4 panes in one window | Split into multiple named windows |
| Logs captured with raw `cat >> file` | Use sanitized `tmux pipe-pane -o` |
| Readiness checks omitted | Add `wait_for_port` or `wait_for_http` where dependencies exist |
| `ENV_CMD` defined but not used | Prefix the actual `tmux send-keys` launch commands with it |

## Verification Checklist

- `bash -n` passes
- Validator script returns `ok: true`
- The script uses local-first defaults unless remote access was requested
- Window count matches the service inventory
- All critical services have correct working directories and launch commands

## Eval Discipline

When improving this skill itself, compare against a baseline. Use `evals/evals.json` for initial prompts and run each case with:

- the current skill
- no skill or a snapshot of the previous skill version

Also test triggering separately with `evals/trigger-queries.json`. Run both should-trigger and should-not-trigger queries multiple times and record trigger rate, not just a single pass/fail.

Keep the eval workspace outside the skill directory, as described in the Agent Skills eval guidance.
