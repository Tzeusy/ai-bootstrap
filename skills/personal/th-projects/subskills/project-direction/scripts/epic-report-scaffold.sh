#!/usr/bin/env bash
# epic-report-scaffold.sh — Generate initial report scaffold for a beads epic
# Creates the report file, diagram directory, and populates metadata from beads
#
# Usage: bash epic-report-scaffold.sh <epic-id> [repo_root]
#   epic-id: The beads epic ID
#   repo_root: defaults to current directory
#
# Requires: bd (beads CLI), jq, git

set -euo pipefail

# Escape characters that would trigger expansion inside an unquoted heredoc.
# Backslash must be escaped first, then backtick and dollar, so that strings
# sourced from bd/jq/git (which we do not control) are rendered as literal text
# rather than executed as command substitutions or variable expansions.
heredoc_escape() {
  local s="$1"
  s="${s//\\/\\\\}"   # backslash -> \\
  s="${s//\`/\\\`}"   # backtick  -> \`
  s="${s//\$/\\\$}"   # dollar    -> \$
  printf '%s' "$s"
}

# Like heredoc_escape but leaves backslashes untouched. Used for the children
# table, whose markdown pipe-escapes (\|) are produced by jq and would be
# corrupted if backslashes were doubled. Still neutralizes the command/var
# expansion vectors (backtick, dollar) that the unquoted heredoc would honor.
heredoc_escape_keep_backslash() {
  local s="$1"
  s="${s//\`/\\\`}"   # backtick -> \`
  s="${s//\$/\\\$}"   # dollar   -> \$
  printf '%s' "$s"
}

if [ -z "${1:-}" ]; then
  echo "Usage: epic-report-scaffold.sh <epic-id> [repo_root]"
  echo "  epic-id: The beads epic ID (e.g., beads-abc123)"
  exit 1
fi

EPIC_ID="$1"
REPO="${2:-.}"
cd "$REPO"

# --- Gather epic data ---
echo "Gathering epic data for $EPIC_ID..."

epic_json=$(bd show "$EPIC_ID" --json 2>/dev/null) || {
  echo "ERROR: Could not find epic $EPIC_ID (bd show failed)"
  exit 1
}

# Validate we got real JSON with a title
epic_title=$(echo "$epic_json" | jq -r '.title // empty' 2>/dev/null)
if [ -z "$epic_title" ]; then
  echo "ERROR: Could not find epic $EPIC_ID or it has no title"
  exit 1
fi

epic_desc=$(echo "$epic_json" | jq -r '.description // ""')
epic_status=$(echo "$epic_json" | jq -r '.status // "unknown"')
epic_type=$(echo "$epic_json" | jq -r '.type // "unknown"')
epic_priority=$(echo "$epic_json" | jq -r '.priority // "unknown"')

echo "  Title: $epic_title"
echo "  Status: $epic_status"

# --- Gather children ---
children_json=$(bd children "$EPIC_ID" --json 2>/dev/null || echo '[]')
total_children=$(echo "$children_json" | jq 'length')
closed_children=$(echo "$children_json" | jq '[.[] | select(.status == "closed")] | length')

echo "  Children: $closed_children/$total_children closed"

# --- Create slug ---
slug=$(echo "$epic_title" | tr '[:upper:]' '[:lower:]' | sed 's/[^a-z0-9]/-/g' | sed 's/--*/-/g' | sed 's/^-//' | sed 's/-$//' | cut -c1-50)

# --- Create directories ---
report_dir="docs/reports"
diagram_dir="$report_dir/diagrams"
mkdir -p "$diagram_dir"

report_file="$report_dir/${EPIC_ID}-${slug}.md"
echo "  Report: $report_file"

# --- Gather git data ---
date_str=$(date +%Y-%m-%d)

# Find commits referencing this epic or its children.
# Pass each id as its own --grep flag; git ORs multiple --grep patterns,
# so this catches both epic and child commits without regex-escaping issues.
child_ids=$(echo "$children_json" | jq -r '.[].id' 2>/dev/null || true)
grep_args=(--grep="$EPIC_ID")
for cid in $child_ids; do
  grep_args+=(--grep="$cid")
done

commit_log=$(git log --oneline --all "${grep_args[@]}" 2>/dev/null | head -20 || echo "(no commits found referencing $EPIC_ID)")

# Files changed (approximate — from commits mentioning the epic or its children)
files_changed=$(git log --all "${grep_args[@]}" --name-only --pretty=format: 2>/dev/null | sort -u | grep -v '^$' | head -30 || echo "(could not determine)")

# --- Generate children table ---
children_table=""
if [ "$total_children" -gt 0 ]; then
  # jq escapes markdown pipes in titles (| -> \|) so a title cannot add table
  # columns. Note: heredoc_escape is NOT applied to children_table (it would
  # double the backslash of \|); instead the targeted escape below neutralizes
  # backtick/dollar without disturbing the jq-produced \| sequence.
  children_table=$(echo "$children_json" | jq -r '.[] | "| \(.id) | \(.title | gsub("\\|"; "\\|")) | \(.status) | \(.priority // "—") | \(.type // "task") |"')
