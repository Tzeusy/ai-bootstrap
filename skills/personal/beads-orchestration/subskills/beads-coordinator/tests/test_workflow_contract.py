# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import json
import os
import shutil
import tempfile
import re
import subprocess
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
LOOP = SKILL_ROOT / "references" / "coordinator-loop.md"
SAFETY = SKILL_ROOT / "references" / "runtime-and-safety.md"
EPIC = SKILL_ROOT / "references" / "epic-coordination.md"
COMMANDS = SKILL_ROOT / "references" / "commands.md"
WRITER = SKILL_ROOT.parent / "beads-writer" / "SKILL.md"
TOKEN_EFFICIENCY = SKILL_ROOT.parents[1] / "references" / "token-efficiency.md"
NORMALIZER = SKILL_ROOT / "scripts" / "normalize_pr_review_state.py"
RANKER = SKILL_ROOT / "scripts" / "rank_ready_work.py"
REVIEW_FAILURE_PROTOCOL = (
    SKILL_ROOT.parent / "beads-pr-reviewer-worker" / "references" / "failure-protocol.md"
)
SKILL_AUDIT_WORKFLOW = SKILL_ROOT.parents[4] / ".github" / "workflows" / "skill-audit.yml"


# A `bd` invocation that writes tracker state. Group 1 is whatever sits between
# `bd` and the subcommand (global flags), group 2 the subcommand.
BD_MUTATION = re.compile(
    r"\bbd((?:\s+-C\s+\S+|\s+--actor\s+\S+)*)\s+"
    r"(update|create|close|unclaim|dep add|dep remove|kv set|kv clear|epic close-eligible)(?=\s)"
)


