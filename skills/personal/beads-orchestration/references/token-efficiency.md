# Token Efficiency

Applies to every execution path and the planning allocation contract. Keep
sessions useful, packets current, outputs projected and verdicts reusable.
Cache hits still cost money and activity counts do not measure active engineering
time. No cache percentage implies measured speedup or savings.

## Cache-first execution: persistent outcome owners

The execution units, branch choice, packet, evidence and recovery rules live in
[delivery-model.md](delivery-model.md). A persistent owner carries a bounded
outcome through packages and corrections; several cohesive beads can share one
claim set/worktree/PR/review cycle. Continue the same session for corrections or
the next related package. A new branch does not require a new session.

Default to one implementation owner; add independent owners only for disjoint
outcomes or a separately owned shared prerequisite within the existing lane
budget. Keep an independent reviewer session, reused while independence holds.
Fan out for independent judgment or material context isolation, not to relay
routine engineering. Retire on demonstrated compaction drift or a new context
and model requirement; publish the current recovery packet first.

Wake on useful events, not solely to keep a cache warm. Use the bounded cadence
and registry rules in
[runtime-and-safety.md](../subskills/beads-coordinator/references/runtime-and-safety.md).

## Command output discipline

- Never dump unfiltered `--json` output into context. Project to the fields you
  will actually use:

  ```bash
  bd ready --json | jq -c '[.[] | {id, title, priority, type, labels, assignee}]'
  bd list --status=blocked --label pr-review --json | jq -c '[.[] | {id, title, labels, assignee, external_ref}]'
  bd show <id> --json | jq '.[0] | {id, title, status, assignee, labels, external_ref}'   # coordinator view
  ```

  Workers implementing a bead additionally need `description`,
  `acceptance_criteria`, `design`, and `notes` — project to those, not the full record.
- For `gh`, always pass an explicit `--json <fields>` list; never fetch default
  field sets.
- Route long stdout (test runs, builds, installs) to a file; read back only the
  exit status and the failure tail:

  ```bash
  <gate command> >"$TMPDIR/gate.log" 2>&1; status=$?
  [ $status -ne 0 ] && tail -40 "$TMPDIR/gate.log"
  ```

- Never re-run a command just to re-see output you already have in context.

## Verification discipline

- While iterating, run only the tests covering the changed area (test file,
  package, or `-k` selection).
- The full required gate runs once per tree, in the tier the repository's
  test-scope or CI policy assigns it (`../../th-engineering/subskills/ci-discipline/SKILL.md`).
  Skip the local run only when the repository assigns broad lanes to hosted
  CI or a merge queue **and** a required hosted check covers the tree that
  lands; then the hosted run is the gate and no local copy precedes it.
  Otherwise (no hosted CI, CI not required, a direct push to the base) run it
  exactly once, immediately before handoff, with the runner's quiet flag
  (`-q`, `--quiet`, `--silent`).
- On a full-gate failure, iterate on the failing subset (`--lf`, named test
  ids), then re-run the full gate once more.
- This narrows iteration only — it never substitutes a lighter gate for one the
  repository defines, and never adds a heavier local run than the repository's
  placement policy calls for. Nobody re-runs a passing gate on an unchanged
  tree: implementer and reviewer share the hosted verdict for the exact head.

## Model right-sizing

- Follow the assignment tables in
  `../subskills/beads-coordinator/references/runtime-and-safety.md`. Default
  down, escalate on evidence: a wrong-too-weak dispatch costs one redispatch; a
  habitually-too-strong dispatch taxes every bead.
- **Model continuity beats per-bead right-sizing inside a lane.** Pick a
  lane's model once, from the highest tier among its chain's beads, and keep
  it. Switching models mid-lane throws away the cache. Right-sizing applies
  when a lane is formed and to one-shot dispatches (probes, formatting, a
  lone bead).
- If the bead carries a `complexity:<tier>` label (stamped by `beads-writer`),
  use it directly instead of re-deriving complexity from the description,
  unless the design/specification override or Reconciliation Floor in
  `../subskills/beads-coordinator/references/runtime-and-safety.md` applies.

## Reference loading

- Load a reference file only when its owning step is actually reached; never
  preload the whole `references/` tree.
- Search `known-errors.md` with `rg -i -n '<error text>'` and read only the
  matching section — do not read the whole catalog on every error.
