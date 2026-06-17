#!/usr/bin/env bash
# validate-th-projects.sh — Package-level validator for skills/personal/th-projects.
#
# Runs from any working directory; resolves all paths from BASH_SOURCE.
# Checks: shell syntax, project-shape self-tests, and fixture structural
# invariants (including the overclaim gate check for project-review).
#
# Exit 0 = all checks passed. Exit 1 = one or more failures.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

pass_count=0
fail_count=0

_pass() { echo "  PASS: $1"; pass_count=$((pass_count + 1)); }
_fail() { echo "  FAIL: $1" >&2; fail_count=$((fail_count + 1)); }
section() { echo ""; echo "=== $1 ==="; }

# ── helpers ───────────────────────────────────────────────────────────────────

require_file() {
  local file="$1" label="$2"
  if [[ -f "$file" ]]; then
    _pass "$label"
    return 0
  else
    _fail "$label (missing: ${file#"$ROOT/"})"
    return 1
  fi
}

check_pattern() {
  local file="$1" pattern="$2" label="$3"
  if grep -Eq "$pattern" "$file"; then
    _pass "$label"
  else
    _fail "$label (pattern not found in ${file#"$ROOT/"})"
  fi
}

# ── 1. Shell syntax check ─────────────────────────────────────────────────────
section "Shell syntax check"

shopt -s nullglob
all_scripts=()
while IFS= read -r -d '' s; do
  all_scripts+=("$s")
done < <(find "$ROOT" -path '*/scripts/*.sh' -print0)
shopt -u nullglob

