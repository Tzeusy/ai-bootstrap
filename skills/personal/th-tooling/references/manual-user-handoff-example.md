# Manual Handoff Example: Root Disk Audit

Authors: tze, Claude Sonnet 5

This example diagnoses a filesystem whose visible non-root scan accounts for
far less space than `df`. Root-owned container storage requires the user's
interactive sudo credential.

## Disclosure

```text
What it does: Runs read-only du and lsof checks across root-owned storage and writes each result under ~/.tmp/root-disk-audit/.
Risk: none; no deletes, configuration changes, or service impact.
State changes: output files and a latest symlink under ~/.tmp/root-disk-audit/ only.
```

## Script

```bash
#!/usr/bin/env bash
set -uo pipefail

slug="root-disk-audit"
real_user="${SUDO_USER:-$USER}"
real_home="$(getent passwd "$real_user" | cut -d: -f6)"
tmproot="$real_home/.tmp/$slug"
outdir="$tmproot/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$outdir"

sudo du -xh --max-depth=1 / 2>&1 | sort -rh \
  | tee "$outdir/root-depth1.txt"
sudo du -xh --max-depth=3 /var/lib/rancher 2>&1 | sort -rh \
  | tee "$outdir/rancher-depth3.txt"
sudo du -sh /var/lib/rancher/k3s/storage/*/ 2>&1 | sort -rh \
  | tee "$outdir/pv-storage-sorted.txt"
sudo lsof +L1 2>/dev/null | sort -k7 -rn | head -20 \
  | tee "$outdir/deleted-open-files.txt"

ln -sfn "$outdir" "$tmproot/latest"
if [ "$(id -u)" -eq 0 ] && [ -n "${SUDO_USER:-}" ]; then
  chown -R "$real_user" "$tmproot"
fi
echo "Done. Results saved under: $outdir"
```

Tell the user to run `sudo ~/root-disk-audit.sh` in their own terminal. After
confirmation, resolve `~/.tmp/root-disk-audit/latest/` and read the result
files directly. Never request paste-back.
