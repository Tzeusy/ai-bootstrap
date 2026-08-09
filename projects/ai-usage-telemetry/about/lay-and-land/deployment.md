# Deployment Topology

**Status:** Proposed, **[Inferred]** target deployment derived from Draft
doctrine and RFC 0001. Image construction and publication are outside this
documentation-only bootstrap.

## Runtime Shape

AI Usage Telemetry runs as one long-lived, non-root container per developer
workstation. Its internal poll loop uses a configurable interval with a
five-minute default; the host does not need cron or a systemd timer.

```text
host source streams (read-only) ─┐
mounted TOML (read-only) ────────┼─> container process ─> OTLP projector/delivery/checkpoint ─> OTLP endpoint
sink secret environment ─────────┤                    └─> PostgreSQL projector/delivery/checkpoint ─> PostgreSQL
state volume (read-write) <───────┘

TOML owns cadence, source selection, and the independent enablement/configuration
of both sinks. It cannot widen code-owned extraction, ledger admission, the
PostgreSQL projection allowlist, or the OTLP attribute/vocabulary registry.
```

## Mount Contract

| Container surface | Access | Purpose |
|---|---|---|
| Registered Claude session leaf/root | Read-only | Assistant usage records, split into independently cursor-bearing streams |
| Claude quota-cache file | Read-only | Subscription-window snapshots and source freshness |
| Registered Codex sessions leaf/root | Read-only | Token, turn-context, and rate-limit records, split into independently cursor-bearing streams |
| TOML configuration | Read-only | Cadence, aliases, source selection, sink enablement/destinations, and registered projection subsets |
| Durable `/data` volume | Read-write | SQLite ledger, lock, migrations, and delivery checkpoints |

Credential-bearing auth stores are not part of the mount contract. Startup
resolves and validates every source path; symlinks, broad parents, home/config
roots, and overlaps with known auth roots are rejected. Each mount is explicit
so the container cannot wander into unrelated developer data. The container
uses a read-only root filesystem and drops unnecessary privilege; `/data` is
the deliberate persistent write boundary, with only bounded runtime scratch
space if the chosen runtime requires it.

## Network Contract

- No inbound API, listener, or application port exists in v1. Local inspection
  uses the stable read-only SQLite views.
- Egress is limited operationally to configured OTLP and PostgreSQL endpoints,
  plus name resolution needed to reach them.
- Either sink, both sinks, or neither sink may be enabled while the local ledger
  continues collecting. A deployment with neither external sink creates no sink
  clients and performs no sink DNS or network work; it remains fully queryable
  and diagnosable through SQLite.
- Registry coordinates, endpoint hostnames, TLS material, database DSNs, and
  OTLP headers are deployment-specific and must not be committed.

## Packaging and Distribution

- The later implementation targets Python with `uv` and a reproducible
  multi-stage image.
- One OCI multi-architecture image contract targets `linux/amd64` and
  `linux/arm64`, runs without root privileges, and uses the same locked
  dependency inputs on both. Native smoke tests must prove equivalent
  normalization, ledger/view schema, replay safety, privacy behavior, and
  local-only operation; architecture-specific substitutions require review.
- Versioned project content documents a generic image reference. Personal
  builds may be published to a private registry through ignored local
  configuration; the registry is not a project dependency.
- Source remains buildable without access to the owner's registry.

## Persistence and Recovery

The `/data` volume is durable state, not cache. Losing it can lose deduplication
history and historical events after source tools prune their logs. V1 retains
admitted facts indefinitely: rotation or deletion of a source stream does not
retract them, and ordinary recovery never silently resets or prunes the ledger.
Lossless SQLite maintenance is distinct from retention deletion. On unsafe low
space, collection fails visibly before committing facts or advancing a stream
cursor and keeps existing local views readable where the filesystem permits.

After a restart, the container resumes stream cursors and destination-scoped sink
checkpoints from SQLite ledger order. Stream replay is safe through stable fact
identity and an accounting fingerprint that excludes cursor, export, and
configuration changes. OTLP and PostgreSQL resume independently; changing a
destination cannot silently reuse another destination's checkpoint.

## Environment Boundaries

- **Development:** fully synthetic fixture mounts and disposable state/sink
  services; real personal session stores are not test fixtures.
- **Personal deployment:** explicit host mounts, persistent state, and locally
  configured sinks. Private registry details remain outside tracked files.
- **Other developers:** build the portable image or pull it from a registry
  they trust; no homelab repository or workstation-specific path is required.
