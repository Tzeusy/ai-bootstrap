# /// script
# requires-python = ">=3.11"
# ///
"""Behavioral tests for beads-pr-reviewer-worker scripts.

Tests use fake `gh`, `git`, and `bd` executables injected via PATH so the
scripts can be exercised without real GitHub / git / Beads access.  Each test
creates a temporary bin directory, writes small Python scripts that return
canned JSON, then runs the real script under test as a subprocess.
"""

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
SCRIPTS = SKILL_ROOT / "scripts"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

class FakeBinDir:
    """Context manager that owns a temporary directory of fake executables."""

    def __init__(self):
        self._tmp = None
        self.path: Path | None = None

    def __enter__(self) -> "FakeBinDir":
        self._tmp = tempfile.TemporaryDirectory()
        self.path = Path(self._tmp.name)
        return self

    def __exit__(self, *args) -> None:
        self._tmp.cleanup()

    def add(self, name: str, body: str) -> None:
        """Write a fake executable with the given Python body."""
        exe = self.path / name
        exe.write_text(f"#!/usr/bin/env python3\n{textwrap.dedent(body)}")
        exe.chmod(0o755)

    def env(self, **extra: str) -> dict:
        """Return an env dict with this dir prepended to PATH."""
        env = os.environ.copy()
        env["PATH"] = f"{self.path}:{env.get('PATH', '')}"
        env.update(extra)
        return env


def run_script(script_name: str, args: list[str], env: dict | None = None) -> subprocess.CompletedProcess:
    script = SCRIPTS / script_name
    return subprocess.run(
        [sys.executable, str(script)] + args,
        capture_output=True,
        text=True,
        env=env,
    )


# ---------------------------------------------------------------------------
# discover_quality_gates.py — no external tools, pure filesystem
# ---------------------------------------------------------------------------

