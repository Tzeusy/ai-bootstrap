# Data Flow

**Status:** Accepted, **[Inferred]** target-state flow, grounded in the
**[Observed]** local record shapes described in
[`RFC 0001`](../legends-and-lore/rfcs/0001-adapter-ledger-and-sink-contract.md).

## Usage and Quota Flow

```mermaid
flowchart TD
    AA[Authorize profile] --> AB[Runtime validation<br/>ValidatedSourceHandle]
    AB --> AC[Storage preflight<br/>AdmissionDecision permitted]
    AC --> AD[Generic stay-beneath discovery<br/>adapter filename predicate]
    AD --> A[Scan next source-stream record]
    Z -->|Yes, with or without newline| F[Quarantine stream\nhold cursor before record]
    Z -->|No| B{Complete record?}
    B -->|No: bounded incomplete tail| C[Hold stream cursor\nwait for later cycle]
    B -->|Yes| D{Record kind classification}
    D -->|registered_irrelevant / context_only / quota_state_only| E[Zero-fact ledger transaction\nwith permitted transition]
    D -->|Unknown / unregistered / malformed| F[Quarantine stream\nhold cursor before record]
    D -->|Registered usage or quota| G[Field-project with code-owned extraction registry]
    G --> H{Schema and arithmetic valid?}
    H -->|No: malformed| F
    H -->|Yes| I[Invoke source-independent domain<br/>instant + cwd + category + age]
    I --> J[Build UsageEvent / QuotaSnapshot<br/>identity + fingerprint]
    J --> K{Ledger identity exists?}
    K -->|Same fingerprint| L[Validated replay]
    K -->|New identity| M[Transactional ledger insert]
    K -->|Different fingerprint| F
    E --> N[Commit stream cursor]
    L --> N
    M --> O[Update aggregates + stream cursor + sink work]
    O --> P[Commit SQLite transaction]
    N --> P
    P --> Q[Stable read-only SQLite views]
    P --> PR[LedgerProjectionReader]
    PR --> R[Independent OTLP projection + delivery]
    PR --> S[Independent PostgreSQL projection + delivery]
    R --> T{OTLP durable acknowledgement?}
    S --> U{PostgreSQL durable acknowledgement?}
    T -->|No| V[Retain OTLP pending state]
    U -->|No| W[Retain PostgreSQL pending state]
    T -->|Yes| X[Advance OTLP checkpoint]
    U -->|Yes| Y[Advance PostgreSQL checkpoint]
```

## Trust-Boundary Transitions

1. **Untrusted mount → validated stream entry.** Runtime returns
   `ValidatedSourceHandle` only after canonical mount/path checks. Generic
   discovery consumes the handle, performs regular-file/non-symlink
   stay-beneath traversal and generation, and applies the adapter-owned filename
   predicate. Adapters implement neither runtime validation nor discovery.
2. **Validated entry → normalized record.** The parser requires an injected
   ledger/storage `AdmissionDecision=permitted`, decodes only paths in the
   adapter-owned extraction registry, and supplies registered source
   fields/evidence to source-independent domain interfaces. Those interfaces
   alone construct `UsageEvent`/`QuotaSnapshot`, identity, canonical instant,
   cwd basename, categories, fingerprint, and age. Prompt/response content and
   credentials have no normalized representation and are skip-only.
3. **Normalized record → durable ledger.** Identity, record data, cursor,
   aggregates, and sink-pending state change in one SQLite transaction. Identity
   and the accounting fingerprint exclude cursor positions and export/config
   choices. A crash before commit changes nothing; a crash after commit is
   replayable.
4. **Ledger → local query.** Stable public views branch directly from committed
   ledger state for local users and structured health.
5. **Ledger → OTLP.** `LedgerProjectionReader`, not a public view/private-table
   query, supplies committed projection input. The projection deliberately drops event/session
   identifiers, raw paths, and unbounded metadata. Only dimensions and finite
   values in the OTLP attribute/vocabulary registry cross this boundary.
6. **Ledger → PostgreSQL.** `LedgerProjectionReader`, not a public view/private-
   table query, supplies stable normalized columns and metadata selected by the
   PostgreSQL allowlist. Delivery and its checkpoint are independent from OTLP.

## Source-Specific Context

- **[Observed/Inferred] Claude Code family:** one assistant usage observation
  can appear on repeated physical records. The versioned adapter deduplicates by
  an evidence-backed native identity instead of counting JSONL lines. Claude
  quota remains `unknown/unavailable`; its credential-bearing global state is
  not mounted.
- **[Observed/Inferred] Codex family:** token-count state does not carry all
  attribution fields and may repeat the previous contribution on a
  rate-limit-only update. Each stream applies the latest preceding turn context
  and emits usage only for validated cumulative advancement. Parser context
  persists with that stream's cursor and never crosses into another stream.
- **[Unknown] Future adapter:** admission requires a stable content-free event
  identity, source-time semantics, and quota capability decision. A cloud-only
  dashboard is not silently treated as a local adapter.

## Failure Paths

- An incomplete final JSONL record below the active byte cap waits for a later
  cycle with its stream cursor held. Crossing the cap without a newline is an
  immediate `record_limit` quarantine, not an indefinitely deferred tail.
- Only `registered_irrelevant`, `context_only`, or `quota_state_only` may advance
  a complete record with zero facts, and only when its permitted parser-context
  or quota-component transition and cursor commit in the same ledger
  transaction.
- A missing required profile member or bound is `unsupported_profile` before
  traversal; a missing or wrongly typed required projected record value is
  `recognized_malformed`; only measured bound overflow is `record_limit`.
- An unknown kind or malformed/semantically inconsistent complete record
  quarantines only its stream, leaves its cursor before the record, and emits a
  degraded signal that family/global summaries do not mask.
- A failed sink retains its own pending work; the other sink continues.
- A poll cycle never marks stale quota data fresh merely because the collector
  reread it.
- Missing quota data is unavailable or stale, never zero utilization.
