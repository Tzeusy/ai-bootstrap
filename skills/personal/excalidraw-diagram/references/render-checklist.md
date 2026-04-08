# Render Checklist

After every significant edit:

1. Render the file with `uv run scripts/render_excalidraw.py path/to/file.excalidraw`.
2. Inspect the image.
3. Fix anything that weakens clarity.
4. Re-render.

## Check For

- text clipping
- overlapping elements
- arrows landing on the wrong element
- arrows cutting through labels or boxes
- uneven spacing
- weak hierarchy
- unreadable evidence artifacts
- lopsided composition

## Stop When

- the visual structure matches the intended conceptual structure
- the diagram is readable at export size
- the composition looks balanced without caveats
