# Development Doctrine

## Contribution Rules

1. Prefer editing canonical shared content before touching downstream tool-specific copies.
2. Introduce tool-specific files only when the target platform's syntax or execution model requires it.
3. Preserve provenance. If a non-`personal/` skill came from upstream, update from upstream or fork intentionally instead of silently treating the vendored copy as wholly local authorship.
4. Keep regeneration scripts with the artifacts they justify; do not hand-edit vendored outputs without updating their regeneration path.
5. Treat repository docs as part of the product. If a structural rule changes, doctrine, RFCs, and specs must move with it.
6. Preserve local-only boundaries. New runtime files belong in ignored paths unless they are deliberately portable, non-secret defaults.

## Review Questions

- Is this artifact shared across tools, or truly tool-specific?
- Is this content locally authored, upstream-derived, or an intentional fork?
- If it is generated, where is the checked-in regeneration path?
- Does this change introduce local state that should be ignored?
- Will a new contributor know where to find the authoritative version after this change?

## Anti-Patterns

- Copying a shared skill into a tool namespace and then evolving it independently without documenting the fork.
- Committing caches, logs, runtime IDs, or machine-specific settings as if they were portable config.
- Burying load-bearing repository rules inside one tool's prompt file instead of documenting them in shared docs.
