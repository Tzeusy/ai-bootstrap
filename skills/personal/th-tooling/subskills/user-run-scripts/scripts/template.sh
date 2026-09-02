#!/usr/bin/env bash
# Template for a script the USER runs themselves (sudo/TTY/manual step the
# agent's sandbox cannot do). Copy this, rename the slug, fill in commands.
#
# Do not attempt to run this for the user (sudo -S, askpass, piped
# password, etc.) — hand it to them to run in their own terminal.
set -uo pipefail  # not -e: keep reporting later sections even if one fails
                   # (switch to `set -euo pipefail` for a dependent mutating
                   # sequence where any failure must halt immediately)

slug="CHANGE_ME"  # short kebab-case name for this task, e.g. root-disk-audit

# Resolve the real invoking user's home even if the WHOLE script is run
# under `sudo` (e.g. `sudo ~/script.sh`), which resets $HOME to /root by
# default — a bare `$HOME` here would silently write into /root/.tmp,
# unreadable to the agent and to the user without another sudo. This
# matters even if individual commands below also say `sudo` themselves.
real_home="$(getent passwd "${SUDO_USER:-$USER}" | cut -d: -f6)"
tmproot="$real_home/.tmp/$slug"
outdir="$tmproot/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$outdir"

# TODO: add your commands here, each teed into its own file under $outdir
echo "==> Example section"
sudo true 2>&1 | tee "$outdir/example.txt"

# Repoint latest/ to this run — always last, only on reaching this line
ln -sfn "$outdir" "$tmproot/latest"

# If this whole script ran under sudo, everything above was created as
# root — hand it back to the real user so it's readable without sudo.
if [ "$(id -u)" -eq 0 ] && [ -n "${SUDO_USER:-}" ]; then
  chown -R "$SUDO_USER" "$tmproot"
fi

echo
echo "Done. Results saved under: $outdir"
echo "Latest symlink: $tmproot/latest"
ls -la "$outdir"
