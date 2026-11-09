# Flow A — Code Ahead of Spec

Input: the `code-ahead` rows from the mapping table. Output: each row landed
as `[Observed]` bookkeeping, attached to the bead that already owns it, filed
as a defect, recorded as immaterial, or carried to the owner dossier — never
silently dropped, never silently specified.

The failure this flow prevents: an agent reads the code, writes a spec that
describes it, and calls the project reconciled. That makes every accident,
shortcut, and scope creep normative. Shipped behavior proves what exists;
only doctrine says what should.

Every row carries a deterministic **surface-id**, reused as its audit-key and
decision-ID slug so re-runs dedupe: `cli:<cmd>--<flag>`,
`http:<METHOD>:<route>`, `config:<key>`, `env:<VAR>`, `event:<name>`,
`file:<artifact>`, `ui:<route>#<action>`, `api:<module>.<symbol>`,
`net:<destination>`, `job:<name>`, `flag:<name>`, or a seam slug
(`seam:<module>`) for requirement-backed work — no spaces, so the key survives as one token.

## 1. Pre-gate filters (lead, before drafting)

Take each row through these in order; the first that matches decides it.

| Filter | Test | Outcome |
|---|---|---|
| Internal | Not observable by any user, operator, or consumer | Not a row. Over-complexity there is `/th-engineering` greenfield-parity's |
| In flight | A signed active change's `ADDED` requirement covers it | Reclassify `concrete` or `spec-ahead/in-flight` |
| Owned | A live bead adds, changes, or removes this behavior (any audit-key — `greenfield:` included — or a text match in the ledger's live lists) | `bd update <id> --append-notes "<date> spec-concretization @<sha>: code-ahead <surface-id> at <file:line>; spec sync owed"`; no draft. That bead's per-change spec sync owns it |
| Restates | The existing SHALL sentence already entails the behavior: no new input, mode, option, output, default, or side effect | Reclassify `concrete`. A missing scenario for it lands as an ambiguity clarification without the gate. Anything more is *exceeding*: draft and gate it |
| Defect | Accidental **and** unrelied-on: crash, hang, data loss, security exposure, or leaked internals with no verified external consumer and no documentation describing it | Flow B defect bead (`Audit-key: spec:defect:<capability>:<surface-id>`). Accidental but documented or externally consumed → draft and gate; removing relied-on behavior is the owner's call |
| Immaterial | Not documented, not tested, no verified external consumer, and nothing a consumer could reasonably depend on (log wording, debug output, incidental ordering) | Report line only. When in doubt it is material |

Special shapes, decided before drafting:

- **Flags and defaults.** Specify what a fresh install gets: the shipped
  default (code default, or the packaged config when one ships). A knob is
  its own requirement only when documented or operator-facing; otherwise it
  is a scenario of the behavior it tunes. Flag-gated behavior that is off by
  default is unreleased work: route it through its owning bead, or raise
  `concretize:adopt:<capability>/flag:<name>` — never bookkeep it as SHALL.
  Deployment overrides (helm values, prod env) are operations, not spec;
  [Unknown] when only runtime shows them.
- **Deprecated behavior** (warning emitted, marked deprecated in docs or
  code) is never drafted as an unqualified SHALL. With a verified external
  consumer: draft it with a scenario for the deprecation signal, and propose
  a deprecation bead (consumer, migration) plus a dated removal bead under
  `concretize:deprecate:<capability>/<surface-id>`. No consumer: owner item
  recommending removal.
- **Documented, not implemented, not specified** is not code-ahead: file a
  docs-correction bead (`spec:docs:<capability>:<surface-id>`), or route to
  `../project-feature-request/` if the doc records wanted intent. Never draft
  a requirement from docs alone; docs that contradict unspecified code go
  into that draft's evidence.

Everything left is a draft candidate.

## 2. Draft

Write each candidate as a requirement block exactly per
[`spec-format.md`](../../../references/spec-format.md): normative SHALL/MUST
paragraph, then `ID`, `Source`, `Scope`, then scenarios.

- **Facts, not framing.** The normative paragraph states behavior only — no
  purpose or benefit language ("for reliability", "to help users"). The
  drafter has read the code and will rationalize it; framing is how that
  leaks past an un-anchored gate.
- **Effects list.** Each draft carries a scratch-only `Effects:` list:
  inputs read, outputs, persisted state, network destinations, data leaving
  the process, defaults, who can trigger it. The gate judges the Effects
  list; an omitted effect found later sends the draft back for rewrite.
- **Contract, not transcript.** Specify what a consumer relies on, at the
  level of the surrounding spec. Exact log text, internal ordering, and
  incidental defaults freeze accidents into contract; leave them out unless
  a consumer depends on them.
- **Scenarios from evidence.** Derive WHEN/THEN from the code path and the
  tests that exercise it, including the failure behavior the code actually
  implements. A scenario you cannot point at code for is invention — drop it.
- **Semantic gate.** Run spec-format § Semantic Quality Gate. Each applicable
  risk dimension the code does not handle (failure, authorization,
  concurrency, limits…) is recorded as `N/A — <reason>` or filed as a defect
  or owner item — never invented, never silently dropped.
- **Group by capability.** Several flags of one command are usually one
  requirement with several scenarios, not several requirements.
- `ID`: next free number across main and active deltas for that capability.
  `Source: [Observed] <path>:<line>` (the gate adds the doctrine reference).
  `Scope: pending` until the gate decides.
- New capability (no main spec fits) → draft a 1-3 sentence `Purpose` too.

Drafts live in the run's scratch report until landed; they are not written
to `openspec/` before the gate.

## 3. Vision gate (fresh-context reviewer)

One subagent per run, all drafts batched, at the lead's model tier. The lead
read the code and is anchored on it; the reviewer must not be. Brief:

- **Read:** `about/heart-and-soul/` (vision, non-goals, v1 scope), relevant
  `about/legends-and-lore/` decisions and the ideas ledger, owner decisions
  the lead found in bead notes or decision records that requested this
  behavior, and the drafts with their Effects lists.
- **Do not read** implementation, tests, or the mapping table. Judge what the
  behavior *is*, from the draft text alone.
- **Per draft, return:** verdict, the cited doctrine (file + rule/section),
  one-sentence reasoning naming the clause fulfilled or violated, and a scope
  recommendation. Report every draft; a clean `serves` still needs its
  citation.

| Verdict | Meaning | Citation required |
|---|---|---|
| `serves` | A direct instance of a specific mandate, success criterion, ship item, or recorded owner decision. Support needing an inference step ("improves UX; vision values UX") is not `serves` | The clause fulfilled |
| `neutral` | No mandate supports it; nothing forbids it. A parked idea in the ideas ledger is `neutral`, citing the park record | The doctrine sections checked |
| `conflicts` | Contradicts a principle, non-goal, rejected idea, or scope boundary. Wins over `serves` when both apply | The rule violated |

The lead may contest an upgrade (`neutral`/`conflicts` → `serves`) only with
a contrary doctrine citation; the contested row becomes an owner item, never
an override. A downgrade needs no contest — it is already an owner item.
Draft-quality issues the reviewer raises (framing, missing effect,
implementation-shaped) are fixed and re-gated before landing.

No subagent facility → nothing lands: every draft becomes a
`concretize:adopt` owner item marked "vision gate not run".

## 4. Land

| Verdict | Action | Authority |
|---|---|---|
| `serves` | Write as main-spec bookkeeping | Agent (router autonomy table: [Observed] bookkeeping that serves cited doctrine) |
| `neutral` | Owner item: adopt or remove | Owner |
| `conflicts` | Owner item: remove or amend doctrine | Owner |

Bookkeeping mechanics:

- Extend the capability's main spec; create
  `openspec/specs/<capability>/spec.md` (with `Purpose`) only when no spec
  fits.
- An active `MODIFIED`/`REMOVED` delta restates the requirement → never edit
  the delta (signed text is the owner's; unsigned text is a proposal in
  someone's funnel). Land the bookkeeping in the main spec and add a
  `tasks.md` item or bead note telling that change to carry the scenario,
  and report it.
- `Source: [Observed] <path>:<line> — serves <doctrine ref>` (one line).
- `Scope` follows the mandate's horizon, not the fact the code exists: v1
  mandate, or a mandate with no stated horizon → `v1-mandatory`. Shipped
  behavior serving only a later-horizon mandate is "ahead of horizon" —
  `post-v1` means not currently delivered (spec-format), so it is an owner
  item `concretize:horizon:<capability>/<surface-id>`: pull forward as
  `v1-mandatory` / keep as `post-v1`, unverified / remove. An implemented
  `post-v1` requirement found in the specs gets the same item.
- A new scenario under an existing requirement keeps that requirement's ID.
  Backfilling a legacy ID-less requirement follows the same Scope rule; if no
  mandate decides it, carry it in an owner item.
- Re-run `spec-trace-check.py` in default mode (`--authoring` fails on
  legacy specs): the touched files gain no new errors or warnings.
- Verification path: if an existing test already asserts the scenario, add
  the `Spec: REQ-…` citation to it in the same bookkeeping change. Otherwise
  the landed `v1-mandatory` requirement becomes a `spec-ahead/unverified`
  row for flow B, so bookkeeping always ends with a test path.

## 5. Owner items

Carried to the closeout dossier ([closeout.md](closeout.md#owner-dossier)).
Batch only when one answer applies to every member (all neutral flags of one
command, adopted or removed together). Each item carries the draft text and
Effects list, the reviewer's verdict and citation, the exposure and
consumers, and `file:line`. Decision IDs use the row's surface-id.

| Gate | Options (recommended first, by rule below) | Decision ID |
|---|---|---|
| `neutral` behavior | Adopt as observed spec at scope X / remove the behavior / defer (stays reported) | `concretize:adopt:<capability>/<surface-id>` |
| `conflicts` behavior | Remove the behavior / amend doctrine to admit it (`../project-shape/references/doctrine-amendment.md`) / keep under a dated removal for a named consumer | `concretize:conflict:<capability>/<surface-id>` |
| Ahead of horizon | Pull forward / keep post-v1 unverified / remove | `concretize:horizon:<capability>/<surface-id>` |
| Deprecated with consumer | Deprecation pair at proposed date / shorter date / remove now | `concretize:deprecate:<capability>/<surface-id>` |
| Contested upgrade | The reviewer's verdict / the lead's, each with citation | `concretize:verdict:<capability>/<surface-id>` |

Recommendation rule: adopt neutral behavior that is documented, tested, or
externally consumed, cheap to keep, and consistent with doctrine's spirit;
recommend removal when it adds surface or maintenance with no consumer, or
is half-built. For conflicts, removal is the default — doctrine wins unless
the owner amends it.

After the answer: adopt → bookkeeping per step 4 (the decision is the
`serves` citation); remove → a `spec:remove:<capability>:<surface-id>` flow
B bead (plus a `REMOVED` delta if any spec mentions it); amend doctrine →
project-shape's amendment path, then re-gate.

## No doctrine

Without `about/heart-and-soul/`, the gate judges against the project's
stated purpose with every verdict labeled [Inferred] — only the README's
purpose/goal statement and explicit non-goals, never its feature, usage, or
reference sections, which describe the code under review and would make
every behavior serve itself. `serves [Inferred]` needs a purpose sentence
the behavior directly instances; otherwise `neutral`. The report says the
gate ran in lite mode and recommends `../project-shape/` — it never invents
doctrine to judge against.
