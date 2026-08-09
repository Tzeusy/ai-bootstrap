# Formal Review: RFC 0001

**Date:** 2026-08-10  
**Result:** PASS after two source/privacy rounds, one accounting/operations
repair round, and exact-digest confirming passes  
**Authority:** Technical review plus activated Owner Decision 0001  
**Scope:** RFC 0001, Evidence 0001, reconciled doctrine/topology/craft, and
lifecycle authority. This is documentation/spec-readiness evidence, not runtime
or release evidence.

## Accepted artifact set

| Artifact | SHA-256 |
|---|---|
| `rfcs/0001-adapter-ledger-and-sink-contract.md` | `f2ad18746a60db8cc9435aabca6c81a62017e0fd7e86275bc564c57731d88526` |
| `evidence/0001-source-and-bounds.md` | `5401c9fb0e621af6f35385f89f9cc2cc1d260a3a2119c457ba9e27784e787a1e` |
| `evidence/0001-synthetic-vectors.md` | `1b284a304d604fb01d83cb1faab57a5f33a9e62749913abd9c5e93ab3193918e` |
| `evidence/0001-provenance.md` | `dcfffe320712afbdcf805e05d30b277130e4bf81f9d718d4f4408bc077f482f0` |
| `heart-and-soul/decisions/0001-finalize-and-specify.md` | `1733027f39aa364f5a42af96f2486aa1cf5f8aa60246536d22b15da1c9ddbdee` |

The RFC/evidence digests include their Accepted status. The decision digest
includes activation and the same accepted artifact set. A later semantic change
requires an amendment/successor and fresh review; a release profile still needs
its own exact values and executable evidence.

## Review lanes

| Independent lane | Focus | Final verdict |
|---|---|---|
| `source_evidence_audit` | Source provenance, privacy boundary, Claude/Codex semantics, identity, categories, retention epistemics | PASS |
| `limits_evidence_audit` | Accounting, parser/reconciliation/storage bounds, OTLP conservation/catch-up, health, multiarchitecture | PASS |
| `launch_gate_preflight` | Lifecycle, owner authority, navigation, cross-pillar consistency, specification eligibility | PASS |

The launch-gate lane name describes its reusable reviewer context; this review
was not a launch-gate administration and records no `READY` verdict.

## Findings and dispositions

### Source and privacy

| Finding | Disposition |
|---|---|
| A separate Claude quota cache was unsupported and appeared to require credential-bearing global state. | Removed the mount/schema/source. Claude quota is `unknown/unavailable`; adding it requires a new credential-free boundary review. |
| Claude local paths/co-occurrence and identity lacked content-safe evidence. | Ran client 2.1.226 with fresh HOME/XDG/config, fake key, isolated loopback-only network, and a synthetic SSE mock. Recorded safe invocation, structural assertions, artifact digest, and cleanup without opening personal data. |
| The A/B/A mock sequence was initially misclassified as valid replay even though the vendor contract makes request IDs globally unique. | Reclassified A/B/A as a negative identity-reuse collision. Valid replay repeats the exact synthetic record; timestamp remains source time/fingerprint input. |
| Claude inclusive output was mislabeled as visible/non-reasoning output. | Added `output_unclassified`; `output_non_reasoning` is used only with an explicit split. |
| Codex `last_token_usage` was assumed to be a fresh delta and cache-write support was omitted. | Recorded rate-limit-only re-emission and `cache_write_input_tokens`; arithmetic and request identity remain disabled until a reviewed adapter profile freezes them. |
| Exactness claimed it could detect records deleted before discovery. | Pre-discovery state is `coverage_unknown`; `retention_gap` requires positive evidence across a known unconsumed cursor or registered sequence. |
| OpenCode was deferred merely for lacking quota. | Deferred for missing end-to-end identity, replay/mutation, privacy-projection, capability, and failure evidence; missing quota alone is an explicit capability gap. |

### Accounting, bounds, and operations

| Finding | Disposition |
|---|---|
| Draft parser constants lacked evidence and an unterminated record could grow without limit. | Replaced constants with immutable parser profiles; raw-byte/depth/key/path/numeric guards apply during scanning, including before newline, with `N-1/N/N+1` vectors. |
| A fixed rescan interval lacked a supported workload envelope and overdue state. | Reconciliation profiles bind deadline plus stream/byte/record/append envelope, durable overdue state, `source_envelope_exceeded`, recovery, and starvation/boundary tests. |
| OTLP dimension maxima had impossible cross-products and could silently omit values. | Profiles enumerate realizable full series identities, enforce project limits before an equal-or-higher SDK cap, partition conserved sum overflow, and block non-mergeable gauges. |
| OTLP catch-up could exceed request size with no atomic acknowledgement rule. | Added deterministic capped batches and checkpoint advance only after every batch for one target sequence is durably acknowledged. |
| SQLite free-space checks were described as proof, conflicted with record transaction granularity, and omitted maintenance amplification. | Defined a fail-closed guard per consumed-record transaction, explicit SQLite failure handling/reopen verification, hysteresis, and separate backup/migration/checkpoint/VACUUM headroom. |
| Storage health could not be persisted when the ledger was full. | Read-only inspection/restart recompute storage/database state and expose `storage_hold` or `ledger_unavailable` even when persisted health is stale. |
| Exact numeric profiles required implementation measurements but implementation was forbidden. | The first OpenSpec may authorize a finite, test-only non-production measurement harness. Real mounts, durable ingestion, remote export, and release claims remain disabled until profiles pass and freeze. |
| One architecture could have been omitted from a nominal v1 release. | V1 publication requires one OCI image index with native-gated `linux/amd64` and `linux/arm64`; emulation cannot replace either gate. |

### Lifecycle and documentation

| Finding | Disposition |
|---|---|
| The prior project-shape PASS covered RFC digest `975f...`, not the evidence-revised candidate. | This formal review supersedes it for RFC acceptance and binds the complete accepted digest set above. |
| Evidence documents initially claimed review without a current reviewer/revision. | Their status remained Candidate until these lanes converged; Accepted status is bound to this record. |
| Owner authority could have been inferred from agent review. | Owner Decision 0001 records the user's standing conditional direction, hard activation gates, reopen conditions, accepted digests, and explicit non-authorizations. |
| OpenSpec absence could be mistaken for a defect or implicit authorization. | It remains intentionally absent. The next authority step is reviewed launch parameters plus a named-commit project-direction gate verdict of `READY`. |

## Content-safe evidence statement

No reviewer opened personal sessions, prompts, responses, tool calls, global
application state, credential files, or auth databases. The only generated
session was fully synthetic, isolated from external networking and existing user
state, structurally inspected, hashed, and moved to operating-system trash.
Public-source claims are pinned in the provenance manifest.

## Confirming pass

After every blocking finding above was changed, the three independent lanes
re-read the candidate and reported PASS at the accepted digest set. Mechanical
checks also reported no whitespace errors, four authored `about/` pillars, and
the expected pre-OpenSpec `STRUCTURED`/4-of-5 state.

## Authority boundary

This review supports doctrine adoption, RFC acceptance, and launch-gate
administration. It does not make unmeasured profile values true, activate a
candidate source profile, prove an implementation, declare the launch gate
`READY`, authorize production ingestion/export, or satisfy either native release
gate.
