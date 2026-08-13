#!/usr/bin/env bash

# This contract test protects the narrow hosted-evidence route for the
# documentation-only telemetry project. It creates visible PR evidence only;
# it does not configure or imply required branch policy.
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

require_line() {
    local file="$1"
    local expected="$2"

    grep -Fqx -- "$expected" "$file" || return 1
}

validate_workflow() {
    local file="$1"
    local checkout_block
    local paths_block
    local permissions_block
    local setup_uv_block
    local expected_paths

    [[ -f "$file" ]] || return 1

    require_line "$file" 'name: AI Usage Telemetry checks' || return 1
    require_line "$file" '  pull_request:' || return 1
    require_line "$file" '    branches: [main]' || return 1
    require_line "$file" '  workflow_dispatch:' || return 1
    ! grep -Eq '^  (push|pull_request_target):' "$file" || return 1

    paths_block="$(awk '
        /^    paths:$/ { capture = 1; next }
        capture && /^      - / { print; next }
        capture { capture = 0 }
    ' "$file")"
    expected_paths=$'      - ".github/workflows/ai-usage-telemetry-pr-checks.yml"\n      - "projects/ai-usage-telemetry/**"\n      - "tests/ai-usage-telemetry-pr-checks-test.sh"'
    [[ "$paths_block" == "$expected_paths" ]] || return 1

    permissions_block="$(awk '
        /^permissions:$/ { capture = 1; next }
        capture && /^  [A-Za-z_][A-Za-z_-]*:/ { print; next }
        capture { capture = 0 }
    ' "$file")"
    [[ "$permissions_block" == '  contents: read' ]] || return 1
    # Keep one top-level permission map. A job-level declaration is denied
    # regardless of whether it uses scalar, flow-map, or block-map syntax.
    [[ "$(grep -Ec '^[[:space:]]*permissions:' "$file")" -eq 1 ]] || return 1
    # Reject write-bearing values within any workflow/job permission map,
    # including scalar write-all and inline mapping forms.
    if awk '
        function leading_spaces(text, prefix) {
            prefix = text
            sub(/[^ ]+.*/, "", prefix)
            return length(prefix)
        }
        {
            if ($0 ~ /^[[:space:]]*permissions:[[:space:]]*/) {
                value = $0
                sub(/^[[:space:]]*permissions:[[:space:]]*/, "", value)
                if (value ~ /(^|[^[:alnum:]_-])write(-all)?([^[:alnum:]_-]|$)/) {
                    found = 1
                }
                permissions_indent = leading_spaces($0)
                in_permissions = 1
                next
            }
            if (!in_permissions) {
                next
            }
            current_indent = leading_spaces($0)
            if ($0 !~ /^[[:space:]]*(#|$)/ && current_indent <= permissions_indent) {
                in_permissions = 0
                next
            }
            if (current_indent > permissions_indent &&
                $0 ~ /^[[:space:]]*[A-Za-z_][A-Za-z0-9_-]*[[:space:]]*:[[:space:]]*[^#]*write(-all)?([^A-Za-z0-9_-]|$)/) {
                found = 1
            }
        }
        END { exit found ? 0 : 1 }
    ' "$file"; then
        return 1
    fi

    checkout_block="$(awk '
        /^      - uses: actions\/checkout@v4$/ { capture = 1; print; next }
        capture && /^      - / { capture = 0 }
        capture { print }
    ' "$file")"
    [[ "$checkout_block" == *$'        with:\n          persist-credentials: false'* ]] || return 1
    ! grep -Eq '^[[:space:]]+persist-credentials:[[:space:]]*true[[:space:]]*$' "$file" || return 1

    setup_uv_block="$(awk '
        /^      - uses: astral-sh\/setup-uv@v5$/ { capture = 1; print; next }
        capture && /^      - / { capture = 0 }
        capture { print }
    ' "$file")"
    [[ "$setup_uv_block" == *$'        with:\n          enable-cache: false'* ]] || return 1
    ! grep -Eq '^[[:space:]]+enable-cache:[[:space:]]*true[[:space:]]*$' "$file" || return 1

    require_line "$file" '      - uses: actions/checkout@v4' || return 1
    require_line "$file" '      - uses: actions/setup-node@v4' || return 1
    require_line "$file" '          node-version: 22' || return 1
    require_line "$file" '      - uses: astral-sh/setup-uv@v5' || return 1
    require_line "$file" '        run: npm install --global @fission-ai/openspec@1.3.1' || return 1
    require_line "$file" '        run: openspec validate --all --strict' || return 1
    require_line "$file" '        run: uv run ../../skills/personal/th-projects/scripts/spec-trace-check.py . --authoring' || return 1
    require_line "$file" '        run: bash ../../skills/personal/th-projects/subskills/project-shape/scripts/shape-scan.sh .' || return 1
    require_line "$file" '        working-directory: projects/ai-usage-telemetry' || return 1

    require_line "$file" '                  --deselect=about/legends-and-lore/evidence/0003/tests/test_inner_probe_0003.py::InnerProbeTests::test_loopback_mock_positive_control_accepts_without_reading_request_values' || return 1
    grep -Fq -- 'tests/spec' "$file" || return 1
    grep -Fq -- 'about/legends-and-lore/evidence/tests' "$file" || return 1
    grep -Fq -- 'about/legends-and-lore/evidence/0003/tests' "$file" || return 1
    grep -Fq -- 'NOTICE: no listed telemetry test directories are present' "$file" || return 1

    ! grep -Fq '${{' "$file" || return 1
    ! grep -Eiq '(^|[^A-Za-z0-9_])(curl|wget|nc|netcat|socat|telnet|ftp|ssh|scp|rsync|dig|nslookup|host)([^A-Za-z0-9_]|$)|(^|[^A-Za-z0-9_])(socket|urllib|requests|http\.client|fetch|axios|dns)([^A-Za-z0-9_]|$)|https?://|127\.0\.0\.1|localhost' "$file" || return 1
    ! grep -Eiq 'pull_request_target|actions/cache|secrets\.|(^|[^A-Za-z])(claude|codex)([^A-Za-z]|$)|\.claude|\.codex|(^|[[:space:]])sink' "$file" || return 1
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
    'unsafe-github-expression' \
    '/^      - name: Install OpenSpec$/a\        run: echo "${{ github.sha }}"'
mutate_and_reject \
    'outbound-network-code' \
    '/^      - name: Install OpenSpec$/a\        run: python -c '\''import socket; socket.create_connection(("example.com", 443))'\'''

printf 'PASS: AI Usage Telemetry PR workflow contract\n'
