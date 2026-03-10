# Bitwarden Secrets Manager CLI reference

Use this reference when you need detailed subcommand behavior or authentication setup. Keep guidance aligned with the official documentation:
https://bitwarden.com/help/secrets-manager-cli/

## Must-use wrapper

Wrap processes that need secrets so values are injected into the process environment:

```
bws run --project-id ${BWS_TZEHOUSE_ID_PROD} -- {command}
bws run --project-id ${BWS_TZEHOUSE_ID_DEV} -- {command}
```

## Safe usage notes

- Do not print secrets or write them to disk.
- Do not hardcode project IDs; use the provided environment variables.
- Prefer short-lived, command-scoped secret injection via `bws run`.
