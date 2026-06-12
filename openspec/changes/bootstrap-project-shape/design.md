# Design

## Approach

Bootstrap the five-pillar shape with repository-level documents plus
instruction-file routing for in-repo sessions:

- doctrine for identity, boundaries, and contribution rules;
- engineering standards for verification, review, interface hygiene, and
  local-only state discipline;
- one repository RFC for layer boundaries and distribution flow;
- topology maps for major components and data movement; and
- one OpenSpec domain covering repository-shape invariants.

## Traceability

- Doctrine rules D1-D7 are defined in `about/heart-and-soul/vision.md`.
- `about/craft-and-care/` defines the repository's execution-quality bar for
  shape changes.
- RFC 0001 translates those rules into a concrete repository contract.
- The repository-shape spec converts the contract into testable requirements and
  scenarios.

## Risks

- Repository shape docs can become aspirational if not tied to current structure.
- Tool-specific drift can reappear if future changes bypass the shared source-of-truth model.

## Mitigation

- Keep the first RFC narrowly focused on current top-level structure.
- Use scenarios that can be audited from the filesystem and docs.
