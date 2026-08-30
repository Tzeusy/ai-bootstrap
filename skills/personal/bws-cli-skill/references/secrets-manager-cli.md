# Bitwarden Secrets Manager CLI reference

Use this reference for command details beyond the skill's default wrappers.
The source of truth is Bitwarden's
[Secrets Manager CLI documentation](https://bitwarden.com/help/secrets-manager-cli/),
reviewed 2026-08-31 against local `bws 1.0.0` help.

## Authentication

`bws` accepts the access token from `BWS_ACCESS_TOKEN`. Prefer that environment
variable over `--access-token`, which can expose the token through command
arguments or shell history. Presence checks must remain content-blind:

```bash
command -v bws >/dev/null
bws --version
test -n "${BWS_ACCESS_TOKEN-}"
```

If a trusted host provisions `/secrets/.env`, source it without shell tracing:

```bash
if [ -r /secrets/.env ]; then
  set -a
  . /secrets/.env
  set +a
fi
```

Do not inspect the file or print any resulting environment value.

## Project-scoped execution

Use the environment selector for the intended boundary and pass the executable
after `--`:

```bash
bws run --project-id "${BWS_TZEHOUSE_ID_PROD:?}" -- command arg
bws run --project-id "${BWS_TZEHOUSE_ID_DEV:?}" -- command arg
```

`bws run` injects matching secret values as child-process environment
variables. This avoids an intermediate plaintext file, but does not prevent the
child, its descendants, or unsafe diagnostics from exposing them.

## Current options and caveats

- `--project-id <PROJECT_ID>` limits injection to one project.
- `--uuids-as-keynames` (or `BWS_UUIDS_AS_KEYNAMES=true`) substitutes
  POSIX-compatible UUID-derived keys when secret names are unsafe or invalid as
  shell identifiers.
- `--no-inherit-env` drops most inherited variables but always retains `PATH`
  and does not sandbox the command.
- `--shell <SHELL>` selects a shell when the command requires shell syntax.
  Prefer direct executable arguments when no shell expansion is needed.

Never validate by listing, getting, echoing, or serializing secrets. If a
consumer needs a live check, run the intended application command and inspect
only its non-sensitive exit status or explicitly safe metadata.
