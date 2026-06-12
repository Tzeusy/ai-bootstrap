---
name: transcript-retention
description: >
  Use to manage the disk footprint of AI-tool session state — Claude Code
  transcripts (~/.claude/projects), Codex rollouts (~/.codex/sessions),
  shell snapshots, logs, and sqlite WAL files — by reporting usage and
  applying an age-based compress/delete policy. Triggers: "how big is my
  session history", "clean up old transcripts", "codex sessions are eating
  disk", "transcript retention".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
compatibility: Linux/macOS with gzip and standard find; assumes ~/.claude and ~/.codex tool homes.
---

# Transcript Retention

Session stores grow without bound (observed 2026-06-12: `~/.codex/sessions`
3.4G, `~/.claude/projects` 700M). But transcripts are not junk: they are
the **data source for [../audit-skill-hygiene/SKILL.md](../audit-skill-hygiene/SKILL.md)**
and for any future usage analytics. Retention policy therefore defines the
maximum audit window — decide retention *with* that trade-off, never as
plain disk cleanup.

## Inventory first (always safe)

```bash
du -sh ~/.claude/projects ~/.codex/sessions ~/.codex/shell_snapshots \
       ~/.codex/log ~/.codex/tmp 2>/dev/null
# Age profile: bytes per month
find ~/.codex/sessions ~/.claude/projects -name "*.jsonl" -printf "%TY-%Tm %s\n" 2>/dev/null \
  | awk '{b[$1]+=$2} END {for (m in b) printf "%s  %6.0f MB\n", m, b[m]/1e6}' | sort
```

Report the inventory and the proposed action per tier before touching
anything.

## Default policy (adjust per user preference)

| Age | Action | Rationale |
|---|---|---|
| < 60d | keep as-is | active audit window, resumable sessions |
| 60–180d | `gzip` in place | ~10x smaller; still grep-able via `zgrep` for audits |
| > 180d | propose deletion | beyond any realistic audit window |

- Compression is safe and reversible; **deletion is destructive** — always
  list the candidates (count + size + date range) and get explicit
  confirmation before `rm`.
- Never touch files modified in the last 7 days regardless of policy: an
  active session's transcript may have an old creation date.
- `~/.codex/tmp` and rotated logs are exempt from the confirmation rule
  (genuinely disposable), but report what was reclaimed.

## Hard stops

- Do not delete or compress sqlite databases or their `-wal`/`-shm`
  sidecars (`goals_*.sqlite`, `memories_*.sqlite`, `state_*.sqlite`) — they
  are live state, not history, and a WAL file belongs to its DB.
- Do not prune transcripts younger than the longest audit window the user
  relies on; if unsure, ask before the delete tier (compress tier is fine).
- If a `zgrep`-based audit has never been exercised after the first
  compression pass, run one spot-check (`zgrep -c '"name":"Skill"'` on a
  compressed file) and note that audit tooling must use `zgrep`/`zcat` for
  the compressed tier.
