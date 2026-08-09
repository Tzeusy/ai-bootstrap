# Launch Gate: Pre-Specification Readiness

Load for the launch-gate focus mode: a project is about to author its **first**
specifications, or a specification effort stalled and the question is whether
the layers above it ever settled. The gate answers one question with cited
evidence — *are the core goals and requirements set out well enough that
specifications can now be synthesized from them?*

A benchmark-style question series, administered to a **fresh-context reviewer**
(subagent or human) at each synthesis↔review cycle. Its verdicts are the
acceptance criteria for the "begin specifications" decision.

**Not authority.** No verdict here adopts, accepts, or approves anything on the
owner's behalf. The gate is a process instrument; the owner reads the verdicts
and decides. A `READY` verdict does not start spec work — it removes the
objection to starting it.

**Design intent.** The questions are formulated *independently of the artifacts
under judgment*, so they detect faults in that corpus rather than inherit them.
Every question is falsifiable (carries a "fails when"), every verdict cites
evidence, and everything project-specific lives in the parameter block (§7).

## Where this sits

| | |
|---|---|
| Runs after | Doctrine exists and is adopted; a shape corpus (design contracts) is drafted |
| Runs before | Phase 2 changeset synthesis authors the first spec |
| Consumes | `about/heart-and-soul/` (goal statement), `about/legends-and-lore/` (shape corpus), entry/status documents |
| Produces | A gate record (§4), a trend-log line (§5), and — when `NOT READY` — a remediation candidate list routed per §8 |
| Never produces | Specs, changesets, beads, or an owner decision |

Distinguish from siblings: `../../project-shape/` *builds* the pillars and scores
their maturity; this gate asks whether what was built is **sufficient to
specify from**. A mature-looking corpus can still fail E3. Conversely a project
with no doctrine at all does not need the gate — it needs project-shape
bootstrap, and administering a gate against absent doctrine wastes a reviewer.

## 1. Derivation tiers — how independence is kept

Every question is tagged with where it comes from:

- **[U] Universal** — any pre-specification project should pass it, whatever
  the project claims about itself. These are the bias hedge: they hold even if
  the project's own goal statement has blind spots. Ship verbatim.
- **[P] Package-derived** — follows from the shared invariants every
  th-projects-governed repo already accepts (evidence labeling; the autonomy
  contract's human decision points — see the router's *Shared invariants*).
  Ship verbatim; drop one only when the project has rejected the underlying
  invariant **on the record**, and note the drop in the gate record.
- **[G] Goal-derived** — authored per project from its *adopted goal statement*
  (doctrine/vision), which is the thing specifications must serve. Using the
  goal statement is legitimate; using the corpus under judgment is not. Write
  [G] questions during parameter binding (§7), before the administration, and
  keep them in the project's parameter block so they are stable across runs.

**No question may be derived from the artifacts under judgment.** If a question
can only be stated using the shape corpus's internal structure — its module
names, clause IDs, package boundaries — it does not belong here. A gate whose
questions were written while reading the candidate RFCs cannot detect what
those RFCs got wrong.

**Question IDs are stable forever** — never renumbered, never reused. Amend in
place or by appending; every amendment gets a changelog entry (§9). The trend
log is only meaningful across comparable questions.

## 2. Administration protocol

Give the reviewer:

1. This file.
2. The project's goal statement (doctrine/vision) and public entry document.
3. Read access to the repository at a **named commit**.
4. The project's parameter block (§7), including its [G] questions.

Withhold from the reviewer:

- Authoring history, prior review results, and prior gate administrations
  (except when answering F1, which needs the trend log).
- Any summary of "how it's going." The reviewer reads primary artifacts. The
  administering session must not narrate state — a briefed reviewer inherits
  the corpus's blind spots, which is exactly what the gate exists to avoid.

The materials list is fixed by this file plus the parameter block — never
curated per administration. Record any deviation (something added, missing, or
unreadable) in the gate record.

**Rules for the reviewer:**

- **Verdict vocabulary is closed:** `Met`, `Not met`, `Unknown(reason)`.
  Nothing else. No "partially met", no "met with caveats" — a caveat that
  matters makes it `Not met`; one that doesn't is omitted.
