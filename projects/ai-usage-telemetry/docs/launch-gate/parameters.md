# Launch-Gate Parameters: AI Usage Telemetry

**Version:** 1.2
**Status:** [Observed] Binding amended after the first administration; fresh review pending
**Bound from:** adopted [`vision.md`](../../about/heart-and-soul/vision.md) and
the th-projects universal/package-derived launch-gate instrument. Shape-corpus
details were not used to derive the questions or adversarial examples.

## Project binding

| Parameter | Binding |
|---|---|
| `PROJECT` | AI Usage Telemetry |
| `GOAL_STATEMENT` | `about/heart-and-soul/vision.md` |
| `ENTRY_DOCUMENT` | `about/README.md` |
| `CURRENT_STATE` | `about/README.md#lifecycle-status` |
| `SHAPE_CORPUS` | Accepted baseline plus explicitly pending launch remediation under `about/legends-and-lore/`, `about/lay-and-land/`, and `about/craft-and-care/`; administration is blocked until the remediation has independent review and recorded acceptance |
| `SPEC_MEDIUM` | OpenSpec under `openspec/`: accepted capability requirements in `specs/<capability>/spec.md`; active proposal/design/delta/tasks in `changes/<change>/`; requirement form and change process follow `skills/personal/th-projects/references/spec-format.md` |
| `HUMAN_DECIDER` | Tze, repository owner. Only an explicit owner directive or recorded owner decision performs an owner act. Agents may draft, review, and report gate verdicts; they cannot adopt doctrine, accept an RFC/spec, waive a gate, or expand irreversible scope. For the current task, Decision 0001 conditionally authorizes specification merge only after the recorded launch gate and required quality cycles pass. |
| `EPISTEMIC_LABELS` | `[Observed]`, `[Inferred]`, `[Unknown]` |
| `THESIS_CHECKPOINTS` | After the Synthetic-to-SQLite capability is accepted and before any sibling implementation, its disposable synthetic-only harness must produce one durable, content-free, locally queryable contribution and no second contribution on replay. Requiring content, credentials, a remote service, or weakened replay exactness falsifies the bounded thesis and reopens shape. Before release, native amd64/arm64 evidence must preserve equal normalized facts and privacy/ledger/health/projection contracts, and each optional projection must be repairable from the ledger alone; failure falsifies the portable-service thesis before release. |
| `RESOURCE_ENVELOPE` | [Observed] One human decision-maker is named and current governance work is repository-agent assisted. [Unknown] No additional human staffing, weekly-hours allocation, delivery deadline, or paid hosted-service budget is committed. V1 may assume none of them: each capability must remain bounded and independently reviewable, and any plan that requires one must stop for a new owner resource decision. |

## First specification candidate

`FIRST_SPEC_CANDIDATE` is **Synthetic-to-SQLite Usage Spine**:

> Specify one end-to-end outcome: a qualified, fully synthetic Claude Code
> 2.1.226 usage record is field-projected without materializing content,
> normalized, persisted into a disposable SQLite ledger, replayed without a
> second contribution, and visible through one read-only local usage view.

The primary acceptance boundary is one synthetic source record → one durable,
content-free, locally queryable contribution. It tests the thesis before most of
the system exists. This capability spec does not own Codex, quota, real personal
mounts, production activation, multi-stream quarantine/reconciliation,
low-space and migration recovery, complete health surfaces, container
packaging, OTLP/PostgreSQL, dashboards, billing/cost, OpenCode, or host
schedulers. Companion capability specs in the **same initial OpenSpec
changeset** own every in-v1 outcome that RFC 0001 requires before implementation
or release; excluding them from this one capability must not defer them beyond
that changeset. Each capability is independently reviewable, acceptable, or
rejectable. A rejected companion blocks implementation and release but does not
invalidate an accepted sibling capability or the thesis evidence it produces.
Once this spine is independently accepted, only its disposable, synthetic-only
thesis-test harness may be built before siblings; real source mounts, production
packaging, remote sinks, and release remain blocked.

### Prerequisites

| Prerequisite | State at binding |
|---|---|
| Adopted goal statement and data boundary | Satisfied through Owner Decision 0001; launch remediation does not amend doctrine |
| Accepted design contract for adapter/ledger/failure semantics | Pending: accepted RFC 0001 baseline remains authoritative while clarification amendments receive independent review and recorded acceptance |
| Content-safe source/bounds evidence and synthetic-vector inventory | Satisfied as specification inputs; executable release evidence remains downstream |
| Defined specification form/home/change process | Satisfied by `SPEC_MEDIUM` |
| Project-specific spec granularity and acceptance authority | Bound above and in E1 answers below; fresh v1.2 parameter review pending |
| OpenSpec directory | Explicitly waived by the launch-gate protocol and Owner Decision 0001: pre-gate absence is required, and the directory is created only after a `READY` verdict |

## D2 task-routing exercises

- `D2_ROUTINE_TASK`: Configure a human-readable local account alias for an
  existing supported source without reading credentials or native account
  identity.
- `D2_AUTHORITY_TASK`: Permit a source adapter to mount or read a credential
  store to establish account identity.
- `D2_SEAM_TASK`: Introduce a new field through source extraction, ledger
  admission, and PostgreSQL projection without treating one layer's approval as
  approval in the others.

## A3 plausible near-misses

1. **Local AI Workbench Journal:** imports local coding-assistant sessions into
   a user-owned full-text workspace with usage timelines and search, never
   sending the records to a third party.
