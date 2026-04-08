#!/usr/bin/env bash
# eval-fallbacks.sh — Validate constrained-environment guidance remains explicit and consistent.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

SKILL_FILE="$ROOT_DIR/SKILL.md"
REVIEW_PROTOCOL="$ROOT_DIR/references/review-protocol.md"
OVERVIEW_GUIDE="$ROOT_DIR/references/generate-overview.md"
BOOTSTRAP_GUIDE="$ROOT_DIR/references/consultative-bootstrapping.md"
EVAL_SCENARIOS="$ROOT_DIR/references/evaluation-scenarios.md"

pass_count=0

fail() {
  echo "FAIL: $1" >&2
  exit 1
}

require_pattern() {
  local file="$1" pattern="$2" label="$3"
  if ! grep -Eq "$pattern" "$file"; then
    fail "$label ($file)"
  fi
  pass_count=$((pass_count + 1))
}

require_pattern "$SKILL_FILE" 'Lite mode' "main skill documents lite mode"
require_pattern "$SKILL_FILE" 'No-diagram mode' "main skill documents no-diagram mode"
require_pattern "$REVIEW_PROTOCOL" 'Fallback When Subagents Are Unavailable' "review protocol documents subagent fallback"
require_pattern "$REVIEW_PROTOCOL" 'coherence pass|adversarial pass|user for validation' "review protocol describes explicit lite review steps"
require_pattern "$OVERVIEW_GUIDE" 'Mermaid|prose fallback|skip diagrams' "overview guide documents diagram fallback"
require_pattern "$BOOTSTRAP_GUIDE" 'Mid-Tier Model Guidance' "bootstrapping guide documents mid-tier guidance"
require_pattern "$BOOTSTRAP_GUIDE" 'user validation checkpoints|conservative wording' "bootstrapping guide explains mid-tier tradeoffs"
require_pattern "$EVAL_SCENARIOS" 'Constrained environment: no subagents' "evaluation scenarios include no-subagent case"
require_pattern "$EVAL_SCENARIOS" 'Constrained environment: no Excalidraw' "evaluation scenarios include no-diagram case"
require_pattern "$EVAL_SCENARIOS" 'Mid-tier model' "evaluation scenarios include mid-tier case"

echo "PASS: $pass_count fallback guidance checks"
