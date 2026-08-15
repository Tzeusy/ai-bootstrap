#!/usr/bin/env bash

# This contract test protects the narrow hosted-evidence route for the
# documentation-only telemetry project.
# This creates visible, exact-head, informational evidence for accidental
# regressions in telemetry changes only. Because the workflow and its in-tree
# contract can change together, they do not constitute an independently protected
# or adversarial no-write/no-network enforcement control.
# It does not configure or imply required branch policy.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORKFLOW="$ROOT/.github/workflows/ai-usage-telemetry-pr-checks.yml"
MUTATION_ROOT="$(mktemp -d "${TMPDIR:-/tmp}/ai-usage-telemetry-pr-checks-test.XXXXXX")"

cleanup() {
    local status=$?

    rm -rf -- "$MUTATION_ROOT"
    exit "$status"
}
trap cleanup EXIT

fail() {
    printf 'FAIL: %s\n' "$*" >&2
    exit 1
}

assert_claim_scope() {
    local file="$1"

    grep -Fqx '# This creates visible, exact-head, informational evidence for accidental' "$file" \
        || fail "limited workflow claim is missing: $file"
    grep -Fqx '# regressions in telemetry changes only. Because the workflow and its in-tree' "$file" \
        || fail "accidental-regression scope is missing: $file"
    grep -Fqx '# contract can change together, they do not constitute an independently protected' "$file" \
        || fail "co-mutable oracle limitation is missing: $file"
    grep -Fqx '# or adversarial no-write/no-network enforcement control.' "$file" \
        || fail "adversarial-enforcement limitation is missing: $file"
}

assert_claim_scope "$WORKFLOW"
assert_claim_scope "${BASH_SOURCE[0]}"

# The runner has Bash but does not provision a YAML parser as part of this
# workflow. Its fixed security surface is therefore bound to this complete,
# fail-closed schema: any YAML spelling, permission, action, or run-step drift
# fails before CI can execute it.
canonical_workflow() {
    cat <<'EOF'
name: AI Usage Telemetry checks

on:
  pull_request:
    branches: [main]
    paths:
      - ".github/workflows/ai-usage-telemetry-pr-checks.yml"
      - "projects/ai-usage-telemetry/**"
      - "tests/ai-usage-telemetry-pr-checks-test.sh"
  workflow_dispatch:

# This creates visible, exact-head, informational evidence for accidental
# regressions in telemetry changes only. Because the workflow and its in-tree
# contract can change together, they do not constitute an independently protected
# or adversarial no-write/no-network enforcement control.
# It does not configure or imply required branch policy.
permissions:
  contents: read

jobs:
  telemetry-validation:
    name: telemetry-validation
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: projects/ai-usage-telemetry
    steps:
      - uses: actions/checkout@v4
        with:
          persist-credentials: false

      - uses: actions/setup-node@v4
        with:
          node-version: 22

      - uses: astral-sh/setup-uv@v5
        with:
          enable-cache: false

      - name: Install OpenSpec
        run: npm install --global @fission-ai/openspec@1.3.1

      - name: Run workflow contract test
        run: bash ../../tests/ai-usage-telemetry-pr-checks-test.sh

      - name: Validate OpenSpec
        run: openspec validate --all --strict

      - name: Validate authoring traceability
        run: uv run ../../skills/personal/th-projects/scripts/spec-trace-check.py . --authoring

      - name: Scan project shape
        run: bash ../../skills/personal/th-projects/subskills/project-shape/scripts/shape-scan.sh .

      - name: Run scoped telemetry tests
        shell: bash
        run: |
          test_dirs=(
            tests/spec
            about/legends-and-lore/evidence/tests
            about/legends-and-lore/evidence/0003/tests
          )
          found_test_dir=0

          for test_dir in "${test_dirs[@]}"; do
            if [[ -d "$test_dir" ]]; then
              found_test_dir=1
              pytest_args=(uv run --with pytest pytest -q "$test_dir")
              if [[ "$test_dir" == "about/legends-and-lore/evidence/0003/tests" &&
                    -f "$test_dir/test_inner_probe_0003.py" ]]; then
                pytest_args+=(
                  --deselect=about/legends-and-lore/evidence/0003/tests/test_inner_probe_0003.py::InnerProbeTests::test_loopback_mock_positive_control_accepts_without_reading_request_values
                )
              fi
              "${pytest_args[@]}"
            else
              echo "NOTICE: no scoped telemetry test directory at $test_dir"
            fi
          done

          if [[ "$found_test_dir" -eq 0 ]]; then
            echo "NOTICE: no listed telemetry test directories are present"
          fi
EOF
}

