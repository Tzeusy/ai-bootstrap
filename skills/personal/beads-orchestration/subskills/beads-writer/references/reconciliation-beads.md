# Reconciliation Beads

Every epic must end with one final child bead that performs spec-to-code reconciliation.

## Contract

- Create the reconciliation bead last, after all implementation children exist.
- Make it depend on every other child so it runs last.
- Use the same priority as the epic.
- Tag the title with generation: `gen-1`, `gen-2`, or `gen-3`.
- `gen-3` is the hard limit. Do not create `gen-4`.
- Add the `reconciliation` label (`--label reconciliation`). The coordinator
  keys model selection off this label: for a medium-or-higher epic the
  reconciliation bead is dispatched at `EPIC_COMPLEXITY_MODEL` (Opus on
  Claude), not the default coding tier. See "Reconciliation Floor" in the
  coordinator's `runtime-and-safety.md`.

Purpose: verify that every requirement from the original epic or spec has a corresponding implementation bead and code change. If gaps exist, create missing child beads and, if needed, the next-generation reconciliation bead.

## Template

- Title: `Reconcile spec-to-code (gen-1) for <epic summary>`
- Type: `task`
- Priority: same as the epic
- Label: `reconciliation`
- Description:

```text
Deep-dive review: compare the original spec/requirements (see epic description)
against the implementation delivered by sibling beads under this epic.

Mindset: audit the CODEBASE against the spec, not the sibling diffs against
their bead descriptions. Your job is to FALSIFY the coverage claim, not to
collect confirming evidence. A requirement counts as implemented only after
you have read the implementing code — a test existing, or the suite being
green, is never sufficient evidence by itself.

Workflow:
1. Re-read the epic description and all sibling bead descriptions/acceptance criteria.
2. Audit the code. Start from the sibling diffs, but treat the whole codebase
   as in scope — spec invariants bind pre-existing code too.
3. For every universal or negative requirement ("no X anywhere", "every Y
   must", "the only path is Z"): enumerate ALL code paths performing that
   operation (search the repo), and verify each one. One compliant path
   proves nothing.
4. Audit the instruments. For every guardrail/scan test, read its regex,
   glob, and scan roots and check they cover the surface the spec mandates —
   a green-but-blind guardrail is itself a gap. For every spec scenario,
   confirm a test EXECUTES the behavior (DB/integration level); a test that
   merely greps source for the feature does not count.
5. When several surfaces implement the same contract (N readers of one
   store, N writers of one table), diff them against each other for
   consistency: filters, defaults, ordering, authz.
6. Produce a checklist mapping every spec requirement to its implementing
   bead and code evidence (file:line), classified
   implemented/partial/missing/deviates. For large epics, fan out
   independent per-spec-area skeptic subagents and merge their findings.
7. For any requirement not covered or only partially covered:
   a. Create a new child bead under this epic describing the missing work.
   b. Set appropriate priority and link dependencies.
8. If gap beads were created in step 7, create a follow-up reconciliation bead
   for the next generation that depends on all new gap beads.
9. Keep this reconciliation bead open or blocked until all new gap beads and
   any follow-up reconciliation bead are closed.
10. Re-run the requirement-to-bead checklist and close this bead only when all
    requirements show full coverage.
11. If coverage is complete and the epic is managed via an OpenSpec change,
    run /opsx:sync to synchronize deltas into the authoritative application spec.
```

- Acceptance criteria:

```text
1. Every requirement in the epic spec has a corresponding implementation bead.
2. Universal/negative invariants are verified by enumerating every code path
   that performs the operation, not by citing a single compliant example.
3. Guardrail/scan tests were audited for blind spots (scan scope vs the
   spec-mandated surface), and every spec scenario has a behavior-executing
   test (not a source-grep).
4. Any gaps found result in new child beads under the same epic.
5. If gaps were found, a follow-up reconciliation bead for the next generation was created.
6. The close reason records the reconciliation summary.
```

## Known Failure Modes (why the template insists on falsification)

Observed in practice (butlers entity-v3 gen-1 recon, 2026-06: reported 26/26
"full coverage"; an adversarial re-audit the next day found two P1 violations
and four P2 gaps). The four holes, all generalizable:

1. **Instrument trust.** "Guardrail test exists + suite green" was accepted as
   proof of an invariant; the guardrail's regex was blind to the one real
   violating form in the codebase (`ON CONFLICT ... DO UPDATE` vs a
   `UPDATE ... SET` pattern). The instrument is an audit target, not evidence.
2. **Positive-example verification of universal claims.** "No merge without
   review" was checked by confirming the new endpoint complies; two
   pre-existing endpoints that bypass it were never searched for.
3. **Diff scoping.** Auditing only "changes delivered by sibling beads"
   structurally excludes pre-existing code that violates the new spec.
4. **No cross-surface diffing.** Four readers of the same store each looked
   fine in isolation; only comparing them side by side exposed an
   inconsistent filter.

A matching exercise ("find evidence each requirement is implemented") will
report full coverage on an epic with live spec violations. Only counterexample
search finds the gaps.

## Dependency Wiring

Create the bead first, then add dependencies from the reconciliation bead to every implementation child:

```bash
bd dep add <recon-id> <child-id>
```

If new gap beads are created later, wire the next-generation reconciliation bead to those new gaps as well.
