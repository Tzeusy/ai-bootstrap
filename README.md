# ai-bootstrap

Portable AI coding assistant configs, agents, and skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Codex](https://github.com/openai/codex), [Gemini CLI](https://github.com/google-gemini/gemini-cli), and [OpenCode](https://github.com/opencode-ai/opencode). Designed to be cloned (or added as a git submodule) and symlinked into your home directory.

## Structure

```
.claude/          # Claude Code config (CLAUDE.md, settings, plugins)
.codex/           # Codex config (AGENTS.md, config.toml, prompts)
.gemini/          # Gemini CLI config (GEMINI.md, settings, agents)
opencode/         # OpenCode config
agents/           # Tool-agnostic agent fleet (6 specialized roles)
skills/           # 70+ skills (SKILL.md entry points)
```

## Quick Start

```bash
# Clone
git clone --recursive https://github.com/Tzeusy/ai-bootstrap.git

# Symlink tool configs into your home directory
ln -sfn "$(pwd)/ai-bootstrap/.claude" ~/.claude
ln -sfn "$(pwd)/ai-bootstrap/.codex" ~/.codex
ln -sfn "$(pwd)/ai-bootstrap/.gemini" ~/.gemini

# Skills need to be copied/symlinked into each tool's skills directory
# Example for Claude Code:
mkdir -p ~/.claude/skills
for skill in ai-bootstrap/skills/*/SKILL.md; do
  name="$(basename "$(dirname "$skill")")"
  ln -sfn "$(dirname "$(realpath "$skill")")" ~/.claude/skills/"$name"
done
```

## Agent Fleet

A cooperative 6-agent fleet for structured software delivery. Agents operate across four phases (Plan, Implement, Review, Ship) with feedback loops and quality gates.

| Agent | Role |
|-------|------|
| **project-manager** | Coordinates fleet, decomposes work, delegates tasks |
| **developer** | Implements features, writes code |
| **designer** | Design system, component specs, UX review |
| **security** | Threat model, security requirements, audit |
| **tester** | Test strategy, test suites, verification |
| **reviewer** | Code review, architecture audit, release gate |

See [`agents/AGENTS.md`](agents/AGENTS.md) for the full specification.

## Skills

Skills are self-contained prompts that extend LLM tool capabilities. Each skill lives in `skills/<name>/SKILL.md`.

Categories include:
- **Development workflow** -- test-driven-development, systematic-debugging, verification-before-completion, dispatching-parallel-agents
- **Code quality** -- requesting-code-review, receiving-code-review, cruft-cleanup, finishing-a-development-branch
- **Content creation** -- blogpost-editor, blogpost-formatter, content-research-writer, doc-coauthoring
- **Design & art** -- frontend-design, canvas-design, algorithmic-art, excalidraw-diagram-skill
- **Document handling** -- pdf, docx, pptx, xlsx
- **Planning** -- writing-plans, executing-plans, brainstorming, software-architecture-documentation
- **Agents & AI** -- writing-agents, mcp-builder, claude-api, skill-creator
- **Productivity** -- file-organizer, invoice-organizer, changelog-generator, domain-name-brainstormer

## Customization

Machine-specific settings that should **not** be committed:

- **`.codex/config.toml`**: Add your `[projects."..."]` sections and `[[skills.config]]` entries with absolute paths
- **`.gemini/settings.json`**: Set your `telemetry.otlpEndpoint` if using OpenTelemetry
- **Skills**: Add private skills to `.gitignore` (e.g., `skills/my-private-skill/`)

## License

[MIT](LICENSE)
