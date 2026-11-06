# Finite Outcome Closeout

Use when an accepted outcome needs cross-child or end-to-end verification.
Keep one closeout path on the existing outcome: its checklist, an existing
report, or one closeout bead when separately assignable work is warranted.
There is no mandatory reconciliation bead per epic/package and no recursive
reconciliation-generation hierarchy.

## Contract

The accepted outcome remains open while mandatory acceptance is partial.
A closeout verifies code and required runtime behavior against that baseline,
including activation when accepted scope requires it. Specification adoption,
foundation delivery, and dark source merges are reported separately.

If a closeout bead is useful, give it the outcome's priority, exact governing
references, and the `reconciliation` label for the existing model-selection
floor. Make it depend only on the implementation needed for its proof. Do not
block a useful mandatory release on an optional tail. Reuse this same record
when evidence is incomplete; report gaps to the existing implementation owner
rather than creating another reconciliation generation.

## Verification Prompt

```text
Verify the accepted outcome at <outcome-id> against its governing contract
(request/behavior evidence or applicable exact spec sections).
Read the current acceptance and source. Reuse existing tests/review evidence
for unchanged relevant content, then check the cross-child/runtime seam the
outcome actually requires. Do not equate merged foundations with activation.

For each accepted requirement, record implemented/partial/missing/deviates,
with source evidence and the required behavior proof. For universal or negative
claims, enumerate the applicable paths, including pre-existing paths; one
compliant example is insufficient. Check that any scan/guard covers its
mandated surface and compare multiple producers/consumers of the same contract.
A green test proves only the behavior and environment it exercised.

Return ordinary correctness gaps to the accountable implementation owner in
the same package/PR where possible. Report gap candidates only when a distinct
prerequisite, scope, or governing boundary really requires separate work; dedupe
against existing tracking. Preserve every incomplete acceptance item on the
original outcome. Do not create recursive closeout records or silently defer
mandatory criteria. Any scope amendment needs its actual authority.

Report complete acceptance only with evidence for all mandatory criteria,
including authorization/activation/runtime proof where required. A dispatched
worker reports; the holding coordinator or looper performs lifecycle closure
after independently confirming the required evidence and landing state.
```

## Evidence and Follow-through

Do not add tests for behavior already pinned by a suitable gate merely to
produce a reconciliation artifact. Extend the nearest behavior-executing test
when a real gap exists under the shared test-growth policy. Preserve substantive
findings and refresh only evidence invalidated by relevant content or environment
changes. An unchanged review/test verdict is not repeated because the next
session resumed.

The owner updates the same outcome's checklist with remaining criteria and the
next proof. A separately approved deferral names the acceptance removed and
its authority. Useful landed work remains published if an optional tail is
held. The larger outcome is reported as partial until its accepted mandatory
scope is actually met.
