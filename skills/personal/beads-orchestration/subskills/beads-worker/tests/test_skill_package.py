# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import re
import unittest
from pathlib import Path

import yaml


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKILL_MD = SKILL_ROOT / "SKILL.md"
OPENAI_YAML = SKILL_ROOT / "agents" / "openai.yaml"
ASSERT_CONTEXT = SKILL_ROOT / "scripts" / "assert_worker_context.py"
EMIT_REPORT = SKILL_ROOT / "scripts" / "emit_worker_report.py"
RUNTIME_CONTRACT = SKILL_ROOT / "references" / "runtime-contract.md"
WORKER_REPORT = SKILL_ROOT / "references" / "worker-report.md"


class BeadsWorkerPackageTests(unittest.TestCase):
    def test_skill_is_slimmer_than_five_hundred_lines(self) -> None:
        line_count = len(SKILL_MD.read_text(encoding="utf-8").splitlines())
        self.assertLessEqual(line_count, 500)

    def test_skill_declares_compatibility(self) -> None:
        frontmatter = SKILL_MD.read_text(encoding="utf-8").split("---", 2)[1]
        self.assertIn("compatibility:", frontmatter)
        self.assertIn("git worktrees", frontmatter)
        self.assertIn("gh", frontmatter)

    def test_skill_references_deterministic_helpers_and_references(self) -> None:
        contents = SKILL_MD.read_text(encoding="utf-8")
        self.assertIn("scripts/assert_worker_context.py", contents)
        self.assertIn("scripts/emit_worker_report.py", contents)
        self.assertIn("references/runtime-contract.md", contents)
        self.assertIn("references/worker-report.md", contents)

    def test_openai_metadata_exists_and_mentions_skill(self) -> None:
        self.assertTrue(OPENAI_YAML.exists(), OPENAI_YAML)
        config = yaml.safe_load(OPENAI_YAML.read_text(encoding="utf-8"))
        interface = config["interface"]
        self.assertIn("display_name", interface)
        self.assertIn("short_description", interface)
        self.assertIn("default_prompt", interface)
        self.assertIn("$beads-worker", interface["default_prompt"])

    def test_expected_helper_files_exist(self) -> None:
        for path in (ASSERT_CONTEXT, EMIT_REPORT, RUNTIME_CONTRACT, WORKER_REPORT):
            self.assertTrue(path.exists(), path)

    def test_python_entrypoints_use_pep723_headers(self) -> None:
        for path in (ASSERT_CONTEXT, EMIT_REPORT):
            contents = path.read_text(encoding="utf-8")
            self.assertIn("# /// script", contents, path)
            self.assertIn('requires-python = ">=3.11"', contents, path)

    def test_skill_documents_branch_binding(self) -> None:
        contents = SKILL_MD.read_text(encoding="utf-8")
        self.assertRegex(contents, re.compile(r"agent/<ISSUE_ID>", re.IGNORECASE))
        self.assertRegex(contents, re.compile(r"branch.*must.*agent", re.IGNORECASE))

    def test_skill_documents_structured_invalid_runtime_context_handoff(self) -> None:
        contents = SKILL_MD.read_text(encoding="utf-8")
        self.assertRegex(contents, re.compile(r"invalid-runtime-context", re.IGNORECASE))
        self.assertRegex(contents, re.compile(r"emit_worker_report\.py", re.IGNORECASE))


if __name__ == "__main__":
    unittest.main()
