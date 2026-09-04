# Project-Level Craft-And-Care Gate

Shared by `beads-worker` and `beads-pr-reviewer-worker`. Some repositories
define a project-local `craft-and-care` skill (usually a `doctrine` subskill
per `th-projects`) as the execution-quality bar for implementation work.

## Discovery

Before the first edit (worker) or the first finding (reviewer), look for a
repo-owned `craft-and-care/SKILL.md` in the worktree's standard skill
locations (`.claude/skills/**`, `about/craft-and-care/`). If none exists,
continue with the dispatching subskill alone — this gate adds nothing.

## When it exists

- Read it once, before implementation or review; it is a required quality bar,
  not advice.
- Worker: follow it while implementing. Reviewer: use it as the bar for
  findings and merge readiness.
- Both: run one final standards pass against the **actual diff** before
  handoff. At minimum confirm the change does not violate the project's
  explicit standards around:
  - cleanup versus compatibility cruft,
  - readability and simplicity over cleverness,
  - explicitness over hidden magic,
  - fail-fast behavior over silent fallback unless the project says otherwise,
  - same-change documentation or contract updates when behavior changed,
  - risk-scaled verification depth.

The pass is a check against the project's written bar; it never widens scope
or overrides the bead's acceptance criteria.
