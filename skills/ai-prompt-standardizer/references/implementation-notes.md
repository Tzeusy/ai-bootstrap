# Implementation Notes

## Recursion Prevention

- Source walks always skip directories named `.codex`, `.claude`, `.gemini`, and `.github`.
- This prevents generated output from being re-ingested as canonical input.

## Cleaning Strategy

- `--clean` removes orphaned generated files that no longer map to a source.
- Skills cleaning is scoped to `ai-bootstrap/.*/skills/**` only.
- Agents cleaning is scoped to managed agent outputs only:
  - `.codex/**/AGENTS.override.md` and `.codex/AGENTS.md`
  - `.claude/**/CLAUDE.md`
  - `.gemini/**/GEMINI.md`
  - `.github/agents/*.agent.md`
- Other tool config files are not removed.

## Path Normalization

- All input and output paths use `pathlib.Path.resolve()`.
- Relative mapping is computed from the canonical root (`ai-bootstrap/skills` and `ai-bootstrap/agents`).
- GitHub agent filenames use `Path.parts` to remain OS-agnostic.

## Read-Only Protection

- If a destination exists and is not writable, the run fails with a clear error.
- Dry-run still reports the error so CI can detect it early.

## Deterministic Ordering

- Planned operations are sorted by destination path and action before execution.
- This ensures stable output ordering across runs and platforms.
