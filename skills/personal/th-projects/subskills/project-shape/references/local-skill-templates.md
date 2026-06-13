# Local Skill Templates

Install as `.claude/skills/<name>/SKILL.md` (and `.codex/`, `.gemini/` equivalents) in the target project. Each skill is an **index** — which file to read for a task, not what the file says.

**CRITICAL FORMAT:** Every SKILL.md **MUST** begin with YAML frontmatter delimited by `---` (fields: `name`, `description`). Without it, loaders silently reject the file. Don't omit either `---` delimiter; don't start with a markdown heading.

**Authoring mandate:** Follow `agentskills.io` conventions + `/skill-creator` best practices; review against `/th-engineering` (skill-standards) before shipping. Means: valid minimal frontmatter, trigger-oriented `description`, concise routing body (don't repeat source material), explicit navigation cues so the agent loads only files needed for the current task, package-level alignment between `SKILL.md` and referenced support files.

**Progressive discovery mandate:** Design every pillar skill for targeted retrieval. `SKILL.md` = discovery/index layer; fan heavier/narrower content into `references/*.md`, `scripts/*`. Link support files directly from `SKILL.md` with "read when..." guidance — no hidden sidecars.

Customize tables and rules for your project's domains. After customizing any generated skill, run `/th-engineering` (skill-standards) as the final rubric pass for trigger quality, grounding, metadata hygiene, progressive discovery.

## Template: heart-and-soul

```yaml
---
name: heart-and-soul
description: >
  CRITICAL — Load the project's foundational doctrine before making architectural decisions,
  writing code, designing APIs, creating tests, or proposing features. The about/heart-and-soul/
  directory contains prime directives: what the system is, what it is not, how it works, and
  what v1 ships. Selectively load ONLY the documents relevant to your current task. Use
  proactively at the start of substantive work, when making design decisions, or when unsure
  about project conventions.
---

# Project Doctrine — Heart and Soul

The `about/heart-and-soul/` directory contains the prime directives of this project. These are
not documentation — they are doctrine. They define the principles the code must embody.

**Consult relevant soul files before:**
- Making any architectural or design decision
- Writing new modules, traits, or public APIs
- Proposing features or scope changes

**Do NOT load all files at once.** Select only what your current task requires.

## Document Index

### Always relevant
| File | Read when... | Key content |
|------|-------------|-------------|
| `about/heart-and-soul/vision.md` | Starting any session, scope questions | Core thesis, non-goals |
| `about/heart-and-soul/v1.md` | Implementing anything, scoping features | What v1 ships vs defers |

### Select by domain
| File | Read when... | Key content |
|------|-------------|-------------|
| `about/heart-and-soul/architecture.md` | Protocol, transport, rendering | Structural philosophy |
<!-- Add rows for each domain file -->

## Non-Negotiable Rules

<!-- Number your project's absolute rules here -->
1. [Rule from doctrine]
2. [Rule from doctrine]
```

## Template: legends-and-lore

```yaml
---
name: legends-and-lore
description: >
  Load design contracts (RFCs) to contextualize implementation work. The about/legends-and-lore/
  directory contains numbered design documents defining wire-level contracts, data models, state
  machines, and quantitative budgets. Consult relevant RFCs before implementing features, writing
  protocol definitions, designing state machines, or resolving cross-subsystem integration
  questions. Selectively load ONLY the RFCs relevant to your current task.
---

# Design Contracts — Legends and Lore

The `about/legends-and-lore/` directory contains the authoritative design contracts. These are
wire-level specifications that code must conform to.

**Consult relevant RFCs before:**
- Implementing any subsystem or feature
- Writing or modifying protocol definitions
- Setting or validating performance budgets
- Resolving how two subsystems interact

**Do NOT load all RFCs at once.** Select by task domain.

## RFC Index

### Foundation
| RFC | File | Read when... | Key content |
|-----|------|-------------|-------------|
| 0001 | `about/legends-and-lore/rfcs/0001-<name>.md` | [domain] | [summary] |
<!-- Add rows for each RFC -->

## Key Contracts

<!-- List load-bearing contracts that agents must know about -->
1. [Contract from RFCs]
2. [Contract from RFCs]
```

## Template: spec-and-spine

```yaml
---
name: spec-and-spine
description: >
  Ground all implementation work in capability specifications (openspec/). The capability
  specs are the single source of truth for feature planning and development. Use before
  implementing any feature, when detecting spec-code divergence, when evolving specs, or when
  planning new work. Triggers: "check the spec", "what does the spec say", "spec drift",
  "divergence", "reconcile", "does the code match the spec".
---

# Capability Specs — Spec and Spine

OpenSpec capability specifications are the backbone of this project. Every feature, every task,
every test traces back to a normative requirement in a spec.

## Five-Pillar Model

| Layer | Location | Role |
|-------|----------|------|
| Doctrine | `about/heart-and-soul/` | WHY — philosophical foundations |
| Design Contracts | `about/legends-and-lore/` | HOW — wire-level contracts |
| Capability Specs | `openspec/` | WHAT — normative requirements with testable scenarios |
| Topology | `about/lay-and-land/` | WHERE — component boundaries and connections |
| Engineering Standards | `about/craft-and-care/` | WHO WE ARE WHEN WE BUILD — engineering character in practice: implementation quality, verification, review, operability, maintainability |

## Domain Lookup

| Domain | Spec path | Source RFC |
|--------|-----------|------------|
| [Domain] | `openspec/changes/<change>/specs/<domain>/spec.md` | RFC NNNN |
<!-- Add rows for each spec -->

## Grounding Workflow

1. **Identify domains** — Which spec(s) does this work touch?
2. **Load selectively** — Read only relevant spec(s)
3. **Verify coverage** — Confirm requirements exist for planned behavior
4. **No requirement? Spec first.** — Write the spec before writing code
5. **Implement against scenarios** — WHEN/THEN scenarios are acceptance criteria
6. **Reconcile after** — Verify behavior matches spec post-implementation

## Quick Reference

| Need | Skill |
|------|-------|
| Underlying wire contracts | `/legends-and-lore` |
| Philosophical foundations | `/heart-and-soul` |
| Execution-quality standards | `/craft-and-care` |
```

## Template: lay-and-land

```yaml
---
name: lay-and-land
description: >
  Load the project's topology maps to understand where components live, how they connect,
  and what boundaries exist. The about/lay-and-land/ directory contains component inventories,
  data flow diagrams, dependency maps, and deployment topology. Consult before: adding new
  components, modifying integration points, changing deployment, or when unsure where something
  lives in the system. Use proactively when onboarding or when work crosses component boundaries.
---

# System Topology — Lay and Land

The `about/lay-and-land/` directory contains the spatial understanding of this project — where
components live, how data flows, what boundaries exist, and how the system is deployed.

**Consult topology maps before:**
- Adding or restructuring components
- Modifying integration points or APIs between subsystems
- Changing deployment targets or infrastructure
- Working on something that crosses component boundaries

**Do NOT load all maps at once.** Select by what you need to understand.

## Map Index

| Map | Read when... | Key content |
|-----|-------------|-------------|
| `about/lay-and-land/components.md` | Need to understand what exists and who owns what | Component inventory, boundaries, ownership |
| `about/lay-and-land/data-flow.md` | Need to understand how data moves | Data paths, transformations, trust boundaries |
| `about/lay-and-land/deployment.md` | Need to understand where things run | Environments, targets, infrastructure |
| `about/lay-and-land/dependencies.md` | Need to understand what depends on what | Internal + external dependencies |
<!-- Add rows for additional maps -->

## Key Boundaries

<!-- List the most important architectural boundaries -->
1. [Boundary from topology]
2. [Boundary from topology]

## Quick Reference

| Need | Skill |
|------|-------|
| Why a boundary exists | `/heart-and-soul` |
| How a boundary communicates | `/legends-and-lore` |
| What a component must do | `/spec-and-spine` |
| How changes here should be verified and maintained | `/craft-and-care` |
```

## Template: craft-and-care

```yaml
---
name: craft-and-care
description: >
  MANDATORY for all non-trivial implementation work. Load the project's execution-quality
  standards before implementing changes, reviewing pull requests, designing tests, altering
  APIs, adding dependencies, changing observability, or preparing documentation and operational
  updates. The about/craft-and-care/ directory defines how work must be implemented, verified,
  reviewed, documented, operated, and maintained here. Selectively load ONLY the files relevant
  to the current change.
---

# Engineering Standards — Craft and Care

The `about/craft-and-care/` directory contains this project's execution-quality standards.
These documents do not define what the system is for, how a subsystem works, what a feature
must do, or where components live. They define how changes must be carried out well here.

Read this pillar as the project's engineering character in action: not just "how to do the work,"
but what kind of engineer this project expects you to be while doing it.

This pillar should express stack-neutral engineering principles and reviewable expectations,
not technology recommendations. State standards in terms of evidence, invariants, change
safety, maintainability, and operational care.

This pillar adopts the canonical default quality bar from `/th-engineering` (engineering-bar
subskill) — nine default biases, definition of done, and the change-level subskills that
operationalize them — **by reference**. The documents here record only this project's
deviations: overridden biases (with reasons) and project-specific standards the default bar
does not cover. When this pillar conflicts with the default bar, this pillar wins.

**Consult relevant craft files before:**
- Any non-trivial implementation work
- Reviewing a pull request or preparing one for review
- Modifying a public API, interface, or shared schema
- Adding, upgrading, or removing dependencies
- Changing logging, metrics, tracing, alerts, or runtime behavior
- Deciding whether a bug fix, refactor, or feature is actually done

**Do NOT load the whole directory by default.** Start with `engineering-bar.md`, then load
only the narrower standards docs the current change needs.

## Document Index

| File | Read when... | Key content |
|------|-------------|-------------|
| `about/craft-and-care/README.md` | Orienting to the pillar | Scope boundary, reading order, file map |
| `about/craft-and-care/engineering-bar.md` | Any non-trivial change | Definition of done, maintainability bar, clarity standards, change hygiene |
| `about/craft-and-care/testing-and-verification.md` | Planning or judging evidence | Test expectations, regression discipline, verification thresholds |
| `about/craft-and-care/observability-and-operations.md` | Runtime-sensitive work | Logging, metrics, tracing, operational readiness, rollback/runbook expectations |
| `about/craft-and-care/interfaces-and-dependencies.md` | API or dependency changes | Compatibility, deprecation, versioning, dependency policy |
| `about/craft-and-care/review-and-documentation.md` | Review or handoff | Review standards, author/reviewer obligations, documentation update expectations |
| `about/craft-and-care/security-and-secrets.md` | Sensitive data or privileged changes | Secret handling, least privilege, unsafe-default hygiene |
| `about/craft-and-care/performance-discipline.md` | Performance-sensitive work | Measurement discipline, regression expectations, benchmark standards |

## Scope Guardrails

| If the question is... | Load... |
|-----------------------|---------|
| Why does this trade-off matter? | `/heart-and-soul` |
| How is this contract or subsystem designed? | `/legends-and-lore` |
| What behavior is required? | `/spec-and-spine` |
| Where does this component live and connect? | `/lay-and-land` |
| What quality evidence is required before merge or ship? | `/craft-and-care` |

## Default Biases

The default biases are not restated here. Load `/th-engineering` (engineering-bar subskill)
for the canonical list and definition of done; the narrower th-engineering subskills
(code-readability, test-rigor, dependency-hygiene, cruft-cleanup) operationalize individual
biases. This project's overrides and additions live in the Document Index files above and
take precedence over the defaults.

## Mandatory Use Rule

For non-trivial implementation work, this skill is not optional. If the task requires judgment
about testing, review quality, observability, compatibility, dependency hygiene, documentation,
security, performance discipline, or maintainability, load this pillar.
```

## Installation

For each template:

1. Create `.claude/skills/<name>/SKILL.md` in the target project
2. Replace placeholder tables with your project's actual files and domains
3. Repeat for `.codex/skills/` and `.gemini/skills/` if using those tools

All five skills should be installed: `heart-and-soul`, `legends-and-lore`, `spec-and-spine`, `lay-and-land`, `craft-and-care`.

The templates above are starting points — customize heavily for your project's specific domains, files, and conventions. When a pillar grows beyond a compact routing skill, split detail into targeted sub-docs or utilities instead of expanding `SKILL.md` into a monolith.

Before relying on these local skills, remove scaffold markers/placeholders and run:

```bash
bash <skill-path>/scripts/shape-scan.sh [project-root]
bash <skill-path>/scripts/self-test.sh
```
