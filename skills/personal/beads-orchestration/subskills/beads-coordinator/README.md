# beads-coordinator

Orchestration subskill for unattended Beads throughput. It never implements
code: it normalizes Beads state, prioritizes PR review, claims ready issues
atomically, dispatches isolated workers, and reconciles their reports back into
Beads. Workers push code and report; the coordinator owns the Beads state
machine.

Start with [`SKILL.md`](SKILL.md): it states the invariants once and its
read-order table names the single file that owns each procedure. Do not
duplicate that table here.

## Diagrams

![Coordinator cycle](assets/coordinator-cycle.svg)

![PR-review lane](assets/pr-review-lane.svg)

Editable sources: `assets/*.excalidraw`.
