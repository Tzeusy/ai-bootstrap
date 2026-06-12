# Reconciliation Beads

Every epic must end with one final child bead that performs spec-to-code reconciliation.

## Contract

- Create the reconciliation bead last, after all implementation children exist.
- Make it depend on every other child so it runs last.
- Use the same priority as the epic.
- Tag the title with generation: `gen-1`, `gen-2`, or `gen-3`.
- `gen-3` is the hard limit. Do not create `gen-4`.

Purpose: verify that every requirement from the original epic or spec has a corresponding implementation bead and code change. If gaps exist, create missing child beads and, if needed, the next-generation reconciliation bead.

## Template

- Title: `Reconcile spec-to-code (gen-1) for <epic summary>`
- Type: `task`
- Priority: same as the epic
- Description:

```text
Deep-dive review: compare the original spec/requirements (see epic description)
against the implementation delivered by sibling beads under this epic.

Workflow:
1. Re-read the epic description and all sibling bead descriptions/acceptance criteria.
2. Audit the codebase changes delivered by each sibling bead.
3. Produce a checklist mapping every spec requirement to its implementing bead.
4. For any requirement not covered or only partially covered:
   a. Create a new child bead under this epic describing the missing work.
   b. Set appropriate priority and link dependencies.
5. If gap beads were created in step 4, create a follow-up reconciliation bead
   for the next generation that depends on all new gap beads.
6. Keep this reconciliation bead open or blocked until all new gap beads and
   any follow-up reconciliation bead are closed.
7. Re-run the requirement-to-bead checklist and close this bead only when all
   requirements show full coverage.
8. If coverage is complete and the epic is managed via an OpenSpec change,
   run /opsx:sync to synchronize deltas into the authoritative application spec.
```

- Acceptance criteria:

```text
1. Every requirement in the epic spec has a corresponding implementation bead.
2. Any gaps found result in new child beads under the same epic.
3. If gaps were found, a follow-up reconciliation bead for the next generation was created.
4. The close reason records the reconciliation summary.
```

## Dependency Wiring

Create the bead first, then add dependencies from the reconciliation bead to every implementation child:

```bash
bd dep add <recon-id> <child-id>
```

If new gap beads are created later, wire the next-generation reconciliation bead to those new gaps as well.
