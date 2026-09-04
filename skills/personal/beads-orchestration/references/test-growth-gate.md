# Test Growth Gate

Shared by `beads-worker` (write time) and `beads-pr-reviewer-worker` (review
time). It applies `th-engineering` test-rigor bar 10 ("growth governance") to
the autonomous lane, where nobody else notices a suite doubling.

Why it exists: under agentic development every bead adds tests and none
removes them. Observed in butlers: 9.4k tests to 17.4k in twelve weeks, CI
minutes tracking the count, and reviewers waving through "more tests" as if
more were free. Tests are production code with a run-time cost on every PR.

## Write-time rules (worker)

1. **Search before writing.** Find the nearest existing test that pins the
   seam you changed (`rg -l "<function or route>" tests/`). Extend it, or add
   a case to its parametrization, before creating a new test function or file.
2. **One gate species per behavior.** Each behavior or invariant is pinned by
   exactly one of: a behavior-executing test at the real seam, a source-scan
   guard script in CI, or a type/lint rule. Do not add a source-grep test for
   something a behavior test already covers, or a behavior test for something
   a guard script already enforces. If the bead's acceptance criteria name the
   species, use that one.
3. **No letter-of-law tests.** A test that asserts source text, a log line, a
   docstring, an exact error string, or the presence of a function is a
   finding unless that string is a documented contract (CLI output, API error
   code, wire format). Test what the code does at its boundary.
4. **One canonical factory per entity.** Reuse the fixture/factory the suite
   already has. A copy-pasted setup block is the bloat vector the next agent
   clones.
5. **State the net delta.** The PR body (and the worker report `Summary`)
   carries one line: `Tests: +<added> ~<extended> -<removed>`. Adds-only growth
   in an area that already has tests needs a one-sentence reason.
6. **Respect the repo test budget.** If the repository enforces a per-lane
   collected-test budget (for example a `check_test_budget.py` ratchet),
   exceeding it is fixed in the same PR by condensing, or the budget raise is
   justified in the PR body with the delta line. Never raise it silently.
7. **Scope the local run.** Follow the repo's test-scope policy while
   iterating; run the repo's defined full gate exactly once before handoff
   (see `token-efficiency.md`). Do not invent a lighter final gate.

## Review-time rules (reviewer)

- The test diff is part of the review, not an appendix. Read it with the same
  scrutiny as the production diff.
- Findings (leave a `correction-required` thread like any other):
  - missing or implausible `Tests:` delta line;
  - more new test functions than behaviors changed, without the reason;
  - a new test whose setup duplicates an existing fixture or whose assertions
    are a subset of an existing test's;
  - a second gate species for an already-pinned behavior;
  - a letter-of-law assertion that is not a contract;
  - a snapshot regenerated to get green without a stated behavior change.
- A PR that deletes or condenses redundant tests while keeping every unique
  behavior pinned is a positive signal, not a risk; do not ask for the deleted
  tests back unless a pinned behavior was lost.
- Do not block on test count alone. The bar is "does each test catch a
  plausible bug no other test catches", applied to what this PR added.

## Not covered here

Coverage thresholds, mutation testing, and the periodic condensation pass live
in `th-engineering/subskills/test-rigor/references/suite-discipline.md`. This
gate only stops the autonomous lane from growing the suite without thinking.
