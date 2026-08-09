# Legends and Lore

Design contracts for AI Usage Telemetry.

**Status:** RFC 0001 is Draft. Its project-shape review passed; RFC-local
evidence, formal RFC review, and explicit human-owner acceptance remain. See the
central [lifecycle matrix](../README.md#lifecycle-status) and the
[`reviews/0001/`](./reviews/0001/) record.

This pillar answers how local usage facts cross tool-specific session formats,
the durable normalized ledger, and optional telemetry sinks without exposing
conversation content or depending on vendor credentials.

Reading order:

1. [`rfcs/0001-adapter-ledger-and-sink-contract.md`](./rfcs/0001-adapter-ledger-and-sink-contract.md): the v1 contracts for source adapters, normalized usage and quota facts, exact local accounting, failure isolation, and optional OTLP Metrics and PostgreSQL sinks.
2. Review rounds are recorded under [`reviews/0001/`](./reviews/0001/);
   unresolved blocking findings keep the RFC in Draft.

Relationship to the other pillars:

- [`heart-and-soul`](../heart-and-soul/README.md) defines why local facts must become user-owned history while content and credentials stay outside the collector.
- Legends-and-lore defines the load-bearing runtime, adapter, ledger, and sink contracts that preserve those principles.
- OpenSpec is currently absent and may turn the contract into testable
  capability requirements only after doctrine adoption and RFC acceptance.
- [`lay-and-land`](../lay-and-land/README.md) maps the components, mounts, data flow, and deployment boundary.
- [`craft-and-care`](../craft-and-care/README.md) governs implementation quality, verification, observability, and maintenance.

RFC 0001 is a draft. It is not accepted project law until its review findings
have explicit dispositions and the human owner accepts it.
