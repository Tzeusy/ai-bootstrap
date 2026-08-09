# Data Boundaries

AI Usage Telemetry exists to make local usage facts queryable without turning
local AI sessions into a surveillance dataset. This boundary applies equally
to normal operation, retries, diagnostics, migrations, and failure handling.

## Data Classes

[Inferred] The product recognizes four data classes with different trust
boundaries:

| Class | Examples | Local treatment | Export treatment |
|---|---|---|---|
| **Content** | Prompts, responses, message bodies, content-bearing attachments, and tool-call transcripts | A field-projecting parser may traverse their encoded bytes but must never decode, allocate, copy, hash, log, diagnose, or retain their values | Prohibited. Content cannot be admitted by code or configuration. |
| **Ordinary metadata** | Tool, model when known, repository-basename project label, configured account alias, event time, quota window, and source freshness | May enter the stable ledger schema only when the code-owned extraction and ledger-admission registries both admit it | Denied unless the destination's separate projection registry admits it and configuration selects it |
| **Sensitive metadata** | Absolute working-directory paths, native account identifiers, session or conversation identifiers, source filenames, offsets, and deduplication keys | Minimize and keep local only when required for stream resolution, provenance, or exact accounting | Not exportable merely because configuration names it; a destination registry must explicitly admit the exact field and its bounded use |
| **Credentials** | API keys, access or refresh tokens, cookies, credential-bearing auth databases, and auth configuration | Must not be mounted, read, copied, logged, or retained | Prohibited. Credentials cannot be enabled by an allowlist. |

[Inferred] Token counts, unique usage-request counts, quota utilization, and
freshness are telemetry measures, not metadata permission shortcuts. Enabling a
sink selects which registered measures it receives; destination projection
controls independently select which descriptive fields may accompany them.

## Source Boundary

[Observed] Claude Code usage fields are present on usage-bearing assistant
records in local JSONL session files. Codex emits token-count records whose
`last_token_usage` is a per-event delta and whose rate-limit data can describe
quota state. Codex's token-count payload does not itself establish model
identity.

[Inferred] A **source family** is one tool-format domain such as Claude Code or
Codex. Each family contains one or more independently ordered **source streams**,
and each stream contains **records**. Cursor, parser context, quarantine,
freshness, and health belong to the stream, not only to a family-wide adapter.

[Inferred] The container receives separate, explicit, resolved read-only leaf
mounts for registered Claude and Codex source locations. It receives one
writable volume for its own SQLite state. It does not receive a home-directory
mount, a writable source mount, a symlinked parent that broadens access, or a
credential-bearing auth-store mount.

[Inferred] Source adapters use a field-projecting streaming parser and may
decode only paths registered in code for usage, quota, source identity, and
safe metadata. Reading bytes to traverse a record is permitted; content-bearing
values are skip-only and must never be decoded, allocated into an application
object, copied, hashed, logged, fingerprinted, or retained. Records exceeding
declared depth or size limits are malformed. Raw records are never a diagnostic
or dead-letter format; diagnostics contain only a source-family name, safe
stream alias, bounded field-path class, record position, and error code.

[Inferred] Only an explicitly registered irrelevant record may advance a stream
cursor without producing a fact. An unknown record kind or malformed complete
record holds the cursor before that record and quarantines the affected stream.
Other streams may continue, but family and global health summaries remain
degraded while any member stream is quarantined.

[Inferred] If a dimension cannot be established without content, credentials,
or guessing, it remains absent. For example, Codex model attribution must come
from a registered non-content event in the same source context or be recorded as
unknown; the collector must not infer it from conversation text.

## Admission and Projection Registries

[Inferred] Four controls remain separate and deny by default:

1. The **code-owned extraction registry** fixes exact source paths, scalar types,
   size bounds, sensitivity, and whether a value may be materialized. Runtime
   configuration cannot add a path.
2. The **stable ledger admission and schema** fixes which normalized fields may
   become facts and which immutable fields participate in logical identity and
   the accounting fingerprint.
3. The **PostgreSQL projection allowlist** fixes which stable columns and
   extension fields may leave for that sink. Configuration may select a subset;
   it cannot add a field.
4. The **OTLP attribute and vocabulary registry** fixes allowed dimensions,
   values, and cardinality budgets. Configuration may select a subset but cannot
   invent a dimension or value.

No export, endpoint, alias, or configuration change may rewrite an admitted
fact, change its logical identity, or change its accounting fingerprint.
Changing a projection stops or starts future delivery according to its own sink
checkpoint; it does not create a new source contribution.

[Inferred] The default project label, when available, is the repository basename
rather than an absolute path. An account label is a configured alias when
discovering a native identifier would require credential access. The alias is
configuration, not evidence that the collector authenticated to the tool.

[Unknown] Project attribution for usage outside a discoverable repository needs
a downstream contract. V1 must expose the missing mapping rather than exporting
an absolute path or inventing a project name.

## Storage and Sink Boundaries

### Local SQLite Ledger

[Inferred] SQLite is the durable source of truth. It retains normalized usage
records, quota snapshots, safe interpretive metadata, source provenance, and
the local accounting identity required to make overlapping polls idempotent.
Identity is scoped across the collector, source family, and source stream rather
than inferred from a cursor or path alone. Normalized records are retained
indefinitely in v1; deletion or rotation of a source does not delete admitted
history.

The ledger must never contain raw source records, content values, credentials,
or copied auth-store data. Local storage does not excuse crossing the content
or credential boundary.

[Inferred] V1 provides a sink-independent local query and health contract through
stable read-only SQLite views named `usage_events`, `usage_event_amounts`,
`quota_snapshots`, `source_health`, `sink_health`, and `ledger_health`.
`source_health` reports stream-level state and supports non-masking family/global
summaries. No inbound API or listener is part of this contract.

### OTLP Metrics

[Inferred] OTLP exports bounded cumulative usage measures and quota/freshness
gauges derived from committed ledger facts. Only attributes and values admitted
by the OTLP registry may accompany them. Absolute paths, session IDs, source
filenames, deduplication keys, and arbitrary JSONB do not belong in metric
dimensions.

OTLP is an optional projection, not a ledger. An OTLP outage cannot block local
accounting or another sink, and recovery must not double-count source events.

### PostgreSQL

[Inferred] PostgreSQL is an optional query sink with normalized usage and quota
tables. Registered descriptive metadata may be copied into JSONB only after the
PostgreSQL projection allowlist is applied. JSONB is not an escape hatch for raw
records, content, credentials, or unregistered fields.

PostgreSQL does not own stream cursors or accounting truth. A PostgreSQL outage
cannot stop local collection or OTLP export, and a retry must reproduce the
same normalized facts without creating new source contributions.

## Failure and Freshness

[Inferred] Health is tracked per source stream and per optional sink. A parser
failure quarantines only the affected stream; a sink failure degrades only that
projection. Healthy streams continue committing to SQLite. Family and global
summaries must surface every degraded member rather than average or mask it.
Each degraded state identifies the affected boundary and exposes how old its
last successful source or export state is.

[Inferred] Every quota snapshot carries canonical `0-1` utilization, source
observation time when the source provides it, collection time, and explicit
fresh, stale, or unknown freshness evidence. Consumers must distinguish "zero
utilization" from "no registered quota data" and "fresh" from "last known";
unknown source time must not be replaced with collection time.

[Unknown] OpenCode and future tools do not yet have a proposed, reviewed, and
owner-accepted end-to-end local
usage-and-quota boundary. Their files must not be mounted or parsed merely
because a partial local format exists; support begins only after the source,
identity, quota, privacy, and failure contracts are resolved.
