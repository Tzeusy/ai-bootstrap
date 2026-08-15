# Disposable Synthetic-to-SQLite Thesis

This evidence is content-free. It names no personal source, credential, raw
record, secret, destination, or reusable production bypass.

## Fixed inputs

- Fixture inventory: `tests/fixtures/synthetic-thesis/manifest.json`
- Qualified input: `qualified-claude.jsonl`, version `synthetic-thesis@1`
- Synthetic database: a disposable SQLite file under the test temporary
  directory; it is not retained or used by a production package.
- Launcher: `thesis.launcher.launch`, which first validates Decision 0002's one
  `synthetic-usage-spine` row is exactly `accepted` and that its bound
  `spec.md` SHA-256 still matches. Direct harness construction repeats that
  check, so it has no authorization bypass. Only then does the harness reject
  forbidden configuration and validate the canonical manifest, fixture
  membership, projected accounting digest, and projected types before it
  creates the temporary database directory or opens SQLite. The manifest never
  hashes raw fixture bytes: committed Git bytes pin each fully synthetic vector,
  while `projected_sha256` binds only registered accounting values after the
  bounded structural projection. Every rejected fixture leaves no database
  file, table, or durable contribution.

## Exercise command

From the repository root:

```sh
uv run pytest projects/ai-usage-telemetry/tests/spec/test_synthetic_usage_spine.py -q
```

The requirement-named tests execute launcher preflight, the byte-projecting
parser, SQLite transaction, line/file/restart/rescan replay, capture probes,
the bounded exercise, and retirement enforcement. The privacy matrix uses real
synthetic nested, JSON-escaped, malformed, duplicate-registered-key,
32-level/33-level, and over-64-KiB skipped-field fixtures through the launcher
and harness. The parser receives one `memoryview` over a read-only mapped source
buffer rather than a copied JSONL line; it decodes only registered scalar tokens
after a structural pass has rejected duplicate registered keys. The privacy
capture counts the real projected fingerprint input, observes parameters at the
actual SQLite execution boundary, and scans every SQLite table, view, and
durable database page. A fresh-interpreter A/B/A sequence proves replay,
collision, reopen, and rescan state survives process boundaries.

## Bounded read exercise

After the one setup run, the exercise performs exactly these six public reads:

1. `usage_events`
2. `usage_event_amounts`
3. `logical_requests`
4. `synthetic_aggregates`
5. `ledger_health`
6. versioned `aiut.health/v1` health

The test derives answers from those returned values and compares them with a
separate fixed-fixture oracle. It visibly rejects more than six reads, any
private base-table request, an omitted answer, and elapsed time greater than
ten minutes. No private ledger table is queried by the exercise.
