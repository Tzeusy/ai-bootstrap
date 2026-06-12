# Excalidraw JSON Notes

## Required Top-Level Fields

- `type`
- `version`
- `source`
- `elements`
- `appState`
- `files`

## Skill-Specific App State

Set these fields when generating diagrams for this skill:

```json
{
  "viewBackgroundColor": "<theme background>",
  "gridSize": 20,
  "excalidrawDiagramTheme": "default"
}
```

`excalidrawDiagramTheme` lets the renderer infer the source theme when exporting to another catalog theme.

## Common Element Types

- `rectangle`: process or concrete component
- `ellipse`: start, end, or soft boundary
- `diamond`: decision
- `arrow`: directional relationship
- `line`: structural guide
- `text`: label or annotation

## Reminders

- `text` and `originalText` should contain only human-readable content.
- Use `fontFamily: 3`.
- Keep `opacity: 100` unless a user explicitly wants a different effect.
- Use `roundness: { "type": 3 }` for rounded rectangles.
