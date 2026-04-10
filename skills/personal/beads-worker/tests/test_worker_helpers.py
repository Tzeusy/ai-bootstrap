# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
ASSERT_CONTEXT = SKILL_ROOT / "scripts" / "assert_worker_context.py"
EMIT_REPORT = SKILL_ROOT / "scripts" / "emit_worker_report.py"


class AssertWorkerContextTests(unittest.TestCase):
    def test_context_passes_for_expected_worktree_and_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            worktree = Path(tmp) / "worker"
            repo_root = Path(tmp) / "repo"
            worktree.mkdir()
            repo_root.mkdir()

            result = subprocess.run(
                [
                    "python3",
                    str(ASSERT_CONTEXT),
                    "--worktree-path",
                    str(worktree),
                    "--repo-root",
                    str(repo_root),
                    "--issue-id",
                    "bd-42",
                    "--current-path",
                    str(worktree),
                    "--branch",
                    "agent/bd-42",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["expected_branch"], "agent/bd-42")

    def test_context_fails_for_wrong_branch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            worktree = Path(tmp) / "worker"
            repo_root = Path(tmp) / "repo"
            worktree.mkdir()
            repo_root.mkdir()

            result = subprocess.run(
                [
                    "python3",
                    str(ASSERT_CONTEXT),
                    "--worktree-path",
                    str(worktree),
                    "--repo-root",
                    str(repo_root),
                    "--issue-id",
                    "bd-42",
                    "--current-path",
                    str(worktree),
                    "--branch",
                    "feature/misbound",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "invalid-runtime-context")
        self.assertIn("branch", " ".join(payload["reasons"]))


class EmitWorkerReportTests(unittest.TestCase):
    def test_completed_pr_opened_requires_pr_metadata(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(EMIT_REPORT),
                "--status",
                "completed-pr-opened",
                "--issue-id",
                "bd-42",
                "--worktree-path",
                "/tmp/worktree",
                "--head-commit",
                "abc123",
                "--handoff-path",
                "pr-required",
                "--branch-pushed",
                "yes",
                "--summary",
                "Implemented the change.",
                "--quality-gate",
                "lint=pass",
                "--quality-gate",
                "typecheck=pass",
                "--quality-gate",
                "tests=pass",
                "--changes",
                "skills/personal/beads-worker/SKILL.md: tightened worker contract",
                "--tests",
                "python3 -m unittest: pass",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("PR-URL", result.stderr)

    def test_completed_direct_merge_candidate_emits_report(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(EMIT_REPORT),
                "--status",
                "completed-direct-merge-candidate",
                "--issue-id",
                "bd-42",
                "--worktree-path",
                "/tmp/worktree",
                "--head-commit",
                "abc123",
                "--handoff-path",
                "direct-merge-candidate",
                "--branch-pushed",
                "yes",
                "--summary",
                "Implemented the change.",
                "--quality-gate",
                "lint=pass",
                "--quality-gate",
                "typecheck=pass",
                "--quality-gate",
                "tests=pass",
                "--changes",
                "skills/personal/beads-worker/SKILL.md: tightened worker contract",
                "--tests",
                "python3 -m unittest: pass",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("## Worker Report: bd-42", result.stdout)
        self.assertIn("Status: completed-direct-merge-candidate", result.stdout)
        self.assertIn("PR-URL: n/a", result.stdout)

    def test_blocked_report_captures_recovery_details(self) -> None:
        result = subprocess.run(
            [
                "python3",
                str(EMIT_REPORT),
                "--status",
                "blocked-awaiting-coordinator",
                "--issue-id",
                "bd-42",
                "--worktree-path",
                "/tmp/worktree",
                "--head-commit",
                "abc123",
                "--handoff-path",
                "blocked-awaiting-coordinator",
                "--branch-pushed",
                "yes",
                "--recovery-state",
                "branch-pushed",
                "--resume-condition",
                "GitHub auth is restored",
                "--summary",
                "Push succeeded but PR creation is blocked on auth.",
                "--quality-gate",
                "lint=pass",
                "--quality-gate",
                "typecheck=pass",
                "--quality-gate",
                "tests=pass",
                "--changes",
                "skills/personal/beads-worker/SKILL.md: tightened worker contract",
                "--tests",
                "python3 -m unittest: pass",
                "--blockers-json",
                '[{"title":"Restore GitHub auth","type":"task","priority":1,"depends_on":"bd-42","rationale":"gh pr create failed due to auth","unblock_condition":"GitHub auth works again"}]',
                "--failing-command",
                "gh pr create --base main --head agent/bd-42",
                "--remote-branch",
                "origin/agent/bd-42",
                "--dirty-worktree",
                "no",
                "--unpushed-commits",
                "no",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("Recovery-Details:", result.stdout)
        self.assertIn("Failing-Command: gh pr create --base main --head agent/bd-42", result.stdout)
        self.assertIn("Remote-Branch: origin/agent/bd-42", result.stdout)


if __name__ == "__main__":
    unittest.main()
