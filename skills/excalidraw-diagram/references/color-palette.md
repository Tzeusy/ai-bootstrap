# Color Palette & Brand Style

**This is the single source of truth for all colors and brand-specific styles.** To customize diagrams for your own brand, edit this file — everything else in the skill is universal.

---

## Shape Colors (Semantic)

Colors encode meaning, not decoration. Each semantic purpose has a fill/stroke pair.

| Semantic Purpose | Fill | Stroke |
|------------------|------|--------|
| Primary/Neutral | `#3b82f6` | `#1e3a5f` |
| Secondary | `#60a5fa` | `#1e3a5f` |
| Tertiary | `#93c5fd` | `#1e3a5f` |
| Start/Trigger | `#fed7aa` | `#c2410c` |
| End/Success | `#a7f3d0` | `#047857` |
| Warning/Reset | `#fee2e2` | `#dc2626` |
| Decision | `#fef3c7` | `#b45309` |
| AI/LLM | `#ddd6fe` | `#6d28d9` |
| Inactive/Disabled | `#dbeafe` | `#1e40af` (use dashed stroke) |
| Error | `#fecaca` | `#b91c1c` |

**Rule**: Always pair a darker stroke with a lighter fill for contrast.

---

## Text Colors (Hierarchy)

Use color on free-floating text to create visual hierarchy without containers.

| Level | Color | Use For |
|-------|-------|---------|
| Title | `#1e40af` | Section headings, major labels |
| Subtitle | `#3b82f6` | Subheadings, secondary labels |
| Body/Detail | `#64748b` | Descriptions, annotations, metadata |
| On light fills | `#374151` | Text inside light-colored shapes |
| On dark fills | `#ffffff` | Text inside dark-colored shapes |

---

## Evidence Artifact Colors

Used for code snippets, data examples, and other concrete evidence inside technical diagrams.

| Artifact | Background | Text Color |
|----------|-----------|------------|
| Code snippet | `#1e293b` | Syntax-colored (language-appropriate) |
| JSON/data example | `#1e293b` | `#22c55e` (green) |

---

## Default Stroke & Line Colors

| Element | Color |
|---------|-------|
| Arrows | Use the stroke color of the source element's semantic purpose |
| Structural lines (dividers, trees, timelines) | Primary stroke (`#1e3a5f`) or Slate (`#64748b`) |
| Marker dots (fill + stroke) | Primary fill (`#3b82f6`) |

---

## Background

| Property | Light | Dark |
|----------|-------|------|
| Canvas background | `#ffffff` | `#1e1e2e` |

---

## Dark Mode

Dark mode is applied automatically by the render script via `--dark`. You do **not** need to create separate `.excalidraw` files — author diagrams in light mode and the renderer transforms colors at render time.

```bash
# Render light (default)
uv run python render_excalidraw.py diagram.excalidraw --format svg

# Render dark (auto-transforms colors, outputs diagram_dark.svg)
uv run python render_excalidraw.py diagram.excalidraw --format svg --dark
```

### Dark Mode Shape Colors

Fills become darker, strokes become lighter — maintaining contrast on the dark canvas.

| Semantic Purpose | Fill (dark) | Stroke (dark) |
|------------------|-------------|---------------|
| Primary/Neutral | `#1e40af` | `#7dd3fc` |
| Secondary | `#1e40af` | `#7dd3fc` |
| Tertiary | `#1e3a5f` | `#7dd3fc` |
| Start/Trigger | `#7c2d12` | `#fb923c` |
| End/Success | `#064e3b` | `#34d399` |
| Warning/Reset | `#7f1d1d` | `#f87171` |
| Decision | `#78350f` | `#fbbf24` |
| AI/LLM | `#4c1d95` | `#a78bfa` |
| Inactive/Disabled | `#1e3a5f` | `#93c5fd` |
| Error | `#7f1d1d` | `#f87171` |

### Dark Mode Text Colors

| Level | Color (dark) |
|-------|-------------|
| Title | `#93c5fd` |
| Subtitle | `#60a5fa` |
| Body/Detail | `#94a3b8` |
| On dark fills | `#e2e8f0` |
| On evidence artifacts | `#ffffff` (unchanged) |

### Colors That Don't Change

Evidence artifact backgrounds (`#1e293b`), evidence text (`#22c55e`), and white text (`#ffffff`) are already dark-mode native and are preserved as-is.
