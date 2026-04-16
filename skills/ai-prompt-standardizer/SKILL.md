---
name: ai-prompt-standardizer
description: Use when synchronizing canonical ai-bootstrap prompt assets into tool-specific folders or enforcing prompt mirror consistency in CI.
---

# AI Prompt Standardizer

## Overview

Standardize prompt assets by mirroring canonical `ai-bootstrap/skills` and `ai-bootstrap/agents` into tool-specific folders (`.codex`, `.claude`, `.gemini`, `.github`) with deterministic, idempotent sync.

## When To Use

- Canonical prompt content changes and downstream tool mirrors must be updated.
- CI needs a check to prevent drift between sources and generated outputs.
- Orphaned generated files must be cleaned safely.

## Workflow

1. Run the CLI from repo root.
2. Use `--dry-run` to review changes.
3. Use `--check` in CI for non-zero exit on drift.
4. Use `--clean` only when you want to remove orphaned generated files.

## Quick Reference

- CLI entrypoint: `ai-bootstrap/skills/ai-prompt-standardizer/scripts/ai_prompt_standardizer.py`
- Dry run: `scripts/dry-run.sh`
- Example: `scripts/example.sh`
- Tests: `scripts/test.sh`
- Mapping rules: `references/mapping-spec.md`
- Edge cases: `references/implementation-notes.md`

## Usage

```bash
python ai-bootstrap/skills/ai-prompt-standardizer/scripts/ai_prompt_standardizer.py --dry-run --only all
python ai-bootstrap/skills/ai-prompt-standardizer/scripts/ai_prompt_standardizer.py --only skills
python ai-bootstrap/skills/ai-prompt-standardizer/scripts/ai_prompt_standardizer.py --only agents --clean
python ai-bootstrap/skills/ai-prompt-standardizer/scripts/ai_prompt_standardizer.py --check --only all
```

## Resources

- `scripts/ai_prompt_standardizer.py` implements the sync engine and CLI.
- `references/mapping-spec.md` documents all mapping rules and examples.
- `references/implementation-notes.md` covers recursion prevention, cleanup, and path handling.
- `assets/fixtures/` contains deterministic test fixtures and expected output snapshots.
