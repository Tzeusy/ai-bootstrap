---
name: th-workflow
description: >
  Use for the day-to-day development workflow around a change, idea to
  merged branch: brainstorming intent and design before building or
  modifying a feature; executing a written implementation plan in
  checkpointed batches; dispatching parallel subagents for independent
  problems; requesting a code review before merge; verifying review
  feedback before acting on it; finishing a branch (merge, PR, keep,
  discard). Triggers: "brainstorm this feature", "design before building",
  "execute this plan", "these failures look independent", "request a
  review", "the reviewer says", "merge or PR?", "clean up this branch".
metadata:
  owner: tze
  authors:
    - obra/superpowers (upstream)
    - tze
    - Claude Fable 5.1
  status: active
  last_reviewed: "2026-09-02"
---

# TH Workflow

Superskill router for the change lifecycle: design → plan execution →
review → integration. Six subskills live under `subskills/`, each a complete
skill package (maintained forks of `obra/superpowers`), discovered lazily —
load **at most one** subskill body per step.

This superskill governs *procedure* around a change. The *quality* of the
code is `/th-engineering`; project-level specs and prioritization are
`/th-projects`; unattended Beads issue execution has its own worker flows in
`/beads-orchestration` and does not route here.

## Routing table

| Task intent | Subskill | Typical trigger |
|---|---|---|
| Turn an idea into a validated design before implementation: one question at a time, 2–3 approaches, design presented in sections. | [subskills/brainstorming/SKILL.md](subskills/brainstorming/SKILL.md) | "brainstorm this feature", "design this before we build", "what should this look like" |
| Execute a written plan in batches with review checkpoints; stop on blockers instead of guessing. | [subskills/executing-plans/SKILL.md](subskills/executing-plans/SKILL.md) | "execute this plan", "work through docs/plans/…" |
| Two or more independent problems (different test files, subsystems, bugs): one subagent per domain, run concurrently, integrate results. | [subskills/dispatching-parallel-agents/SKILL.md](subskills/dispatching-parallel-agents/SKILL.md) | "these failures are unrelated", "investigate these in parallel" |
| Dispatch a reviewer subagent over a git range with the bundled prompt template; act on findings by severity. | [subskills/requesting-code-review/SKILL.md](subskills/requesting-code-review/SKILL.md) | "request a review", "review before I merge" |
| Handle incoming review feedback: verify before implementing, push back with evidence, no performative agreement. | [subskills/receiving-code-review/SKILL.md](subskills/receiving-code-review/SKILL.md) | "the reviewer says…", "should I apply this suggestion" |
| Implementation complete and tests green: verify, present merge / PR / keep / discard, execute the choice, clean up the worktree. | [subskills/finishing-a-development-branch/SKILL.md](subskills/finishing-a-development-branch/SKILL.md) | "I'm done, what now", "merge or PR", "clean up this branch" |

## Routing rules

- **Lifecycle order**: brainstorming → executing-plans → requesting-code-review
  (↔ receiving-code-review) → finishing-a-development-branch. Each subskill
  names its successor; load the successor only when that step arrives.
- **Design depth**: a repo with `about/` shape docs and an OpenSpec surface
  takes feature design through `/th-projects` (project-feature-request);
  brainstorming here is the lightweight path for repos without one.
- **Review substance vs. review procedure**: *what* to check (readability,
  tests, dependencies, engineering bar) → `/th-engineering`; *how* to
  dispatch a reviewer or respond to one → here.
- **Parallelism**: dispatching-parallel-agents covers ad-hoc fan-out on
  independent problems. Beads-tracked work fans out through
  `/beads-orchestration` (beads-coordinator) instead.
- **Fallback**: workflow-adjacent but no row fits (writing the plan itself,
  git mechanics) → proceed with router-level guidance; do not load a
  subskill to browse.

## Discover subskills

The routing table above is the primary index. Verify frontmatter only if the
table seems stale:

```bash
PKG="$(dirname "<absolute-path-to-this-SKILL.md>")"
rg -n "^name:|^description:" "$PKG"/subskills/*/SKILL.md
```
