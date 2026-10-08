#!/usr/bin/env bash
# Create /home/orca/.tmp/<slug>/run.sh from the user-run template if it does not exist.
# Usage: scaffold.sh <slug>     (slug: lowercase, digits, dashes)
# Prints the run.sh path. Never overwrites an existing run.sh.
set -euo pipefail
slug="${1:?usage: scaffold.sh <slug>}"
[[ "$slug" =~ ^[a-z0-9][a-z0-9-]*$ ]] || { echo "bad slug: $slug" >&2; exit 2; }
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
dir="/home/orca/.tmp/$slug"
umask 002
mkdir -p "$dir/artifacts"
chmod 2770 "$dir" "$dir/artifacts"
if [ ! -e "$dir/run.sh" ]; then
  sed "s/__SLUG__/$slug/g" "$here/../assets/run.sh.template" > "$dir/run.sh"
fi
chmod 0770 "$dir/run.sh"
bash -n "$dir/run.sh"
echo "$dir/run.sh"
