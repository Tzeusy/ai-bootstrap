# /// script
# requires-python = ">=3.11"
# ///
"""Exercise package delivery against a process-isolated fake Beads store."""
from __future__ import annotations

import importlib.util
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
  row['assignee'] = actor; row['status'] = 'in_progress'; persist()
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
