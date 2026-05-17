# Superskills

Use this reference when a skill package needs broader scope than one workflow
but should still stay cheap to discover and load.

## Definition

A superskill is one of the two valid skill package shapes:

- `skill`: a standard agentskills.io-style skill package with one top-level
  `SKILL.md` and optional `references/`, `scripts/`, and `assets/`.
- `superskill`: a router package with one top-level `SKILL.md` plus
  `subskills/`, where each subskill is itself a standard skill package.

The superskill's public job is routing. It owns one broad trigger in the global
skill catalog, then directs the agent to internal subskills only when the task
needs them.

The context contract is:

- The top-level `SKILL.md` frontmatter is the only superskill metadata that
  belongs in the global skill catalog.
- Internal subskills are package-local resources, not separately installed
  top-level skills.
- The router body may tell the agent how to inspect subskill frontmatter, but
  subskill bodies are read only after the router selects a relevant subskill.

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
  agents/openai.yaml
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

Use `subskills/` for internal workflows that have their own trigger, workflow,
and support files. Use `references/` for documents the router or subskills read
as supporting context.

Each `subskills/<name>/` directory should follow the standard skill shape:

```text
subskills/workflow-a/
  SKILL.md
  agents/openai.yaml
  references/
  scripts/
  assets/
```

Only include `agents/openai.yaml`, `references/`, `scripts/`, or `assets/` when
the subskill needs them.

## Router Requirements

The top-level router `SKILL.md` should:

- Use trigger-oriented frontmatter for the broad capability, not a list of every
  internal workflow.
- State that internal subskills are discovered lazily from `subskills/`.
- Give a cheap lookup method, such as:

```bash
find subskills -maxdepth 2 -name SKILL.md -print
rg -n "^name:|^description:" subskills
```

- Define the selection criteria for each subskill in one concise routing table.
- Load at most one or two subskills for an ordinary task.
- Say what to do when no subskill fits: continue with router-level guidance,
  ask for clarification, or create a new subskill if the user requested skill
  maintenance.

## Subskill Requirements

Each internal subskill should:

- Have valid `SKILL.md` frontmatter with `name` and `description`.
- Use a name scoped to the package, for example
  `superskill-workflow-a`, so reports and validation output stay unambiguous.
- Keep its description trigger-oriented even though it is not globally loaded.
- Link its own support files directly.
- Avoid restating router policy unless the subskill needs a local hard stop.
- Be usable after reading only the router plus that subskill.

## Validation

Before shipping a superskill:

- Verify the top-level skill with the normal skill validator.
- Verify every `subskills/*/SKILL.md` for valid frontmatter and link integrity,
  even if the platform does not load nested skills automatically.
- Test one broad user request that should trigger the router and select a
  subskill.
- Test one request that should stay inside the router or be declined because no
  subskill fits.
- Confirm install or mirror scripts do not flatten `subskills/` into the global
  skill directory unless that is an explicit product decision.

## Anti-Patterns

- Installing every internal subskill as a top-level skill, which defeats the
  context contract.
- Making the router a long combined manual instead of a selector.
- Hiding unrelated domains under one attractive broad name.
- Letting subskills depend on unlinked sibling files or unstated router context.
- Adding a subskill without updating the router table and verification cases.
