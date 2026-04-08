# Deployment

This repository is not deployed as a service. Its deployment model is local installation.

## Runtime Topology

1. A user clones `genai/` directly or includes it as a git submodule.
2. Tool-specific directories such as `.claude/`, `.codex/`, and `.gemini/` are symlinked or copied into home-directory config paths.
3. `opencode/` is installed as config under `$HOME/.config/opencode`.
4. Shared skills from `skills/` are mirrored into tool-specific skill-entrypoint directories such as `.claude/skills`, `.codex/skills`, `.gemini/skills`, and `.gemini/antigravity/skills`, then exposed to the runtime through the installed paths.
5. Agent runtimes read those installed files during interactive sessions.

## Environment Boundaries

- **Versioned repository:** canonical local source, shared documentation, reproducible scripts, and tracked baseline config.
- **In-repo mirror surfaces:** tool-specific skill directories used for local mirroring but not treated as authored source.
- **Installed local targets:** active runtime configuration surfaces under `$HOME` and `$HOME/.config`.
- **Local-only state:** caches, sessions, logs, secrets, runtime IDs, auth material, and per-machine overrides that must remain unversioned.

## Operational Implication

Changes in this repo are primarily documentation, prompt, and config changes. Verification therefore centers on structure, placement, and traceability more often than on compiling or deploying an application binary.
