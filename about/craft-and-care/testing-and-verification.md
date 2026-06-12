# Testing and Verification

Verification in this repository is mostly about proving structure,
traceability, and reproducibility rather than compiling an application binary.

## Evidence Scales With Risk

| Change type | Minimum evidence |
|-------------|------------------|
| Doctrine, RFC, topology, or spec edits | Cross-read the affected pillars and confirm they still agree on naming, boundaries, and source-of-truth rules |
| `SKILL.md` or local skill routing edits | Validate YAML frontmatter, direct file references, and trigger wording; confirm the skill routes back to canonical docs instead of duplicating them |
| Scripts or generated artifacts | Run the targeted script, dry run, or self-test when available; do not hand-edit generated outputs without checking the regeneration path |
| Tool-facade or mirror changes | Confirm the canonical source is still obvious, mirror names still match the intended source, and local-only ignored state was not promoted into tracked content |

## Required Posture

- If you touch a verification script, run it.
- If you change a structural contract, re-read the affected doctrine, RFC, spec,
  and local skill surfaces together.
- If a bug fix closes a drift or routing problem, include evidence that the same
  drift will be caught or prevented next time.
- If you cannot run the expected verification, say so explicitly and state what
  remains unproven.

## Repository-Specific Checks

- Shape language should agree across `about/README.md`, `about/`, RFC 0001, and
  the repository-shape spec.
- In-repo shape-navigation routes (`CLAUDE.md`, `AGENTS.md`, pillar READMEs)
  should stay thin and point to real files in `about/` or `openspec/`.
- Mirror surfaces should never become the only place a rule or workflow is
  documented.
