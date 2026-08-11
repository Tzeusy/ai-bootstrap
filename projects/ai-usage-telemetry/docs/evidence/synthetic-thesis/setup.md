# Disposable Synthetic-to-SQLite Thesis

This evidence is content-free. It names no personal source, credential, raw
record, secret, destination, or reusable production bypass.

## Fixed inputs

- Fixture inventory: `tests/fixtures/synthetic-thesis/manifest.json`
- Qualified input: `qualified-claude.jsonl`, version `synthetic-thesis@1`
- Synthetic database: a disposable SQLite file under the test temporary
  directory; it is not retained or used by a production package.
- Launcher: `thesis.launcher.launch`, which rejects forbidden configuration
  before opening the fixture, manifest, database, credential reader, sink, or
  network path.

## Exercise command

From the repository root:

```sh
uv run pytest projects/ai-usage-telemetry/tests/spec/test_synthetic_usage_spine.py -q
```

The six requirement-named tests execute the launcher, field-projecting parser,
SQLite transaction, replay/collision path, capture probes, and bounded exercise
oracle. No private ledger table is queried by the exercise.
