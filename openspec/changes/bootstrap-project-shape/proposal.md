# Proposal: Bootstrap Project Shape

## Why

The `genai/` repository already contains substantial shared content and multiple tool-specific configuration surfaces, but it had no explicit doctrine, no repository-level RFC, no topology maps, and no normative spec describing what must remain true about its structure.

## Impact

- Adds `about/` as the repository's self-knowledge layer.
- Adds an initial repository RFC that defines structural boundaries.
- Adds an initial OpenSpec change with testable requirements for future audits.

## Non-Goals

- This change does not reorganize repository contents.
- This change does not add per-skill RFCs or per-tool exhaustive specs.
