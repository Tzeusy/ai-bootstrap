#!/usr/bin/env bash
# Claude Code StatusLine - cross-platform (macOS + Ubuntu)
# Line 1: Model | tokens used/total | % used <count> | % remain <count> | thinking: on/off
# Line 2: current (5h): <bar> | weekly (7d): <bar> [| extra: <bar>]
# Line 3: resets <time> | resets <datetime> [| resets <date>]

# Read JSON from stdin
INPUT=$(cat)
if [ -z "$INPUT" ]; then
    printf "Claude"
    exit 0
fi

# Require jq
if ! command -v jq &>/dev/null; then
    printf "Claude (install jq)"
    exit 0
fi

# --- ANSI Colors ---
blue=$'\033[38;2;0;153;255m'
orange=$'\033[38;2;255;176;85m'
green=$'\033[38;2;0;160;0m'
cyan=$'\033[38;2;46;149;153m'
red=$'\033[38;2;255;85;85m'
yellow=$'\033[38;2;230;200;0m'
white=$'\033[38;2;220;220;220m'
dim=$'\033[2m'
reset=$'\033[0m'
sep=" ${dim}|${reset} "

# --- Helper: format token count (50k, 1.2m) ---
format_tokens() {
    local n=$1
    if [ "$n" -ge 1000000 ]; then
        awk "BEGIN { printf \"%.1fm\", $n/1000000 }"
    elif [ "$n" -ge 1000 ]; then
        awk "BEGIN { printf \"%dk\", int($n/1000 + 0.5) }"
    else
        printf "%d" "$n"
    fi
}

# --- Helper: format number with commas (portable) ---
format_commas() {
    printf "%d" "$1" | sed -e :a -e 's/\(.*[0-9]\)\([0-9]\{3\}\)/\1,\2/;ta'
}

# --- Helper: build colored progress bar (● filled, ○ empty) ---
build_bar() {
    local pct=$1 width=$2
    [ "$pct" -lt 0 ] 2>/dev/null && pct=0
    [ "$pct" -gt 100 ] 2>/dev/null && pct=100
    local filled=$(( pct * width / 100 ))
    local empty=$(( width - filled ))

    local bar_color
    if [ "$pct" -ge 90 ]; then bar_color=$red
    elif [ "$pct" -ge 70 ]; then bar_color=$yellow
    elif [ "$pct" -ge 50 ]; then bar_color=$orange
    else bar_color=$green
    fi

    local filled_str="" empty_str=""
    local i
    for ((i=0; i<filled; i++)); do filled_str+="●"; done
    for ((i=0; i<empty; i++)); do empty_str+="○"; done

    printf "%s%s%s%s%s" "$bar_color" "$filled_str" "$dim" "$empty_str" "$reset"
}

# --- Helper: parse ISO time to local (cross-platform) ---
format_reset_time() {
    local iso=$1 style=$2
    [ -z "$iso" ] && return

    if [[ "$OSTYPE" == darwin* ]]; then
        # macOS: use python3 (always available, BSD date can't parse ISO reliably)
        python3 -c "
from datetime import datetime, timezone
dt = datetime.fromisoformat('${iso}'.replace('Z','+00:00')).astimezone()
if '${style}' == 'time':
    print(dt.strftime('%-I:%M%p').lower(), end='')
else:
    print(dt.strftime('%b %-d, %-I:%M%p').lower(), end='')
" 2>/dev/null
    else
        # Linux: GNU date handles ISO natively
        if [ "$style" = "time" ]; then
            date -d "$iso" "+%-l:%M%P" 2>/dev/null | tr -d ' '
        else
            date -d "$iso" "+%b %-d, %-l:%M%P" 2>/dev/null | sed 's/  / /g'
        fi
    fi
}

# ========== PARSE MODEL & CONTEXT FROM STDIN JSON ==========

model_name=$(echo "$INPUT" | jq -r '.model.display_name // "Claude"')
size=$(echo "$INPUT" | jq -r '.context_window.context_window_size // 200000')
input_tokens=$(echo "$INPUT" | jq -r '.context_window.current_usage.input_tokens // 0')
cache_create=$(echo "$INPUT" | jq -r '.context_window.current_usage.cache_creation_input_tokens // 0')
cache_read=$(echo "$INPUT" | jq -r '.context_window.current_usage.cache_read_input_tokens // 0')

current=$(( input_tokens + cache_create + cache_read ))
used_fmt=$(format_tokens "$current")
total_fmt=$(format_tokens "$size")

if [ "$size" -gt 0 ]; then
    pct_used=$(( current * 100 / size ))
else
    pct_used=0
fi
pct_remain=$(( 100 - pct_used ))
used_comma=$(format_commas "$current")
remain_comma=$(format_commas "$(( size - current ))")

# --- Thinking status ---
thinking="Off"
thinking_color=$dim
settings_file="$HOME/.claude/settings.json"
if [ -f "$settings_file" ]; then
    thinking_val=$(jq -r '.alwaysThinkingEnabled // false' "$settings_file" 2>/dev/null)
    if [ "$thinking_val" = "true" ]; then
        thinking="On"
        thinking_color=$orange
    fi
fi

# ========== LINE 1: Model | tokens | % used | % remain | thinking ==========

