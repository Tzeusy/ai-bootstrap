# Worked Example: `root-disk-audit`

Session precedent: root filesystem at 83% used, but a non-sudo `du` scan of
`/` only accounted for ~30% of that — the gap was root-owned directories
(`/var/lib/rancher` containerd overlay layers, k3s PV storage) that `du`
silently skips without permission. Diagnosing it required `sudo du` into
those paths, which the agent's sandbox cannot run interactively.

## Pre-presentation disclosure given to the user

```
What it does: sudo du/lsof across several root-owned directories
  (/var/lib/rancher, /var/lib/docker, /var/lib/snapd, /opt, /usr) plus a
  check for deleted-but-still-open files. Every command is read-only.
Risk: none — no deletes, no writes, no service impact. sudo is used only
  to read directory sizes and open-file tables.
State changes: none. Only writes new files under ~/.tmp/root-disk-audit/.
```

## The script (`~/root-disk-audit.sh`)

The first version of this script used a bare `$HOME` and was handed off as
`sudo ~/root-disk-audit.sh` (whole-script sudo). That reproduced exactly the
pitfall documented above: the run's output landed under `/root/.tmp/`
instead of `~/.tmp/`, unreadable without another sudo round-trip. The
version below is the fixed one.

```bash
#!/usr/bin/env bash
set -uo pipefail

slug="root-disk-audit"
real_home="$(getent passwd "${SUDO_USER:-$USER}" | cut -d: -f6)"
tmproot="$real_home/.tmp/$slug"
outdir="$tmproot/$(date +%Y%m%d-%H%M%S)"
mkdir -p "$outdir"

echo "==> Full root breakdown (depth 1, with sudo)"
sudo du -xh --max-depth=1 / 2>&1 | sort -rh | tee "$outdir/root-depth1.txt"

echo
echo "==> /var/lib/rancher breakdown (depth 3)"
sudo du -xh --max-depth=3 /var/lib/rancher 2>&1 | sort -rh | tee "$outdir/rancher-depth3.txt"

echo
echo "==> k3s PV storage per-volume, sorted largest first"
sudo du -sh /var/lib/rancher/k3s/storage/*/ 2>&1 | sort -rh | tee "$outdir/pv-storage-sorted.txt"

echo
echo "==> /var/lib/docker (if present)"
sudo du -sh /var/lib/docker 2>&1 | tee "$outdir/docker.txt"

echo
echo "==> /var/lib/snapd/snaps (old revisions often pile up)"
sudo du -sh /var/lib/snapd/snaps 2>&1 | tee "$outdir/snapd-snaps.txt"

echo
echo "==> Any deleted-but-still-open files holding space (top 20 by size)"
sudo lsof +L1 2>/dev/null | sort -k7 -rn | head -20 | tee "$outdir/deleted-open-files.txt"

ln -sfn "$outdir" "$tmproot/latest"

if [ "$(id -u)" -eq 0 ] && [ -n "${SUDO_USER:-}" ]; then
  chown -R "$SUDO_USER" "$tmproot"
fi

echo
echo "Done. Results saved under: $outdir"
ls -la "$outdir"
```

## Handoff to the user

> Run in your own terminal (needs your interactive sudo password):
> `sudo ~/root-disk-audit.sh`
> Tell me when it's done — I'll read `~/.tmp/root-disk-audit/latest/` myself.

## Reading the results back

```bash
readlink -f ~/.tmp/root-disk-audit/latest   # resolve the run directory
ls ~/.tmp/root-disk-audit/latest
```

Then `Read` the individual `.txt` files under that resolved path directly —
never ask the user to paste terminal output back into chat.
