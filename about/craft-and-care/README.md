# Craft and Care

Engineering standards for the `ai-bootstrap/` repository.

This pillar answers who we are when we change this repo: explicit about source
of truth, disciplined about verification, skeptical of silent divergence, and
careful with local-only state.

Read this pillar whenever work changes shared skills, tool facades, repository
structure, generated assets, or review/readiness expectations.

Reading order:

1. [`engineering-bar.md`](./engineering-bar.md): the definition of done for
   non-trivial repository changes.
2. [`testing-and-verification.md`](./testing-and-verification.md): what
   evidence is required before claiming a change is correct.
3. [`interfaces-and-dependencies.md`](./interfaces-and-dependencies.md): how
   adapter surfaces, upstream skill trees, and mirror entrypoints must be
   handled.
4. [`review-and-documentation.md`](./review-and-documentation.md): author and
   reviewer obligations, plus same-change doc-update rules.
5. [`security-and-secrets.md`](./security-and-secrets.md): local-only state and
   secret-handling boundaries for tracked tool config.

Relationship to the other pillars:

- `heart-and-soul` says why the repo exists and what boundaries are
  constitutional.
- `legends-and-lore` says how repository shape and distribution are meant to
  work.
- `lay-and-land` shows where the canonical layers, mirrors, and install targets
  live.
- `openspec/` says what repository-shape invariants must remain true.
- `craft-and-care` says how changes to all of the above must be carried out
  well.
