# Inventory and Classification

Step 3 of every run. Output: one mapping table in which every requirement and
every observable behavior has exactly one row and one class. Flows A and B
consume that table; audit mode reports it and stops.

## Effective spec

Build from the ledger, not by re-reading every spec first:

- Main specs: `openspec/specs/*/spec.md`.
- Active (non-archived) deltas: `openspec/changes/*/specs/*/spec.md`. Only a
  **signed** active change overrides main specs. The ledger's `governed-by:`
  marks a main requirement restated by an active `MODIFIED`/`REMOVED`:
  signed → judge code against the delta; `UNSIGNED` → judge against the main
  text (an unsigned delta is a proposal, and one drafted to match the code
  would otherwise mask the divergence). Sign-off evidence rules:
  [spec-ahead.md § 2](spec-ahead.md#2-scope-and-active-changes).
- A signed active change's `ADDED` requirement is in flight. Its row is `concrete`
  if implemented, else `spec-ahead` owned by that change — flow B checks the
  change has a plan (open `tasks.md` items or beads), it does not re-plan it.
- `post-v1` requirements are out of scope: listed, never planned.
  `v1-reserved` is `concrete` when the declared schema/stub exists.
- Requirements without IDs: classify by title; backfilling the ID is part of
  whatever bookkeeping or bead touches them (spec-format § Legacy Specs).

## Inventories

**Spec side** — per capability: requirements (ID, title, scope), scenarios
(WHEN/THEN), the governing change if any. The ledger already lists these.

**Consumers first** — list verified external consumers before judging any
surface: published package or API clients, other repositories, persisted user
data and its readers, documented integrations. Same-repo callers never count.
Each row's exposure (internal / exported / externally consumed) decides how
much latitude removal or the defect filter has later.

**Implementation side** — per capability, follow the contract into code.
Read `CLAUDE.md`/`README` and `about/lay-and-land/` first for layout. Then
enumerate the **observable surface** mechanically where possible, because
code-ahead behavior hides at surfaces nobody re-read:

| Surface | Where to look |
|---|---|
| CLI commands, flags, exit codes | arg parsers, command registries, `--help` output |
| HTTP/RPC routes, request/response fields, status codes | routers, schema/OpenAPI, handlers |
| Config keys, env vars, defaults | config loaders, schema files, `.env.example` |
| Files, events, messages emitted; persisted formats | writers, publishers, migrations, serializers |
| UI screens, actions, states (loading/empty/error) | routes/pages, components with handlers |
| Scheduled/background behavior | cron/timer registrations, workers, queues |
| Failure behavior | error mapping, retries, fallbacks, timeouts |
| Library public API | exports, public types, plugin/extension hooks |
| Outbound calls and data egress | HTTP clients, SDK calls, telemetry, webhooks — every destination and what is sent |
| Access control | permission checks, roles, auth middleware, who can trigger what |
| Limits | rate limits, quotas, size caps, timeouts a caller can hit |
| Operator surface | metrics, health/readiness endpoints, admin commands |
| Feature flags | flag registries and their defaults |
| Documented behavior | README/docs/`--help` text, changelog — documented behavior is promised behavior; documented-but-unbuilt is handled in [code-ahead.md § 1](code-ahead.md#1-pre-gate-filters-lead-before-drafting) |

Per surface item: what it does observably, `file:line`, and test evidence.
Tests are an inventory source too: a test asserting behavior no spec
mentions is a strong code-ahead signal.

Partition large repos by capability slice (one evidence owner each); a
cross-cutting worker only for an independently reviewable shared contract
(auth, error envelope, persistence format), advising slice owners rather than
re-scanning their files.

## Mapping table

Built by the lead, who holds both inventories:

| Row (surface-id) | Class | Requirement (ID / title) | Implementation (`file:line`) | Exposure | Test evidence | Evidence label | Notes |
|---|---|---|---|---|---|---|---|

Evidence labels per router invariant: [Observed] read in code/tests at the
audited SHA, [Inferred] reasoned from structure, [Unknown] not determinable.

## Classes (closed vocabulary)

| Class | Meaning | Sub-kind | Goes to |
|---|---|---|---|
| `concrete` | Requirement met in spirit; `v1-mandatory` has a test citing its ID | — | Nothing (counted) |
| `spec-ahead` | Requirement not met | `missing` (no implementation) · `partial` (some scenarios unmet) · `unverified` (implemented, no test cites the ID) · `in-flight` (owned by an active change) | Flow B |
| `code-ahead` | Observable behavior with no governing requirement, or exceeding one (extra mode, option, side effect, broader input) | — | Flow A |
| `divergent` | Requirement and behavior both exist and disagree | — | Flow B's divergence decision |
| `unknown` | Cannot be decided from repo evidence (runtime-only, external system, missing access) | — | Bounded investigation (flow B) |

Rules that keep classification honest:

- **Spirit, not wording.** A requirement is met when its observable outcome
  holds, whatever the code structure. Flag only missing capability or
  behavior that contradicts the spec.
- **Exceeding is code-ahead, not concrete.** A flag, default, or side effect
  the requirement never mentions gets its own code-ahead row even when the
  rest of the requirement is met.
- **Unverified is a gap.** Implemented-but-untested `v1-mandatory` is
  `spec-ahead/unverified`: the spec's claim is unproven, and the work (a test
  citing the ID at the behavior seam) is cheap and plannable.
- **Defects are not features.** Under a requirement, accidental behavior is
  `divergent`. Outside any, it is `code-ahead` and flow A's defect filter
  decides — relied-on accidents (documented or externally consumed) still go
  to the owner, never straight to removal.
- **Unknown is a last resort, with a target.** Name the evidence that would
  decide it (a command, an environment, a person) — never "needs
  investigation".
- **One class per row.** A requirement partially met *and* contradicted is
  `divergent`; divergence decides first, the rest follows.

## Audit-mode report

Audit mode stops here. Deliver, outcome first, in complete sentences:

1. Verdict: concrete share and the count per class, at the audited SHA.
2. The mapping table (or per-capability tables for large repos).
3. What a full run would do: bookkeeping candidates, likely owner gates,
   beads it would attach/new/close — proposals, not actions.
4. Anything [Unknown] and the evidence that would decide it.

Audit mode reports inline and writes no convergence record, so neither the
next run nor direction mistakes it for a filed plan.

No spec edits, no bead mutations, no questionnaire.
