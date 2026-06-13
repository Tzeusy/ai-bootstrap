# Render Checklist

After every significant edit:

1. Render the file with `uv run scripts/render_excalidraw.py path/to/file.excalidraw`.
2. Read any renderer layout warnings before looking at the image.
3. Inspect the image.
4. Fix anything that weakens clarity.
   Rewrite tight labels first, then re-break lines, then resize containers if needed.
5. Re-render.

## Check For

- text clipping
- boxed labels using more than about 70-75% of container width
- boxed labels using more than about 60-65% of container height
- boxed labels with less than about 24px horizontal or 14px vertical padding
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
- boxed labels have comfortable padding, not edge-to-edge lines
- the composition looks balanced without caveats
