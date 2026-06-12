# Lay and Land

Topology for the `ai-bootstrap/` repository.

This pillar answers where repository structure becomes operational: which paths are canonical source, which are mirrors, which are installed runtime destinations, and which paths are deliberately local-only.

- [`components.md`](./components.md): major repository zones, ownership boundaries, and tracked-vs-local state splits.
- [`data-flow.md`](./data-flow.md): how authored content becomes mirrored or installed runtime configuration, plus how generated assets are refreshed.
- [`deployment.md`](./deployment.md): where this repository lives on disk and how each tool consumes it.
- [`assets/README.md`](./assets/README.md): conventions for future diagram sources, rendered outputs, and regeneration metadata.

Relationship to the other pillars:

- [`heart-and-soul`](../heart-and-soul/README.md) doctrine says why the canonical/mirror/local-only boundaries exist.
- [`legends-and-lore`](../legends-and-lore/README.md) RFC 0001 is the contract these maps depict; if a map and the RFC disagree, treat it as drift to fix.
- [`openspec/`](../../openspec/) states the testable requirements the mapped layout must keep satisfying.
- [`craft-and-care`](../craft-and-care/README.md) defines how changes to the mapped structure must be verified.