line1="${blue}${model_name}${reset}"
line1+="${sep}${orange}${used_fmt} / ${total_fmt}${reset}"
line1+="${sep}${green}${pct_used}% used ${orange}${used_comma}${reset}"
line1+="${sep}${cyan}${pct_remain}% remain ${blue}${remain_comma}${reset}"
line1+="${sep}thinking: ${thinking_color}${thinking}${reset}"

# ========== LINES 2-3: Usage limits (cached API call) ==========

cache_dir="${TMPDIR:-/tmp}"
cache_file="${cache_dir}/claude-statusline-usage-cache.json"
cache_max_age=60

needs_refresh=true
if [ -f "$cache_file" ]; then
    if [[ "$OSTYPE" == darwin* ]]; then
        cache_mtime=$(stat -f %m "$cache_file" 2>/dev/null || echo 0)
    else
        cache_mtime=$(stat -c %Y "$cache_file" 2>/dev/null || echo 0)
    fi
    now=$(date +%s)
    age=$(( now - cache_mtime ))
    if [ "$age" -lt "$cache_max_age" ]; then
        needs_refresh=false
    fi
fi

usage_data=""
if [ "$needs_refresh" = true ]; then
    creds_file="$HOME/.claude/.credentials.json"
    if [ -f "$creds_file" ] && command -v curl &>/dev/null; then
        token=$(jq -r '.claudeAiOauth.accessToken // empty' "$creds_file" 2>/dev/null)
        if [ -n "$token" ]; then
            response=$(curl -s --max-time 5 \
                -H "Accept: application/json" \
                -H "Content-Type: application/json" \
                -H "Authorization: Bearer $token" \
                -H "anthropic-beta: oauth-2025-04-20" \
                -H "User-Agent: claude-code/2.1.34" \
                "https://api.anthropic.com/api/oauth/usage" 2>/dev/null) || true
            if [ -n "$response" ] && echo "$response" | jq . &>/dev/null; then
                usage_data="$response"
                echo "$response" > "$cache_file" 2>/dev/null || true
            fi
        fi
    fi
fi

# Fall back to stale cache
if [ -z "$usage_data" ] && [ -f "$cache_file" ]; then
    usage_data=$(cat "$cache_file" 2>/dev/null) || true
fi

line2=""
line3=""
bar_width=10

if [ -n "$usage_data" ]; then
    # --- 5-hour (current) ---
    five_pct=$(echo "$usage_data" | jq -r '.five_hour.utilization // 0' | awk '{printf "%d", $1+0.5}')
    five_reset_iso=$(echo "$usage_data" | jq -r '.five_hour.resets_at // empty')
    five_reset=$(format_reset_time "$five_reset_iso" "time")
    five_bar=$(build_bar "$five_pct" "$bar_width")

    # --- 7-day (weekly) ---
    seven_pct=$(echo "$usage_data" | jq -r '.seven_day.utilization // 0' | awk '{printf "%d", $1+0.5}')
    seven_reset_iso=$(echo "$usage_data" | jq -r '.seven_day.resets_at // empty')
    seven_reset=$(format_reset_time "$seven_reset_iso" "datetime")
    seven_bar=$(build_bar "$seven_pct" "$bar_width")

    # Line 2: progress bars
    line2="${white}current:${reset} ${five_bar} ${cyan}${five_pct}%${reset}"
    line2+="${sep}${white}weekly:${reset} ${seven_bar} ${cyan}${seven_pct}%${reset}"

    # Line 3: reset times
    line3="${white}resets ${five_reset}${reset}"
    line3+="${sep}${white}resets ${seven_reset}${reset}"

    # --- Extra usage (if enabled) ---
    extra_enabled=$(echo "$usage_data" | jq -r '.extra_usage.is_enabled // false')
    if [ "$extra_enabled" = "true" ]; then
        extra_pct=$(echo "$usage_data" | jq -r '.extra_usage.utilization // 0' | awk '{printf "%d", $1+0.5}')
        extra_used=$(echo "$usage_data" | jq -r '.extra_usage.used_credits // 0' | awk '{printf "%.2f", $1/100}')
        extra_limit=$(echo "$usage_data" | jq -r '.extra_usage.monthly_limit // 0' | awk '{printf "%.2f", $1/100}')
        extra_bar=$(build_bar "$extra_pct" "$bar_width")

        # Next month's 1st for reset date
        if [[ "$OSTYPE" == darwin* ]]; then
            extra_reset=$(date -v+1m -v1d "+%b %-d" 2>/dev/null | tr '[:upper:]' '[:lower:]')
        else
            extra_reset=$(date -d "$(date +%Y-%m-01) +1 month" "+%b %-d" 2>/dev/null | tr '[:upper:]' '[:lower:]')
        fi

        line2+="${sep}${white}extra:${reset} ${extra_bar} ${cyan}\$${extra_used}/\$${extra_limit}${reset}"
        line3+="${sep}${white}resets ${extra_reset}${reset}"
    fi
fi

# ========== OUTPUT ==========

printf "%s" "$line1"
[ -n "$line2" ] && printf "\n%s" "$line2"
[ -n "$line3" ] && printf "\n%s" "$line3"
