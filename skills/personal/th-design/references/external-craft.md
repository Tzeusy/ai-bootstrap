# Optional External Craft Setup

Read this only when a project explicitly needs the deep iterative frontend
polish workflow from `pbakaus/impeccable`.

Load `~/.agents/vendor/impeccable/SKILL.md` by path. The package stays outside
scanned skill directories because its broad triggers collide with `th-design`.
It expects a project-side `.agents/skills/impeccable/` installation and runs
`node .agents/skills/impeccable/scripts/load-context.mjs` from the project
root, using its PRODUCT.md and DESIGN.md conventions.

If that wiring is absent, use
[`frontend-design`](../subskills/frontend-design/SKILL.md). In either case,
the selected workflow remains subject to the project's design system and the
[`design-bar`](../subskills/design-bar/SKILL.md).
