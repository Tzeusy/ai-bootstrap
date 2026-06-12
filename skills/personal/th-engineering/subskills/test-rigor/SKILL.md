---
name: test-rigor
description: >
  Use when judging or improving the quality of tests — whether they assert behavior,
  cover edge and failure paths, protect against regressions, and stay trustworthy —
  in a diff, test suite, or review. Complements process skills like
  test-driven-development: this is the bar for what tests are worth, not when to
  write them.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
---

# Test Rigor

A test suite's job is to fail when behavior breaks and only then. This
subskill judges whether tests earn trust: would they catch the bugs this code
will actually have, and can a maintainer believe a green run?

## Use This Skill When

- Reviewing tests that accompany a change — are they meaningful or ornamental?
- Auditing a suite: coverage gaps, tautological tests, flakiness, mock overuse
- Writing tests for a bugfix or risky refactor and deciding what to assert
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
2. **Every bugfix ships a regression test** — Written to fail on the
   pre-fix code. A fix without a failing-then-passing test is unverified.
3. **Edge and failure paths are first-class** — Empty inputs, boundaries,
   invalid states, error branches, and concurrency-sensitive paths get tests
   proportional to their blast radius. Happy-path-only coverage of a
   failure-prone component is a finding.
4. **No tautologies** — A test that mirrors the implementation's logic to
   compute its expected value, or that asserts a mock returned what the mock
   was told to return, verifies nothing. Expected values are literals or
   independently derived.
5. **Mock only at boundaries you don't own** — Network, clock, filesystem,
   third-party services. Mocking your own internals welds tests to the
   implementation (violating 1) and lets integration bugs through. Design
   the boundary for mockability: each external operation gets its own named,
   SDK-style function rather than one generic fetcher — specific functions
   mock cleanly; generic ones push conditional logic into the mocks
   (see [seams-and-dependencies](../dependency-hygiene/references/seams-and-dependencies.md)).
6. **Deterministic or quarantined** — A test that fails intermittently is
   worse than no test: it trains people to ignore red. Fix the
   nondeterminism (time, ordering, shared state) or delete the test; never
   retry-until-green.
7. **A failure names the defect** — Test names state the expected behavior
   ("rejects_expired_token"), and assertion messages make the diff readable.
   A maintainer should localize the bug from the failure output alone.
8. **Tests are maintained code** — Duplication, dead fixtures, and
   copy-paste setup rot suites until people stop reading failures. Shared
   setup is factored deliberately; unreadable tests are a finding.

## Workflow

1. Diff first: for each behavior the change adds or alters, find the test
   that pins it. Missing pin → finding (expectation 1–3).
2. Read each new/changed test and apply the mutation thought-experiment:
   name a one-line bug in the code under test that this test would *not*
   catch but should. If asserting becomes hard, the test is tautological or
   over-mocked (4, 5).
3. Check the suite's trustworthiness signals: flaky markers, retries,
   sleeps, ignored failures (6), opaque names (7), rotting fixtures (8).
4. Write or fix in-scope tests directly — a finding about a missing test is
   resolved by the test, not a TODO. Verify new tests fail when the guarded
   behavior is broken (revert the fix or inject the bug locally to check).

## Trigger Sanity Check

- Should trigger: "review these tests", "are these tests meaningful",
  "what's missing from this suite", "tests pass but I don't trust them —
  what would they actually catch?"
- Should not trigger: "write the feature test-first" (TDD process,
  `/test-driven-development`) or "why is CI red" (debugging,
  `/systematic-debugging`).
