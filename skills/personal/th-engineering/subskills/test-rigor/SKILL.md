---
name: test-rigor
description: >
  Use when judging or improving the quality of tests — whether they assert behavior,
  cover edge and failure paths, protect against regressions, and stay trustworthy —
  in a diff, test suite, or review; also suite-level health: tier structure
  (unit/component/integration), targeted runnability, runtime, and growth control.
  Complements process skills like test-driven-development: this is the bar for what
  tests are worth, not when to write them.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-08-02"
---

# Test Rigor

A test suite's job: fail when behavior breaks, and only then. This subskill
judges whether tests earn trust — would they catch the bugs this code will
actually have, and can a maintainer believe a green run?

## Use This Skill When

- Reviewing tests that accompany a change — meaningful or ornamental?
- Auditing a suite: coverage gaps, tautological tests, flakiness, mock
  overuse, bloat, slow or untargetable runs
- Writing tests for a bugfix or risky refactor, deciding what to assert
- Asked any phrasing in the Trigger Sanity Check below

## Do Not Use This Skill For

- The red-green-refactor process itself — `/test-driven-development`
- Diagnosing a failing test's root cause — [diagnosis](../diagnosis/SKILL.md)
  (evidence bar) or `/systematic-debugging` (process)
- Production-code clarity — [code-readability](../code-readability/SKILL.md)

## Core Rule

**A test is worth keeping only if some plausible bug makes it fail.** Before
accepting any test, ask: what defect does this catch? If the honest answer is
"none — it re-asserts the implementation" or "it tests the mock," the test is
cost without protection.


## The Bar

Reviewable expectations — cite the one violated, with file:line evidence:

1. **Assert behavior, not implementation** — Tests pin observable outcomes
   (return values, state transitions, emitted effects), not internal call
   sequences. A pure refactor should not break tests; a behavior change must.
   Where a spec exists, tests derive from its scenarios and target the public
   interface the spec names — spec → interface tests → implementation
   (red-green process: `/test-driven-development`; spec shape: `/th-projects`).
2. **Every bugfix ships a regression test** — Written to fail on pre-fix
   code. A fix without a failing-then-passing test is unverified.
3. **Edge and failure paths are first-class** — Empty inputs, boundaries,
   invalid states, error branches, and concurrency-sensitive paths get tests
   proportional to blast radius. Happy-path-only coverage of a
   failure-prone component is a finding.
4. **No tautologies** — A test that mirrors the implementation's logic to
   compute its expected value, or that asserts a mock returned what the mock
   was told to return, verifies nothing. Expected values are literals or
   independently derived.
5. **Mock only at boundaries you don't own** — Network, clock, filesystem,
   third-party services. Mocking your own internals welds tests to the
   implementation (violating 1) and lets integration bugs through. Design
   the boundary for mockability: each external operation gets its own named,
   SDK-style function, not one generic fetcher — specific functions mock
   cleanly; generic ones push conditional logic into the mocks
   (see [seams-and-dependencies](../dependency-hygiene/references/seams-and-dependencies.md)).
   When a dependency forces a choice, climb the mock ladder — real call >
   local substitute > live dev server > fake > mock
   ([suite-discipline](references/suite-discipline.md)).
6. **Deterministic or quarantined** — A test that fails intermittently is
   worse than no test: it trains people to ignore red. Fix the
   nondeterminism (time, ordering, shared state) or delete the test; never
   retry-until-green.
7. **A failure names the defect** — Test names state expected behavior
   ("rejects_expired_token"); assertion messages make the diff readable.
   A maintainer should localize the bug from failure output alone.
8. **Tests are maintained code** — Duplication, dead fixtures, and
   copy-paste setup rot suites until people stop reading failures. Shared
   setup is factored deliberately; unreadable tests are a finding.
9. **Suite is tiered and targetable** — Every test maps to one tier
   (unit / component / integration); network only above unit, enforced
   mechanically. Iteration runs a scoped subset; the full gate runs exactly
   once before completion. Tier definitions, budgets, run commands:
   [suite-discipline](references/suite-discipline.md).
10. **Growth is governed** — A test is worth *adding* only if it catches a
    plausible bug no existing test catches: search for the nearest existing
    test first and prefer extending it. Reviews state the net test delta;
    adds-only growth in a mature area is a finding
    ([suite-discipline](references/suite-discipline.md)).

## Workflow

1. Diff first: for each behavior the change adds or alters, find the test
   that pins it. Missing pin → finding (expectation 1–3).
2. Read each new/changed test; apply the mutation thought-experiment: name a
   one-line bug in the code under test this test would *not* catch but should.
   If asserting becomes hard, the test is tautological or over-mocked (4, 5).
3. Check the suite's trustworthiness signals: flaky markers, retries,
   sleeps, ignored failures (6), opaque names (7), rotting fixtures (8).
4. Write or fix in-scope tests directly — a missing-test finding is resolved
   by the test, not a TODO. New tests follow bar 10: extend the nearest
   existing test when one already pins the behavior. Verify new tests fail
   when the guarded behavior is broken (revert the fix or inject the bug
   locally to check).
5. Suite-level work only (structure, runtime, bloat, condensation): load
   [suite-discipline](references/suite-discipline.md); a condensation
   pass's classify step additionally loads
   [condensation-classification](references/condensation-classification.md)
   (keep/delete/rewrite tree, plumbing-vs-contract litmus). Per-test
   judgment needs only this file.

## Trigger Sanity Check

- Should trigger: "review these tests", "are these tests meaningful",
  "what's missing from this suite", "tests pass but I don't trust them —
  what would they actually catch?", "the suite is slow / bloated — what do
  we cut", "which tests should run while iterating"
- Should not trigger: "write the feature test-first" (TDD process,
  `/test-driven-development`) or "why is CI red" (debugging,
  `/systematic-debugging`).
