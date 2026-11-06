# Delivery and ownership

Shared execution contract for coordinator, looper, worker, reviewer and planning.
Read when allocating or continuing delivery; this is the policy source of truth.

## Three distinct units

- **Accepted outcome**: the finite owner-visible capability, including required
  activation and runtime proof. Its existing epic/task retains the original
  acceptance criteria until delivered or explicitly amended by the proper authority.
- **Delivery package**: cohesive implementation with one rollback/review surface.
  It contains one or more existing beads, uses an existing member as its **anchor**,
  and has one branch, worktree, PR and independent review record. No wrapper bead
  is required. A package can deliver a foundation without completing its outcome.
- **Owner session**: one accountable implementer retains the accepted outcome,
  current packet, package and ordinary implementation/testing/review corrections.
  A new package need not mean a new session. A bead is a tracking/claim/acceptance
  unit; it is no longer necessarily a delivery or dispatch unit.

Keep unrelated outcomes in separate packages with separate rollback paths. Package
membership follows a shared contract, fixtures, migration or reviewer decision;
size alone neither joins nor splits work. Do not retroactively rewrite closed history.

## Persistent owners by default

Use the existing **beads-looper implement mode** as an outcome-owning session.
For an explicitly coordinated run, keep the worker session attached to that same
outcome; the coordinator allocates, handles lifecycle writes and recovers sessions,
without relaying routine engineering conversations. No second execution framework.

An owner carries the current outcome through implementation, failure diagnosis,
corrections and landing or explicit handoff. The independent reviewer communicates
findings directly to it and retains its own canonical review record. The coordinator
need only receive package state changes, hard gates and terminal receipts. Reviewers
never become the ordinary implementation owner. If they author semantic fixes,
those changes need another independent reviewer.

Use the existing actor registry and atomic claims, not an epic-wide exclusive lock.
Claim only the bounded package being worked, not every future descendant. Record
outcome affinity and session/resume locator in the anchor's current notes. That
intent does not exclude peers from independent work. A shared prerequisite has
one canonical implementation owner; dependents link it and do not build private
copies on their feature branches. Use ranker prerequisite inheritance to advance
that chain before opening more downstream sessions.

Ordinary corrections retain claims and the implementation worktree. The reviewer
uses its own `review/<review-id>` branch/worktree, so no worktree transfer or
original-bead release/reclaim is needed. A dispatched worker still reports lifecycle
changes to its controller; a looper performs them itself as holder.

## Branch choice is independent of session choice

Default: `agent/<anchor>` based on the repository's integration base; accumulate
cohesive commits locally and publish checkpoints, then one PR to that base.
Related existing correction beads share this cycle. Commit messages identify member
IDs; PR description maps member acceptance and remaining work. Keep commits
logically reviewable and bisectable; use fixups only when repository policy allows.
A persistent owner can deliver several such packages to main without being replaced.

A **bounded milestone integration branch** is useful when an intermediate state
cannot safely land, or tightly coupled changes otherwise repeat fixed queue/review
cost. It is a package, not a default branch per weeks-long epic. Record its base,
accepted landing scope, focused checks, complete final gate and a checkpoint at
which to land or split. Internal work is ordinary commits with focused validation;
independent review covers changed behavior incrementally in the same review record.
Internal PRs/stacks are optional for truly separate authorship or repository policy,
never a new mandatory ceremony per child. All required final-base PR/review/queue
checks still run on the actual landing tree. A PR merged only to an integration
branch is accumulated source, not delivery to main.

Integration branches amortize fixed gates but delay feedback and concentrate drift,
conflicts, terminal diff and rollback cost. Prefer several bounded packages over a
single enormous terminal diff. Fetch the base at checkpoints, use `git merge-tree`
to detect textual conflict and focused seam tests to detect interface incompatibility.
A clean branch is not rebased just because the base moved. A semantic base change
invalidates affected evidence even if merge-tree is clean. Reconcile actual conflicts
in the implementation owner's worktree; independently review the changed content.
Repository-required checks on merge groups/main remain binding even if duplicated.
Harness support does not change Butlers CI or grant permission to target another base.

Do not hold useful work hostage to an optional tail. Publish commits and the current
packet on every meaningful checkpoint. If a tail blocks, land a safe accepted subset
through the real gates, record members still incomplete, and keep the original
outcome open. Carry required remainder in that outcome's existing acceptance state;
create another bead only for a genuinely different ownership or authority boundary.
A deliberate deferral/scope amendment requires the governing authority, never an
implicit reinterpretation of a foundation merge as feature completion.

## Current operative packet

One concise current packet per package: accepted outcome and exclusions, member IDs
and individual acceptance, owned interfaces, governing adopted contract locators,
current source anchors, relevant behavior/failure seams and checks, open authority
or prerequisite gates, base and recovery/resume locator. Link immutable specs/history;
do not inline archives, superseded alternatives, whole before/after contracts,
transcripts or hash inventories. References must be resolvable by a cold session.
No word/token cap: include what changes implementation decisions.

Approved direction, adopted behavior and executable scope differ. Settle shared
interfaces once before allocating their dependents; ground changed assumptions in
an actual source/feasibility walk. Missing product/trust authority blocks its
specific dependent slice. A filled template alone does not prove readiness.

