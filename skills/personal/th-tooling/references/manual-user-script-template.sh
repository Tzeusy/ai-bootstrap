#!/usr/bin/env bash
# Authors: tze, Claude Sonnet 5
# Copy for a user-run sudo, TTY, or manual handoff. Do not run it for the user.
set -uo pipefail

slug="CHANGE_ME"
real_user="${SUDO_USER:-$USER}"
real_home="$(getent passwd "$real_user" | cut -d: -f6)"
tmproot="$real_home/.tmp/$slug"
outdir="$tmproot/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$outdir"

# Replace this read-only example. Tee each command to a separate output file.
echo "==> Example section"
true 2>&1 | tee "$outdir/example.txt"

ln -sfn "$outdir" "$tmproot/latest"
if [ "$(id -u)" -eq 0 ] && [ -n "${SUDO_USER:-}" ]; then
  chown -R "$real_user" "$tmproot"
fi

echo "Done. Results saved under: $outdir"
echo "Latest symlink: $tmproot/latest"
