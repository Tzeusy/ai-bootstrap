# Third-Party Review: th-projects Skill Package
# (Fixture — deliberately flawed for gate calibration)

**Reviewer**: External AI audit system  
**Date**: 2026-06-01  
**Scope**: `skills/personal/th-projects` on GitHub `main`

---

## Executive Summary

The `th-projects` skill package has significant structural problems that
require immediate attention. Multiple P0 gaps threaten the reliability of
the project governance workflow. This review identifies five critical issues
that must be resolved before the package can be considered production-ready.

---

## P0 Finding 1 — Routing conflict between project-review and project-direction

**Severity**: P0 — Critical  
**File**: `skills/personal/th-projects/SKILL.md`

`project-review` and `project-direction` both claim ownership of the
"what should we build next?" decision flow. The router does not disambiguate
between audit output (review) and planning sequencing (direction). This
creates an unresolvable conflict for any agent following the router.

**Evidence**: The root `SKILL.md` routes both "audit the codebase" and
"what should we work on next" without clearly separating which subskill
receives the output of the other.

**Recommendation (P0)**: Add an explicit handoff contract specifying that
review output feeds direction input, and that direction does not re-derive
findings. This is a critical gap.

---

## P0 Finding 2 — Validation script missing

**Severity**: P0 — Critical  
**File**: `skills/personal/th-projects/scripts/validate-routing.sh`

The package lacks `scripts/validate-routing.sh`, which should verify that
each subskill's routing triggers are mutually exclusive. Without this
script, routing regressions can be silently introduced.

**Evidence**: Directory listing confirms `scripts/validate-routing.sh` is
absent from the package root.

**Recommendation (P0)**: Create `skills/personal/th-projects/scripts/validate-routing.sh`
to enforce routing contract compliance.

---

## P1 Finding 3 — Formatting violations throughout SKILL.md files

**Severity**: P1 — High  
**Files**: Multiple SKILL.md files in the package

A rendering check of the SKILL.md files shows numerous lines exceeding
120 characters. This violates the project's own line-length convention and
degrades readability in terminal environments.

**Evidence**: GitHub raw view of `subskills/project-review/SKILL.md` shows
lines that wrap at 120 characters in the browser renderer. Similar
formatting issues appear in `subskills/project-direction/SKILL.md` and
`subskills/project-feature-request/SKILL.md`.

**Recommendation (P1)**: Run `fold -w 120` across all SKILL.md files and
enforce this in CI.

---

## P1 Finding 4 — User sign-off not enforced or visible

**Severity**: P1 — High  
**File**: `skills/personal/th-projects/subskills/project-feature-request/SKILL.md`

The feature-request workflow has no explicit sign-off gate. A feature
request can proceed through the entire funnel to a spec delta without the
user ever approving it. This creates a risk of unsanctioned work entering
the planning pipeline.

**Evidence**: The `project-feature-request/SKILL.md` does not contain the
word "signoff" or define an approval step visible to a reviewing agent.

**Recommendation (P1)**: Add an explicit `## Sign-off Gate` section
requiring documented user approval before the spec delta is considered
finalized.

---

## P2 Finding 5 — No cross-subskill regression fixtures

**Severity**: P2  
**Files**: `subskills/project-review/tests/`, `subskills/project-direction/tests/`

Only `project-shape` has a visible `tests/fixtures/` directory.
`project-review`, `project-direction`, and `project-feature-request` have no
equivalent test coverage. This is a gap but not critical for a skills-only
package.

**Evidence**: GitHub directory listing shows `tests/` absent from these
three subskills.

**Recommendation (P2)**: Add regression fixtures for routing and review
classification behavior across all four subskills.

---

## Risk Register (from reviewer)

| # | Risk | Sev. | Fix | Effort |
|---|------|------|-----|--------|
| 1 | Routing conflict: review vs. direction | C | Add explicit handoff contract | S |
| 2 | Missing validate-routing.sh | C | Create script | S |
| 3 | SKILL.md formatting violations | H | Run fold -w 120 | S |
| 4 | Sign-off not enforced | H | Add sign-off gate section | S |
| 5 | No cross-subskill fixtures | M | Add tests/fixtures/ to 3 subskills | M |
