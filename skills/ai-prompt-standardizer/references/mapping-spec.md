# Mapping Spec

## Base Directories

- Canonical sources live under `ai-bootstrap/skills/` and `ai-bootstrap/agents/`.
- Generated outputs mirror into `ai-bootstrap/.codex/`, `ai-bootstrap/.claude/`, `ai-bootstrap/.gemini/`, and `ai-bootstrap/.github/`.

## Skills Sync (Verbatim)

Source:
- `ai-bootstrap/skills/**` (recursive)

Destinations (verbatim mirror):
- `ai-bootstrap/.codex/skills/**`
- `ai-bootstrap/.claude/skills/**`
- `ai-bootstrap/.gemini/skills/**`
- `ai-bootstrap/.github/skills/**`

Rules:
- Preserve relative paths.
- Always overwrite destination files.
- Skip recursion into tool-specific folders (`.codex`, `.claude`, `.gemini`, `.github`).

## Professions Sync (Tool-Specific)

Source of truth:
- `ai-bootstrap/agents/AGENTS.md`
- `ai-bootstrap/agents/<path...>/AGENTS.md`

### Codex

- `ai-bootstrap/agents/AGENTS.md` → `ai-bootstrap/.codex/AGENTS.md`
- `ai-bootstrap/agents/<path...>/AGENTS.md` → `ai-bootstrap/.codex/<path...>/AGENTS.override.md`

### Claude

- `ai-bootstrap/agents/AGENTS.md` → `ai-bootstrap/.claude/CLAUDE.md`
- `ai-bootstrap/agents/<path...>/AGENTS.md` → `ai-bootstrap/.claude/<path...>/CLAUDE.md`

### Gemini

- `ai-bootstrap/agents/AGENTS.md` → `ai-bootstrap/.gemini/GEMINI.md`
- `ai-bootstrap/agents/<path...>/AGENTS.md` → `ai-bootstrap/.gemini/<path...>/GEMINI.md`

### GitHub Copilot (Agnostic Prompt Mirrors)

For each `ai-bootstrap/agents/<path...>/AGENTS.md`, generate one file under `ai-bootstrap/.github/agents/`.

Naming:
- Replace `/` with `__` in the path.
- `ai-bootstrap/agents/AGENTS.md` → `ai-bootstrap/.github/agents/root.agent.md`
- `ai-bootstrap/agents/application/backend/AGENTS.md` → `ai-bootstrap/.github/agents/application__backend.agent.md`

Content:
- Prepend a generated header pointing to the source path.
- Append the full AGENTS content verbatim with no tool-specific additions.
