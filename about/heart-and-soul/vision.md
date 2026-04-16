# Vision

## What This Repository Is

`ai-bootstrap/` is the canonical local home for reusable AI-assistant operating knowledge: a skills-first shared workflow library, Beads-backed execution patterns, tool-specific configuration layers, and a smaller agent-prompt corpus kept for selective reuse. It exists so one repository can define a coherent engineering workflow and then project that workflow into multiple agent runtimes without hiding the logic inside private local state.

## What This Repository Is Not

- It is not a single-tool dotfiles dump where every platform diverges independently.
- It is not a production service or deployable runtime with a long-lived server control plane.
- It is not a cache for machine-specific secrets, session state, or one-off local experiments.
- It is not a generic prompt scrapbook with no structure, traceability, or maintenance contract.

## Non-Negotiable Rules

1. **Skills-first canonical layer:** Reusable workflow logic lives in `skills/`, with `skills/personal/` as the primary home of local operating-model customization.
2. **Thin adapters:** Tool namespaces such as `.claude/`, `.codex/`, `.gemini/`, and `opencode/` may diverge only when the target platform requires distinct syntax, metadata, or runtime behavior.
3. **Provenance stays visible:** Local mirroring source and upstream authorship are different concepts. Upstream-derived skill trees remain upstream-derived even when this repo is the local source used for installation and mirroring.
4. **Portable installation:** Repository structure must support cloning or submodule use plus symlink/copy installation into a user's home directory without bespoke hidden setup.
5. **Portable baselines, local overrides:** Shared non-secret defaults may be versioned, including curated checked-in tool config, but secrets, runtime IDs, caches, session traces, and per-machine overrides must remain outside committed canonical content or be explicitly gitignored.
6. **Reproducible generated assets:** Vendored or generated artifacts must have a documented regeneration path checked into the repository.
7. **Human-and-agent legibility:** A contributor should be able to answer "where does this belong?" and "what is authoritative?" from repository docs alone.

## Success Criteria

The repository succeeds when:

- supported tools can consume the intended configs and skills without ambiguity about source of truth;
- the Beads-centered execution path remains explicit rather than tribal knowledge;
- contributors know whether a new artifact belongs in `skills/`, a tool namespace, or the secondary `agents/` reference layer;
- upstream-derived skill content remains distinguishable from local `skills/personal/` workflow assets;
- local-only files stay out of git history; and
- repository docs make cross-tool traceability explicit enough for both humans and LLM agents.
