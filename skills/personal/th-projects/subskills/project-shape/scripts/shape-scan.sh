#!/usr/bin/env bash
# shape-scan.sh — Discover and assess project shape artifacts
# Usage: shape-scan.sh [project-root]
#
# Canonical layout:
#   about/heart-and-soul/  (doctrine)
#   about/legends-and-lore/    (design contracts / RFCs)
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

is_placeholder_file() {
  local file="$1"
  [ -f "$file" ] || return 1
  if grep -Eq 'SHAPE-SCAFFOLD|<name>|<Title>|\[domain\]|\[summary\]|\[Contract from RFCs\]|\[Boundary from topology\]|\[Rule from doctrine\]|One paragraph thesis statement|Add rows for|Replace this scaffold|placeholder/template content' "$file"; then
    return 0
  fi
  if grep -Eq '^[[:space:]]*[0-9]+\.$|^[[:space:]]*-$|^\|[[:space:]]*\|([[:space:]]*\|)+$' "$file"; then
    return 0
  fi
  return 1
}

count_authored_markdown_files() {
  local dir="$1"
  local authored=0
  [ -d "$dir" ] || {
    echo 0
    return
  }
  while IFS= read -r file; do
    if ! is_placeholder_file "$file"; then
      authored=$((authored + 1))
    fi
  done < <(find "$dir" -name '*.md' -type f 2>/dev/null | sort)
  echo "$authored"
}

count_numbered_list_items() {
  local file="$1"
  [ -f "$file" ] || {
    echo 0
    return
  }
  grep -Ec '^[[:space:]]*[0-9]+\.[[:space:]]+\S' "$file" || true
}

count_markdown_files() {
  local dir="$1" pattern="${2:-*.md}"
  [ -d "$dir" ] || {
    echo 0
    return
  }
  find "$dir" -type f -name "$pattern" 2>/dev/null | wc -l
}

count_files_matching() {
  local dir="$1" pattern="$2" grep_pattern="$3"
  local matches=0
  [ -d "$dir" ] || {
    echo 0
    return
  }
  while IFS= read -r file; do
    grep -Eiq "$grep_pattern" "$file" && matches=$((matches + 1))
  done < <(find "$dir" -type f -name "$pattern" 2>/dev/null | sort)
  echo "$matches"
}

count_paths_matching() {
  local grep_pattern="$1"
  shift
  local matches=0
  local path
  for path in "$@"; do
    [ -f "$path" ] || continue
    grep -Eiq "$grep_pattern" "$path" && matches=$((matches + 1))
  done
  echo "$matches"
}

classify_content_state() {
  local authored="$1" total="$2"
  if [ "$total" -eq 0 ]; then
    echo "empty"
  elif [ "$authored" -eq 0 ]; then
    echo "scaffolded"
  elif [ "$authored" -lt "$total" ]; then
    echo "mixed"
  else
    echo "authored"
  fi
}

emit_content_state() {
  local label="$1" state="$2"
  case "$state" in
    empty) echo "  Content: EMPTY — structure exists but no markdown content yet" ;;
    scaffolded) echo "  Content: SCAFFOLDED — placeholder/template content still present" ;;
    mixed) echo "  Content: MIXED — some authored content, some scaffold/template content remains" ;;
    authored) echo "  Content: AUTHORED — no scaffold markers detected in markdown files" ;;
    *) echo "  Content: UNKNOWN" ;;
  esac
}

extract_frontmatter() {
  local file="$1"
  awk '
    NR == 1 && $0 == "---" { in_fm = 1; next }
    in_fm && $0 == "---" { exit }
    in_fm { print }
  ' "$file"
}

extract_description_text() {
  local file="$1"
  awk '
    BEGIN { in_fm = 0; in_desc = 0 }
    NR == 1 && $0 == "---" { in_fm = 1; next }
    in_fm && $0 == "---" { exit }
    in_desc {
      if ($0 ~ /^  / || $0 == "") {
        sub(/^  /, "", $0)
        print
        next
      }
      in_desc = 0
    }
    in_fm && $0 ~ /^description:[[:space:]]*/ {
      line = $0
      sub(/^description:[[:space:]]*/, "", line)
      if (line == ">" || line == "|") {
        in_desc = 1
        next
      }
      print line
    }
  ' "$file" | tr '\n' ' ' | sed 's/[[:space:]]\+/ /g; s/^ //; s/ $//'
}

