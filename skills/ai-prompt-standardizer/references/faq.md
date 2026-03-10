# FAQ

## Why only agnostic prompt mirroring for GitHub?

GitHub Copilot prompt artifacts are still evolving. This skill keeps outputs minimal and agnostic so downstream tooling can layer tool-specific metadata later.

## Why is `genai/` the base directory?

This repo stores prompt assets under `genai/`. The sync tool treats `genai/skills` and `genai/agents` as canonical sources, and mirrors into tool-specific folders under `genai/`.

## Can I add new tool targets?

Yes. Update `references/mapping-spec.md` first, then extend the planner in `scripts/ai_prompt_standardizer.py`.
