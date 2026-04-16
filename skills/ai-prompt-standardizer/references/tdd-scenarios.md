# TDD Scenarios (Documented)

This skill follows a documented TDD approach using fixtures and a failing test harness.

## Scenario 1: Missing CLI should fail tests (RED)

- Setup: Run `scripts/test.sh` before the CLI exists.
- Expected: Test fails with a missing script error.
- Purpose: Confirms tests detect missing implementation.

## Scenario 2: Skills + Agents sync with fixtures (GREEN)

- Setup: Use `assets/fixtures/base` as input with `--only all`.
- Expected: Output matches `assets/fixtures/expected` exactly.
- Purpose: Validates mapping and copy behavior.

## Scenario 3: Clean removes orphans

- Setup: Add a stray file under `ai-bootstrap/.codex/skills/` in a fixture copy.
- Expected: `--clean` removes the stray file and leaves mapped outputs intact.
- Purpose: Validates safe cleanup rules.

## Scenario 4: Read-only destination detection

- Setup: Mark a destination file read-only in a fixture copy.
- Expected: Sync fails with a clear error before writing.
- Purpose: Confirms protection against unwritable outputs.
