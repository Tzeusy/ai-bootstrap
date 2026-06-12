#!/usr/bin/env bash
# self-test.sh — Regression checks for project-shape scaffolding and scanning.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCAN_SCRIPT="$SCRIPT_DIR/shape-scan.sh"
INIT_SCRIPT="$SCRIPT_DIR/shape-init.sh"
FIXTURES_DIR="$(cd "$SCRIPT_DIR/.." && pwd)/tests/fixtures"

TMP_ROOT="$(mktemp -d)"
trap 'rm -rf "$TMP_ROOT"' EXIT

pass_count=0

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

assert_contains() {
  local haystack="$1" needle="$2" label="$3"
  if ! grep -Fq "$needle" <<< "$haystack"; then
    fail "$label (missing: $needle)"
  fi
}

assert_not_contains() {
  local haystack="$1" needle="$2" label="$3"
  if grep -Fq "$needle" <<< "$haystack"; then
    fail "$label (unexpected: $needle)"
  fi
}

run_case() {
  local name="$1"
  shift
  echo "== $name =="
  "$@"
  pass_count=$((pass_count + 1))
}

case_fresh_scaffold_not_mature() {
  local repo="$TMP_ROOT/fresh"
  local out
  bash "$INIT_SCRIPT" "$repo" --tools=claude >/dev/null
  out="$(bash "$SCAN_SCRIPT" "$repo")"
  assert_contains "$out" "Assessment: SHAPED — Full structure present, but authored content is still incomplete" "fresh scaffold should not be mature"
  assert_contains "$out" "Pillars needing authoring: 5/5" "fresh scaffold should report scaffolded pillars"
  assert_not_contains "$out" "Assessment: MATURE" "fresh scaffold must never report mature"
}

case_invalid_frontmatter_rejected() {
  local repo="$TMP_ROOT/invalid-frontmatter"
  local out
  mkdir -p "$repo/about/heart-and-soul" "$repo/.claude/skills/heart-and-soul"
  cat > "$repo/about/heart-and-soul/vision.md" <<'EOF'
# Vision

This project exists to make shape audits trustworthy.
EOF
  cat > "$repo/.claude/skills/heart-and-soul/SKILL.md" <<'EOF'
---
name: heart-and-soul
description: Use when grounding implementation work in the project's doctrine.
metadata: not-supported
---

# Heart and Soul

Read the doctrine before making foundational decisions.
EOF
  out="$(bash "$SCAN_SCRIPT" "$repo")"
  assert_contains "$out" "[INVALID] unsupported frontmatter key(s): metadata" "unsupported frontmatter key should be rejected"
}

case_authored_repo_can_be_mature() {
  local repo="$FIXTURES_DIR/mature-layout"
  local out

  out="$(bash "$SCAN_SCRIPT" "$repo")"
  assert_contains "$out" "Assessment: MATURE — Full shape with agent navigation" "authored repo should be mature"
  assert_contains "$out" "Pillars needing authoring: 0/5" "authored repo should not report scaffolded pillars"
}

case_four_pillars_without_craft_not_mature() {
  local repo="$TMP_ROOT/no-craft"
  local out
  mkdir -p \
    "$repo/about/heart-and-soul" \
    "$repo/about/legends-and-lore/rfcs" \
    "$repo/about/lay-and-land" \
    "$repo/openspec/changes/core/specs/core" \
    "$repo/.claude/skills/heart-and-soul" \
    "$repo/.claude/skills/legends-and-lore" \
    "$repo/.claude/skills/spec-and-spine" \
    "$repo/.claude/skills/lay-and-land"

  cat > "$repo/about/heart-and-soul/vision.md" <<'EOF'
# Vision

Real doctrine for a project with no engineering-standards pillar.

## Non-Negotiable Rules
1. Rule one.
EOF
  cat > "$repo/about/heart-and-soul/v1.md" <<'EOF'
# V1 Scope

## V1 Ships

- one thing
EOF
  cat > "$repo/about/legends-and-lore/rfcs/0001-x.md" <<'EOF'
# RFC 0001

Implements doctrine from vision.md.
EOF
  cat > "$repo/about/lay-and-land/components.md" <<'EOF'
# Components

Topology reflects RFC and spec boundaries.
EOF
  cat > "$repo/openspec/changes/core/specs/core/spec.md" <<'EOF'
# Spec

Source: RFC 0001

### Scenario: one
- **WHEN** x
- **THEN** y
EOF

  for s in heart-and-soul legends-and-lore spec-and-spine lay-and-land; do
    cat > "$repo/.claude/skills/$s/SKILL.md" <<EOF
---
name: $s
description: Use when reading $s.
---

# $s
EOF
  done

  out="$(bash "$SCAN_SCRIPT" "$repo")"
  assert_contains "$out" "[ABSENT] about/craft-and-care/" "missing craft-and-care should be reported absent"
  assert_contains "$out" "Pillars present: 4/5" "four authored pillars should count 4/5"
  assert_contains "$out" "Assessment: STRUCTURED" "four pillars without craft-and-care should be structured"
  assert_not_contains "$out" "Assessment: MATURE" "four pillars without craft-and-care must never be mature"
}

case_legacy_layout_detected() {
  local repo="$FIXTURES_DIR/legacy-layout"
  local out
  out="$(bash "$SCAN_SCRIPT" "$repo")"
  assert_contains "$out" "Contracts: 1 documents in docs/rfcs/ (1 authored)" "legacy RFC location should be detected"
  assert_contains "$out" "[FOUND] ARCHITECTURE.md (legacy single-file topology)" "legacy topology file should be detected"
  assert_contains "$out" "Assessment: MATURE — Full shape with agent navigation" "legacy fixture should still qualify as mature"
}

