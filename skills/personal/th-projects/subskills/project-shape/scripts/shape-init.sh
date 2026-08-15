#!/usr/bin/env bash
# shape-init.sh — Scaffold project shape: pillar directories and local skills
# Usage: shape-init.sh [project-root] [--pillars=1,2,3,4,5] [--skills-only] [--tools=claude,codex,gemini]
#
# Canonical layout:
#   about/heart-and-soul/  (doctrine)
#   about/legends-and-lore/    (design contracts / RFCs)
#   about/lay-and-land/    (topology / maps)
#   about/craft-and-care/  (engineering standards / execution quality)
#   openspec/             (capability specs — product, stays at root)
#   .<tool>/skills/doctrine/{SKILL.md,subskills/<pillar>/SKILL.md}
#                         (one router in the agent catalog; five pillar navigators under it)
#
# Idempotent: skips anything that already exists.
set -euo pipefail

ROOT="${1:-.}"
mkdir -p "$ROOT"
ROOT="$(cd "$ROOT" && pwd)"
PILLARS="1,2,3,4,5"
SKILLS_ONLY=false
TOOLS="claude"

# --- Parse args ---
shift || true
for arg in "$@"; do
  case "$arg" in
    --pillars=*) PILLARS="${arg#--pillars=}" ;;
    --skills-only) SKILLS_ONLY=true ;;
    --tools=*) TOOLS="${arg#--tools=}" ;;
    *) echo "Unknown arg: $arg"; exit 1 ;;
  esac
done

IFS=',' read -ra PILLAR_LIST <<< "$PILLARS"
IFS=',' read -ra TOOL_LIST <<< "$TOOLS"

created=0
skipped=0
SCAFFOLD_MARKER="<!-- SHAPE-SCAFFOLD: replace scaffold content with authored project-specific content -->"

# --- Helpers ---
create_file() {
  local path="$1" content="$2"
  if [ -f "$path" ]; then
    skipped=$((skipped + 1))
    return
  fi
  mkdir -p "$(dirname "$path")"
  printf '%s\n' "$content" > "$path"
  echo "  [CREATED] $path"
  created=$((created + 1))
}

create_dir() {
  local dir="$1"
  if [ -d "$dir" ]; then
    skipped=$((skipped + 1))
    return
  fi
  mkdir -p "$dir"
  echo "  [CREATED] $dir/"
  created=$((created + 1))
}

# Guard: repos on the optional .syzygy canon must not gain about/ mirrors of
# a pillar that already lives under .syzygy/ (one pillar, one home).
syzygy_canon_guard() {
  local pillar_label="$1" syzygy_dir="$2"
  if [ -d "$ROOT/$syzygy_dir" ]; then
    echo ""
    echo "## $pillar_label"
    echo "  [SKIPPED] $syzygy_dir/ exists — this repo keeps the pillar under the .syzygy canon; not scaffolding an about/ mirror"
    return 0
  fi
  return 1
}

