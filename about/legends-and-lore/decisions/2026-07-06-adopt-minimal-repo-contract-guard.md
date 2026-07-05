# Decision: Adopt Minimal Repo-Contract Drift Guard (v1 scope)

Date: 2026-07-06 · Decided by: tze (via aib-86z human-scope-decision gate)

## Request summary

The 2026-06-17 third-party review proposed a full `repo-contract.yml` with 8
automated checks. `about/heart-and-soul/v1.md` explicitly defers "fully
automated cross-tool sync and validation for every mirror surface", so the
proposal was scoped down and flagged for a human decision rather than
auto-adopted.

## Decision

Adopt a **minimal two-check guard only** — `tests/repo-contract-test.sh`:

1. README "Skills Layout And Provenance" ↔ `.gitmodules` submodule inventory,
   both directions (REQ-repository-shape-002).
2. No tracked file may be gitignore-matched or on a small never-track
   denylist of session/auth/cache state (REQ-repository-shape-006).

These are exactly the checks that would have caught the two confirmed
findings behind aib-c0n (README provenance drift) and aib-v0c (tracked
machine-local `.gemini` state). The guard cites the requirement IDs it
enforces, so `spec-trace-check.py` counts them as covered.

## What would change the outcome

Expanding beyond these two checks requires a v1 scope amendment first — the
v1 deferral of full mirror-surface validation stands. Revisit at v2 scoping
or if a third confirmed drift class appears.
