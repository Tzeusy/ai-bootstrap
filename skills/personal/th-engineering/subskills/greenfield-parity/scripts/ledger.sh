#!/usr/bin/env bash
# Emit the already-known ledger for an idempotent audit run: open/in-progress
# beads, recently closed beads, prior review packets, and the last recorded
# convergence record. Output is compact and projected; paste it verbatim into
# reviewer prompts.
#
# Usage: ledger.sh [repo_root] [closed_limit]
#   repo_root     Beads-backed repo (default: cwd)
#   closed_limit  how many recently closed beads to list (default: 40)
set -euo pipefail
root="${1:-.}"; limit="${2:-40}"
command -v bd >/dev/null || { echo "ledger.sh: bd CLI not found; cannot build ledger" >&2; exit 2; }
command -v jq >/dev/null || { echo "ledger.sh: jq not found" >&2; exit 2; }
cd "$root"
echo "## Open / in-progress"
bd list --json --limit 0 | jq -r '.[] | select(.status != "closed") | "\(.id) \(.status) [\((.labels // []) | join(","))] \(.title)"'
echo; echo "## Recently closed (last $limit)"
bd list --status closed --sort closed --limit "$limit" --json | jq -r '.[] | "\(.id) \(.closed_at // "") \(.title)"'
echo; echo "## Audit-keyed beads"
bd search "Audit-key: greenfield:" 2>/dev/null | sed '/^No issues/d' || true
echo; echo "## Prior review packets"
ls docs/reviews/ 2>/dev/null || echo "(none)"
echo; echo "## Last convergence record"
last="$(ls docs/reviews/*greenfield-delta.md 2>/dev/null | sort | tail -1 || true)"
[ -n "$last" ] && grep -E '^(Audited|Findings|Parity share|Owner gates):' "$last" || echo "(none — first run)"
echo; echo "## Prior owner questionnaires (packets + answers)"
qroot="${QUESTIONNAIRE_STATE_ROOT:-$HOME/.tmp/user-questionnaire}"
repo="$(basename "$(pwd -P)")"
# questionnaire_web.py keeps answers in <qroot>/<packet stem>-<sha1(abs packet path)[:8]>/,
# not beside the packet; derive that state dir the same way.
found=0
for d in "$qroot"/*"$repo"*greenfield*/; do
  [ -d "$d" ] || continue; found=1
  echo "${d%/}"
  for packet in "$d"*.md; do
    [ -f "$packet" ] || continue
    abs="$(realpath "$packet")"; stem="$(basename "$abs" .md)"
    digest="$(printf '%s' "$abs" | sha1sum | cut -c1-8)"
    answers="$qroot/$stem-$digest/answers.json"
    if [ -f "$answers" ]; then
      jq -r --arg p "$(basename "$packet")" '"  \($p): completed: \(.completed_at // "no") apply_now: \(.apply_now) answered: \(.items | length)"' "$answers"
    else
      echo "  $(basename "$packet"): no answers recorded"
    fi
  done
done
[ "$found" = 1 ] || echo "(none)"
