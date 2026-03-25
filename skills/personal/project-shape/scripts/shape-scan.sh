#!/usr/bin/env bash
# shape-scan.sh — Discover and assess project shape artifacts
# Usage: shape-scan.sh [project-root]
#
# Canonical layout:
#   about/heart-and-soul/  (doctrine)
#   about/law-and-lore/    (design contracts / RFCs)
#   about/lay-and-land/    (topology / maps)
#   openspec/             (capability specs — product, stays at root)
#
# Also detects legacy layouts (heart-and-soul/ at root, docs/rfcs/, maps/, etc.)
set -euo pipefail

ROOT="${1:-.}"
ROOT="$(cd "$ROOT" && pwd)"

echo "=== Project Shape Scan ==="
echo "Root: $ROOT"
echo ""

# --- Helpers ---
check_dir() {
  local label="$1" dir="$2"
  if [ -d "$dir" ]; then
    local count
    count=$(find "$dir" -name '*.md' -type f 2>/dev/null | wc -l)
    echo "  [FOUND] $label ($count markdown files)"
    return 0
  else
    echo "  [ABSENT] $label"
    return 1
  fi
}

check_file() {
  local label="$1" file="$2"
  if [ -f "$file" ]; then
    local lines
    lines=$(wc -l < "$file")
    echo "    - $label ($lines lines)"
    return 0
  else
    return 1
  fi
}

check_skill() {
  local name="$1"
  local found=0
  for tool_dir in .claude .codex .gemini .opencode; do
    local skill_path="$ROOT/$tool_dir/skills/$name/SKILL.md"
    if [ -f "$skill_path" ]; then
      # Validate YAML frontmatter: file must start with --- and have a closing ---
      local first_line
      first_line=$(head -1 "$skill_path")
      if [ "$first_line" = "---" ]; then
        # Check for closing delimiter (second --- within first 20 lines)
        local has_closing
        has_closing=$(tail -n +2 "$skill_path" | head -20 | grep -c '^---$' || true)
        if [ "$has_closing" -ge 1 ]; then
          # Check for required fields
          local has_name has_desc
          has_name=$(sed -n '2,20p' "$skill_path" | grep -c '^name:' || true)
          has_desc=$(sed -n '2,20p' "$skill_path" | grep -c '^description:' || true)
          if [ "$has_name" -ge 1 ] && [ "$has_desc" -ge 1 ]; then
            echo "    - $tool_dir/skills/$name/ [VALID]"
          else
            echo "    - $tool_dir/skills/$name/ [INVALID] missing required name/description fields"
          fi
        else
          echo "    - $tool_dir/skills/$name/ [INVALID] missing closing --- delimiter"
        fi
      else
        echo "    - $tool_dir/skills/$name/ [INVALID] missing YAML frontmatter (file must start with ---)"
      fi
      found=1
    fi
  done
  if [ "$found" -eq 0 ]; then
    echo "    - No local skill installed for '$name'"
  fi
}

# Resolve pillar directory: check canonical path first, then legacy fallback
resolve_pillar() {
  local canonical="$1" legacy="$2"
  if [ -d "$canonical" ]; then
    echo "$canonical"
  elif [ -d "$legacy" ]; then
    echo "$legacy"
  else
    echo ""
  fi
}

# --- Pillar 1: Doctrine ---
echo "## Pillar 1: Doctrine (WHY)"
HAS_DIR=$(resolve_pillar "$ROOT/about/heart-and-soul" "$ROOT/heart-and-soul")
if [ -n "$HAS_DIR" ]; then
  label="${HAS_DIR#$ROOT/}"
  check_dir "$label/" "$HAS_DIR"
  [ "$HAS_DIR" = "$ROOT/heart-and-soul" ] && echo "    [LEGACY] Consider moving to about/heart-and-soul/"
  check_file "vision.md" "$HAS_DIR/vision.md" || echo "    - [MISSING] vision.md (critical)"
  check_file "v1.md" "$HAS_DIR/v1.md" || true
  check_file "architecture.md" "$HAS_DIR/architecture.md" || true
  check_file "security.md" "$HAS_DIR/security.md" || true
  check_file "failure.md" "$HAS_DIR/failure.md" || true
  check_file "development.md" "$HAS_DIR/development.md" || true
  check_file "validation.md" "$HAS_DIR/validation.md" || true
  check_file "README.md" "$HAS_DIR/README.md" || true
  echo "  Local skill:"
  check_skill "heart-and-soul"
else
  echo "  [ABSENT] about/heart-and-soul/"
  for f in PHILOSOPHY.md MANIFESTO.md VALUES.md VISION.md; do
    [ -f "$ROOT/$f" ] && echo "  [HINT] Found $f in root — consider moving to about/heart-and-soul/"
  done
fi
echo ""

