# Launch-Gate Parameters: AI Usage Telemetry

**Version:** 1.0  
**Status:** Reviewed binding; one review pass and one confirming pass completed  
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
| `SHAPE_CORPUS` | Accepted shape under `about/legends-and-lore/`, `about/lay-and-land/`, and `about/craft-and-care/` |
| `SPEC_MEDIUM` | OpenSpec under `openspec/`: accepted capability requirements in `specs/<capability>/spec.md`; active proposal/design/delta/tasks in `changes/<change>/`; requirement form and change process follow `skills/personal/th-projects/references/spec-format.md` |
| `HUMAN_DECIDER` | Tze, repository owner. Only an explicit owner directive or recorded owner decision performs an owner act. Agents may draft, review, and report gate verdicts; they cannot adopt doctrine, accept an RFC/spec, waive a gate, or expand irreversible scope. For the current task, Decision 0001 conditionally authorizes specification merge only after the recorded launch gate and required quality cycles pass. |
| `EPISTEMIC_LABELS` | `[Observed]`, `[Inferred]`, `[Unknown]` |

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
that changeset.

### Prerequisites

| Prerequisite | State at binding |
|---|---|
| Adopted goal statement and data boundary | Satisfied through Owner Decision 0001 |
| Accepted design contract for adapter/ledger/failure semantics | Satisfied through RFC 0001 formal review |
| Content-safe source/bounds evidence and synthetic-vector inventory | Satisfied as specification inputs; executable release evidence remains downstream |
| Defined specification form/home/change process | Satisfied by `SPEC_MEDIUM` |
| Project-specific spec granularity and acceptance authority | Bound above and in E1 answers below |
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

1. Accepted local facts remain in SQLite indefinitely; optional sinks never
   become the history authority.
2. Content and credentials may not be decoded, materialized, logged, retained,
   or exported.
3. Replaying an already accepted source event must not create another normalized
   token or request contribution.
4. An unknown or malformed complete record must quarantine only its affected
   stream while healthy streams continue and aggregate health remains degraded.
5. The collector is one non-root long-running container with a five-minute
   default poll and no inbound port.

The project answer and a random nonce are held outside the repository and the
reviewer's materials until their classifications are fixed. This parameter
block commits to the exact key bytes with SHA-256
`4f38f814de67238ddc4d84518149ebcc7344b148a35c4e15ce9bb38fe36ac610`. The gate record must reveal the nonce and answer key after
comparison so any reader can verify that the administrator did not change the
answer after seeing the verdict.

## E1 project-specific specification answers

| Sub-verdict | Binding |
|---|---|
| Form | Normative MUST/SHALL requirements with stable ID, Source, Scope, and immediately adjacent WHEN/THEN scenarios per the shared spec format |
| Home | Accepted specs in `openspec/specs/`; active deltas and rationale in `openspec/changes/` |
| Granularity | One falsifiable vertical outcome with one primary acceptance boundary; Synthetic-to-SQLite Usage Spine is record → ledger → view, while every other lifecycle/source/sink/runtime outcome remains a separate capability in the same RFC-required initial changeset |
| Acceptance authority | Tze accepts a changeset. For this task, the recorded conditional direction activates only after a `READY` gate, mechanical trace checks, at least four sequential th-projects/th-engineering improvement cycles with fixes between, and no unresolved blocker |
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

- **1.0 (2026-08-10):** Initial child-project binding before the first
  administration. Review narrowed the first capability to one vertical outcome,
  kept all RFC-required companion capabilities in the same initial changeset,
  hardened A3, completed the shape corpus and prerequisite bindings, and moved
  the nonce-bound E4 answer outside the reviewer-readable repository. No prior
  administered parameter set exists.
