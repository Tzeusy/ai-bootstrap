# Expected Gate Output: third-party-overclaims

Phase 3.5 applied to `input-review.md`. Shows correct classification,
required gate steps, and Veracity Ledger entries for each claim.

---

## Gate Walkthrough

### Finding 1 — Routing conflict (reviewer severity: P0)

**Step 1 — Re-open named file**: `skills/personal/th-projects/SKILL.md`

**Step 2 — Search contradictory evidence**: Searched for "audit vs. plan",
"review classifies", "direction decides", "what to build next".

Found:
- Root `SKILL.md` contains explicit "Audit vs. plan" routing disambiguation.
- `project-review/SKILL.md`: "Not for: deciding what to build next (use /project-direction)"
- `project-direction/SKILL.md`: "Not for: scoring repo health or confirming findings (use /project-review)"
- Root `SKILL.md` Phase 3 output item: "confirmed findings feed direction; direction does not re-derive them"

**Step 3 — Path verification**: `skills/personal/th-projects/SKILL.md` exists. ✓

**Step 4 — Process claim verification**: The router explicitly separates audit
(review classifies) from planning (direction decides). The handoff contract
exists in prose across both subskill SKILL.md files.

**Step 5 — Classification**: `[Incorrect]`  
The routing conflict does not exist. The router already disambiguates these
roles explicitly and each subskill's scope excludes the other's.

**Step 6 — Action**: Remove from risk register. Add to Veracity Ledger.

---

### Finding 2 — Missing validate-routing.sh (reviewer severity: P0)

**Step 1 — Re-open named file**: Checked `skills/personal/th-projects/scripts/`
directory.

**Step 2 — Search contradictory evidence**: The claim that `validate-routing.sh`
exists nowhere implies the package's routing is unvalidated. However, the
claim that this *specific* script should exist and is *missing* requires the
path to have been a stated commitment somewhere.

**Step 3 — Path verification**: `skills/personal/th-projects/scripts/validate-routing.sh`
does **not** exist. The root `th-projects/` package has no `scripts/`
directory visible.

**Step 4 — Process claim verification**: No SKILL.md, spec, or doc file
commits to the existence of `validate-routing.sh`. This path is an invention
of the external reviewer, not a stated package requirement.

**Step 5 — Classification**: `[Incorrect]`  
The file does not exist, but its absence is not a defect — the package never
committed to having it. Claiming a missing file is a P0 gap requires the file
to have been a stated requirement. It was not.

