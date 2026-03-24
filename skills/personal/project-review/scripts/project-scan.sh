#!/usr/bin/env bash
# project-scan.sh — Quick automated scan of a repository's structure
# Produces a structured summary for the project-mapping subagent
#
# Usage: bash project-scan.sh [repo_root]
#   repo_root defaults to current directory
#
# Compatible with both GNU (Linux) and BSD (macOS) coreutils.

set -euo pipefail

REPO="${1:-.}"
cd "$REPO"

# Common exclusion patterns (reused across find calls)
EXCLUDES=(-not -path '*/.git/*' -not -path '*/node_modules/*' -not -path '*/vendor/*' \
  -not -path '*/dist/*' -not -path '*/build/*' -not -path '*/__pycache__/*' \
  -not -path '*/.venv/*' -not -path '*/venv/*' -not -path '*/target/*' \
  -not -path '*/.env*')

echo "=== PROJECT SCAN: $(basename "$(pwd)") ==="
echo "Path: $(pwd)"
echo "Date: $(date +%Y-%m-%d)"
echo ""

# --- Languages (by file extension) ---
echo "=== LANGUAGES (by file extension, top 15) ==="
find . -type f "${EXCLUDES[@]}" \
  -not -name '*.lock' -not -name 'package-lock.json' -not -name 'yarn.lock' \
  2>/dev/null | grep -o '\.[^./]*$' | sed 's/^\.//' | sort | uniq -c | sort -rn | head -15
echo ""

# --- Directory structure (top 2 levels, top 3 for src-like dirs) ---
echo "=== DIRECTORY STRUCTURE ==="
find . -maxdepth 2 -type d "${EXCLUDES[@]}" -not -name '.*' 2>/dev/null | sort | head -50
echo ""

# --- Package manifests ---
echo "=== PACKAGE MANIFESTS ==="
for f in package.json pyproject.toml setup.py setup.cfg Cargo.toml go.mod Gemfile \
         pom.xml build.gradle build.gradle.kts composer.json mix.exs Project.toml \
         pubspec.yaml Makefile CMakeLists.txt meson.build justfile Taskfile.yml; do
  while IFS= read -r match; do
    [ -n "$match" ] && echo "  $f: $match"
  done < <(find . -maxdepth 3 -name "$f" "${EXCLUDES[@]}" 2>/dev/null | head -5)
done
echo ""

# --- Lock files ---
echo "=== LOCK FILES ==="
for f in package-lock.json yarn.lock pnpm-lock.yaml poetry.lock Pipfile.lock \
         Cargo.lock go.sum Gemfile.lock composer.lock mix.lock pubspec.lock; do
  while IFS= read -r match; do
    [ -n "$match" ] && echo "  $f: $match"
  done < <(find . -maxdepth 3 -name "$f" -not -path '*/node_modules/*' 2>/dev/null | head -3)
done
echo ""

# --- CI/CD ---
echo "=== CI/CD CONFIGURATION ==="
for f in .github/workflows .gitlab-ci.yml Jenkinsfile .circleci bitbucket-pipelines.yml \
         .travis.yml appveyor.yml azure-pipelines.yml .buildkite; do
  if [ -e "$f" ]; then
    echo "  Found: $f"
    if [ -d "$f" ]; then
      ls -1 "$f" 2>/dev/null | head -10 | sed 's/^/    /'
    fi
  fi
done
echo ""

# --- Deploy / Infrastructure ---
echo "=== DEPLOY / INFRASTRUCTURE ==="
for f in Dockerfile docker-compose.yml docker-compose.yaml \
         fly.toml render.yaml railway.json vercel.json netlify.toml \
         serverless.yml serverless.yaml sam-template.yaml \
         Procfile app.yaml; do
  while IFS= read -r match; do
    [ -n "$match" ] && echo "  $f: $match"
  done < <(find . -maxdepth 3 -name "$f" "${EXCLUDES[@]}" 2>/dev/null | head -3)
done
for d in k8s kubernetes terraform pulumi infra deploy .terraform; do
  [ -d "$d" ] && echo "  Directory: $d/"
done
echo ""

# --- Database / Migrations ---
echo "=== DATABASE / MIGRATIONS ==="
for d in migrations alembic prisma drizzle knex sql; do
  while IFS= read -r match; do
    if [ -n "$match" ]; then
      count=$(find "$match" -type f 2>/dev/null | wc -l | tr -d ' ')
      echo "  $match/ ($count files)"
    fi
  done < <(find . -maxdepth 4 -type d -name "$d" "${EXCLUDES[@]}" 2>/dev/null | head -3)
done
# Also check nested paths
for d in db/migrate db/migrations; do
  [ -d "$d" ] && echo "  $d/ ($(find "$d" -type f 2>/dev/null | wc -l | tr -d ' ') files)"
