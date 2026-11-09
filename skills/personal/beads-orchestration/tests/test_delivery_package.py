# /// script
# requires-python = ">=3.11"
# ///
"""Exercise package delivery against a process-isolated fake Beads store."""
from __future__ import annotations

import importlib.util
import copy
import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/delivery_package.py"
spec = importlib.util.spec_from_file_location("delivery_package", SCRIPT)
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)
FAKE_BD = '''#!/usr/bin/env python3
import fcntl, json, os, signal, sys
from pathlib import Path
args = sys.argv[1:]
actor = args[args.index('--actor')+1]
args = args[args.index('--actor')+2:]
path = Path(os.environ['FAKE_DB'])
with path.open('r+') as stream:
 fcntl.flock(stream, fcntl.LOCK_EX)
 state = json.load(stream)
 command, member = args[:2]
 if '--metadata' in args and ('--set-metadata' in args or '--unset-metadata' in args): sys.exit(1)
 row = state['rows'][member]
 if command == 'show':
  print(json.dumps([row])); sys.exit(0)
 def persist():
  stream.seek(0); json.dump(state, stream); stream.truncate(); stream.flush(); os.fsync(stream.fileno())
 if '--claim' in args:
  if state.get('race_on') == member:
   row['assignee'] = 'coord-other'; row['status'] = 'in_progress'; persist()
  if row.get('assignee') not in (None, '', actor): sys.exit(13)
  row['assignee'] = actor; row['status'] = 'in_progress'
  if state.get('gate_after_claim') == member: state['rows']['bd-prereq']['status'] = 'open'
  persist()
  if state.get('crash_on') == member:
   state.pop('crash_on'); persist(); os.kill(os.getppid(), signal.SIGKILL)
 else:
  if '--if-assignee' in args and row.get('assignee', '') != args[args.index('--if-assignee')+1]: sys.exit(13)
  if '--if-status' in args and row.get('status') != args[args.index('--if-status')+1]: sys.exit(13)
  i = 2
  while i < len(args):
   flag = args[i]
   if flag == '--json': i += 1; continue
   value = args[i+1]; i += 2
   if flag == '--assignee': row['assignee'] = value
   elif flag == '--status': row['status'] = value
   elif flag == '--unset-metadata': row.setdefault('metadata', {}).pop(value, None)
   elif flag == '--set-metadata':
    key, value = value.split('=', 1)
    row.setdefault('metadata', {})[key] = value
   elif flag == '--metadata': row.setdefault('metadata', {}).update(json.loads(value))
  persist()
 print(json.dumps([row]))
'''


def delivery(anchor="bd-a", members=None, owner="coord-owner"):
    return {"schema": "beads-delivery/v1", "anchor": anchor, "members": members or ["bd-a", "bd-b"], "owner": owner, "outcome": "bd-feature", "base_branch": "main", "packet": "docs/current.md#runtime-corrections"}


def row(member):
    return {"id": member, "status": "open", "assignee": "", "labels": [], "metadata": {}, "dependencies": []}


class DeliveryLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "bd").write_text(FAKE_BD)
        (self.root / "bd").chmod(0o755)
        self.store = self.root / "store.json"
        self.write({"rows": {m: row(m) for m in ("bd-a", "bd-b", "bd-c", "bd-prereq")}})
        self.manifest = self.root / "delivery.json"
        self.manifest.write_text(json.dumps(delivery()))
        self.journal = self.root / "journal.json"
        self.env = {**os.environ, "FAKE_DB": str(self.store), "PATH": str(self.root) + os.pathsep + os.environ["PATH"]}

    def write(self, state):
        self.store.write_text(json.dumps(state))

    def read(self):
        return json.loads(self.store.read_text())

    def run_package(self, command, *extra):
        return subprocess.run(["python3", str(SCRIPT), command, "--delivery-file", str(self.manifest), "--repo-root", str(self.root), "--journal", str(self.journal), *extra], capture_output=True, text=True, env=self.env)

    def test_related_corrections_claim_and_release_one_package_without_touching_independent_work(self):
        state = self.read()
        for member in ("bd-a", "bd-b"):
            state["rows"][member]["metadata"]["unrelated"] = {"enabled": True}
        self.write(state)
        result = self.run_package("claim")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        rows = self.read()["rows"]
        self.assertEqual(package.package_index(list(rows.values())), {"bd-a": "bd-a", "bd-b": "bd-a"})
        self.assertEqual(rows["bd-c"]["status"], "open")
        self.assertEqual(rows["bd-a"]["metadata"]["delivery"], delivery())
        self.assertEqual(rows["bd-a"]["metadata"]["unrelated"], {"enabled": True})
        released = self.run_package("release")
        self.assertEqual(released.returncode, 0, released.stdout)
        rows = self.read()["rows"]
        self.assertTrue(all(not rows[m]["assignee"] for m in ("bd-a", "bd-b")))
        self.assertEqual(rows["bd-a"]["status"], "open")  # Unfinished work returns to runnable discovery.
        self.assertEqual(package.package_index(list(rows.values())), {})
        self.assertEqual(rows["bd-a"]["metadata"]["unrelated"], {"enabled": True})
        self.assertEqual(rows["bd-b"]["metadata"]["unrelated"], {"enabled": True})

    def test_actual_nested_blocking_edges_reject_open_before_claim_and_allow_closed(self):
        for kind in ("actual", "legacy", "both"):
            for status in ("open", "closed"):
                with self.subTest(kind=kind, status=status):
                    self.journal = self.root / f"journal-{kind}-{status}.json"
                    state = {"rows": {m: row(m) for m in ("bd-a", "bd-b", "bd-c", "bd-prereq")}}
                    edge = ({"id": "bd-prereq", "dependency_type": "blocks"} if kind == "actual" else
                            {"depends_on_id": "bd-prereq", "issue_id": "bd-b", "type": "blocks"})
                    if kind == "both": edge.update(id="bd-prereq", dependency_type="blocks")
                    state["rows"]["bd-b"]["dependencies"] = [edge]
                    state["rows"]["bd-prereq"]["status"] = status
                    self.write(state)
                    result = self.run_package("claim")
                    if status == "open":
                        self.assertNotEqual(result.returncode, 0, result.stdout)
                        self.assertIn("external-blocker:bd-b:bd-prereq", result.stdout)
                        self.assertEqual(self.read(), state)
                        self.assertFalse(self.journal.exists())
                    else:
                        self.assertEqual(result.returncode, 0, result.stdout)
                        self.assertEqual(self.run_package("release").returncode, 0)
                        self.journal.unlink()

    def test_malformed_or_conflicting_dependency_identity_never_claims(self):
        for edges in ({}, [None], [{"id": "bd-prereq"}],
                      [{"id": "bd-prereq", "dependency_type": None}],
                      [{"id": "bd-prereq", "dependency_type": "blocks", "type": "parent-child"}],
                      [{"id": "bd-prereq", "depends_on_id": "bd-c", "type": "blocks"}],
                      [{"id": "bd-prereq", "issue_id": "bd-other", "type": "blocks"}],
                      [{"dependency_type": "blocks"}], [{"id": [], "dependency_type": "blocks"}]):
            with self.subTest(edges=edges):
                state = self.read(); state["rows"]["bd-b"]["dependencies"] = edges; self.write(state)
                result = self.run_package("claim")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertEqual(self.read(), state)
                self.assertFalse(self.journal.exists())

    def test_actual_internal_edges_allow_acyclic_members_and_refuse_cycles(self):
        state = self.read()
        state["rows"]["bd-a"]["dependencies"] = [{"id": "bd-b", "dependency_type": "blocks"}]
        state["rows"]["bd-b"]["dependencies"] = [{"id": "bd-a", "dependency_type": "blocks"}]
        self.write(state)
        result = self.run_package("claim")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("cyclic-package-dependencies", result.stdout)
        self.assertEqual(self.read(), state)
        self.assertFalse(self.journal.exists())
        state["rows"]["bd-b"]["dependencies"] = [{"id": "bd-c", "dependency_type": "parent-child"}]
        self.write(state)
        self.assertEqual(self.run_package("claim").returncode, 0)

    def test_reopened_actual_gate_after_acquisition_compensates_and_keeps_preowned_claim(self):
        state = self.read()
        state["gate_after_claim"] = "bd-b"
        state["rows"]["bd-a"].update(status="in_progress", assignee="coord-owner")
        state["rows"]["bd-b"]["dependencies"] = [{"id": "bd-prereq", "dependency_type": "blocks"}]
        state["rows"]["bd-prereq"].update(status="closed", assignee="coord-gate")
        self.write(state)
        result = self.run_package("claim")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("external-blocker:bd-b:bd-prereq", result.stdout)
        rows = self.read()["rows"]
        self.assertEqual((rows["bd-a"]["status"], rows["bd-a"]["assignee"]), ("in_progress", "coord-owner"))
        self.assertEqual((rows["bd-b"]["status"], rows["bd-b"]["assignee"]), ("open", ""))
        self.assertEqual((rows["bd-prereq"]["status"], rows["bd-prereq"]["assignee"]), ("open", "coord-gate"))
        self.assertEqual(json.loads(self.journal.read_text())["state"], "released")

    def test_stale_active_journal_cannot_erase_tracker_branch_on_release(self):
        self.assertEqual(self.run_package("claim").returncode, 0)
        state = self.read()
        state["rows"]["bd-a"]["metadata"]["delivery"]["branch"] = "agent/bd-a-vendors"
        self.write(state)
        journal_before = self.journal.read_bytes()
        result = self.run_package("release")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("journal-delivery-mismatch", result.stdout)
        self.assertEqual(self.read(), state)
        self.assertEqual(self.journal.read_bytes(), journal_before)

    def test_claim_returns_exact_explicit_accepted_branch(self):
        accepted = {**delivery(), "branch": "agent/bd-a-vendors-20261109"}
        self.manifest.write_text(json.dumps(accepted))
        result = self.run_package("claim")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(json.loads(result.stdout)["branch"], accepted["branch"])
        self.assertEqual(self.read()["rows"]["bd-a"]["metadata"]["delivery"], accepted)

    def test_invalid_accepted_branch_never_claims_or_creates_journal(self):
        before = self.read()
        for branch in (None, "", "main", "master", "HEAD", "review/bd-review", "refs/heads/a", "agent/a..b", "-option", "agent/.hidden", "agent/a.lock", "agent/a@{1}", "agent/a b", "agent/a\nnext"):
            with self.subTest(branch=branch):
                self.manifest.write_text(json.dumps({**delivery(), "branch": branch}))
                result = self.run_package("claim")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("invalid-delivery-branch", result.stdout)
                self.assertEqual(self.read(), before)
                self.assertFalse(self.journal.exists())

    def test_journal_cannot_release_matching_ids_in_a_different_repository(self):
        self.assertEqual(self.run_package("claim").returncode, 0)
        before = self.read()
        foreign = self.root / "different-repository"
        foreign.mkdir()
        result = self.run_package("release", "--repo-root", str(foreign))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("journal-repository-mismatch", result.stdout)
        self.assertEqual(self.read(), before)
        self.assertEqual(json.loads(self.journal.read_text())["state"], "active")

    def test_interrupted_recovery_reports_foreign_claim_without_touching_peer(self):
        state = self.read(); state["crash_on"] = "bd-b"; self.write(state)
        self.assertLess(self.run_package("claim").returncode, 0)
        state = self.read()
        state["rows"]["bd-b"]["assignee"] = "coord-peer"
        self.write(state)
        result = self.run_package("recover")
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["state"], "recovery-incomplete")
        self.assertEqual(payload["foreign_claims"], [{"id": "bd-b", "assignee": "coord-peer"}])
        self.assertEqual(payload["failures"], ["bd-b"])
        self.assertEqual(self.read()["rows"]["bd-b"]["assignee"], "coord-peer")
        self.assertEqual(self.read()["rows"]["bd-a"]["assignee"], "")
        self.assertEqual(json.loads(self.journal.read_text())["state"], "recovery-incomplete")

    def test_active_package_recovery_is_refused_without_undoing_delivery(self):
        self.assertEqual(self.run_package("claim").returncode, 0)
        before = self.read()
        result = self.run_package("recover")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("use-release-for-active-package", result.stdout)
        self.assertEqual(self.read(), before)
        self.assertEqual(json.loads(self.journal.read_text())["state"], "active")

    def test_partial_landing_release_and_new_package_preserve_acceptance_and_traceability(self):
        self.assertEqual(self.run_package("claim").returncode, 0)
        state = self.read()
        state["rows"]["bd-a"]["status"] = "closed"
        self.write(state)
        active_rows = list(state["rows"].values())
        self.assertEqual(package.package_index(active_rows)["bd-b"], "bd-a")
        result = self.run_package("release")
        self.assertEqual(result.returncode, 0, result.stdout)
        rows = self.read()["rows"]
        self.assertEqual(rows["bd-a"]["status"], "closed")
        self.assertEqual(rows["bd-b"]["status"], "open")
        self.assertEqual(rows["bd-a"]["metadata"]["delivery"]["state"], "released")
        self.assertEqual(rows["bd-a"]["metadata"]["delivery"]["members"], ["bd-a", "bd-b"])
        self.manifest.write_text(json.dumps(delivery("bd-b", ["bd-b"])))
        self.journal = self.root / "remaining-journal.json"
        self.assertEqual(self.run_package("claim").returncode, 0)
        self.assertEqual(package.package_index(list(self.read()["rows"].values())), {"bd-b": "bd-b"})
        self.assertEqual(self.read()["rows"]["bd-a"]["status"], "closed")

    def test_release_preserves_hard_blocked_member_state(self):
        self.assertEqual(self.run_package("claim").returncode, 0)
        state = self.read()
        state["rows"]["bd-b"]["status"] = "blocked"
        self.write(state)
        self.assertEqual(self.run_package("release").returncode, 0)
        self.assertEqual(self.read()["rows"]["bd-b"]["status"], "blocked")
        self.assertEqual(self.read()["rows"]["bd-b"]["assignee"], "")
        self.assertEqual(self.read()["rows"]["bd-a"]["status"], "open")

    def test_competing_member_claim_rolls_back_only_new_claims(self):
        state = self.read()
        state["race_on"] = "bd-b"
        state["rows"]["bd-a"].update(assignee="coord-owner", status="in_progress")
        self.write(state)
        result = self.run_package("claim")
        self.assertNotEqual(result.returncode, 0)
        rows = self.read()["rows"]
        self.assertEqual(rows["bd-a"]["assignee"], "coord-owner")
        self.assertEqual(rows["bd-b"]["assignee"], "coord-other")
        self.assertEqual(json.loads(self.journal.read_text())["state"], "released")

    def test_partial_claim_failure_releases_new_claim_and_preserves_foreign_winner(self):
        state = self.read(); state["race_on"] = "bd-b"; self.write(state)
        self.assertNotEqual(self.run_package("claim").returncode, 0)
        rows = self.read()["rows"]
        self.assertEqual(rows["bd-a"]["status"], "open")
        self.assertEqual(rows["bd-a"]["assignee"], "")
        self.assertEqual(rows["bd-b"]["assignee"], "coord-other")

    def test_session_death_after_claim_is_recoverable_from_durable_intent(self):
        state = self.read(); state["crash_on"] = "bd-b"; self.write(state)
        result = self.run_package("claim")
        self.assertLess(result.returncode, 0)
        journal = json.loads(self.journal.read_text())
        self.assertEqual(journal["attempted"], ["bd-a", "bd-b"])
        recovered = self.run_package("recover")
        self.assertEqual(recovered.returncode, 0, recovered.stdout)
        self.assertTrue(all(not self.read()["rows"][m]["assignee"] for m in ("bd-a", "bd-b")))
        self.assertTrue(self.manifest.exists())

    def test_shared_prerequisite_and_hard_hold_block_only_dependent_package(self):
        state = self.read()
        state["rows"]["bd-b"]["dependencies"] = [{"type": "blocks", "issue_id": "bd-b", "depends_on_id": "bd-prereq"}]
        state["rows"]["bd-prereq"].update(assignee="coord-substrate", status="in_progress")
        self.write(state)
        result = self.run_package("claim")
        self.assertIn("external-blocker", result.stdout)
        self.assertFalse(self.journal.exists())
        self.manifest.write_text(json.dumps(delivery("bd-c", ["bd-c"])))
        self.assertEqual(self.run_package("claim").returncode, 0)
        self.assertEqual(self.read()["rows"]["bd-prereq"]["assignee"], "coord-substrate")
        self.run_package("release")
        self.journal.unlink()
        state = self.read(); state["rows"]["bd-c"]["labels"] = ["owner-held"]; self.write(state)
        self.assertIn("member-held", self.run_package("claim").stdout)
        state = self.read(); state["rows"]["bd-c"]["labels"] = ["scope:local-state"]; self.write(state)
        self.assertIn("member-held", self.run_package("claim").stdout)


    def test_existing_package_member_cannot_join_another_session_package(self):
        self.assertEqual(self.run_package("claim").returncode, 0)
        self.manifest.write_text(json.dumps(delivery("bd-c", ["bd-c", "bd-b"], "coord-other")))
        self.journal = self.root / "other-journal.json"
        self.assertNotEqual(self.run_package("claim").returncode, 0)
        self.assertEqual(self.read()["rows"]["bd-c"]["assignee"], "")

    def test_internal_dependencies_are_ordered_but_cycles_are_rejected(self):
        state = self.read()
        state["rows"]["bd-b"]["dependencies"] = [{"type": "blocks", "depends_on_id": "bd-a"}]
        self.write(state)
        self.assertEqual(self.run_package("claim").returncode, 0)
        self.run_package("release"); self.journal.unlink()
        state = self.read()
        for member in ("bd-a", "bd-b"): state["rows"][member]["status"] = "open"
        state["rows"]["bd-a"]["dependencies"] = [{"type": "blocks", "depends_on_id": "bd-b"}]
        self.write(state)
        self.assertIn("cyclic-package-dependencies", self.run_package("claim").stdout)


