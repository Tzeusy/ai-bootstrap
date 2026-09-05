# Candidate Evidence 0002: Claude Snapshot and Codex Fork Semantics

**Status:** Candidate evidence; non-normative and not accepted
**Date:** 2026-08-12
**Scope:** aib-kwx only
**Artifact class:** about/legends-and-lore/evidence/ candidate evidence
**Reader:** accepting owner, successor-change author, and independent privacy/accounting reviewers
**Retirement:** Retain immutable history until a successor owner decision either accepts replacement evidence/contract bytes or rejects this candidate. Link that successor from the governing RFC; do not rewrite this record.

This record resolves the source-semantics inquiry without changing any accepted RFC, OpenSpec, evidence, or decision bytes. It uses only public source, executable version/hash metadata, and hand-authored structural fixtures. It does not open a personal session, authentication store, credential, broad home/config root, real source mount, sink, or client network path. Tokscale is comparative only and was not downloaded or executed.

## Disposition and hard gate

| Subject | Evidence disposition | Effect on the current accepted contract |
|---|---|---|
| Claude Code 2.1.227 progressive usage snapshots under (sessionId, requestId) | **Unresolved.** Public documentation confirms session JSONL and partial streaming output, but not repeated persisted usage-bearing records under one native identity. No isolated producer run was authorized here. | The build remains unsupported for this unproved behavior. A producer-confirmed progressive snapshot would contradict the current same-identity-change collision rule and require the successor route below. |
| Codex 0.147.0 copied fork history | **Confirmed contract gap.** The pinned public source copies fork history into a fresh child rollout, writes child session metadata before pending copied items, and keeps the copied prefix for the child. | The accepted Codex native identity (session_meta.payload.id, cumulative landmark) distinguishes parent and child copies even when they represent one inherited contribution. That is not ledger-neutral and cannot be repaired by a parser-local skip. |

**Hard gate:** Do not activate or implement the Codex adapter/accounting profile in aib-swr.3, nor revise source-independent identity behavior in aib-swr.2, until a successor owner decision accepts exact replacement bytes and required independent PR-stage reviews pass. Claude remains unsupported_profile for progressive-snapshot behavior until the exact build has content-free producer confirmation. This candidate does not draft an amendment or choose a replacement identity rule.

## Reproducible identity pins

| Subject | Pin | Safe observation |
|---|---|---|
| Claude Code | 2.1.227; executable SHA-256 6832dc3f1797b890b71116e5f2dbbf9a83fd3d0498c235b4b0f9cd0e6e499ad6 | claude --version; sha256sum "$(command -v claude)" |
| Codex executable | codex-cli 0.147.0; executable SHA-256 cb0a15567e9a60a5820d54b0f6ae86d504dc3805c1eab21a47f70e3eb7b73a40 | codex --version; sha256sum "$(command -v codex)" |
| Codex public source | Annotated tag rust-v0.147.0; tag object 3ed6f04f6bf8b7c46299d1cb1ff99c74ce21a51d; peeled commit be6e8eac029b183056b7e4402879f15d2c85f61b | git ls-remote https://github.com/openai/codex.git refs/tags/rust-v0.147.0 'refs/tags/rust-v0.147.0^{}' |
| Tokscale | 9814fa49e8ba32b19d94ef2b1545b66b17944435 | Comparative-only reference from the issue packet; no installation, download, or execution. |

The local executable identities identify reviewed artifacts only. They do not claim that a private on-disk format is an upstream compatibility promise.

## Version-pinned observations

### Claude: explicit unresolved boundary

