#!/usr/bin/env bash
# Harness doctor: run every snapshot flow's VERIFY check as one pass/fail
# report, refreshing nothing. Checks mirror references/snapshot-flows.md —
# keep the two in sync when adding a flow.
#
# Usage: ./harness_doctor.sh        # exit 0 = all pass, 1 = failures
set -uo pipefail

DOTFILES_DIR="${DOTFILES_DIR:-$HOME/.dotfiles}"
AI_BOOTSTRAP_DIR="$DOTFILES_DIR/ai-bootstrap"
fails=0

check() { # name, command...
    local name=$1; shift
    if "$@" >/dev/null 2>&1; then
        echo "PASS  $name"
    else
        echo "FAIL  $name   ($*)"
        fails=$((fails + 1))
    fi
}

# Flow 1: skill symlinks — no broken links in any tool home
broken=$(find "$AI_BOOTSTRAP_DIR/.codex/skills" "$AI_BOOTSTRAP_DIR/.gemini/skills" \
              "$AI_BOOTSTRAP_DIR/.gemini/antigravity/skills" "$AI_BOOTSTRAP_DIR/.claude/skills" \
              -maxdepth 1 -xtype l 2>/dev/null | wc -l)
if [ "$broken" -eq 0 ]; then echo "PASS  skill symlinks (no broken links)"; else
    echo "FAIL  skill symlinks ($broken broken links — re-run bootstrap.sh skills section)"; fails=$((fails+1)); fi

# Flow 2: submodules — no missing (-) or pointer-drifted (+) entries
for repo in "$DOTFILES_DIR" "$AI_BOOTSTRAP_DIR"; do
    drift=$(git -C "$repo" submodule status --recursive 2>/dev/null | grep -c '^[+-]')
    if [ "$drift" -eq 0 ]; then echo "PASS  submodules in $(basename "$repo")"; else
        echo "WARN  submodules in $(basename "$repo") ($drift drifted/missing — may be intentional mid-work)"; fi
done

# Flow 3: shell loads cleanly
check "zsh loads cleanly" zsh -ic exit

# Flow 5: beads health (per repo; bd may be absent on some machines)
if command -v bd >/dev/null 2>&1; then
    check "bd doctor (dotfiles)" bd -C "$DOTFILES_DIR" doctor
else
    echo "SKIP  bd doctor (bd not installed)"
fi

# Required harness binaries
for bin in uv rg gh jq git; do
    check "binary: $bin" command -v "$bin"
done

echo
if [ "$fails" -eq 0 ]; then echo "harness doctor: all checks passed"; else
    echo "harness doctor: $fails check(s) FAILED"; fi
exit "$((fails > 0))"