class BeadsCoordinatorWorkflowContractTests(unittest.TestCase):
    def test_owner_hold_guards_and_inventory_execute_documented_procedure(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        procedure = contents.split("# owner-merge-procedure: begin", 1)[1].split(
            "# owner-merge-procedure: end", 1
        )[0]
        real_jq = shutil.which("jq")
        self.assertIsNotNone(real_jq)

        def run(responses, body, fail_direct=False):
            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                fixture = {"responses": responses, "fail_direct": fail_direct}
                (root / "fixture.json").write_text(json.dumps(fixture))
                fake_gh = '''#!/usr/bin/env python3
import json, os, sys
from pathlib import Path
root = Path(os.environ["FAKE_ROOT"])
args = sys.argv[1:]
fixture = json.loads((root / "fixture.json").read_text())
if args[:2] == ["api", "graphql"] and any(a.startswith("query=query(") for a in args):
    assert "--paginate" in args and "--slurp" in args, args
    query = next(a for a in args if a.startswith("query="))
    assert "first:100" in query and "$endCursor" in query and "pageInfo" in query, query
    count_file = root / "reads"
    index = int(count_file.read_text()) if count_file.exists() else 0
    count_file.write_text(str(index + 1))
    item = fixture["responses"][index]
    if item == "FAIL":
        sys.exit(1)
    print(json.dumps(item))
    sys.exit(0)
with (root / "actions").open("a") as output:
    output.write(json.dumps(args) + "\\n")
if fixture["fail_direct"] and args[:2] == ["pr", "merge"] and "--auto" not in args:
    sys.exit(1)
'''
                (root / "gh").write_text(fake_gh)
                # Exercise real jq semantics through a fake PATH executable,
                # exactly as the published projection runs in an acting shell.
                (root / "jq").write_text(
                    "#!/usr/bin/env python3\nimport os, sys\nos.execv("
                    + repr(real_jq) + ", [" + repr(real_jq) + "] + sys.argv[1:])\n"
                )
                (root / "git").write_text(
                    '#!/usr/bin/env python3\nimport os\nfrom pathlib import Path\n'
                    'with (Path(os.environ["FAKE_ROOT"]) / "actions").open("a") as f: f.write("base-push\\n")\n'
                )
                for command in ("gh", "jq", "git"):
                    (root / command).chmod(0o755)
                result = subprocess.run(
                    ["bash", "-c", procedure + "\nOWNER=owner\nREPO=repo\n" + body],
                    env={**os.environ, "PATH": str(root) + os.pathsep + os.environ["PATH"],
                         "FAKE_ROOT": str(root)}, capture_output=True, text=True,
                )
                actions = (root / "actions").read_text().splitlines() if (root / "actions").exists() else []
                return result, actions

        def page(nodes, more=False, cursor=None, *, state="OPEN", inventory=False):
            connection = {"nodes": nodes, "pageInfo": {"hasNextPage": more, "endCursor": cursor}}
            pr = {"pullRequests": connection} if inventory else {"pullRequest": {"state": state, "labels": connection}}
            return {"data": {"repository": pr}}

        unheld = [page([])]
        held = [page([{"name": "owner-merge"}])]
        late_hold = [page([{"name": f"tag-{i}"} for i in range(100)], True, "next"),
                     page([{"name": "owner-merge"}])]
        malformed = [page([{"name": None}])]
        partial = [page([], True, "next")]
        errors = [{**page([]), "errors": [{"message": "partial response"}]}]
        invalid = ("FAIL", [], malformed, partial, errors, [None],
                   [page([], True, "same"), page([], True, "same"), page([])])
        direct = 'owner_merge_guard 42 && gh pr merge 42 --squash'
        auto = direct + ' --auto'
        enqueue = "owner_merge_guard 42 && gh api graphql -f 'query=mutation{enqueuePullRequest}'"
        close = 'gh pr comment 42 --body reason\nowner_merge_guard 42 && gh pr close 42'
        for action in (direct, auto, enqueue):
            # Includes queue-direct initial enrollment; re-enrollment/retry is
            # a separate action with a separate label observation below.
            for evidence in (held, late_hold, *invalid):
                with self.subTest(action=action, evidence=evidence):
                    result, actions = run([evidence], action)
                    self.assertNotEqual(result.returncode, 0, result.stdout)
                    self.assertEqual(actions, [])
            result, actions = run([unheld], action)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(actions), 1)
            # Label added after earlier readiness or inventory suppresses the
            # actual attempt. Every fallback and queue-direct retry rechecks.
            result, actions = run([unheld, held], 'owner_merge_guard 42\n' + action)
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertEqual(actions, [])
        for fallback in (auto, enqueue):
            result, actions = run([unheld, held], direct + '\n' + fallback, fail_direct=True)
            self.assertEqual(result.returncode, 3, result.stderr)
            self.assertEqual(len(actions), 1, actions)
            self.assertNotIn("--auto", actions[0])
        result, actions = run([unheld, held], auto + '\n' + auto)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(len(actions), 1)
        result, actions = run([held], close)
        self.assertEqual(result.returncode, 3, result.stderr)
        self.assertEqual(len(actions), 1)
        self.assertIn('"comment"', actions[0])
        # Removal is effective on the next call, without a local marker reset.
        result, actions = run([held, unheld], direct + '\n' + direct)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(actions), 1)
        for state in ("MERGED", "CLOSED"):
            result, actions = run([[page([{"name": "owner-merge"}], state=state)]], direct)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("terminal-pr", result.stderr)
            self.assertEqual(actions, [])

        pr = {"number": 42, "title": "Foreign branch held PR", "state": "OPEN",
              "statusCheckRollup": {"state": "SUCCESS"}}
        branch_action = 'owner_merge_branch_guard agent/test && git push origin HEAD:main'
        for evidence in ([page([pr], inventory=True)], "FAIL", [page([], True, "next", inventory=True)]):
            result, actions = run([evidence], branch_action)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(actions, [])
        result, actions = run([[page([], inventory=True)]], branch_action)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(actions, ["base-push"])

        # All prefixes, all pages: never query only the agent/ ownership lane.
        inventory = [page([{**pr, "number": i} for i in range(1, 101)], True, "next", inventory=True),
                     page([{**pr, "number": 101, "statusCheckRollup": None},
                           {**pr, "number": 102, "statusCheckRollup": {"state": "FAILURE"}},
                           {"number": 103, "title": "Missing CI", "state": "OPEN"}], inventory=True)]
        result, actions = run([inventory], 'owner_merge_inventory')
        self.assertEqual(result.returncode, 0, result.stderr)
        rows = [json.loads(line.removeprefix("Held PR: ")) for line in result.stdout.splitlines()]
        self.assertEqual(len(rows), 103)
        self.assertEqual(rows[0], {"number": 1, "title": pr["title"], "ci_state": "SUCCESS"})
        self.assertEqual([row["ci_state"] for row in rows[-3:]], ["UNKNOWN", "FAILURE", "UNKNOWN"])
        self.assertEqual(actions, [])
        result, _ = run([[page([], inventory=True)]], 'owner_merge_inventory')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), "Held PRs: none")
        for evidence in ("FAIL", [], [None], [page([], True, "next", inventory=True)],
                         [{**page([], inventory=True), "errors": [{"message": "partial"}]}],
                         [page([{"number": 42}], inventory=True)]):
            result, actions = run([evidence], 'owner_merge_inventory')
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(result.stdout.strip(), "Held PRs: unavailable/partial")
            self.assertEqual(actions, [])

    def test_dispatch_requires_structured_acceptance_and_cohesion_check(self) -> None:
        contents = LOOP.read_text(encoding="utf-8").lower()
        self.assertIn("dispatch readiness", contents)
        self.assertIn("cohesion", contents)
        self.assertIn("acceptance criteria", contents)

    def test_discoveries_are_classified_before_bead_creation(self) -> None:
        contents = LOOP.read_text(encoding="utf-8").lower()
        for phrase in (
            "current-pr correctness",
            "prerequisite blocker",
            "new behavior",
            "duplicate",
        ):
            self.assertIn(phrase, contents)

    def test_review_risk_tiers_and_exact_head_are_explicit(self) -> None:
        contents = SAFETY.read_text(encoding="utf-8").lower()
        self.assertIn("review risk tiers", contents)
        self.assertIn("exact head sha", contents)
        self.assertIn("auth", contents)
        self.assertIn("data loss", contents)

    def test_model_selection_matches_complexity_and_plan_policy(self) -> None:
        contents = SAFETY.read_text(encoding="utf-8")
        self.assertIn("| Strategy | Claude | Codex / ChatGPT | Gemini |", contents)
        for row in (
            "| `EPIC_COMPLEXITY_MODEL` | Opus 5.5 High | GPT-6.1 Sol XHigh | gemini-4-argon |",
            "| `HIGH_COMPLEXITY_MODEL` | Opus 5.5 Medium | GPT-6.1 Sol High | gemini-4-argon |",
            "| `MEDIUM_COMPLEXITY_MODEL` | Sonnet 5.5 High | GPT-6.1 Sol High | gemini-4-argon |",
            "| `LOW_COMPLEXITY_MODEL` | Sonnet 5.5 Low | GPT-6.1 Sol Low | gemini-3.8-flash |",
            "| `TRIVIAL_COMPLEXITY_MODEL` | Haiku 5.5 Low | GPT-6.1 Terra Low | gemini-3.8-flash |",
            "| `DESIGN_AND_SPECIFICATION_MODEL` | Opus 5.5 High | GPT-6.1 Sol XHigh | gemini-4-argon |",
        ):
            self.assertIn(row, contents)
        for binding in (
            "| GPT-6.1 Terra Low | `gpt-6.1-terra` | `low` |",
            "| GPT-6.1 Sol Low | `gpt-6.1-sol` | `low` |",
            "| GPT-6.1 Sol High | `gpt-6.1-sol` | `high` |",
            "| GPT-6.1 Sol XHigh | `gpt-6.1-sol` | `xhigh` |",
            "| Haiku 5.5 Low | `claude-haiku-5-5` | `low` |",
            "| Sonnet 5.5 Low | `claude-sonnet-5-5` | `low` |",
            "| Sonnet 5.5 High | `claude-sonnet-5-5` | `high` |",
            "| Opus 5.5 Medium | `claude-opus-5-5` | `medium` |",
            "| Opus 5.5 High | `claude-opus-5-5` | `high` |",
        ):
            self.assertIn(binding, contents)
        self.assertIn("Plan/design/specification override", contents)
        self.assertIn("before the complexity-label fast path", contents)
        self.assertIn("never dispatch Terra for anything that needs judgment", contents)
        self.assertIn("do not dispatch Astra, Luna, or GPT-5.6-generation", contents)
        self.assertIn("Never dispatch Haiku for anything that needs judgment", contents)
        for path in (WRITER, TOKEN_EFFICIENCY):
            self.assertIn("design/specification override", path.read_text(encoding="utf-8"))

    def test_refresh_is_event_driven_with_cache_bounded_wakes(self) -> None:
        loop = LOOP.read_text(encoding="utf-8").lower()
        self.assertIn("event-driven", loop)
        self.assertIn("no-progress frontier", loop)
        self.assertIn("safety sweep", loop)
        # Numbers are canonical in runtime-and-safety.md; the loop only points.
        safety = SAFETY.read_text(encoding="utf-8").lower()
        self.assertIn("orchestrator wake cadence", safety)
        self.assertIn("4m50s", safety)
        self.assertIn("1-hour", safety)
        self.assertIn("60 minutes", safety)
        self.assertIn("3 consecutive no-op wakes", safety)
        self.assertNotIn("30-minute safety sweep", loop)

    def test_dispatch_preserves_context_affinity_when_safe(self) -> None:
        contents = LOOP.read_text(encoding="utf-8").lower()
        self.assertIn("context affinity", contents)

    def test_dispatch_continues_warm_lanes_before_spawning(self) -> None:
        loop = LOOP.read_text(encoding="utf-8")
        self.assertIn("Lane continuation first", loop)
        self.assertIn("LANE-CONTINUATION", loop)
        self.assertIn("| Worker lanes | 1 by default", loop)
        self.assertIn("Cache-first execution", TOKEN_EFFICIENCY.read_text(encoding="utf-8"))

    def test_worktree_creation_is_bound_to_repo_root(self) -> None:
        command = '(cd "${REPO_ROOT}" && bd worktree create'
        for document in (LOOP, EPIC):
            with self.subTest(document=document.name):
                self.assertIn(command, document.read_text(encoding="utf-8"))

    def test_review_cycle_state_has_a_canonical_note(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn("[review-cycle]", contents)
        self.assertIn("substantive_reopenings=", contents)
        self.assertIn("reviewed_head_sha=", contents)

    def test_correction_lane_temporarily_detaches_and_restores_review_gate(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn('bd --actor "$COORDINATOR_ID" dep remove <original-id> <review-id>', contents)
        self.assertIn("REVIEW_CORRECTION_MODE=yes", contents)
        self.assertIn('bd --actor "$COORDINATOR_ID" dep add <original-id> <review-id>', contents)

    def test_queue_membership_uses_entry_and_never_infers_rebase_from_absence(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn("mergeQueueEntry{position enqueuedAt} labels(first:20)", contents)
        self.assertIn("`merge_queue_entry` is non-null", contents)
        self.assertIn("queue metadata alone", contents)
        self.assertNotIn("the queue ejected it", contents)

        documents = (LOOP, REVIEW_FAILURE_PROTOCOL)
        valid_cases = {
            "queued": (
                {
                    "state": "OPEN",
                    "mergedAt": None,
                    "autoMergeRequest": None,
                    "mergeQueueEntry": {
                        "position": 1,
                        "enqueuedAt": "2026-09-06T13:55:14Z",
                    },
                },
                {"auto_merge_armed": False, "queue_position": 1},
            ),
            "armed": (
                {
                    "state": "OPEN",
                    "mergedAt": None,
                    "autoMergeRequest": {"enabledAt": None},
                    "mergeQueueEntry": None,
                },
                {"auto_merge_armed": True, "queue_position": None},
            ),
            "absent": (
                {
                    "state": "OPEN",
                    "mergedAt": None,
                    "autoMergeRequest": None,
                    "mergeQueueEntry": None,
                },
                {"auto_merge_armed": False, "queue_position": None},
            ),
            "merged": (
                {
                    "state": "MERGED",
                    "mergedAt": "2026-09-06T14:05:09Z",
                    "autoMergeRequest": None,
                    "mergeQueueEntry": None,
                },
                {"auto_merge_armed": False, "queue_position": None},
            ),
        }
        invalid_cases = {
            "partial data with errors": (
                {"errors": [{"message": "partial failure"}]},
                {
                    "state": "OPEN",
                    "mergedAt": None,
                    "autoMergeRequest": None,
                    "mergeQueueEntry": None,
                },
            ),
            "empty queue entry": (
                {},
                {
                    "state": "OPEN",
                    "mergedAt": None,
                    "autoMergeRequest": None,
                    "mergeQueueEntry": {},
                },
            ),
            "null queue fields": (
                {},
                {
                    "state": "OPEN",
                    "mergedAt": None,
                    "autoMergeRequest": None,
                    "mergeQueueEntry": {"position": None, "enqueuedAt": None},
                },
            ),
        }

        for document in documents:
            match = re.search(
                r"\| jq -e '([^'\n]+)'", document.read_text(encoding="utf-8")
            )
            self.assertIsNotNone(match, document)
            projection = match.group(1)
            for name, (pull_request, expected) in valid_cases.items():
                pull_request["labels"] = {"nodes": []}
                result = subprocess.run(
                    ["jq", "-e", projection],
                    input=json.dumps(
                        {"data": {"repository": {"pullRequest": pull_request}}}
                    ),
                    capture_output=True,
                    text=True,
                )
                with self.subTest(document=document.name, case=name):
                    self.assertEqual(result.returncode, 0, result.stderr)
                    output = json.loads(result.stdout)
                    self.assertEqual(output["state"], pull_request["state"])
                    self.assertEqual(output["mergedAt"], pull_request["mergedAt"])
                    self.assertEqual(
                        output["auto_merge_armed"], expected["auto_merge_armed"]
                    )
                    entry = output["merge_queue_entry"]
                    self.assertEqual(
                        None if entry is None else entry["position"],
                        expected["queue_position"],
                    )
            for name, (top_level, pull_request) in invalid_cases.items():
                pull_request["labels"] = {"nodes": []}
                payload = {
                    **top_level,
                    "data": {"repository": {"pullRequest": pull_request}},
                }
                result = subprocess.run(
                    ["jq", "-e", projection],
                    input=json.dumps(payload),
                    capture_output=True,
                    text=True,
                )
                with self.subTest(document=document.name, case=name):
                    self.assertNotEqual(result.returncode, 0, result.stdout)

    def test_review_bead_template_is_packet_complete(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn('--acceptance="1. Record reviewer identity', contents)
        self.assertIn('--design="Independent exact-head review', contents)

    def test_correction_worktree_has_an_explicit_re_review_hand_back(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn("Correction-to-re-review hand-back", contents)
        self.assertIn(
            "git -C <review-worktree> checkout -B agent/<original-id> origin/agent/<original-id>",
            contents,
        )
        self.assertIn("expected reviewer branch is `agent/<original-id>`", contents)

    def test_initial_review_bootstrap_uses_two_stage_branch_attestation(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn("Stage 1 — dispatch bootstrap", contents)
        self.assertIn("`agent/<review-id>`", contents)
        self.assertIn("Stage 2 — prepared-head attestation", contents)
        self.assertIn("`agent/<original-id>`", contents)
        self.assertIn("Re-review hand-back starts at Stage 2", contents)

    def test_post_merge_cleanup_maps_original_and_review_ids(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        cleanup = contents.split(
            "### Post-closure branch and worktree cleanup (merged PRs)", 1
        )[1].split("Priority rule:", 1)[0]
        for command in (
            'git push origin --delete "agent/${ORIGINAL_ID}"',
            'bd worktree remove ".worktrees/parallel-agents/${REVIEW_ID}"',
            'git branch -D "agent/${ORIGINAL_ID}"',
            'git branch -D "agent/${REVIEW_ID}"',
        ):
            self.assertIn(command, cleanup)
        self.assertIn(
            "the transferred worktree path remains keyed by `REVIEW_ID`",
            cleanup,
        )
        self.assertNotIn("agent/<id>", cleanup)

    def test_step_zero_uses_the_report_only_normalizer_then_reverifies_before_mutation(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertTrue(NORMALIZER.exists(), NORMALIZER)
        self.assertIn("scripts/normalize_pr_review_state.py", contents)
        self.assertIn("beads-pr-review-normalization/v1", contents)
        self.assertIn("immediately before each actual mutation", contents)
        self.assertIn("sole PR-state mutator", contents)
        self.assertIn("manual-triage", contents)
        for phrase in ("## Owner merge hold", "held-for-owner", "owner_merge_inventory",
                       "Merge-Performed: no", "PR-Closed: no", "normalizer v1 recommendations",
                       "hold-only blocker", "MERGED/CLOSED", "no atomic server guarantee"):
            self.assertIn(phrase, contents)
        self.assertIn("coordinator-loop.md#owner-merge-hold", SAFETY.read_text(encoding="utf-8"))
        # The fail-closed contract is canonical in the script docstring, not the
        # loop doc, so the coordinator does not re-read it every cycle.
        self.assertIn("module docstring", contents)
        docstring = NORMALIZER.read_text(encoding="utf-8").split('"""', 2)[1]
        for phrase in (
            "Fail-closed contract",
            "manual-triage",
            "self-referential",
            "resolver `issue_id`",
            "required label, status, or uniqueness",
            "creation timestamp",
            "`gh-pr:<N>`",
            "skip-command-failure",
            "cyclic-review-relation",
            "duplicate review-ID",
            "same original",
        ):
            self.assertIn(phrase, docstring)

    def test_selection_reads_the_finish_first_queue_and_its_docstring_contract(self) -> None:
        loop = LOOP.read_text(encoding="utf-8")
        self.assertTrue(RANKER.exists(), RANKER)
        self.assertIn("scripts/rank_ready_work.py", loop)
        self.assertIn("beads-work-queue/v1", loop)
        self.assertIn("module docstring", loop)
        docstring = RANKER.read_text(encoding="utf-8").split('"""', 2)[1]
        for phrase in ("Ranking contract", "Fail-closed", "`beads.max_lanes`", "`needs-shaping`", "prerequisites first"):
            self.assertIn(phrase, docstring)

    def test_parallel_coordinators_section_owns_identity_registry_and_adoption(self) -> None:
        safety = SAFETY.read_text(encoding="utf-8")
        section = safety.split("## Parallel Coordinators", 1)[1].split("\n## ", 1)[0]
        for phrase in ('--actor "$COORDINATOR_ID"', "beads.coordinator.", "beads.max_lanes", "--if-assignee", "extra_lanes"):
            self.assertIn(phrase, section)

    def test_every_documented_bd_mutation_carries_the_coordinator_actor(self) -> None:
        # Without --actor, a claim falls back to the shared git identity and two
        # coordinators read each other's claims as their own. A bare name such
        # as `bd update` in prose is a mention, not a command, and is skipped.
        for path in (LOOP, SAFETY, EPIC, COMMANDS):
            for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
                for match in BD_MUTATION.finditer(line):
                    with self.subTest(file=path.name, line=number):
                        self.assertIn('--actor "$COORDINATOR_ID"', match.group(1), line.strip())

    def test_registry_writes_and_releases_go_through_their_owners(self) -> None:
        # Hand-written registry timestamps keep dead coordinators "live"; a
        # `--status open` release keeps the old assignee on an idle bead.
        for path in (LOOP, SAFETY, EPIC, COMMANDS):
            contents = path.read_text(encoding="utf-8")
            with self.subTest(file=path.name):
                self.assertNotRegex(contents, r'kv (?:set|clear) "?beads\.coordinator\.')
                self.assertNotRegex(contents, r"update <[a-z-]+> --status open")
        loop = LOOP.read_text(encoding="utf-8")
        for phrase in ("coordinator_registry.py register", "coordinator_registry.py deregister", "unclaim <id>"):
            self.assertIn(phrase, loop)

    def test_a_failed_ranking_dispatches_nothing(self) -> None:
        step_one = LOOP.read_text(encoding="utf-8").split("## Step 1:", 1)[1].split("\n## ", 1)[0]
        self.assertIn("`status: fatal`: dispatch nothing this wake", step_one)
        self.assertIn("three consecutive fatal", step_one)
        self.assertNotIn("bd ready --json", step_one)

    def test_review_deduplication_uses_parsed_chronology_and_fails_closed(self) -> None:
        contents = LOOP.read_text(encoding="utf-8")
        self.assertIn("parsed creation chronology", contents)
        self.assertIn("partial manual triage", contents)
        self.assertIn("never choose by raw timestamp text", contents)

    def test_pr_ci_runs_only_the_report_only_fake_command_suites(self) -> None:
        contents = SKILL_AUDIT_WORKFLOW.read_text(encoding="utf-8")
        marker = "      - name: Run report-only Beads safety suites"
        self.assertIn(marker, contents)
        step = contents.split(marker, 1)[1].split(
            "      - name:", 1
        )[0]
        for command in (
            "uv run skills/personal/beads-orchestration/subskills/beads-coordinator/tests/test_normalize_pr_review_state.py",
            "uv run skills/personal/beads-orchestration/subskills/beads-coordinator/tests/test_rank_ready_work.py",
            "uv run skills/personal/beads-orchestration/subskills/beads-coordinator/tests/test_workflow_contract.py",
            "uv run skills/personal/beads-orchestration/subskills/beads-cleanup/tests/test_cleanup_scan.py",
            "uv run skills/personal/beads-orchestration/subskills/beads-pr-reviewer-worker/tests/test_skill_package.py",
            "uv run skills/personal/beads-orchestration/subskills/beads-pr-reviewer-worker/tests/test_scripts.py",
        ):
            self.assertIn(command, step)
        self.assertNotIn("bd ", step)
        self.assertNotIn("gh ", step)


if __name__ == "__main__":
    unittest.main()
