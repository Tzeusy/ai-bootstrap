# Adversarial Review Protocol

Load this reference before dispatching the mandatory review subagent and when
processing its findings.

## Independence and inputs

The packet author cannot self-review. Use a fresh subagent that has not drafted
the item. One subagent may review a cohesive batch, but every item must receive
its own traceable scope verdict and recommendation verdict.

Give the reviewer:

- the exact draft packet path and item IDs;
- the target project's `th-projects` router and relevant heart-and-soul, RFC,
  spec, lay-and-land, and craft-and-care artifacts;
- the relevant `/th-engineering` bar or local adoption of it;
- canonical tracker/source IDs and evidence snapshot; and
- explicit read-only scope.

Do not summarize toward the preferred answer. Do not ask the reviewer to
"confirm" the recommendation.

## Dispatch prompt

```text
Adversarially review these owner-decision items: {ITEM_IDS} in {PACKET_PATH}.
You are independent of the author. Read the cited source artifacts and the
target project's th-projects shape and th-engineering bar.

For EACH item, challenge two things separately:
1. Problem scope: Is this genuinely a hard owner gate, correctly bounded,
   deduplicated, current, and neither hiding nor expanding the real decision?
2. Recommendation: Are the options complete and materially distinct, and does
   the recommendation best satisfy doctrine, user value, tractability,
   dependencies, risk, churn, and the engineering bar?

Return Observed/Inferred/Unknown claims with evidence. Identify counterexamples,
omitted options, stale evidence, and authority leakage. Use this exact result:
- Scope verdict: Pass | Revise | Reject — reason
- Recommendation verdict: Pass | Revise | Reject — reason
- Material corrections: list or None
- Evidence freshness: exact commit/ref and uninspected live sources

Do not edit files or perform live/external mutations.
```

## Verdict bar

**Scope passes** only when all are true:

- an owner act is genuinely required under the repository's autonomy policy;
- the item describes one decision and names its canonical provenance;
- prerequisites, dependents, and authorization boundary are correct;
- material claims are fresh and evidence-backed; and
- no duplicate question, hidden scope, or preselected false framing remains.

**Recommendation passes** only when all are true:

- 2-4 real options cover the meaningful choice space, including defer/status
  quo when legitimate;
- pros/cons include operational, migration, security/data, and user effects
  where relevant;
- the recommendation traces to the local doctrine/spec and respects topology;
- it meets the local `th-engineering` quality bar, including tests,
  dependencies, cleanup, documentation, and failure behavior; and
- the recommendation does not smuggle in authority beyond the stated gate.

`[Unknown]` is acceptable only when the decision can safely be made despite it
and the packet explains why. Otherwise verdict `Revise`.

## Correction loop

1. Record the review verbatim or as a lossless structured summary.
2. Set any item with `Revise` or `Reject` to `Needs-rework`.
3. Correct framing, evidence, options, recommendation, and boundary.
4. Send the corrected artifact back for independent subagent review. Prefer the
   same reviewer for a narrow verification pass; use a fresh reviewer if the
   prior reviewer authored the semantic solution or the decision materially
   changed.
5. Mark `Review-ready` only after both verdicts are `Pass` on the current item.

Mechanical validation never substitutes for this review. A `Pass` also does
not approve the decision; only the owner can do that.
