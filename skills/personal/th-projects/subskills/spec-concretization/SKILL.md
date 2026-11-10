---
name: spec-concretization
description: >
  Use when specs and implementation must be fully reconciled in both
  directions — code doing things no spec describes, specs requiring things the
  code doesn't do yet, or the two disagreeing — and the result must land as
  vision-gated spec updates plus a complete, backlog-deduplicated work plan.
  Also the read-only audit form ("does code match the spec?"), and re-runs
  that must not duplicate prior findings. Triggers: "reconcile spec vs
  implementation", "does code match the spec", "what's implemented but
  undocumented", "what's specified but not built", "the code is ahead of the
  spec", "plan the work to finish the spec", "concretize the specs".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Opus 5.5
  status: active
  last_reviewed: "2026-11-09"
compatibility: The ledger script needs uv and Python 3.10+; the backlog side needs the bd CLI in a Beads-backed repo (otherwise --no-beads and report-only planning). Owner gates use sibling user-questionnaire scripts and a subagent facility.
---

# Spec Concretization

Spec and code are two views of one system. They are **concrete** when every
observable behavior is governed by a requirement and every in-scope
requirement is implemented, verified by a test citing its ID, or owned by
exactly one planned bead. A run closes the distance in both directions:

- **Code ahead of spec** → draft the missing requirements, then judge each
  against doctrine before it may enter the spec. Shipped behavior is evidence
  of what exists, not authority for what should.
- **Spec ahead of code** → reconcile every unmet requirement against the
  outstanding backlog first, then plan all remaining work to close the gap.

Exhaustive by design — every spec, both directions, no sampling — and a
backstop to per-change spec sync (router invariant), never a substitute.

## Use / Do Not Use

| Ask | Route |
|---|---|
| An imperative to reconcile, concretize, or plan; after a milestone; before a release | This skill, **full mode** |
| "Does the code match the spec?" — a question, no ask to act | This skill, **audit mode** (stops at the report) |
| One spec found wrong mid-implementation | `../project-feature-request/` amendment mode |
| Concretize *one* idea or request into a spec | `../project-feature-request/` |
| One already-confirmed drift; what to build next | `../project-direction/` |
| Repo health scoring; internal over-complexity ("over-engineered?") | `../project-review/`; `/th-engineering` greenfield-parity |

## Core Rules

1. **Mechanical before semantic.** `spec-trace-check.py` and the ledger run
   before any agent judges coverage; structural spec errors are fixed or
   listed first, because a broken ID breaks every join after it.
2. **Effective spec = main specs + signed active deltas.** A signed change
   overrides main specs and owns its own plan: its unmet requirements are
   checked for a plan, not re-planned; behavior it adds is in flight, not
   code-ahead. An unsigned delta is a proposal — listed, never governing,
   never planned from.
3. **Judge observable behavior, by spirit.** Internal structure, private APIs,
   and module shape are not spec rows; complexity there goes to
   greenfield-parity. One row per would-be requirement, never per function.
4. **Closed classification.** Each row is `concrete`, `spec-ahead`,
   `code-ahead`, `divergent`, or `unknown`
   ([inventory-and-classification.md](references/inventory-and-classification.md)).
5. **Divergence defaults to the spec.** Spec is source of truth; code that
   disagrees is a defect planned as spec-ahead work, unless named evidence
   shows the spec is wrong — then an amendment the owner signs. Never edit a
   spec to match code on your own authority; that launders drift into truth.
6. **Draft, then judge un-anchored.** Code-ahead drafts are judged against
   doctrine by a fresh-context reviewer given doctrine and drafts only, never
   the code: whoever read the code rationalizes it
   ([code-ahead.md](references/code-ahead.md)).
7. **Only `serves` enters the spec unasked.** Behavior serving a cited
   mandate becomes `[Observed]` main-spec bookkeeping. Doctrine-neutral or
   conflicting behavior is an owner gate: adopting or removing it changes
   committed scope either way.