- **Met requires cited evidence** — file paths and quoted text. An unsupported
  Met is recorded as Unknown.
- **Not met requires a concrete counterexample** — the artifact and passage
  that fails, or the sweep (with denominator) that shows absence.
- **Unknown is a respectable answer.** No evidence means Unknown, never a
  guessed pass. State what evidence would settle it.
- **Attempt to fail every question first.** The reviewer's job is
  falsification; a question survives a genuine attempt to break it, or its
  verdict is not credible.
- **No aggregate score is the deliverable.** A summary table is fine; a single
  percentage or grade substituting for per-question verdicts is not. Rollups
  hide exactly the defects this gate exists to catch.
- **Evidence is commit-anchored.** Every citation must exist at the named
  commit; evidence quoted from any other version is void.

**Dispatch.** One reviewer subagent per administration, dispatched per
[`subagent-template.md`](subagent-template.md) with the §2 materials as its
*only* context — never the orchestrator's conversation. Alternate reviewer
model families across administrations where the environment allows; a family
that authored the corpus is the weakest available auditor of it. Split the
series across parallel reviewers only along section boundaries, and never split
D from E3 (E3 is credible only from a reviewer who has demonstrated
comprehension in D).

**Shape of a run:**

- **Order:** A → B → C → D → E → F → G. D must precede E3. Within a section,
  questions are independent.
- **Effort:** most of A–C are document-level judgments (minutes each); D1, D2,
  E3, and E4 are exercises (tens of minutes); F needs the trend log and a
  corpus sweep. A full administration should fit one focused session — if it
  cannot, that is itself evidence against D1.
- **Full vs delta:** between cycles, a delta administration (re-asking only
  questions whose evidence changed) is fine for steering. The gate *decision*
  requires a full administration at the named commit — regressions do not
  announce themselves.
- Copy the verdict words exactly into the record; never soften them. Quote
  questions verbatim at the version administered — a verdict rendered against a
  paraphrased question is void — and record every operationalization judgment
  call.

## 3. The question series

### A. Problem and vision

- **A1 [U]** Does the project name a specific, *lived* human problem — one
  whose resolution would be observable in a specific person's behavior?
  *Fails when:* the problem is a category ("agent observability") rather than
  an experience.
- **A2 [U]** Is the thesis falsifiable — does the project state what evidence
  would prove it wrong, and when that judgment gets made?
  *Fails when:* every conceivable outcome can be narrated as success, or the
  falsifier has no trigger point.
- **A3 [U]** Are the exclusion boundaries sharp enough to *reject a plausible
  near-miss* — could a reviewer, citing only the goal statement, refuse a
  product that superficially resembles the goal?
  *Fails when:* the is/is-not list only excludes strawmen nobody would build.
  *Administer concretely:* judge the pre-written `NEAR_MISSES` from the
  parameter block, accepting or rejecting each with a citation — never invent
  softer near-misses on the spot.
- **A4 [U]** Is the problem tractable as scoped: does a smallest end-to-end
  slice exist that exercises the core loop and could be built and honestly
  evaluated with bounded effort?
  *Fails when:* the first demonstrable value requires most of the system.
- **A5 [U]** Are the project's consumers enumerated, and does every major shape
  commitment trace to a named consumer's need — and every named consumer to at
  least one commitment that serves it?
  *Fails when:* a consumer exists only in rhetoric, or a shape element serves
  no one who was named.
- **A6 [U]** Is the scope achievable with the resources the project actually
  has — people, attention, money, calendar — stated rather than implied?
  *Fails when:* the shape silently assumes a team, budget, or cadence the
  project does not have.

### B. Decomposability and sequencing

- **B1 [U]** Does the shape decompose into chunks each independently
  understandable, independently acceptable-or-rejectable, and valuable before
  later chunks exist?
  *Fails when:* acceptance is practically all-or-nothing, whatever the
  packaging says.
- **B2 [U]** Is chunk ordering explicit and acyclic — does no chunk's
  acceptance silently presume an unaccepted one?
  *Fails when:* a chunk's text relies on a sibling that could still be
  rejected, with no stated fallback.
