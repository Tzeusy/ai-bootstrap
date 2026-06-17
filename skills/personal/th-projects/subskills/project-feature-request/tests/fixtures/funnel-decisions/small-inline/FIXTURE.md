# Fixture: Small Request → Beads-Writer Direct (No project-direction Needed)

## Input

**Trigger phrase**: "Add a `--version` flag to the CLI that prints the
installed package version."

**Context**: A user has noticed the CLI has no version flag. The version is
already recorded in `pyproject.toml`. Implementation is a one-liner using
the `importlib.metadata` stdlib. No new component boundary, no external
contract, no doctrine tension. One developer, one day.

**Session state**: Cold start. One request. `about/` pillars present.

## Expected Outcome

**Size**: Small — one component, no new boundaries, no doctrine tension.

**All gates answered inline in one pass.**

**Decision**: Approved → handoff directly to `beads-orchestration`
(beads-writer) for a single task bead; `project-direction` is NOT involved.

**Rationale**: `project-feature-request` SKILL.md sign-off section:
> **Approved** → hand the spec delta to `../project-direction/SKILL.md`
> for sequencing and decomposition; **for a small single-task request, file
> directly via `/beads-orchestration` (beads-writer)** with the spec
> reference.

The sizing table confirms "Small": one component, no new boundaries, no
doctrine tension → "All gates inline in one pass; minutes, not sessions."

## Gate Summary (Inline)

- **G0 Baseline**: shape present; no pillar constrains this request.
- **G1 Motif**: "User needs version introspection for debugging and scripting.
  Success: `cli --version` prints `cli 1.2.3` and exits 0."
  Motif: *version introspection*.
- **G2 Doctrine**: aligned — project values developer ergonomics; no
  non-negotiables touched. [Observed: `about/heart-and-soul/`]
- **G3 Topology**: lives in `cli/main.py` (argument parser); touches no
  boundaries; calls `importlib.metadata.version("package-name")`.
- **G4 Design**: no sketch needed — standard argparse pattern, no new state.
- **G5 Spec**: WHEN user runs `cli --version` THEN output is
  `cli {version}\n` and exit code is 0. Out of scope: changelog, update
  checks, machine-readable output.
- **G6 Bar**: add test asserting flag exists and output matches package
  metadata. No observability requirement (no network, no side effects).

## Key Assertions

1. **One request per run**: only this request is processed.
2. All gates answered in a single pass (no deep subagents per gate).
3. Funnel does NOT route to `project-direction` (no sequencing needed).
4. Funnel routes to `beads-orchestration` (beads-writer) with the spec
   reference and a single task bead.
5. **No implementation**: no code written or outlined beyond what's in the
   spec's WHEN/THEN scenarios.
6. **No sequencing leakage**: no task ordering, sprint planning, or
   implementation steps beyond the spec delta.
7. Sign-off is presented to the user before the bead is filed.

## Boundary

Small ≠ skipped. Every gate is answered — brevity is the point, not
omission. A small request that turns out to touch a boundary mid-funnel
(e.g., Gate 3 reveals the version must be read from a remote registry)
re-classifies to Medium and the funnel deepens accordingly.
