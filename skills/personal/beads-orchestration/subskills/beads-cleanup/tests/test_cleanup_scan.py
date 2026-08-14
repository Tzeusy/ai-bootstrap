#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Behavioral tests for the cleanup subskill's report-only scan."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = SKILL_ROOT / "scripts" / "cleanup_scan.py"


class FakeBinDir:
    def __init__(self) -> None:
        self._tmp: tempfile.TemporaryDirectory[str] | None = None
        self.path: Path | None = None

    def __enter__(self) -> "FakeBinDir":
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name)
        return self

    def __exit__(self, *args: object) -> None:
        assert self._tmp is not None
        self._tmp.cleanup()

    def add(self, name: str, body: str) -> None:
        assert self.path is not None
        executable = self.path / name
        executable.write_text(f"#!/usr/bin/env python3\n{textwrap.dedent(body)}", encoding="utf-8")
        executable.chmod(0o755)

    def env(self, **extra: str) -> dict[str, str]:
        assert self.path is not None
        environment = os.environ.copy()
        environment["PATH"] = f"{self.path}:{environment.get('PATH', '')}"
        environment.update(extra)
        return environment


def install_fakes(fake_bin: FakeBinDir) -> None:
    fake_bin.add(
        "bd",
        """
        import json
        import os
        import sys

        fixture = json.loads(open(os.environ["CLEANUP_FIXTURE"], encoding="utf-8").read())
        with open(os.environ["CLEANUP_CALLS"], "a", encoding="utf-8") as calls:
            calls.write(json.dumps({"tool": "bd", "argv": sys.argv[1:]}) + "\\n")
        argv = sys.argv[1:]
        if argv[:1] == ["-C"]:
            argv = argv[2:]

        def fail(key):
            message = fixture.get("failures", {}).get(key)
            if message:
                print(message, file=sys.stderr)
                raise SystemExit(1)

        if argv[:2] == ["dep", "list"]:
            issue_id = argv[2]
            fail(f"bd-dep:{issue_id}")
            print(json.dumps(fixture.get("dependencies", {}).get(issue_id, [])))
            raise SystemExit(0)

        if argv[:2] == ["worktree", "list"]:
            fail("bd-worktree-list")
            print(fixture.get("worktrees_raw", ""))
            raise SystemExit(0)

        if "list" in argv:
            label = argv[argv.index("--label") + 1] if "--label" in argv else ""
            status = next((part.split("=", 1)[1] for part in argv if part.startswith("--status=")), "")
            key = f"bd-list:{status}:{label}"
            fail(key)
            if status == "in_progress":
                print(json.dumps(fixture.get("in_progress", [])))
            elif label == "review-running":
                print(json.dumps(fixture.get("review_running", [])))
            elif label == "pr-review" and status == "blocked":
                print(json.dumps(fixture.get("blocked_pr_review", [])))
            elif label == "pr-review-task":
                print(
                    json.dumps(
                        fixture.get(
                            "pr_review_tasks_all",
                            fixture.get("blocked_pr_review_tasks", []),
                        )
                    )
                )
            elif label == "pr-review":
                print(json.dumps(fixture.get("pr_review_all", [])))
            elif status == "blocked":
                print(json.dumps(fixture.get("blocked", [])))
            else:
                print(json.dumps([]))
            raise SystemExit(0)

        if "show" in argv:
            issue_id = argv[argv.index("show") + 1]
            fail(f"bd-show:{issue_id}")
            payload = fixture.get("shows", {}).get(issue_id)
            if payload is None:
                print("unmatched show " + issue_id, file=sys.stderr)
                raise SystemExit(1)
            print(json.dumps(payload))
            raise SystemExit(0)

        if argv[:2] == ["dolt", "status"]:
            fail("bd-dolt-status")
            print("healthy")
            raise SystemExit(0)
        if argv[:1] == ["doctor"]:
            fail("bd-doctor")
            print("healthy")
            raise SystemExit(0)
        print("unmatched bd command", file=sys.stderr)
        raise SystemExit(1)
        """,
    )
    fake_bin.add(
        "gh",
        """
        import json
        import os
        import sys

        fixture = json.loads(open(os.environ["CLEANUP_FIXTURE"], encoding="utf-8").read())
        with open(os.environ["CLEANUP_CALLS"], "a", encoding="utf-8") as calls:
            calls.write(json.dumps({"tool": "gh", "argv": sys.argv[1:]}) + "\\n")
        argv = sys.argv[1:]
        if argv[:2] == ["repo", "view"]:
            print("owner/repo")
            raise SystemExit(0)
        if argv[:2] == ["pr", "list"]:
            message = fixture.get("failures", {}).get("gh-pr-list")
            if message:
                print(message, file=sys.stderr)
                raise SystemExit(1)
            print(json.dumps(fixture.get("open_prs", [])))
            raise SystemExit(0)
        if argv[:2] == ["pr", "view"]:
            number = argv[2]
            message = fixture.get("failures", {}).get(f"gh-pr-view:{number}")
            if message:
                print(message, file=sys.stderr)
                raise SystemExit(1)
            payload = fixture.get("prs", {}).get(str(number))
            if payload is None:
                print("unmatched pr " + str(number), file=sys.stderr)
                raise SystemExit(1)
            print(json.dumps(payload))
            raise SystemExit(0)
        print("unmatched gh command", file=sys.stderr)
        raise SystemExit(1)
        """,
    )
    fake_bin.add(
        "git",
        """
        import json
        import os
        import sys

        fixture = json.loads(open(os.environ["CLEANUP_FIXTURE"], encoding="utf-8").read())
        with open(os.environ["CLEANUP_CALLS"], "a", encoding="utf-8") as calls:
            calls.write(json.dumps({"tool": "git", "argv": sys.argv[1:]}) + "\\n")
        argv = sys.argv[1:]

        def fail(key):
            message = fixture.get("failures", {}).get(key)
            if message:
                print(message, file=sys.stderr)
                raise SystemExit(1)

        if "ls-remote" in argv:
            branch = argv[-1].removeprefix("agent/")
            fail(f"git-ls-remote:{branch}")
            if branch in fixture.get("remote_branches", []):
                print("deadbeef\\trefs/heads/agent/" + branch)
            raise SystemExit(0)
        if "log" in argv:
            worktree = argv[argv.index("-C") + 1] if "-C" in argv else ""
            worktree_id = worktree.rstrip("/").split("/")[-1]
            fail(f"git-log:{worktree_id}")
            if worktree_id in fixture.get("unpublished_worktrees", []):
                print("abc123 useful commit")
            raise SystemExit(0)
        raise SystemExit(0)
        """,
    )