- **B3 [U]** Does the first buildable slice generate *evidence about the thesis
  itself*, not just infrastructure?
  *Fails when:* the slice proves the team can build plumbing but nothing about
  whether the product idea is right.
- **B4 [U]** Can any single chunk be rejected without collapsing the whole — is
  partial acceptance a designed state rather than an accident?
  *Fails when:* rejecting one chunk invalidates digests, references, or
  premises across the others.
- **B5 [U]** Does the sequencing retire risk early — are the assumptions most
  likely to invalidate the thesis scheduled to be tested in the earliest chunks
  that can test them?
  *Fails when:* early chunks are the comfortable ones and every
  thesis-threatening unknown lives late — or nobody can name the riskiest
  assumption at all.

### C. Authority discipline

- **C1 [U]** Does authority flow one way — doctrine → shape → specs →
  implementation — with each layer citing upward and no lower layer quietly
  redefining a higher one?
  *Fails when:* a lower artifact restates a higher rule with drifted meaning,
  or a summary is treated as the rule.
- **C2 [U]** Is every normative "should" owned by exactly one artifact, with
  conflicts between artifacts resolved by rule rather than by reading order?
  *Fails when:* two artifacts answer the same question and a reader must guess
  which wins; or a rule lives only inside a validator, index, or generated
  report.
  *Scope note:* C2 asks whether exactly one owner **exists** (ownership); D2
  asks whether a reader can **find** it (routing). Evidence for one is not
  evidence for the other.
- **C3 [P]** Does the project apply its own epistemics *to itself* — are claims
  about its own state evidence-backed and labeled ([Observed] / [Inferred] /
  [Unknown]), with absence of evidence rendered as unknown, never as done?
  *Fails when:* a status document claims green/zero/complete without a sweep
  run against the current bytes.
- **C4 [P]** Are the human decision points enumerated and non-delegable — can a
  reader determine *from artifacts alone* whether any given decision was
  actually made by a human?
  *Fails when:* an agent-authored artifact could pass as an owner act, or a
  pending decision is indistinguishable from a made one.
- **C5 [U]** Does the shape separate what the project controls from what it
  assumes of its substrate — external tools, formats, platforms — with each
  load-bearing assumption recorded alongside a stated posture if it breaks?
  *Fails when:* an external dependency is treated as guaranteed, or its failure
  would reshape the project and no artifact admits that.
- **C6 [U]** Does required authority scale with irreversibility — are
  hard-to-undo or externally visible actions gated more strongly than routine,
  revertable ones?
  *Fails when:* one approval level covers everything, or an irreversible effect
  is reachable through a routine path.

### D. Comprehensibility

- **D1 [U]** Fresh-engineer test: can a capable engineer with no prior contact
  state the problem, thesis, current lifecycle stage, and next pending decision
  after bounded reading (≤ 60 min)?
  *Fails when:* correctness requires archaeology — reading history, resolving
  contradictory metadata, or knowing which documents are stale.
- **D2 [U]** Task-routing test: from the front door, can they reach the
  *single* rule governing one concrete task without exhaustive reading?
  *Administer concretely:* use the tasks fixed in the parameter block
  (`D2_ROUTINE_TASK`, `D2_AUTHORITY_TASK`, `D2_SEAM_TASK`), chosen before the
  administration — never by the reviewer or the administering session mid-run.
  At least one task must cross a seam between two chunks.
  *Fails when:* the route requires reading the corpus, or two routes give two
  answers.
- **D3 [U]** Is invented vocabulary minimal and defined-before-use — does each
  coined term buy clarity ordinary language couldn't?
  *Fails when:* the default reading path uses a term before defining it, or a
  coined term shadows an ordinary word's meaning.
- **D4 [U]** Do the entry/summary documents make no claim their sources don't —
  is simplification confined to presentation, never meaning?
  *Fails when:* an overview asserts something stronger, softer, or fresher than
  its owning source.

### E. Readiness to author specifications — the gate itself

- **E1 [U]** Is it defined what a specification *is* here — form, home,
  granularity, acceptance authority, and change process — before the first one
  is written?
  *Fails when:* the first spec author would have to invent the medium while
  writing the message.
  *Record sub-verdicts:* form, home, granularity, acceptance authority, change
  process — five answers, not one. E1 is Met only when all five are.
  *Default binding:* a th-projects repo answers form/home/change-process with
  [`references/spec-format.md`](../../../references/spec-format.md) and
  `openspec/`; granularity and acceptance authority are still project answers.
