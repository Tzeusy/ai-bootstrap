# RFC 0001 Project-Shape Review

**Date:** 2026-08-10

**Scope:** Doctrine, RFC 0001, topology, and engineering-standard coherence

**Reviewed RFC SHA-256:** `975f5e0c63651b1411169f83159fc09c6135b2c80e00519a3d2a4c1b1c396b7d`

**Result:** PASS for the project-shape documentation slice; RFC remains Draft

This record captures independent design review of the first authored project
shape. It is not human-owner acceptance and does not authorize OpenSpec or
implementation. The digest identifies the rechecked RFC after every finding
below was resolved.

## Review sequence

The initial uncommitted author draft received two independent, non-ratifying
exploratory reviews: one cross-pillar coherence pass and one adversarial RFC/
privacy/accounting pass. That pre-record draft did not have a stable digest and
was never proposed for acceptance. Their blocking findings were applied before
the current reviewed artifact was frozen.

A fresh reviewer then read every Markdown document and checked the integrated
shape. Its first pass returned six remaining findings. After the dispositions
below, the same reviewer rechecked only those findings against the digest above
and returned PASS with no remaining blocker.

## Exploratory findings and dispositions

| Finding | Disposition | Evidence in the reviewed draft |
|---|---|---|
| Mixed-content parsing did not make “content stays outside” executable. | **Accepted.** Replaced general object parsing with a code-owned, field-projecting streaming contract, hard limits, safe diagnostics, and non-materialization sentinels. | RFC, “Mixed-Content Streaming Field Projection”; craft privacy and verification standards |
| Unknown records could be consumed and lost. | **Accepted.** Only registered irrelevant kinds may advance without a fact; unknown and recognized malformed records hold and quarantine their stream. | RFC, “Incremental Reads, Rescans, and Quarantine”; topology failure flow |
| Cursor state could miss replacement, pre-cursor mutation, or stale Codex context. | **Accepted.** Added generation, offset, safe prefix anchor, parser context, validation, clean rescans, and periodic reconciliation. | RFC, “Incremental Reads, Rescans, and Quarantine” |
| Event, request, quota, and PostgreSQL identities were under-scoped. | **Accepted.** Added immutable technical namespaces, complete request/quota subject keys, versioned accounting fingerprints, and mandatory relational constraints/transactions. Aliases are projection-only. | RFC, normalized facts, source attribution, ledger, and PostgreSQL sections |
| Extraction, retention, sink allowlists, and fingerprint policy were conflated. | **Accepted.** Separated the code-owned extraction registry, closed ledger schema, PostgreSQL projection allowlist, and bounded OTLP attribute/vocabulary policy. | RFC, “Privacy and Cardinality Budget”; doctrine data boundaries |
| OTLP cumulative delivery lacked reset, writer, and numerical-cardinality semantics. | **Accepted.** Added ledger epoch/start time, cumulative monotonic sums, fenced single-writer lease, at-least-once delivery, provisional value/series ceilings, and schema evolution. | RFC, “OTLP Metrics Projection” |
| Sink checkpoints and late enablement lacked destination identity and ordering. | **Accepted.** Added `ledger_seq` and destination/projection/epoch-scoped checkpoints with independent origin catch-up. | RFC, ledger and sink-independence sections |
| Local-ledger-only mode promised queryable history without a stable query/health interface. | **Accepted.** Added sink-independent read-only SQLite views and a non-networked structured inspection command. | RFC, “Health and Freshness State”; doctrine and craft interface documents |
| Runtime, mounts, credentials, and network boundaries were policy prose only. | **Accepted.** Added fixed targets, no-symlink/broad-parent checks, non-root/read-only-root controls, no ports, local-only no-network mode, sink egress limits, and locked dependencies. | RFC runtime section; deployment topology; security standard |
| Indefinite retention lacked source-deletion, low-disk, maintenance, and privacy-repair semantics. | **Accepted.** Defined exactness over accepted observations, non-retraction, lossless maintenance, atomic storage holds, and narrow owner-authorized privacy repair. | RFC, “Retention, Maintenance, and Storage Pressure” |
| Topology hid independent sink paths and stream-level failure. | **Accepted.** Redrew independent projectors/delivery/checkpoints and standardized source family, source stream, and record vocabulary with non-masking summaries. | `lay-and-land/components.md` and `data-flow.md` |
| Lifecycle language claimed approval before owner ratification. | **Accepted.** Added one Draft/Proposed/Absent matrix and made OpenSpec conditional on doctrine adoption and RFC acceptance. | top-level `about/README.md` |
| Multi-architecture intent lacked parity evidence. | **Accepted.** Required one manifest and native parity gates for normalization, fingerprints, schema, privacy, runtime, and sink payloads. | RFC integration; craft verification; deployment topology |

## Fresh integrated-review findings and dispositions

| Finding | Disposition | Evidence in the reviewed draft |
|---|---|---|
| OpenSpec was both forbidden before RFC acceptance and required to supply pre-review quota fixtures. | **Accepted.** The pre-review dependency is now an RFC-local evidence annex and synthetic vectors; OpenSpec remains downstream. | RFC Claude quota section; lifecycle matrix |
| Secondary request and quota identities still admitted aliases or incomplete scope. | **Accepted.** Request and quota-subject keys now carry immutable collector, ledger, adapter, and source namespaces; aliases are projection-only. | RFC `UsageEvent`, `QuotaSnapshot`, and Claude quota sections |
| Public SQLite view names differed across pillars. | **Accepted.** All pillars now use `usage_events`, `usage_event_amounts`, `quota_snapshots`, `source_health`, `sink_health`, and `ledger_health`. | RFC health section; doctrine and craft interface documents |
| Fixture policy alternated between synthetic-only and redacted real inputs. | **Accepted.** All fixture guidance now requires fully synthetic data without copied source values. | craft privacy, testing, and interface documents; deployment topology |
| A Draft RFC called itself authoritative. | **Accepted.** Authority is explicitly conditional on owner acceptance. | RFC integration; lifecycle matrix |
| Exact parser, rescan, and cardinality limits lacked evidence. | **Accepted.** The mechanisms remain mandatory, while current numbers are Draft-provisional and require an evidence annex before acceptance. | RFC parser, reconciliation, and OTLP sections |

## Verification evidence

- `shape-scan.sh projects/ai-usage-telemetry` reports an authored, four-pillar
  `STRUCTURED` shape; OpenSpec is intentionally absent at this lifecycle stage.
- Every relative Markdown link resolves.
- Markdown fence balance and trailing-whitespace checks pass.
- Exact doctrine principle titles remain unchanged and trace into RFC decisions.
- No scaffold markers, private registry coordinates, secrets, or personal
  absolute paths are present.

## Remaining authority gates

1. Produce the RFC-local source-evidence annex and synthetic vectors for the
   Claude quota cache and the provisional parser/reconciliation/cardinality
   numbers.
2. Run formal RFC privacy, accounting, and operational review against that
   evidence and record its dispositions here.
3. Obtain explicit human-owner adoption of doctrine and acceptance of RFC 0001.
4. Only then author OpenSpec capabilities and local pillar navigation skills.
