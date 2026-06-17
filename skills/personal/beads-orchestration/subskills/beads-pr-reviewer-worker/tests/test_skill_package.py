# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = SKILL_ROOT / "SKILL.md"
OPENAI_YAML = SKILL_ROOT / "agents" / "openai.yaml"
SCRIPTS_DIR = SKILL_ROOT / "scripts"
EVALUATION_MD = SKILL_ROOT / "references" / "evaluation.md"
FAILURE_PROTOCOL_MD = SKILL_ROOT / "references" / "failure-protocol.md"
THREAD_OPERATIONS_MD = SKILL_ROOT / "references" / "thread-operations.md"

MUTATION_SCRIPTS = [
    "prepare_pr_branch.py",
    "resolve_review_thread.py",
    "reply_to_review_thread.py",
    "create_inline_review_comment.py",
    "evaluate_merge_readiness.py",
]


class BreadsPrReviewerWorkerPackageTests(unittest.TestCase):
    def test_skill_is_slimmer_than_five_hundred_lines(self) -> None:
        line_count = len(SKILL_MD.read_text(encoding="utf-8").splitlines())
        self.assertLessEqual(line_count, 500)

    def test_skill_frontmatter_has_required_fields(self) -> None:
        frontmatter = SKILL_MD.read_text(encoding="utf-8").split("---", 2)[1]
        self.assertIn("name: beads-pr-reviewer-worker", frontmatter)
        self.assertIn("metadata:", frontmatter)
        self.assertIn("owner: tze", frontmatter)
        self.assertIn("authors:", frontmatter)
        self.assertIn("compatibility:", frontmatter)
        self.assertIn("gh", frontmatter)
        self.assertIn("git worktrees", frontmatter)

    def test_skill_references_all_bundled_scripts(self) -> None:
        contents = SKILL_MD.read_text(encoding="utf-8")
        for script in [
            "scripts/resolve_review_context.py",
            "scripts/prepare_pr_branch.py",
            "scripts/list_review_threads.py",
            "scripts/evaluate_merge_readiness.py",
            "scripts/discover_quality_gates.py",
            "scripts/reply_to_review_thread.py",
            "scripts/resolve_review_thread.py",
            "scripts/create_inline_review_comment.py",
        ]:
            self.assertIn(script, contents, f"SKILL.md should reference {script}")

    def test_skill_references_bundled_references(self) -> None:
        contents = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("references/thread-operations.md", contents)
        self.assertIn("references/failure-protocol.md", contents)
        self.assertIn("references/evaluation.md", contents)

    def test_skill_documents_non_negotiable_boundaries(self) -> None:
        contents = SKILL_MD.read_text(encoding="utf-8")
        self.assertRegex(contents, re.compile(r"Non-Negotiable", re.IGNORECASE))
        self.assertIn("WORKTREE_PATH", contents)
        self.assertIn("REPO_ROOT", contents)

    def test_skill_documents_terminal_statuses(self) -> None:
        contents = SKILL_MD.read_text(encoding="utf-8")
        for status in ("merged-pr", "pushed-review-fixes", "blocked-awaiting-coordinator", "invalid-runtime-context"):
            self.assertIn(status, contents, f"SKILL.md should document status: {status}")

    def test_openai_yaml_exists_with_required_fields(self) -> None:
        self.assertTrue(OPENAI_YAML.exists(), OPENAI_YAML)
        contents = OPENAI_YAML.read_text(encoding="utf-8")
        self.assertIn("display_name", contents)
        self.assertIn("short_description", contents)
        self.assertIn("$beads-pr-reviewer-worker", contents)

    def test_expected_reference_files_exist(self) -> None:
        for path in (EVALUATION_MD, FAILURE_PROTOCOL_MD, THREAD_OPERATIONS_MD):
            self.assertTrue(path.exists(), f"Missing reference file: {path}")

    def test_evaluation_md_covers_validation_tracks(self) -> None:
        contents = EVALUATION_MD.read_text(encoding="utf-8")
        self.assertIn("Track 1", contents)
        self.assertIn("Track 2", contents)
        self.assertIn("Track 3", contents)
        self.assertIn("Track 4", contents)

    def test_all_scripts_compile(self) -> None:
        for script in SCRIPTS_DIR.glob("*.py"):
            result = subprocess.run(
                [sys.executable, "-m", "py_compile", str(script)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, f"{script.name}: {result.stderr}")

    def test_scripts_have_pep723_headers(self) -> None:
        for script in SCRIPTS_DIR.glob("*.py"):
            contents = script.read_text(encoding="utf-8")
            self.assertIn("# /// script", contents, f"{script.name} missing PEP 723 header")
            self.assertIn('requires-python = ">=3.', contents, f"{script.name} missing requires-python")

    def test_mutation_scripts_expose_help(self) -> None:
        for name in MUTATION_SCRIPTS:
            script = SCRIPTS_DIR / name
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, f"{name}: --help failed: {result.stderr}")

    def test_mutation_scripts_have_dry_run_flag(self) -> None:
        """Every mutation-capable script must expose --dry-run so tests can exercise it without real GitHub calls."""
        for name in MUTATION_SCRIPTS:
            script = SCRIPTS_DIR / name
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                capture_output=True,
                text=True,
            )
            help_text = result.stdout + result.stderr
            self.assertIn("--dry-run", help_text, f"{name} is missing --dry-run flag")

    def test_read_only_scripts_expose_help(self) -> None:
        read_only = ["resolve_review_context.py", "list_review_threads.py", "discover_quality_gates.py"]
        for name in read_only:
            script = SCRIPTS_DIR / name
            result = subprocess.run(
                [sys.executable, str(script), "--help"],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, f"{name}: --help failed: {result.stderr}")


if __name__ == "__main__":
    unittest.main()