The [session documentation](https://code.claude.com/docs/en/sessions) says that local sessions use JSONL, and the [CLI documentation](https://code.claude.com/docs/en/cli-usage) describes partial streamed output. Neither establishes that version 2.1.227 persists multiple usage-bearing assistant observations sharing one (sessionId, requestId), nor whether a change in those observations is a producer-defined progressive snapshot rather than malformed reuse.

The accepted contract currently treats a same identity with a changed timestamp, message identity, model, or amount as a collision. The structural cases keep these possibilities distinct:

- exact replay is a duplicate;
- unconfirmed monotone and non-monotone changes are unresolved and admit no replacement fact;
- an incomplete decreasing observation remains an incomplete-tail hold;
- unconfirmed identity reuse remains a collision; and
- a counterfactual producer-confirmed monotone progression exposes the precise contract gap without claiming that it occurred.

**Claude falsifier / next admissible evidence:** A disposable isolated producer run of this exact binary must show, with a fake configuration root, fake credential, loopback-only synthetic transport, no real source mount, and no retained record bytes, whether two complete persisted structural observations share the pair while all permitted fields show producer-confirmed snapshot semantics. Its report must retain only build pin, fixture/oracle digests, safe field-presence assertions, canary results, and named aib-swr.2 vectors. Until then, this record makes no progressive-snapshot claim.

### Codex: copied child rollout is established

The public source at the pinned commit establishes this chain:

1. [fork_thread](https://github.com/openai/codex/blob/be6e8eac029b183056b7e4402879f15d2c85f61b/codex-rs/core/src/thread_manager.rs#L1027-L1097) documents a fresh child id and passes already-read rollout history to the fork path with `ForkPersistence::Copied`.
2. [record_initial_history](https://github.com/openai/codex/blob/be6e8eac029b183056b7e4402879f15d2c85f61b/codex-rs/core/src/session/mod.rs#L1359-L1396) handles `InitialHistory::Forked`, retains the copied prefix for `ForkPersistence::Copied`, and persists those rollout items.
3. The [RolloutRecorder create path](https://github.com/openai/codex/blob/be6e8eac029b183056b7e4402879f15d2c85f61b/codex-rs/rollout/src/recorder.rs#L832-L871) constructs and retains session metadata containing the child thread id and fork lineage. Its [writer path](https://github.com/openai/codex/blob/be6e8eac029b183056b7e4402879f15d2c85f61b/codex-rs/rollout/src/recorder.rs#L1715-L1734) writes session metadata before pending rollout items.

Therefore a copied parent cumulative landmark can enter a child stream whose session_meta.payload.id is fresh. The current accepted Codex native identity uses both values, so parent and child facts have distinct native fact and request keys despite sharing one inherited semantic contribution. The duplicate-only cursor rule cannot make this neutral because the child identity is deliberately different; path, timestamp bucket, archive location, and scan order are excluded from identity and cannot substitute for lineage.

This is a source-contract gap, not a parser bug. A successor must decide and accept a source-faithful lineage or inherited-prefix rule at the shared identity/accounting boundary. It must not introduce a parser-local skip that silently changes duplicate, request-count, or cursor semantics.

The static observation does **not** settle Codex cache/reasoning arithmetic, all archived/live relocation behavior, or the exact serialized field set for all fork variants. Those remain fail-closed: archived/live relocation is a reconciliation hypothesis, decreasing cumulative landmarks are a malformed hold, and a future profile must prove the arithmetic and one-landmark-to-one-request relation required by REQ-source-adapter-profiles-010.

**Codex falsifiers:** This gap inference is falsified if a synthetic, content-free serialized-child probe proves that copied history has no usage landmark, that copied usage stays bound to the parent native identity, or that a successor accepted contract makes the child copy ledger-neutral without changing retained-history meaning. None of those probes ran here.

## Structural fixture, independent oracle, and executed capture controls

The fixture is hand-authored and contains only symbolic identifiers, structural relations, source links, version pins, and harmless canary labels. It contains no prompt, response, tool result, real path, raw record, credential, or content derivative. The adjacent verifier reads only that fixed sibling fixture, rejects command-line input, uses no subprocess/environment/network API, and has distinct Claude collision and Codex fork-neutrality oracle routines. Its recursive admission schema rejects unknown keys at the root and every declared nested object; an unregistered scalar mutation is therefore rejected rather than accepted by a denylist gap. It performs four deliberate in-memory mutations:

1. add an unregistered fixture scalar, which must break fixture admission;
2. make a fork child session equal its parent, which must break the contract-gap relation;
3. replace one independent canary label, which must break the privacy oracle; and
4. mutate an exact Claude replay timestamp, which must break the replay oracle.

The fixture declares distinct positive canaries for application value, decoder,
parser, log, exception, output capture, crash output, SQLite, OTLP, PostgreSQL,
image layer, filesystem, environment, and packet/network capture. Its expected
blockers are content decode, forbidden decoder/materializer use, sentinel egress,
credential access, broad-root access, and unexpected network activity. The
Codex cases separately cover the original contribution plus human, subagent,
and nested first-child-owned copied prefixes, including a same-millisecond
boundary and the archived/live-duplication hypothesis.

`exercise_0002_capture_controls.py` executed every declared positive canary
lane and every declared negative control using only an in-memory opaque
synthetic value. Each negative control is invoked and must reject before the
value can be stringified, converted to bytes, materialized, or handed to an
external operation. The executed result is **14 canary lanes exercised, 6
negative controls rejected, and 0 synthetic value touches**. This is stronger
than a declaration-only check, but its explicit limitation matters: it proves
the isolated candidate harness, not a future producer or production parser,
mount, credential reader, or network client. Those later executable lanes
remain required before any profile can activate.

| Artifact | SHA-256 | Purpose |
|---|---|---|
| [0002-source-semantics-fixtures.json](./0002-source-semantics-fixtures.json) | 4c8c4f16609bf719d22c888197be2c9a37ac64fe3978b1750ecddf9fc7086568 | Content-free Claude/Codex structural fixtures, executed-control limitation, canary lanes, and falsifiers. |
| [verify_0002_source_semantics.py](./verify_0002_source_semantics.py) | eecb5c568e00b0a3b201881fe3e82678ccfc73ea44a4c9c73afc08376d58e7ee | Independently derives the declared relationships, admits only the fixed fixture shape, and requires all four deliberate mutations to fail. |
| [exercise_0002_capture_controls.py](./exercise_0002_capture_controls.py) | 20c8e1b702c1e8403b15f65f9fb6f95709d823be214f583717a0b354d132e327 | Executes every content-free positive canary and negative rejection control without opening a producer or external resource. |

Run the oracle with:

    python3 about/legends-and-lore/evidence/verify_0002_source_semantics.py
    python3 about/legends-and-lore/evidence/exercise_0002_capture_controls.py

It is a candidate-evidence checker only; it is not a production parser, domain, ledger, runtime, mount, or sink implementation.

## Current accepted-byte integrity

The following immutable authority bytes were checked and remain outside this patch:

| Artifact | Current SHA-256 |
|---|---|
| RFC 0001 | f17a85ddd20c7c3c7998ea2a8d0d2f425b84cc57363ec942f5ea554b8cefaab8 |
| Evidence 0001 source/bounds | 2ca7455f0c331c8d46774f9c72bb8c3f2d6b360255fab4663bfd5d32bc09cf7d |
| Evidence 0001 synthetic vectors | 4808a21a78997c7886b220c29f7bb477b6ca6bd604dcb1afd0a8bf95eacc19f6 |
| Evidence 0001 provenance | dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0 |
| Active OpenSpec design | 13229d7e540f41dbf23ff8ae741983cbf4af7feebe15aa48391bba4e78afa21f |
| source-adapter-profiles specification | e1d13becbc66431332d484409c0263efe6e08046c0726c0373126764022c6696 |
| event-identity-and-normalization specification | e788522cce1d7e676cc03acae923462ab80b13236d887c78d7444a862e07966f |

## Required successor handoff — no amendment drafted

This is a cold-start feature-amendment handoff, not a proposed amendment. The accepting owner must choose replacement semantics and then authorize exact bytes through the normal successor-decision route.

| Gate | Required future work |
|---|---|
| 0 — baseline | Preserve this candidate, current accepted-byte hashes, and full source pin; do not reinterpret this finding as authorization to implement. |
| 1 — problem | State how copied inherited usage is prevented from contributing a second fact or logical request while preserving authentic child lineage and retained history. |
| 2 — doctrine | Reconfirm Content and Credentials Stay Outside, Normalization Preserves Meaning, Accounting Is Eventually Exact, and Partial Failure Is Explicit. |
| 3 — impact map | Use the exact surface map below. The successor must mark every listed requirement `replacement` or `unchanged-with-rationale`, name replacement bytes and migrations where applicable, and must not use a wildcard family. |
| 4 — design | Write no parser-local exception. The owner-selected design must define native fact identity, native request identity, copied-prefix lineage, duplicate/collision behavior, cursor effect, retained-history/backfill effect, and archive/live reconciliation. |
| 5 — executable contract | Amend the RFC and every affected active OpenSpec requirement in one traced change, then bind complete fixtures/oracles. aib-swr.2 and aib-swr.3 must own named identity and Codex vectors if the result becomes confirmed-current. |
| 6 — acceptance | Obtain independent privacy/security and accounting/ledger reviews at the exact PR head, resolve their findings, run strict OpenSpec/trace/shape/link/whitespace gates, and obtain a successor owner decision naming each replacement byte. |

### Exact successor impact map

This map is complete for the confirmed copied-prefix gap. It identifies review
surfaces, not permission to edit them in this candidate.

| Surface | Exact successor scope | Required disposition |
|---|---|---|
| RFC 0001 | `§ Source-Specific V1 Attribution → Codex rollouts`; `§ UsageEvent`; `§ SQLite Ledger and Atomicity`; `§ Incremental Reads, Rescans, and Quarantine`; `§ Compatibility and Evolution`; and `§ Specification and Doctrine Boundary → Required before implementation or release OpenSpec` | Name each replacement section byte, or mark it unchanged with a source-faithful rationale. |
| Source profile and identity specs | `REQ-source-adapter-profiles-008`, `REQ-source-adapter-profiles-009`, `REQ-source-adapter-profiles-010`; `REQ-event-identity-and-normalization-002`, `REQ-event-identity-and-normalization-003`, `REQ-event-identity-and-normalization-004`, `REQ-event-identity-and-normalization-005`; `REQ-durable-local-ledger-003`, `REQ-durable-local-ledger-004` | Replace the exact IDs whose native fact/request identity, copied contribution, duplicate/collision, or atomic cursor semantics change; state `unchanged-with-rationale` for each other listed ID. |
| Synthetic evidence specs | `REQ-synthetic-usage-spine-001`, `REQ-synthetic-usage-spine-002`, `REQ-synthetic-usage-spine-003`, `REQ-synthetic-usage-spine-004`, `REQ-synthetic-usage-spine-005`, `REQ-synthetic-usage-spine-006` | Classify each exact ID; the successor must bind copied-prefix fixtures, replay/collision vectors, canary evidence, and a separate oracle before activation. |
| Reconciliation and health specs | `REQ-stream-reconciliation-and-health-001`, `REQ-stream-reconciliation-and-health-002`, `REQ-stream-reconciliation-and-health-003`, `REQ-stream-reconciliation-and-health-004`, `REQ-stream-reconciliation-and-health-005`, `REQ-stream-reconciliation-and-health-006`, `REQ-stream-reconciliation-and-health-007`, `REQ-stream-reconciliation-and-health-008`, `REQ-stream-reconciliation-and-health-009`, `REQ-stream-reconciliation-and-health-010` | Classify each exact ID for child-prefix cursor, rescan, archived/live relocation, hold, and non-masking-health effects; replacement requires exact vectors and recovery evidence. |
| Release-profile governance specs | `REQ-release-profile-governance-002`, `REQ-release-profile-governance-004`, `REQ-release-profile-governance-006`, `REQ-release-profile-governance-007` | Bind the new member/evidence digest, fail closed before activation, and declare compatibility, rescan, identity, fingerprint, and migration consequences. |
| Existing candidate artifacts | `about/legends-and-lore/evidence/0002-source-semantics-candidate.md`; `about/legends-and-lore/evidence/0002-source-semantics-fixtures.json`; `about/legends-and-lore/evidence/verify_0002_source_semantics.py`; `about/legends-and-lore/evidence/exercise_0002_capture_controls.py`; `about/legends-and-lore/evidence/tests/test_0002_source_semantics.py` | Retain these candidate bytes as historical evidence; do not relabel them accepted or edit accepted 0001 evidence. |
| New successor fixture and oracle paths | `tests/fixtures/codex/rollout-copied-prefix.jsonl`; `tests/fixtures/codex/rollout-copied-prefix-subagent.jsonl`; `tests/fixtures/codex/rollout-copied-prefix-nested.jsonl`; `tests/fixtures/codex/rollout-copied-prefix-same-millisecond.jsonl`; `tests/fixtures/codex/rollout-copied-prefix-relocation.jsonl`; `tests/fixtures/codex/rollout-copied-prefix-cumulative-regression.jsonl`; `tests/oracles/codex_copied_prefix_oracle.py`; `tests/spec/test_event_identity_and_normalization.py`; `tests/spec/test_source_adapter_profiles.py`; `tests/spec/test_stream_reconciliation_and_health.py` | These paths do not exist yet. Create them only in the successor change after the owner selects semantics; use fully synthetic content-free values and an independently implemented oracle. |
| Beads and owner-decision surfaces | `aib-kwx` remains evidence-only; `aib-swr.2` remains blocked for source-independent identity foundations; `aib-swr.3` remains blocked for Codex adapter/accounting activation; successor Decision must name each replacement RFC/spec/fixture byte and its accepted digest. `aib-tvp` is explicitly not a surface of this handoff. | Keep all implementation blocked until the successor decision and exact-head independent privacy/accounting review accept the replacement set. |

aib-tvp is out of scope. No accepted document was modified, no Beads lifecycle state was changed, and no implementation task was started.

## Evidence run ledger

Run these commands from `projects/ai-usage-telemetry` before PR review:

| Command | Expected result | Candidate-evidence relationship |
|---|---|---|
| `python3 about/legends-and-lore/evidence/verify_0002_source_semantics.py` | `PASS; 4 deliberate mutations rejected`: unregistered scalar admission, copied-child identity, canary-label, and Claude replay mutations all fail. | Candidate-evidence-only structural oracle; it does not accept or amend any RFC/OpenSpec/Decision bytes. |
| `python3 about/legends-and-lore/evidence/exercise_0002_capture_controls.py` | `PASS; 14 canary lanes exercised; 6 negative controls rejected; 0 synthetic value touches`. Each declared content decode, forbidden materializer, egress, credential, broad-root, and network control rejects before an opaque synthetic value is touched. | Candidate-evidence-only isolated harness. It does not execute a producer, production parser, mount, credential reader, or network client. |
| `python3 -m unittest discover -s about/legends-and-lore/evidence/tests -p 'test_0002_source_semantics.py' -v` | Five targeted regressions pass: exact source ranges, unregistered-scalar rejection, executed capture controls, exact impact map, and this ledger contract. | Candidate-evidence-only regression suite; it prevents the corrective harness from being omitted from this mandatory ledger. |
| `python3 -m json.tool about/legends-and-lore/evidence/0002-source-semantics-fixtures.json >/dev/null` | Valid JSON with no emitted fixture value. | Validates only the synthetic candidate fixture. |
| `python3 -m py_compile about/legends-and-lore/evidence/verify_0002_source_semantics.py about/legends-and-lore/evidence/exercise_0002_capture_controls.py about/legends-and-lore/evidence/tests/test_0002_source_semantics.py` | All three Python files compile. | Checks the candidate verifier, isolated harness, and regression suite only. |
| `openspec validate --all --strict` | Active change validates with zero failures. | Confirms the accepted contract set remains valid; this candidate does not alter it. |
| `uv run ../../skills/personal/th-projects/scripts/spec-trace-check.py . --authoring` | Authoring trace has zero errors and warnings. | Confirms candidate evidence did not disturb the accepted requirement trace. |
| `git diff --cached --check` | No whitespace errors in the candidate-only patch. | Does not authorize contract or implementation work. |

PR integration remains blocked pending independent privacy/accounting review. This author has not performed or claimed that independent review.
