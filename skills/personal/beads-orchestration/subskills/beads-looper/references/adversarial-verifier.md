# Adversarial Verifier

The implement lane wrote the code, so it is the worst-placed party to judge
it. Before a bead lands or opens a PR, a fresh subagent tries to prove it is
not done. This is the independence case in `../../../references/token-efficiency.md`
→ "Fan out only when independence is the point". The verifier starts cold on
purpose.

## When

- After the gate assigned to the local tier passes (full, or scoped when a
  required hosted check gates landing), before the worker's Phase 5 hand-off.
- Again after any fix made for a blocking finding.
- After a correction pass, scoped to the correction diff and its threads.

## Dispatch

Spawn the verifier through the runtime's native subagent mechanism. On
Claude Code that is the Agent tool with a general-purpose agent, which can run
tests. Pick its model from the bead's complexity
(`../../beads-coordinator/references/runtime-and-safety.md` → "Assignment
Rules"). Never go below this lane's model for a high-risk-tier change
("Review Risk Tiers").

Give it the work, not your conclusions. A verifier handed your summary tends
to confirm it. The prompt carries only:

- `ISSUE_ID`, `WORKTREE_PATH`, and the diff range `origin/<base>...HEAD`
- the acceptance criteria verbatim, plus the description's scope and
  non-goals (`bd show <id> --json | jq '{acceptance_criteria, description, design}'`)
- the path of the local gate log, labelled `full` or `scoped`
- the rules: read-only, meaning no edits, commits, pushes, `bd` writes, or
  `gh` writes, with test output routed to files outside the worktree

## Charge

Tell the verifier to try to break the change:

1. For each acceptance criterion, find the code and the test that prove it,
   and mark it `met`, `unmet`, or `unverifiable`. "A test exists" is not
   proof; check that the test would fail without the change.
2. Hunt for regressions in callers of changed code, for edge cases the tests
   skip, and for error paths.
3. Flag scope creep beyond the bead, and conflicts with the governing spec or
   repo doctrine.
4. Apply the repo's craft-and-care bar and the test-growth gate
   (`../../../references/craft-and-care-gate.md`,
   `../../../references/test-growth-gate.md`).
5. Run any targeted tests it needs to settle a doubt.

## Verdict Contract

The verifier ends with exactly one JSON object:

```json
{"verdict": "pass|fail",
 "criteria": [{"criterion": "...", "status": "met|unmet|unverifiable", "evidence": "file:line or test id"}],
 "findings": [{"severity": "blocking|non-blocking", "where": "file:line", "claim": "...", "repro": "command or input"}]}
```

`fail` means at least one `unmet` criterion or `blocking` finding.

## Acting On It

- **Blocking finding or unmet criterion.** Either fix it, or dispute it with
  evidence (a test, a spec line, a repro that disproves it) and record the
  dispute as a `[decision]`. After fixes, re-run the targeted tests, then the
  local-tier gate once, then the verifier. Continue the same verifier session for
  re-checks, since it already holds the findings.
- **Non-blocking finding.** Fix it if it takes less than two minutes.
  Otherwise list it under `Discovered-Follow-Ups-JSON`.
- **Rounds are capped at three verifier runs.** If disputed findings still
  stand after that, move to the PR path and list the disputes in the PR body
  under "Verifier disputes" for the review lane to arbitrate. A disputed
  direct-merge candidate becomes a PR. If a criterion is genuinely unmet and
  cannot be met inside the bead, the bead is not done. Take the worker's
  "Handling Blockers" path, after checking decision-autonomy.
- Put the final verdict line (`verifier: pass after N rounds`, or the
  disputes) in the PR body or the close reason. The verdict is evidence, so
  it travels with the work.