8. **Reconcile before you create.** Every row matches the ledger (live and
   recently closed beads, active changes) first: code-ahead behavior a live
   bead already owns gets a note, not a draft; every spec-ahead row and every
   spec-linked bead takes exactly one reconciliation state
   ([spec-ahead.md § 3](references/spec-ahead.md#3-reconcile-against-the-ledger)).
   `new` is the last resort.
9. **Plan all of it.** Every in-scope spec-ahead requirement ID ends with
   exactly one owning bead or a named exclusion with its authority. Cohesive
   beads per the [work-allocation contract](../../references/work-allocation.md),
   never one per row.
10. **Convergence is done.** Re-running on the same head changes nothing; on
    the remediated head it files nothing new
    ([closeout.md](references/closeout.md)).

## Workflow

1. **Baseline.** Run project-shape's scanner
   (`bash ../project-shape/scripts/shape-scan.sh <repo>`); read doctrine
   (`about/heart-and-soul/`) and topology. No `openspec/` → stop and route to
   project-shape. No requirements in `openspec/specs/` and no signed change →
   this run would author the project's first specs: pass direction's
   [launch gate](../project-direction/references/launch-gate.md) first
   (READY → continue with an empty spec side; NOT READY → stop with its
   brief). Unsigned changes alone are proposals awaiting sign-off — report
   them for `../project-feature-request/` sign-off; they never count as the
   spec side. No doctrine → flow A runs in lite mode
   ([code-ahead.md § No doctrine](references/code-ahead.md#no-doctrine)).
2. **Mechanical pass.**
   ```bash
   uv run <th-projects>/scripts/spec-trace-check.py <repo> > "$SCRATCH/trace.txt" 2>&1; tail -n 30 "$SCRATCH/trace.txt"
   uv run <this-skill>/scripts/concretization-ledger.py <repo> > "$SCRATCH/ledger.md" || echo "ledger exit $?"
   ```
   Read `## Summary` first, then grep per slice
   (`rg '^REQ-<capability>-' "$SCRATCH/ledger.md"`); never load the whole
   ledger into a dispatch prompt. The ledger joins every requirement (scope, test citation, active-change
   governance) to the beads citing it, and lists orphan, spec-linked, and
   other live beads plus the last convergence record. It is the
   "already known" input for every later step.
3. **Inventory and classify** both sides; build the mapping table.
4. **Flow A — code ahead:** extract, draft, vision-gate, land or gate.
5. **Flow B — spec ahead** (includes divergent rows the spec wins): reconcile
   against the ledger, then plan all remaining work.
6. **Close out:** report, convergence record, owner dossier.

Audit mode stops after step 3 with the classified report and the actions a
full run would take; no spec edits, no bead mutations. A direct owner
instruction narrows either mode.

## Delegation

Cache-first: the lead does mapping, classification, and planning in one warm
session. Subagents pay only for:

- **Independence** — the vision gate reviewer (one per run, all drafts
  batched, lead's model tier) and the questionnaire's adversarial reviewer.
- **Context isolation** — inventory workers when spec + source reading would
  not fit the lead's context: partition by capability slice, one evidence
  owner per slice, lowest tier that reads code reliably, at most four at
  once (fewer if fewer slots). They return inventories, never verdicts.

Dispatch prompts carry the slice, its grepped ledger lines, and the output
contract (one per-surface item as in
[inventory-and-classification.md § Inventories](references/inventory-and-classification.md#inventories));
workers fetch files themselves.

## Stops

- Spec edits only as `[Observed]` main-spec bookkeeping for `serves` rows,
  or pure ambiguity clarifications that change no behavior. Delta specs are
  never edited by this skill. Everything else that
  changes a spec, doctrine, or committed scope waits on the owner.
- No implementation. The deliverable is specs, a backlog, and a report.
- A bead `in_progress` or assigned to anyone but this run's explicit actor
  gets a note, never a status, acceptance, or ownership change. Closing a
  bead follows the delivery model's closure rule, not "the requirement looks
  met" ([spec-ahead.md § 3](references/spec-ahead.md#3-reconcile-against-the-ledger)).
- Architecture, trust-boundary, migration, or concurrency-model gaps not
  already in a design contract go to `../project-direction/` as a handoff,
  not beads; sequencing questions are handed off after the beads are filed.
- Ledger script exits 2 (no `bd`, unreadable source) → fix the environment
  or rerun `--no-beads` and say flow B ran report-only. Never guess the
  backlog.

## Read Order

| File | Read when | Content |
|---|---|---|
| [`references/inventory-and-classification.md`](references/inventory-and-classification.md) | Step 3, every run | Effective spec, both inventories, observable-surface checklist, mapping table, classification rules, audit-mode report |
| [`references/code-ahead.md`](references/code-ahead.md) | Flow A | Extraction rules, draft format, pre-gate filters, vision gate brief + verdicts, landing outcomes, owner item shapes |
| [`references/spec-ahead.md`](references/spec-ahead.md) | Flow B and divergent rows | Divergence decision, ledger reconciliation states, coverage matrix, work-graph construction, ordering, bead packet, escalation |
| [`references/closeout.md`](references/closeout.md) | Step 6 | Audit-key, report template, convergence record, owner dossier, re-run semantics |
| [`../../references/spec-format.md`](../../references/spec-format.md) | Writing any requirement | Main vs delta specs, ID/Source/Scope, WHEN/THEN, semantic quality gate |
| [`../../references/work-allocation.md`](../../references/work-allocation.md) | Flow B planning | Cohesive beads, packet contents, ownership, discovery triage |

[`scripts/concretization-ledger.py`](scripts/concretization-ledger.py)
`<repo> [--tests-dir DIR] [--beads-json FILE | --no-beads] [--json]` — run in
step 2 and again at closeout to confirm the plan. Self-tests:
`uv run --with pytest pytest -q tests/` from this directory.

## Trigger Sanity Check

- Should trigger: "Reconcile the specs against the code and plan whatever's missing."
- Should trigger: "The code has grown features the spec never mentions — get the specs current."
- Should trigger: "Does the implementation actually match openspec?" (audit mode)
- Should not trigger: "This requirement is wrong, I'm mid-implementation." (feature-request amendment)
- Should not trigger: "Is this module over-engineered for its spec?" (greenfield-parity)
