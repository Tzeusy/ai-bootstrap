# Interfaces and Dependencies

This repository's interfaces are mostly path contracts, mirrored skill names,
and adapter-specific config surfaces rather than network APIs.

## Source-of-Truth Boundaries

- Shared workflow logic belongs in `skills/`.
- `skills/personal/` is the primary locally authored workflow layer.
- Non-`personal/` skill trees keep their upstream-derived, vendored, or
  intentional-fork provenance.
- `.claude/`, `.codex/`, `.gemini/`, and `opencode/` are adapter surfaces, not
  the default home for shared logic.
- Repository-shape navigation lives in the project instruction files
  (`CLAUDE.md`, `AGENTS.md`) and the pillar READMEs, which are entrypoints
  into canonical docs, not independent sources of truth. No repo-specific
  skills go into `.claude/skills`, `.codex/skills`, or `.gemini/skills`,
  because those surfaces are the user's global catalogs on installed machines.

## Interface Hygiene

- Do not create a second copy of shared content in a tool namespace unless the
  platform genuinely requires different syntax or runtime semantics.
- If a shared artifact and a tool-specific counterpart both exist, document
  which is authoritative and why.
- Preserve the flattened skill-name constraint at install time. If provenance is
  ambiguous from the installed name alone, document the source tree that owns
  the content.
- Keep the OpenCode install contract explicit: it installs under
  `$HOME/.config/opencode`, not under `$HOME/.opencode`.

## Dependency Hygiene

- When updating submodules, vendored copies, or intentional forks, preserve the
  provenance trail instead of silently normalizing them into "local" content.
- When adding a generated asset or support script, keep the regeneration or
  refresh path checked in.
- Prefer removing stale internal compatibility layers over preserving them once
  the repository has fully migrated.