def bead(issue_id: str, status: str, **extra: object) -> dict[str, object]:
    return {"id": issue_id, "status": status, **extra}


def heartbeat(timestamp: str) -> str:
    return f"[beads-heartbeat]\nowner=coordinator:test\nlast_heartbeat_at={timestamp}\n[/beads-heartbeat]"


class CleanupScanTests(unittest.TestCase):
    maxDiff = None

    def run_fixture(
        self,
        fixture: dict[str, object],
        *,
        now: str = "2026-08-14T04:00:00Z",
    ) -> tuple[subprocess.CompletedProcess[str], list[dict[str, object]], str]:
        with tempfile.TemporaryDirectory() as tmp, FakeBinDir() as fake_bin:
            root = Path(tmp)
            repo_root = root / "repo"
            repo_root.mkdir()
            for worktree_id in fixture.get("worktree_dirs", []):
                (repo_root / ".worktrees" / "parallel-agents" / str(worktree_id)).mkdir(parents=True)
            fixture_path = root / "fixture.json"
            calls_path = root / "calls.jsonl"
            fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
            normalizer = None
            if "normalizer_stdout" in fixture:
                normalizer = root / "normalizer.py"
                normalizer.write_text(
                    "\n".join(
                        (
                            "import json",
                            "import os",
                            "import sys",
                            "fixture = json.loads(open(os.environ['CLEANUP_FIXTURE'], encoding='utf-8').read())",
                            "print(fixture['normalizer_stdout'])",
                            "raise SystemExit(int(fixture.get('normalizer_exit', 0)))",
                        )
                    ),
                    encoding="utf-8",
                )
            install_fakes(fake_bin)
            argv = [sys.executable, str(SCRIPT), "--repo-root", str(repo_root), "--now", now]
            if normalizer is not None:
                argv.extend(["--normalizer", str(normalizer)])
            result = subprocess.run(
                argv,
                capture_output=True,
                text=True,
                env=fake_bin.env(
                    CLEANUP_FIXTURE=str(fixture_path),
                    CLEANUP_CALLS=str(calls_path),
                ),
            )
            calls = [
                json.loads(line)
                for line in calls_path.read_text(encoding="utf-8").splitlines()
            ] if calls_path.exists() else []
        return result, calls, str(repo_root)

    def test_empty_scan_emits_the_compact_versioned_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, FakeBinDir() as fake_bin:
            repo_root = Path(tmp)
            fake_bin.add(
                "bd",
                """
                import json
                import sys

                if "list" in sys.argv:
                    print(json.dumps([]))
                elif "worktree" in sys.argv:
                    print("")
                else:
                    print("ok")
                """,
            )
            fake_bin.add("gh", "import json\nprint(json.dumps([]))")
            fake_bin.add("git", "raise SystemExit(0)")

            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(repo_root),
                    "--now",
                    "2026-08-14T04:00:00Z",
                ],
                capture_output=True,
                text=True,
                env=fake_bin.env(),
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "blockers": [],
                "claims": [],
                "dolt": {"doctor": "healthy", "status": "healthy"},
                "errors": [],
                "generated_at": "2026-08-14T04:00:00Z",
                "pr_review": {
                    "errors": [],
                    "findings": [],
                    "schema": "beads-pr-review-normalization/v1",
                    "self_heal_candidates": [],
                    "status": "empty",
                },
                "review_locks": [],
                "schema": "beads-cleanup-scan/v1",
                "status": "empty",
                "worktrees": [],
            },
        )
        self.assertEqual(result.stderr, "")

    def test_reports_stale_claims_dependencies_worktrees_locks_and_unpublished_work(self) -> None:
        fixture = {
            "in_progress": [
                bead("aib-stale", "in_progress", assignee="other", notes=heartbeat("2026-08-14T03:00:00Z")),
                bead("aib-live", "in_progress", assignee="other", notes=heartbeat("2026-08-14T03:50:00Z")),
            ],
            "blocked": [bead("aib-blocked", "blocked"), bead("aib-unblock", "blocked")],
            "review_running": [bead("aib-lock", "blocked", notes=heartbeat("2026-08-14T03:00:00Z"))],
            "dependencies": {
                "aib-blocked": [{"depends_on_id": "aib-dep-open"}, {"depends_on_id": "aib-dep-closed"}],
                "aib-unblock": [{"depends_on_id": "aib-dep-closed"}],
            },
            "shows": {
                "aib-dep-open": [bead("aib-dep-open", "open")],
                "aib-dep-closed": [bead("aib-dep-closed", "closed")],
                "aib-stale": [bead("aib-stale", "in_progress")],
                "aib-closed": [bead("aib-closed", "closed")],
            },
            "worktrees_raw": "worktree /safe/parallel-agents/aib-stale\nworktree /safe/parallel-agents/aib-closed\n",
            "worktree_dirs": ["aib-stale", "aib-closed"],
            "remote_branches": ["aib-stale", "aib-closed"],
            "unpublished_worktrees": ["aib-stale"],
            "blocked_pr_review": [],
            "blocked_pr_review_tasks": [],
            "open_prs": [],
        }

        result, calls, repo_root = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        stale = next(item for item in payload["claims"] if item["id"] == "aib-stale")
        self.assertEqual(stale["heartbeat_state"], "stale")
        self.assertTrue(stale["worktree_exists"])
        self.assertTrue(stale["remote_branch_exists"])
        self.assertTrue(stale["unpublished_work"])
        self.assertEqual(stale["recommendation"], "preserve-unpublished-work")
        live = next(item for item in payload["claims"] if item["id"] == "aib-live")
        self.assertEqual(live["heartbeat_state"], "fresh")
        self.assertEqual(live["recommendation"], "preserve-live-claim")
        blocked = next(item for item in payload["blockers"] if item["id"] == "aib-blocked")
        self.assertFalse(blocked["all_blockers_closed"])
        self.assertEqual(blocked["recommendation"], "remain-blocked")
        unblocked = next(item for item in payload["blockers"] if item["id"] == "aib-unblock")
        self.assertTrue(unblocked["all_blockers_closed"])
        self.assertEqual(unblocked["recommendation"], "unblock-candidate")
        lock = payload["review_locks"][0]
        self.assertEqual(lock["id"], "aib-lock")
        self.assertEqual(lock["recommendation"], "release-review-lock-candidate")
        worktree = next(item for item in payload["worktrees"] if item["worktree_id"] == "aib-closed")
        self.assertEqual(worktree["recommendation"], "cleanup-eligible-after-verification")
        self.assertNotIn(repo_root, result.stdout + result.stderr)
        self.assertTrue(any(call["tool"] == "git" for call in calls))

    def test_cleanup_embeds_canonical_dotted_review_findings_without_reparsing(self) -> None:
        original_id = "aib-swr.1"
        review_id = "aib-review.1"
        fixture = {
            "in_progress": [],
            "blocked": [bead(original_id, "blocked", labels=["pr-review"], external_ref="gh-pr:41")],
            "review_running": [],
            "blocked_pr_review": [
                bead(original_id, "blocked", labels=["pr-review"], external_ref="gh-pr:41"),
                bead(review_id, "blocked", labels=["pr-review", "pr-review-task"], created_at="2026-08-14T03:00:00Z"),
            ],
            "blocked_pr_review_tasks": [],
            "shows": {
                original_id: [bead(original_id, "blocked", external_ref="gh-pr:41")],
                review_id: [
                    {
                        "id": review_id,
                        "description": f"Original implementation bead: {original_id}\nhttps://github.com/owner/repo/pull/41",
                        "dependencies": [],
                    }
                ],
            },
            "prs": {
                "41": {
                    "number": 41,
                    "url": "https://github.com/owner/repo/pull/41",
                    "state": "OPEN",
                    "isDraft": False,
                    "mergeStateStatus": "CLEAN",
                    "reviewDecision": None,
                    "headRefName": f"agent/{original_id}",
                    "baseRefName": "main",
                    "headRefOid": "abc123",
                    "createdAt": "2026-08-14T03:00:00Z",
                    "mergedAt": None,
                }
            },
            "open_prs": [],
        }

        result, _, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        review = next(item for item in json.loads(result.stdout)["pr_review"]["findings"] if item["review_id"] == review_id)
        self.assertEqual(review["original_id"], original_id)
        self.assertEqual(review["recommendation"], "dispatch-canonical-review")

    def test_nonzero_normalizer_discards_even_valid_stdout_as_partial_manual_triage(self) -> None:
        normalizer_payload = {
            "errors": [],
            "findings": [],
            "generated_at": "2026-08-14T04:00:00Z",
            "schema": "beads-pr-review-normalization/v1",
            "self_heal_candidates": [
                {
                    "canonical_review_id": None,
                    "context_status": "resolved",
                    "cooldown_until": "2026-08-14T04:05:00Z",
                    "original_id": "aib-swr.1",
                    "pr_number": 41,
                    "recommendation": "self-heal-original-and-review-wiring",
                }
            ],
            "status": "success",
        }
        fixture = {
            "in_progress": [],
            "blocked": [],
            "review_running": [],
            "normalizer_stdout": json.dumps(normalizer_payload),
            "normalizer_exit": 9,
        }

        result, _, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(payload["pr_review"]["status"], "partial")
        self.assertEqual(payload["pr_review"]["findings"], [])
        self.assertEqual(payload["pr_review"]["self_heal_candidates"], [])
        self.assertIn({"code": "normalizer-failed", "scope": "pr-review"}, payload["errors"])

    def test_cleanup_rejects_bool_pr_number_from_normalizer_evidence(self) -> None:
        normalizer_payload = {
            "errors": [],
            "findings": [],
            "schema": "beads-pr-review-normalization/v1",
            "self_heal_candidates": [
                {
                    "canonical_review_id": None,
                    "context_status": "resolved",
                    "cooldown_until": "2026-08-14T04:05:00Z",
                    "original_id": "aib-swr.1",
                    "pr_number": True,
                    "recommendation": "self-heal-original-and-review-wiring",
                }
            ],
            "status": "success",
        }
        fixture = {
            "in_progress": [],
            "blocked": [],
            "review_running": [],
            "normalizer_stdout": json.dumps(normalizer_payload),
        }

        result, _, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(payload["pr_review"]["status"], "partial")
        candidate = payload["pr_review"]["self_heal_candidates"][0]
        self.assertEqual(candidate["context_status"], "invalid-pr-number")
        self.assertIsNone(candidate["pr_number"])
        self.assertEqual(candidate["recommendation"], "manual-triage")
        self.assertIn({"code": "invalid-pr-number", "scope": "pr-review"}, payload["pr_review"]["errors"])

    def test_error_bearing_success_normalizer_is_partial_manual_triage(self) -> None:
        normalizer_payload = {
            "errors": [{"code": "invalid-pr-created-at", "scope": "pr-state"}],
            "findings": [],
            "schema": "beads-pr-review-normalization/v1",
            "self_heal_candidates": [],
            "status": "success",
        }
        fixture = {
            "in_progress": [],
            "blocked": [],
            "review_running": [],
            "normalizer_stdout": json.dumps(normalizer_payload),
        }

        result, _, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(payload["pr_review"]["status"], "partial")
        self.assertIn({"code": "invalid-pr-created-at", "scope": "pr-state"}, payload["pr_review"]["errors"])
        self.assertIn({"code": "normalizer-failed", "scope": "pr-review"}, payload["errors"])

    def test_worktree_correlation_preserves_opaque_ids_containing_review(self) -> None:
        issue_id = "aib-release-review-preserve"
        fixture = {
            "in_progress": [],
            "blocked": [],
            "review_running": [],
            "shows": {issue_id: [bead(issue_id, "closed")]},
            "worktrees_raw": f"worktree /safe/parallel-agents/{issue_id}\\n",
            "worktree_dirs": [issue_id],
            "remote_branches": [issue_id],
            "blocked_pr_review": [],
            "blocked_pr_review_tasks": [],
            "open_prs": [],
        }

        result, calls, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        worktree = json.loads(result.stdout)["worktrees"][0]
        self.assertEqual(worktree["worktree_id"], issue_id)
        self.assertEqual(worktree["issue_id"], issue_id)
        self.assertEqual(worktree["issue_status"], "closed")
        self.assertEqual(worktree["recommendation"], "cleanup-eligible-after-verification")
        self.assertIn(["show", issue_id, "--json"], [call["argv"] for call in calls if call["tool"] == "bd"])

    def test_failed_git_evidence_never_recommends_releasing_a_stale_claim(self) -> None:
        secret = "TOKEN=top-secret /private/absolute/path Traceback"
        fixture = {
            "in_progress": [
                bead("aib-remote-failed", "in_progress", notes=heartbeat("2026-08-14T03:00:00Z")),
                bead("aib-log-failed", "in_progress", notes=heartbeat("2026-08-14T03:00:00Z")),
            ],
            "blocked": [],
            "review_running": [],
            "worktrees_raw": "worktree /safe/parallel-agents/aib-log-failed\\n",
            "worktree_dirs": ["aib-log-failed"],
            "remote_branches": ["aib-log-failed"],
            "blocked_pr_review": [],
            "blocked_pr_review_tasks": [],
            "open_prs": [],
            "failures": {
                "git-ls-remote:aib-remote-failed": secret,
                "git-log:aib-log-failed": secret,
            },
        }

        result, _, repo_root = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        for issue_id in ("aib-remote-failed", "aib-log-failed"):
            finding = next(item for item in payload["claims"] if item["id"] == issue_id)
            self.assertEqual(finding["recommendation"], "manual-triage")
        self.assertIn({"code": "command-failed", "scope": "claims"}, payload["errors"])
        for forbidden in ("TOKEN=top-secret", "/private/absolute/path", "Traceback", repo_root):
            self.assertNotIn(forbidden, result.stdout + result.stderr)

    def test_unknown_beads_states_are_null_and_force_manual_triage(self) -> None:
        secret_status = "TOKEN=top-secret /private/absolute/path Traceback"
        fixture = {
            "in_progress": [],
            "blocked": [bead("aib-blocked", "blocked")],
            "review_running": [bead("aib-lock", secret_status, notes=heartbeat("2026-08-14T03:00:00Z"))],
            "dependencies": {"aib-blocked": [{"depends_on_id": "aib-dependency"}]},
            "shows": {
                "aib-dependency": [bead("aib-dependency", secret_status)],
                "aib-worktree": [bead("aib-worktree", secret_status)],
            },
            "worktrees_raw": "worktree /safe/parallel-agents/aib-worktree\\n",
            "worktree_dirs": ["aib-worktree"],
            "blocked_pr_review": [],
            "blocked_pr_review_tasks": [],
            "open_prs": [],
        }

        result, _, repo_root = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        blocker = payload["blockers"][0]
        self.assertIsNone(blocker["dependencies"][0]["status"])
        self.assertEqual(blocker["recommendation"], "manual-triage")
        lock = payload["review_locks"][0]
        self.assertEqual(lock["recommendation"], "manual-triage")
        worktree = payload["worktrees"][0]
        self.assertIsNone(worktree["issue_status"])
        self.assertEqual(worktree["recommendation"], "manual-triage")
        for scope in ("blockers", "review-locks", "worktrees"):
            self.assertIn({"code": "invalid-bead-status", "scope": scope}, payload["errors"])
        for forbidden in ("TOKEN=top-secret", "/private/absolute/path", "Traceback", repo_root):
            self.assertNotIn(forbidden, result.stdout + result.stderr)

    def test_partial_and_fatal_errors_are_sanitized(self) -> None:
        secret = "TOKEN=top-secret /private/absolute/path Traceback"
        partial_fixture = {
            "in_progress": [],
            "blocked": [],
            "review_running": [],
            "blocked_pr_review": [],
            "blocked_pr_review_tasks": [],
            "open_prs": [],
            "failures": {"bd-dolt-status": secret, "bd-doctor": secret},
        }
        result, _, repo_root = self.run_fixture(partial_fixture)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        self.assertEqual(payload["dolt"], {"doctor": "unhealthy", "status": "unhealthy"})
        for forbidden in ("TOKEN=top-secret", "/private/absolute/path", "Traceback", repo_root):
            self.assertNotIn(forbidden, result.stdout + result.stderr)

        fatal_fixture = {
            "failures": {
                "bd-list:in_progress:": secret,
                "bd-list:blocked:": secret,
                "bd-list::review-running": secret,
                "bd-list:blocked:pr-review": secret,
                "bd-list:blocked:pr-review-task": secret,
                "gh-pr-list": secret,
                "bd-dolt-status": secret,
                "bd-doctor": secret,
                "bd-worktree-list": secret,
            }
        }
        fatal, _, _ = self.run_fixture(fatal_fixture)
        self.assertNotEqual(fatal.returncode, 0)
        self.assertEqual(json.loads(fatal.stdout)["status"], "fatal")
        for forbidden in ("TOKEN=top-secret", "/private/absolute/path", "Traceback"):
            self.assertNotIn(forbidden, fatal.stdout + fatal.stderr)

    def test_fake_commands_match_strict_read_only_argv_allowlists(self) -> None:
        fixture = {
            "in_progress": [],
            "blocked": [],
            "review_running": [],
            "blocked_pr_review": [],
            "blocked_pr_review_tasks": [],
            "open_prs": [],
        }
        result, calls, repo_root = self.run_fixture(fixture)
        self.assertEqual(result.returncode, 0, result.stderr)
        allowed = {
            "bd": {
                (
                    "-C",
                    repo_root,
                    "list",
                    "--status=blocked",
                    "--label",
                    "pr-review",
                    "--json",
                    "--limit",
                    "0",
                ),
                ("-C", repo_root, "list", "--label", "pr-review-task", "--json", "--limit", "0"),
                ("-C", repo_root, "list", "--status=in_progress", "--json", "--limit", "0"),
                ("-C", repo_root, "list", "--status=blocked", "--json", "--limit", "0"),
                ("-C", repo_root, "list", "--label", "review-running", "--json", "--limit", "0"),
                ("-C", repo_root, "worktree", "list"),
                ("-C", repo_root, "dolt", "status"),
                ("-C", repo_root, "doctor"),
            },
            "gh": {("pr", "list", "--state", "open", "--json", "number,headRefName,createdAt")},
            "git": set(),
        }
        self.assertTrue(calls)
        for call in calls:
            tool = call["tool"]
            argv = call["argv"]
            self.assertIsInstance(tool, str)
            self.assertIsInstance(argv, list)
            self.assertIn(tool, allowed, call)
            self.assertIn(tuple(argv), allowed[tool], call)

    def test_invalid_bootstrap_never_echoes_a_secret_or_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            secret_now = "TOKEN=top-secret /private/absolute/path Traceback"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(Path(tmp) / "missing"),
                    "--now",
                    secret_now,
                ],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fatal")
        self.assertIsNone(payload["generated_at"])
        for forbidden in ("TOKEN=top-secret", "/private/absolute/path", "Traceback", tmp):
            self.assertNotIn(forbidden, result.stdout + result.stderr)

    def test_unexpected_bootstrap_failure_never_emits_a_traceback_or_raw_now(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            loop = Path(tmp) / "loop"
            loop.symlink_to(loop)
            secret_now = "TOKEN=top-secret /private/absolute/path Traceback"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--repo-root",
                    str(loop),
                    "--now",
                    secret_now,
                ],
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fatal")
        self.assertIsNone(payload["generated_at"])
        for forbidden in ("TOKEN=top-secret", "/private/absolute/path", "Traceback", tmp):
            self.assertNotIn(forbidden, result.stdout + result.stderr)

    def test_malformed_list_data_is_a_sanitized_partial_report(self) -> None:
        fixture = {
            "in_progress": ["TOKEN=top-secret /private/absolute/path"],
            "blocked": [],
            "review_running": [],
            "blocked_pr_review": [],
            "blocked_pr_review_tasks": [],
            "open_prs": [],
        }

        result, _, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        self.assertIn({"code": "invalid-record", "scope": "claims"}, payload["errors"])
        self.assertNotIn("TOKEN=top-secret", result.stdout + result.stderr)
        self.assertNotIn("/private/absolute/path", result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
