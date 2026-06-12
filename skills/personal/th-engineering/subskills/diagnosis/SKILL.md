---
name: diagnosis
description: >
  Use when diagnosing a hard bug, intermittent/flaky failure, or performance regression
  and you need the evidence bar for the diagnosis itself — a repeatable feedback loop,
  ranked falsifiable hypotheses before instrumentation, tagged debug logging that gets
  cleaned up, and a regression test at the correct seam. Complements process skills like
  systematic-debugging: this is the bar for what counts as a verified root cause, not a
  debugging walkthrough.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
---

# Diagnosis

A diagnosis is a claim about cause, and an unverified causal claim ships the
wrong fix. This subskill grades the evidence produced while debugging: how the
failure is reproduced, how hypotheses are eliminated, and what proof a
root-cause story must carry before a fix is trusted.

## Use This Skill When

- A bug resists the first obvious fix, or its root-cause story is hand-wavy
- A failure is intermittent, flaky, or environment-dependent
- A performance regression needs locating, not just lamenting
- Reviewing a fix whose explanation is "this seems to make it go away"

## Do Not Use This Skill For

- The step-by-step debugging walkthrough — `/systematic-debugging` (process);
  this subskill grades the evidence that process produces
- Judging the test suite itself — [test-rigor](../test-rigor/SKILL.md)
- The post-fix definition of done —
  [engineering-bar](../engineering-bar/SKILL.md)

## Core Rule

**Diagnose with a loop, not a stare.** Every hypothesis gets a cheap,
repeatable experiment, and the fix is proven by the same loop that reproduced
the failure. "I read the code and I'm fairly sure" is a hypothesis, not a
diagnosis.

## The Bar

Cite the item violated, with the run/log evidence:

1. **A feedback loop exists before theorizing** — Build the cheapest
   repeatable failure signal first, escalating only as needed: failing test →
   direct invocation (curl, CLI one-liner) → throwaway harness script →
   headless browser / trace replay → property fuzzing → commit bisection →
   differential run (working vs. broken environment) → human-in-the-loop
   script. Loop quality is measured in speed, signal sharpness, and
   determinism — improving the loop is diagnostic progress, not a detour.
2. **Non-deterministic failures get rate-raised, not retried** — A 1% flake
   is not debuggable; drive reproduction toward ≥50% with parallel runs,
   stress injection, and seed/timing manipulation before hypothesizing.
   Retry-until-green is evidence destruction (test-rigor bar 6).
3. **Hypotheses are ranked and falsifiable before instrumentation** — Write
   3–5 candidate causes, ordered by likelihood × cost-to-test, each with the
   observation that would kill it. Instrument to *discriminate between*
   hypotheses, never to "see what's happening".
4. **Instrumentation is tagged and temporary** — Prefix every debug log with
   a unique investigation tag (e.g. `[DEBUG-x7q2]`); grep the tag before
   commit — a surviving debug print is cruft
   ([cruft-cleanup](../cruft-cleanup/SKILL.md)). A genuine observability gap
   found en route gets promoted into deliberate, structured logging
   (engineering-bar bias 3), not left as a print.
5. **The fix is proven by the loop** — Red before, green after, on the same
   loop. "I can no longer reproduce it" without a recorded loop run is not
   evidence; neither is a passing suite that never reproduced the failure.
6. **A regression test lands at the correct seam** — The test exercises the
   layer where the cause is observable, not three mocks away from it. If no
   such seam exists, say so: that is an architectural finding
   ([dependency-hygiene](../dependency-hygiene/SKILL.md)), and the fix is
   incomplete without at least naming it. test-rigor bar 2 requires the
   regression test; this names where it belongs.
7. **Performance regressions are measured before they are blamed** —
   Establish a baseline number, then bisect (commits, configs, or inputs)
   against it. A perf fix claim carries before/after measurements under the
   same conditions, never "feels faster".
8. **Close with the prevention question** — "What would have prevented this
   bug?" and route the answer: missing coverage →
   [test-rigor](../test-rigor/SKILL.md); missing seam or boundary →
   [dependency-hygiene](../dependency-hygiene/SKILL.md); silent fallback or
   unlogged failure path → [engineering-bar](../engineering-bar/SKILL.md)
   biases 3 and 6. An answered prevention question that changes nothing is a
   finding in itself.

## Workflow

1. **Loop** (bar 1) — build the cheapest repeatable signal; if flaky,
   rate-raise first (bar 2).
2. **Rank** (bar 3) — list 3–5 falsifiable hypotheses with kill conditions.
3. **Discriminate** (bar 4) — add tagged instrumentation that separates the
   top hypotheses; run the loop; cross off what the evidence kills.
4. **Fix and prove** (bar 5) — apply the fix; show the loop red→green.
5. **Pin** (bar 6) — write the regression test at the correct seam; verify it
   fails on the pre-fix code.
6. **Clean** (bar 4) — grep the investigation tag; delete or deliberately
   promote every hit.
7. **Prevent** (bar 8) — answer the prevention question and route it.

## Trigger Sanity Check

- Should trigger: "diagnose this", "this test fails one run in twenty",
  "p99 latency doubled since last week — find out why", "is this root-cause
  analysis actually verified?"
- Should not trigger: "walk me through debugging basics"
  (`/systematic-debugging`) or "review this test suite" (test-rigor).

## Provenance

The loop ladder, rate-raising protocol, log tagging, and correct-seam rule
are adapted from `skills/mattpocock-skills/skills/engineering/diagnose/`
(which also ships a reusable HITL loop script template).
