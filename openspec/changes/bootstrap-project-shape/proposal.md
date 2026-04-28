# Proposal: Bootstrap Project Shape

## Why

The `ai-bootstrap/` repository already contains substantial shared content and
multiple tool-specific configuration surfaces, but it had no explicit doctrine,
no repository-level RFC, no topology maps, no engineering-standards pillar, and
no normative spec describing what must remain true about its structure.

## Impact

- Adds `about/` as the repository's self-knowledge layer.
- Adds an initial repository RFC that defines structural boundaries.
- Adds a repository-specific `craft-and-care` pillar for execution-quality
  expectations.
- Adds an initial OpenSpec change with testable requirements for future audits.
- Installs project-local pillar skills that route tool-local agents back into
  canonical docs.

## Non-Goals

- This change does not reorganize repository contents.
- This change does not add per-skill RFCs or per-tool exhaustive specs.
