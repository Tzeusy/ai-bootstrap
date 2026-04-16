# Reviewer Skill Evaluation

Use this validation loop whenever the skill, helper scripts, or report contract
change materially.

## Track 1: Trigger Quality

Validate that the description triggers on review-lane prompts and stays quiet on
 unrelated implementation prompts.

Should trigger:
- "Use the reviewer worker for this blocked `pr-review-task` bead"
- "This PR already exists and needs follow-up on review threads"
- "Retry merge assessment for this open PR review bead"

Should not trigger:
- "Implement this ready Beads issue"
- "Create a new PR for this branch"
- "Coordinate the next ready issue"

## Track 2: Helper Smoke Tests

Run each helper with `--help`:

```bash
python3 scripts/resolve_review_context.py --help
python3 scripts/prepare_pr_branch.py --help
python3 scripts/list_review_threads.py --help
python3 scripts/evaluate_merge_readiness.py --help
python3 scripts/discover_quality_gates.py --help || true
python3 scripts/validate_review_text.py --help
python3 scripts/reply_to_review_thread.py --help
python3 scripts/resolve_review_thread.py --help
python3 scripts/create_inline_review_comment.py --help
```

Also run syntax validation:

```bash
python3 -m py_compile scripts/*.py
```

## Track 3: Contract Dry Run

Check that the coordinator and reviewer agree on terminal statuses and report
shape.

Minimum accepted reviewer statuses:
- `merged-pr`
- `pushed-review-fixes`
- `blocked-awaiting-coordinator`
- `invalid-runtime-context`

If the coordinator-side reconciliation docs or parser expect different status
names, fix the contract drift before shipping the skill update.

Also verify the terminal reply contract with the validator:

```bash
python3 scripts/validate_review_text.py \
  --kind reply \
  --text $'Accepted in deadbeef.\nReason: closed the review concern.'

python3 scripts/validate_review_text.py \
  --kind reply \
  --text "fixed"
```

The first command should pass. The second should fail because it is not a
terminal reply body.

## Track 4: End-To-End Review Simulation

On a safe test PR:
1. resolve context
2. prepare branch
3. list threads
4. draft a terminal reply, validate it, and post it with a stable dedupe key
5. rerun the same reply and verify it is skipped as duplicate
6. evaluate merge readiness with required checks available
7. verify a resolved thread without a terminal reply is reported as a blocker
8. verify a required-check fetch failure fails closed

## Exit Criteria

Do not consider the skill update complete unless:
- description and trigger examples look correct
- helper scripts compile and expose `--help`
- reviewer/coordinator status vocabularies match
- terminal replies are validated before thread resolution
- the merge-readiness helper fails closed when check status is unavailable and
  flags resolved threads that are missing a terminal reply
