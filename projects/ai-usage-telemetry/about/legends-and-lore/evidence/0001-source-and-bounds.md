# Evidence 0001: Source Semantics and Bounded Profiles

**Status:** Accepted evidence annex for RFC 0001  
**Date:** 2026-08-10  
**Observed client versions:** Claude Code 2.1.226; Codex 0.147.0

## Purpose and safety boundary

This annex records the evidence used to accept or reject source and resource
claims in RFC 0001. No personal session record, prompt, response, tool call,
global application state, credential file, or authentication database was
opened. Local inspection used client versions, allowlisted executable schema
literals, and one fully synthetic Claude capture in a fresh isolated namespace;
its exact safety/provenance record is
[`0001-provenance.md`](./0001-provenance.md). Public documentation and pinned
public source own semantic claims where available. Real records must never be
copied, redacted, hashed, or repurposed as fixtures.

`[Observed]` means directly supported by the pinned source or documented client
surface. `[Inferred]` means a project design derived from those facts.
`[Unknown]` means the project must fail closed until evidence changes.

## Source capability decision

| Source | Usage | Local quota | V1 decision |
|---|---|---|---|
| Claude Code 2.1.226 | **Observed**, version-specific session JSONL fields | **Unavailable** within the credential-free boundary | Admit usage through a versioned adapter; report quota `unknown/unavailable` |
| Codex 0.147.0 | **Observed** rollout token-count state | **Observed** optional local rate-limit snapshots | Admit only validated cumulative usage advancement and structurally present rate-limit snapshots |
| OpenCode | Partial local shape only | Not established | Defer until identity, replay/mutation, privacy, and failure semantics are reviewed end to end |

Capability absence is data, not zero. A source does not need quota support to
provide usage, but every unsupported capability must remain explicit in health
and query surfaces.

## Claude Code evidence

