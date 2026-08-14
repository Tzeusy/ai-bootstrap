#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Behavioral tests for the coordinator's report-only PR-review normalizer."""

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
SCRIPT = SKILL_ROOT / "scripts" / "normalize_pr_review_state.py"


class FakeBinDir:
    """Temporary fake command directory used only by subprocess tests."""

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


def run_normalizer(
    repo_root: Path,
    *,
    now: str,
    env: dict[str, str],
    resolver: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    argv = [sys.executable, str(SCRIPT), "--repo-root", str(repo_root), "--now", now]
    if resolver is not None:
        argv.extend(["--resolver", str(resolver)])
    return subprocess.run(
        argv,
        capture_output=True,
        text=True,
        env=env,
    )


def install_fakes(fake_bin: FakeBinDir) -> None:
    fake_bin.add(
        "bd",
        """
        import json
        import os
        import sys

        fixture = json.loads(open(os.environ["NORMALIZER_FIXTURE"], encoding="utf-8").read())
        with open(os.environ["NORMALIZER_CALLS"], "a", encoding="utf-8") as calls:
            calls.write(json.dumps({"tool": "bd", "argv": sys.argv[1:]}) + "\\n")

        argv = sys.argv[1:]
        if argv[:1] == ["-C"]:
            argv = argv[2:]

        def fail(key):
            if key in fixture.get("failures", {}):
                print(fixture["failures"][key], file=sys.stderr)
                raise SystemExit(1)

        if "list" in argv:
            label = argv[argv.index("--label") + 1] if "--label" in argv else ""
            status = next((part.split("=", 1)[1] for part in argv if part.startswith("--status=")), "")
            key = f"bd-list:{status}:{label}"
            fail(key)
            if label == "pr-review" and status == "blocked":
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
            else:
                print(json.dumps([]))
            raise SystemExit(0)

        if "show" in argv:
            issue_id = argv[argv.index("show") + 1]
            key = f"bd-show:{issue_id}"
            fail(key)
            payload = fixture.get("shows", {}).get(issue_id)
            if payload is None:
                print("unmatched show " + issue_id, file=sys.stderr)
                raise SystemExit(1)
            print(json.dumps(payload))
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

        fixture = json.loads(open(os.environ["NORMALIZER_FIXTURE"], encoding="utf-8").read())
        with open(os.environ["NORMALIZER_CALLS"], "a", encoding="utf-8") as calls:
            calls.write(json.dumps({"tool": "gh", "argv": sys.argv[1:]}) + "\\n")

        argv = sys.argv[1:]
        if argv[:2] == ["repo", "view"]:
            print("owner/repo")
            raise SystemExit(0)
        if argv[:2] == ["pr", "list"]:
            failure = fixture.get("failures", {}).get("gh-pr-list")
            if failure:
                print(failure, file=sys.stderr)
                raise SystemExit(1)
            print(json.dumps(fixture.get("open_prs", [])))
            raise SystemExit(0)
        if argv[:2] == ["pr", "view"]:
            number = argv[2]
            failure = fixture.get("failures", {}).get(f"gh-pr-view:{number}")
            if failure:
                print(failure, file=sys.stderr)
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

        with open(os.environ["NORMALIZER_CALLS"], "a", encoding="utf-8") as calls:
            calls.write(json.dumps({"tool": "git", "argv": sys.argv[1:]}) + "\\n")
        raise SystemExit(0)
        """,
    )


def review_task(
    issue_id: str,
    original_id: str,
    *,
    created_at: str = "2026-08-14T03:00:00Z",
    status: str = "blocked",
) -> dict[str, object]:
    return {
        "id": issue_id,
        "labels": ["pr-review", "pr-review-task"],
        "created_at": created_at,
        "status": status,
    }


def original_bead(issue_id: str, pr_number: int) -> dict[str, object]:
    return {
        "id": issue_id,
        "labels": ["pr-review"],
        "external_ref": f"gh-pr:{pr_number}",
        "status": "blocked",
    }


def review_show(issue_id: str, original_id: str) -> list[dict[str, object]]:
    return [
        {
            "id": issue_id,
            "description": (
                f"Original implementation bead: {original_id}\n"
                "https://github.com/owner/repo/pull/41"
            ),
            "dependencies": [],
        }
    ]


def pr_payload(state: str, *, created_at: str = "2026-08-14T03:00:00Z", merged_at: str | None = None) -> dict[str, object]:
    return {
        "number": 41,
        "url": "https://github.com/owner/repo/pull/41",
        "state": state,
        "isDraft": False,
        "mergeStateStatus": "CLEAN",
        "reviewDecision": None,
        "headRefName": "agent/aib-swr.1",
        "baseRefName": "main",
        "headRefOid": "abc123",
        "createdAt": created_at,
        "mergedAt": merged_at,
    }


class NormalizePrReviewStateTests(unittest.TestCase):
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
            fixture_path = root / "fixture.json"
            calls_path = root / "calls.jsonl"
            fixture_path.write_text(json.dumps(fixture), encoding="utf-8")
            resolver = None
            if "resolver_payload" in fixture:
                resolver = root / "resolver.py"
                resolver.write_text(
                    "\n".join(
                        (
                            "import json",
                            "import os",
                            "import sys",
                            "fixture = json.loads(open(os.environ['NORMALIZER_FIXTURE'], encoding='utf-8').read())",
                            "print(json.dumps(fixture['resolver_payload']))",
                            "raise SystemExit(int(fixture.get('resolver_exit', 0)))",
                        )
                    ),
                    encoding="utf-8",
                )
            install_fakes(fake_bin)
            result = run_normalizer(
                repo_root,
                now=now,
                env=fake_bin.env(
                    NORMALIZER_FIXTURE=str(fixture_path),
                    NORMALIZER_CALLS=str(calls_path),
                ),
                resolver=resolver,
            )
            calls = [
                json.loads(line)
                for line in calls_path.read_text(encoding="utf-8").splitlines()
            ] if calls_path.exists() else []
        return result, calls, str(repo_root)

    def test_empty_scan_emits_a_compact_deterministic_envelope(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, FakeBinDir() as fake_bin:
            repo_root = Path(tmp)
            fake_bin.add(
                "bd",
                """
                import json
                import sys

                if "list" in sys.argv:
                    print(json.dumps([]))
                    raise SystemExit(0)
                print("unexpected bd command", file=sys.stderr)
                raise SystemExit(1)
                """,
            )
            fake_bin.add(
                "gh",
                """
                import json
                print(json.dumps([]))
                """,
            )
            fake_bin.add("git", "raise SystemExit(0)")

            result = run_normalizer(
                repo_root,
                now="2026-08-14T04:00:00Z",
                env=fake_bin.env(),
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(
            json.loads(result.stdout),
            {
                "errors": [],
                "findings": [],
                "generated_at": "2026-08-14T04:00:00Z",
                "schema": "beads-pr-review-normalization/v1",
                "self_heal_candidates": [],
                "status": "empty",
            },
        )
        self.assertEqual(result.stderr, "")

    def test_fake_commands_match_strict_read_only_argv_allowlists(self) -> None:
        result, calls, repo_root = self.run_fixture(
            {
                "blocked_pr_review": [],
                "blocked_pr_review_tasks": [],
                "open_prs": [],
            }
        )

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

    def test_preserves_dotted_child_and_reports_open_pr_cooldown(self) -> None:
        original_id = "aib-swr.1"
        review_id = "aib-review.1"
        fixture = {
            "blocked_pr_review": [
                original_bead(original_id, 41),
                review_task(review_id, original_id),
            ],
            "shows": {
                original_id: [original_bead(original_id, 41)],
                review_id: review_show(review_id, original_id),
            },
            "prs": {"41": pr_payload("OPEN", created_at="2026-08-14T03:57:00Z")},
            "open_prs": [],
        }

        result, calls, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        task = next(item for item in payload["findings"] if item["review_id"] == review_id)
        self.assertEqual(task["original_id"], original_id)
        self.assertEqual(task["canonical_review_id"], review_id)
        self.assertEqual(task["pr_number"], 41)
        self.assertEqual(task["pr_state"], "OPEN")
        self.assertEqual(task["cooldown_until"], "2026-08-14T04:02:00Z")
        self.assertEqual(task["recommendation"], "wait-for-cooldown")
        self.assertTrue(any(call["tool"] == "bd" for call in calls))
        self.assertTrue(any(call["tool"] == "gh" for call in calls))

    def test_duplicate_review_tasks_choose_the_chronological_oldest_then_id(self) -> None:
        original_id = "aib-swr.1"
        first_review = "aib-review.1"
        duplicate_review = "aib-review.2"
        fixture = {
            "blocked_pr_review": [
                original_bead(original_id, 41),
                review_task(first_review, original_id, created_at="2026-08-14T03:00:00+02:00"),
                review_task(duplicate_review, original_id, created_at="2026-08-14T02:30:00Z"),
            ],
            "shows": {
                original_id: [original_bead(original_id, 41)],
                first_review: review_show(first_review, original_id),
                duplicate_review: review_show(duplicate_review, original_id),
            },
            "prs": {"41": pr_payload("OPEN", created_at="2026-08-14T03:00:00Z")},
            "open_prs": [],
        }

        result, calls, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        duplicate = next(item for item in payload["findings"] if item["review_id"] == duplicate_review)
        self.assertEqual(duplicate["canonical_review_id"], first_review)
        self.assertEqual(duplicate["duplicate_of"], first_review)
        self.assertEqual(duplicate["recommendation"], "dedupe-review-task")

    def test_invalid_review_task_created_at_fails_closed_without_canonical_selection(self) -> None:
        original_id = "aib-swr.1"
        invalid_review = "aib-review.1"
        other_review = "aib-review.2"
        fixture = {
            "blocked_pr_review": [
                original_bead(original_id, 41),
                review_task(invalid_review, original_id, created_at="not-a-timestamp"),
                review_task(other_review, original_id, created_at="2026-08-14T03:00:00Z"),
            ],
            "shows": {
                original_id: [original_bead(original_id, 41)],
                invalid_review: review_show(invalid_review, original_id),
                other_review: review_show(other_review, original_id),
            },
            "prs": {"41": pr_payload("OPEN")},
            "open_prs": [],
        }

        result, _, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        self.assertIn({"code": "invalid-created-at", "scope": "review-context"}, payload["errors"])
        for review_id in (invalid_review, other_review):
            finding = next(item for item in payload["findings"] if item["review_id"] == review_id)
            self.assertEqual(finding["context_status"], "invalid-created-at")
            self.assertIsNone(finding["canonical_review_id"])
            self.assertIsNone(finding["duplicate_of"])
            self.assertEqual(finding["recommendation"], "manual-triage")

    def test_resolver_bool_pr_number_is_invalid_manual_triage(self) -> None:
        review_id = "aib-review.1"
        fixture = {
            "blocked_pr_review": [review_task(review_id, "aib-swr.1")],
            "resolver_payload": {"ok": True, "original_id": "aib-swr.1", "pr_number": True},
            "prs": {"True": pr_payload("OPEN")},
            "open_prs": [],
        }

        result, _, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        finding = next(item for item in payload["findings"] if item["review_id"] == review_id)
        self.assertEqual(finding["context_status"], "invalid-pr-number")
        self.assertIsNone(finding["pr_number"])
        self.assertEqual(finding["recommendation"], "manual-triage")
        self.assertIn({"code": "invalid-pr-number", "scope": "review-context"}, payload["errors"])

    def test_invalid_pr_created_at_is_partial_manual_triage_for_every_state(self) -> None:
        original_id = "aib-swr.1"
        review_id = "aib-review.1"
        for state in ("OPEN", "CLOSED", "MERGED"):
            with self.subTest(state=state):
                fixture = {
                    "blocked_pr_review": [original_bead(original_id, 41), review_task(review_id, original_id)],
                    "shows": {
                        original_id: [original_bead(original_id, 41)],
                        review_id: review_show(review_id, original_id),
                    },
                    "prs": {"41": pr_payload(state, created_at="not-a-timestamp")},
                    "open_prs": [],
                }

                result, _, _ = self.run_fixture(fixture)

                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "partial")
                for finding in payload["findings"]:
                    self.assertEqual(finding["context_status"], "invalid-pr-created-at")
                    self.assertIsNone(finding["pr_state"])
                    self.assertEqual(finding["recommendation"], "manual-triage")
                self.assertIn({"code": "invalid-pr-created-at", "scope": "pr-state"}, payload["errors"])

    def test_malformed_open_pr_candidates_are_partial_manual_triage_never_self_heal(self) -> None:
        original_id = "aib-swr.1"
        cases = {
            "bool-number": (
                {"number": True, "headRefName": f"agent/{original_id}", "createdAt": "2026-08-14T03:00:00Z"},
                "invalid-pr-number",
                None,
            ),
            "invalid-created-at": (
                {"number": 77, "headRefName": f"agent/{original_id}", "createdAt": "not-a-timestamp"},
                "invalid-pr-created-at",
                77,
            ),
        }
        for name, (open_pr, error_code, expected_number) in cases.items():
            with self.subTest(name=name):
                fixture = {
                    "blocked_pr_review": [],
                    "shows": {original_id: [{"id": original_id, "status": "open", "labels": [], "external_ref": ""}]},
                    "open_prs": [open_pr],
                }

                result, _, _ = self.run_fixture(fixture)

                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "partial")
                candidate = payload["self_heal_candidates"][0]
                self.assertEqual(candidate["context_status"], error_code)
                self.assertEqual(candidate["pr_number"], expected_number)
                self.assertEqual(candidate["recommendation"], "manual-triage")
                self.assertIn({"code": error_code, "scope": "open-prs"}, payload["errors"])

    def test_active_review_task_is_canonical_and_blocks_self_heal(self) -> None:
        original_id = "aib-swr.1"
        review_id = "aib-review.1"
        fixture = {
            "blocked_pr_review": [original_bead(original_id, 41)],
            "pr_review_tasks_all": [
                review_task(review_id, original_id, status="in_progress"),
            ],
            "shows": {
                original_id: [original_bead(original_id, 41)],
                review_id: review_show(review_id, original_id),
            },
            "prs": {"41": pr_payload("OPEN", created_at="2026-08-14T03:00:00Z")},
            "open_prs": [
                {
                    "number": 41,
                    "headRefName": f"agent/{original_id}",
                    "createdAt": "2026-08-14T03:00:00Z",
                }
            ],
        }

        result, calls, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        original = next(item for item in payload["findings"] if item["kind"] == "original")
        self.assertEqual(original["canonical_review_id"], review_id)
        candidate = payload["self_heal_candidates"][0]
        self.assertEqual(candidate["canonical_review_id"], review_id)
        self.assertEqual(candidate["recommendation"], "review-wiring-current")
        task_lists = [
            call["argv"]
            for call in calls
            if call["tool"] == "bd" and "pr-review-task" in call["argv"]
        ]
        self.assertTrue(task_lists)
        self.assertTrue(all("--status=blocked" not in argv for argv in task_lists))

    def test_incomplete_active_task_lookup_never_recommends_self_heal(self) -> None:
        secret = "TOKEN=top-secret /private/absolute/path Traceback"
        original_id = "aib-swr.1"
        fixture = {
            "blocked_pr_review": [original_bead(original_id, 41)],
            "shows": {original_id: [original_bead(original_id, 41)]},
            "prs": {"41": pr_payload("OPEN", created_at="2026-08-14T03:00:00Z")},
            "open_prs": [
                {
                    "number": 41,
                    "headRefName": f"agent/{original_id}",
                    "createdAt": "2026-08-14T03:00:00Z",
                }
            ],
            "failures": {"bd-list::pr-review-task": secret},
        }

        result, _, repo_root = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        original = next(item for item in payload["findings"] if item["kind"] == "original")
        self.assertEqual(original["recommendation"], "manual-triage")
        self.assertEqual(payload["self_heal_candidates"][0]["recommendation"], "manual-triage")
        for forbidden in ("TOKEN=top-secret", "/private/absolute/path", "Traceback", repo_root):
            self.assertNotIn(forbidden, result.stdout + result.stderr)

    def test_malformed_pr_review_task_inventory_blocks_self_heal(self) -> None:
        original_id = "aib-swr.1"
        malformed_inventories = {
            "non-record": ["malformed-task-inventory-record"],
            "missing-task-label": [
                {
                    "created_at": "2026-08-14T03:00:00Z",
                    "id": "aib-review.1",
                    "labels": ["pr-review"],
                    "status": "blocked",
                }
            ],
        }
        for name, inventory in malformed_inventories.items():
            with self.subTest(name=name):
                fixture = {
                    "blocked_pr_review": [],
                    "pr_review_tasks_all": inventory,
                    "shows": {original_id: [original_bead(original_id, 41)]},
                    "open_prs": [
                        {
                            "number": 41,
                            "headRefName": f"agent/{original_id}",
                            "createdAt": "2026-08-14T03:00:00Z",
                        }
                    ],
                }

                result, _, _ = self.run_fixture(fixture)

                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(payload["status"], "partial")
                self.assertEqual(payload["self_heal_candidates"][0]["recommendation"], "manual-triage")
                self.assertIn(
                    {"code": "invalid-record", "scope": "blocked-pr-review-task"},
                    payload["errors"],
                )

    def test_resolver_context_failures_are_safe_and_do_not_fall_back(self) -> None:
        cases = {
            "missing": ("No explicit original marker or dependency", "missing-original-id"),
            "malformed": ("Original implementation bead: aib-swr.invalid", "malformed-original-id"),
            "ambiguous": (
                "Original implementation bead: aib-swr.1\nOriginal implementation bead: aib-swr.2",
                "ambiguous-original-id",
            ),
        }
        for name, (description, error_code) in cases.items():
            with self.subTest(name=name):
                review_id = "aib-review.1"
                fixture = {
                    "blocked_pr_review": [review_task(review_id, "aib-swr.1")],
                    "shows": {
                        review_id: [{"id": review_id, "description": description, "dependencies": []}],
                    },
                    "prs": {},
                    "open_prs": [],
                }
                result, _, _ = self.run_fixture(fixture)
                self.assertEqual(result.returncode, 0, result.stderr)
                finding = json.loads(result.stdout)["findings"][0]
                self.assertEqual(finding["context_status"], error_code)
                self.assertEqual(finding["original_id"], None)
                self.assertEqual(finding["recommendation"], "manual-triage")

    def test_pr_state_recommendations_cover_merged_closed_open_and_command_failure(self) -> None:
        cases = {
            "MERGED": ("MERGED", "close-review-and-original", None),
            "CLOSED": ("CLOSED", "close-review-reopen-original", None),
            "OPEN": ("OPEN", "dispatch-canonical-review", None),
            "command-failure": ("OPEN", "skip-command-failure", "TOKEN=secret /private/path Traceback"),
        }
        original_id = "aib-swr.1"
        review_id = "aib-review.1"
        for name, (state, recommendation, failure) in cases.items():
            with self.subTest(name=name):
                fixture = {
                    "blocked_pr_review": [original_bead(original_id, 41), review_task(review_id, original_id)],
                    "shows": {
                        original_id: [original_bead(original_id, 41)],
                        review_id: review_show(review_id, original_id),
                    },
                    "prs": {"41": pr_payload(state)},
                    "open_prs": [],
                    "failures": {"gh-pr-view:41": failure} if failure else {},
                }
                result, _, repo_root = self.run_fixture(fixture)
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                finding = next(item for item in payload["findings"] if item["review_id"] == review_id)
                self.assertEqual(finding["recommendation"], recommendation)
                if failure:
                    self.assertEqual(finding["context_status"], "command-failed")
                    for forbidden in ("TOKEN=secret", "/private/path", "Traceback", repo_root):
                        self.assertNotIn(forbidden, result.stdout + result.stderr)

    def test_unknown_pr_state_is_sanitized_to_a_partial_manual_triage_finding(self) -> None:
        secret_state = "TOKEN=top-secret /private/absolute/path Traceback"
        original_id = "aib-swr.1"
        review_id = "aib-review.1"
        fixture = {
            "blocked_pr_review": [original_bead(original_id, 41), review_task(review_id, original_id)],
            "shows": {
                original_id: [original_bead(original_id, 41)],
                review_id: review_show(review_id, original_id),
            },
            "prs": {"41": pr_payload(secret_state)},
            "open_prs": [],
        }

        result, _, repo_root = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        finding = next(item for item in payload["findings"] if item["review_id"] == review_id)
        self.assertEqual(finding["context_status"], "invalid-pr-state")
        self.assertIsNone(finding["pr_state"])
        self.assertEqual(finding["recommendation"], "manual-triage")
        self.assertIn({"code": "invalid-pr-state", "scope": "pr-state"}, payload["errors"])
        for forbidden in ("TOKEN=top-secret", "/private/absolute/path", "Traceback", repo_root):
            self.assertNotIn(forbidden, result.stdout + result.stderr)

    def test_open_agent_branch_reports_a_dotted_self_heal_candidate(self) -> None:
        original_id = "aib-swr.1"
        fixture = {
            "blocked_pr_review": [],
            "shows": {
                original_id: [{"id": original_id, "status": "open", "labels": [], "external_ref": ""}],
            },
            "prs": {},
            "open_prs": [
                {
                    "number": 77,
                    "headRefName": f"agent/{original_id}",
                    "createdAt": "2026-08-14T03:00:00Z",
                }
            ],
        }

        result, _, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        candidate = json.loads(result.stdout)["self_heal_candidates"][0]
        self.assertEqual(candidate["original_id"], original_id)
        self.assertEqual(candidate["pr_number"], 77)
        self.assertEqual(candidate["recommendation"], "self-heal-original-and-review-wiring")

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
            "blocked_pr_review": ["TOKEN=top-secret /private/absolute/path"],
            "open_prs": [],
        }

        result, _, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        self.assertIn({"code": "invalid-record", "scope": "blocked-pr-review"}, payload["errors"])
        self.assertNotIn("TOKEN=top-secret", result.stdout + result.stderr)
        self.assertNotIn("/private/absolute/path", result.stdout + result.stderr)

    def test_missing_canonical_pr_reference_is_an_unresolved_partial_finding(self) -> None:
        fixture = {
            "blocked_pr_review": [
                {"id": "aib-swr.1", "labels": ["pr-review"], "external_ref": ""},
            ],
            "open_prs": [],
        }

        result, _, _ = self.run_fixture(fixture)

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "partial")
        finding = payload["findings"][0]
        self.assertEqual(finding["context_status"], "missing-pr-number")
        self.assertEqual(finding["recommendation"], "manual-triage")
        self.assertIn({"code": "missing-pr-number", "scope": "original-context"}, payload["errors"])


if __name__ == "__main__":
    unittest.main()