class DeliveryAcceptanceTests(unittest.TestCase):
    def test_index_rejects_noncanonical_member_pr_association(self):
        rows = [row("bd-a"), row("bd-b")]
        for member in rows:
            member["assignee"] = "coord-owner"
            member["metadata"]["delivery_anchor"] = "bd-a"
        rows[0]["metadata"]["delivery"] = delivery()
        rows[1]["external_ref"] = "gh-pr:5"
        with self.assertRaisesRegex(ValueError, "noncanonical-member-pr-reference"):
            package.package_index(rows)
        rows[1]["external_ref"] = "jira:source-issue"
        self.assertEqual(package.package_index(rows), {"bd-a": "bd-a", "bd-b": "bd-a"})

    def test_foundation_merge_does_not_complete_feature_or_partial_member(self):
        results = [{"id": "bd-a", "status": "satisfied", "evidence": "runtime representation gate passed"}, {"id": "bd-b", "status": "blocked", "evidence": "activation awaits owner authority"}]
        self.assertEqual(package.closure_plan(delivery(), results, False)["close"], [])
        plan = package.closure_plan(delivery(), results, True)
        self.assertEqual(plan["close"], ["bd-a"])
        self.assertEqual(plan["retain"], ["bd-b"])
        self.assertFalse(plan["outcome_complete"])
        with self.assertRaises(ValueError): package.closure_plan(delivery(), results[:1], True)

    def test_unchanged_content_verdict_reused_source_change_and_runtime_observations_not_reused(self):
        inputs = {"src/runtime.py": "blob-a", "tests/test_runtime.py": "blob-b", "spec.md": "blob-c"}
        record = {"kind": "content", "verdict": "pass", "inputs": inputs}
        self.assertTrue(package.content_verdict_reusable(record, dict(inputs)))
        self.assertFalse(package.content_verdict_reusable(record, {**inputs, "src/runtime.py": "changed"}))
        self.assertFalse(package.content_verdict_reusable({**record, "kind": "runtime"}, inputs))


