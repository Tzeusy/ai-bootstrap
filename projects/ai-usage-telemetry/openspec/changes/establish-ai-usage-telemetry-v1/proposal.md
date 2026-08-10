## Why

Developers have local AI-tool usage facts but no durable, content-free account
that survives source deletion, retries, or optional-sink failure. The accepted
project shape is ready to become testable capability contracts: launch gate
[`2026-08-10-96ba99d.md`](../../../docs/launch-gate/2026-08-10-96ba99d.md)
recorded `READY` against commit
`96ba99dda1503e2f278df9b76abd3c5872faa8fd`, with an empty E3 reopen list.

R1-R5 converged on exact reviewed HEAD
`e2bb9ea78984878c6e06a9e37946f923032150f9`; R5 returned
`APPROVED_FOR_PROMOTION` with findings `0 / 0 / 0`. Owner
[Decision 0002](../../../about/heart-and-soul/decisions/0002-accept-v1-capability-contracts.md)
independently accepted all eleven exact R5 contract rows. A later final branch
review found bounded numeric/time representation gaps in four rows; exact-head
confirmation approved their corrections with findings `0 / 0 / 0`, and
[Decision 0003](../../../about/heart-and-soul/decisions/0003-accept-final-branch-contract-corrections.md)
replaces only those four bindings. The [acceptance projection](./acceptance.md)
records the composed eleven-row accepted set. No capability is implemented,
and this change is neither archived nor release-authorized.

## What Changes

- Define the first independently acceptable Synthetic-to-SQLite Usage Spine
  and its human legibility checkpoint.
- Specify deny-by-default Claude Code and Codex source-profile activation,
  source-faithful normalization, identity, replay, reconciliation, and quota
  behavior.
- Specify the durable SQLite authority, stable local query surface, explicit
  health, storage/recovery behavior, and indefinite retained history.
- Specify independent bounded OTLP Metrics and idempotent PostgreSQL projections.
- Specify the immutable release-profile evidence gate and portable,
  multi-architecture, non-root container boundary.
- Keep all application implementation, real personal-source activation, remote
  export, and release evidence outside this documentation changeset.

## Capabilities

### New Capabilities

- `synthetic-usage-spine`: One qualified synthetic Claude record becomes one
  durable, content-free, locally queryable contribution; replay is neutral and
  a bounded developer exercise tests whether the result is legible.
- `source-adapter-profiles`: Claude Code and Codex extraction manifests,
  discriminators, context rules, unsupported-profile holds, and version-pinned
  activation evidence.
- `event-identity-and-normalization`: Cross-source logical identity,
  accounting fingerprints, source times, attribution, token categories, and
  unique usage-request contributions.
- `stream-reconciliation-and-health`: Source discovery, cursor/anchor rules,
  rescans, quarantine, coverage/retention gaps, freshness, and non-masking
  component health.
- `durable-local-ledger`: SQLite schema authority, per-record atomicity,
  constraints, migrations, storage admission, indefinite retention,
  maintenance, backup, and privacy-repair boundaries.
- `quota-snapshot-semantics`: Source capability availability, canonical
  utilization, window identity, observation/collection time, freshness, and
  deterministic current-snapshot selection.
- `local-query-contract`: Stable read-only usage, amount, quota, source-health,
  sink-health, and ledger-health views, plus the versioned non-networked
  read-only structured-health JSON inspection contract, with compatibility
  rules.
- `otlp-metrics-projection`: Cumulative instruments, full series identity,
  allowlisted vocabularies, cardinality budgets, leased checkpoints, catch-up,
  retry, and schema evolution.
- `postgresql-history-projection`: Idempotent event/amount/quota history,
  allowlisted metadata, event time, transactional checkpoints, and catch-up.
- `release-profile-governance`: Immutable profile ID/digest, domain profile
  membership, measurement/evidence gates, compatibility, activation, and
  fail-closed release behavior.
- `portable-runtime-and-release`: Canonical mounts, configuration/secrets,
  privilege/filesystem/network isolation, disabled-sink non-instantiation,
  locked inputs, and native amd64/arm64 parity gates.

Each capability is an independently reviewable delta. The owner may accept or
reject each one without erasing sibling decisions. A rejected or unknown
required capability blocks archival, every non-synthetic implementation path,
real-source mounting or fact acceptance, sink delivery, and release; archival
requires explicit owner acceptance of all eleven. Domain capabilities own their
exact values and executable evidence. `release-profile-governance` only
composes accepted domain evidence into immutable profile identity,
compatibility, activation, and fail-closed authorization.

### Modified Capabilities

None. This is the project's first capability changeset.

## Impact

- Adds the first `openspec/` capability pillar for
  `projects/ai-usage-telemetry`; no application package exists or is created.
- Binds every requirement upward to adopted doctrine and the exact RFC/spec
  bytes authorized by the central lifecycle matrix and owner decisions; no
  linked artifact promotes itself.
- Establishes the complete initial changeset required before non-synthetic
  implementation, real mounts, sinks, or release can be authorized.
- The Synthetic-to-SQLite capability remains independently acceptable and may
  later authorize only a disposable synthetic-only thesis-test harness. That
  harness reads no real source mount, accepts no non-synthetic fact, opens no
  network or sink path, ships no production package, and creates no reusable
  production shortcut. It authorizes no real collection, sink delivery, or
  release, and no authorization is exercised here.
