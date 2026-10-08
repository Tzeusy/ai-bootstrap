#!/usr/bin/env bash
# Create <base>/<slug>/run.sh from the user-run template if it does not exist,
# after pruning user-run dirs and runs older than 7 days (cleanup.sh).
# Usage: scaffold.sh <slug>     (slug: lowercase, digits, dashes)
# <base> is $USER_RUN_BASE, default $HOME/.tmp of the Claude session user.
# Prints the run.sh path. Never overwrites an existing run.sh.
set -euo pipefail
slug="${1:?usage: scaffold.sh <slug>}"
[[ "$slug" =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo "bad slug: $slug" >&2; exit 2; }
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
base="${USER_RUN_BASE:-$HOME/.tmp}"
[[ "$base" =~ ^/[A-Za-z0-9/._-]*$ ]] || { echo "bad base dir (want [A-Za-z0-9/._-]): $base" >&2; exit 2; }
dir="$base/$slug"
umask 002

"$here/cleanup.sh" --quiet --keep "$slug" || echo "warning: cleanup failed (continuing)" >&2

mkdir -p "$dir/artifacts"
chmod 2770 "$dir" "$dir/artifacts"
if [ ! -e "$dir/run.sh" ]; then
  sed -e "s|__SLUG_DIR__|$dir|g" -e "s|__SLUG__|$slug|g" \
    "$here/../assets/run.sh.template" > "$dir/run.sh.tmp"
  mv "$dir/run.sh.tmp" "$dir/run.sh"
fi
chmod 0770 "$dir/run.sh"
bash -n "$dir/run.sh"
echo "$dir/run.sh"
