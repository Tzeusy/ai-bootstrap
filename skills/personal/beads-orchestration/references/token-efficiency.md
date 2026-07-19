# Token Efficiency

Applies to every subskill in this package. The orchestration engine's cost is
dominated by (a) verbose command output landing in context, (b) full test
suites run repeatedly, and (c) oversized models on mechanical work. These rules
cap all three. They never override correctness rules — when a safety rule and
an efficiency rule conflict, safety wins.

## Command output discipline

- Never dump unfiltered `--json` output into context. Project to the fields you
  will actually use:

  ```bash
  bd ready --json | jq -c '[.[] | {id, title, priority, type, labels, assignee}]'
  bd list --status=blocked --label pr-review --json | jq -c '[.[] | {id, title, labels, assignee, external_ref}]'
  bd show <id> --json | jq '{id, title, status, assignee, labels, external_ref}'   # coordinator view
  ```

  Workers implementing a bead additionally need `description`,
  `acceptance_criteria`, and `notes` — project to those, not the full record.
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
  package, or `-k` selection). Run the repository's full required gate exactly
  once, immediately before handoff, with the runner's quiet flag (`-q`,
  `--quiet`, `--silent`).
- On a full-gate failure, iterate on the failing subset (`--lf`, named test
  ids), then re-run the full gate once more.
- This narrows iteration only — it never substitutes a lighter gate for one the
  repository defines. The final pre-handoff run is always the full defined gate.

## Model right-sizing

- Follow the assignment tables in
  `../subskills/beads-coordinator/references/runtime-and-safety.md`. Default
  down, escalate on evidence: a wrong-too-weak dispatch costs one redispatch; a
  habitually-too-strong dispatch taxes every bead.
- If the bead carries a `complexity:<tier>` label (stamped by `beads-writer`),
  use it directly instead of re-deriving complexity from the description.

## Reference loading

- Load a reference file only when its owning step is actually reached; never
  preload the whole `references/` tree.
- Search `known-errors.md` with `rg -i -n '<error text>'` and read only the
  matching section — do not read the whole catalog on every error.
