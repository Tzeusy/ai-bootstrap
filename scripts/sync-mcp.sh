#!/usr/bin/env bash

# Register missing user-scope MCP entries with installed agent CLIs.
# Existing entries stay untouched; authentication remains local/manual.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
transport=http
if [ "${1-}" = --stdio ]; then
    [ "$#" -ge 3 ] || { echo 'Usage: sync-mcp.sh --stdio <name> <command> [args...]' >&2; exit 2; }
    transport=stdio
    shift
    server_name="$1"
    shift
    server_command=("$@")
else
    [ "$#" -le 1 ] || { echo 'Usage: sync-mcp.sh [mcp-servers.tsv]' >&2; exit 2; }
    manifest="${1:-$root/mcp-servers.tsv}"
    manifest="$(cd "$(dirname "$manifest")" && pwd -P)/$(basename "$manifest")"
fi

present_claude() { claude mcp get "$1" >/dev/null 2>&1; }
present_codex() { codex mcp get "$1" >/dev/null 2>&1; }
present_gemini() {
    jq -e --arg n "$1" '.mcpServers[$n]' "$HOME/.gemini/settings.json" >/dev/null 2>&1
}
add_claude() {
    local name="$1"; shift
    if [ "$transport" = stdio ]; then
        claude mcp add --scope user --transport stdio "$name" -- "$@" >/dev/null
    else
        claude mcp add --scope user --transport http "$name" "$1" >/dev/null
    fi
}
add_codex() {
    local name="$1"; shift
    if [ "$transport" = stdio ]; then
        codex mcp add "$name" -- "$@" >/dev/null
    else
        codex mcp add "$name" --url "$1" >/dev/null
    fi
}
add_gemini() {
    local name="$1"; shift
    local settings="$HOME/.gemini/settings.json" temporary arguments
    mkdir -p "$(dirname "$settings")" || return "$?"
    if [ ! -f "$settings" ]; then
        printf '{}\n' > "$settings" || return "$?"
    fi
    temporary="$(mktemp)" || return "$?"
    if [ "$transport" = stdio ]; then
        if ! arguments="$(jq -cn --args '$ARGS.positional' -- "${@:2}")"; then
            rm -f -- "$temporary"; return 1
        fi
        if ! jq --arg n "$name" --arg c "$1" --argjson a "$arguments" \
            '.mcpServers[$n] = {command: $c, args: $a}' "$settings" > "$temporary"; then
            rm -f -- "$temporary"; return 1
        fi
    elif ! jq --arg n "$name" --arg u "$1" \
        '.mcpServers[$n] = {httpUrl: $u}' "$settings" > "$temporary"; then
        rm -f -- "$temporary"; return 1
    fi
    if ! mv -f -- "$temporary" "$settings"; then
        rm -f -- "$temporary"; return 1
    fi
}

# A project .mcp.json must not shadow the user entry during presence checks.
neutral_directory="$(mktemp -d)"
trap 'rm -rf -- "$neutral_directory"' EXIT
cd "$neutral_directory"
register_server() {
    local name="$1" tool found=0; shift
    for tool in claude codex gemini; do
        command -v "$tool" >/dev/null 2>&1 || continue
        found=1
        if "present_$tool" "$name"; then
            printf 'present %-7s %s (unchanged; verify existing entry)\n' "$tool" "$name"
        else
            # Keep failures distinct from "present"; do not swallow CLI errors.
            "add_$tool" "$name" "$@" || return "$?"
            printf 'added   %-7s %s\n' "$tool" "$name"
        fi
    done
    if [ "$transport" = stdio ] && [ "$found" -eq 0 ]; then
        echo 'No installed MCP client CLI found (claude, codex, gemini).' >&2
        return 1
    fi
}
if [ "$transport" = stdio ]; then
    register_server "$server_name" "${server_command[@]}"
else
    while IFS=$'\t' read -r name url; do
        case "$name" in ''|'#'*) continue ;; esac
        register_server "$name" "$url"
    done < "$manifest"
fi