class MemoryReconciliationClient:
    """Closed tracker collaborator: exact read identities and owner/status CAS."""
    def __init__(self, root, rows):
        self.repo_root, self.owner = str(root), "coord-owner"
        self.rows = copy.deepcopy(rows)
        self.writes = []

    def show(self, member):
        return copy.deepcopy(self.rows[member])

    def call(self, *args):
        assert args[0] == "update" and "--claim" not in args
        record = self.rows[args[1]]
        assert record["assignee"] == args[args.index("--if-assignee") + 1]
        if "--if-status" in args:
            assert record["status"] == args[args.index("--if-status") + 1]
        if "--metadata" in args:
            record["metadata"].update(json.loads(args[args.index("--metadata") + 1]))
        for index, value in enumerate(args):
            if value == "--unset-metadata": record["metadata"].pop(args[index + 1], None)
        if "--assignee" in args: record["assignee"] = args[args.index("--assignee") + 1]
        if "--status" in args: record["status"] = args[args.index("--status") + 1]
        self.writes.append(args)
        return [copy.deepcopy(record)]


class ActiveBranchReconciliationTests(unittest.TestCase):
    def setUp(self):
        from unittest.mock import patch
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()
        self.source = Path(self.tmp.name) / "source"
        self.git_env = {**os.environ, "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null"}
        def git(*args):
            return subprocess.run(["git", *args], cwd=self.root, env=self.git_env,
                                  capture_output=True, text=True, check=True)
        git("init", "--template=", "-b", "main")
        git("config", "user.name", "Fixture")
        git("config", "user.email", "fixture@example.invalid")
        (self.root / "fixture").write_text("owned source")
        git("add", "fixture")
        git("-c", "core.hooksPath=/dev/null", "commit", "-m", "fixture")
        self.head = git("rev-parse", "HEAD").stdout.strip()
        self.old = delivery()
        self.target = {**self.old, "branch": "agent/bd-a-vendors"}
        git("-c", "core.hooksPath=/dev/null", "worktree", "add", "-b", self.target["branch"], str(self.source), "HEAD")
        self.pr = {"number": 60, "state": "OPEN", "headRefName": self.target["branch"],
                   "headRefOid": self.head, "baseRefName": "main", "isCrossRepository": False,
                   "headRepository": {"name": "fixture", "id": "nonessential-provider-field"},
                   "headRepositoryOwner": {"login": "owner", "id": "provider-extra"}}
        original_run = subprocess.run
        def run(argv, **kwargs):
            if argv[0] == "gh":
                self.assertEqual(Path(kwargs["cwd"]), self.root)
                output = "owner/fixture" if argv[1] == "repo" else json.dumps(self.pr)
                return subprocess.CompletedProcess(argv, 0, output, "")
            self.assertEqual(argv[0], "git")
            self.assertNotIn("GIT_DIR", kwargs["env"])
            self.assertNotIn("GIT_WORK_TREE", kwargs["env"])
            return original_run(argv, **kwargs)
        patcher = patch.object(package.subprocess, "run", side_effect=run)
        patcher.start(); self.addCleanup(patcher.stop)
        self.rows = {m: row(m) for m in self.old["members"]}
        for record in self.rows.values():
            record.update(assignee="coord-owner", status="blocked")
            record["metadata"] = {"delivery_anchor": "bd-a", "unrelated": {"keep": True}}
        self.rows["bd-a"]["metadata"]["delivery"] = copy.deepcopy(self.old)
        self.rows["bd-a"]["external_ref"] = "gh-pr:60"
        self.path = Path(self.tmp.name) / "journal.json"
        self.journal = {"schema": "beads-delivery-journal/v1", "repo_root": str(self.root),
                        "delivery": copy.deepcopy(self.old), "state": "active", "attempted": self.old["members"],
                        "before": {m: {"status": "open", "assignee": "", "metadata": {}} for m in self.old["members"]}}
        package.save_journal(self.path, self.journal, initial=True)
        self.client = MemoryReconciliationClient(self.root, self.rows)

    def reconcile(self, target=None):
        with package.journal_lock(self.path):
            journal = json.loads(self.path.read_text())
            return package.reconcile_branch(self.client, journal, self.path, target or self.target,
                worktree=str(self.source), pr=60, head=self.head)

    def test_exact_actual_git_and_pr_binding_amends_only_branch_and_repeats_idempotently(self):
        before = copy.deepcopy(self.client.rows)
        original_journal = copy.deepcopy(self.journal)
        self.assertEqual(self.reconcile()["reconciliation"], "complete")
        self.assertEqual(self.reconcile()["reconciliation"], "complete")
        self.assertEqual(len(self.client.writes), 1)
        journal = json.loads(self.path.read_text())
        self.assertEqual(journal["before"], original_journal["before"])
        self.assertEqual(journal["branch_reconciliation"]["from"], self.old)
        self.assertEqual(journal["delivery"], self.target)
        self.assertEqual(journal["branch_reconciliation"]["binding"]["head"], self.head)
        before["bd-a"]["metadata"]["delivery"] = self.target
        self.assertEqual(self.client.rows, before)
        released = package.release_claims(self.client, journal, self.path, recovery=False)
        self.assertEqual(released["state"], "released")
        self.assertEqual(self.client.rows["bd-a"]["metadata"]["delivery"], {**self.target, "state": "released"})
        self.assertEqual(json.loads(self.path.read_text())["branch_reconciliation"]["from"], self.old)

    def test_each_interrupted_phase_resumes_without_reclaim_or_duplicate_tracker_write(self):
        from unittest.mock import patch
        for malformed in ({}, [], "prepared", {"schema": "wrong", "phase": "complete"},
                          {"schema": "beads-branch-reconciliation/v1", "phase": "complete", "to": self.target}):
            with self.subTest(malformed=malformed):
                bad = {**self.journal, "branch_reconciliation": malformed}
                with self.assertRaisesRegex(ValueError, "reconciliation-incomplete"):
                    package.release_claims(self.client, bad, self.path, recovery=False)
                self.assertEqual(self.client.writes, [])
        for point in ("prepared", "tracker-applied-no-ack", "tracker-written", "complete"):
            with self.subTest(point=point):
                package.save_journal(self.path, copy.deepcopy(self.journal))
                self.client = MemoryReconciliationClient(self.root, self.rows)
                save, call = package.save_journal, self.client.call
                def interrupted_save(path, value, **kwargs):
                    save(path, value, **kwargs)
                    if value.get("branch_reconciliation", {}).get("phase") == point:
                        raise RuntimeError("injected power loss after durable journal phase")
                def interrupted_call(*args):
                    result = call(*args)
                    if point == "tracker-applied-no-ack":
                        raise RuntimeError("injected lost tracker acknowledgement")
                    return result
                with patch.object(package, "save_journal", side_effect=interrupted_save), \
                     patch.object(self.client, "call", side_effect=interrupted_call):
                    with self.assertRaises(RuntimeError): self.reconcile()
                interrupted = json.loads(self.path.read_text())
                if interrupted["branch_reconciliation"]["phase"] != "complete":
                    with self.assertRaisesRegex(ValueError, "reconciliation-incomplete"):
                        package.release_claims(self.client, interrupted, self.path, recovery=False)
                self.assertEqual(self.reconcile()["reconciliation"], "complete")
                self.assertEqual(len(self.client.writes), 1)
                final = json.loads(self.path.read_text())
                self.assertEqual(final["delivery"], self.target)
                self.assertEqual(final["branch_reconciliation"]["from"], self.old)
                self.assertEqual(final["before"], self.journal["before"])

    def test_wrong_identity_provider_git_and_foreign_claims_refuse_without_prepare(self):
        for key, value in (("owner", "coord-other"), ("members", ["bd-a"]), ("packet", "other"),
                           ("outcome", "bd-other"), ("base_branch", "other"), ("branch", "main")):
            with self.subTest(identity=key):
                with self.assertRaises(ValueError): self.reconcile({**self.target, key: value})
                self.assertEqual(json.loads(self.path.read_text()), self.journal)
        for key, value in (("state", "CLOSED"), ("headRefName", "agent/bd-a-neighbor"),
                           ("headRefOid", "0" * 40), ("baseRefName", "other"), ("isCrossRepository", True),
                           ("number", 61), ("headRepository", {"name": "other"})):
            with self.subTest(provider=key):
                original = copy.deepcopy(self.pr)
                self.pr[key] = value
                with self.assertRaises(ValueError): self.reconcile()
                self.pr = original
                self.assertEqual(json.loads(self.path.read_text()), self.journal)
        for mutate in ("foreign-owner", "wrong-pointer", "wrong-pr", "held", "released"):
            with self.subTest(tracker=mutate):
                self.client = MemoryReconciliationClient(self.root, self.rows)
                if mutate == "foreign-owner": self.client.rows["bd-b"]["assignee"] = "coord-peer"
                if mutate == "wrong-pointer": self.client.rows["bd-b"]["metadata"]["delivery_anchor"] = "bd-c"
                if mutate == "wrong-pr": self.client.rows["bd-a"]["external_ref"] = "gh-pr:61"
                if mutate == "held": self.client.rows["bd-b"]["labels"] = ["owner-held"]
                if mutate == "released": self.client.rows["bd-a"]["metadata"]["delivery"]["state"] = "released"
                with self.assertRaises(ValueError): self.reconcile()
                self.assertEqual(self.client.writes, [])
                self.assertEqual(json.loads(self.path.read_text()), self.journal)
        self.client = MemoryReconciliationClient(self.root, self.rows)
        (self.source / "fixture").write_text("unexpected dirty source")
        with self.assertRaisesRegex(ValueError, "tracked-source-dirty"): self.reconcile()
        self.assertEqual(self.client.writes, [])

    def test_prepared_foreign_takeover_and_tracker_phase_regression_never_overwrite(self):
        from unittest.mock import patch
        for phase in ("prepared", "tracker-written"):
            with self.subTest(phase=phase):
                package.save_journal(self.path, copy.deepcopy(self.journal))
                self.client = MemoryReconciliationClient(self.root, self.rows)
                save = package.save_journal
                def crash(path, value, **kwargs):
                    save(path, value, **kwargs)
                    if value.get("branch_reconciliation", {}).get("phase") == phase:
                        raise RuntimeError("crash")
                with patch.object(package, "save_journal", side_effect=crash):
                    with self.assertRaises(RuntimeError): self.reconcile()
                if phase == "prepared": self.client.rows["bd-b"]["assignee"] = "coord-peer"
                else: self.client.rows["bd-a"]["metadata"]["delivery"] = copy.deepcopy(self.old)
                before = copy.deepcopy(self.client.rows)
                with self.assertRaises(ValueError): self.reconcile()
                self.assertEqual(self.client.rows, before)

    def test_journal_consumers_cannot_overlap(self):
        with package.journal_lock(self.path):
            with self.assertRaises(BlockingIOError):
                with package.journal_lock(self.path): pass


