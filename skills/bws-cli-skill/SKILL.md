---
name: bws-cli-skill
description: Use when working with Bitwarden Secrets Manager CLI (bws) to run commands with injected secrets, manage secret-manager environment variables, or explain bws usage. Essential for wrapping processes with `bws run --project-id ${BWS_TZEHOUSE_ID_PROD or BWS_TZEHOUSE_ID_DEV} -- {command}`.
---

# bws CLI skill

## Overview

Use this skill to guide LLM behavior for the Bitwarden Secrets Manager CLI. Prioritize safe, idempotent usage and emphasize running commands through `bws run` so secrets are injected into the process environment without being written to disk.

## Quick start

1. Confirm `bws` is installed and available in `PATH`.
2. Ensure a valid Bitwarden Secrets Manager access token is present (per official docs).
3. If `/secrets/.env` exists, load it into the current process before running `bws`:
   - `set -a; source /secrets/.env; set +a`
3. Wrap any process that needs secrets with:
   - `bws run --project-id ${BWS_TZEHOUSE_ID_PROD} -- {command}`
   - `bws run --project-id ${BWS_TZEHOUSE_ID_DEV} -- {command}`

## Core guidance

- Prefer `bws run` for any command that requires secrets so values stay in memory only.
- Use explicit project IDs from `BWS_TZEHOUSE_ID_PROD` or `BWS_TZEHOUSE_ID_DEV`; do not hardcode IDs.
- If `/secrets/.env` is the source of project IDs or tokens, load it into the current shell process (avoid printing env values).
- Keep secrets out of logs, files, and repo history.
- If a task requires other bws commands, consult `references/secrets-manager-cli.md` and the official docs.

## Usage examples

- Load env vars then run a production command:
  - `set -a; source /secrets/.env; set +a`
  - `bws run --project-id ${BWS_TZEHOUSE_ID_PROD} -- {command}`
- Run a production command with secrets:
  - `bws run --project-id ${BWS_TZEHOUSE_ID_PROD} -- {command}`
- Run a development command with secrets:
  - `bws run --project-id ${BWS_TZEHOUSE_ID_DEV} -- {command}`

## Reference

For detailed CLI subcommands and authentication setup, read `genai/skills/bws-cli-skill/references/secrets-manager-cli.md` and the official docs at https://bitwarden.com/help/secrets-manager-cli/.