- **E2 [U]** Is the first specification identified, with every prerequisite
  either satisfied or explicitly waived on the record?
  *Fails when:* "what comes first" is answered differently by different
  documents, or prerequisites are discovered rather than listed.
- **E3 [U]** Would authoring the first spec force reopening any doctrine- or
  shape-level question? Enumerate them.
  *The sharpest single gate:* hand the reviewer the shape corpus and the first
  spec's charter, and ask what they would have to reopen. An empty list —
  genuinely arrived at, not asserted — is the readiness signal.
  *Fails when:* the list is non-empty; "ready" is then false regardless of
  every other verdict.
  *Credibility protocol:* the reviewer first enumerates the first spec's
  central concepts and obligations, then traces each to the shape artifact that
  would govern it. An empty reopen-list **without this trace table** is
  recorded as Unknown, not Met — a shallow reading also produces an empty list.
- **E4 [U]** Is the shape/spec boundary crisp enough that an author knows which
  side any given sentence falls on — without asking?
  *Administer concretely:* the reviewer classifies the five pre-written
  `E4_CANDIDATES` from the parameter block; disagreement with the project's own
  routing is a fail. Candidates are written before the administration, like
  `NEAR_MISSES` — a reviewer who picks their own examples picks easy ones.
- **E5 [U]** Do acceptance criteria exist for a spec itself — how one will be
  judged complete, testable, and faithful to the shape above it?
  *Fails when:* spec acceptance would be a vibe check by whoever reviews it.
- **E6 [U]** Is there a defined propagation path for a shape change *after*
  specs exist — how affected specs are detected, who amends them, and how the
  interim disagreement is surfaced rather than hidden?
  *Fails when:* the first post-spec shape amendment would create silent
  contradictions between layers.
  *Default binding:* th-projects answers this with per-change spec sync
  (feature-request amendment mode) plus episodic reconciliation as backstop;
  Met still requires the project to have adopted it, not merely inherited it.

### F. Process health and convergence

- **F1 [U]** Is the improvement cycle *converging* — are successive review
  rounds finding fewer and less severe defects, with a declared stop condition
  other than exhaustion?
  *Requires the trend log (§5).*
  *Fails when:* each round's fixes mint the next round's findings, or no one
  can state what would end the cycle.
- **F2 [U]** Is the governance corpus proportionate to what it protects — does
  each artifact have an owner and a retirement path, and does repairing a
  defect not routinely create new artifacts?
  *Fails when:* the corpus grows monotonically; defect → new report → new
  validator → new defect.
  *Operational proxies:* artifact-count trend across cycles; the ratio of
  normative artifacts to meta-artifacts (reports, validators, indexes) — meta
  should not outgrow normative; a sweep for artifacts no reading route reaches.
- **F3 [U]** Can the owner make each acceptance decision from a bounded packet
  in one sitting, without archaeology?
  *Fails when:* the honest answer to "what am I binding?" requires reading
  history or trusting a summary the packet itself calls non-authoritative.
- **F4 [U]** If all improvement stopped today, would the corpus be safe to
  abandon — no artifact left misstating the current state to a future reader?
  *Fails when:* any stale claim, superseded offering, or dead route is
  reachable from a default reading path without a banner.

### G. Gate self-scrutiny

- **G1 [U]** Completeness critic — the reviewer answers: *what readiness
  dimension could this project fail that no question above would catch?*
  Proposed missing questions go into the record and are considered for
  amendment of this instrument (§9).
  *G1 yields no Met/Not-met verdict; an administration that skips it is
  incomplete and cannot support a gate decision.*

### [G] questions

Append the project's goal-derived questions here in the record, numbered from
`G1`'s successors in a project-local namespace (`P1`, `P2`, …) so they never
collide with this file's IDs. Each needs the same shape as above: a claim, a
"fails when", and a citation to the doctrine clause it derives from.

## 4. Verdict computation and record

The launch-gate rule:

> **Ready to begin specifications** = every E question `Met`, **and** no
> `Not met` anywhere in A–D, **and** F1 not diverging.

Qualifications:

- `Unknown` in A–D does not block by itself, but each must carry what evidence
  would settle it; unsettled Unknowns accumulate as owner risk, stated in the
  record.
- F is a health gauge with veto power: a diverging F1 makes any "ready" claim
  premature regardless of E, because the E verdicts are then unstable.
- The gate can be *passed with enumerated deferrals* only by explicit owner
  decision — never by the reviewer or the administering session.
- G1 yields no verdict and never blocks, but an administration missing G1 is
  incomplete and cannot support a gate decision.

One record per administration, written to
`docs/launch-gate/YYYY-MM-DD-<short-sha>.md` (same convention as review packets
under `docs/reviews/`). Store it verbatim; never edit a past administration —
supersede it.

```markdown
# Launch-gate administration — {date}, commit {sha}
Reviewer: {model/version, fresh context: yes/no}
Reviewer model family: {alternate families across administrations where possible}
Materials given: {list, with deviations from the fixed list called out}
Operationalization notes: {every judgment call made interpreting a question}
Tier drops: {any [P] question dropped + the on-record rejection that justifies it}

| Q | Verdict | Evidence / counterexample (paths + quotes) |
|---|---------|--------------------------------------------|
| A1 | Met | ... |

E1 sub-verdicts: form / home / granularity / acceptance authority / change process
E3 reopen-list: {empty | enumerated items} + trace table
Unknowns and what would settle them: {list}
Reviewer's falsification notes: {what they tried to break and couldn't}
G1 proposed missing questions: {list | none}
Gate verdict per §4: READY / NOT READY / READY-WITH-DEFERRALS (owner only)
```

## 5. Trend log

Append one line per administration to `docs/launch-gate/trend.md`; this is F1's
evidence.

```markdown
| Date | Commit | Not-met | Unknown | Deferred | Reopened | New findings vs prior | Gate verdict |
|------|--------|---------|---------|----------|----------|-----------------------|--------------|
```

Convergence means the Not-met and new-findings columns trend to zero across
administrations *without the questions being weakened*. If a question is ever
amended, note it here — a trend across different questions is not a trend.

A deferral is a finding until resolved: moving a finding from Not-met to
Deferred must never improve the read of any other column. Reopened counts
findings previously recorded resolved that recurred — a nonzero Reopened column
indicts the resolution process, not just the finding.

## 6. Relationship to reconciliation tiers

The gate is **not** a reconciliation pass and does not consume the pass budget
in the SKILL's reconciliation protocol:

- The gate record is evidence, not a normative artifact — its own falsification
  protocol is the review, so no reconciliation tier applies on top of it.
- The **parameter block is durable and project-owned**: authoring or amending
  it is change-tier, small (one pass + confirming pass). Parameters written
  loosely are the cheapest way to game the gate.
- Doctrine or shape edits prompted by findings are change-tier under their
  owning subskill, not here.
- The gate's cycle has its own stop condition (F1 convergence + the §4 rule);
  the 6-pass convergence ceiling does not apply to it. Successive `NOT READY`
  administrations with no movement are an F1 finding to bring to the owner, not
  a reason to keep re-administering.

## 7. Parameter block

Bind once per project; store it with the project (alongside the trend log) so
administrations are comparable. Defaults below assume the five-pillar canon;
substitute the `.syzygy` canon paths where `../../project-shape/` detected it.