@unittest.skipUnless(shutil.which("bd"), "native bd CLI is unavailable")
class NativeDeliveryIntegrationTests(unittest.TestCase):
    """Use a fresh embedded database, never the developer's shared server."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="beads-delivery-native-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.repo = self.root / "repo"
        self.repo.mkdir()
        self.native_bd = shutil.which("bd")
        self.env = {key: value for key, value in os.environ.items() if key in {"PATH", "HOME", "USER", "LOGNAME", "LANG", "LC_ALL", "TMPDIR"}}
        self.run_native(["git", "init", "-q", str(self.repo)])
        self.run_native(["git", "-C", str(self.repo), "config", "user.name", "Delivery fixture"])
        self.run_native(["git", "-C", str(self.repo), "config", "user.email", "fixture@example.invalid"])
        self.run_native([self.native_bd, "init", "--prefix", "pkg", "--non-interactive", "--skip-hooks", "--skip-agents", "--quiet"])
        config = json.loads((self.repo / ".beads/metadata.json").read_text())
        self.assertEqual(config.get("dolt_mode"), "embedded", "Native integration requires an isolated embedded DB")
        self.members = [self.bd("create", "--title", title, "--type", "task", "--description", "Isolated delivery fixture", "--silent").stdout.strip() for title in ("Related adapter correction A", "Related adapter correction B")]
        self.delivery = delivery(self.members[0], self.members)
        self.manifest = self.root / "delivery.json"
        self.manifest.write_text(json.dumps(self.delivery))
        self.journal = self.root / "journal.json"

    def run_native(self, command, *, env=None, check=True):
        return subprocess.run(command, cwd=self.repo, env=env or self.env, capture_output=True, text=True, check=check, timeout=60)

    def bd(self, *args):
        return self.run_native([self.native_bd, "-C", str(self.repo), "--actor", self.delivery["owner"] if hasattr(self, "delivery") else "coord-owner", *args])

    def show(self, member):
        value = json.loads(self.bd("show", member, "--json").stdout)
        return value[0] if isinstance(value, list) else value

    def run_package(self, command, *, env=None):
        return self.run_native(["python3", str(SCRIPT), command, "--delivery-file", str(self.manifest), "--repo-root", str(self.repo), "--journal", str(self.journal)], env=env, check=False)

    def test_native_claim_release_preserve_typed_manifest_and_unrelated_metadata(self):
        for member in self.members:
            self.bd("update", member, "--metadata", json.dumps({"unrelated": {"enabled": True, "revision": 7}}))
            self.bd("update", member, "--set-metadata", 'literal={"enabled":true}')
            self.assertEqual(package.metadata(self.show(member))["literal"], '{"enabled":true}')
        claimed = self.run_package("claim")
        self.assertEqual(claimed.returncode, 0, claimed.stdout + claimed.stderr)
        rows = [self.show(member) for member in self.members]
        self.assertEqual(package.metadata(rows[0])["delivery"], self.delivery)
        self.assertIsInstance(package.metadata(rows[0])["delivery"], dict)
        self.assertEqual(package.package_index(rows), dict.fromkeys(self.members, self.members[0]))
        released = self.run_package("release")
        self.assertEqual(released.returncode, 0, released.stdout + released.stderr)
        for member in self.members:
            current = self.show(member)
            self.assertEqual(current["status"], "open")
            self.assertFalse(current.get("assignee"))
            self.assertNotIn("delivery_anchor", package.metadata(current))
            self.assertEqual(package.metadata(current)["unrelated"], {"enabled": True, "revision": 7})
            self.assertEqual(package.metadata(current)["literal"], '{"enabled":true}')
        self.assertEqual(package.metadata(self.show(self.members[0]))["delivery"], {**self.delivery, "state": "released"})

    def test_native_interrupted_metadata_publication_recovers_typed_prior_receipt(self):
        anchor = self.members[0]
        previous = {**self.delivery, "packet": "docs/previous.md", "state": "released"}
        self.bd("update", anchor, "--claim", "--metadata", json.dumps({"delivery": previous, "unrelated": {"keep": True}}))
        shim_dir = self.root / "shim"
        shim_dir.mkdir()
        shim = shim_dir / "bd"
        shim.write_text("""#!/usr/bin/env python3
