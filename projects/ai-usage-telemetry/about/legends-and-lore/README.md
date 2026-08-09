# Legends and Lore

Design contracts for AI Usage Telemetry.

**Status:** RFC 0001 is accepted through Owner Decision 0001 after RFC-local
evidence and formal review. See the central
[lifecycle matrix](../README.md#lifecycle-status) and the
[`reviews/0001/`](./reviews/0001/) record.

This pillar answers how local usage facts cross tool-specific session formats,
the durable normalized ledger, and optional telemetry sinks without exposing
conversation content or depending on vendor credentials.

Reading order:

1. [`rfcs/0001-adapter-ledger-and-sink-contract.md`](./rfcs/0001-adapter-ledger-and-sink-contract.md): the v1 contracts for source adapters, normalized usage and quota facts, exact local accounting, failure isolation, and optional OTLP Metrics and PostgreSQL sinks.
2. [`evidence/0001-source-and-bounds.md`](./evidence/0001-source-and-bounds.md)
   records the content-safe source evidence and bounded release-profile decision;
   [`evidence/0001-synthetic-vectors.md`](./evidence/0001-synthetic-vectors.md)
   defines the pre-implementation evidence inventory; and
   [`evidence/0001-provenance.md`](./evidence/0001-provenance.md) pins reviewed
   clients, public source, safe commands, and unresolved structural claims.
3. Review rounds are recorded under [`reviews/0001/`](./reviews/0001/);
   unresolved blocking findings would require an amendment or successor RFC.

Relationship to the other pillars:

- [`heart-and-soul`](../heart-and-soul/README.md) defines why local facts must become user-owned history while content and credentials stay outside the collector.
- Legends-and-lore defines the load-bearing runtime, adapter, ledger, and sink contracts that preserve those principles.
- OpenSpec is currently absent and may turn the contract into testable
  capability requirements only after a `READY` launch-gate administration.
- [`lay-and-land`](../lay-and-land/README.md) maps the components, mounts, data flow, and deployment boundary.
- [`craft-and-care`](../craft-and-care/README.md) governs implementation quality, verification, observability, and maintenance.

RFC 0001 is accepted project law at the exact artifact digest recorded by Owner
Decision 0001; the formal review and later specification-authoring erratum
review preserve the digest trail. Source/resource profiles still require their
downstream evidence gates before real mounts, ingestion, exports, or a release
claim are enabled.
