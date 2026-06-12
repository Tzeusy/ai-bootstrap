# Review and Documentation

Review in this repo is primarily about preventing silent drift in source of
truth, naming, provenance, and local-state boundaries.

## Author Obligations

- State which layer is authoritative for the change.
- Update README, doctrine, RFC, spec, and standards material in the same change
  when their meaning moved.
- Call out anything that could not be fully verified.
- Keep in-repo shape-navigation routes (`CLAUDE.md`, `AGENTS.md`) aligned with
  the canonical docs they index.

## Reviewer Blocking Findings

Block the change if any of the following are true:

- the authoritative copy of a workflow, rule, or asset became less clear;
- shared logic was duplicated into a tool facade without a documented reason;
- a local skill became a monolith or no longer routes to canonical docs;
- generated or vendored content changed without a regeneration path;
- the change weakens provenance, flattened-name clarity, or local-only state
  boundaries;
- the shape docs disagree about pillar naming, placement rules, or installation
  semantics.

## Documentation Discipline

- Structural rules belong in shared docs, not only in one tool's prompt file.
- If a change affects where something belongs, update the relevant shape docs
  before or alongside the code/config move.
- If a rule is repeatedly enforced in review, promote it into the correct pillar
  instead of relying on reviewer memory.
