# Publish a visual

Read only when adding an image, diagram or PDF. Generate content with the
appropriate existing renderer; keep the dashboard shell fixed.

Put output under `<workspace>/artifacts/`, then include the relative path and
label in a checkpoint:

```json
{"artifacts":[{"path":"architecture.svg","label":"Workspace architecture"}]}
```

Artifacts merge by `path`; `{"path":"old.svg","drop":true}` unpublishes one. For a
chart or table built from numbers, prefer a [panel](protocol.md#panels): it
needs no renderer and no file.
Supported formats: PNG, JPEG, WebP, GIF, SVG, PDF and Excalidraw source. Use the
existing Excalidraw renderer for diagrams; publish rendered output alongside
source when useful. PDFs and source files download as attachments.

Only explicitly listed existing files below `artifacts/` are served. Paths must
be visible and relative; symlinks, traversal, hidden paths and `secrets` or
`credentials` components are rejected. HTML/JS files are not dashboard plugins.
Keep credentials and raw transcripts out of snapshots, rendered artifacts and
downloadable sources.
