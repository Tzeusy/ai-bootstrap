# FAQ

## Why only agnostic prompt mirroring for GitHub?

GitHub Copilot prompt artifacts are still evolving. This skill keeps outputs minimal and agnostic so downstream tooling can layer tool-specific metadata later.

## Why is `ai-bootstrap/` the base directory?

This repo stores prompt assets under `ai-bootstrap/`. The sync tool treats `ai-bootstrap/skills` and `ai-bootstrap/agents` as canonical sources, and mirrors into tool-specific folders under `ai-bootstrap/`.

## Can I add new tool targets?

Yes. Update `references/mapping-spec.md` first, then extend the planner in `scripts/ai_prompt_standardizer.py`.
