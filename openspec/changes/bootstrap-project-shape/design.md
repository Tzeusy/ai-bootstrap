# Design

## Approach

Bootstrap the four-pillar shape with repository-level documents only:

- doctrine for identity, boundaries, and contribution rules;
- one repository RFC for layer boundaries and distribution flow;
- topology maps for major components and data movement; and
- one OpenSpec domain covering repository-shape invariants.

## Traceability

- Doctrine rules D1-D7 are defined in `about/heart-and-soul/vision.md`.
- RFC 0001 translates those rules into a concrete repository contract.
- The repository-shape spec converts the contract into testable requirements and scenarios.

## Risks

- Repository shape docs can become aspirational if not tied to current structure.
- Tool-specific drift can reappear if future changes bypass the shared source-of-truth model.

## Mitigation

- Keep the first RFC narrowly focused on current top-level structure.
- Use scenarios that can be audited from the filesystem and docs.
