# Planning and Review Cycle Hardening Plan

> Bead: `aib-45u`

## Goal

Reduce duplicated work, micro-PR overhead, and reviewer-authored correction
loops without weakening review of security, persistence, concurrency, or other
high-risk changes.

## Design

Keep policy at the narrowest authoritative layer:

- `th-projects/references/work-allocation.md` owns work-unit shape, dispatch
  readiness, additive contract sequencing, and discovery classification.
- `beads-writer` applies that policy before creating issues; `beads-coordinator`
  applies a lightweight gate before dispatch and classifies worker/reviewer
  discoveries before creating more beads.
- `beads-pr-reviewer-worker` remains an independent verifier. Corrections return
  to the implementation/recovery lane, with exact-head re-review and a
  two-correction checkpoint.
- `th-design` and `th-engineering` define whether review findings are small and
  in-scope enough to fix now or must return to the governing spec/allocation
  workflow. They do not duplicate Beads mechanics.

## Implementation Tasks

1. Add failing governance assertions to
   `skills/personal/th-projects/scripts/validate-th-projects.sh` for the dispatch
   packet, cohesion scan, additive rollout, and correction checkpoint.
2. Add failing documentation-contract assertions to the Beads skill package
   tests for discovery classification, reviewer independence, exact-head
   attestation, review risk tiers, and event-driven coordinator refresh.
3. Update `skills/personal/th-projects/references/work-allocation.md` and the
   project-direction Phase 3 handoff to satisfy the new allocation assertions.
4. Update beads-writer workflow/checklist and beads-coordinator loop/safety
   references. Put review-cycle behavior in reviewer references rather than the
   already-dirty reviewer `SKILL.md` in the canonical checkout.
5. Update design-bar and engineering-bar review guidance with the shared
   finding classification and ownership boundary.
6. Re-run focused tests, all four skill audits, `validate-th-projects.sh`, and
   the same three pressure scenarios against the modified worktree.
7. Review the diff, verify the canonical checkout's pre-existing dirty files
   are unchanged, commit on `agent/aib-45u`, push, and close the bead only after
   the branch is published and verification evidence is recorded.

## Verification Commands

```bash
python3 -m pytest skills/personal/beads-orchestration/subskills/*/tests/ --import-mode=importlib -q
bash skills/personal/th-projects/scripts/validate-th-projects.sh
uv run skills/personal/th-engineering/subskills/skill-standards/scripts/audit_skill.py skills/personal/beads-orchestration
uv run skills/personal/th-engineering/subskills/skill-standards/scripts/audit_skill.py skills/personal/th-projects
uv run skills/personal/th-engineering/subskills/skill-standards/scripts/audit_skill.py skills/personal/th-design
uv run skills/personal/th-engineering/subskills/skill-standards/scripts/audit_skill.py skills/personal/th-engineering
```
