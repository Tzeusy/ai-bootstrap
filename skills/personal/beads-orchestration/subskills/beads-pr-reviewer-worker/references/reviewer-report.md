# Reviewer Report

Generate the handoff with `scripts/emit_reviewer_report.py`; do not recreate the
large report template manually. The helper validates scalar enums, JSON arrays,
quality-gate values, merge authority, and status-specific evidence.

Required common fields: status, issue/original IDs, branch, worktree, head and
reviewed-head commits, `Reviewer-Identity:`, `Risk-Tier:`, branch-pushed state, PR
metadata, merge authorization/performance, close state, summary, and the three
quality gates. Pass review actions, follow-ups, and blockers as compact JSON
arrays.

Status rules:

- `merged-pr`: `merge-authorized=yes`, `merge-performed=yes`, exact reviewed
  head, PR metadata, and no blockers.
- `corrections-required`: at least one `correction-required` review action;
  merge was not performed.
- `pushed-review-fixes`: branch pushed, merge not performed, and a fresh
  independent reviewer is still required.
- `blocked-awaiting-coordinator`: non-empty blocker array and no merge.
- `invalid-runtime-context`: no meaningful review or GitHub mutation occurred.

JSON objects remain content-safe: include concise titles, classifications,
URLs, and rationale; never include secret values, raw command dumps, full issue
payloads, or verbose gate logs.

Example validation-only invocation:

```bash
python3 scripts/emit_reviewer_report.py \
  --status corrections-required --issue-id bd-review-1 \
  --original-issue bd-42 --branch agent/bd-42 --worktree-path /safe/worktree \
  --head-commit abc --reviewed-head-commit abc --reviewer-identity reviewer-1 \
  --risk-tier standard --branch-pushed yes --pr-url https://example.invalid/pr/1 \
  --pr-number 1 --base-branch main --merge-authorized no \
  --merge-performed no --pr-closed no --summary "One correction remains." \
  --quality-gate lint=pass --quality-gate typecheck=pass \
  --quality-gate tests=pass \
  --review-actions-json '[{"thread_url":"https://example.invalid/thread/1","action":"correction-required","summary":"Fail closed on malformed evidence"}]'
```
