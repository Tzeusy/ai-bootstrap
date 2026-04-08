#!/usr/bin/env bash
# shape-init.sh — Scaffold project shape: pillar directories and local skills
# Usage: shape-init.sh [project-root] [--pillars=1,2,3,4] [--skills-only] [--tools=claude,codex,gemini]
#
# Canonical layout:
#   about/heart-and-soul/  (doctrine)
#   about/law-and-lore/    (design contracts / RFCs)
#   about/lay-and-land/    (topology / maps)
#   openspec/             (capability specs — product, stays at root)
#
# Idempotent: skips anything that already exists.
set -euo pipefail

ROOT="${1:-.}"
mkdir -p "$ROOT"
ROOT="$(cd "$ROOT" && pwd)"
PILLARS="1,2,3,4"
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

# --- Pillar scaffolds ---
scaffold_heart_and_soul() {
  if [ "$SKILLS_ONLY" = true ]; then return; fi
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
  echo ""
  echo "## Pillar 2: about/law-and-lore/"
  create_dir "$ROOT/about/law-and-lore"
  create_dir "$ROOT/about/law-and-lore/rfcs"
  create_dir "$ROOT/about/law-and-lore/reviews"
  create_file "$ROOT/about/law-and-lore/README.md" "# Law and Lore

$SCAFFOLD_MARKER

Numbered design contracts, RFCs, and review notes live here.

1. Start with \`rfcs/0001-TEMPLATE.md\`
2. Replace the template with a real RFC before relying on this pillar
3. Add review notes under \`reviews/\` as decisions evolve"

  create_file "$ROOT/about/law-and-lore/rfcs/0001-TEMPLATE.md" "# RFC 0001: <Title>

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

# --- Local skill scaffolds ---
install_skill() {
  local name="$1" content="$2"
  for tool in "${TOOL_LIST[@]}"; do
    local skill_dir="$ROOT/.${tool}/skills/${name}"
    create_file "$skill_dir/SKILL.md" "$content"
  done
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
  install_skill "law-and-lore" "---
name: law-and-lore
description: >
  Load design contracts (RFCs) to contextualize implementation work. The about/law-and-lore/
  directory contains numbered design documents defining wire-level contracts, data models, state
  machines, and quantitative budgets. Consult relevant RFCs before implementing features, writing
  protocol definitions, or resolving cross-subsystem integration questions. Selectively load
  ONLY the RFCs relevant to your current task.
---

# Design Contracts — Law and Lore

$SCAFFOLD_MARKER

The \`about/law-and-lore/\` directory contains the authoritative design contracts.

**Consult relevant RFCs before:**
- Implementing any subsystem or feature
- Writing or modifying protocol definitions
- Setting or validating performance budgets
- Resolving how two subsystems interact

**Do NOT load all RFCs at once.** Select by task domain.

## RFC Index

| RFC | File | Read when... | Key content |
|-----|------|-------------|-------------|
| 0001 | \`about/law-and-lore/rfcs/0001-<name>.md\` | [domain] | [summary] |
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

## Four-Pillar Model

| Layer | Location | Role |
|-------|----------|------|
| Doctrine | \`about/heart-and-soul/\` | WHY — philosophical foundations |
| Design Contracts | \`about/law-and-lore/\` | HOW — wire-level contracts |
| Capability Specs | \`openspec/\` | WHAT — normative requirements with testable scenarios |
| Topology | \`about/lay-and-land/\` | WHERE — component boundaries and connections |

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
| Underlying wire contracts | \`/law-and-lore\` |
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
| How a boundary communicates | \`/law-and-lore\` |
| What a component must do | \`/spec-and-spine\` |"
}

# --- Main ---
echo "=== Project Shape Init ==="
echo "Root: $ROOT"
echo "Pillars: $PILLARS"
echo "Tools: $TOOLS"
if [ "$SKILLS_ONLY" = true ]; then
  echo "Mode: skills only"
fi

# Scaffold pillars and their skills
for p in "${PILLAR_LIST[@]}"; do
  case "$p" in
    1) scaffold_heart_and_soul; scaffold_skill_heart_and_soul ;;
    2) scaffold_law_and_lore; scaffold_skill_law_and_lore ;;
    3) scaffold_openspec; scaffold_skill_spec_and_spine ;;
    4) scaffold_lay_and_land; scaffold_skill_lay_and_land ;;
    *) echo "Unknown pillar: $p (use 1-4)"; exit 1 ;;
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
  echo "  2. Customize local skill index tables with your actual files and domains"
  echo "  3. Run shape-scan.sh to verify the result"
fi
