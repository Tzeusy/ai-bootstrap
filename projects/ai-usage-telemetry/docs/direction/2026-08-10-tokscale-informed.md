# Tokscale-Informed Project Direction

**Date:** 2026-08-10
**Baseline:** `e738ad88f89575e2a438e65fe49127f8b80c4500`
**Project:** internal local service for developers
**Maturity:** accepted pre-implementation contracts; no application code
**Comparative source:** Tokscale commit
[`9814fa49`](https://github.com/junhoyeo/tokscale/commit/9814fa49e8ba32b19d94ef2b1545b66b17944435)

Claims below use the project's `[Observed]`, `[Inferred]`, and `[Unknown]`
evidence vocabulary. Tokscale is comparative evidence, not an upstream
compatibility promise and not an implementation dependency.

## Executive Summary

[Observed] AI Usage Telemetry is trying to turn narrow local Claude Code and
Codex usage observations into durable, eventually exact, user-owned SQLite
history without admitting conversation content or credentials. Optional OTLP
and PostgreSQL sinks remain projections of that local authority. The seven
[vision principles](../../about/heart-and-soul/vision.md#non-negotiable-principles)
and the [V1 boundary](../../about/heart-and-soul/v1.md) remain coherent and
unchanged.

[Observed] The project's specification baseline is strong: five mature shape
pillars, eleven accepted capability contracts, 100 mandatory requirement IDs,
249 scenarios, and a complete Beads allocation. Implementation, behavior tests,
runtime evidence, observability, packaging, and release evidence are still
missing. Documentation readiness must not be presented as collector readiness.

[Inferred] Tokscale validates the feasibility of the basic parser and replay
problem and contributes useful test methodology. It also exposes two source-
semantics unknowns that should be resolved before domain and adapter identities
harden: progressive Claude usage snapshots and copied Codex fork history. The
highest-leverage next work is therefore the disposable synthetic thesis and a
bounded source-semantics evidence gate in parallel, followed by the existing
implementation spine.

## Project Spirit and Requirements

**Core problem:** preserve locally observable AI usage as queryable history
without converting private sessions into a surveillance dataset.

**Primary user:** a developer running one local container and querying stable
read-only ledger views.

**Success looks like:** supported observations converge exactly once into
retained SQLite facts; source and sink failures remain scoped and visible;
content and credentials are demonstrably absent; optional sinks recover from
ledger origin without becoming accounting authorities.

**Trying to be:** a narrow, evidence-gated accounting service with small
source-specific adapters and explicit failure semantics.

**Not trying to be:** a dashboard, billing calculator, cloud collector,
credential-backed quota client, broad plugin framework, or social usage
product.

| Requirement | Class | Evidence | Current status |
|---|---|---|---|
| Content and credentials never become application values | Hard | Vision principle 2; `REQ-source-adapter-profiles-002/004` | Specified, unimplemented |
| Supported observations converge exactly once | Hard | Vision principle 3; identity, ledger, and reconciliation specs | Specified, unimplemented |
| SQLite is the retained accounting authority | Hard | Vision principle 1; `REQ-durable-local-ledger-*` | Specified, unimplemented |
| Stream and sink failure remain non-masking | Hard | Vision principle 4; stream/query/sink specs | Specified, unimplemented |
| Claude and Codex V1 profiles are evidence-gated | Hard | V1 boundary; `REQ-source-adapter-profiles-001` | Accepted contract; profile evidence absent |
| Package layout, backoff, SQLite tuning, and batch sizing | Soft | RFC implementation latitude | Open to implementation evidence |
| Pricing, dashboards, extra adapters, inbound API | Non-goal/deferred | Vision and V1 deferrals | Excluded from this graph |
| Progressive Claude and copied-fork Codex semantics | Unknown | Tokscale hypotheses versus accepted source identity | Evidence gate `aib-kwx` |

### Contradictions and Unknowns

[Unknown] Tokscale treats repeated Claude `messageId:requestId` observations as
progressively complete snapshots and merges token fields by maximum
([parser rationale](https://github.com/junhoyeo/tokscale/blob/9814fa49e8ba32b19d94ef2b1545b66b17944435/crates/tokscale-core/src/sessions/claudecode.rs#L485-L490),
[merge implementation](https://github.com/junhoyeo/tokscale/blob/9814fa49e8ba32b19d94ef2b1545b66b17944435/crates/tokscale-core/src/sessions/claudecode.rs#L887-L915)).
The accepted contract treats changed accounting under `(sessionId, requestId)`
as a collision. Tokscale alone cannot resolve that conflict.

[Unknown] Tokscale explicitly tracks Codex fork ancestry and suppresses copied
parent history until the child contributes its own work
([fork state](https://github.com/junhoyeo/tokscale/blob/9814fa49e8ba32b19d94ef2b1545b66b17944435/crates/tokscale-core/src/sessions/codex.rs#L348-L450)).
The accepted Codex manifest does not project those fields. A parser-local skip
would conflict with the project's no-skip and ledger-dedup design; version-
pinned evidence must establish whether the current native identity already
makes copied observations neutral.

## Current State

| Dimension | Status | Summary | Evidence |
|---|---|---|---|
| Spec adherence | Missing implementation | No code exists to match or drift from the target contracts | [V1 status](../../about/heart-and-soul/v1.md) |
| Core workflows | Missing | Source -> domain -> SQLite -> query/sink exists only as a target flow | [data flow](../../about/lay-and-land/data-flow.md) |
| Test confidence | Missing | Test requirements are strong; no project test tree exists | [testing standard](../../about/craft-and-care/testing-and-verification.md) |
| Observability | Missing | Health vocabularies and views are specified but not executable | [operations standard](../../about/craft-and-care/observability-and-operations.md) |
| Delivery readiness | Missing | No locked package, image, CI, native evidence, or release artifact exists | [acceptance boundary](../../openspec/changes/establish-ai-usage-telemetry-v1/acceptance.md) |
| Architectural fitness | Strong target, missing implementation | One-way runtime/source/domain/ledger/reader boundaries support the intended direction | [component map](../../about/lay-and-land/components.md) |

## Alignment and Tractability Review

| Item | Alignment | Value | Leverage | Tractability | Timing | Risk | Churn |
|---|---|---:|---:|---|---|---|---|
| Reimplement full-versus-incremental differential oracles | Core/supporting | High | High | Ready under current specs | Now | Low | Low |
| Resolve Claude snapshot and Codex fork semantics | Core | High | High | Ready as bounded evidence | Now | Medium | Low before domain work |
| Execute the accepted implementation spine | Core | High | High | Ready after its evidence/dependency gates | Now/soon | High, greenfield | Medium |
| Split runtime foundation from exact candidate closeout | Supporting | Medium | Medium | Ready; independent rollback and ownership | Before runtime dispatch | Medium | Low now |
| Install or wholesale-vendor Tokscale | Misaligned | Low | Low | Requires new dependency/provenance decisions | Never in V1 | Very high | High |

### Aligned Next Steps

- Run the disposable synthetic-to-SQLite thesis (`aib-swr.1`).
- In parallel, run the content-safe producer-semantics gate (`aib-kwx`).
- Borrow Tokscale's full-versus-incremental equivalence, malformed-tail,
  compaction/replacement, fork, and hermetic-environment test motifs by
  independently implementing them under the accepted privacy and identity
  contracts.
- Continue through domain, sources, ledger/query, independent sinks, runtime,
  exact candidate closeout, and one terminal reconciliation.

### Premature or Rejected

- Do not implement per-field maxima, accept cumulative regressions, or skip
  copied fork history until producer semantics and stable identity are proved.
- Do not add an archive mount merely because Tokscale scans one; that changes
  the accepted topology and source boundary.
- Do not use Tokscale's cache as durable history, raw-prefix hashes, broad
  recursive discovery, pricing egress, credential readers, cloud/social paths,
  prompt-derived reporting, or TUI surface.
- Do not install Tokscale or copy its source into the V1 collector. If exact
  source reuse is proposed later, it must re-enter through dependency,
  licensing/provenance, privacy, and feature-amendment gates.

## Gap Analysis

| Gap | Class | Why it matters | Response | Effort |
|---|---|---|---|---|
| Claude repeated-request semantics | Blocker before domain/source identity | Wrong merge/collision behavior can lose or double count usage | Version-pinned synthetic producer evidence; amend only if confirmed | S-M |
| Codex fork/copied-history semantics | Blocker before domain/source identity | A child stream may replay parent usage under a new session ID | Public-source plus synthetic fork corpus; prove ledger-neutral identity | S-M |
| No executable collector spine | Primary delivery gap | Every user workflow is absent | Follow the accepted A-R graph | XL overall |
| No full/incremental differential evidence | Important enhancement | Cursor bugs can pass happy-path parser tests | Add independent cold/warm equivalence oracles in source work | S |
| Runtime/release packet was oversized | Planning gap | One owner could not land or roll back a coherent result in one session | Split G1 runtime foundation from G2 exact candidate closeout | M |

No OpenSpec changeset is created by this direction pass. If `aib-kwx`
confirms a contract gap, it must produce a `$th-projects` feature-amendment
handoff and remain blocking until a successor owner decision identifies exact
replacement bytes. The existing RFC, evidence 0001 artifacts, Decisions
0002/0003, and all eleven current specs remain byte-unchanged here.

## Recommended Work Plan

```text
(A aib-swr.1 synthetic thesis || S aib-kwx source evidence)
                         |
                         v
              B aib-swr.2 domain/profile foundation
                         |
                         v
              C aib-swr.3 sources/reconciliation
                         |
                         v
              D aib-swr.4 ledger/query
                         |
             +-----------+-----------+
             v           v           v
 E aib-swr.5 OTLP  F aib-swr.6 PG  G1 aib-swr.7 runtime
             +-----------+-----------+
                         |
                         v
              G2 aib-swr.9 exact candidate
                         |
                         v
              R aib-swr.8 reconciliation
```

### Chunk 1: Prove the Thesis and Source Semantics

**Objective:** retire the disposable end-to-end thesis while independently
resolving the two source-semantics unknowns.
**Spec reference:** `REQ-synthetic-usage-spine-001..006` plus evidence gate
against `REQ-source-adapter-profiles-005..010`.
**Dependencies:** accepted baseline only.
**Parallelizable:** yes; the two outcomes share no implementation surface.
**Acceptance:** `aib-swr.1` remains synthetic/disposable; `aib-kwx` returns a
closed evidence disposition and cannot silently change accepted bytes.

### Chunk 2: Establish Domain and Source Behavior

**Objective:** build source-independent exact domain/profile primitives, then
the bounded Claude/Codex adapters and reconciliation state machine.
**Spec reference:** event, quota, release-profile foundation, source-adapter,
and stream-reconciliation capabilities.
**Dependencies:** both Chunk 1 outcomes; C follows B.
**Acceptance:** behavior tests use independent byte/state oracles, synthetic
inputs, no Tokscale dependency, and no real source.

### Chunk 3: Make Local History Authoritative

**Objective:** implement the atomic SQLite ledger, stable read-only views, and
health.
**Spec reference:** durable-local-ledger and local-query-contract.
**Dependencies:** C.
**Acceptance:** replay, failure, migration, latch, storage, and unreadable-
ledger matrices execute at the real SQLite/query seams.

### Chunk 4: Add Independent Outputs and Runtime

**Objective:** implement OTLP, PostgreSQL, and the portable runtime/container
foundation as three independently reversible outcomes.
**Spec reference:** OTLP, PostgreSQL, and
`REQ-portable-runtime-and-release-001,003..008`.
**Dependencies:** D.
**Parallelizable:** yes; all consume stable upstream ports and own separate
protocol/runtime surfaces.
**Acceptance:** no sink becomes authority; G1 creates no final profile/image
digest or release claim.

### Chunk 5: Prove the Exact Candidate

**Objective:** compose immutable evidence, build exact native candidates, run
the common gate, and produce an unpublished manifest reference.
**Spec reference:** `REQ-portable-runtime-and-release-009..010` and
`REQ-release-profile-governance-001,004,005,007,009`.
**Dependencies:** E, F, and G1.
**Acceptance:** G2 alone owns final profile bytes, final child-image digests,
parity, and manifest reference; every missing or divergent input fails closed.

### Chunk 6: Falsify Completion

**Objective:** reconcile the complete codebase against all 100 IDs, 249
scenarios, and separately stated invariants.
**Dependencies:** all eight implementation outcomes.
**Acceptance:** one terminal gen-1 reconciliation (`aib-swr.8`) audits code,
tests, instruments, and cross-surface consistency; archive and publication stay
separately gated.

## Do Not Do Yet

| Item | Reason | Revisit when |
|---|---|---|
| Change accepted identity/collision semantics | Tokscale is not producer authority | `aib-kwx` produces confirmed contradictory evidence and owner accepts a successor delta |
| Read personal Claude/Codex state | Current evidence and implementation gates are synthetic-only | Exact release evidence and later owner/resource gates pass |
| Add archive roots or more adapters | New source/topology contracts are absent | A separate feature request passes doctrine, privacy, identity, and replay review |
| Publish an image or archive OpenSpec | No implementation/native/release evidence exists | G2 and R pass, followed by explicit release acceptance |
| Build dashboard, pricing, social, or credential-backed quota | Outside V1 and partly constitutionally excluded | New owner-adopted direction, where permitted |

## Evidence Index

- [Vision](../../about/heart-and-soul/vision.md)
- [V1 boundary](../../about/heart-and-soul/v1.md)
- [Data boundaries](../../about/heart-and-soul/data-boundaries.md)
- [RFC 0001](../../about/legends-and-lore/rfcs/0001-adapter-ledger-and-sink-contract.md)
- [Source and bounds evidence](../../about/legends-and-lore/evidence/0001-source-and-bounds.md)
- [Synthetic vectors](../../about/legends-and-lore/evidence/0001-synthetic-vectors.md)
- [OpenSpec proposal](../../openspec/changes/establish-ai-usage-telemetry-v1/proposal.md)
- [OpenSpec tasks](../../openspec/changes/establish-ai-usage-telemetry-v1/tasks.md)
- [Tokscale Claude parser](https://github.com/junhoyeo/tokscale/blob/9814fa49e8ba32b19d94ef2b1545b66b17944435/crates/tokscale-core/src/sessions/claudecode.rs)
- [Tokscale Codex parser](https://github.com/junhoyeo/tokscale/blob/9814fa49e8ba32b19d94ef2b1545b66b17944435/crates/tokscale-core/src/sessions/codex.rs)
- [Tokscale scanner](https://github.com/junhoyeo/tokscale/blob/9814fa49e8ba32b19d94ef2b1545b66b17944435/crates/tokscale-core/src/scanner.rs)

---

## Conclusion

**Real direction**: Build a narrow, privacy-enforced local accounting service
whose durable SQLite history and source evidence are stricter than the broad
analytics products that inspired it.

**Work on next**: Run `aib-swr.1` and `aib-kwx` in parallel; then continue
through B, C, D, E/F/G1, G2, and terminal reconciliation.

**Stop pretending**: The project has excellent accepted contracts, but it does
not yet have a collector, tests, runtime evidence, images, or release.
