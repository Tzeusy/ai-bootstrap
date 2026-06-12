# Funnel Gates: Inputs, Exit Criteria, Kill Conditions

Each gate has a required output. A gate may be *brief* (small requests answer
most gates in a sentence) but never *skipped* — a skipped gate is where scope
creep and doctrine drift enter.

## Gate 0 — Baseline

**Input**: repository; `about/` and `openspec/` if present.
**Do**: run `../../project-shape/scripts/shape-scan.sh <repo>` when available;
otherwise glance for the five pillars manually.
**Output**: one line per pillar — present/absent and whether it constrains this
request.
**Exit**: you know which later gates have a normative source and which will be
[Inferred].
**Never**: block the funnel on missing shape. Note it, suggest project-shape
separately, continue in lite mode.

## Gate 1 — Concretize the Motif

**Input**: the raw request, the requester.
**Do**: interview until you can state, in the requester's own language:
- **Problem** — what hurts today, with a concrete example
- **Who** — which user/persona hits it, how often
- **Success** — what observable behavior changes when this ships
- **Motif** — the recurring need this is an instance of (a request is one
  instance; the spec should name the pattern so the design generalizes the
  right amount and no further)

Challenge patterns (borrow freely from
`../../project-shape/references/consultative-bootstrapping.md`):
- "Give me the last time this actually happened."
- "If we shipped only half of this, which half is the point?"
- "What are you doing today instead, and why is that intolerable?"
- "Is this the need, or the solution you already picked for it?"

**Exit**: problem + success criteria are falsifiable; the motif is named.
**Kill**: the requester cannot produce a concrete instance — park it as an
observation, not a feature.

## Gate 2 — Doctrine

**Input**: Gate 1 output; `about/heart-and-soul/` if present.
**Do**: check the request against vision, non-negotiables, and explicit
scope boundaries ("what this is NOT").
**Output**: one of —
- **Aligned**: cite the specific principle or scope line it serves
- **Conflict**: cite the contradicted principle; outcome is *reject* or
  *escalate a doctrine change* (full alignment required), never a quiet
  exception
- **No doctrine**: record your alignment judgment as [Inferred] and flag that
  the project is accumulating direction debt

**Exit**: an explicit verdict with citation.
**Kill**: conflict + requester unwilling to escalate doctrine. Record the
rejection; this is the funnel working, not failing.

## Gate 3 — Topology

**Input**: Gates 1-2 output; `about/lay-and-land/` if present.
**Do**: name the components this touches, the boundaries it crosses, the
integration points it adds, and where the new behavior is observable.
**Output**: a placement statement — "lives in X, talks to Y over Z, changes the
A↔B contract / changes no contracts".
**Exit**: someone who knows the codebase could point at the directories.
**Kill / loop**: if the honest answer is "everywhere", the request is a program
not a feature — return to Gate 1 and split by motif.

## Gate 4 — Design Sketch

**Input**: Gates 1-3; `about/legends-and-lore/` conventions
(`../../project-shape/references/pillar-legends-and-lore.md`).
**Do** (medium+): draft the minimal RFC delta — the state machine, wire
contract, or data shape that is genuinely new, plus the trade-offs considered
and rejected. Reuse existing contracts by reference.
**Do** (small): one sentence: why no design delta is needed.
**Exit**: a reviewer could disagree with something specific.
**Kill / park**: no technically credible path exists — write the exploratory
RFC stub stating what would have to become true, and park.

## Gate 5 — Specification

**Input**: all prior gates; `../../../references/spec-format.md`;
existing `openspec/` tree.
**Do**:
- Extend an existing spec when the capability fits its scope; create
  `openspec/specs/{category}-{name}/spec.md` only for genuinely new
  capabilities
- Check active `openspec/changes/*/specs/` first — active changes override
  main specs; build on them, don't fork
- Write WHEN/THEN scenarios for success, error, and edge behavior (observable
  behavior only — no internal architecture)
- Write the **out of scope** list — what this request deliberately does not
  cover; this is the anti-scope-creep contract

**Exit**: every Gate 1 success criterion maps to at least one scenario; every
scenario is testable as written.
**Kill / loop**: a requirement resists WHEN/THEN phrasing — it is still a
feeling, not a behavior. Return to Gate 1 for that slice.

## Gate 6 — Engineering Bar

**Input**: Gate 5 spec delta; `about/craft-and-care/` if present.
**Do**: import the applicable standards into acceptance criteria —
- Testing: what proves each scenario (unit/integration/manual), regression
  expectations
- Observability: what gets logged/measured so the behavior is verifiable in
  production
- Review and compatibility expectations for the touched boundaries
- Migration/rollback notes when behavior changes under users

If craft-and-care is absent: state the bar you are assuming, labeled
[Inferred], so sign-off includes the quality contract and not just the
feature.

**Exit**: "done" is defined in the spec delta itself; an implementer needs no
follow-up question to know what quality means here.

## Funnel Summary Template

```
## Feature Request: {name}
Size: {small|medium|large}
- G1 Motif: {problem → motif} [evidence]
- G2 Doctrine: {aligned|conflict|inferred} — {citation}
- G3 Topology: {placement statement}
- G4 Design: {sketch ref | "not needed because…"}
- G5 Spec: {spec path(s), N scenarios, out-of-scope list}
- G6 Bar: {standards imported | assumed bar}
Open questions: {…}
Recommended handoff: {project-direction | beads-writer | park | reject}
```