done
# Schema files
for pattern in schema.prisma schema.sql drizzle.config.ts drizzle.config.js knexfile.js knexfile.ts; do
  while IFS= read -r match; do
    [ -n "$match" ] && echo "  Schema: $match"
  done < <(find . -maxdepth 4 -name "$pattern" "${EXCLUDES[@]}" 2>/dev/null | head -3)
done
echo ""

# --- API schemas ---
echo "=== API SCHEMAS ==="
for pattern in openapi.yaml openapi.json swagger.yaml swagger.json schema.graphql; do
  while IFS= read -r match; do
    [ -n "$match" ] && echo "  $match"
  done < <(find . -maxdepth 4 -name "$pattern" "${EXCLUDES[@]}" 2>/dev/null | head -5)
done
# GraphQL files
gql_count=$(find . -name '*.graphql' -o -name '*.gql' 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ' || echo 0)
[ "${gql_count:-0}" -gt 0 ] && echo "  GraphQL files: $gql_count"
# Proto files
proto_count=$(find . -name '*.proto' 2>/dev/null | grep -v node_modules | wc -l | tr -d ' ' || echo 0)
[ "${proto_count:-0}" -gt 0 ] && echo "  Protobuf files: $proto_count"
echo ""

# --- Test structure ---
echo "=== TEST STRUCTURE ==="
for d in tests test __tests__ spec e2e cypress playwright; do
  while IFS= read -r dir; do
    if [ -n "$dir" ]; then
      count=$(find "$dir" -type f 2>/dev/null | wc -l | tr -d ' ')
      echo "  $dir/ ($count files)"
    fi
  done < <(find . -maxdepth 3 -type d -name "$d" -not -path '*/node_modules/*' 2>/dev/null | head -5)
done
# Test config files
for f in jest.config.js jest.config.ts vitest.config.ts vitest.config.js \
         pytest.ini conftest.py .mocharc.yml .mocharc.json \
         cypress.config.ts cypress.config.js playwright.config.ts playwright.config.js; do
  [ -e "$f" ] && echo "  Config: $f"
done
# Coverage config
for f in .nycrc .nycrc.json .c8rc .coveragerc .istanbul.yml codecov.yml; do
  [ -e "$f" ] && echo "  Coverage: $f"
done
# Count test files
test_count=$(find . -type f \( -name '*test*' -o -name '*spec*' -o -name '*_test.*' \) \
  -not -path '*/node_modules/*' -not -path '*/.git/*' -not -path '*/vendor/*' 2>/dev/null | wc -l | tr -d ' ')
echo "  Total test files found: $test_count"
echo ""

# --- Linting / Formatting ---
echo "=== LINTING / FORMATTING ==="
for f in .eslintrc .eslintrc.js .eslintrc.json .eslintrc.yml eslint.config.js eslint.config.mjs \
         .prettierrc .prettierrc.json .prettierrc.yml prettier.config.js \
         ruff.toml .flake8 .pylintrc mypy.ini .mypy.ini pyright \
         .rubocop.yml .golangci.yml clippy.toml rustfmt.toml \
         .editorconfig biome.json biome.jsonc deno.json \
         .stylelintrc .stylelintrc.json; do
  [ -e "$f" ] && echo "  $f"
done
# Pre-commit hooks
for f in .pre-commit-config.yaml .husky; do
  [ -e "$f" ] && echo "  Pre-commit: $f"
done
# Type checking configs
for f in tsconfig.json pyrightconfig.json; do
  [ -e "$f" ] && echo "  Types: $f"
done
echo ""

# --- Documentation ---
echo "=== DOCUMENTATION ==="
for f in README.md README.rst README.txt CHANGELOG.md CHANGELOG.rst CHANGES.md \
         CONTRIBUTING.md CODE_OF_CONDUCT.md LICENSE LICENSE.md LICENSE.txt \
         ARCHITECTURE.md SECURITY.md ADR; do
  if [ -e "$f" ]; then
    if [ -d "$f" ]; then
      adr_count=$(find "$f" -type f 2>/dev/null | wc -l | tr -d ' ')
      echo "  $f/ ($adr_count files)"
    else
      lines=$(wc -l < "$f" 2>/dev/null | tr -d ' ' || echo "?")
      echo "  $f ($lines lines)"
    fi
  fi
done
if [ -d "docs" ]; then
  doc_count=$(find docs -type f 2>/dev/null | wc -l | tr -d ' ')
  echo "  docs/ directory ($doc_count files)"
fi
if [ -d "examples" ]; then
  ex_count=$(find examples -type f 2>/dev/null | wc -l | tr -d ' ')
  echo "  examples/ directory ($ex_count files)"
fi
echo ""

# --- Governance & Automation ---
echo "=== GOVERNANCE & AUTOMATION ==="
for f in CODEOWNERS .github/CODEOWNERS docs/CODEOWNERS; do
  [ -e "$f" ] && echo "  CODEOWNERS: $f"
done
for f in renovate.json .renovaterc .renovaterc.json .github/renovate.json \
         .github/dependabot.yml .dependabot/config.yml; do
  [ -e "$f" ] && echo "  Dep updates: $f"
done
for f in .github/SECURITY.md SECURITY.md; do
  [ -e "$f" ] && echo "  Security policy: $f"
done
# Runtime version pins
for f in .nvmrc .node-version .ruby-version .python-version .tool-versions .mise.toml; do
  [ -e "$f" ] && echo "  Runtime pin: $f"
done
echo ""

# --- Monorepo signals ---
echo "=== MONOREPO SIGNALS ==="
for f in nx.json lerna.json turbo.json pnpm-workspace.yaml rush.json; do
  [ -e "$f" ] && echo "  Found: $f"
done
if [ -d "packages" ]; then
  pkg_count=$(find packages -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  echo "  packages/ ($pkg_count packages)"
fi
if [ -d "apps" ]; then
  app_count=$(find apps -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l | tr -d ' ')
  echo "  apps/ ($app_count apps)"
fi
echo ""

# --- Git signals ---
echo "=== GIT SIGNALS ==="
if [ -d ".git" ]; then
  echo "  Commits: $(git rev-list --count HEAD 2>/dev/null || echo 'unknown')"
  echo "  Contributors: $(git shortlog -sn --no-merges HEAD 2>/dev/null | wc -l | tr -d ' ')"
  echo "  First commit: $(git log --reverse --format='%ai' 2>/dev/null | head -1 || echo 'unknown')"
  echo "  Latest commit: $(git log -1 --format='%ai' 2>/dev/null || echo 'unknown')"
  echo "  Tags: $(git tag 2>/dev/null | wc -l | tr -d ' ')"
  latest_tag=$(git describe --tags --abbrev=0 2>/dev/null || echo 'none')
  echo "  Latest tag: $latest_tag"
  echo "  Branches: $(git branch -a 2>/dev/null | wc -l | tr -d ' ')"
  # Shallow clone detection
  if [ -f ".git/shallow" ]; then
    echo "  WARNING: Shallow clone detected — commit counts may be inaccurate"
  fi
  if [ -f ".gitmodules" ]; then
    submod_count=$(grep -c '\[submodule' .gitmodules 2>/dev/null || echo '0')
    echo "  Submodules: $submod_count"
  fi
  # Churn hotspots (top 10 most-changed files in last 500 commits)
  echo "  --- Churn hotspots (top 10, last 500 commits) ---"
  git log --oneline -500 --name-only --pretty=format: 2>/dev/null \
    | sort | uniq -c | sort -rn | head -10 | sed 's/^/    /'
fi
echo ""

# --- Repo size ---
echo "=== REPO SIZE (excluding .git, node_modules, vendor) ==="
total_files=$(find . -type f "${EXCLUDES[@]}" 2>/dev/null | wc -l | tr -d ' ')
echo "  Total files: $total_files"

# Source file count and lines (approximate, using xargs in batches)
src_files=$(find . -type f \
  \( -name '*.ts' -o -name '*.tsx' -o -name '*.js' -o -name '*.jsx' \
     -o -name '*.py' -o -name '*.go' -o -name '*.rs' -o -name '*.java' \
     -o -name '*.rb' -o -name '*.c' -o -name '*.cpp' -o -name '*.h' \
     -o -name '*.cs' -o -name '*.swift' -o -name '*.kt' -o -name '*.scala' \
     -o -name '*.ex' -o -name '*.exs' -o -name '*.hs' -o -name '*.ml' \
     -o -name '*.php' -o -name '*.lua' -o -name '*.sh' -o -name '*.bash' \
     -o -name '*.zsh' -o -name '*.vim' -o -name '*.el' \) \
  "${EXCLUDES[@]}" 2>/dev/null || true)

if [ -n "$src_files" ]; then
  src_count=$(echo "$src_files" | wc -l | tr -d ' ')
  # Use xargs with batch size to avoid ARG_MAX
  src_lines=$(echo "$src_files" | xargs -L 500 wc -l 2>/dev/null | awk '/total$/{s+=$1} END{print s+0}')
  # If no "total" lines (single batch), sum all
  if [ "$src_lines" = "0" ]; then
    src_lines=$(echo "$src_files" | xargs wc -l 2>/dev/null | tail -1 | awk '{print $1}')
  fi
  echo "  Source files: $src_count"
  echo "  Source lines: ~$src_lines"
fi
echo ""

echo "=== SCAN COMPLETE ==="