## Claims, reports and canonical association

The optional `beads-delivery/v1` manifest is executable via
[`../scripts/delivery_package.py`](../scripts/delivery_package.py). Its anchor
is `ISSUE_ID`, so the one-bead branch/report convention remains useful. Store the
manifest in anchor `metadata.delivery`; member `metadata.delivery_anchor` points
back. Only the anchor gets `external_ref=gh-pr:N`. Exactly one review bead relates
to that anchor; member traceability lives in the manifest and PR/report, never
repeated unique refs or duplicate review dependencies.

For example (all IDs are existing records):

```json
{"schema":"beads-delivery/v1","anchor":"bd-a","members":["bd-a","bd-b"],
 "owner":"coordinator:codex-example","outcome":"bd-feature","base_branch":"main",
 "packet":"bd-a design: current adapter packet; openspec/specs/adapters/spec.md"}
```

Resolve `PACKAGE_HELPER` to this skill's absolute `scripts/delivery_package.py`.
Keep manifest/journal outside tracked source and record their locators on anchor.

```bash
uv run "$PACKAGE_HELPER" validate --delivery-file "$DELIVERY_FILE"
uv run "$PACKAGE_HELPER" claim --delivery-file "$DELIVERY_FILE" \
  --repo-root "$REPO_ROOT" --journal "$CLAIM_JOURNAL"
# Only an interrupted acquisition uses recover; active work uses explicit release.
uv run "$PACKAGE_HELPER" recover --repo-root "$REPO_ROOT" --journal "$CLAIM_JOURNAL"
uv run "$PACKAGE_HELPER" release --repo-root "$REPO_ROOT" --journal "$CLAIM_JOURNAL"
# After independently confirming main landing, provide complete per-member evidence:
uv run "$PACKAGE_HELPER" closure-plan --delivery-file "$DELIVERY_FILE" \
  --results-file "$MEMBER_RESULTS" --landed-main
```

Recover refuses an active package; it compensates interrupted acquisition only.
Release preserves closed/blocked states, reopens unfinished in-progress members,
and retains the released anchor receipt. Foreign ownership or repository mismatch
is an explicit incomplete recovery, never permission to clear a peer. Before a
remaining member begins a new package, release the old membership after verifying
its landing/recovery state; do not overwrite active package metadata in place.

Use the helper for multi-bead claims: individual `--claim` operations are atomic,
whole-package acquisition is not. It journals attempts before mutation and
compensates only claims newly acquired by this attempt. A failed claim dispatches
nothing. Recover an interrupted attempt from its journal before continuing; never
clear another actor's claim. Do not use a bulk `bd update --claim` as a transaction.
External dependency/authorization holds remain real; ordered member dependencies
can be satisfied inside a package, but cannot authorize work through an external gate.

Bootstrap and report helpers accept `--delivery-file`. The report identifies each
member's acceptance result and evidence. A failed/partial package is not a success
for every member. Closure requires that member's verified acceptance **and** source
landed on the actual delivery base (normally main). Use the helper's closure plan
as a recommendation, then freshly verify authority/PR state and mutate as holder.
A source-only foundation cannot close an activation-inclusive member or its outcome.

## Evidence and review

Record what a verdict proves: relevant source/diff or tree, governing contract,
base/interface assumptions, command/environment and result. Tests and independent
review of unchanged relevant content can be reused across wakes, compaction and
owner recovery. A changed commit SHA requires establishing content equivalence,
not automatically repeating the whole verdict. Changed relevant content or base
assumptions invalidates affected evidence; recheck that delta. Broad checks still
cover the final landing tree in the repository-assigned tier.

Runtime/environment evidence (permissions, deployment, service availability,
owner labels, CI/queue status) is time-sensitive: refresh when its assumptions
changed or at the action it authorizes. An old source verdict never proves live
behavior or current merge permission. Bind the final merge receipt to the current
head, with reused content evidence and its equivalence proof explicitly identified.
Reuse the same independent reviewer while independence holds; retain substantive
findings and recheck deltas in the existing review record.

## Waits, preemption and recovery

- Runnable prerequisite: finish it under one owner; multiple outcomes may wait on it.
- Technical wait (CI/review/external dependency): retain outcome affinity and resume
  on its event, using a bounded fallback. Do useful in-outcome work when available;
  do not continuously poll or open unrelated outcomes just to fill slots.
- Owner hold: publish precise dependent scope, authority and unblock event. Continue
  unaffected work; never infer consent from a prior answer or elapsed time.

P0/emergency work preempts at a safe commit/checkpoint; publish recovery state,
release or retain claims explicitly and identify who will resume. Outcome affinity
is not indefinite custody of a backlog. Do not seize a live owner's claims.

Continuation resumes the same Claude agent/session or Codex thread when supported.
Compaction/recovery packet names actor, session locator, package/member state,
published head/PR, local-only work, reviewed content and remaining gates. A fresh
launch is recovery, not continuation: validate cwd, ownership and remote/local
state before editing. Registry expiry alone never proves local work is disposable.
When a session dies, recover package claims together under existing guarded dead-owner
rules, preserve pushed branches and quarantine unpublished work. Never delete a
worktree merely because a PR opened or a member left `in_progress`.
