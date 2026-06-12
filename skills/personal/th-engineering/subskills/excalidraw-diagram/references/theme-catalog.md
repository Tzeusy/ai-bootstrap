# Theme Catalog

Themes live in `references/themes/catalog.json` and individual JSON theme files in `references/themes/`.

## How to Use

1. Pick a theme name from the catalog. If the user does not request one, use `default`.
2. Read the matching theme file before generating diagram colors.
3. Set `appState.excalidrawDiagramTheme` to the selected theme name in the `.excalidraw` file.
4. Set `appState.viewBackgroundColor` to the theme's `background`.

## Theme Shape

Each theme file declares:

- `name`
- `mode`
- `background`
- `fills`
- `strokes`
- `text`
- `evidence`

Mode is implicit in the theme. Do not add a separate dark-mode switch.

## Default Theme

If no theme is specified, use the default theme from the catalog. The current default is a dark VS Code-inspired palette.

## Available Themes

- `default`: dark default palette for the skill
- `vscode-dark`: updated VS Code dark theme
- `vscode-light`: updated VS Code light theme
- `midnight`: cool dark blue variant
- `monokai`: vibrant high-contrast dark theme
- `solarized-dark`
- `solarized-light`
- `tomorrow-night-blue`
- `abyss`
- `kimbie-dark`
- `red`
- `quiet-light`

## Authoring Rule

Do not invent colors inside the skill. All color choices must come from the selected theme file.