check_skill() {
  local name="$1"
  local found=0
  for tool_dir in .claude .codex .gemini .opencode; do
    local skill_path="$ROOT/$tool_dir/skills/$name/SKILL.md"
    if [ -f "$skill_path" ]; then
      local first_line close_count frontmatter unexpected_keys name_value description_text
      first_line=$(head -1 "$skill_path")
      if [ "$first_line" != "---" ]; then
        echo "    - $tool_dir/skills/$name/ [INVALID] missing YAML frontmatter (file must start with ---)"
        found=1
        continue
      fi

      close_count=$(tail -n +2 "$skill_path" | grep -c '^---$' || true)
      if [ "$close_count" -lt 1 ]; then
        echo "    - $tool_dir/skills/$name/ [INVALID] missing closing --- delimiter"
        found=1
        continue
      fi

      frontmatter=$(extract_frontmatter "$skill_path")
      unexpected_keys=$(printf '%s\n' "$frontmatter" | sed -n 's/^\([A-Za-z0-9_-]\+\):.*/\1/p' | grep -Ev '^(name|description)$' || true)
      if [ -n "$unexpected_keys" ]; then
        echo "    - $tool_dir/skills/$name/ [INVALID] unsupported frontmatter key(s): $(printf '%s' "$unexpected_keys" | paste -sd ', ' -)"
        found=1
        continue
      fi

      name_value=$(printf '%s\n' "$frontmatter" | sed -n 's/^name:[[:space:]]*//p' | head -1)
      description_text=$(extract_description_text "$skill_path")
      if [ -z "$name_value" ] || [ -z "$description_text" ]; then
        echo "    - $tool_dir/skills/$name/ [INVALID] missing required name/description fields"
        found=1
        continue
      fi
      if ! [[ "$name_value" =~ ^[a-z0-9-]+$ ]]; then
        echo "    - $tool_dir/skills/$name/ [INVALID] name must use lowercase letters, numbers, and hyphens only"
        found=1
        continue
      fi
      if [ "${#name_value}" -gt 64 ]; then
        echo "    - $tool_dir/skills/$name/ [INVALID] name exceeds 64 characters"
        found=1
        continue
      fi
      if [[ "$name_value" =~ (anthropic|claude) ]]; then
        echo "    - $tool_dir/skills/$name/ [INVALID] name uses reserved words"
        found=1
        continue
      fi
      if [ "${#description_text}" -gt 1024 ]; then
        echo "    - $tool_dir/skills/$name/ [INVALID] description exceeds 1024 characters"
        found=1
        continue
      fi
      if printf '%s\n%s\n' "$name_value" "$description_text" | grep -Eq '<[^>]+>'; then
        echo "    - $tool_dir/skills/$name/ [INVALID] XML-like tags are not allowed in metadata"
        found=1
        continue
      fi
      if is_placeholder_file "$skill_path"; then
        echo "    - $tool_dir/skills/$name/ [VALID, TEMPLATE] customize before relying on agent navigation"
      else
        echo "    - $tool_dir/skills/$name/ [VALID]"
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

resolve_design_contract_dir() {
  if [ -d "$ROOT/about/legends-and-lore" ]; then
    echo "$ROOT/about/legends-and-lore"
  elif [ -d "$ROOT/docs/rfcs" ] || [ -d "$ROOT/docs/adrs" ]; then
    echo "$ROOT/docs"
  elif [ -d "$ROOT/rfcs" ]; then
    echo "$ROOT/rfcs"
  elif [ -d "$ROOT/adrs" ]; then
    echo "$ROOT/adrs"
  elif [ -d "$ROOT/design" ]; then
    echo "$ROOT/design"
  elif [ -d "$ROOT/decisions" ]; then
    echo "$ROOT/decisions"
  else
    echo ""
  fi
}

resolve_topology_dir() {
  if [ -d "$ROOT/about/lay-and-land" ]; then
    echo "$ROOT/about/lay-and-land"
  elif [ -d "$ROOT/maps" ]; then
    echo "$ROOT/maps"
  elif [ -d "$ROOT/architecture" ]; then
    echo "$ROOT/architecture"
  elif [ -d "$ROOT/diagrams" ]; then
    echo "$ROOT/diagrams"
  elif [ -d "$ROOT/topology" ]; then
    echo "$ROOT/topology"
  else
    echo ""
  fi
}

emit_traceability_summary() {
  local doctrine_rules="$1" rfc_docs="$2" rfc_doctrine_refs="$3" spec_docs="$4" spec_source_refs="$5" spec_scenarios="$6" topology_docs="$7" topology_cross_refs="$8"
  echo "## Traceability"
  echo "  Doctrine rules detected: $doctrine_rules"
  echo "  Design contracts referencing doctrine: $rfc_doctrine_refs/$rfc_docs"
  echo "  Specs with source references: $spec_source_refs/$spec_docs"
  echo "  Specs with scenarios: $spec_scenarios/$spec_docs"
  echo "  Topology docs cross-linking other pillars: $topology_cross_refs/$topology_docs"
}

# --- Pillar 1: Doctrine ---
echo "## Pillar 1: Doctrine (WHY)"
HAS_DIR=$(resolve_pillar "$ROOT/about/heart-and-soul" "$ROOT/heart-and-soul")
if [ -n "$HAS_DIR" ]; then
  label="${HAS_DIR#$ROOT/}"
  total_md=$(find "$HAS_DIR" -name '*.md' -type f 2>/dev/null | wc -l)
  authored_md=$(count_authored_markdown_files "$HAS_DIR")
  doctrine_state=$(classify_content_state "$authored_md" "$total_md")
  check_dir "$label/" "$HAS_DIR"
  emit_content_state "Doctrine" "$doctrine_state"
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
LAL_DIR=$(resolve_design_contract_dir)
if [ -n "$LAL_DIR" ]; then
  label="${LAL_DIR#$ROOT/}"
  total_md=$(find "$LAL_DIR" -name '*.md' -type f 2>/dev/null | wc -l)
  authored_md=$(count_authored_markdown_files "$LAL_DIR")
  law_state=$(classify_content_state "$authored_md" "$total_md")
  check_dir "$label/" "$LAL_DIR"
  emit_content_state "Design Contracts" "$law_state"
  # Find rfcs — could be at about/legends-and-lore/rfcs/ or legacy docs/rfcs/
  RFC_DIR=""
  [ -d "$LAL_DIR/rfcs" ] && RFC_DIR="$LAL_DIR/rfcs"
  [ -z "$RFC_DIR" ] && [ -d "$LAL_DIR/adrs" ] && RFC_DIR="$LAL_DIR/adrs"
  if [ -n "$RFC_DIR" ]; then
    rfc_count=$(find "$RFC_DIR" -maxdepth 1 -name '*.md' -type f 2>/dev/null | wc -l)
    authored_rfc_count=$(count_authored_markdown_files "$RFC_DIR")
    echo "    - Contracts: $rfc_count documents in ${RFC_DIR#$ROOT/}/ ($authored_rfc_count authored)"
  else
    echo "    - [MISSING] rfcs/ or adrs/ (no numbered design docs)"
  fi
  REVIEW_DIR=""
  [ -d "$LAL_DIR/reviews" ] && REVIEW_DIR="$LAL_DIR/reviews"
  if [ -n "$REVIEW_DIR" ]; then
    review_count=$(find "$REVIEW_DIR" -name '*.md' -type f 2>/dev/null | wc -l)
    echo "    - Reviews: $review_count review documents"
  fi
  [ -d "$LAL_DIR/prompts" ] && echo "    - Epic prompts: present"
  [ -d "$LAL_DIR/notes" ] && echo "    - Notes: present"
  [ "$LAL_DIR" = "$ROOT/docs" ] && echo "    [LEGACY] Consider restructuring as about/legends-and-lore/"
  echo "  Local skill:"
  check_skill "legends-and-lore"
else
  echo "  [ABSENT] about/legends-and-lore/"
  if [ -d "$ROOT/docs/reviews" ]; then
    echo "  [HINT] Found docs/reviews/ without RFCs/ADRs — review notes alone do not establish the design-contract pillar"
  fi
  for d in design rfcs adrs decisions; do
    [ -d "$ROOT/$d" ] && echo "  [HINT] Found $d/ in root — consider consolidating under about/legends-and-lore/"
  done
fi
echo ""

# --- Pillar 3: Capability Specs (openspec/ — always at root) ---
echo "## Pillar 3: Capability Specs (WHAT)"
if check_dir "openspec/" "$ROOT/openspec"; then
  total_md=$(find "$ROOT/openspec" -name '*.md' -type f 2>/dev/null | wc -l)
  authored_md=$(count_authored_markdown_files "$ROOT/openspec")
  spec_state=$(classify_content_state "$authored_md" "$total_md")
  substantive_specs=0
  if [ -d "$ROOT/openspec/changes" ]; then
    change_count=$(find "$ROOT/openspec/changes" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l)
    echo "    - Changes: $change_count spec changes"
    for change_dir in "$ROOT/openspec/changes"/*/; do
      [ -d "$change_dir" ] || continue
      change_name=$(basename "$change_dir")
      if [ -d "$change_dir/specs" ]; then
        spec_count=$(find "$change_dir/specs" -name 'spec.md' -type f 2>/dev/null | wc -l)
        authored_spec_count=$(count_authored_markdown_files "$change_dir/specs")
        substantive_specs=$((substantive_specs + authored_spec_count))
        echo "    - $change_name: $spec_count capability specs ($authored_spec_count authored)"
      fi
    done
  fi
  if [ "$substantive_specs" -eq 0 ]; then
    spec_state="scaffolded"
  fi
  emit_content_state "Capability Specs" "$spec_state"
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
LAY_DIR=$(resolve_topology_dir)
if [ -n "$LAY_DIR" ]; then
  label="${LAY_DIR#$ROOT/}"
  total_md=$(find "$LAY_DIR" -name '*.md' -type f 2>/dev/null | wc -l)
  authored_md=$(count_authored_markdown_files "$LAY_DIR")
  topology_state=$(classify_content_state "$authored_md" "$total_md")
  check_dir "$label/" "$LAY_DIR"
  emit_content_state "Topology" "$topology_state"
  [ "$LAY_DIR" = "$ROOT/maps" ] && echo "    [LEGACY] Consider moving to about/lay-and-land/"
  [ "$LAY_DIR" = "$ROOT/architecture" ] && echo "    [LEGACY] Consider consolidating architecture/ into about/lay-and-land/"
  [ "$LAY_DIR" = "$ROOT/diagrams" ] && echo "    [LEGACY] Consider consolidating diagrams/ into about/lay-and-land/"
  [ "$LAY_DIR" = "$ROOT/topology" ] && echo "    [LEGACY] Consider consolidating topology/ into about/lay-and-land/"
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
  if [ -f "$ROOT/ARCHITECTURE.md" ]; then
    echo "  [FOUND] ARCHITECTURE.md (legacy single-file topology)"
    if is_placeholder_file "$ROOT/ARCHITECTURE.md"; then
      echo "  Content: SCAFFOLDED — placeholder/template content still present"
      topology_state="scaffolded"
    else
      echo "  Content: AUTHORED — no scaffold markers detected in markdown files"
      topology_state="authored"
    fi
    echo "    [LEGACY] Consider splitting into about/lay-and-land/"
    echo "  Local skill:"
    check_skill "lay-and-land"
  else
    echo "  [ABSENT] about/lay-and-land/"
    for d in architecture diagrams topology; do
      [ -d "$ROOT/$d" ] && echo "  [HINT] Found $d/ in root — consider consolidating under about/lay-and-land/"
    done
    [ -f "$ROOT/ARCHITECTURE.md" ] && echo "  [HINT] Found ARCHITECTURE.md in root — consider splitting into about/lay-and-land/"
    topology_state="absent"
  fi
fi
echo ""

# --- Traceability ---
doctrine_rules=0
rfc_docs=0
rfc_doctrine_refs=0
spec_docs=0
spec_source_refs=0
spec_scenarios=0
topology_docs=0
topology_cross_refs=0

if [ -n "${HAS_DIR:-}" ] && [ -f "$HAS_DIR/vision.md" ] && ! is_placeholder_file "$HAS_DIR/vision.md"; then
  doctrine_rules=$(count_numbered_list_items "$HAS_DIR/vision.md")
fi

if [ -n "${LAL_DIR:-}" ]; then
  rfc_scan_dir=""
  [ -d "$LAL_DIR/rfcs" ] && rfc_scan_dir="$LAL_DIR/rfcs"
  [ -z "$rfc_scan_dir" ] && [ -d "$LAL_DIR/adrs" ] && rfc_scan_dir="$LAL_DIR/adrs"
  if [ -n "$rfc_scan_dir" ]; then
    rfc_docs=$(count_authored_markdown_files "$rfc_scan_dir")
    rfc_doctrine_refs=$(count_files_matching "$rfc_scan_dir" '*.md' 'doctrine|principle|heart-and-soul|vision\.md|non-negotiable')
  fi
fi

if [ -d "$ROOT/openspec" ]; then
  spec_docs=$(count_files_matching "$ROOT/openspec" 'spec.md' '.')
  spec_source_refs=$(count_files_matching "$ROOT/openspec" 'spec.md' '^Source:[[:space:]]')
  spec_scenarios=$(count_files_matching "$ROOT/openspec" 'spec.md' '^#{3,4}[[:space:]]*Scenario:|^[[:space:]]*-[[:space:]]*\*\*WHEN\*\*')
fi

if [ -n "${LAY_DIR:-}" ] && [ -d "$LAY_DIR" ]; then
  topology_docs=$(count_authored_markdown_files "$LAY_DIR")
  topology_cross_refs=$(count_files_matching "$LAY_DIR" '*.md' 'RFC|heart-and-soul|legends-and-lore|openspec|doctrine|spec')
elif [ -f "$ROOT/ARCHITECTURE.md" ] && ! is_placeholder_file "$ROOT/ARCHITECTURE.md"; then
  topology_docs=1
  topology_cross_refs=$(count_paths_matching 'RFC|heart-and-soul|legends-and-lore|openspec|doctrine|spec' "$ROOT/ARCHITECTURE.md")
fi

emit_traceability_summary "$doctrine_rules" "$rfc_docs" "$rfc_doctrine_refs" "$spec_docs" "$spec_source_refs" "$spec_scenarios" "$topology_docs" "$topology_cross_refs"
echo ""

# --- Summary ---
echo "## Shape Summary"
pillars=0
[ -n "$(resolve_pillar "$ROOT/about/heart-and-soul" "$ROOT/heart-and-soul")" ] && pillars=$((pillars + 1))
[ -n "$(resolve_design_contract_dir)" ] && pillars=$((pillars + 1))
[ -d "$ROOT/openspec" ] && pillars=$((pillars + 1))
[ -n "$(resolve_topology_dir)" ] && pillars=$((pillars + 1))
[ -f "$ROOT/ARCHITECTURE.md" ] && [ "$pillars" -lt 4 ] && topology_present_by_file=1 || topology_present_by_file=0
[ "$topology_present_by_file" -eq 1 ] && pillars=$((pillars + 1))

skills=0
template_skills=0
for name in heart-and-soul legends-and-lore spec-and-spine lay-and-land; do
  for tool_dir in .claude .codex .gemini .opencode; do
    if [ -f "$ROOT/$tool_dir/skills/$name/SKILL.md" ]; then
      skills=$((skills + 1))
      is_placeholder_file "$ROOT/$tool_dir/skills/$name/SKILL.md" && template_skills=$((template_skills + 1))
      break
    fi
  done
done

scaffolded_pillars=0
for state in "${doctrine_state:-absent}" "${law_state:-absent}" "${spec_state:-absent}" "${topology_state:-absent}"; do
  case "$state" in
    scaffolded|mixed|empty) scaffolded_pillars=$((scaffolded_pillars + 1)) ;;
  esac
done

echo "  Pillars present: $pillars/4"
echo "  Local skills installed: $skills/4"
echo "  Pillars needing authoring: $scaffolded_pillars/4"
echo "  Local skill templates still uncustomized: $template_skills/4"

if [ "$pillars" -eq 0 ]; then
  echo "  Assessment: UNSHAPED — No knowledge architecture detected"
elif [ "$pillars" -eq 1 ]; then
  echo "  Assessment: NASCENT — Beginning to take shape"
elif [ "$pillars" -le 3 ]; then
  echo "  Assessment: STRUCTURED — $(( 4 - pillars )) pillar(s) missing"
elif [ "$pillars" -eq 4 ] && [ "$scaffolded_pillars" -gt 0 ]; then
  echo "  Assessment: SHAPED — Full structure present, but authored content is still incomplete"
elif [ "$pillars" -eq 4 ] && [ "$skills" -lt 4 ]; then
  echo "  Assessment: SHAPED — All pillars present, install remaining local skills"
elif [ "$pillars" -eq 4 ] && [ "$template_skills" -gt 0 ]; then
  echo "  Assessment: SHAPED — Pillars are authored, but local skill templates still need customization"
elif [ "$pillars" -eq 4 ] && {
  [ "$doctrine_rules" -eq 0 ] ||
  [ "$rfc_docs" -eq 0 ] ||
  [ "$rfc_doctrine_refs" -lt "$rfc_docs" ] ||
  [ "$spec_docs" -eq 0 ] ||
  [ "$spec_source_refs" -lt "$spec_docs" ] ||
  [ "$spec_scenarios" -lt "$spec_docs" ] ||
  [ "$topology_docs" -eq 0 ] ||
  [ "$topology_cross_refs" -eq 0 ];
}; then
  echo "  Assessment: SHAPED — Structure is complete, but traceability is not yet strong enough for mature status"
elif [ "$pillars" -eq 4 ] && [ "$skills" -eq 4 ]; then
  echo "  Assessment: MATURE — Full shape with agent navigation"
fi