class DiscoverQualityGatesTests(unittest.TestCase):
    def test_empty_directory_returns_no_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "discover_quality_gates.py")],
                capture_output=True,
                text=True,
                cwd=tmp,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["commands"], {})

    def test_package_json_with_scripts_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            pkg = {"scripts": {"lint": "eslint .", "test": "jest", "build": "tsc"}}
            (Path(tmp) / "package.json").write_text(json.dumps(pkg))
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "discover_quality_gates.py")],
                capture_output=True,
                text=True,
                cwd=tmp,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("lint", payload["commands"])
        self.assertIn("test", payload["commands"])
        # build is not a tracked gate
        self.assertNotIn("build", payload["commands"])

    def test_makefile_with_lint_target_discovered(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "Makefile").write_text("lint:\n\tflake8 .\ntypecheck:\n\tmypy .\n")
            result = subprocess.run(
                [sys.executable, str(SCRIPTS / "discover_quality_gates.py")],
                capture_output=True,
                text=True,
                cwd=tmp,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn("lint", payload["commands"])
        self.assertIn("typecheck", payload["commands"])


# ---------------------------------------------------------------------------
# evaluate_merge_readiness.py
# ---------------------------------------------------------------------------

def _make_gh_evaluate(bin_dir: FakeBinDir, *, pr_state: str = "OPEN",
                       is_draft: bool = False, merge_state: str = "CLEAN",
                       review_decision: str | None = None, unresolved: int = 0,
                       check_states: list[str] | None = None,
                       checks_error: str | None = None) -> None:
    """Configure a fake `gh` for evaluate_merge_readiness tests."""
    thread_nodes = json.dumps([{"isResolved": False}] * unresolved +
                              [{"isResolved": True}] * 0)
    pr_json = json.dumps({
        "state": pr_state,
        "isDraft": is_draft,
        "mergeStateStatus": merge_state,
        "reviewDecision": review_decision,
        "mergedAt": None,
        "url": "https://github.com/owner/repo/pull/42",
        "baseRefName": "main",
        "headRefName": "agent/test-42",
    })
    if check_states is None:
        checks_json = json.dumps([{"state": "SUCCESS"}])
    else:
        checks_json = json.dumps([{"state": s} for s in check_states])
    checks_error_body = f'print({repr(checks_error)}, file=__import__("sys").stderr); raise SystemExit(1)' if checks_error else ""

    bin_dir.add("gh", f"""
import sys
import json

argv = sys.argv[1:]
cmd = ' '.join(argv)

if 'pr' in argv and 'view' in argv and '--json' in argv:
    print({repr(pr_json)})
    sys.exit(0)

if 'pr' in argv and 'checks' in argv:
    {checks_error_body or f'print({repr(checks_json)}); sys.exit(0)'}

if 'api' in argv and 'graphql' in argv:
    # Return thread count query response
    nodes = {repr(thread_nodes)}
    payload = {{"data": {{"repository": {{"pullRequest": {{"reviewThreads": {{"nodes": json.loads(nodes), "pageInfo": {{"hasNextPage": False, "endCursor": None}}}}}}}}}}}}
    print(json.dumps(payload))
    sys.exit(0)

print(json.dumps({{"error": "unmatched: " + cmd}}), file=sys.stderr)
sys.exit(1)
""")


class EvaluateMergeReadinessTests(unittest.TestCase):
    def test_merge_ok_when_all_conditions_green(self) -> None:
        with FakeBinDir() as fbd:
            _make_gh_evaluate(fbd, pr_state="OPEN", is_draft=False,
                              merge_state="CLEAN", unresolved=0,
                              check_states=["SUCCESS"])
            result = run_script("evaluate_merge_readiness.py",
                                ["--owner", "owner", "--repo", "repo", "--pr-number", "42"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["merge_ok"])
        self.assertEqual(payload["reasons"], [])

    def test_merge_blocked_by_unresolved_threads(self) -> None:
        with FakeBinDir() as fbd:
            _make_gh_evaluate(fbd, unresolved=2)
            result = run_script("evaluate_merge_readiness.py",
                                ["--owner", "owner", "--repo", "repo", "--pr-number", "42"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["merge_ok"])
        self.assertTrue(any("unresolved_threads" in r for r in payload["reasons"]))

    def test_merge_blocked_by_failed_required_checks(self) -> None:
        with FakeBinDir() as fbd:
            _make_gh_evaluate(fbd, check_states=["FAILURE"])
            result = run_script("evaluate_merge_readiness.py",
                                ["--owner", "owner", "--repo", "repo", "--pr-number", "42"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["merge_ok"])
        self.assertTrue(any("required_non_green" in r for r in payload["reasons"]))

    def test_merge_blocked_for_draft_pr(self) -> None:
        with FakeBinDir() as fbd:
            _make_gh_evaluate(fbd, is_draft=True)
            result = run_script("evaluate_merge_readiness.py",
                                ["--owner", "owner", "--repo", "repo", "--pr-number", "42"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["merge_ok"])
        self.assertIn("draft", payload["reasons"])

    def test_merge_blocked_for_closed_pr(self) -> None:
        with FakeBinDir() as fbd:
            _make_gh_evaluate(fbd, pr_state="CLOSED")
            result = run_script("evaluate_merge_readiness.py",
                                ["--owner", "owner", "--repo", "repo", "--pr-number", "42"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["merge_ok"])
        self.assertTrue(any("state=CLOSED" in r for r in payload["reasons"]))

    def test_merge_blocked_by_changes_requested(self) -> None:
        with FakeBinDir() as fbd:
            _make_gh_evaluate(fbd, review_decision="CHANGES_REQUESTED")
            result = run_script("evaluate_merge_readiness.py",
                                ["--owner", "owner", "--repo", "repo", "--pr-number", "42"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertFalse(payload["merge_ok"])
        self.assertTrue(any("CHANGES_REQUESTED" in r for r in payload["reasons"]))

    def test_pending_checks_block_merge(self) -> None:
        with FakeBinDir() as fbd:
            _make_gh_evaluate(fbd, check_states=["PENDING"])
            result = run_script("evaluate_merge_readiness.py",
                                ["--owner", "owner", "--repo", "repo", "--pr-number", "42"],
                                env=fbd.env())
        payload = json.loads(result.stdout)
        self.assertFalse(payload["merge_ok"])
        self.assertTrue(any("required_non_green" in r for r in payload["reasons"]))

    def test_skipped_checks_allow_merge(self) -> None:
        with FakeBinDir() as fbd:
            _make_gh_evaluate(fbd, check_states=["SKIPPED"])
            result = run_script("evaluate_merge_readiness.py",
                                ["--owner", "owner", "--repo", "repo", "--pr-number", "42"],
                                env=fbd.env())
        payload = json.loads(result.stdout)
        self.assertTrue(payload["merge_ok"])

    def test_required_checks_unavailable_fails_closed(self) -> None:
        with FakeBinDir() as fbd:
            _make_gh_evaluate(fbd, checks_error="fatal: unable to fetch checks")
            result = run_script("evaluate_merge_readiness.py",
                                ["--owner", "owner", "--repo", "repo", "--pr-number", "42"],
                                env=fbd.env())
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stderr)
        self.assertIn("error_code", payload)

    def test_dry_run_flag_accepted(self) -> None:
        with FakeBinDir() as fbd:
            _make_gh_evaluate(fbd)
            result = run_script("evaluate_merge_readiness.py",
                                ["--owner", "owner", "--repo", "repo", "--pr-number", "42", "--dry-run"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)


# ---------------------------------------------------------------------------
# resolve_review_context.py
# ---------------------------------------------------------------------------

class ResolveReviewContextTests(unittest.TestCase):
    def _make_bins(self, bin_dir: FakeBinDir, *,
                   description: str = "Original implementation bead: aib-abc\nhttps://github.com/owner/repo/pull/99",
                   bd_list: list | None = None) -> None:
        review_json = json.dumps([{
            "id": "aib-xyz",
            "description": description,
            "dependencies": [],
        }])
        bd_list_json = json.dumps(bd_list or [])
        pr_json = json.dumps({
            "number": 99,
            "url": "https://github.com/owner/repo/pull/99",
            "state": "OPEN",
            "isDraft": False,
            "mergeStateStatus": "CLEAN",
            "reviewDecision": None,
            "headRefName": "agent/aib-abc",
            "baseRefName": "main",
            "mergedAt": None,
            "headRefOid": "abc123",
        })
        original_json = json.dumps([{
            "id": "aib-abc",
            "description": "Implement thing",
            "external_ref": "gh-pr:99",
        }])

        bin_dir.add("bd", f"""
import sys
import json

argv = sys.argv[1:]
if 'show' in argv:
    issue_id = argv[argv.index('show') + 1]
    if issue_id == 'aib-xyz':
        print({repr(review_json)})
        sys.exit(0)
    elif issue_id == 'aib-abc':
        print({repr(original_json)})
        sys.exit(0)

if 'list' in argv:
    print({repr(bd_list_json)})
    sys.exit(0)

print(json.dumps({{"error": "unmatched bd: " + ' '.join(argv)}}), file=sys.stderr)
sys.exit(1)
""")
        bin_dir.add("gh", f"""
import sys
import json

argv = sys.argv[1:]
cmd = ' '.join(argv)

if 'repo' in argv and 'view' in argv:
    print('owner/repo')
    sys.exit(0)

if 'pr' in argv and 'view' in argv:
    print({repr(pr_json)})
    sys.exit(0)

print(json.dumps({{"error": "unmatched gh: " + cmd}}), file=sys.stderr)
sys.exit(1)
""")

    def test_success_resolves_context_from_description(self) -> None:
        with FakeBinDir() as fbd:
            self._make_bins(fbd)
            result = run_script("resolve_review_context.py",
                                ["--issue-id", "aib-xyz"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["original_id"], "aib-abc")
        self.assertEqual(payload["pr_number"], 99)
        self.assertEqual(payload["owner"], "owner")
        self.assertEqual(payload["repo"], "repo")

    def test_ambiguous_original_id_fails(self) -> None:
        # Both patterns match but yield different IDs — the real ambiguity case.
        # resolve_review_context uses re.search per-pattern, so repeating the
        # same pattern line only captures the first match; to get two distinct
        # IDs we need to trigger both regex patterns.
        description = ("Original implementation bead: aib-abc\n"
                       "Review target bead: aib-def\n"
                       "https://github.com/owner/repo/pull/99")
        with FakeBinDir() as fbd:
            self._make_bins(fbd, description=description)
            result = run_script("resolve_review_context.py",
                                ["--issue-id", "aib-xyz"],
                                env=fbd.env())
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stderr)
        self.assertIn("ambiguous", payload["error_code"])

    def test_missing_original_id_fails(self) -> None:
        with FakeBinDir() as fbd:
            self._make_bins(fbd, description="No original bead here", bd_list=[])
            result = run_script("resolve_review_context.py",
                                ["--issue-id", "aib-xyz"],
                                env=fbd.env())
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stderr)
        self.assertIn("missing", payload["error_code"])


# ---------------------------------------------------------------------------
# prepare_pr_branch.py
# ---------------------------------------------------------------------------

class PreparePrBranchTests(unittest.TestCase):
    def test_success_returns_ready(self) -> None:
        with FakeBinDir() as fbd:
            fbd.add("git", """
import sys
import json

argv = sys.argv[1:]
# All git commands succeed; diff returns empty (no beads divergence)
if argv[:1] == ['diff']:
    print('')
elif argv[:1] == ['status']:
    print('')
# Everything else succeeds silently
sys.exit(0)
""")
            result = run_script("prepare_pr_branch.py",
                                ["--base-branch", "main", "--head-branch", "agent/test-1"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "ready")
        self.assertTrue(payload["ok"])

    def test_rebase_conflict_returns_error(self) -> None:
        with FakeBinDir() as fbd:
            fbd.add("git", """
import sys

argv = sys.argv[1:]
if argv[:1] == ['rebase'] and '--abort' not in argv:
    print('CONFLICT (content): Merge conflict in foo.py', file=sys.stderr)
    sys.exit(1)
sys.exit(0)
""")
            result = run_script("prepare_pr_branch.py",
                                ["--base-branch", "main", "--head-branch", "agent/test-1"],
                                env=fbd.env())
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "rebase-conflict")
        self.assertFalse(payload["ok"])

    def test_push_failure_after_beads_cleanup_returns_blocked(self) -> None:
        with FakeBinDir() as fbd:
            fbd.add("git", """
import sys

argv = sys.argv[1:]
if argv[:1] == ['diff']:
    print('some beads diff content')  # triggers cleanup path
elif argv[:1] == ['status']:
    print('M .beads/issues.jsonl')    # dirty after checkout
elif argv[:1] == ['push']:
    print('push failed: remote rejected', file=sys.stderr)
    sys.exit(1)
sys.exit(0)
""")
            result = run_script("prepare_pr_branch.py",
                                ["--base-branch", "main", "--head-branch", "agent/test-1"],
                                env=fbd.env())
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "blocked")

    def test_dry_run_skips_all_git_mutations(self) -> None:
        """In --dry-run mode the script must not invoke git at all."""
        with FakeBinDir() as fbd:
            # This fake git always fails — if it's called, the test fails.
            fbd.add("git", """
import sys
print('git called in dry-run!', file=sys.stderr)
sys.exit(99)
""")
            result = run_script("prepare_pr_branch.py",
                                ["--base-branch", "main", "--head-branch", "agent/test-1", "--dry-run"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "dry-run")
        self.assertTrue(payload["ok"])


# ---------------------------------------------------------------------------
# list_review_threads.py
# ---------------------------------------------------------------------------

class ListReviewThreadsTests(unittest.TestCase):
    def test_success_returns_thread_list(self) -> None:
        threads_payload = {
            "data": {
                "repository": {
                    "pullRequest": {
                        "reviewThreads": {
                            "nodes": [
                                {
                                    "id": "T_1",
                                    "isResolved": False,
                                    "isOutdated": False,
                                    "comments": {
                                        "nodes": [
                                            {
                                                "id": "C_1",
                                                "databaseId": 1,
                                                "body": "Please add tests",
                                                "path": "foo.py",
                                                "line": 10,
                                                "originalLine": 10,
                                                "url": "https://github.com/owner/repo/pull/1#comment",
                                                "createdAt": "2026-01-01T00:00:00Z",
                                                "author": {"login": "reviewer"},
                                            }
                                        ],
                                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                                    },
                                }
                            ],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                        }
                    }
                }
            }
        }

        with FakeBinDir() as fbd:
            fbd.add("gh", f"""
import sys
import json
print({repr(json.dumps(threads_payload))})
sys.exit(0)
""")
            result = run_script("list_review_threads.py",
                                ["--owner", "owner", "--repo", "repo", "--pr-number", "1"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["thread_count"], 1)
        self.assertEqual(payload["unresolved_count"], 1)

    def test_command_failure_exits_nonzero(self) -> None:
        with FakeBinDir() as fbd:
            fbd.add("gh", """
import sys
print('gh: connection refused', file=sys.stderr)
sys.exit(1)
""")
            result = run_script("list_review_threads.py",
                                ["--owner", "owner", "--repo", "repo", "--pr-number", "1"],
                                env=fbd.env())
        self.assertNotEqual(result.returncode, 0)
        payload = json.loads(result.stderr)
        self.assertFalse(payload["ok"])
        self.assertIn("error_code", payload)


# ---------------------------------------------------------------------------
# reply_to_review_thread.py
# ---------------------------------------------------------------------------

class ReplyToReviewThreadTests(unittest.TestCase):
    def _base_args(self):
        return [
            "--owner", "owner",
            "--repo", "repo",
            "--pr-number", "42",
            "--comment-id", "1001",
            "--thread-id", "T_kwDOAbc123",
            "--body", "Fixed now.",
            "--dedupe-key", "aib-test:T_kwDOAbc123:reply",
        ]

    def test_creates_reply_when_no_duplicate(self) -> None:
        # Thread has comments but none with the dedupe key
        empty_thread_payload = json.dumps({
            "data": {
                "node": {
                    "comments": {
                        "nodes": [{"id": "C_1", "databaseId": 1, "body": "other comment",
                                   "author": {"login": "reviewer"}, "url": "https://example.com/c1"}],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        })
        new_comment_payload = json.dumps({
            "id": 9999,
            "html_url": "https://github.com/owner/repo/pull/42#comment-9999",
        })

        with FakeBinDir() as fbd:
            fbd.add("gh", f"""
import sys
import json

argv = sys.argv[1:]
if 'graphql' in argv:
    print({repr(empty_thread_payload)})
else:
    # POST request to create comment
    print({repr(new_comment_payload)})
sys.exit(0)
""")
            result = run_script("reply_to_review_thread.py", self._base_args(), env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "created")

    def test_skips_duplicate_when_dedupe_key_present(self) -> None:
        dedupe_key = "aib-test:T_kwDOAbc123:reply"
        thread_payload = json.dumps({
            "data": {
                "node": {
                    "comments": {
                        "nodes": [
                            {"id": "C_1", "databaseId": 1,
                             "body": f"Fixed now.\n\ndedupe-key: {dedupe_key}",
                             "author": {"login": "bot"},
                             "url": "https://github.com/owner/repo/pull/42#comment-1"},
                        ],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        })

        with FakeBinDir() as fbd:
            fbd.add("gh", f"""
import sys
import json
print({repr(thread_payload)})
sys.exit(0)
""")
            result = run_script("reply_to_review_thread.py", self._base_args(), env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "duplicate-skipped")

    def test_dry_run_does_not_post_comment(self) -> None:
        """In --dry-run, the POST to create the reply must not be called."""
        empty_thread_payload = json.dumps({
            "data": {
                "node": {
                    "comments": {
                        "nodes": [],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        })

        with FakeBinDir() as fbd:
            fbd.add("gh", f"""
import sys
import json

argv = sys.argv[1:]
if 'graphql' in argv:
    print({repr(empty_thread_payload)})
    sys.exit(0)

# Any non-graphql call (i.e. the POST mutation) should fail the test
print('POST called in dry-run!', file=sys.stderr)
sys.exit(99)
""")
            result = run_script("reply_to_review_thread.py",
                                self._base_args() + ["--dry-run"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "dry-run")


# ---------------------------------------------------------------------------
# resolve_review_thread.py
# ---------------------------------------------------------------------------

class ResolveReviewThreadTests(unittest.TestCase):
    def _status_payload(self, is_resolved: bool) -> str:
        return json.dumps({
            "data": {
                "node": {"id": "T_kwDOAbc123", "isResolved": is_resolved}
            }
        })

    def _resolve_payload(self) -> str:
        return json.dumps({
            "data": {
                "resolveReviewThread": {
                    "thread": {"id": "T_kwDOAbc123", "isResolved": True}
                }
            }
        })

    def test_resolves_unresolved_thread(self) -> None:
        status_json = self._status_payload(False)
        resolve_json = self._resolve_payload()
        calls: list[str] = []

        with FakeBinDir() as fbd:
            fbd.add("gh", f"""
import sys
import json

argv = sys.argv[1:]
args_str = ' '.join(argv)
# Identify by query content passed via -f query=...
query = ''
for i, a in enumerate(argv):
    if a == '-f':
        kv = argv[i+1] if i+1 < len(argv) else ''
        if kv.startswith('query='):
            query = kv[len('query='):]

if 'resolveReviewThread' in query:
    print({repr(resolve_json)})
else:
    print({repr(status_json)})
sys.exit(0)
""")
            result = run_script("resolve_review_thread.py",
                                ["--thread-id", "T_kwDOAbc123"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "resolved")

    def test_already_resolved_thread_is_skipped(self) -> None:
        status_json = self._status_payload(True)

        with FakeBinDir() as fbd:
            fbd.add("gh", f"""
import sys
import json
# Only the status query matters here; mutation should not be called
argv = sys.argv[1:]
query = ''
for i, a in enumerate(argv):
    if a == '-f':
        kv = argv[i+1] if i+1 < len(argv) else ''
        if kv.startswith('query='):
            query = kv[len('query='):]
if 'resolveReviewThread' in query:
    print('mutation called on already-resolved thread!', file=sys.stderr)
    sys.exit(99)
print({repr(status_json)})
sys.exit(0)
""")
            result = run_script("resolve_review_thread.py",
                                ["--thread-id", "T_kwDOAbc123"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "already-resolved")

    def test_dry_run_skips_mutation_for_unresolved_thread(self) -> None:
        status_json = self._status_payload(False)

        with FakeBinDir() as fbd:
            fbd.add("gh", f"""
import sys
import json

argv = sys.argv[1:]
query = ''
for i, a in enumerate(argv):
    if a == '-f':
        kv = argv[i+1] if i+1 < len(argv) else ''
        if kv.startswith('query='):
            query = kv[len('query='):]
if 'resolveReviewThread' in query:
    print('mutation called in dry-run!', file=sys.stderr)
    sys.exit(99)
print({repr(status_json)})
sys.exit(0)
""")
            result = run_script("resolve_review_thread.py",
                                ["--thread-id", "T_kwDOAbc123", "--dry-run"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "dry-run")


# ---------------------------------------------------------------------------
# create_inline_review_comment.py
# ---------------------------------------------------------------------------

class CreateInlineReviewCommentTests(unittest.TestCase):
    def _base_args(self):
        return [
            "--owner", "owner",
            "--repo", "repo",
            "--pr-number", "42",
            "--commit-id", "abc123",
            "--path", "foo.py",
            "--line", "10",
            "--body", "This looks problematic.",
            "--dedupe-key", "aib-test:foo.py:10",
        ]

    def test_creates_comment_when_no_duplicate(self) -> None:
        list_payload = json.dumps([])  # no existing comments
        create_payload = json.dumps({
            "id": 7777,
            "html_url": "https://github.com/owner/repo/pull/42#comment-7777",
        })

        with FakeBinDir() as fbd:
            fbd.add("gh", f"""
import sys
import json

argv = sys.argv[1:]
# Distinguish list vs create by presence of mutation params
if '-F' in argv and 'per_page=100' in ' '.join(argv):
    print({repr(list_payload)})
else:
    print({repr(create_payload)})
sys.exit(0)
""")
            result = run_script("create_inline_review_comment.py",
                                self._base_args(), env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "created")

    def test_skips_duplicate_comment(self) -> None:
        dedupe_key = "aib-test:foo.py:10"
        list_payload = json.dumps([{
            "id": 1234,
            "path": "foo.py",
            "line": 10,
            "original_line": 10,
            "body": f"This looks problematic.\n\ndedupe-key: {dedupe_key}",
            "html_url": "https://github.com/owner/repo/pull/42#comment-1234",
        }])

        with FakeBinDir() as fbd:
            fbd.add("gh", f"""
import sys
import json
print({repr(list_payload)})
sys.exit(0)
""")
            result = run_script("create_inline_review_comment.py",
                                self._base_args(), env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "duplicate-skipped")

    def test_dry_run_does_not_create_comment(self) -> None:
        list_payload = json.dumps([])  # no existing comments

        with FakeBinDir() as fbd:
            fbd.add("gh", f"""
import sys
import json

argv = sys.argv[1:]
# List call is allowed; create call (no per_page) should not happen
if '-F' in argv and 'per_page=100' in ' '.join(argv):
    print({repr(list_payload)})
    sys.exit(0)

# Any non-list call = mutation = should not happen in dry-run
print('POST called in dry-run!', file=sys.stderr)
sys.exit(99)
""")
            result = run_script("create_inline_review_comment.py",
                                self._base_args() + ["--dry-run"],
                                env=fbd.env())
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "dry-run")


if __name__ == "__main__":
    unittest.main()