# --- Pillar 2: Design Contracts ---
echo "## Pillar 2: Design Contracts (HOW)"
LAL_DIR=$(resolve_pillar "$ROOT/about/law-and-lore" "$ROOT/docs")
if [ -n "$LAL_DIR" ]; then
  label="${LAL_DIR#$ROOT/}"
  check_dir "$label/" "$LAL_DIR"
  # Find rfcs — could be at about/law-and-lore/rfcs/ or legacy docs/rfcs/
  RFC_DIR=""
  [ -d "$LAL_DIR/rfcs" ] && RFC_DIR="$LAL_DIR/rfcs"
  if [ -n "$RFC_DIR" ]; then
    rfc_count=$(find "$RFC_DIR" -maxdepth 1 -name '*.md' -type f 2>/dev/null | wc -l)
    echo "    - RFCs: $rfc_count documents in ${RFC_DIR#$ROOT/}/"
  else
    echo "    - [MISSING] rfcs/ (no numbered design docs)"
  fi
  REVIEW_DIR=""
  [ -d "$LAL_DIR/reviews" ] && REVIEW_DIR="$LAL_DIR/reviews"
  if [ -n "$REVIEW_DIR" ]; then
    review_count=$(find "$REVIEW_DIR" -name '*.md' -type f 2>/dev/null | wc -l)
    echo "    - Reviews: $review_count review documents"
  fi
  [ -d "$LAL_DIR/prompts" ] && echo "    - Epic prompts: present"
  [ -d "$LAL_DIR/notes" ] && echo "    - Notes: present"
  [ "$LAL_DIR" = "$ROOT/docs" ] && echo "    [LEGACY] Consider restructuring as about/law-and-lore/"
  echo "  Local skill:"
  check_skill "law-and-lore"
else
  echo "  [ABSENT] about/law-and-lore/"
  for d in design rfcs adrs decisions; do
    [ -d "$ROOT/$d" ] && echo "  [HINT] Found $d/ in root — consider consolidating under about/law-and-lore/"
  done
fi
echo ""

# --- Pillar 3: Capability Specs (openspec/ — always at root) ---
echo "## Pillar 3: Capability Specs (WHAT)"
if check_dir "openspec/" "$ROOT/openspec"; then
  if [ -d "$ROOT/openspec/changes" ]; then
    change_count=$(find "$ROOT/openspec/changes" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l)
    echo "    - Changes: $change_count spec changes"
    for change_dir in "$ROOT/openspec/changes"/*/; do
      [ -d "$change_dir" ] || continue
      change_name=$(basename "$change_dir")
      if [ -d "$change_dir/specs" ]; then
        spec_count=$(find "$change_dir/specs" -name 'spec.md' -type f 2>/dev/null | wc -l)
        echo "    - $change_name: $spec_count capability specs"
      fi
    done
  fi
  echo "  Local skill:"
  check_skill "spec-and-spine"
else
  for d in specs requirements features; do
    [ -d "$ROOT/$d" ] && echo "  [HINT] Found $d/ in root — consider adopting openspec/"
  done
fi
echo ""

# --- Pillar 4: Topology ---
echo "## Pillar 4: Topology (WHERE)"
LAY_DIR=$(resolve_pillar "$ROOT/about/lay-and-land" "$ROOT/maps")
if [ -n "$LAY_DIR" ]; then
  label="${LAY_DIR#$ROOT/}"
  check_dir "$label/" "$LAY_DIR"
  [ "$LAY_DIR" = "$ROOT/maps" ] && echo "    [LEGACY] Consider moving to about/lay-and-land/"
  check_file "components.md" "$LAY_DIR/components.md" || true
  check_file "data-flow.md" "$LAY_DIR/data-flow.md" || true
  check_file "deployment.md" "$LAY_DIR/deployment.md" || true
  check_file "dependencies.md" "$LAY_DIR/dependencies.md" || true
  check_file "integration.md" "$LAY_DIR/integration.md" || true
  check_file "README.md" "$LAY_DIR/README.md" || true
  if [ -d "$LAY_DIR/assets" ]; then
    diagram_count=$(find "$LAY_DIR/assets" -type f 2>/dev/null | wc -l)
    echo "    - Diagrams: $diagram_count files in ${LAY_DIR#$ROOT/}/assets/"
  fi
  echo "  Local skill:"
  check_skill "lay-and-land"
else
  echo "  [ABSENT] about/lay-and-land/"
  for d in architecture diagrams topology; do
    [ -d "$ROOT/$d" ] && echo "  [HINT] Found $d/ in root — consider consolidating under about/lay-and-land/"
  done
  [ -f "$ROOT/ARCHITECTURE.md" ] && echo "  [HINT] Found ARCHITECTURE.md in root — consider splitting into about/lay-and-land/"
fi
echo ""

# --- Summary ---
echo "## Shape Summary"
pillars=0
[ -n "$(resolve_pillar "$ROOT/about/heart-and-soul" "$ROOT/heart-and-soul")" ] && pillars=$((pillars + 1))
[ -n "$(resolve_pillar "$ROOT/about/law-and-lore" "$ROOT/docs")" ] && pillars=$((pillars + 1))
[ -d "$ROOT/openspec" ] && pillars=$((pillars + 1))
[ -n "$(resolve_pillar "$ROOT/about/lay-and-land" "$ROOT/maps")" ] && pillars=$((pillars + 1))

skills=0
for name in heart-and-soul law-and-lore spec-and-spine lay-and-land; do
  for tool_dir in .claude .codex .gemini .opencode; do
    [ -f "$ROOT/$tool_dir/skills/$name/SKILL.md" ] && { skills=$((skills + 1)); break; }
  done
done

echo "  Pillars present: $pillars/4"
echo "  Local skills installed: $skills/4"

if [ "$pillars" -eq 0 ]; then
  echo "  Assessment: UNSHAPED — No knowledge architecture detected"
elif [ "$pillars" -eq 1 ]; then
  echo "  Assessment: NASCENT — Beginning to take shape"
elif [ "$pillars" -le 3 ]; then
  echo "  Assessment: STRUCTURED — $(( 4 - pillars )) pillar(s) missing"
elif [ "$pillars" -eq 4 ] && [ "$skills" -lt 4 ]; then
  echo "  Assessment: SHAPED — All pillars present, install remaining local skills"
elif [ "$pillars" -eq 4 ] && [ "$skills" -eq 4 ]; then
  echo "  Assessment: MATURE — Full shape with agent navigation"
fi
