# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock


SKILL_ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = SKILL_ROOT / "scripts" / "skill_usage_audit.py"
REPO_ROOT = SKILL_ROOT.parents[4]
LINKER = REPO_ROOT / "scripts" / "link-ai-skills.sh"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
AS_OF = "2026-08-14T00:00:00Z"
AS_OF_DATETIME = datetime(2026, 8, 14, tzinfo=timezone.utc)


AUDIT_MODULE_SPEC = importlib.util.spec_from_file_location("skill_usage_audit", AUDIT_SCRIPT)
if AUDIT_MODULE_SPEC is None or AUDIT_MODULE_SPEC.loader is None:
    raise RuntimeError("unable to load the audit script for behavioral tests")
AUDIT_MODULE = importlib.util.module_from_spec(AUDIT_MODULE_SPEC)
AUDIT_MODULE_SPEC.loader.exec_module(AUDIT_MODULE)

CANDIDATES = [
    "using-superpowers",
    "brainstorming",
    "writing-plans",
    "executing-plans",
    "using-git-worktrees",
    "test-driven-development",
    "systematic-debugging",
    "verification-before-completion",
    "dispatching-parallel-agents",
    "subagent-driven-development",
    "finishing-a-development-branch",
    "requesting-code-review",
    "receiving-code-review",
]


def write_skill(root: Path, relative: str) -> Path:
    skill_dir = root / relative
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_dir.joinpath("SKILL.md").write_text(
        f"---\nname: {skill_dir.name}\ndescription: Synthetic test skill.\n---\n",
        encoding="utf-8",
    )
    return skill_dir


def write_manifest(root: Path, entries: list[dict[str, str]]) -> Path:
    manifest = root / "catalog-manifest.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": 1,
                "selection_rule": "shallowest-path, then lexical",
                "excluded_names": ["writing-skills"],
                "surfaces": [".claude/skills", ".codex/skills"],
                "skills": entries,
            }
        ),
        encoding="utf-8",
    )
    return manifest


def set_mtime(path: Path, when: datetime) -> None:
    timestamp = when.timestamp()
    os.utime(path, (timestamp, timestamp))


def matrix_row(report: dict, name: str) -> dict:
    return next(row for row in report["decision_matrix"] if row["name"] == name)


def claude_skill_event(name: str) -> str:
    return json.dumps(
        {
            "type": "assistant",
            "message": {
                "role": "assistant",
                "content": [{"type": "tool_use", "name": "Skill", "input": {"skill": name}}],
            },
        }
    )


def fixture_records(name: str) -> list[dict]:
    return [json.loads(line) for line in (FIXTURES / name).read_text(encoding="utf-8").splitlines()]


