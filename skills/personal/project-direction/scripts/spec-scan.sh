#!/usr/bin/env bash
# spec-scan.sh — Discover specification, design, roadmap, and planning artifacts in a repo
# Produces a structured inventory for the direction-model subagent
#
# Usage: bash spec-scan.sh [repo_root]
#   repo_root defaults to current directory
#
# Compatible with GNU (Linux) and BSD (macOS) coreutils.

set -euo pipefail

REPO="${1:-.}"
cd "$REPO"

EXCLUDES=(-not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/vendor/*' \
  -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/__pycache__/*' \
  -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/target/*')

echo "=== SPEC SCAN: $(basename "$(pwd)") ==="
echo "Path: $(pwd)"
echo "Date: $(date +%Y-%m-%d)"
echo ""

# --- Specification artifacts ---
echo "=== SPECIFICATION ARTIFACTS ==="
# OpenSpec directories
for d in openspec spec specs specification design; do
  if [ -d "$d" ]; then
    count=$(find "$d" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "  $d/ ($count files)"
    find "$d" -type f -name '*.md' -o -name '*.yaml' -o -name '*.yml' -o -name '*.json' \
      2>/dev/null | sort | head -20 | sed 's/^/    /'
  fi
done
# Spec files at root or in docs
for pattern in SPEC.md SPECIFICATION.md DESIGN.md ARCHITECTURE.md REQUIREMENTS.md; do
  while IFS= read -r match; do
    if [ -n "$match" ]; then
      lines=$(wc -l < "$match" 2>/dev/null | tr -d ' ' || echo "?")
      echo "  $match ($lines lines)"
    fi
  done < <(find . -maxdepth 3 -name "$pattern" "${EXCLUDES[@]}" 2>/dev/null | head -5)
done
echo ""

# --- Design documents ---
echo "=== DESIGN DOCUMENTS ==="
for d in docs/design docs/architecture docs/adr ADR adr rfcs RFC docs/rfcs; do
  if [ -d "$d" ]; then
    count=$(find "$d" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "  $d/ ($count files)"
    find "$d" -type f -name '*.md' 2>/dev/null | sort | head -15 | sed 's/^/    /'
  fi
done
echo ""

# --- Roadmap and planning ---
echo "=== ROADMAP & PLANNING ==="
for pattern in ROADMAP.md ROADMAP.rst TODO.md BACKLOG.md MILESTONES.md PLAN.md STATUS.md; do
  while IFS= read -r match; do
    if [ -n "$match" ]; then
      lines=$(wc -l < "$match" 2>/dev/null | tr -d ' ' || echo "?")
      echo "  $match ($lines lines)"
    fi
  done < <(find . -maxdepth 3 -name "$pattern" "${EXCLUDES[@]}" 2>/dev/null | head -5)
done
# Planning directories
for d in .pm docs/plans plans roadmap; do
  if [ -d "$d" ]; then
    count=$(find "$d" -type f 2>/dev/null | wc -l | tr -d ' ')
    echo "  $d/ ($count files)"
    find "$d" -type f -name '*.md' 2>/dev/null | sort | head -10 | sed 's/^/    /'
  fi
done
echo ""

# --- Agent and AI context docs ---
echo "=== AGENT / AI CONTEXT ==="
for pattern in AGENTS.md CLAUDE.md CODEX.md .cursorrules .clinerules; do
  while IFS= read -r match; do
    if [ -n "$match" ]; then
      lines=$(wc -l < "$match" 2>/dev/null | tr -d ' ' || echo "?")
      echo "  $match ($lines lines)"
    fi
  done < <(find . -maxdepth 3 -name "$pattern" "${EXCLUDES[@]}" 2>/dev/null | head -5)
done
for d in .claude .codex .gemini .genai genai ai-bootstrap; do
  if [ -d "$d" ]; then
    echo "  $d/ (AI tool config)"
  fi
done
echo ""

# --- Issue tracking artifacts ---
echo "=== ISSUE TRACKING ==="
# Beads
if [ -d ".beads" ]; then
  open_count=$(set +o pipefail; find .beads -name '*.json' -exec grep -l '"status":"open"\|"status":"in_progress"' {} \; 2>/dev/null | wc -l | tr -d ' ')
  total_count=$(set +o pipefail; find .beads -name '*.json' -type f 2>/dev/null | wc -l | tr -d ' ')
  echo "  .beads/ ($total_count issues, ~$open_count open/in_progress)"
fi
# GitHub issues reference
if [ -d ".github" ]; then
  for f in .github/ISSUE_TEMPLATE .github/ISSUE_TEMPLATE.md; do
    [ -e "$f" ] && echo "  Issue templates: $f"
  done
fi
# Linear/Jira references in docs
linear_refs=$(set +o pipefail; grep -rl 'linear\.app\|LIN-\|LINEAR-' . --include='*.md' 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
[ "${linear_refs:-0}" -gt 0 ] 2>/dev/null && echo "  Linear references found in $linear_refs files"
jira_refs=$(set +o pipefail; grep -rl 'jira\.\|JIRA-\|atlassian' . --include='*.md' 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ')
[ "${jira_refs:-0}" -gt 0 ] 2>/dev/null && echo "  Jira references found in $jira_refs files"
echo ""

# --- README and top-level docs ---
echo "=== TOP-LEVEL DOCUMENTATION ==="
for f in README.md README.rst README.txt CHANGELOG.md CHANGES.md \
         CONTRIBUTING.md LICENSE LICENSE.md SECURITY.md; do
  if [ -e "$f" ]; then
    lines=$(wc -l < "$f" 2>/dev/null | tr -d ' ' || echo "?")
    echo "  $f ($lines lines)"
  fi
done
if [ -d "docs" ]; then
  doc_count=$(find docs -type f 2>/dev/null | wc -l | tr -d ' ')
  echo "  docs/ ($doc_count files)"
fi
if [ -d "examples" ]; then
  ex_count=$(find examples -type f 2>/dev/null | wc -l | tr -d ' ')
  echo "  examples/ ($ex_count files)"
fi
echo ""

# --- Project structure summary ---
echo "=== PROJECT STRUCTURE (top 2 levels) ==="
find . -maxdepth 2 -type d "${EXCLUDES[@]}" -not -name '.*' 2>/dev/null | sort | head -40
echo ""

# --- Package manifests (for project metadata) ---
echo "=== PACKAGE METADATA ==="
for f in package.json pyproject.toml Cargo.toml go.mod; do
  while IFS= read -r match; do
    [ -n "$match" ] && echo "  $match"
  done < <(find . -maxdepth 2 -name "$f" "${EXCLUDES[@]}" 2>/dev/null | head -3)
done
echo ""

# --- Git signals ---
echo "=== GIT SIGNALS ==="
if [ -d ".git" ]; then
  echo "  Commits: $(git rev-list --count HEAD 2>/dev/null || echo 'unknown')"
  echo "  Contributors: $(git shortlog -sn --no-merges HEAD 2>/dev/null | wc -l | tr -d ' ')"
  echo "  Latest commit: $(git log -1 --format='%ai %s' 2>/dev/null || echo 'unknown')"
  echo "  Tags: $(git tag 2>/dev/null | wc -l | tr -d ' ')"
  latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo 'none')
  echo "  Latest tag: $latest_tag"
  if [ -f ".git/shallow" ]; then
    echo "  WARNING: Shallow clone — history may be incomplete"
  fi
  # Recent activity by area (last 200 commits)
  echo "  --- Recent activity by directory (last 200 commits) ---"
  { git log --oneline -200 --name-only --pretty=format: 2>/dev/null \
    | grep '/' | sed 's|/.*||' | sort | uniq -c | sort -rn | head -10 | sed 's/^/    /'; } || true
  # Recent spec/doc changes
  echo "  --- Recent spec/doc changes (last 50 commits) ---"
  { git log --oneline -50 --diff-filter=AM -- '*.md' 'openspec/' 'spec/' 'docs/' 'SPEC*' 'DESIGN*' 'ARCHITECTURE*' 'ROADMAP*' 2>/dev/null | head -10 | sed 's/^/    /'; } || true
fi
echo ""

# --- Test structure (brief) ---
echo "=== TEST STRUCTURE (brief) ==="
test_count=$(find . -type f \( -name '*test*' -o -name '*spec*' -o -name '*_test.*' \) \
  "${EXCLUDES[@]}" 2>/dev/null | wc -l | tr -d ' ')
echo "  Total test files: $test_count"
for d in tests test __tests__ spec e2e; do
  while IFS= read -r dir; do
    if [ -n "$dir" ]; then
      count=$(find "$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
      echo "  $dir/ ($count files)"
    fi
  done < <(find . -maxdepth 2 -type d -name "$d" -not -path '*/node_modules/*' 2>/dev/null | head -3)
done
echo ""

# --- CI/CD (brief) ---
echo "=== CI/CD (brief) ==="
for f in .github/workflows .gitlab-ci.yml Jenkinsfile .circleci; do
  if [ -e "$f" ]; then
    echo "  Found: $f"
    [ -d "$f" ] && ls -1 "$f" 2>/dev/null | head -5 | sed 's/^/    /'
  fi
done
echo ""

echo "=== SCAN COMPLETE ==="