validate_workflow() {
    local file="$1"

    [[ -f "$file" ]] || return 1
    cmp -s <(canonical_workflow) "$file"
}

mutate_and_reject() {
    local label="$1"
    local mutation="$2"
    local mutated="$MUTATION_ROOT/${label//[^A-Za-z0-9_.-]/_}.yml"

    sed -e "$mutation" "$WORKFLOW" > "$mutated"
    if validate_workflow "$mutated"; then
        fail "semantic mutation was accepted: $label"
    fi
    printf 'PASS: rejects mutation: %s\n' "$label"
}

validate_workflow "$WORKFLOW" || fail "workflow contract is missing or invalid"
printf 'PASS: base workflow contract\n'

mutate_and_reject \
    'missing-telemetry-path' \
    's#      - "projects/ai-usage-telemetry/\*\*"#      - "projects/unrelated/**"#'
mutate_and_reject \
    'missing-read-only-permission' \
    's/^  contents: read$/  contents: write/'
mutate_and_reject \
    'wrong-openspec-pin' \
    's/@fission-ai\/openspec@1\.3\.1/@fission-ai\/openspec@1.3.0/'
mutate_and_reject \
    'missing-required-validation' \
    '/openspec validate --all --strict/d'
mutate_and_reject \
    'missing-workflow-contract-execution' \
    '/^        run: bash \.\.\/\.\.\/tests\/ai-usage-telemetry-pr-checks-test\.sh$/d'
mutate_and_reject \
    'skipped-workflow-contract-execution' \
    '/^      - name: Run workflow contract test$/a\        if: false'
mutate_and_reject \
    'missing-loopback-deselection' \
    '/--deselect=about\/legends-and-lore\/evidence\/0003\/tests\/test_inner_probe_0003\.py::InnerProbeTests::test_loopback_mock_positive_control_accepts_without_reading_request_values/d'

mutate_and_reject \
    'job-write-permission' \
    '/^  telemetry-validation:$/a\    permissions:\n      actions: write'
mutate_and_reject \
    'job-write-all-permission' \
    '/^  telemetry-validation:$/a\    permissions: write-all'
mutate_and_reject \
    'job-contents-write-permission' \
    '/^  telemetry-validation:$/a\    permissions:\n      contents: write'
mutate_and_reject \
    'job-flow-write-permission' \
    '/^  telemetry-validation:$/a\    permissions: { contents: write }'
mutate_and_reject \
    'workflow-write-all-permission' \
    '/^permissions:$/,/^jobs:$/c\permissions: write-all\n\njobs:'
mutate_and_reject \
    'workflow-flow-write-permission' \
    '/^permissions:$/,/^jobs:$/c\permissions: { contents: write }\n\njobs:'
mutate_and_reject \
    'enabled-setup-uv-cache' \
    '/^      - uses: astral-sh\/setup-uv@v5$/a\        with:\n          enable-cache: true'
mutate_and_reject \
    'persisted-checkout-credentials' \
    '/^      - uses: actions\/checkout@v4$/a\        with:\n          persist-credentials: true'
mutate_and_reject \
    'duplicate-checkout-action' \
    '/^          persist-credentials: false$/a\      - uses: actions/checkout@v4\n        with:\n          persist-credentials: false'
mutate_and_reject \
    'duplicate-checkout-action-quoted-true' \
    '/^          persist-credentials: false$/a\      - uses: actions/checkout@v4\n        with:\n          persist-credentials: "true"'
mutate_and_reject \
    'duplicate-setup-uv-action' \
    '/^          enable-cache: false$/a\      - uses: astral-sh/setup-uv@v5\n        with:\n          enable-cache: false'
mutate_and_reject \
    'duplicate-setup-uv-action-quoted-true' \
    '/^          enable-cache: false$/a\      - uses: astral-sh/setup-uv@v5\n        with:\n          enable-cache: "true"'
mutate_and_reject \
    'unsafe-github-expression' \
    '/^      - name: Install OpenSpec$/a\        run: echo "${{ github.sha }}"'
mutate_and_reject \
    'outbound-network-code' \
    '/^      - name: Install OpenSpec$/a\        run: python -c '\''import socket; socket.create_connection(("example.com", 443))'\'''
mutate_and_reject \
    'spaced-job-write-all-permission' \
    '/^  telemetry-validation:$/a\    permissions : write-all'
mutate_and_reject \
    'unexpected-network-capable-run-step' \
    '/^        run: npm install --global @fission-ai\/openspec@1\.3\.1$/a\      - name: Unexpected network-capable run\n        run: bash -c "exec 3<>/dev/tcp/198.51.100.1/443"'

printf 'PASS: AI Usage Telemetry PR workflow contract\n'