class CatalogManifestTests(unittest.TestCase):
    def test_manifest_reuses_linker_selection_without_creating_tool_homes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            write_skill(repo, "skills/alpha/shared-name")
            write_skill(repo, "skills/omega/shared-name")
            write_skill(repo, "skills/deeper/nested/shared-name")
            write_skill(repo, "skills/writing-skills")
            write_skill(repo, "skills/archive/archived-skill")
            write_skill(repo, "skills/personal/example/subskills/hidden-skill")
            write_skill(repo, "skills/vendor/vendor-skill")
            (repo / "skills/vendor/.git").mkdir(parents=True)

            result = subprocess.run(
                ["bash", str(LINKER), "--catalog-manifest", str(repo)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            manifest = json.loads(result.stdout)
            entries = {entry["name"]: entry for entry in manifest["skills"]}
            self.assertEqual(entries["shared-name"]["source"], "skills/alpha/shared-name")
            self.assertEqual(entries["vendor-skill"]["ownership"], "submodule")
            self.assertNotIn("writing-skills", entries)
            self.assertNotIn("archived-skill", entries)
            self.assertNotIn("hidden-skill", entries)
            self.assertNotIn(str(repo), result.stdout)
            self.assertFalse((repo / ".claude").exists())
            self.assertFalse((repo / ".codex").exists())
            self.assertFalse((repo / ".gemini").exists())

    def test_manifest_selection_matches_normal_linker_selection(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            write_skill(repo, "skills/alpha/shared-name")
            write_skill(repo, "skills/omega/shared-name")
            write_skill(repo, "skills/deeper/nested/shared-name")

            manifest_result = subprocess.run(
                ["bash", str(LINKER), "--catalog-manifest", str(repo)],
                capture_output=True,
                text=True,
                check=False,
            )
            link_result = subprocess.run(
                ["bash", str(LINKER), str(repo)],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(manifest_result.returncode, 0, manifest_result.stderr)
            self.assertEqual(link_result.returncode, 0, link_result.stderr)
            manifest = json.loads(manifest_result.stdout)
            source = next(entry["source"] for entry in manifest["skills"] if entry["name"] == "shared-name")
            linked_source = Path(os.readlink(repo / ".claude/skills/shared-name")).resolve()
            self.assertEqual(linked_source, (repo / source).resolve())


class UsageAuditTests(unittest.TestCase):
    def test_actual_audit_path_never_decodes_synthetic_content_or_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            manifest = self.make_complete_catalog(repo)
            self.seed_old_repo_history(repo)
            catalog = AUDIT_MODULE.load_catalog_manifest(repo, manifest)
            claude_dir = repo / "transcripts" / "claude"
            codex_dir = repo / "transcripts" / "codex"
            claude_dir.mkdir(parents=True)
            codex_dir.mkdir(parents=True)
            shutil.copyfile(FIXTURES / "claude-events.jsonl", claude_dir / "events.jsonl")
            shutil.copyfile(FIXTURES / "codex-events.jsonl", codex_dir / "events.jsonl")
            for source in (claude_dir, codex_dir):
                marker = source / "history.jsonl"
                marker.write_text("\n", encoding="utf-8")
                set_mtime(marker, AS_OF_DATETIME - timedelta(days=100))
            for event_file in (claude_dir / "events.jsonl", codex_dir / "events.jsonl"):
                set_mtime(event_file, AS_OF_DATETIME - timedelta(days=5))

            with mock.patch.object(
                AUDIT_MODULE.json,
                "loads",
                side_effect=AssertionError("transcript values must not reach json decoding"),
            ):
                report = AUDIT_MODULE.build_report(
                    repo,
                    catalog,
                    claude_dir,
                    codex_dir,
                    AS_OF_DATETIME,
                    90,
                    30,
                )

            rendered = AUDIT_MODULE.render_text(report)
            self.assertTrue(report["coverage"]["complete"])
            self.assertEqual(matrix_row(report, "test-driven-development")["counts"]["primary"]["total"], 2)
            self.assertEqual(matrix_row(report, "brainstorming")["counts"]["primary"]["claude"], 1)
            for sentinel in (
                "SYNTHETIC_CONTENT_SENTINEL_AIB_C4M",
                "SYNTHETIC_CREDENTIAL_SENTINEL_AIB_C4M",
            ):
                self.assertNotIn(sentinel, rendered)

    def test_failed_open_source_fails_coverage_closed_in_actual_audit_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            source = write_skill(repo, "skills/personal/systematic-debugging")
            manifest = write_manifest(
                repo,
                [{"name": "systematic-debugging", "source": str(source.relative_to(repo)), "ownership": "repo"}],
            )
            write_skill(repo, "skills/superpowers/skills/test-driven-development")
            self.seed_old_repo_history(repo)
            catalog = AUDIT_MODULE.load_catalog_manifest(repo, manifest)
            claude_dir = repo / "transcripts" / "claude"
            codex_dir = repo / "transcripts" / "codex"
            claude_dir.mkdir(parents=True)
            codex_dir.mkdir(parents=True)
            claude_history = claude_dir / "history.jsonl"
            failed_open = claude_dir / "unreadable.jsonl"
            codex_history = codex_dir / "history.jsonl"
            claude_history.write_text("\n", encoding="utf-8")
            failed_open.write_text(claude_skill_event("writing-plans") + "\n", encoding="utf-8")
            codex_history.write_text("\n", encoding="utf-8")
            set_mtime(claude_history, AS_OF_DATETIME - timedelta(days=100))
            set_mtime(failed_open, AS_OF_DATETIME - timedelta(days=5))
            set_mtime(codex_history, AS_OF_DATETIME - timedelta(days=100))

            original_open = AUDIT_MODULE.os.open
            failed = False

            def fail_one_transcript(path: object, flags: int, *args: object, **kwargs: object) -> object:
                nonlocal failed
                if path == failed_open.name and kwargs.get("dir_fd") is not None:
                    failed = True
                    raise OSError("synthetic failed-open")
                return original_open(path, flags, *args, **kwargs)

            with mock.patch.object(AUDIT_MODULE.os, "open", new=fail_one_transcript):
                report = AUDIT_MODULE.build_report(
                    repo,
                    catalog,
                    claude_dir,
                    codex_dir,
                    AS_OF_DATETIME,
                    90,
                    30,
                )

            self.assertTrue(failed)
            row = matrix_row(report, "systematic-debugging")
            self.assertFalse(report["coverage"]["claude"]["available"])
            self.assertFalse(report["coverage"]["claude"]["coverage_complete"])
            self.assertFalse(report["coverage"]["complete"])
            self.assertEqual(row["counts"]["primary"]["total"], 0)
            self.assertEqual(row["disposition"], "insufficient-evidence")
            self.assertEqual(row["protection_reason"], "incomplete-history")

    def test_failed_metadata_read_fails_coverage_closed_in_actual_audit_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            source = write_skill(repo, "skills/personal/systematic-debugging")
            manifest = write_manifest(
                repo,
                [{"name": "systematic-debugging", "source": str(source.relative_to(repo)), "ownership": "repo"}],
            )
            write_skill(repo, "skills/superpowers/skills/test-driven-development")
            self.seed_old_repo_history(repo)
            catalog = AUDIT_MODULE.load_catalog_manifest(repo, manifest)
            claude_dir = repo / "transcripts" / "claude"
            codex_dir = repo / "transcripts" / "codex"
            claude_dir.mkdir(parents=True)
            codex_dir.mkdir(parents=True)
            claude_history = claude_dir / "history.jsonl"
            unreadable_metadata = claude_dir / "unstatable.jsonl"
            codex_history = codex_dir / "history.jsonl"
            claude_history.write_text("\n", encoding="utf-8")
            unreadable_metadata.write_text(claude_skill_event("writing-plans") + "\n", encoding="utf-8")
            codex_history.write_text("\n", encoding="utf-8")
            set_mtime(claude_history, AS_OF_DATETIME - timedelta(days=100))
            set_mtime(unreadable_metadata, AS_OF_DATETIME - timedelta(days=5))
            set_mtime(codex_history, AS_OF_DATETIME - timedelta(days=100))

            target_metadata = unreadable_metadata.stat()
            original_fstat = AUDIT_MODULE.os.fstat
            failed = False

            def fail_one_stat(fd: int) -> os.stat_result:
                nonlocal failed
                metadata = original_fstat(fd)
                if (metadata.st_dev, metadata.st_ino) == (target_metadata.st_dev, target_metadata.st_ino):
                    failed = True
                    raise OSError("synthetic failed-stat")
                return metadata

            with mock.patch.object(AUDIT_MODULE.os, "fstat", new=fail_one_stat):
                report = AUDIT_MODULE.build_report(
                    repo,
                    catalog,
                    claude_dir,
                    codex_dir,
                    AS_OF_DATETIME,
                    90,
                    30,
                )

            self.assertTrue(failed)
            row = matrix_row(report, "systematic-debugging")
            self.assertFalse(report["coverage"]["claude"]["available"])
            self.assertFalse(report["coverage"]["claude"]["coverage_complete"])
            self.assertFalse(report["coverage"]["complete"])
            self.assertEqual(row["counts"]["primary"]["total"], 0)
            self.assertEqual(row["disposition"], "insufficient-evidence")
            self.assertEqual(row["protection_reason"], "incomplete-history")

    def test_malformed_record_fails_coverage_closed_in_actual_audit_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            source = write_skill(repo, "skills/personal/systematic-debugging")
            manifest = write_manifest(
                repo,
                [{"name": "systematic-debugging", "source": str(source.relative_to(repo)), "ownership": "repo"}],
            )
            write_skill(repo, "skills/superpowers/skills/test-driven-development")
            self.seed_old_repo_history(repo)
            catalog = AUDIT_MODULE.load_catalog_manifest(repo, manifest)
            claude_dir = repo / "transcripts" / "claude"
            codex_dir = repo / "transcripts" / "codex"
            claude_dir.mkdir(parents=True)
            codex_dir.mkdir(parents=True)
            claude_history = claude_dir / "history.jsonl"
            malformed = claude_dir / "malformed.jsonl"
            codex_history = codex_dir / "history.jsonl"
            claude_history.write_text("\n", encoding="utf-8")
            malformed.write_bytes(
                claude_skill_event("writing-plans").encode("utf-8") + b" synthetic-trailing-bytes\n"
            )
            codex_history.write_text("\n", encoding="utf-8")
            set_mtime(claude_history, AS_OF_DATETIME - timedelta(days=100))
            set_mtime(malformed, AS_OF_DATETIME - timedelta(days=5))
            set_mtime(codex_history, AS_OF_DATETIME - timedelta(days=100))

            report = AUDIT_MODULE.build_report(
                repo,
                catalog,
                claude_dir,
                codex_dir,
                AS_OF_DATETIME,
                90,
                30,
            )

            row = matrix_row(report, "systematic-debugging")
            self.assertFalse(report["coverage"]["claude"]["available"])
            self.assertFalse(report["coverage"]["claude"]["coverage_complete"])
            self.assertEqual(report["coverage"]["claude"]["input_errors"], 1)
            self.assertFalse(report["coverage"]["complete"])
            self.assertEqual(row["counts"]["primary"]["total"], 0)
            self.assertEqual(row["disposition"], "insufficient-evidence")
            self.assertEqual(row["protection_reason"], "incomplete-history")

    def test_invalid_utf8_in_skipped_string_fails_coverage_closed_in_actual_audit_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, catalog, claude_dir, codex_dir = self.make_established_zero_usage_audit_inputs(tmp)
            malformed = claude_dir / "invalid-utf8-skipped.jsonl"
            malformed.write_bytes(
                b'{"type":"assistant","message":{'
                b'"role":"assistant","content":[{"type":"tool_use","name":"Skill",'
                b'"input":{"skill":"writing-plans"}}],"unregistered":"\x80"}}\n'
            )
            set_mtime(malformed, AS_OF_DATETIME - timedelta(days=5))

            report = AUDIT_MODULE.build_report(
                repo,
                catalog,
                claude_dir,
                codex_dir,
                AS_OF_DATETIME,
                90,
                30,
            )

            claude_coverage = report["coverage"]["claude"]
            row = matrix_row(report, "systematic-debugging")
            self.assertFalse(claude_coverage["available"])
            self.assertFalse(claude_coverage["input_complete"])
            self.assertFalse(claude_coverage["coverage_complete"])
            self.assertEqual(claude_coverage["input_errors"], 1)
            self.assertFalse(report["coverage"]["complete"])
            self.assertEqual(row["counts"]["primary"]["total"], 0)
            self.assertEqual(row["disposition"], "insufficient-evidence")
            self.assertEqual(row["protection_reason"], "incomplete-history")

    def test_valid_unicode_in_skipped_string_preserves_actual_audit_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, catalog, claude_dir, codex_dir = self.make_established_zero_usage_audit_inputs(tmp)
            valid = claude_dir / "valid-unicode-skipped.jsonl"
            valid.write_bytes(
                (
                    json.dumps(
                        {
                            "type": "assistant",
                            "message": {
                                "role": "assistant",
                                "content": [
                                    {
                                        "type": "tool_use",
                                        "name": "Skill",
                                        "input": {"skill": "systematic-debugging"},
                                    }
                                ],
                                "unregistered": "synthetic unicode ☃",
                            },
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                ).encode("utf-8")
            )
            set_mtime(valid, AS_OF_DATETIME - timedelta(days=5))

            report = AUDIT_MODULE.build_report(
                repo,
                catalog,
                claude_dir,
                codex_dir,
                AS_OF_DATETIME,
                90,
                30,
            )

            claude_coverage = report["coverage"]["claude"]
            row = matrix_row(report, "systematic-debugging")
            self.assertTrue(claude_coverage["available"])
            self.assertTrue(claude_coverage["input_complete"])
            self.assertTrue(claude_coverage["coverage_complete"])
            self.assertEqual(claude_coverage["input_errors"], 0)
            self.assertTrue(report["coverage"]["complete"])
            self.assertEqual(row["counts"]["primary"]["total"], 1)

    def test_real_extractors_ignore_skill_like_decoys_in_unverified_event_fields(self) -> None:
        claude_fixture = FIXTURES / "claude-events.jsonl"
        codex_fixture = FIXTURES / "codex-events.jsonl"
        claude_records = fixture_records("claude-events.jsonl")
        codex_records = fixture_records("codex-events.jsonl")

        user_contents = [
            record["message"]["content"]
            for record in claude_records
            if record.get("type") == "user" and record.get("message", {}).get("role") == "user"
        ]
        self.assertTrue(
            any(
                "<command-message>" not in content
                and "<command-name>/systematic-debugging</command-name>" in content
                for content in user_contents
            )
        )
        self.assertTrue(
            any(
                "<command-args><command-name>/systematic-debugging</command-name></command-args>" in content
                for content in user_contents
            )
        )
        self.assertTrue(
            any(
                record.get("payload", {}).get("type") == "function_call"
                and record["payload"].get("name") != "read_file"
                and json.loads(record["payload"]["arguments"]).get("path")
                == "skills/personal/systematic-debugging/SKILL.md"
                for record in codex_records
            )
        )

        claude_counts = AUDIT_MODULE.scan_claude([claude_fixture])
        codex_counts = AUDIT_MODULE.scan_codex([codex_fixture])

        self.assertEqual(claude_counts["writing-plans"], 1)
        self.assertEqual(codex_counts["test-driven-development"], 1)
        self.assertEqual(claude_counts["systematic-debugging"], 0)
        self.assertEqual(codex_counts["systematic-debugging"], 0)

    def test_codex_read_file_skips_false_and_null_unregistered_arguments(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            transcript = Path(tmp) / "codex-events.jsonl"
            transcript.write_text(
                json.dumps(
                    {
                        "type": "response_item",
                        "payload": {
                            "type": "function_call",
                            "name": "read_file",
                            "arguments": json.dumps(
                                {
                                    "path": "skills/superpowers/skills/test-driven-development/SKILL.md",
                                    "cache": False,
                                    "optional": None,
                                }
                            ),
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )

            outcome = AUDIT_MODULE.scan_codex([transcript])

            self.assertEqual(outcome["test-driven-development"], 1)
            self.assertTrue(outcome.input_complete)

    def make_complete_catalog(self, repo: Path) -> Path:
        entries = []
        for name in CANDIDATES:
            relative = f"skills/personal/{name}"
            if name == "test-driven-development":
                relative = "skills/superpowers/skills/test-driven-development"
            if name == "subagent-driven-development":
                relative = "skills/vendor/subagent-driven-development"
            write_skill(repo, relative)
            entries.append(
                {
                    "name": name,
                    "source": relative,
                    "ownership": "submodule" if name == "subagent-driven-development" else "repo",
                }
            )
        (repo / "skills/vendor/.git").mkdir(parents=True)
        return write_manifest(repo, entries)

    def seed_old_repo_history(self, repo: Path) -> None:
        subprocess.run(["git", "-C", str(repo), "init", "-q"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
        subprocess.run(["git", "-C", str(repo), "config", "user.name", "Audit Fixture"], check=True)
        subprocess.run(["git", "-C", str(repo), "add", "skills/personal", "skills/superpowers"], check=True)
        old = AS_OF_DATETIME - timedelta(days=180)
        env = os.environ.copy()
        env["GIT_AUTHOR_DATE"] = old.isoformat()
        env["GIT_COMMITTER_DATE"] = old.isoformat()
        subprocess.run(
            ["git", "-C", str(repo), "commit", "-qm", "fixture history"],
            check=True,
            env=env,
        )

    def make_established_zero_usage_audit_inputs(self, tmp: str) -> tuple[Path, dict, Path, Path]:
        """Build only synthetic, otherwise coverage-complete audit inputs."""
        repo = Path(tmp) / "repo"
        repo.mkdir()
        source = write_skill(repo, "skills/personal/systematic-debugging")
        manifest = write_manifest(
            repo,
            [{"name": "systematic-debugging", "source": str(source.relative_to(repo)), "ownership": "repo"}],
        )
        write_skill(repo, "skills/superpowers/skills/test-driven-development")
        self.seed_old_repo_history(repo)
        catalog = AUDIT_MODULE.load_catalog_manifest(repo, manifest)
        claude_dir = repo / "transcripts" / "claude"
        codex_dir = repo / "transcripts" / "codex"
        claude_dir.mkdir(parents=True)
        codex_dir.mkdir(parents=True)
        for transcript_dir in (claude_dir, codex_dir):
            marker = transcript_dir / "history.jsonl"
            marker.write_text("\n", encoding="utf-8")
            set_mtime(marker, AS_OF_DATETIME - timedelta(days=100))
        return repo, catalog, claude_dir, codex_dir

    def test_actual_audit_path_discovers_normal_nested_transcripts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, catalog, claude_dir, codex_dir = self.make_established_zero_usage_audit_inputs(tmp)
            nested_event = claude_dir / "normal-nested" / "recent.jsonl"
            nested_event.parent.mkdir()
            nested_event.write_text(claude_skill_event("writing-plans") + "\n", encoding="utf-8")
            set_mtime(nested_event, AS_OF_DATETIME - timedelta(days=5))

            report = AUDIT_MODULE.build_report(
                repo,
                catalog,
                claude_dir,
                codex_dir,
                AS_OF_DATETIME,
                90,
                30,
            )

            claude_coverage = report["coverage"]["claude"]
            self.assertTrue(claude_coverage["available"])
            self.assertTrue(claude_coverage["coverage_complete"])
            self.assertEqual(claude_coverage["input_errors"], 0)
            self.assertEqual(claude_coverage["files_available"], 2)
            self.assertEqual(claude_coverage["files_scanned_primary"], 1)
            self.assertTrue(report["coverage"]["complete"])
            self.assertEqual(matrix_row(report, "systematic-debugging")["disposition"], "candidate-follow-up")

    def test_nested_traversal_denial_fails_coverage_closed_in_actual_audit_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, catalog, claude_dir, codex_dir = self.make_established_zero_usage_audit_inputs(tmp)
            denied_dir = claude_dir / "synthetic-denied"
            denied_event = denied_dir / "recent.jsonl"
            denied_dir.mkdir()
            denied_event.write_text(claude_skill_event("writing-plans") + "\n", encoding="utf-8")
            set_mtime(denied_event, AS_OF_DATETIME - timedelta(days=5))

            denied_metadata = denied_dir.stat()
            original_scandir = AUDIT_MODULE.os.scandir
            denied = False

            def deny_nested_directory(path: object) -> object:
                nonlocal denied
                if isinstance(path, int):
                    metadata = os.fstat(path)
                    if (metadata.st_dev, metadata.st_ino) == (denied_metadata.st_dev, denied_metadata.st_ino):
                        denied = True
                        raise PermissionError("synthetic nested traversal denial")
                return original_scandir(path)

            with mock.patch.object(AUDIT_MODULE.os, "scandir", new=deny_nested_directory):
                report = AUDIT_MODULE.build_report(
                    repo,
                    catalog,
                    claude_dir,
                    codex_dir,
                    AS_OF_DATETIME,
                    90,
                    30,
                )

            self.assertTrue(denied)
            claude_coverage = report["coverage"]["claude"]
            row = matrix_row(report, "systematic-debugging")
            self.assertFalse(claude_coverage["available"])
            self.assertFalse(claude_coverage["input_complete"])
            self.assertFalse(claude_coverage["coverage_complete"])
            self.assertEqual(claude_coverage["input_errors"], 1)
            self.assertFalse(report["coverage"]["complete"])
            self.assertEqual(row["counts"]["primary"]["total"], 0)
            self.assertEqual(row["disposition"], "insufficient-evidence")
            self.assertEqual(row["protection_reason"], "incomplete-history")

    def assert_synthetic_swap_fails_coverage_closed(self, report: dict) -> None:
        claude_coverage = report["coverage"]["claude"]
        row = matrix_row(report, "systematic-debugging")
        self.assertEqual(row["counts"]["primary"]["total"], 0)
        self.assertFalse(claude_coverage["available"])
        self.assertFalse(claude_coverage["input_complete"])
        self.assertFalse(claude_coverage["coverage_complete"])
        self.assertEqual(claude_coverage["input_errors"], 1)
        self.assertFalse(report["coverage"]["complete"])
        self.assertEqual(row["disposition"], "insufficient-evidence")
        self.assertEqual(row["protection_reason"], "incomplete-history")

    def test_file_symlink_swap_fails_coverage_closed_in_actual_audit_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, catalog, claude_dir, codex_dir = self.make_established_zero_usage_audit_inputs(tmp)
            queued_event = claude_dir / "queued-file.jsonl"
            outside_event = Path(tmp) / "synthetic-outside-file.jsonl"
            queued_event.write_text(claude_skill_event("writing-plans") + "\n", encoding="utf-8")
            outside_event.write_text(claude_skill_event("systematic-debugging") + "\n", encoding="utf-8")
            set_mtime(queued_event, AS_OF_DATETIME - timedelta(days=5))
            swapped = False
            original_scan = AUDIT_MODULE.scan_claude

            def swap_before_scan(files: object, sensitivity_files: object = ()) -> object:
                nonlocal swapped
                queued_event.unlink()
                queued_event.symlink_to(outside_event)
                swapped = True
                return original_scan(files, sensitivity_files)

            with mock.patch.object(AUDIT_MODULE, "scan_claude", new=swap_before_scan):
                report = AUDIT_MODULE.build_report(
                    repo,
                    catalog,
                    claude_dir,
                    codex_dir,
                    AS_OF_DATETIME,
                    90,
                    30,
                )

            self.assertTrue(swapped)
            self.assert_synthetic_swap_fails_coverage_closed(report)

    def test_queued_directory_symlink_swap_fails_coverage_closed_in_actual_audit_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo, catalog, claude_dir, codex_dir = self.make_established_zero_usage_audit_inputs(tmp)
            queued_directory = claude_dir / "queued-directory"
            queued_event = queued_directory / "recent.jsonl"
            moved_directory = claude_dir / "moved-directory"
            outside_directory = Path(tmp) / "synthetic-outside-directory"
            outside_event = outside_directory / "recent.jsonl"
            queued_directory.mkdir()
            outside_directory.mkdir()
            queued_event.write_text(claude_skill_event("writing-plans") + "\n", encoding="utf-8")
            outside_event.write_text(claude_skill_event("systematic-debugging") + "\n", encoding="utf-8")
            set_mtime(queued_event, AS_OF_DATETIME - timedelta(days=5))
            swapped = False
            original_scan = AUDIT_MODULE.scan_claude

            def swap_before_scan(files: object, sensitivity_files: object = ()) -> object:
                nonlocal swapped
                queued_directory.rename(moved_directory)
                queued_directory.symlink_to(outside_directory, target_is_directory=True)
                swapped = True
                return original_scan(files, sensitivity_files)

            with mock.patch.object(AUDIT_MODULE, "scan_claude", new=swap_before_scan):
                report = AUDIT_MODULE.build_report(
                    repo,
                    catalog,
                    claude_dir,
                    codex_dir,
                    AS_OF_DATETIME,
                    90,
                    30,
                )

            self.assertTrue(swapped)
            self.assert_synthetic_swap_fails_coverage_closed(report)

    def run_audit(self, repo: Path, manifest: Path, claude_dir: Path, codex_dir: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [
                sys.executable,
                str(AUDIT_SCRIPT),
                "--repo-root",
                str(repo),
                "--catalog-manifest",
                str(manifest),
                "--claude-dir",
                str(claude_dir),
                "--codex-dir",
                str(codex_dir),
                "--as-of",
                AS_OF,
                "--since-days",
                "90",
                "--sensitivity-days",
                "30",
                "--json",
            ],
            capture_output=True,
            text=True,
            check=False,
        )

    def test_report_counts_only_verified_event_fields_and_redacts_fixture_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            manifest = self.make_complete_catalog(repo)
            self.seed_old_repo_history(repo)
            claude_dir = repo / "transcripts" / "claude"
            codex_dir = repo / "transcripts" / "codex"
            claude_dir.mkdir(parents=True)
            codex_dir.mkdir(parents=True)
            shutil.copyfile(FIXTURES / "claude-events.jsonl", claude_dir / "events.jsonl")
            shutil.copyfile(FIXTURES / "codex-events.jsonl", codex_dir / "events.jsonl")
            for source in (claude_dir, codex_dir):
                marker = source / "history.jsonl"
                marker.write_text("\n", encoding="utf-8")
                set_mtime(marker, AS_OF_DATETIME - timedelta(days=100))
            for event_file in (claude_dir / "events.jsonl", codex_dir / "events.jsonl"):
                set_mtime(event_file, AS_OF_DATETIME - timedelta(days=5))

            result = self.run_audit(repo, manifest, claude_dir, codex_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            test_driven = matrix_row(report, "test-driven-development")
            self.assertEqual(test_driven["counts"]["primary"]["claude"], 1)
            self.assertEqual(test_driven["counts"]["primary"]["codex"], 1)
            self.assertEqual(matrix_row(report, "writing-plans")["counts"]["primary"]["claude"], 1)
            self.assertEqual(matrix_row(report, "brainstorming")["counts"]["primary"]["claude"], 1)
            self.assertEqual(
                matrix_row(report, "dispatching-parallel-agents")["counts"]["primary"]["codex"],
                1,
            )
            self.assertEqual(matrix_row(report, "systematic-debugging")["counts"]["primary"]["total"], 0)
            self.assertEqual(matrix_row(report, "systematic-debugging")["disposition"], "candidate-follow-up")
            self.assertEqual(matrix_row(report, "subagent-driven-development")["ownership"], "submodule")
            self.assertEqual(matrix_row(report, "subagent-driven-development")["freshness"], "unknown-age")
            self.assertTrue(report["coverage"]["complete"])
            self.assertEqual(len(report["decision_matrix"]), 13)
            for forbidden in (
                "SYNTHETIC_SECRET_SENTINEL_AIB_C4M",
                "fixture-session-id",
                "fixture-project",
                str(repo),
                "events.jsonl",
                "history.jsonl",
            ):
                self.assertNotIn(forbidden, result.stdout)

    def test_audit_generates_the_linker_manifest_without_creating_tool_homes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            scripts_dir = repo / "scripts"
            scripts_dir.mkdir()
            linker_copy = scripts_dir / "link-ai-skills.sh"
            shutil.copyfile(LINKER, linker_copy)
            linker_copy.chmod(0o755)
            write_skill(repo, "skills/personal/systematic-debugging")
            claude_dir = repo / "transcripts" / "claude"
            codex_dir = repo / "transcripts" / "codex"
            claude_dir.mkdir(parents=True)
            codex_dir.mkdir(parents=True)
            (claude_dir / "recent.jsonl").write_text("{}\n", encoding="utf-8")
            (codex_dir / "recent.jsonl").write_text("{}\n", encoding="utf-8")
            set_mtime(claude_dir / "recent.jsonl", AS_OF_DATETIME - timedelta(days=2))
            set_mtime(codex_dir / "recent.jsonl", AS_OF_DATETIME - timedelta(days=2))

            result = subprocess.run(
                [
                    sys.executable,
                    str(AUDIT_SCRIPT),
                    "--repo-root",
                    str(repo),
                    "--claude-dir",
                    str(claude_dir),
                    "--codex-dir",
                    str(codex_dir),
                    "--as-of",
                    AS_OF,
                    "--json",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            row = matrix_row(report, "systematic-debugging")
            self.assertEqual(row["source"], "skills/personal/systematic-debugging")
            self.assertFalse((repo / ".claude").exists())
            self.assertFalse((repo / ".codex").exists())
            self.assertFalse((repo / ".gemini").exists())

    def test_short_history_makes_zero_count_insufficient_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            source = write_skill(repo, "skills/personal/systematic-debugging")
            manifest = write_manifest(
                repo,
                [{"name": "systematic-debugging", "source": str(source.relative_to(repo)), "ownership": "repo"}],
            )
            claude_dir = repo / "transcripts" / "claude"
            codex_dir = repo / "transcripts" / "codex"
            claude_dir.mkdir(parents=True)
            codex_dir.mkdir(parents=True)
            (claude_dir / "recent.jsonl").write_text("{}\n", encoding="utf-8")
            (codex_dir / "recent.jsonl").write_text("{}\n", encoding="utf-8")
            set_mtime(claude_dir / "recent.jsonl", AS_OF_DATETIME - timedelta(days=2))
            set_mtime(codex_dir / "recent.jsonl", AS_OF_DATETIME - timedelta(days=2))

            result = self.run_audit(repo, manifest, claude_dir, codex_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertFalse(report["coverage"]["complete"])
            self.assertEqual(matrix_row(report, "systematic-debugging")["disposition"], "insufficient-evidence")

    def test_one_sided_coverage_keeps_zero_count_insufficient_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            source = write_skill(repo, "skills/personal/systematic-debugging")
            manifest = write_manifest(
                repo,
                [{"name": "systematic-debugging", "source": str(source.relative_to(repo)), "ownership": "repo"}],
            )
            write_skill(repo, "skills/superpowers/skills/test-driven-development")
            self.seed_old_repo_history(repo)
            claude_dir = repo / "transcripts" / "claude"
            codex_dir = repo / "transcripts" / "codex"
            claude_dir.mkdir(parents=True)
            codex_dir.mkdir(parents=True)
            claude_history = claude_dir / "history.jsonl"
            codex_recent = codex_dir / "recent.jsonl"
            shutil.copyfile(FIXTURES / "claude-events.jsonl", claude_history)
            shutil.copyfile(FIXTURES / "codex-events.jsonl", codex_recent)
            set_mtime(claude_history, AS_OF_DATETIME - timedelta(days=100))
            set_mtime(codex_recent, AS_OF_DATETIME - timedelta(days=2))

            result = self.run_audit(repo, manifest, claude_dir, codex_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            row = matrix_row(report, "systematic-debugging")
            self.assertTrue(report["coverage"]["claude"]["coverage_complete"])
            self.assertFalse(report["coverage"]["codex"]["coverage_complete"])
            self.assertFalse(report["coverage"]["complete"])
            self.assertEqual(row["freshness"], "established")
            self.assertEqual(row["counts"]["primary"]["total"], 0)
            self.assertEqual(row["disposition"], "insufficient-evidence")
            self.assertEqual(row["protection_reason"], "incomplete-history")

    def test_thresholds_keep_marginal_and_zero_usage_in_review_only_states(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "repo"
            repo.mkdir()
            manifest = self.make_complete_catalog(repo)
            self.seed_old_repo_history(repo)
            claude_dir = repo / "transcripts" / "claude"
            codex_dir = repo / "transcripts" / "codex"
            claude_dir.mkdir(parents=True)
            codex_dir.mkdir(parents=True)
            events = claude_dir / "events.jsonl"
            events.write_text(
                "\n".join(
                    [
                        claude_skill_event("dispatching-parallel-agents"),
                        claude_skill_event("dispatching-parallel-agents"),
                        claude_skill_event("dispatching-parallel-agents"),
                        claude_skill_event("writing-plans"),
                    ]
                )
                + "\n",
                encoding="utf-8",
            )
            for source in (claude_dir, codex_dir):
                marker = source / "history.jsonl"
                marker.write_text("\n", encoding="utf-8")
                set_mtime(marker, AS_OF_DATETIME - timedelta(days=100))
            set_mtime(events, AS_OF_DATETIME - timedelta(days=5))

            result = self.run_audit(repo, manifest, claude_dir, codex_dir)

            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(matrix_row(report, "dispatching-parallel-agents")["disposition"], "retain")
            self.assertEqual(matrix_row(report, "writing-plans")["disposition"], "marginal-review")
            self.assertEqual(matrix_row(report, "systematic-debugging")["disposition"], "candidate-follow-up")
            self.assertEqual(matrix_row(report, "using-superpowers")["disposition"], "measurement-limited")

    def test_as_of_requires_an_explicit_utc_timestamp(self) -> None:
        result = subprocess.run(
            [sys.executable, str(AUDIT_SCRIPT), "--as-of", "2026-08-14T00:00:00", "--json"],
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("UTC", result.stderr)


if __name__ == "__main__":
    unittest.main()
