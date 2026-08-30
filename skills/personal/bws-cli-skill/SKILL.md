---
name: bws-cli-skill
description: >
  Use when running a process with Bitwarden Secrets Manager CLI (bws),
  selecting the local production or development project, or explaining safe
  BWS authentication and environment injection. Requires content-blind
  handling; never inspect, print, log, or persist secret values.
metadata:
  owner: tze
  authors:
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
  provenance:
    source: local pre-localization package
    relationship: moved into the authored catalog and safety-tuned
compatibility: Requires bws; local project selectors are BWS_TZEHOUSE_ID_PROD and BWS_TZEHOUSE_ID_DEV.
---

# Bitwarden Secrets Manager CLI

Inject secrets only into the command that needs them. Choose the project
explicitly and quote the selector:

```bash
bws run --project-id "${BWS_TZEHOUSE_ID_PROD:?}" -- command arg
bws run --project-id "${BWS_TZEHOUSE_ID_DEV:?}" -- command arg
```

## Safety boundary

- Authenticate with `BWS_ACCESS_TOKEN`; never pass its value on a command line.
- If this machine supplies credentials through trusted `/secrets/.env`, source
  it without tracing. Never `cat`, echo, diff, or otherwise inspect that file.
- Validate only metadata: `command -v bws`, `bws --version`, and content-blind
  presence tests such as `test -n "${BWS_ACCESS_TOKEN-}"`.
- Never run `env`, `printenv`, shell tracing, or diagnostic dumps inside
  `bws run`. The child process and its descendants can read injected values.
- Secret names become environment-variable names. Use only trusted,
  POSIX-safe names; `--uuids-as-keynames` is the safer fallback for names that
  are not POSIX-compatible.
- `--no-inherit-env` reduces inherited shell state but is not a sandbox. The
  child retains ordinary access to the machine.
- Do not use secret list/get output as a health check. Do not persist injected
  values to logs, files, shell history, fixtures, or repository content.

For authentication, command quoting, project filtering, and isolation options,
read the [local CLI reference](./references/secrets-manager-cli.md). Consult the
[official Bitwarden CLI documentation](https://bitwarden.com/help/secrets-manager-cli/)
when behavior may have changed.
