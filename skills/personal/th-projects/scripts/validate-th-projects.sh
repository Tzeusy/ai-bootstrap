#!/usr/bin/env bash
# validate-th-projects.sh — Package-level validator for skills/personal/th-projects.
#
# Runs from any working directory; resolves all paths from BASH_SOURCE.
# Checks: shell syntax, project-shape self-tests, fixture structural invariants,
# governance contracts, and spec-trace behavior.
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
  if grep -q 'project-review' <<<"$all_routes"; then
    _pass "project-direction: fixtures include a project-review routing case"
  else
    _fail "project-direction: fixtures must include a case routing to project-review"
  fi
  if grep -q 'project-direction' <<<"$all_routes"; then
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
  if grep -qi 'Reject' <<<"$all_decisions"; then
    _pass "project-feature-request: fixtures include at least one Reject decision"
  else
    _fail "project-feature-request: fixtures must include at least one Reject decision"
  fi
  if grep -qiE 'Approved|Park|Not specifiable' <<<"$all_decisions"; then
    _pass "project-feature-request: fixtures include non-rejection outcomes (Approved/Park/Not specifiable)"
  else
    _fail "project-feature-request: fixtures must include non-rejection outcomes"
  fi
  if grep -Rqi 'subagent per gate' "$FEATURE_FIXTURES"; then
    _fail "project-feature-request: fixtures retain the retired subagent-per-gate allocation"
  else
    _pass "project-feature-request: fixtures use one funnel owner with conditional specialists"
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

# ── 4. spec-trace-check fixtures ─────────────────────────────────────────────
section "Governance contract checks"

ROUTER="$ROOT/SKILL.md"
SPEC_FORMAT="$ROOT/references/spec-format.md"
WORK_ALLOCATION="$ROOT/references/work-allocation.md"
FEATURE_SKILL="$ROOT/subskills/project-feature-request/SKILL.md"
DIRECTION_SKILL="$ROOT/subskills/project-direction/SKILL.md"
RECONCILIATION="$ROOT/subskills/project-review/references/spec-reconciliation.md"

check_pattern "$ROUTER" 'VISION.*continuous constraint' \
  "router: VISION is an always-on constraint"
check_pattern "$ROUTER" 'Gap|TODO|adjacent idea' \
  "router: proactive discovery capture is explicit"
check_pattern "$SPEC_FORMAT" '^## Semantic Quality Gate' \
  "spec format: semantic clarity/completeness gate exists"
check_pattern "$SPEC_FORMAT" 'normative SHALL/MUST paragraph.*contiguous.*ID.*Source.*Scope.*scenarios' \
  "spec format: canonical requirement ordering is explicit"
check_pattern "$FEATURE_SKILL" '/th-design' \
  "feature request: user-surface specs route to th-design"
if require_file "$WORK_ALLOCATION" \
    "references/work-allocation.md exists"; then
  check_pattern "$WORK_ALLOCATION" 'one bead.*cohesive.*independently verifiable outcome' \
    "work allocation: one cohesive outcome per bead"
  check_pattern "$WORK_ALLOCATION" 'overhead|amortiz' \
    "work allocation: agent overhead affects granularity"
fi
check_pattern "$DIRECTION_SKILL" 'references/work-allocation.md' \
  "project-direction: allocation contract is progressively discoverable"
check_pattern "$RECONCILIATION" 'work-allocation.md' \
  "spec reconciliation: gaps use the shared allocation contract"

# ── 5. spec-trace-check fixtures ─────────────────────────────────────────
section "spec-trace-check fixtures"

TRACE_SCRIPT="$ROOT/scripts/spec-trace-check.py"
TRACE_FIXTURES="$ROOT/tests/fixtures/spec-trace"

if [[ ! -f "$TRACE_SCRIPT" ]]; then
  _fail "script missing: scripts/spec-trace-check.py"
