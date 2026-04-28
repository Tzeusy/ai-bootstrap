# Security and Secrets

The main security risk in this repository is accidentally treating local runtime
state as portable tracked configuration.

## Never Commit As Canonical Content

- secrets, tokens, OAuth material, or private credentials;
- runtime IDs, installation IDs, account files, caches, logs, and session
  traces;
- machine-specific project entries, private absolute paths, or workstation-only
  overrides unless they are intentionally local and ignored.

## Standards

- Prefer local-only files or secret-manager wrappers when commands need
  credentials; do not bake secrets into shared config or checked-in examples.
- If a tool writes private state inside `.claude/`, `.codex/`, `.gemini/`, or
  `opencode/`, document the boundary but do not promote the file into tracked
  baseline config unless it is a portable non-secret default.
- Scrub examples, fixtures, and docs of sensitive values before committing them.
- When in doubt, treat data as local until it is proven portable, non-secret,
  and useful as a shared default.
