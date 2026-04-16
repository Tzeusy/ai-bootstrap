#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
FIXTURES_DIR="${SKILL_DIR}/assets/fixtures"

TMP_DIR="$(mktemp -d)"
cleanup() {
  rm -rf "${TMP_DIR}"
}
trap cleanup EXIT

cp -R "${FIXTURES_DIR}/base/." "${TMP_DIR}/"

python "${SKILL_DIR}/scripts/ai_prompt_standardizer.py" \
  --base "${TMP_DIR}/ai-bootstrap" \
  --only all

diff -ru "${FIXTURES_DIR}/expected" "${TMP_DIR}"

echo "OK: fixtures match expected output"
