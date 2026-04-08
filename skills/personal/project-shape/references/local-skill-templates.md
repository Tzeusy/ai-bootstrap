# Local Skill Templates

Install these as `.claude/skills/<name>/SKILL.md` (and equivalents for `.codex/`, `.gemini/`, etc.) in the target project. Each skill is an **index** — it tells agents which file to read for a given task, not what the file says.

**CRITICAL FORMAT REQUIREMENT:** Every SKILL.md file **MUST** begin with YAML frontmatter delimited by `---`. Without frontmatter, skill loaders silently reject the file. Supported fields: `name` and `description`. Do not omit the opening or closing `---` delimiters. Do not start the file with a markdown heading.

Customize the tables and rules for your project's specific domains.

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

## Template: law-and-lore

```yaml
---
name: law-and-lore
description: >
  Load design contracts (RFCs) to contextualize implementation work. The about/law-and-lore/
  directory contains numbered design documents defining wire-level contracts, data models, state
  machines, and quantitative budgets. Consult relevant RFCs before implementing features, writing
  protocol definitions, designing state machines, or resolving cross-subsystem integration
  questions. Selectively load ONLY the RFCs relevant to your current task.
---

# Design Contracts — Law and Lore

The `about/law-and-lore/` directory contains the authoritative design contracts. These are
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
| 0001 | `about/law-and-lore/rfcs/0001-<name>.md` | [domain] | [summary] |
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

## Four-Pillar Model

| Layer | Location | Role |
|-------|----------|------|
| Doctrine | `about/heart-and-soul/` | WHY — philosophical foundations |
| Design Contracts | `about/law-and-lore/` | HOW — wire-level contracts |
| Capability Specs | `openspec/` | WHAT — normative requirements with testable scenarios |
| Topology | `about/lay-and-land/` | WHERE — component boundaries and connections |

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
| Underlying wire contracts | `/law-and-lore` |
| Philosophical foundations | `/heart-and-soul` |
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
| How a boundary communicates | `/law-and-lore` |
| What a component must do | `/spec-and-spine` |
```

## Installation

For each template:

1. Create `.claude/skills/<name>/SKILL.md` in the target project
2. Replace placeholder tables with your project's actual files and domains
3. Repeat for `.codex/skills/` and `.gemini/skills/` if using those tools

All four skills should be installed: `heart-and-soul`, `law-and-lore`, `spec-and-spine`, `lay-and-land`.

The templates above are starting points — customize heavily for your project's specific domains, files, and conventions.

Before relying on these local skills, remove scaffold markers/placeholders and run:

```bash
bash <skill-path>/scripts/shape-scan.sh [project-root]
bash <skill-path>/scripts/self-test.sh
```
