#!/usr/bin/env bash
# Opt-in user installation; never pair, copy credentials, or launch an agent.
set -euo pipefail
if [ "$#" -ne 1 ] || [ "$1" = --help ]; then
    echo 'Usage: install-tze-hud.sh <tze-hud-main-checkout>' >&2
    exit 2
fi
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
hud_repo="$(cd "$1" && pwd -P)"
[[ "$hud_repo" != *$'\n'* ]] || { echo 'HUD path must fit on one line.' >&2; exit 2; }
export TZE_HUD_REPO="$hud_repo"
# The generated catalogs must be the ones the user's installed clients read.
for tool in claude codex gemini; do
    command -v "$tool" >/dev/null 2>&1 || continue
    if [ ! -d "$HOME/.$tool" ] ||
       [ "$(cd "$HOME/.$tool" && pwd -P)" != "$root/.$tool" ]; then
        echo "Link the $tool home to this ai-bootstrap checkout before installing HUD skills." >&2
        exit 1
    fi
done
# Validate source selection before changing client configuration or catalogs.
"$root/scripts/link-ai-skills.sh" --catalog-manifest "$root" >/dev/null
"$root/scripts/link-ai-skills.sh" "$root"
"$root/scripts/sync-mcp.sh" --stdio tze-hud python3 -u \
    "$hud_repo/.claude/skills/user-test/scripts/hud_mcp_stdio.py"
selection="$(mktemp "$root/.tze-hud-repo.XXXXXX")"
trap 'rm -f -- "$selection"' EXIT
printf '%s\n' "$hud_repo" > "$selection"
mv -f -- "$selection" "$root/.tze-hud-repo"
echo 'HUD user installation configured. Existing MCP entries were retained.'
echo 'Restart the client outside tze-hud and verify fresh authenticated discovery of the five HUD tools.'
