#!/usr/bin/env bash
# Report the latest run of a user-run slug: state, exit code, RESULT lines,
# artifacts and the log tail. Read this before the raw log.
# Usage: status.sh <slug> [tail-lines=40]
set -uo pipefail
slug="${1:?usage: status.sh <slug> [tail-lines]}"
lines="${2:-40}"
dir="${USER_RUN_BASE:-$HOME/.tmp}/$slug"
[ -d "$dir" ] || { echo "no such slug dir: $dir" >&2; exit 2; }

if [ ! -L "$dir/latest.log" ]; then
  echo "state=never-run dir=$dir"
  exit 0
fi
run_id="$(basename "$(readlink "$dir/latest.log")" .log)"

running=0
if [ -e "$dir/.lock" ]; then
  exec 9<"$dir/.lock"
  flock -n 9 || running=1
  exec 9<&-
fi
if [ "$running" = 1 ]; then
  state=running
elif [ -e "$dir/$run_id.exit" ] && [ ! -e "$dir/$run_id.started" ]; then
  state="not-started exit=$(cat "$dir/$run_id.exit") (su failed: wrong password or no terminal; payload never ran)"
elif [ -e "$dir/$run_id.exit" ]; then
  state="done exit=$(cat "$dir/$run_id.exit")"
else
  state="died (no exit code: killed or terminal closed mid-run)"
fi

echo "run=$run_id state=$state"
echo "log=$dir/$run_id.log ($(wc -l < "$dir/$run_id.log") lines)"
echo "--- RESULT lines"
tr -d '\r' < "$dir/$run_id.log" | grep -a '^RESULT' || echo "(none)"
echo "--- artifacts ($dir/artifacts/$run_id)"
ls -la "$dir/artifacts/$run_id" 2>/dev/null | tail -n +4 || echo "(none)"
echo "--- log tail ($lines)"
tail -n "$lines" "$dir/$run_id.log" | tr -d '\r'
