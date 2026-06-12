# Element Templates

Copy-paste JSON scaffolds for Excalidraw elements. Pull actual colors from the selected theme file, not from hardcoded examples.

## Theme Reminder

Before generating elements:

1. Read `references/theme-catalog.md`.
2. Choose a theme.
3. Use colors from that theme file.
4. Set `appState.excalidrawDiagramTheme` in the document.

## Free-Floating Text

```json
{
  "type": "text",
  "id": "label1",
  "x": 100,
  "y": 100,
  "width": 200,
  "height": 25,
  "text": "Section Title",
  "originalText": "Section Title",
  "fontSize": 20,
  "fontFamily": 3,
  "textAlign": "left",
  "verticalAlign": "top",
  "strokeColor": "<theme text color>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 11111,
  "version": 1,
  "versionNonce": 22222,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": null,
  "lineHeight": 1.25
}
```

## Line

```json
{
  "type": "line",
  "id": "line1",
  "x": 100,
  "y": 100,
  "width": 0,
  "height": 200,
  "strokeColor": "<theme structural stroke>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 44444,
  "version": 1,
  "versionNonce": 55555,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [0, 200]]
}
```

## Rectangle

```json
{
  "type": "rectangle",
  "id": "elem1",
  "x": 100,
  "y": 100,
  "width": 180,
  "height": 90,
  "strokeColor": "<theme stroke>",
  "backgroundColor": "<theme fill>",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 12345,
  "version": 1,
  "versionNonce": 67890,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": [{"id": "text1", "type": "text"}],
  "link": null,
  "locked": false,
  "roundness": {"type": 3}
}
```

## Centered Text In A Shape

```json
{
  "type": "text",
  "id": "text1",
  "x": 130,
  "y": 132,
  "width": 120,
  "height": 25,
  "text": "Process",
  "originalText": "Process",
  "fontSize": 16,
  "fontFamily": 3,
  "textAlign": "center",
  "verticalAlign": "middle",
  "strokeColor": "<theme text color>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 1,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 11111,
  "version": 1,
  "versionNonce": 22222,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "containerId": "elem1",
  "lineHeight": 1.25
}
```

## Arrow

```json
{
  "type": "arrow",
  "id": "arrow1",
  "x": 282,
  "y": 145,
  "width": 118,
  "height": 0,
  "strokeColor": "<theme stroke>",
  "backgroundColor": "transparent",
  "fillStyle": "solid",
  "strokeWidth": 2,
  "strokeStyle": "solid",
  "roughness": 0,
  "opacity": 100,
  "angle": 0,
  "seed": 33333,
  "version": 1,
  "versionNonce": 44444,
  "isDeleted": false,
  "groupIds": [],
  "boundElements": null,
  "link": null,
  "locked": false,
  "points": [[0, 0], [118, 0]],
  "startBinding": {"elementId": "elem1", "focus": 0, "gap": 2},
  "endBinding": {"elementId": "elem2", "focus": 0, "gap": 2},
  "startArrowhead": null,
  "endArrowhead": "arrow"
}
```