**Note on severity**: Even if this were a real gap (it isn't), P0 is inflated.
A missing convenience script is at most P2. Demoted to `[Incorrect]` because
the premise (it was required) is false.

**Step 6 — Action**: Remove from risk register. Add to Veracity Ledger.

---

### Finding 3 — SKILL.md formatting violations (reviewer severity: P1)

**Step 1 — Re-open named files**: Would need to open
`subskills/project-review/SKILL.md`, `subskills/project-direction/SKILL.md`,
`subskills/project-feature-request/SKILL.md`.

**Step 2 — Search contradictory evidence**: The claim is based on "GitHub raw
view" browser rendering and wrapping behavior.

**Step 3 — Path verification**: The files exist. ✓

**Step 4 — Process claim verification**: Formatting claims (line-length
violations) require local-checkout evidence or GitHub-blob evidence (raw byte
inspection at a specific commit SHA). The reviewer cites "GitHub raw view"
and "browser renderer" — both are subject to viewport-width wrapping, not
actual file line lengths. No blob-level or `git show` evidence is provided.

**Special rule applies**: Formatting/line-length claims require local-checkout
OR GitHub-blob evidence. Raw/parser rendering alone is insufficient.

**Step 5 — Classification**: `[Unverifiable]`  
Cannot confirm line-length violations from browser rendering. The specific
evidence cited (renderer wrapping) is explicitly excluded by the gate's
special evidence rule.

**Step 6 — Action**: Remove from risk register and roadmap. Do not apply
`fold -w 120`. Add to Veracity Ledger.

---

### Finding 4 — Sign-off not enforced (reviewer severity: P1)

**Step 1 — Re-open named file**: `subskills/project-feature-request/SKILL.md`

**Step 2 — Search contradictory evidence**: Searched for "signoff", "sign-off",
"approval", "signed-off".

Found: `project-feature-request/SKILL.md` defines "signed-off spec delta" as
the funnel output and states "sign-off belongs to the user." Additionally,
`project-direction/SKILL.md` states "no coding before signoff."

**Step 3 — Path verification**: `subskills/project-feature-request/SKILL.md`
exists. ✓

**Step 4 — Process claim verification**: The reviewer claims "the word 'signoff'
does not appear." This is directly contradicted by the file content. The
sign-off requirement is defined; it is user-owned, not system-enforced, which
is the correct design for an agent skill.

**Step 5 — Classification**: `[Incorrect]`  
The file defines sign-off explicitly. The reviewer's claim that the word is
absent is factually wrong. The process claim that "a request can proceed
without user approval" is also wrong — `project-direction` explicitly
blocks implementation before sign-off.

**Step 6 — Action**: Remove from risk register. Add to Veracity Ledger.

---

### Finding 5 — No cross-subskill regression fixtures (reviewer severity: P2)

**Step 1 — Re-open named files**: Checked directory listings for
`subskills/project-review/tests/`, `subskills/project-direction/tests/`,
`subskills/project-feature-request/tests/`.

**Step 2 — Search contradictory evidence**: None of these directories exist
on `main` (at the time of the external review). The claim is structurally
accurate.

**Step 3 — Path verification**: Paths are absent. The claim is factually
correct.

**Step 4 — Process claim verification**: No SKILL.md or spec requires these
directories to exist. The absence is a gap, not a violation.

**Step 5 — Classification**: `[Confirmed]` (as a P2 observation, not a defect)  
Supporting evidence: `project-shape` has visible `tests/fixtures/`; the other
three subskills do not.  
Contradictory evidence checked: No spec requires them; `project-shape` is
the only subskill that ships validation scripts.

**Step 6 — Action**: Keep in risk register at P2 / Medium severity. No
demotion required. Note in handoff that this is a useful improvement, not a
critical gap.

---

## Revised Risk Register (after gate)

_Only confirmed findings appear here._

| # | Risk | Sev. | Likelih. | Impact | Conf. | Fix | Effort |
|---|------|------|----------|--------|-------|-----|--------|
| 1 | No cross-subskill regression fixtures | M | M | M | H | Add tests/fixtures/ to project-review, project-direction, project-feature-request | M |

Four of five original risks removed or demoted. Original P0 severity claims
on routing conflict and missing script were both Incorrect.

---

## Veracity Ledger

_Claims that did not survive Phase 3.5. Not planning inputs._

| Prior claim | Classification | Invalidating evidence / reason |
|-------------|----------------|-------------------------------|
| P0: routing conflict between review and direction | [Incorrect] | `th-projects/SKILL.md` has explicit "Audit vs. plan" routing. `project-review/SKILL.md` excludes planning; `project-direction/SKILL.md` excludes scoring/confirming. No conflict exists. |
| P0: `scripts/validate-routing.sh` is missing | [Incorrect] | Path was never a package commitment. No SKILL.md, spec, or doc commits to this script's existence. Absence of an uncommitted file is not a defect. Severity also inflated — a missing convenience script is at most P2. |
| P1: SKILL.md files exceed 120-char line length | [Unverifiable] | Evidence was browser/renderer wrapping, which is viewport-dependent. Formatting claims require local-checkout or GitHub-blob evidence. Special evidence rule applies. |
| P1: user sign-off not enforced or visible | [Incorrect] | `project-feature-request/SKILL.md` defines "signed-off spec delta" and "sign-off belongs to the user." `project-direction/SKILL.md` states "no coding before signoff." Sign-off is defined and cross-referenced. |
