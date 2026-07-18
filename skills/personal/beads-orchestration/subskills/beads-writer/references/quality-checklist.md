# Quality Checklist

Use this reference before finalizing or after creating beads.

## Final Checklist

- [ ] Title is imperative, specific, and under 72 characters
- [ ] Type matches the actual work
- [ ] Priority is calibrated; not everything is P0 or P1
- [ ] Description answers what, why, and context
- [ ] A fresh independent session could execute the bead as written
- [ ] If this is a subbead, it is comprehensive enough to serve as a standalone prompt
- [ ] Acceptance criteria are testable and enumerated
- [ ] The bead is not a duplicate of open/recently closed work or an active PR
- [ ] The cohesion scan found no sibling sharing two or more allocation signals,
      or the bundle/serialization override is recorded
- [ ] Structured fields contain a complete dispatch-ready packet: outcome,
      non-goals, governing intent, surface/trust-boundary map, relevant behavior
      matrix, documentation impact, and observable verification
- [ ] Dependencies are linked intentionally
- [ ] Labels reuse the existing taxonomy
- [ ] The bead has one testable outcome
- [ ] Epics include one final reconciliation bead that depends on all siblings
- [ ] Reconciliation beads carry generation tags and never exceed `gen-3`
- [ ] Every universal/negative spec invariant ("no X anywhere", "every Y must",
      "the only path is Z") is owned by a bead that sweeps PRE-EXISTING code
      into compliance (enumerate current violating paths; fix/route/retire
      them) — not only by beads making the new code comply
- [ ] Acceptance criteria pin test depth where it matters: behavior-executing
      (DB/integration/render) vs source-scan; a guardrail bead's criteria
      quote the spec's mandated scan surface verbatim, not a paraphrase

## Persistence Checks

You must persist Beads changes after creating or modifying beads.

Beads data is stored in the Dolt database under `.beads/dolt/`. Writes go through the auto-started SQL server, so there is no manual file commit for bead content itself.

Recommended checks:

```bash
bd dolt push
```

If persistence checks fail, run:

```bash
bd doctor --fix --yes
```

## Anti-Patterns

| Anti-pattern | Fix |
|--------------|-----|
| Vague title like "Fix stuff" | Write the concrete behavior or capability |
| Missing description | Explain what changes, why it matters, and the operating context |
| Everything marked urgent | Use the numeric priority scale proportionally |
| Mega-issue with unrelated criteria | Split into focused children under an epic |
| Description prescribes implementation details | Move approach details into `design` or supporting notes |
| Orphaned issue with no links | Add parent or dependency wiring |
| Duplicate of existing work | Search first with `bd list` and `bd search` |
| Tiny subbeads that just restate file names | Expand them until they function as standalone prompts |
| Epic without reconciliation | Add a final terminal reconciliation bead |
| Reconciliation beyond `gen-3` | Stop at `gen-3` and document remaining gaps explicitly |
| Universal invariant concretized only as new-code compliance | Add a sweep bead: enumerate and fix the pre-existing paths the invariant outlaws (observed: "no merge without review" shipped while two legacy merge endpoints kept bypassing it) |