fi

# --- Sanitize untrusted strings before heredoc interpolation ---
# These come from bd/jq (epic/children metadata) or git (commit subjects /
# file paths) and must not be able to execute via the unquoted heredoc.
epic_title=$(heredoc_escape "$epic_title")
epic_desc=$(heredoc_escape "$epic_desc")
epic_status=$(heredoc_escape "$epic_status")
epic_priority=$(heredoc_escape "$epic_priority")
children_table=$(heredoc_escape_keep_backslash "$children_table")
commit_log=$(heredoc_escape "$commit_log")
files_changed=$(heredoc_escape "$files_changed")

# --- Write scaffold ---
cat > "$report_file" << SCAFFOLD
# Epic Report: $epic_title

**Epic ID**: \`$EPIC_ID\`
**Date**: $date_str
**Status**: $closed_children/$total_children children closed ($epic_status)
**Priority**: $epic_priority
**Spec coverage**: <!-- TODO: list spec sections covered -->

## Summary

<!-- TODO: 2-3 paragraphs covering:
  - What was built and why (link to project spirit)
  - Key design decisions made during implementation
  - Current state: what works, what's provisional, what's deferred
-->

$epic_desc

---

## Architecture

<!-- TODO: Generate 1-2 excalidraw diagrams showing what was built.
  Color conventions:
  - New/added: #a7f3d0 (green)
  - Modified: #fef3c7 (yellow)
  - Existing: #e2e8f0 (gray)
  - Removed: #fecaca (red)
  - External: #ddd6fe (purple)

  Generate .excalidraw file using /th-engineering (excalidraw-diagram) skill, then render to SVG.
-->

<!-- ![Architecture overview](diagrams/${EPIC_ID}-architecture.svg) -->

---

## Implementation

### Children

| Bead ID | Title | Status | Priority | Type |
|---------|-------|--------|----------|------|
$children_table

<!-- TODO: For each child bead, expand with:
  - What was done (1-3 sentences)
  - Key code locations (file:line-range format)
  - Design decisions
  - Caveats / known limitations
-->

---

## Spec Compliance

<!-- TODO: Map spec sections to implementation status -->

| Spec Section | Status | Evidence | Notes |
|-------------|--------|---------|-------|
| <!-- spec/section --> | <!-- Implemented/Partial/Deferred --> | <!-- file:line --> | <!-- notes --> |

---

## Test Coverage

### New/changed test files

| File | Tests | What it covers |
|------|-------|---------------|
| <!-- test file --> | <!-- count --> | <!-- description --> |

### Coverage gaps

| Area | Why untested | Risk | Follow-up? |
|------|------------|------|-----------|
| <!-- component --> | <!-- reason --> | <!-- H/M/L --> | <!-- bead ID or "no" --> |

### Test confidence

<!-- TODO: Brief assessment — behavior vs implementation testing, critical path coverage -->

---

## Subsequent Work

### Open beads (existing)

<!-- TODO: List any remaining open children -->

### New follow-up beads

<!-- TODO: Create follow-up beads for remaining TODOs:
  bd create --title="..." --type=task --priority=2 --parent=$EPIC_ID --json
-->

| Bead ID | Title | Type | Priority | Rationale |
|---------|-------|------|----------|-----------|
| <!-- new-bead-id --> | <!-- title --> | <!-- task/bug --> | <!-- P0-P4 --> | <!-- why --> |

### Deferred decisions

| Decision | Context | Revisit when |
|----------|---------|-------------|
| <!-- what --> | <!-- why deferred --> | <!-- trigger --> |

---

## Risks & Notes for Reviewer

### Known risks

| Risk | Severity | Mitigation | Evidence |
|------|----------|-----------|----------|
| <!-- risk --> | <!-- H/M/L --> | <!-- action --> | <!-- file:line --> |

### Questions for reviewer

<!-- TODO: Design decisions needing human judgment, assumptions made -->

### What to look at first

<!-- TODO: Prioritized files/areas for human review -->

---

## Appendix

### A. Commits referencing this epic

\`\`\`
$commit_log
\`\`\`

### B. Files changed

\`\`\`
$files_changed
\`\`\`

### C. Diagram source files

| Diagram | Source | Rendered |
|---------|--------|----------|
| <!-- Architecture --> | \`diagrams/${EPIC_ID}-architecture.excalidraw\` | \`diagrams/${EPIC_ID}-architecture.svg\` |
SCAFFOLD

echo ""
echo "=== Scaffold generated: $report_file ==="
echo ""
echo "Next steps:"
echo "  1. Fill in TODO sections"
echo "  2. Generate excalidraw diagrams and render to SVG"
echo "  3. Create follow-up beads for remaining work"
echo "  4. Link report to epic: bd update $EPIC_ID --append-notes \"Report: $report_file\""
echo "  5. Commit report + diagrams"
