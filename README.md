# ai-bootstrap

Portable AI assistant configs and shared skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), [Codex](https://github.com/openai/codex), [Gemini CLI](https://github.com/google-gemini/gemini-cli), and [OpenCode](https://github.com/opencode-ai/opencode).

The current operating model is **skills-first**, not `agents/`-first. Shared workflows live in `skills/` and are mirrored into each tool's native skills directory. For day-to-day execution, the primary path is the Beads workflow under `skills/personal/`, especially `beads-coordinator`, `beads-worker`, and `beads-pr-reviewer-worker`.

## What This Repo Optimizes For

- One shared skill library that can be consumed by multiple CLI agents.
- Tool-native configs under `.claude/`, `.codex/`, and `.gemini/`.
- Beads-backed work management with explicit workflows instead of ad hoc TODOs.
- Isolated implementation via worktrees and PR-review follow-up via dedicated review workers.

## Structure

```text
.claude/           # Claude Code config and linked skill entrypoints
.codex/            # Codex config, prompts, rules, and linked skill entrypoints
.gemini/           # Gemini CLI config plus linked skills/antigravity skills
opencode/          # OpenCode config
skills/            # Canonical shared skill library
skills/personal/   # Primary home of Beads and project workflow skills
agents/            # Older agent prompts kept for reference / selective reuse
scripts/           # Helper scripts used by the genai setup
```

`agents/` still exists, but it is no longer the center of the system. Treat it as legacy/reference material unless you have a specific reason to use one of those prompts.

## Skills Layout And Provenance

The `skills/` tree is intentionally split by ownership:

- `skills/personal/` is the layer built and maintained by me.
- These are the primary place for custom workflow logic, project-shaping methods, and Beads execution patterns.
- Some personal skills are original; some are maintained forks adapted to my workflow. `skills/personal/excalidraw-diagram/` is an example of that pattern.

Everything else under top-level `skills/` should be treated as upstream-derived material:

- Some directories are checked out as git submodules from open source upstreams.
- The current submodules are `skills/superpowers`, `skills/Skill_Seekers`, `skills/anthropic-skills`, and `skills/notebooklm-skill`.
- Every other non-`personal/` skill directory is a vendored copy of an open source skill or skill bundle.

In practice, that means:

- If the workflow is specific to my operating model, it belongs in `skills/personal/`.
- If a top-level skill came from upstream, prefer updating from upstream or forking intentionally instead of casually rewriting the vendored copy.
- Tool-specific skill directories under `.claude/skills`, `.codex/skills`, and `.gemini/skills` are mirrors of this source tree, not the source of truth.

## Primary Workflow

### 1. Shared skills are canonical

Each skill lives in `skills/<name>/SKILL.md` or `skills/personal/<name>/SKILL.md`. Those source directories are symlinked into:

- `~/.claude/skills/`
- `~/.codex/skills/`
- `~/.gemini/skills/`
- `~/.gemini/antigravity/skills/`

The linked name is flattened, so `skills/personal/beads-worker/` becomes `beads-worker` in the tool-specific skills directory.

Because the linked namespace is flattened by basename, the canonical source remains the `skills/` tree. Provenance and ownership should always be reasoned about from the source directory, not from the mirrored tool-specific link.

### 2. Beads drives execution

The main personal workflow is:

1. Use `beads-writer` or normal `bd` commands to create and shape issues.
2. Start `beads-coordinator` to pull ready work from `bd ready`.
3. `beads-coordinator` runs `beads-cleanup`, claims work, creates isolated worktrees, and dispatches workers.
4. `beads-worker` executes one implementation issue in its own worktree.
5. `beads-pr-reviewer-worker` handles PR review follow-up, review threads, and merge-or-retry decisions, then reports the outcome back to the coordinator for Beads closure.

This is the preferred model for sustained throughput. The coordinator coordinates; workers implement or review.

### 3. Planning lives in skills too

Related personal workflow skills include:

- `project-shape` for doctrine/spec/topology setup
- `project-review` for repo audits
- `project-direction` for spec-driven prioritization
- `reconcile-spec-to-project` for spec/code reconciliation

## Quick Start

Clone this repo and symlink its tool configs into the standard locations in your home directory:

```bash
git clone --recursive https://github.com/Tzeusy/ai-bootstrap.git
cd ai-bootstrap

ln -sfn "$(pwd)/.claude" ~/.claude
ln -sfn "$(pwd)/.codex" ~/.codex
ln -sfn "$(pwd)/.gemini" ~/.gemini
```

Mirror the shared skills into each tool:

```bash
mkdir -p ~/.claude/skills ~/.codex/skills ~/.gemini/skills ~/.gemini/antigravity/skills

declare -A skill_map
while IFS= read -r -d '' skill; do
  dir="$(dirname "$skill")"
  name="$(basename "$dir")"
  skill_map["$name"]="$(realpath "$dir")"
done < <(find "$(pwd)/skills" -maxdepth 3 -type f -name SKILL.md -print0)

for name in "${!skill_map[@]}"; do
  dir="${skill_map[$name]}"
  ln -sfn "$dir" ~/.claude/skills/"$name"
  ln -sfn "$dir" ~/.codex/skills/"$name"
  ln -sfn "$dir" ~/.gemini/skills/"$name"
  ln -sfn "$dir" ~/.gemini/antigravity/skills/"$name"
done
```

If you prefer an explicit standalone mapping, the relevant targets are:

```bash
ln -sfn "$(pwd)/.claude" "$HOME/.claude"
ln -sfn "$(pwd)/.codex" "$HOME/.codex"
ln -sfn "$(pwd)/.gemini" "$HOME/.gemini"
mkdir -p "$HOME/.config"
ln -sfn "$(pwd)/opencode" "$HOME/.config/opencode"
```

This repo is intended to work standalone. Do not assume an enclosing parent repo or nested prefixes for local paths; the source of truth is this repository root, and the destination is the corresponding path under `$HOME`.

## Recommended Entry Points

- Want continuous issue execution: start with `beads-coordinator`
- Want to implement one already-assigned issue in a worktree: use `beads-worker`
- Want PR review follow-up and merge handling: use `beads-pr-reviewer-worker`
- Want to create or decompose backlog work: use `beads-writer`

## Customization

Machine-specific settings that should stay local:

- `.codex/config.toml` project entries and private absolute-path skill config
- `.gemini/settings.json` local telemetry or runtime settings
- `.gemini/installation_id`
- Any private skills you do not want in version control

## License

[MIT](LICENSE)
