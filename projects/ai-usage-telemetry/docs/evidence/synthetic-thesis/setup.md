# Disposable Synthetic-to-SQLite Thesis

This evidence is content-free. It names no personal source, credential, raw
record, secret, destination, or reusable production bypass.

## Fixed inputs

- Fixture inventory: `tests/fixtures/synthetic-thesis/manifest.json`
- Qualified input: `qualified-claude.jsonl`, version `synthetic-thesis@1`
- Synthetic database: a disposable SQLite file under the test temporary
  directory; it is not retained or used by a production package.
- Launcher: `thesis.launcher.launch`, which rejects forbidden configuration
  before any input read. For an allowed run it validates the canonical manifest,
  fixture membership, digest, and projected types before it creates the
  temporary database directory or opens SQLite. Every rejected fixture leaves
  no database file, table, or durable contribution.

## Exercise command

From the repository root:

```sh
uv run pytest projects/ai-usage-telemetry/tests/spec/test_synthetic_usage_spine.py -q
```

The six requirement-named tests execute launcher preflight, the byte-projecting
parser, SQLite transaction, line/file/restart/rescan replay, capture probes,
the bounded exercise, and retirement enforcement. The parser test fails if the
whole raw payload is decoded; skipped sentinel-bearing bytes stay outside the
application value boundary.

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
