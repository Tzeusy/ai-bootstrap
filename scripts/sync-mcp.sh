#!/usr/bin/env bash

# Idempotently register the MCP servers listed in mcp-servers.tsv with each
# installed agent CLI (claude, codex, gemini). Existing entries are left alone.
# Add a new agent (e.g. pi) by writing one add_<tool> function and listing it
# in the loop at the bottom. Logins are manual on first use.

set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
manifest="${1:-$root/mcp-servers.tsv}"

add_claude() { # name url
    claude mcp get "$1" >/dev/null 2>&1 && return 1
    claude mcp add --scope user --transport http "$1" "$2" >/dev/null
}

add_codex() {
    codex mcp get "$1" >/dev/null 2>&1 && return 1
    codex mcp add "$1" --url "$2" >/dev/null
}

add_gemini() {
    local f="$HOME/.gemini/settings.json" tmp
    [ -f "$f" ] || echo '{}' >"$f"
    jq -e --arg n "$1" '.mcpServers[$n]' "$f" >/dev/null 2>&1 && return 1
    tmp="$(mktemp)"
    jq --arg n "$1" --arg u "$2" '.mcpServers[$n] = {httpUrl: $u}' "$f" >"$tmp"
    mv "$tmp" "$f"
}

while IFS=$'\t' read -r name url; do
    case "$name" in ''|'#'*) continue ;; esac
    for tool in claude codex gemini; do
        command -v "$tool" >/dev/null 2>&1 || continue
        if "add_$tool" "$name" "$url"; then
            printf 'added   %-7s %s\n' "$tool" "$name"
        else
            printf 'present %-7s %s\n' "$tool" "$name"
        fi
    done
done <"$manifest"
