# Suite Discipline

Load this when auditing or (re)structuring a test suite — tiers, network
policy, run discipline, growth control, condensation. Judging or writing
individual tests needs only `SKILL.md`; do not load this file for one test.

## Why This Exists

LLM-driven development inflates suites by mechanism, not malice:

- Green tests are the agent's proof-of-work; every harness incentive is
  additive (regression test per bugfix, test-first), none subtractive.
- Sessions see the diff, not the suite: tests get written per-function at
  the granularity of the code just touched, duplicating behavior-level
  coverage that already exists.
- Agents scaffold by cloning a neighboring test file, inheriting and
  multiplying its fixtures.
- Runtime cost grows seconds per session; no single session feels it.

Observed cadence on a heavily LLM-developed suite: test count roughly
doubles between maintenance passes, yet only ~15% proves safely
removable — most growth is real coverage. Prevention is therefore
write-time granularity control plus a scheduled condensation pass, not
mass deletion.

## Tiers

Every test maps to exactly one tier; a test that fits none is a finding.

| Tier | Scope | Network | Budget |
|---|---|---|---|
| **Unit** | One function/module through its public interface | None — no sockets, no live services | ms each; whole tier runs in seconds |
| **Component** | One component's functionality end-to-end | Allowed; live dev server or local substitute | Fast enough for per-change iteration |
| **Integration** | Full feature/UX flow across components | Live dev server target | Scoped runs still possible; full sweep reserved for the gate |

- Tiers are independently targetable by layout or marker
  (`tests/unit/…`, `-m component`); a scoped run must mean the same as
  the full run — no order dependence, no shared mutable state across
  tests.
- **Enforce the network wall mechanically, not by prose**: a
  socket-blocking autouse fixture in the unit tier (pytest:
  `pytest-socket`). Agents follow walls more reliably than guidance, and
  a mock added to dodge the wall becomes a visible, reviewable act.
- Make runtime budgets contract tests: a test that fails when the unit
  tier exceeds its budget gives suite latency an owner instead of a slow
  boil.

## The Mock Ladder

When code under test touches a dependency, take the highest rung
available (extends the category table in
[seams-and-dependencies](../../dependency-hygiene/references/seams-and-dependencies.md)):

1. **Real in-process call** — your own modules are never mocked (bar 5).
2. **Faithful local substitute** — SQLite for Postgres, tmpdir for
   object store.
3. **Live development server** — component/integration tiers exercise
   the real service.
4. **Fake behind an owned port** — for remote-owned services in
   unit-tier tests.
5. **Mock** — last resort: only a network dependency sitting in a
   unit-tier hot path. Clock is the one sanctioned non-network freeze
   (determinism, bar 6).

A suite whose unit tier is mostly rung 5 has a boundary-shape problem,
not a testing problem — route to
[dependency-hygiene](../../dependency-hygiene/SKILL.md).

## Run Discipline

Commands are pytest exemplars; adapt flags per stack, keep the shape.

- **Iterating**: scoped subset covering the change, quiet, fail-fast:
  ```bash
  pytest tests/unit/<area> -q -x --tb=short
  ```
- **Gate**: the full defined suite exactly once before completion,
  routed to a log; read back exit status plus the failure tail, never
  the stream:
  ```bash
  pytest -q --tb=short >"$LOG" 2>&1 || tail -40 "$LOG"
  ```
- The subset never substitutes for the gate; the gate never replaces
  subset iteration.
- After deleting or moving test files, verify imports survive:
  `pytest --collect-only -q` fails here, not in the scoped run.

## Growth Governance

Write-time rules; each is reviewable:

- **Worth-adding** — bar 10: a test is added only if it catches a
  plausible bug no existing test catches. Search first; extend the
  nearest existing test when one pins the behavior.
- **Net delta stated** — the change reports tests added/deleted.
  Adds-only growth in a mature area is a finding, symmetric with
  [cruft-cleanup](../../cruft-cleanup/SKILL.md) for production code.
- **Provenance docstring** — every test cites what it pins: spec
  scenario, invariant/RFC, or bug id. Recorded at write time, later
  condensation is a grep; reconstructed after the fact, it is
  archaeology.
- **One canonical factory per entity** — copy-paste setup blocks are the
  bloat vector agents clone; give them the right template.
- **Snapshot tests are suspect** — agents regenerate snapshots to get
  green, converting them to letter-tests. Require human-reviewed
  snapshot diffs or avoid the pattern.
- **Prefer properties for pure logic** — a few property-based tests
  replace dozens of enumerated examples.

## Condensation Cadence

Schedule a recurring pass (monthly under heavy feature work); do not
wait for crisis. Per pass:

1. **Measure** — count per domain; compare to last pass.
2. **Classify** — walk each test through the keep/delete/rewrite decision
   tree in
   [condensation-classification](condensation-classification.md)
   (load it only for this step). Per-test coverage contexts
   (`pytest --cov --cov-context=test`) surface tests whose covered lines
   are a strict subset of another's; provenance docstrings resolve
   intent.
3. **Rewrite or delete** — each removed test either has its unique
   behavior re-pinned through the public interface or is shown
   redundant. Mock-wiring assertions can encode real contracts — apply
   the plumbing-vs-contract litmus
   ([condensation-classification](condensation-classification.md) §1);
   when in doubt, keep.
4. **Verify** — scoped tiers green, `--collect-only` clean
   (shared-helper deletions fail there, not in scoped runs); commit
   message states the delta.

During audits, spot-check rigor with mutation testing (`mutmut` on one
hot module): surviving mutants name the bugs the suite would miss.