- **[Observed] Session container.** Claude Code documents local sessions as
  JSONL with one object per line in its [session documentation](https://code.claude.com/docs/en/sessions).
- **[Observed, version-specific] Usage field surface.** A fully synthetic
  loopback-only capture from Claude Code 2.1.226 proved co-occurring string paths
  `/type`, `/sessionId`, `/requestId`, `/timestamp`, `/cwd`, `/message/id`, and
  `/message/model`; array-valued skip-only `/message/content`; and the four
  numeric counters under `/message/usage`: `input_tokens`,
  `cache_creation_input_tokens`, `cache_read_input_tokens`, and
  `output_tokens`. The public [Messages API](https://platform.claude.com/docs/en/api/messages)
  defines the counter meanings, but the local shape remains adapter-versioned.
  `/cwd` establishes only a source working directory. No evidence here proves
  repository discovery or a repository-root mapping; v1's normalized project
  field therefore uses only the exact lexical working-directory basename or
  null under the profile-frozen path flavor.
- **[Observed/inferred] Identity and collision.** Anthropic documents every API
  response `request-id` as a [globally unique request
  identifier](https://platform.claude.com/docs/en/api/errors). The deliberately
  non-conforming mock sequence A/B/A produced changed record timestamps, so it
  is a negative identity-reuse/collision vector rather than valid replay. V1
  uses `(sessionId, requestId)`, treats message ID as a consistency field, and
  includes the profile-admitted record timestamp in source time/fingerprint.
  Valid replay repeats the exact synthetic record across lines/files/rescans. A
  changed upstream shape creates a new adapter schema ID rather than inheriting
  this rule.
- **[Observed] Inclusive output.** Anthropic documents `output_tokens` as an
  inclusive output total; reasoning can be separately described when a thinking
  breakdown is present. See [extended thinking token behavior](https://platform.claude.com/docs/en/build-with-claude/extended-thinking).
  Therefore Claude's base counter maps to `output_unclassified`, not
  `output_non_reasoning`.
- **[Unknown/unavailable] Quota.** Static schema literals expose cached usage
  utilization inside global application state. Claude's [application-data
  documentation](https://code.claude.com/docs/en/claude-directory) identifies
  that state as containing OAuth and other global configuration/cache data.
  No independent credential-free quota leaf was found; `stats-cache.json`
  describes historical aggregates rather than subscription-window quota.
  Global state is inadmissible even if a parser could select a few fields.

Adding Claude quota later requires a credential-free, sanitized upstream
surface plus a new source-boundary review and owner acceptance. Discovering
more paths inside credential-bearing state is not sufficient.

## Codex evidence

- **[Observed] Rollout structure.** The pinned source defines rollout items,
  session metadata, and turn context in
  [`protocol.rs`](https://github.com/openai/codex/blob/rust-v0.147.0/codex-rs/protocol/src/protocol.rs#L3075-L3410).
- **[Observed] Usage and limits.** `TokenUsage`, `TokenCountEvent`, and the
  primary/secondary rate-limit structures are defined in
  [`protocol.rs`](https://github.com/openai/codex/blob/rust-v0.147.0/codex-rs/protocol/src/protocol.rs#L2064-L2209).
  `used_percent` is a `0..100` source value; normalization to `0..1` is a
  project inference.
- **[Observed] Re-emission.** Token-count events may be emitted after a
  rate-limit-only update while retaining previous token info, as shown in
  [`session/mod.rs`](https://github.com/openai/codex/blob/rust-v0.147.0/codex-rs/core/src/session/mod.rs#L3764-L3893).
  `last_token_usage` is therefore not proof of a new request. Only a validated,
  componentwise cumulative advancement can yield a candidate contribution.
- **[Observed] Cache write.** `TokenUsage` contains
  `cache_write_input_tokens`, and Responses maps cache-write usage into it in
  [`responses.rs`](https://github.com/openai/codex/blob/rust-v0.147.0/codex-rs/codex-api/src/sse/responses.rs#L122-L147).
- **[Inferred, evidence-gated] Arithmetic and identity.** Whether aggregate
  input/output counters include their cache/reasoning subcomponents, and which
  cumulative advancement corresponds to one unique request, must be fixed by
  the adapter profile and synthetic vectors. A rate-limit update, context-window
  update, or recomputation must not create a request contribution.

## Upstream retention boundary

Claude's session documentation describes upstream transcript cleanup. The
collector can be eventually exact only over complete, supported records that
become observable. It cannot detect or recover a record deleted before source
discovery, so that earlier coverage remains `coverage_unknown`. A
`retention_gap` requires positive evidence: for example, a discovered stream
disappears before its durable cursor consumes it, truncation crosses an
unconsumed cursor, or a registered sequence/manifest proves an omission.

## Bounded release-profile decision

RFC 0001 fixes fail-closed semantics and requires every release to embed
immutable, code-owned profiles with explicit IDs. Exact numeric values belong
in those reviewed profiles because they depend on the implementation and
supported workload; unsupported candidate constants are not evidence.

| Profile | Must freeze | Required evidence before implementation/release |
|---|---|---|
| Parser | raw record bytes excluding delimiter; depth counting; encoded key and structural bounds; projected-path encoded/decoded sizes, multiplicity, numeric range/precision/scale; bounded memory/work | `N-1/N/N+1` vectors, unterminated oversize record, chunk/Unicode/escape boundaries, skip-only non-materialization, minimum container capacity |
| Reconciliation | maximum completion interval; stream/byte/record/append-rate envelope; overdue health; exemption proof | mutation/rotation/replacement tests, restart and starvation cases, at-envelope timing on both supported architectures |
| OTLP projection | resource/scope/metric/attribute series identity; allowed tuples; value-size, per-instrument, process-total, SDK, and request-size caps; sum conservation and gauge blocking | exhaustive tuple enumeration, cap boundaries, SDK/exporter configuration proof, serialized payload measurements |
| Storage | supported volume; maximum transaction growth; SQLite auxiliary-file amplification; enter/resume thresholds; operation-specific maintenance headroom | VFS and real-filesystem ENOSPC/IOERR injection, precheck race, crash atomicity, restart hold, migration/backup/VACUUM headroom |

The OpenTelemetry [metrics data model](https://opentelemetry.io/docs/specs/otel/metrics/data-model/)
defines series using resource, scope, metric, and point attributes; the
[Metrics SDK cardinality rules](https://opentelemetry.io/docs/specs/otel/metrics/sdk/)
require bounded handling rather than silent loss. SQLite documents
[result codes](https://www.sqlite.org/rescode.html),
[transaction behavior](https://www.sqlite.org/lang_transaction.html), and
[VACUUM headroom](https://sqlite.org/lang_vacuum.html); a free-space precheck is
therefore an admission guard, never proof that a write cannot fail.

## Architecture decision

V1 supports both `linux/amd64` and `linux/arm64`. The release tag remains
blocked until one OCI image index contains both runnable manifests and the same
synthetic, privacy, accounting, storage, projection, and runtime suites pass on
native hosts. Cross-emulation may supplement but cannot replace native gates.
Parity compares canonical semantic outputs rather than raw database or wire
bytes. The container structure follows the [OCI image-index
contract](https://github.com/opencontainers/image-spec/blob/main/image-index.md).

## Reproducible refresh procedure

1. Pin client versions and public source tags.
2. Do not open personal sessions, global/auth state, or credentials. Inspect
   only versions, fixed file kinds, and allowlisted executable literals.
3. Prefer official documentation and pinned public source for field types and
   emission semantics.
4. Generate Claude fixtures with a fake config root, fake API key, mock local
   transport, and fully synthetic responses; generate Codex fixtures from
   hand-authored protocol values.
5. Instrument the field projector so forbidden paths cannot invoke scalar
   decoding, materialization, fingerprinting, or diagnostics. Each capture and
   instrumentation channel must also carry a distinct harmless test canary so a
   silent or disconnected oracle cannot pass. Deliberate test-only forbidden
   decoder calls, sentinel leaks, and unexpected network events must make the
   harness fail; use only synthetic non-secret values.
6. Record exact profile IDs, fixture names, expected content-free facts, client
   versions, native architecture, and unresolved claims. Never record live
   paths, identifiers, excerpts, or hashes of personal data.

## Accepted unresolved boundary

No numeric release profile is asserted by this annex because no implementation
or measurement harness exists yet. The first OpenSpec changeset must specify
the profile schemas and may authorize a test-only, non-production measurement
harness under finite candidate bounds. Real source mounts, durable ingestion,
remote export, and any release claim remain disabled until one complete profile
set has exact values and passing synthetic evidence on the minimum supported
capacity.
