# Security and Privacy

The security boundary is exclusion, not sanitization after collection.
**Content and Credentials Stay Outside**: forbidden data must not enter the
telemetry pipeline in the first place.

## Forbidden data

Adapters, the ledger, diagnostics, and sinks must never collect or forward:

- prompt or response text, message bodies, tool-call arguments or results, or
  source-record fragments;
- authentication tokens, cookies, API keys, secret values, credential files,
  or environment dumps;
- metadata absent from the code-owned extraction or stable ledger-admission
  registry, even when an operator has attempted to configure it; or
- ledger-admitted metadata that the applicable PostgreSQL projection allowlist
  or OTLP attribute/vocabulary registry does not permit.

Errors identify only the source family, safe stream alias, bounded field-path
class, record position, and error code. They do not quote the rejected record,
field value, raw parser exception, or content-derived identity. Fixtures and
examples use synthetic values only; irreversible redaction is not evidence that
the production parser avoids materializing content.

## Field-projecting parser boundary

Adapters use a streaming parser that projects only exact registered paths and
scalar types. Traversing encoded bytes is permitted, but a content-bearing or
otherwise unregistered value is skip-only: it is never decoded, allocated into
the application object graph, copied, hashed, logged, fingerprinted, persisted,
or exported. Depth, record-size, scalar-length, and field-count limits are
declared and enforced before unbounded allocation. A limit breach or malformed
complete record holds the stream cursor before that record and quarantines the
affected stream with a safe diagnostic.

## Metadata admission

Four reviewed controls serve distinct purposes:

1. the code-owned extraction registry defines source paths, types, bounds,
   sensitivity, and materialization eligibility;
2. stable ledger admission/schema defines normalized fact fields and immutable
   identity/fingerprint participation;
3. the PostgreSQL projection allowlist defines that sink's columns and extension
   fields; and
4. the OTLP attribute/vocabulary registry defines finite dimensions, values,
   and cardinality budgets.

Deployment configuration may narrow sink projections but cannot widen any
registry. No configuration, alias, or export change may alter a fact's logical
identity or accounting fingerprint.

Adding a field to any registry is a security-relevant interface change. It requires a
documented purpose, cardinality assessment, positive and negative tests, and
review of every destination:

- OTLP receives only bounded, low-cardinality attributes;
- PostgreSQL keeps stable normalized values in named columns and only
  allowlisted extension metadata in JSONB; and
- the local SQLite ledger may retain normalized usage and admitted metadata
  indefinitely, but never forbidden data.

Opaque event identities must be sufficient for deduplication without exposing
source content or credentials outside the local state boundary. Their exact
construction belongs in
[`RFC 0001`](../legends-and-lore/rfcs/0001-adapter-ledger-and-sink-contract.md).

## Filesystem, process, and secret boundaries

- Every registered source leaf is resolved, validated, and mounted explicitly
  read-only. Symlinked scope expansion, broad parent/home/config mounts, and
  overlap with known auth roots fail closed. An adapter never repairs,
  truncates, locks, renames, or annotates a source tool's files.
- The long-running container runs as non-root. Its writable filesystem surface
  is limited to the deliberate state location and bounded runtime scratch space;
  its root filesystem is read-only and unnecessary privilege is dropped.
- V1 exposes no inbound API, listener, or published port. A local-only
  deployment starts no sink client and performs no sink DNS/network activity.
- Sink credentials, when required, arrive through the deployment's external
  secret boundary. They are neither checked in nor persisted in SQLite,
  PostgreSQL telemetry rows, OTLP attributes, logs, crash reports, or fixtures.
- Startup output describes whether required secret inputs are present without
  printing their values.
- A missing or rejected credential degrades only the affected sink and remains
  visible; it does not weaken source, ledger, or other sink safeguards.

## Release-blocking verification

Privacy tests place high-entropy content and credential sentinels in every
unregistered location. Parser instrumentation must prove the values were not
decoded, allocated, copied, or hashed, and capture scans must prove neither the
sentinels nor derived values reached fingerprints, SQLite tables/views, safe
diagnostics, logs, OTLP, or PostgreSQL. Tests also exercise depth/size limits and
safe error reporting. A release is blocked by any sentinel materialization or
egress, unbounded parser allocation, leaked diagnostic value, or ability to
write a declared source mount.

These boundaries also support **The Runtime Boundary Is Portable and Narrow**:
portability must not depend on broader host access or elevated privilege.
