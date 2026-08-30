#!/usr/bin/env bash
# repo-contract-test.sh — minimal repo-contract drift guard (aib-86z).
#
# Enforces exactly two v1-mandatory requirements from
# openspec/changes/bootstrap-project-shape/specs/repository-shape/spec.md:
#
#   Spec: REQ-repository-shape-002 (Provenance Visibility)
#     README's "Skills Layout And Provenance" section and .gitmodules must
#     agree on the submodule inventory, both directions; active skill catalog
#     entries must come from skills/personal and no skill gitlink may remain.
#
#   Spec: REQ-repository-shape-006 (Local-Only State Exclusion)
#     No tracked file may be (a) matched by .gitignore (declared-local-state
#     drift) or (b) on the never-track denylist (session/auth/cache state).
#
# Deliberately nothing broader — v1 (about/heart-and-soul/v1.md) defers full
# mirror-surface validation; scope decision recorded in
# about/legends-and-lore/decisions/2026-07-06-adopt-minimal-repo-contract-guard.md.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

fail_count=0
_pass() { echo "  PASS: $1"; }
_fail() { echo "  FAIL: $1" >&2; fail_count=$((fail_count + 1)); }

# ── Check 1: provenance (REQ-repository-shape-002) ───────────────────────────
echo "=== README provenance vs .gitmodules ==="

section=$(awk '/^## Skills Layout And Provenance/{f=1;next} f&&/^## /{exit} f' README.md)
if [[ -z "$section" ]]; then
  _fail "README.md has no '## Skills Layout And Provenance' section"
else
  # Forward: every registered submodule is mentioned in the section
  while read -r path; do
    if grep -qF "$path" <<<"$section"; then
      _pass "submodule mentioned in README: $path"
    else
      _fail "submodule missing from README provenance section: $path"
    fi
  done < <(git config -f .gitmodules --get-regexp 'submodule\..*\.path' | awk '{print $2}')

  # Reverse: every path the README claims as a current submodule is registered.
  # Anchored on the "current submodule inventory is" sentence; if that wording changes,
  # fail loudly so this check gets updated rather than silently skipping.
  claimed_block=$(sed -n '/current submodule inventory is/,/only\./p' <<<"$section")
  if [[ -z "$claimed_block" ]]; then
    _fail "README provenance section lost its 'current submodule inventory is' sentence — update this check's anchor"
  else
    while read -r tok; do
      if git config -f .gitmodules --get-regexp 'submodule\..*\.path' | awk '{print $2}' | grep -qxF "$tok"; then
        _pass "README-claimed submodule is registered: $tok"
      else
        _fail "README claims submodule not in .gitmodules: $tok"
      fi
    done < <(grep -oE '`[^`]+`' <<<"$claimed_block" | tr -d '\`')
  fi
fi

# ── Check 2: active skill catalog topology ───────────────────────────────────
echo "=== active skill catalog topology ==="

manifest=$(./scripts/link-ai-skills.sh --catalog-manifest .)
expected_skills='["beads-orchestration","bws-cli-skill","th-design","th-engineering","th-projects","th-tooling","th-writing"]'

if jq -e --argjson expected "$expected_skills" \
    '([.skills[].name] | sort) == ($expected | sort)' <<<"$manifest" >/dev/null; then
  _pass "catalog contains the intentional active roots"
else
  _fail "catalog roots differ from the intentional active set"
fi

if jq -e '.excluded_names == [] and all(.skills[]; .source | startswith("skills/personal/"))' \
    <<<"$manifest" >/dev/null; then
  _pass "every active root resolves from skills/personal with no name exclusions"
else
  _fail "catalog contains a non-personal source or stale exclusion"
fi

architecture=$(awk '/^## Architecture Overview/{f=1;next} f&&/^## /{exit} f' CLAUDE.md)
expected_routers='`beads-orchestration`, `th-design`, `th-engineering`, `th-projects`, `th-tooling`, `th-writing`'
compact_architecture=$(tr '\n' ' ' <<<"$architecture" | tr -s ' ')
if [[ "$compact_architecture" == *'Active authored roots live in `skills/personal/`;'* ]] \
    && [[ "$compact_architecture" == *'`skills/archive/` is pruned mixed-origin history.'* ]] \
    && [[ "$compact_architecture" == *"Six router-style active roots ($expected_routers)"* ]] \
    && [[ "$compact_architecture" == *'`bws-cli-skill` is the narrow standalone root.'* ]]; then
  _pass "CLAUDE.md architecture matches catalog source, archive, and router topology"
else
  _fail "CLAUDE.md Architecture Overview drifted from the active catalog topology"
fi

skill_gitlinks=$(git ls-files -s skills | awk '$1 == 160000 {print $4}')
if [[ -z "$skill_gitlinks" ]]; then
  _pass "no gitlink remains under skills/"
else
  _fail "gitlinks remain under skills/:"
  sed 's/^/         /' <<<"$skill_gitlinks" >&2
fi

# ── Check 3: tracked local-only state (REQ-repository-shape-006) ─────────────
echo "=== tracked local-state exclusion ==="

ignored_tracked=$(git ls-files -ci --exclude-standard)
if [[ -z "$ignored_tracked" ]]; then
  _pass "no tracked file is matched by .gitignore"
else
  _fail "tracked-but-ignored files (declared local state committed to git):"
  sed 's/^/         /' <<<"$ignored_tracked" >&2
fi

DENYLIST=('*.sqlite' '*.sqlite3' '*.log' '*settings.local.json' '*auth.json' '*oauth_creds.json' '*installation_id')
for pat in "${DENYLIST[@]}"; do
  hits=$(git ls-files -- "$pat")
  if [[ -z "$hits" ]]; then
    _pass "no tracked files match denylist pattern: $pat"
  else
    _fail "tracked local-state files match '$pat':"
    sed 's/^/         /' <<<"$hits" >&2
  fi
done

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
if [[ $fail_count -gt 0 ]]; then
  echo "FAIL: $fail_count repo-contract check(s) failed"
  exit 1
fi
echo "PASS: repo contract holds (REQ-repository-shape-002, catalog topology, REQ-repository-shape-006)"