if [[ ${#all_scripts[@]} -eq 0 ]]; then
  _fail "no .sh scripts found under th-projects/*/scripts/"
else
  for script in "${all_scripts[@]}"; do
    rel="${script#"$ROOT/"}"
    if err_output=$(bash -n "$script" 2>&1); then
      _pass "syntax OK: $rel"
    else
      _fail "syntax error in $rel: $err_output"
    fi
  done
fi

# ── 2. project-shape self-tests ───────────────────────────────────────────────
section "project-shape self-tests"

SHAPE_SCRIPTS="$ROOT/subskills/project-shape/scripts"

for script_name in self-test.sh eval-fallbacks.sh; do
  script_path="$SHAPE_SCRIPTS/$script_name"
  if [[ ! -f "$script_path" ]]; then
    _fail "script missing: subskills/project-shape/scripts/$script_name"
    continue
  fi
  echo ""
  echo "  -- running $script_name --"
  if bash "$script_path"; then
    _pass "subskills/project-shape/scripts/$script_name"
  else
    _fail "subskills/project-shape/scripts/$script_name"
  fi
done

# ── 3. Fixture structural checks ──────────────────────────────────────────────
section "Fixture structural checks"

# ── 3a. project-direction fixtures ────────────────────────────────────────────
echo ""
echo "  -- project-direction/tests/fixtures/ --"

DIRECTION_FIXTURES="$ROOT/subskills/project-direction/tests/fixtures"

shopt -s nullglob
direction_dirs=("$DIRECTION_FIXTURES"/ambiguous-spec-drift/*/)
shopt -u nullglob

if [[ ${#direction_dirs[@]} -eq 0 ]]; then
  _fail "no fixtures found under subskills/project-direction/tests/fixtures/ambiguous-spec-drift/"
else
  all_routes=""
  for fixture_dir in "${direction_dirs[@]}"; do
    fixture="$fixture_dir/FIXTURE.md"
    name="$(basename "$fixture_dir")"
    if require_file "$fixture" "project-direction/$name/FIXTURE.md exists"; then
      check_pattern "$fixture" '^## Expected Outcome' \
        "project-direction/$name: declares ## Expected Outcome"
      check_pattern "$fixture" '^\*\*Routing\*\*:' \
        "project-direction/$name: declares **Routing**:"
      all_routes+="$(grep '^\*\*Routing\*\*:' "$fixture" 2>/dev/null || true)"$'\n'
    fi
  done

  # Routing variety: fixtures must cover both project-review and project-direction
  # (the "does code match spec?" case routes to review; "act on confirmed drift"
  # routes to direction — both must be present)
  if echo "$all_routes" | grep -q 'project-review'; then
    _pass "project-direction: fixtures include a project-review routing case"
  else
    _fail "project-direction: fixtures must include a case routing to project-review"
  fi
  if echo "$all_routes" | grep -q 'project-direction'; then
    _pass "project-direction: fixtures include a project-direction routing case"
  else
    _fail "project-direction: fixtures must include a case routing to project-direction"
  fi
fi

# ── 3b. project-feature-request fixtures ──────────────────────────────────────
echo ""
echo "  -- project-feature-request/tests/fixtures/ --"

FEATURE_FIXTURES="$ROOT/subskills/project-feature-request/tests/fixtures"

shopt -s nullglob
feature_dirs=("$FEATURE_FIXTURES"/funnel-decisions/*/)
shopt -u nullglob

if [[ ${#feature_dirs[@]} -eq 0 ]]; then
  _fail "no fixtures found under subskills/project-feature-request/tests/fixtures/funnel-decisions/"
else
  all_decisions=""
  for fixture_dir in "${feature_dirs[@]}"; do
    fixture="$fixture_dir/FIXTURE.md"
    name="$(basename "$fixture_dir")"
    if require_file "$fixture" "project-feature-request/$name/FIXTURE.md exists"; then
      check_pattern "$fixture" '^## Expected Outcome' \
        "project-feature-request/$name: declares ## Expected Outcome"
      check_pattern "$fixture" '^\*\*Decision\*\*:' \
        "project-feature-request/$name: declares **Decision**:"
      check_pattern "$fixture" '^## Key Assertions' \
        "project-feature-request/$name: has ## Key Assertions"
      all_decisions+="$(grep '^\*\*Decision\*\*:' "$fixture" 2>/dev/null || true)"$'\n'
    fi
  done

  # Decision variety: must include Reject and at least one non-rejection outcome
  if echo "$all_decisions" | grep -qi 'Reject'; then
    _pass "project-feature-request: fixtures include at least one Reject decision"
  else
    _fail "project-feature-request: fixtures must include at least one Reject decision"
  fi
  if echo "$all_decisions" | grep -qiE 'Approved|Park|Not specifiable'; then
    _pass "project-feature-request: fixtures include non-rejection outcomes (Approved/Park/Not specifiable)"
  else
    _fail "project-feature-request: fixtures must include non-rejection outcomes"
  fi
fi

# ── 3c. project-review fixtures — overclaim gate check ───────────────────────
echo ""
echo "  -- project-review/tests/fixtures/ (overclaim gate) --"

REVIEW_FIXTURE="$ROOT/subskills/project-review/tests/fixtures/third-party-overclaims"

require_file "$REVIEW_FIXTURE/README.md" \
  "project-review/third-party-overclaims/README.md exists"

# The README must document the failure classes the fixture covers (calibration ref)
if [[ -f "$REVIEW_FIXTURE/README.md" ]]; then
  check_pattern "$REVIEW_FIXTURE/README.md" \
    '^## Failure classes' \
    "project-review: README documents failure classes"
fi

require_file "$REVIEW_FIXTURE/input-review.md" \
  "project-review/third-party-overclaims/input-review.md exists"

# The input review must contain P0 claims — otherwise the gate has nothing to catch
if [[ -f "$REVIEW_FIXTURE/input-review.md" ]]; then
  check_pattern "$REVIEW_FIXTURE/input-review.md" \
    'P0' \
    "project-review: input-review.md contains P0 severity claims to gate"
fi

if require_file "$REVIEW_FIXTURE/expected-gate-output.md" \
    "project-review/third-party-overclaims/expected-gate-output.md exists"; then

  GATE_OUT="$REVIEW_FIXTURE/expected-gate-output.md"

  # The gate output must contain a Veracity Ledger — the gate's primary artifact
  # for recording overclaimed/incorrect/unverifiable findings
  check_pattern "$GATE_OUT" \
    '^## Veracity Ledger' \
    "project-review: expected-gate-output.md has ## Veracity Ledger section"

  # Overclaim check (primary): P0 claims in the input must appear in the
  # Veracity Ledger as [Incorrect] or [Unverifiable] — not pass through as
  # planning inputs. This catches the class of failure where an unverified
  # reviewer invents P0 issues (e.g. nonexistent paths, routing conflicts that
  # are explicitly disambiguated, formatting claims from browser rendering).
  check_pattern "$GATE_OUT" \
    'P0.*\[Incorrect\]|P0.*\[Unverifiable\]' \
    "project-review: overclaim check — P0 claims appear in Veracity Ledger as [Incorrect]/[Unverifiable]"

  # Overclaim check (secondary): the Revised Risk Register must not contain
  # original P0 findings. After the gate, demoted/rejected P0s must be absent.
  # Extract the Revised Risk Register section and look for P0 or Critical severity.
  revised_section=$(awk '
    /^## Revised Risk Register/ { p=1; next }
    p && /^## [^#]/              { exit }
    p                            { print }
  ' "$GATE_OUT")
  if echo "$revised_section" | grep -qE '^\|[^|]+\|[^|]+\|\s*(P0|C|Critical)\s*\|'; then
    _fail "project-review: overclaim check — P0/Critical severity survived the gate in Revised Risk Register"
  else
    _pass "project-review: overclaim check — no P0/Critical rows survived into Revised Risk Register"
  fi
fi

# ── Summary ───────────────────────────────────────────────────────────────────
echo ""
echo "=================================================="
total=$((pass_count + fail_count))
echo "Results: $pass_count/$total checks passed"
if [[ $fail_count -gt 0 ]]; then
  echo "FAIL: $fail_count check(s) failed"
  exit 1
fi
echo "PASS: all $pass_count checks passed"