import os, signal, subprocess, sys
result = subprocess.run([os.environ['NATIVE_BD'], *sys.argv[1:]], capture_output=True, text=True)
sys.stdout.write(result.stdout)
sys.stderr.write(result.stderr)
if result.returncode == 0 and '--metadata' in sys.argv and os.environ.get('NATIVE_CRASH_AFTER_METADATA') == 'yes':
    os.kill(os.getppid(), signal.SIGKILL)
sys.exit(result.returncode)
""")
        shim.chmod(0o755)
        crash_env = {**self.env, "PATH": str(shim_dir) + os.pathsep + self.env["PATH"], "NATIVE_BD": self.native_bd, "NATIVE_CRASH_AFTER_METADATA": "yes"}
        interrupted = self.run_package("claim", env=crash_env)
        self.assertLess(interrupted.returncode, 0)
        self.assertEqual(package.metadata(self.show(anchor))["delivery"], self.delivery)
        recovery = self.run_package("recover")
        self.assertEqual(recovery.returncode, 0, recovery.stdout + recovery.stderr)
        restored = self.show(anchor)
        self.assertEqual(package.metadata(restored)["delivery"], previous)
        self.assertIsInstance(package.metadata(restored)["delivery"], dict)
        self.assertEqual(package.metadata(restored)["unrelated"], {"keep": True})
        self.assertEqual(restored["assignee"], self.delivery["owner"])
        self.assertEqual(restored["status"], "in_progress")
        untouched = self.show(self.members[1])
        self.assertEqual(untouched["status"], "open")
        self.assertFalse(untouched.get("assignee"))
        self.assertNotIn("delivery_anchor", package.metadata(untouched))


if __name__ == "__main__":
    unittest.main()
