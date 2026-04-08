# RFC 0001: Repository Shape and Distribution

**Status:** Draft
**Author:** Codex
**Date:** 2026-04-08

## Summary

This RFC defines the repository's structural contract: which directories are canonical local shared layers, which are tool-specific facades, how assets are distributed into local tool homes, and what kinds of runtime state must never be treated as canonical source.

## Motivation

The repository already spans multiple agent runtimes and mixes shared assets with tool-specific configuration. Without an explicit contract, contributors can easily create silent divergence, bury source-of-truth decisions inside one tool's prompt, or commit machine-local runtime state. This RFC operationalizes doctrine rules 1 through 7.

## Design

### 3.1 Repository Layers

The repository is divided into three logical layers:

- **Tool facades:** `.claude/`, `.codex/`, `.gemini/`, and `opencode/` contain platform-specific prompts, settings, rules, metadata, and mirrored skill entrypoints.
- **Shared authoring layers:** `skills/` is the primary shared workflow library, `skills/personal/` is the primary local operating-model layer, `agents/` is a secondary reference corpus, and repository-level docs explain the contract.
- **Support utilities:** `scripts/` and skill-local scripts/assets provide reproducible maintenance operations such as vendored bundle refreshes.

### 3.2 Source-of-Truth Rules

- Shared workflow content belongs in `skills/` by default.
- Tool skill directories such as `.claude/skills`, `.codex/skills`, `.gemini/skills`, and `.gemini/antigravity/skills` are mirrors or entrypoint surfaces, not the authored source of truth.
- Mirrored skill names are flattened by basename, so provenance must be reasoned about from the source tree rather than from the installed name alone.
- Tool namespaces may contain equivalents only when the target platform needs different metadata, formatting, or runtime semantics.
- A contributor introducing a second copy of shared logic must document which copy is authoritative, whether the content is locally authored or upstream-derived, and why the fork exists.

### 3.3 Distribution Model

- The repository is designed to be cloned or vendored as a submodule into a local machine.
- Tool-specific roots are then symlinked or copied into home-directory config locations.
- Shared skills may be copied or symlinked into tool-specific skill directories, but their authored source remains under `skills/`.
- In practice, local installation may pass through in-repo mirror surfaces such as `.claude/skills` or directly into home-directory skill paths; neither mirror layer supersedes the source tree.
- Regeneration or refresh flows must be explicit and scriptable. For example, `scripts/refresh.sh` is the supported way to rebuild the vendored Excalidraw bundle used by the personal Excalidraw skill.

### 3.4 Runtime and Local-Only State

- Secrets, caches, session traces, runtime IDs, and per-machine overrides are not canonical assets.
- When such data must live under a tool namespace for runtime reasons, it must be gitignored or otherwise excluded from the repository contract.
- Versioned baseline settings are allowed when they are portable, non-secret defaults rather than machine-private state.

### 3.5 Documentation Contract

- Top-level README material explains repository purpose and installation.
- Doctrine explains placement rules and boundaries.
- Topology explains where repository layers live and how they connect.
- OpenSpec records normative requirements so future audits can test whether the repo still matches its intended shape.

## Integration

RFC 0001 governs every top-level component:

- `skills/` is the primary cross-tool workflow layer and local mirroring source.
- `agents/` is a secondary reference corpus rather than the main execution path.
- `.claude/`, `.codex/`, `.gemini/`, and `opencode/` are adapter surfaces.
- `about/` and `openspec/` document and constrain the structure above.

## Alternatives Considered

### Put Everything in Tool Namespaces

Rejected because it makes shared content hard to discover, duplicates logic across runtimes, and couples repository organization to current tool vendors.

### Keep Only Shared Content, No Tool Facades

Rejected because target platforms use different metadata formats and runtime conventions. Thin adapters are necessary even when canonical content is shared.

### Document Structure Only in README

Rejected because README prose is too easy to drift into marketing or setup guidance. Load-bearing structure needs doctrine, RFC, topology, and spec coverage.

## V1 Scope

V1 establishes repository-level contracts and an initial specification trail. It does not attempt to write RFCs for every individual skill or agent in the repository.
