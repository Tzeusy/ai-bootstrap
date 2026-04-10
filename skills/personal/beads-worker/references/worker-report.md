# Worker Report

Use `scripts/emit_worker_report.py` to generate the final report instead of
hand-formatting it.

## Required Status Values

- `completed-pr-opened`
- `completed-direct-merge-candidate`
- `blocked-awaiting-coordinator`
- `invalid-runtime-context`

Do not invent synonyms such as `done`, `blocked`, or `needs-review`.

## Standard Usage

```bash
python3 scripts/emit_worker_report.py \
  --status completed-direct-merge-candidate \
  --issue-id "${ISSUE_ID}" \
  --worktree-path "${WORKTREE_PATH}" \
  --head-commit "$(git rev-parse HEAD)" \
  --branch-pushed yes \
  --handoff-path direct-merge-candidate \
  --summary "Implemented the assigned change and verified the required gates." \
  --quality-gate lint=pass \
  --quality-gate typecheck=pass \
  --quality-gate tests=pass \
  --changes "path/to/file: what changed" \
  --tests "pytest path/to/test.py: pass"
```

For PR handoff add:

```bash
  --status completed-pr-opened \
  --handoff-path pr-required \
  --pr-url "${PR_URL}" \
  --pr-number "${PR_NUMBER}" \
  --base-branch "${BASE}" \
  --review-reason "Why this change should go through PR review"
```

For blockers add:

```bash
  --status blocked-awaiting-coordinator \
  --handoff-path blocked-awaiting-coordinator \
  --branch-pushed no \
  --recovery-state local-only \
  --resume-condition "Exact event required before work can resume" \
  --failing-command "Exact command that failed" \
  --remote-branch "origin/agent/${ISSUE_ID}" \
  --dirty-worktree yes|no|unknown \
  --unpushed-commits yes|no|unknown \
  --blockers-json '[{"title":"Concrete blocker title","type":"task","priority":1,"depends_on":"bd-42","rationale":"What is blocked and why","unblock_condition":"What must happen before work can resume"}]'
```

## JSON Arrays

`Discovered-Follow-Ups-JSON` and `Blockers-JSON` must both be valid JSON arrays.

Example follow-up entry:

```json
{
  "title": "Short follow-up title",
  "type": "bug",
  "priority": 2,
  "depends_on": "bd-42",
  "rationale": "Why this should be tracked separately"
}
```

Example blocker entry:

```json
{
  "title": "Concrete blocker title",
  "type": "task",
  "priority": 1,
  "depends_on": "bd-42",
  "rationale": "What is blocked and why",
  "unblock_condition": "What must happen before work can resume"
}
```

## Reporting Rules

- `completed-pr-opened` requires verified PR metadata and `Branch-Pushed: yes`.
- `completed-direct-merge-candidate` requires `PR-URL: n/a`,
  `PR-Number: n/a`, and `Branch-Pushed: yes`.
- `blocked-awaiting-coordinator` requires at least one blocker object and the
  exact failing command.
- `invalid-runtime-context` means stop before touching code or Beads lifecycle
  state.

When blocked after partial progress, include recovery detail so the next worker
does not need manual forensics:
- the exact failing command,
- whether useful commits were pushed,
- the remote branch to resume from if one exists,
- whether the worktree is dirty,
- whether commits remain unpushed.
