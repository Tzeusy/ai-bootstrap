# Superskills

Use when a skill package needs broader scope than one workflow but should
still stay cheap to discover and load.

## Definition

A superskill is one of the two valid skill package shapes:

- `skill`: a standard agentskills.io-style package with one top-level
  `SKILL.md` and optional `references/`, `scripts/`, and `assets/`.
- `superskill`: a router package with one top-level `SKILL.md` plus
  `subskills/`, where each subskill is itself a standard skill package.

`subskills/` is a **local extension** to the agentskills.io spec, not part of
it. Portable consumers ignore the directory; this repo's `bootstrap.sh` prunes
`subskills/` during install so subskill metadata never reaches the global
catalog. That prune is part of the contract, not an accident.

The superskill's public job is routing. It owns one broad trigger in the
global skill catalog, then directs the agent to internal subskills only when
the task needs them.

The context contract:

- The top-level `SKILL.md` frontmatter is the only superskill metadata that
  belongs in the global skill catalog.
- Internal subskills are package-local resources, not separately installed
  top-level skills.
- The router body may tell the agent how to inspect subskill frontmatter, but
  subskill bodies load only after the router selects a relevant subskill.

## When To Use

Use a superskill when all of these are true:

- The domain has several coherent workflows that users naturally name as one
  capability.
- Each workflow has enough instructions, tools, or constraints to deserve its
  own `SKILL.md`.
- Loading every workflow's trigger metadata globally would create catalog noise
  or cause unrelated triggers to fire.
- A small router can choose the relevant workflow from user intent, repo
  context, file type, command name, or risk profile.

Do not use a superskill when:

- One lean `SKILL.md` plus a few references is enough.
- The internal workflows should be independently discoverable from the global
  skill catalog.
- The router would need to read most subskill bodies before it can decide.
- The package is only grouping loosely related skills for organizational
  convenience.

## Package Shape

Prefer this layout:

```text
superskill/
  SKILL.md
  agents/openai.yaml        # optional tool adapter
  subskills/
    workflow-a/
      SKILL.md
      references/
      scripts/
    workflow-b/
      SKILL.md
      references/
      scripts/
  references/
    router-policy.md
  scripts/
    optional-router-helper.py
```

Use `subskills/` for internal workflows with their own trigger, workflow, and
support files. Use `references/` for documents the router or subskills read as
supporting context. Include adapter files, `references/`, `scripts/`, or
`assets/` in a subskill only when it needs them.

## Router Requirements

The top-level router `SKILL.md` should:

- Use trigger-oriented frontmatter for the broad capability, not a list of every
  internal workflow.
- State that internal subskills are discovered lazily from `subskills/`.
- Give a cheap, location-independent lookup method. Resolve the package root
  from the `SKILL.md` path the agent actually loaded — do not assume the
  current working directory is the package:

```bash
PKG="$(dirname "<absolute-path-to-this-SKILL.md>")"
find "$PKG/subskills" -maxdepth 2 -name SKILL.md
rg -n "^name:|^description:" "$PKG"/subskills/*/SKILL.md
```

- Define the selection criteria for each subskill in one concise routing
  table, with a direct link to each `subskills/<name>/SKILL.md`.
- Load at most one or two subskills for an ordinary task.
- Keep realistic selection examples unloaded in `evals/routing.json`, with a
  positive case for every subskill plus negative and ambiguous cases.
- Say what to do when no subskill fits: continue with router-level guidance,
  ask for clarification, or create a new subskill if the user requested skill
  maintenance.

## Subskill Requirements

Each internal subskill should:

- Have valid `SKILL.md` frontmatter with `name` and `description`.
- Use a name that matches its directory and is unique across the repo's
  skills, so reports and validation output stay unambiguous. A short shared
  prefix is recommended when the package has a natural one (this repo's
  practice: `beads-coordinator`, `beads-worker` under `beads-orchestration`;
  `project-shape`, `project-review` under `th-projects`) — the full
  superskill name as a prefix is not required.
- Keep its description trigger-oriented even though it is not globally loaded.
- Link its own support files directly.
- Avoid restating router policy unless the subskill needs a local hard stop.
- Be usable from the router plus that subskill alone.

## Validation

Before shipping a superskill, run the package audit — it validates the router
and every subskill (frontmatter, spec limits, link integrity, PEP 723 on
scripts, routing-table coverage of each subskill):

```bash
uv run <skill-standards>/scripts/audit_skill.py <superskill-dir>
```

Then verify by hand:

- Confirm `evals/routing.json` passes schema and positive route-coverage
  validation. These cases are test inputs, not runtime router prose.
- Test one broad user request that should trigger the router and select a
  subskill.
- Test one request that should stay inside the router or be declined because no
  subskill fits.
- Confirm install or mirror scripts do not flatten `subskills/` into the global
  skill directory unless that is an explicit product decision (in this repo,
  `bootstrap.sh` prunes `subskills/` — keep it that way).

## Anti-Patterns

- Installing every internal subskill as a top-level skill, which defeats the
  context contract.
- Making the router a long combined manual instead of a selector.
- Hiding unrelated domains under one attractive broad name.
- Letting subskills depend on unlinked sibling files or unstated router context.
- Adding a subskill without updating the router table and verification cases.