# --- Pillar scaffolds ---
scaffold_heart_and_soul() {
  if [ "$SKILLS_ONLY" = true ]; then return; fi
  syzygy_canon_guard "Pillar 1: about/heart-and-soul/" ".syzygy/governance/doctrine" && return
  echo ""
  echo "## Pillar 1: about/heart-and-soul/"
  create_dir "$ROOT/about/heart-and-soul"
  create_file "$ROOT/about/heart-and-soul/README.md" "# Heart and Soul

$SCAFFOLD_MARKER

Project doctrine. Reading order:

1. \`vision.md\` — Core thesis, non-goals, non-negotiable rules
2. \`v1.md\` — What v1 ships vs defers

Add domain files as needed (security.md, failure.md, etc.)."

  create_file "$ROOT/about/heart-and-soul/vision.md" "# Vision

$SCAFFOLD_MARKER

## What is this?

<!-- One paragraph thesis statement -->

## What is this NOT?

<!-- 3-5 explicit non-goals -->

1.
2.
3.

## Non-Negotiable Rules

<!-- 5-7 numbered principles the code must embody -->

1.
2.
3.
4.
5.

## Success Criteria

<!-- How do you know this project is working? -->"

  create_file "$ROOT/about/heart-and-soul/v1.md" "# V1 Scope

$SCAFFOLD_MARKER

## V1 Ships

<!-- Explicit list of what the first version includes -->

-

## V1 Defers

<!-- Explicit list with rationale for each deferral -->

| Deferred | Rationale |
|----------|-----------|
| | |

## Platform Targets

-

## Quality Bar

<!-- Performance, reliability, UX thresholds -->"
}

scaffold_law_and_lore() {
  if [ "$SKILLS_ONLY" = true ]; then return; fi
  syzygy_canon_guard "Pillar 2: about/legends-and-lore/" ".syzygy/governance/contracts" && return
  echo ""
  echo "## Pillar 2: about/legends-and-lore/"
  create_dir "$ROOT/about/legends-and-lore"
  create_dir "$ROOT/about/legends-and-lore/rfcs"
  create_dir "$ROOT/about/legends-and-lore/reviews"
  create_file "$ROOT/about/legends-and-lore/README.md" "# Legends and Lore

$SCAFFOLD_MARKER

Numbered design contracts, RFCs, and review notes live here.

1. Start with \`rfcs/0001-TEMPLATE.md\`
2. Replace the template with a real RFC before relying on this pillar
3. Add review notes under \`reviews/\` as decisions evolve"

  create_file "$ROOT/about/legends-and-lore/rfcs/0001-TEMPLATE.md" "# RFC 0001: <Title>

$SCAFFOLD_MARKER

**Status:** Draft
**Author:** <name>
**Date:** $(date +%Y-%m-%d)

## Summary

<!-- One paragraph: what this RFC defines and why -->

## Motivation

<!-- What problem does this solve? Link to doctrine principles. -->

## Design

<!-- The technical contract: data models, state machines, wire formats, budgets -->

## Integration

<!-- How this subsystem connects to others -->

## Alternatives Considered

<!-- What was rejected and why -->

## V1 Scope

<!-- What ships in v1 vs defers -->"
}

scaffold_openspec() {
  if [ "$SKILLS_ONLY" = true ]; then return; fi
  echo ""
  echo "## Pillar 3: openspec/"
  create_dir "$ROOT/openspec"
  create_file "$ROOT/openspec/README.md" "# OpenSpec

$SCAFFOLD_MARKER

Capability specifications live here.

1. Create a real change under \`changes/<change-name>/\`
2. Add one or more authored \`spec.md\` files
3. Replace this scaffold README once the spec structure is established"

  create_file "$ROOT/openspec/config.yaml" "# OpenSpec configuration
version: 1
project: $(basename "$ROOT")
specs_dir: changes"

  create_dir "$ROOT/openspec/changes"
}

scaffold_lay_and_land() {
  if [ "$SKILLS_ONLY" = true ]; then return; fi
  syzygy_canon_guard "Pillar 4: about/lay-and-land/" ".syzygy/map" && return
  echo ""
  echo "## Pillar 4: about/lay-and-land/"
  create_dir "$ROOT/about/lay-and-land"
  create_dir "$ROOT/about/lay-and-land/assets"
  create_file "$ROOT/about/lay-and-land/README.md" "# Lay and Land — System Topology

$SCAFFOLD_MARKER

Maps of where components live, how they connect, and what boundaries exist.

| Map | Description |
|-----|-------------|
| \`components.md\` | Component inventory, ownership, boundaries |
| \`data-flow.md\` | How data moves through the system |
| \`deployment.md\` | Where things run |

Diagrams live in \`assets/\`."

  create_file "$ROOT/about/lay-and-land/components.md" "# Component Map

$SCAFFOLD_MARKER

## Components

<!-- List major components/crates/packages/services -->

| Component | Responsibility | Status |
|-----------|---------------|--------|
| | | |

## Dependencies

<!-- Internal dependency graph — which components depend on which -->

\`\`\`mermaid
graph TD
    A[Component A] --> B[Component B]
\`\`\`

## Boundaries

<!-- What are the trust/ownership/deployment boundaries? -->"

  create_file "$ROOT/about/lay-and-land/data-flow.md" "# Data Flow

$SCAFFOLD_MARKER

## Sources

<!-- Where data enters the system -->

## Transformations

<!-- How data changes as it moves -->

## Sinks

<!-- Where data leaves or is persisted -->"

  create_file "$ROOT/about/lay-and-land/deployment.md" "# Deployment

$SCAFFOLD_MARKER

## Environments

<!-- Where this system runs -->

## Runtime Topology

<!-- Services, jobs, or components per environment -->

## Operational Constraints

<!-- Deployment budgets, scaling, or availability constraints -->"
}

scaffold_craft_and_care() {
  if [ "$SKILLS_ONLY" = true ]; then return; fi
  syzygy_canon_guard "Pillar 5: about/craft-and-care/" ".syzygy/governance/policies" && return
  echo ""
  echo "## Pillar 5: about/craft-and-care/"
  create_dir "$ROOT/about/craft-and-care"
  create_file "$ROOT/about/craft-and-care/README.md" "# Craft and Care

$SCAFFOLD_MARKER

Engineering standards for how changes must be carried out well in this project.

| File | Purpose |
|------|---------|
| \`engineering-bar.md\` | Definition of done, maintainability, clarity, cleanup rules |
| \`testing-and-verification.md\` | Evidence standards and verification expectations |

Add narrower standards docs only when the project's risk profile justifies them."

  create_file "$ROOT/about/craft-and-care/engineering-bar.md" "# Engineering Bar

$SCAFFOLD_MARKER

## Definition of Done

- 

## Default Biases

1.
2.
3."

  create_file "$ROOT/about/craft-and-care/testing-and-verification.md" "# Testing and Verification

$SCAFFOLD_MARKER

## Evidence Scales With Risk

| Change type | Minimum evidence |
|-------------|------------------|
| | |

## Required Posture

- "
}

# --- Local skill scaffolds ---
# Pillar navigators ship as subskills of one `doctrine` superskill: the router
# owns the single global catalog entry, subskill bodies load only on demand.
DOCTRINE_SKILL="doctrine"

install_skill() {
  local name="$1" content="$2"
  for tool in "${TOOL_LIST[@]}"; do
    local skill_dir="$ROOT/.${tool}/skills/${DOCTRINE_SKILL}/subskills/${name}"
    create_file "$skill_dir/SKILL.md" "$content"
  done
}

install_doctrine_router() {
  local content="$1"
  for tool in "${TOOL_LIST[@]}"; do
    create_file "$ROOT/.${tool}/skills/${DOCTRINE_SKILL}/SKILL.md" "$content"
  done
}

scaffold_doctrine_router() {
  install_doctrine_router "---
name: doctrine
description: >
  Load this project's own normative knowledge before deciding, implementing, or reviewing:
  doctrine (why the project exists, what it refuses to do), design contracts (how subsystems
  are specified), capability specs (what behavior is required), topology (where components
  live), and engineering standards (the bar for changing them). Routes to one pillar; do not
  guess project conventions from code alone. Triggers: \"what does this project believe\",
  \"is this in scope\", \"check the spec\", \"which RFC covers this\", \"where does this live\",
  \"what's the engineering bar here\", \"how should this be tested/reviewed\".
---

# Project Doctrine Router

$SCAFFOLD_MARKER

Five-pillar knowledge architecture. Each pillar's navigator lives under
\`subskills/\`; load **at most one** for an ordinary task, then read only the
pillar files that navigator points at.

## Discover subskills

\`\`\`bash
PKG=\"\$(dirname \"<absolute-path-to-this-SKILL.md>\")\"
find \"\$PKG/subskills\" -maxdepth 2 -name SKILL.md
grep -n '^name:\|^description:' \"\$PKG\"/subskills/*/SKILL.md
\`\`\`

## Routing table

| The question is... | Pillar | Load |
|---|---|---|
| WHY — purpose, principles, scope, what we refuse to build | Doctrine | [subskills/heart-and-soul/SKILL.md](subskills/heart-and-soul/SKILL.md) |
| HOW — wire-level contracts, data models, state machines, budgets | Design contracts | [subskills/legends-and-lore/SKILL.md](subskills/legends-and-lore/SKILL.md) |
| WHAT — normative requirements and acceptance scenarios | Capability specs | [subskills/spec-and-spine/SKILL.md](subskills/spec-and-spine/SKILL.md) |
| WHERE — components, boundaries, data flow, deployment | Topology | [subskills/lay-and-land/SKILL.md](subskills/lay-and-land/SKILL.md) |
| WHO WE ARE WHEN WE BUILD — quality bar, tests, review, operability | Engineering standards | [subskills/craft-and-care/SKILL.md](subskills/craft-and-care/SKILL.md) |

## Routing rules

- One pillar per question. Crossing pillars (\"is this in scope AND how do I test it\")
  means two sequential loads, not a bulk read.
- Deciding what to build, prioritizing, or auditing the project → \`/th-projects\`.
  Change-level engineering judgment → \`/th-engineering\`. This router is for
  *this project's* recorded knowledge only.
- No pillar fits → answer from the router, or say the project has not recorded it.
  Do not load a subskill to browse."
}

scaffold_skill_heart_and_soul() {
  install_skill "heart-and-soul" "---
name: heart-and-soul
description: >
  Load the project's foundational doctrine before making architectural decisions,
  writing code, designing APIs, creating tests, or proposing features. The about/heart-and-soul/
  directory contains prime directives: what the system is, what it is not, and what v1 ships.
  Selectively load ONLY the documents relevant to your current task. Use proactively at the
  start of substantive work or when unsure about project conventions.
---

# Project Doctrine — Heart and Soul

$SCAFFOLD_MARKER

The \`about/heart-and-soul/\` directory contains the prime directives of this project.
These are not documentation — they are doctrine.

**Consult relevant soul files before:**
- Making any architectural or design decision
- Writing new modules or public APIs
- Proposing features or scope changes

**Do NOT load all files at once.** Select only what your current task requires.

## Document Index

### Always relevant
| File | Read when... | Key content |
|------|-------------|-------------|
| \`about/heart-and-soul/vision.md\` | Starting any session, scope questions | Core thesis, non-goals, non-negotiable rules |
| \`about/heart-and-soul/v1.md\` | Implementing anything, scoping features | What v1 ships vs defers |

### Select by domain
| File | Read when... | Key content |
|------|-------------|-------------|
<!-- Add rows for each domain file -->

## Non-Negotiable Rules

<!-- Copy numbered rules from vision.md -->"
}

scaffold_skill_law_and_lore() {
  install_skill "legends-and-lore" "---
name: legends-and-lore
description: >
  Load design contracts (RFCs) to contextualize implementation work. The about/legends-and-lore/
  directory contains numbered design documents defining wire-level contracts, data models, state
  machines, and quantitative budgets. Consult relevant RFCs before implementing features, writing
  protocol definitions, or resolving cross-subsystem integration questions. Selectively load
  ONLY the RFCs relevant to your current task.
---

# Design Contracts — Legends and Lore

$SCAFFOLD_MARKER

The \`about/legends-and-lore/\` directory contains the authoritative design contracts.

**Consult relevant RFCs before:**
- Implementing any subsystem or feature
- Writing or modifying protocol definitions
- Setting or validating performance budgets
- Resolving how two subsystems interact

**Do NOT load all RFCs at once.** Select by task domain.

## RFC Index

| RFC | File | Read when... | Key content |
|-----|------|-------------|-------------|
| 0001 | \`about/legends-and-lore/rfcs/0001-<name>.md\` | [domain] | [summary] |
<!-- Add rows for each RFC -->

## Key Contracts

<!-- List load-bearing contracts that agents must know about -->
1.
2."
}

scaffold_skill_spec_and_spine() {
  install_skill "spec-and-spine" "---
name: spec-and-spine
description: >
  Ground all implementation work in capability specifications (openspec/). The capability
  specs are the single source of truth for feature planning and development. Use before
  implementing any feature, when detecting spec-code divergence, when evolving specs, or
  when planning new work.
---

# Capability Specs — Spec and Spine

$SCAFFOLD_MARKER

OpenSpec capability specifications are the backbone of this project. Every feature, every task,
every test traces back to a normative requirement in a spec.

## Five-Pillar Model

| Layer | Location | Role |
|-------|----------|------|
| Doctrine | \`about/heart-and-soul/\` | WHY — philosophical foundations |
| Design Contracts | \`about/legends-and-lore/\` | HOW — wire-level contracts |
| Capability Specs | \`openspec/\` | WHAT — normative requirements with testable scenarios |
| Topology | \`about/lay-and-land/\` | WHERE — component boundaries and connections |
| Engineering Standards | \`about/craft-and-care/\` | WHO WE ARE WHEN WE BUILD — implementation quality, verification, review, operability, maintainability |

## Domain Lookup

| Domain | Spec path | Source RFC |
|--------|-----------|------------|
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
| Underlying wire contracts | \`/legends-and-lore\` |
| Philosophical foundations | \`/heart-and-soul\` |
| System topology | \`/lay-and-land\` |"
}

scaffold_skill_lay_and_land() {
  install_skill "lay-and-land" "---
name: lay-and-land
description: >
  Load the project's topology maps to understand where components live, how they connect,
  and what boundaries exist. The about/lay-and-land/ directory contains component inventories,
  data flow diagrams, dependency maps, and deployment topology. Consult before adding new
  components, modifying integration points, changing deployment, or when unsure where something
  lives in the system.
---

# System Topology — Lay and Land

$SCAFFOLD_MARKER

The \`about/lay-and-land/\` directory contains the spatial understanding of this project — where
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
| \`about/lay-and-land/components.md\` | Need to understand what exists | Component inventory, boundaries, ownership |
| \`about/lay-and-land/data-flow.md\` | Need to understand how data moves | Data paths, transformations, trust boundaries |
| \`about/lay-and-land/deployment.md\` | Need to understand where things run | Environments, targets, infrastructure |
<!-- Add rows for additional maps -->

## Key Boundaries

<!-- List the most important architectural boundaries -->
1.
2.

## Quick Reference

| Need | Skill |
|------|-------|
| Why a boundary exists | \`/heart-and-soul\` |
| How a boundary communicates | \`/legends-and-lore\` |
| What a component must do | \`/spec-and-spine\` |
| How changes here should be carried out | \`/craft-and-care\` |"
}

scaffold_skill_craft_and_care() {
  install_skill "craft-and-care" "---
name: craft-and-care
description: >
  MANDATORY for all non-trivial implementation work. Load the project's
  execution-quality standards before implementing changes, reviewing pull
  requests, changing observability, adding dependencies, or preparing
  documentation and operational updates.
---

# Engineering Standards — Craft and Care

$SCAFFOLD_MARKER

The \`about/craft-and-care/\` directory contains this project's execution-quality
standards. Start with \`engineering-bar.md\`, then load only the narrower
standards the current change needs.

## Document Index

| File | Read when... | Key content |
|------|-------------|-------------|
| \`about/craft-and-care/README.md\` | Orienting to the pillar | Scope boundary and reading order |
| \`about/craft-and-care/engineering-bar.md\` | Any non-trivial change | Definition of done, clarity standards, change hygiene |
| \`about/craft-and-care/testing-and-verification.md\` | Planning evidence | Test expectations, regression discipline, verification thresholds |

## Quick Reference

| Need | Skill |
|------|-------|
| Mission or scope boundary | \`/heart-and-soul\` |
| Structural contract text | \`/legends-and-lore\` |
| Path placement and install topology | \`/lay-and-land\` |
| Normative requirement or scenario | \`/spec-and-spine\` |"
}

# --- Main ---
echo "=== Project Shape Init ==="
echo "Root: $ROOT"
echo "Pillars: $PILLARS"
echo "Tools: $TOOLS"
if [ "$SKILLS_ONLY" = true ]; then
  echo "Mode: skills only"
fi

# Scaffold pillars and their skills (router first — it is the agent entry point)
scaffold_doctrine_router
for p in "${PILLAR_LIST[@]}"; do
  case "$p" in
    1) scaffold_heart_and_soul; scaffold_skill_heart_and_soul ;;
    2) scaffold_law_and_lore; scaffold_skill_law_and_lore ;;
    3) scaffold_openspec; scaffold_skill_spec_and_spine ;;
    4) scaffold_lay_and_land; scaffold_skill_lay_and_land ;;
    5) scaffold_craft_and_care; scaffold_skill_craft_and_care ;;
    *) echo "Unknown pillar: $p (use 1-5)"; exit 1 ;;
  esac
done

echo ""
echo "## Done"
echo "  Created: $created"
echo "  Skipped (already exist): $skipped"
if [ "$created" -gt 0 ]; then
  echo ""
  echo "Next steps:"
  echo "  1. Fill in the TODO/placeholder content in the scaffolded files"
  echo "  2. Customize the doctrine router's table and each pillar subskill's index with your actual files and domains"
  echo "  3. Review the generated doctrine superskill with /th-engineering (skill-standards) before relying on it"
  echo "  4. Run shape-scan.sh to verify the result"
fi
