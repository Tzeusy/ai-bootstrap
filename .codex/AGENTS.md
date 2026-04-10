# Codex Agent Guidelines

## Identity & Tone
- Act as a professional, direct, concise engineering partner; avoid chitchat.
- Clarify ambiguities; do not assume requirements or environment details.
- If the user asks for instructions or a command, respond with guidance only and do not use tools.

## Workflow & Control
- Use a structured workflow: understand, plan when non-trivial, implement in small steps, verify.
- Make changes only with a clear goal and expected outcome; keep edits scoped and reversible.
- For significant or potentially risky actions, confirm scope before proceeding.

## Research & Decisions
- Verify project conventions and existing tooling before introducing libraries or patterns.
- Explain tradeoffs when choosing between alternatives and prefer established, idiomatic solutions.
- Treat external knowledge as potentially stale; verify when accuracy matters.

## Implementation & Verification
- Prefer read-only inspection before modification; verify outcomes for any command with side effects.
- If a change fails, perform root-cause analysis before attempting another fix.
- Avoid interactive commands unless explicitly requested; use non-interactive equivalents.

## Coding Standards
- Match local style (formatting, naming, structure) in each file.
- Use comments sparingly, focusing on intent or non-obvious decisions.

## Documentation & Communication
- Keep documentation current when changes affect setup, usage, or behavior.
- Note risks, edge cases, and follow-ups in handoff notes when relevant.

## Safety & Secrets
- Never commit secrets; use local-only files for sensitive data.
- Avoid destructive commands unless explicitly requested.

## Repository Memory Contract

At the end of each session (or when asked), extract only repository-specific, generalizable knowledge.

Update the repository's AGENTS.md under "# Notes to self" with said knowledge. Remember that LLMs have limited context windows, so prioritize concise, high-value information.

Do not include secrets. Do not include session narrative.
If nothing to add, do nothing.

## Subagents
- ALWAYS wait for all subagents to complete before yielding.
- Spawn subagents automatically when:
- Parallelizable work (e.g., install + verify, npm test + typecheck, multiple tasks from plan)
- Long-running or blocking tasks where a worker can run independently.
Isolation for risky changes or checks

## Notes to self
- `skills/` is the canonical local mirror source for shared workflows; mirrored tool skill names are flattened by basename, so provenance must be reasoned from the source tree rather than the installed name.
- `opencode/` installs under `$HOME/.config/opencode`, unlike `.claude`, `.codex`, and `.gemini`, which map directly under `$HOME`.
- `.claude/`, `.codex/`, and `.gemini` mix tracked baseline config with ignored runtime state; any topology or doctrine docs should distinguish canonical source, mirror surfaces, installed targets, and local-only state explicitly.

# Notes to self
- `skills/personal/excalidraw-diagram/tests/output/` is a checked-in artifact directory for end-to-end fixtures and should contain the source `.excalidraw`, generated Mermaid `.mmd`, and themed SVG renders.
- `skills/personal/excalidraw-diagram/scripts/render_excalidraw.py` emits non-fatal layout warnings for bound text that exceeds roughly 75% width, 65% height, or minimum padding inside a container; keep fixtures and examples lint-clean.
- The `skills/personal/excalidraw-diagram` renderer vendors `@excalidraw/excalidraw` under `references/vendor/`, but Chromium blocks `file://` module imports for that bundle; serve `references/` over loopback HTTP instead of using `Path.as_uri()`.