2. **AI Plan Optimizer:** derives token history locally, joins live model prices
   and plan rules, and recommends which model/subscription minimizes the user's
   next invoice.
3. **Quota Guardian:** ignores conversation content but authenticates to each
   vendor's quota API so it can alert on live cross-tool limits when local state
   is absent or stale.

The reviewer must accept or reject each using only the adopted goal statement.

## E4 shape/spec classification candidates

1. An adapter remains unsupported when its native identity is only guessed from
   collection order, even if sample records parse successfully.
2. Enabling PostgreSQL cannot make it authoritative for retained history or
   projection repair.
3. When a Codex rate-limit-only record repeats unchanged usage counters, it
   updates eligible quota state without adding a token or request contribution.
4. When storage admission fails before a consumed-record transaction, cursor,
   ledger sequence, facts, aggregates, and sink obligations all remain unchanged
   while storage health is degraded.
5. A quota value is current only while its source-observation time remains
   within the active profile's freshness deadline.

The project answer and a random nonce are held outside the repository and the
reviewer's materials until their classifications are fixed. This parameter
block commits to the exact key bytes with SHA-256
`1f51bc4217328f3e3dbe328cca37715c21f6a481700f65c9a7ab332068b3854b`. The gate record must reveal the nonce and answer key after
comparison so any reader can verify that the administrator did not change the
answer after seeing the verdict.

## E1 project-specific specification answers

| Sub-verdict | Binding |
|---|---|
| Form | Normative MUST/SHALL requirements with stable ID, Source, Scope, and immediately adjacent WHEN/THEN scenarios per the shared spec format |
| Home | Accepted specs in `openspec/specs/`; active deltas and rationale in `openspec/changes/` |
| Granularity | One falsifiable vertical outcome with one primary acceptance boundary; Synthetic-to-SQLite Usage Spine is record → ledger → view, while every other lifecycle/source/sink/runtime outcome remains a separate capability in the same RFC-required initial changeset |
| Acceptance authority | Tze accepts or rejects each capability delta independently. An accepted Synthetic-to-SQLite spine may authorize only its disposable synthetic thesis-test harness. The initial changeset becomes accepted/archiveable, and non-synthetic implementation becomes eligible, only when every RFC-required capability is accepted; one rejection blocks that boundary without invalidating accepted siblings. For this task, the recorded conditional direction activates only after a `READY` gate, mechanical trace checks, at least four sequential th-projects/th-engineering improvement cycles with fixes between, and no unresolved blocker |
| Change process | Amend through project-feature-request/spec delta; propagate accepted shape changes to affected specs in the same change and use project-review reconciliation as a backstop |

## Goal-derived questions

- **P1 [G]** Does the first-spec candidate preserve a durable local account of
  accepted facts rather than making an optional sink the effective source of
  truth?  
  *Fails when:* a sink outage, endpoint change, or projection policy can erase,
  replace, or redefine the user's history.  
  *Doctrine basis:* `vision.md`, **1. Local Facts Become User-Owned History.**

- **P2 [G]** Does the candidate prohibit content and credentials across source
  collection, diagnostics, persistence, and export?  
  *Fails when:* any supported outcome requires decoding, retaining, or emitting
  them, including through a convenient error or enrichment path.  
  *Doctrine basis:* `vision.md`, **2. Content and Credentials Stay Outside.**

- **P3 [G]** Does the candidate make accounting eventually exact for every
  supported observable fact across rescans, crashes, and retries while refusing
  to claim unknowable pre-discovery coverage?  
  *Fails when:* a supported fact can be silently lost or counted twice, or
  unknown coverage is narrated as reconciled history.  
  *Doctrine basis:* `vision.md`, **3. Accounting Is Eventually Exact.**

- **P4 [G]** Does the candidate make source, storage, and sink failure explicit
  and scoped without masking degradation or stopping unrelated healthy paths?  
  *Fails when:* aggregate health appears successful while a stream is held/
  stale, or one failed boundary blocks unrelated collection.  
  *Doctrine basis:* `vision.md`, **4. Partial Failure Is Explicit.**

- **P5 [G]** Does the candidate preserve the narrow portable runtime boundary?  
  *Fails when:* it requires broad/writable source mounts, an auth store, host
  scheduler, inbound API, elevated runtime, or architecture-specific semantics.  
  *Doctrine basis:* `vision.md`, **6. The Runtime Boundary Is Portable and Narrow.**

## Changelog

- **1.2 (2026-08-10):** Replaced all five E4 candidates and re-sealed a wholly
  unpublished answer key after the v1.0 gate record made four old routes
  discoverable. Removed the direct no-inbound routing example, bound explicit
  thesis checkpoints and an honestly unknown resource envelope without
  amending doctrine, and limited independent pre-companion implementation to a
  disposable synthetic thesis-test harness. Questions remain unchanged.

- **1.1 (2026-08-10):** After the first `NOT READY` administration, made
  per-capability partial acceptance explicit and replaced the compound runtime
  E4 candidate with one atomic shape/spec-boundary sentence. Re-sealed the E4
  key with a new nonce and digest. Universal, package-derived, and goal-derived
  questions are unchanged; the trend records the parameter amendment.

- **1.0 (2026-08-10):** Initial child-project binding before the first
  administration. Review narrowed the first capability to one vertical outcome,
  kept all RFC-required companion capabilities in the same initial changeset,
  hardened A3, completed the shape corpus and prerequisite bindings, and moved
  the nonce-bound E4 answer outside the reviewer-readable repository. No prior
  administered parameter set exists.
