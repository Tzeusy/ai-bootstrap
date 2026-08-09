# Topology Assets

The first project-shape pass keeps its diagrams as Mermaid inside the topology
documents so the source and argument stay together.

Current topology sources and governing crosslinks:

- [`../components.md`](../components.md) contains the system context and
  component-ownership diagram.
- [`../data-flow.md`](../data-flow.md) contains the record, ledger, and
  independent-sink flow diagram.
- [`../deployment.md`](../deployment.md) defines the mount, network, runtime,
  persistence, and multi-architecture placement those diagrams assume.
- [`../README.md`](../README.md) indexes the complete topology pillar and links
  its adopted [doctrine](../../heart-and-soul/README.md) and accepted
  [RFC 0001](../../legends-and-lore/rfcs/0001-adapter-ledger-and-sink-contract.md)
  authorities.

If a later diagram becomes too dense for Mermaid, store its editable
`.excalidraw` source and rendered SVG here. Record the generating script or
command, date, and governing topology document; never check in an orphaned
render with no reproducible source.
