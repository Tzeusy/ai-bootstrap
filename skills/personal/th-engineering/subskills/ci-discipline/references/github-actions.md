# GitHub Actions Mechanics

Load this when auditing or editing a GitHub Actions pipeline, or measuring
one. The tier model and the bar live in [`../SKILL.md`](../SKILL.md); this
file holds the platform mechanics and the measurement commands. Platform
behavior below was checked against GitHub's docs (merge queues, concurrency,
required status checks) on 2026-11-01; re-check before relying on an edge
case.

## Trigger Shape

One event per state change, cheap tiers on drafts, superseded PR runs
cancelled:

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
  merge_group:            # required if the base branch has a merge queue
  push:
    branches: [main]      # never all branches alongside pull_request

concurrency:
  # One group per PR; every non-PR run gets its own group, so main pushes
  # and merge-queue runs are never cancelled or dropped.
  group: ${{ github.workflow }}-${{ github.event_name == 'pull_request' && github.event.pull_request.number || github.run_id }}
  cancel-in-progress: true

jobs:
  heavy:
    if: github.event_name != 'pull_request' || !github.event.pull_request.draft
```

- `push` without a branch filter plus `pull_request` runs every check twice
  per push to a PR branch.
- Keying the group on the PR number, not `head_ref`, avoids collisions
  between same-named branches on forks. Do not share one group across `main`
  pushes: even with `cancel-in-progress: false`, a new run cancels the
  group's already-pending run, so intermediate pushes go unchecked.
- `ready_for_review` gives the PR its first heavy run when it leaves draft.
- **`push: main` with a merge queue**: the queue already judged the tree it
  pushes, so the push run holds only post-merge work (deploy, coverage
  upload); gate jobs skip on `push`. **Without a queue**, the push run is the
  only check of the tree that actually landed; keep the gate there.

## Required Checks And Skips

The two kinds of skip behave differently as required checks:

- A **job** skipped by `if:` reports **success**, so a required job that a
  broken router skips passes silently.
- A **workflow** not triggered because of `paths` or branch filters reports
  nothing, so its required check stays **pending** and blocks the merge.

Make one aggregate job the only required check, trigger the workflow on
every change, route inside it, and have the aggregate assert which jobs each
routing mode must run. Pass data through `env`, never by interpolating
`${{ }}` into the script:

```yaml
  verdict:
    if: ${{ !cancelled() }}
    needs: [route, guards, unit, integration]
    runs-on: ubuntu-latest
    steps:
      - env:
          NEEDS: ${{ toJSON(needs) }}
          MODE: ${{ needs.route.outputs.mode }}
        run: |
          case "$MODE" in            # jobs each mode must run
            full)   must='["route","guards","unit","integration"]' ;;
            scoped) must='["route","guards"]' ;;
            docs)   must='["route"]' ;;
            *) echo "unknown mode: $MODE" >&2; exit 1 ;;
          esac
          jq -e --argjson must "$must" '
            . as $n
            | all(.[]; .result == "success" or .result == "skipped")
              and all($must[]; $n[.].result == "success")' <<<"$NEEDS"
```

## Merge Queue Semantics

- Every queue entry dispatches its **own** `merge_group` run on a cumulative
  temporary branch (entry 2 tests base + PR 1 + PR 2).
- **Merge limits do not combine builds.** Minimum/maximum group size changes
  how many PRs land together, not how many runs execute. Batching is not a
  run-count lever on GitHub.
- **Build concurrency** (1–100) caps dispatched `merge_group` runs. Peak job
  demand is roughly build concurrency × jobs per run, before any PR work;
  size it against runner capacity, or queue wait replaces execution time.
- On a failed entry the queue removes that PR and rebuilds the entries
  behind it, so one red entry costs every later entry a run.
- With "only merge non-failing pull requests" off, a later entry's pass can
  carry an earlier entry that failed, which absorbs intermittent failures at
  the cost of merging a PR whose own run was red.
- The status-check timeout removes entries whose checks run too long; set it
  above the observed p95 of the terminal gate.

Run-count levers are therefore: fewer entries failing (flakes out of the
blocking path), fewer jobs per run, and a PR tier cheap enough that the queue
run is the only broad one.

## Measurement

Project fields; never dump raw API envelopes into context. Record the
retrieval time with any cohort you cite.

Queue wait vs execution per job, one run (seconds; skipped jobs excluded):

```bash
gh api "repos/{owner}/{repo}/actions/runs/$RUN/jobs?per_page=100" --jq '
  .jobs[] | select(.conclusion != "skipped" and .started_at and .completed_at) |
  [.name,
   ((.started_at|fromdateiso8601) - (.created_at|fromdateiso8601)),
   ((.completed_at|fromdateiso8601) - (.started_at|fromdateiso8601))] | @tsv'
```

A job's `created_at` is when it became eligible, so `started_at - created_at`
is runner queue wait. A dependent job's wait starts after its `needs`
finish; attribute the run's wall time along the critical path, not by
summing jobs.

Runs per PR branch, as **candidate** waste to inspect, not a verdict:

```bash
gh run list --workflow ci.yml --event pull_request --limit 300 \
  --json headBranch,headSha,createdAt --jq '
  group_by(.headBranch)
  | map({branch: .[0].headBranch, runs: length,
         heads: (map(.headSha) | unique | length),
         first: (map(.createdAt) | min), last: (map(.createdAt) | max)})
  | sort_by(-.runs) | .[:15][] | [.branch, .runs, .heads, .first, .last] | @tsv'
```

- `runs > heads` means a head was judged more than once. Some of that is
  by design (`ready_for_review`, `reopened`) or tests a new merge tree after
  the base moved; the rest (manual re-runs, retry-until-green) is waste.
- Many heads per branch is either review-fix rounds (legitimate) or pushes
  before the change was ready for review; read a few branches' histories
  before concluding which.
- Grouping by `headBranch` merges same-named fork branches; use PR numbers
  when forks are in play.

Terminal-gate cohort for p50/p95 time-to-green:

```bash
gh run list --workflow ci.yml --event merge_group --status success --limit 50 \
  --json databaseId,createdAt,updatedAt --jq '
  .[] | [.databaseId, ((.updatedAt|fromdateiso8601) - (.createdAt|fromdateiso8601))] | @tsv'
```

`updatedAt` approximates completion for finished runs; for a cohort used as
evidence, take per-job `completed_at` maxima and check that every required
check is present in each run.
