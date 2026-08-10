# Lay and Land

Topology for AI Usage Telemetry. These maps describe the independently
**Accepted** target state derived from adopted doctrine and the RFC 0001 design
contract. The exact-byte authority of the linked RFC is external to these maps
and follows the central [lifecycle matrix](../README.md#lifecycle-status).
The maps remain **[Inferred]** pre-implementation topology and must be
reconciled when implementation evidence exists.

| Map | Read when |
|---|---|
| [`components.md`](./components.md) | Locating component ownership and dependency boundaries |
| [`data-flow.md`](./data-flow.md) | Tracing usage or quota data through validation, durable state, and delivery |
| [`deployment.md`](./deployment.md) | Building or operating the container and its mounts, network, and state volume |
| [`assets/README.md`](./assets/README.md) | Finding diagram sources and their governing topology crosslinks |

The maps implement the doctrine in
[`heart-and-soul/vision.md`](../heart-and-soul/vision.md) and depict the
contract in
[`RFC 0001`](../legends-and-lore/rfcs/0001-adapter-ledger-and-sink-contract.md).
If the map and contract disagree, treat that as documentation drift and resolve
the governing decision before implementation.