| Parameter | Fill with | Five-pillar default |
|---|---|---|
| `PROJECT` | Name | — |
| `GOAL_STATEMENT` | Adopted doctrine — the thing specs must serve | `about/heart-and-soul/` |
| `ENTRY_DOCUMENT` | Public front door (presentation, never authority) | `README.md` |
| `CURRENT_STATE` | Where lifecycle stage lives | `PROJECT-STATUS.md` or equivalent |
| `SHAPE_CORPUS` | Design contracts under judgment — **readable for answering, withheld from question derivation** | `about/legends-and-lore/` |
| `SPEC_MEDIUM` | Form + home of a spec (absent pre-gate is correct) | `openspec/` per `references/spec-format.md` |
| `FIRST_SPEC_CANDIDATE` | The first spec's charter at the administered commit | — |
| `HUMAN_DECIDER` | Who performs owner acts, and the delegation rule | owner; router autonomy contract |
| `EPISTEMIC_LABELS` | The project's evidence vocabulary | [Observed] / [Inferred] / [Unknown] |
| `THESIS_CHECKPOINTS` | Evidence that would falsify the lived product thesis, and the lifecycle point when each judgment occurs (A2) | — |
| `RESOURCE_ENVELOPE` | Actually committed people, attention, money, and calendar; unknowns stay explicit, with a stop condition before work assumes them (A6) | — |
| `D2_ROUTINE_TASK` | A concrete low-authority task | — |
| `D2_AUTHORITY_TASK` | A task that changes a normative definition | — |
| `D2_SEAM_TASK` | A task crossing two chunks' boundary | — |
| `NEAR_MISSES` (A3) | 3 plausible products a careless reader could mistake for the goal | — |
| `E4_CANDIDATES` (E4) | 5 candidate requirements spanning clear-shape, clear-spec, and genuinely borderline | — |
| `[G]` questions | Goal-derived questions authored from doctrine (§1) | — |

Write `NEAR_MISSES` and `E4_CANDIDATES` to be *hard*: a near-miss nobody would
build and a candidate requirement nobody would misfile turn A3 and E4 into free
passes. Both are authored before the administration and are never changed to
suit a verdict — changing them is an amendment, logged in §9 and flagged in the
trend log.

## 8. Acting on the verdict

- **READY** → proceed to Phase 2 changeset synthesis for `FIRST_SPEC_CANDIDATE`.
  Record the gate record path and its commit SHA in the changeset handoff, the
  way a review packet's SHA is recorded — a spec authored long after a stale
  gate is unbacked.
- **NOT READY** → the `Not met` list becomes the candidate set, routed by
  class, never fixed inline here:
  - doctrine defect or missing mandate (A, C1, C3, C4) →
    `../../project-shape/references/doctrine-amendment.md`;
  - missing or contradictory design contract (B, C5, C6, E2, E3) →
    `../../project-feature-request/` funnel, or an RFC in the lore pillar;
  - comprehensibility or corpus-hygiene defect (D, F2, F4) →
    `../../project-shape/` (routing, staleness) — often the cheapest wins;
  - missing spec machinery (E1, E5, E6) → adopt the defaults above explicitly,
    or author the project's own answer.
  Rank the candidates the way milestone synthesis ranks its own
  ([`milestone-synthesis.md`](milestone-synthesis.md)) and present a
  remediation brief; the owner picks. Then re-administer at a new commit.
- **READY-WITH-DEFERRALS** → owner act only. Each deferral is enumerated in the
  record, stays a finding in the trend log, and is re-asked at the next
  administration.

## 9. Amending this instrument

The [U] questions and the §2/§4 protocol are the invariant; everything
project-specific lives in the parameter block. If a project cannot be assessed
without editing a [U] question, that is a finding **about the question** —
amend here and log it, never fork per project.

- **v1.0** (2026-08-09) — synthesized from Syzygy's
  `launch-gate-pre-specifications.md` v1.3. Generalized the [G]/[U] split into
  [U]/[P]/[G] (package-derived tier grounded in the th-projects shared
  invariants, making C3/C4 portable); replaced the Syzygy binding with a
  parameter-block template plus five-pillar defaults; added `E4_CANDIDATES` to
  the parameter block, closing the same anti-gaming hole `NEAR_MISSES` and the
  D2 tasks already closed; added default bindings for E1/E6; added the
  reconciliation-tier relationship (§6), verdict routing (§8), and record/trend
  homes under `docs/launch-gate/`. The source's three-skill generalization path
  (author / administer / trend) is deliberately collapsed into one focus mode:
  binding, administering, and reading the trend are phases of a single run, and
  three catalog entries would fragment one decision across three routing hops.
- **v1.1** (2026-08-10) — added required `THESIS_CHECKPOINTS` and
  `RESOURCE_ENVELOPE` bindings. A2 and A6 already required those facts, but the
  v1.0 parameter template did not force projects to supply them. The question
  series and verdict computation are unchanged.
