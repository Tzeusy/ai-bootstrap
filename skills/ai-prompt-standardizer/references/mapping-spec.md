# Mapping Spec

## Base Directories

- Canonical sources live under `genai/skills/` and `genai/agents/`.
- Generated outputs mirror into `genai/.codex/`, `genai/.claude/`, `genai/.gemini/`, and `genai/.github/`.

## Skills Sync (Verbatim)

Source:
- `genai/skills/**` (recursive)

Destinations (verbatim mirror):
- `genai/.codex/skills/**`
- `genai/.claude/skills/**`
- `genai/.gemini/skills/**`
- `genai/.github/skills/**`

Rules:
- Preserve relative paths.
- Always overwrite destination files.
- Skip recursion into tool-specific folders (`.codex`, `.claude`, `.gemini`, `.github`).

## Professions Sync (Tool-Specific)

Source of truth:
- `genai/agents/AGENTS.md`
- `genai/agents/<path...>/AGENTS.md`

### Codex

- `genai/agents/AGENTS.md` → `genai/.codex/AGENTS.md`
- `genai/agents/<path...>/AGENTS.md` → `genai/.codex/<path...>/AGENTS.override.md`

### Claude

- `genai/agents/AGENTS.md` → `genai/.claude/CLAUDE.md`
- `genai/agents/<path...>/AGENTS.md` → `genai/.claude/<path...>/CLAUDE.md`

### Gemini

- `genai/agents/AGENTS.md` → `genai/.gemini/GEMINI.md`
- `genai/agents/<path...>/AGENTS.md` → `genai/.gemini/<path...>/GEMINI.md`

### GitHub Copilot (Agnostic Prompt Mirrors)

For each `genai/agents/<path...>/AGENTS.md`, generate one file under `genai/.github/agents/`.

Naming:
- Replace `/` with `__` in the path.
- `genai/agents/AGENTS.md` → `genai/.github/agents/root.agent.md`
- `genai/agents/application/backend/AGENTS.md` → `genai/.github/agents/application__backend.agent.md`

Content:
- Prepend a generated header pointing to the source path.
- Append the full AGENTS content verbatim with no tool-specific additions.
