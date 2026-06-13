# Excalidraw Diagram Skill

A coding-agent skill for generating Excalidraw diagrams that teach through structure, flow, and concrete evidence.

## Provenance

A vendored, improved fork of [coleam00/excalidraw-diagram-skill](https://github.com/coleam00/excalidraw-diagram-skill).

Verified local improvements in this copy:

- Self-contained renderer script with PEP 723 inline metadata
- Theme catalog support with a default theme and theme-bound light/dark mode
- Relative skill-root paths in docs and runtime instructions
- Slimmer `SKILL.md` with heavy guidance moved into reference files
- Prompt-level Mermaid-to/from-Excalidraw interoperability guidance
- Vendored Excalidraw browser bundle for local rendering

## What Makes This Different

- Diagrams argue visually instead of repeating prose as boxes and arrows.
- Technical diagrams use concrete evidence artifacts.
- The renderer exports and immediately supports visual QA loops.
- Colors come from a theme catalog, not hardcoded instructions.
- The prompt layer translates Mermaid into Excalidraw, or derives Mermaid from an Excalidraw scene, on request.

## Installation

In this repository, this vendored directory is the source of truth.

To use elsewhere, copy this directory into your agent's skills directory as `excalidraw-diagram`.

For the original standalone project, use the upstream repository: <https://github.com/coleam00/excalidraw-diagram-skill>.

## Setup

Install the Playwright browser binary for the self-contained renderer:

```bash
uv run scripts/render_excalidraw.py --install-browser
```

The Excalidraw browser bundle is vendored into this skill. Rendering stays local: the renderer serves the packaged bundle from a loopback HTTP endpoint so Chromium loads the module without reaching `esm.sh` or any external CDN.

To refresh that bundle to the latest upstream JS state from npm, run from the repo root:

```bash
scripts/refresh.sh
```

After that, render diagrams directly with:

```bash
uv run scripts/render_excalidraw.py path/to/file.excalidraw
```

## Themes

This skill uses a theme catalog. If the user requests no theme, use the default dark theme from `references/themes/catalog.json`.

To inspect or extend the catalog, read:

- `references/theme-catalog.md`
- `references/themes/catalog.json`

Available built-in themes:

- `default`
- `vscode-dark`
- `vscode-light`
- `midnight`
- `monokai`
- `solarized-dark`
- `solarized-light`
- `tomorrow-night-blue`
- `abyss`
- `kimbie-dark`
- `red`
- `quiet-light`

Example themed render:

```bash
uv run scripts/render_excalidraw.py path/to/file.excalidraw --theme midnight
```

## Usage

Ask your coding agent to create a diagram, for example:

> "Create an Excalidraw diagram showing how the AG-UI protocol streams events from an AI agent to a frontend UI"

The skill handles planning, JSON generation, rendering, and iteration.

It also supports Mermaid interoperability via prompting:

> "Convert this Mermaid flowchart into an Excalidraw diagram that is better for teaching"

> "Read this Excalidraw scene and produce equivalent Mermaid"

For a deterministic Mermaid export from an existing `.excalidraw` file, run:

```bash
uv run scripts/excalidraw_to_mermaid.py path/to/file.excalidraw
```

## File Structure

```text
excalidraw-diagram/
  SKILL.md
  scripts/
    excalidraw_to_mermaid.py
    render_excalidraw.py
  references/
    design-patterns.md
    element-templates.md
    json-schema.md
    mermaid-interoperability.md
    render-checklist.md
    render_template.html
    theme-catalog.md
    vendor/
      excalidraw.bundle.mjs
      excalidraw.bundle.version.json
    themes/
      abyss.json
      catalog.json
      default.json
      kimbie-dark.json
      monokai.json
      midnight.json
      quiet-light.json
      red.json
      solarized-dark.json
      solarized-light.json
      tomorrow-night-blue.json
      vscode-dark.json
      vscode-light.json
  tests/
    fixtures/
      skill-workflow.excalidraw
    output/
      skill-workflow-default.svg
      skill-workflow-midnight.svg
      skill-workflow.excalidraw
      skill-workflow.mmd
    test_skill_end_to_end.py
    test_render_excalidraw.py
    test_skill_package.py
    test_skill_docs.py
```
