#!/usr/bin/env bash
# One repository gate delegates to the canonical package behavior suites.
# Spec: REQ-progress-dashboard-001 REQ-progress-dashboard-002
# Spec: REQ-progress-dashboard-003 REQ-progress-dashboard-004
# Spec: REQ-progress-dashboard-005 REQ-progress-dashboard-006
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
PACKAGE="$ROOT/skills/personal/th-projects/subskills/progress-dashboard"
uv run "$PACKAGE/tests/test_progress_dashboard.py" -q
uv run "$PACKAGE/tests/test_loop_telemetry.py" -q
node --check "$PACKAGE/assets/web/app.js"