case_html_comments_do_not_trigger_scaffold() {
  local repo="$TMP_ROOT/html-comments"
  local out
  mkdir -p \
    "$repo/about/heart-and-soul" \
    "$repo/about/legends-and-lore/rfcs" \
    "$repo/about/lay-and-land" \
    "$repo/openspec/changes/core/specs/core" \
    "$repo/.claude/skills/heart-and-soul" \
    "$repo/.claude/skills/legends-and-lore" \
    "$repo/.claude/skills/spec-and-spine" \
    "$repo/.claude/skills/lay-and-land"

  cat > "$repo/about/heart-and-soul/vision.md" <<'EOF'
# Vision

Real doctrine.

<!-- editorial note retained intentionally -->

## Non-Negotiable Rules
1. Rule one.
EOF
  cat > "$repo/about/heart-and-soul/v1.md" <<'EOF'
# V1 Scope

## V1 Ships

- one thing
EOF
  cat > "$repo/about/legends-and-lore/rfcs/0001-x.md" <<'EOF'
# RFC 0001

Implements doctrine from vision.md.
EOF
  cat > "$repo/about/lay-and-land/components.md" <<'EOF'
# Components

Topology reflects RFC and spec boundaries.
EOF
  cat > "$repo/openspec/changes/core/specs/core/spec.md" <<'EOF'
# Spec

Source: RFC 0001

### Scenario: one
- **WHEN** x
- **THEN** y
EOF

  for s in heart-and-soul legends-and-lore spec-and-spine lay-and-land; do
    cat > "$repo/.claude/skills/$s/SKILL.md" <<EOF
---
name: $s
description: Use when reading $s.
---

# $s
EOF
  done

  out="$(bash "$SCAN_SCRIPT" "$repo")"
  assert_contains "$out" "Content: AUTHORED" "html comments should not force scaffold classification"
  assert_not_contains "$out" "Content: MIXED" "html comments alone should not create mixed state"
}

case_architecture_file_does_not_double_count_topology() {
  # A repo with BOTH a topology dir (about/lay-and-land) and a root
  # ARCHITECTURE.md must count topology once, not twice. Regression for the
  # pillar double-count where the ARCHITECTURE.md fallback fired alongside the
  # already-counted topology dir.
  local repo="$TMP_ROOT/arch-plus-topology"
  local out
  mkdir -p \
    "$repo/about/heart-and-soul" \
    "$repo/about/legends-and-lore/rfcs" \
    "$repo/about/lay-and-land" \
    "$repo/openspec/changes/core/specs/core"

  cat > "$repo/about/heart-and-soul/vision.md" <<'EOF'
# Vision

Doctrine for a repo that still carries a legacy root ARCHITECTURE.md.

## Non-Negotiable Rules
1. Rule one.
EOF
  cat > "$repo/about/legends-and-lore/rfcs/0001-x.md" <<'EOF'
# RFC 0001

Implements doctrine from vision.md.
EOF
  cat > "$repo/about/lay-and-land/components.md" <<'EOF'
# Components

Topology reflects RFC and spec boundaries.
EOF
  cat > "$repo/openspec/changes/core/specs/core/spec.md" <<'EOF'
# Spec

Source: RFC 0001

### Scenario: one
- **WHEN** x
- **THEN** y
EOF
  cat > "$repo/ARCHITECTURE.md" <<'EOF'
# Architecture

Legacy single-file topology, kept alongside about/lay-and-land/ during migration.
EOF

  out="$(bash "$SCAN_SCRIPT" "$repo")"
  assert_contains "$out" "Pillars present: 4/5" "topology dir + ARCHITECTURE.md must count topology once (4/5, not 5/5)"
  assert_not_contains "$out" "Pillars present: 5/5" "ARCHITECTURE.md must not double-count the already-counted topology dir"
}

case_reviews_only_do_not_create_design_pillar() {
  local repo="$TMP_ROOT/reviews-only"
  local out
  mkdir -p "$repo/docs/reviews"
  cat > "$repo/docs/reviews/r1.md" <<'EOF'
# Review

Review notes only.
EOF
  out="$(bash "$SCAN_SCRIPT" "$repo")"
  assert_contains "$out" "[ABSENT] about/legends-and-lore/" "review-only docs should not count as design pillar"
  assert_contains "$out" "docs/reviews/ without RFCs/ADRs" "review-only docs should emit a hint"
  assert_contains "$out" "Assessment: UNSHAPED" "review-only docs should not inflate maturity"
}

run_case "fresh scaffold is not mature" case_fresh_scaffold_not_mature
run_case "unsupported frontmatter keys are rejected" case_invalid_frontmatter_rejected
run_case "fully authored repo is mature" case_authored_repo_can_be_mature
run_case "four pillars without craft-and-care is not mature" case_four_pillars_without_craft_not_mature
run_case "legacy layout is detected conservatively" case_legacy_layout_detected
run_case "html comments do not trigger scaffold classification" case_html_comments_do_not_trigger_scaffold
run_case "ARCHITECTURE.md does not double-count topology" case_architecture_file_does_not_double_count_topology
run_case "review-only docs do not create design pillar" case_reviews_only_do_not_create_design_pillar

echo "PASS: $pass_count project-shape self-test cases"