else
  rc=0
  out=$(uv run "$TRACE_SCRIPT" "$TRACE_FIXTURES/clean" 2>&1) || rc=$?
  if [[ $rc -eq 0 ]]; then
    _pass "spec-trace: clean fixture passes (exit 0)"
  else
    _fail "spec-trace: clean fixture failed (exit $rc): $out"
  fi

  rc=0
  out=$(uv run "$TRACE_SCRIPT" "$TRACE_FIXTURES/clean" --authoring 2>&1) || rc=$?
  if [[ $rc -eq 0 ]]; then
    _pass "spec-trace: clean authoring fixture passes (exit 0)"
  else
    _fail "spec-trace: clean authoring fixture failed (exit $rc): $out"
  fi

  rc=0
  out=$(uv run "$TRACE_SCRIPT" "$TRACE_FIXTURES/ordering-violations" 2>&1) || rc=$?
  if [[ $rc -ne 1 ]]; then
    _fail "spec-trace: ordering violations fixture expected exit 1, got $rc"
  else
    _pass "spec-trace: ordering violations fixture fails (exit 1)"
    for expected in "normative SHALL/MUST paragraph before ID/Source/Scope" \
                    "contiguous ID, Source, Scope after its normative paragraph" \
                    "place ID, Source, Scope before its first scenario" \
                    "place scenarios immediately after ID, Source, Scope"; do
      if grep -q "$expected" <<<"$out"; then
        _pass "spec-trace: ordering violations output reports '$expected'"
      else
        _fail "spec-trace: ordering violations output missing expected finding '$expected'"
      fi
    done
    if grep -q "requirement 'Metadata First With Missing Scope' must place a normative SHALL/MUST paragraph" <<<"$out"; then
      _pass "spec-trace: missing fields do not suppress ordering errors"
    else
      _fail "spec-trace: missing field suppressed a metadata-first ordering error: $out"
    fi
  fi

  rc=0
  out=$(uv run "$TRACE_SCRIPT" "$TRACE_FIXTURES/empty-authoring" --authoring 2>&1) || rc=$?
  if [[ $rc -eq 1 ]] && grep -q 'spec file has no requirements' <<<"$out"; then
    _pass "spec-trace: authoring mode rejects an empty delta beside a valid spec"
  else
    _fail "spec-trace: authoring mode must reject an empty delta beside a valid spec (exit $rc): $out"
  fi

  rc=0
  out=$(uv run "$TRACE_SCRIPT" "$TRACE_FIXTURES/clean" --strict --tests-dir missing 2>&1) || rc=$?
  if [[ $rc -eq 1 ]] && grep -q 'strict mode cannot verify test citation' <<<"$out"; then
    _pass "spec-trace: strict mode rejects missing test discovery"
  else
    _fail "spec-trace: strict mode must reject missing test discovery (exit $rc): $out"
  fi

  rc=0
  out=$(uv run "$TRACE_SCRIPT" "$TRACE_FIXTURES/added-reuses-id" --authoring 2>&1) || rc=$?
  if [[ $rc -eq 1 ]] && grep -q "duplicate ID 'REQ-core-auth-001'" <<<"$out"; then
    _pass "spec-trace: ADDED requirements cannot reuse main-spec IDs"
  else
    _fail "spec-trace: ADDED requirement reused a main-spec ID (exit $rc): $out"
  fi

  rc=0
  out=$(uv run "$TRACE_SCRIPT" "$TRACE_FIXTURES/violations" 2>&1) || rc=$?
  if [[ $rc -ne 1 ]]; then
    _fail "spec-trace: violations fixture expected exit 1, got $rc"
  else
    _pass "spec-trace: violations fixture fails (exit 1)"
    for expected in "delta heading" "unsupported main-spec H2" "has no scenarios" "duplicate ID" \
                    "names spec" "stale test citation" "1 WHEN and 1 THEN"; do
      if grep -q "$expected" <<<"$out"; then
        _pass "spec-trace: violations output reports '$expected'"
      else
        _fail "spec-trace: violations output missing expected finding '$expected'"
      fi
    done
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
