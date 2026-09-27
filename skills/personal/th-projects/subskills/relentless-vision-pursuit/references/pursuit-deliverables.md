# Pursuit Deliverables: Dossier, Gated Epic, Memory

## Dossier

Home: the project's established pursuit home if one exists (check prior
dossiers); default `docs/pursuits/`. Two files per run, docs-only and safe
to commit directly where repo convention allows:

- `YYYY-MM-DD-vision-pursuit.md` — north star (quoted), tier board with
  movement vs baseline, systemic themes with exemplars, ranked move list
  (what / why with doctrine citation / evidence / rough slice plan), and
  the known-ledger snapshot the run deduped against.
- `YYYY-MM-DD-vision-pursuit-data.json` — full per-unit (surface or lens) structured output.
  Document the access pattern in the md, e.g.
  `jq '.audits[] | select(.surface=="<key>")'`.

The `-harvest.json` and state working files (execution discipline §3) stay
beside them, gitignored and never committed. They are the raw material the
dossier can be rebuilt from.

### Size and retention caps

Dossiers accrete every run; cap them so the tree does not become the archive.

- The md stays under **25 KB**, with at most **15 ranked moves** of one short
  paragraph each. Per-move detail lives in the bead's structured fields and
  the JSON, not the md.
- The JSON holds structured per-unit output only (no transcripts, prompts or
  raw tool output) and stays under **500 KB**.
- Only the **two newest runs** keep their `-data.json` in the tree. The change
  adding a new pair removes older JSONs and repoints each pruned run's md
  (links and `jq` examples) to `git show <sha>:<path> | jq …`, pinned to the
  last commit that held it. Git history is the archive.

## Tier board

One row per surface: verdict tier
(`world-class | solid | functional | weak | broken`) and a movement column
vs the prior dossier's baseline. Movement is only *claimed* for surfaces a
verification pass confirmed (Phase 0 step 5); movement inferred from source
reading alone is labeled [Inferred]. First run: tiers only, no movement
column.

## Gated epic (planning, never execution)

A pursuit run files work but must not make it runnable — in repos where an
autonomous fleet picks up ready beads, the gate is the only thing between a
pursuit run and an unsanctioned fleet launch.

1. Create a `[HOLD]` gate bead first, **assigned to the owner**.
2. Create the epic + one child bead per move; every child depends on the
   gate so all are blocked. bd rejects a task blocking an epic ("epics can
   only block other epics") — so also **assign the epic itself to the
   owner** to keep it off `bd ready`.
3. Every bead description cites its evidence and points at the dossier
   JSON by pinned commit (`<sha>:<path>`), so retention pruning never breaks
   the pointer.
4. Bulk creation: `bd create` Dolt-commits per write (slow, serialized) —
   use `--dolt-auto-commit batch` and one `bd dolt commit` at the end.
   **Never** `bd create --graph` (its `--dry-run` actually creates beads
   and drops deps); add edges with `bd dep add`.
5. Release is the owner's move: closing the gate un-blocks the children.
   State this explicitly in the final report.

No bd in the repo → the ranked move list stays in the dossier and the run
stops there; do not improvise a tracker.

## Memory

Write or update one durable memory (`bd remember` where available,
otherwise a `reference` memory) holding the dossier path, epic id, gate id,
and artifact URL if one was published; link the prior pursuit's memory so
runs form a chain.
