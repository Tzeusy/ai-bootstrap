# /// script
# requires-python = ">=3.11"
# ///

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = SKILL_ROOT / "scripts" / "skill_usage_audit.py"
REPO_ROOT = SKILL_ROOT.parents[4]
LINKER = REPO_ROOT / "scripts" / "link-ai-skills.sh"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
AS_OF = "2026-08-14T00:00:00Z"
AS_OF_DATETIME = datetime(2026, 8, 14, tzinfo=timezone.utc)

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

    def test_report_counts_structured_events_and_redacts_fixture_metadata(self) -> None:
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
            self.assertEqual(
                matrix_row(report, "dispatching-parallel-agents")["counts"]["primary"]["codex"],
                1,
            )
            self.assertEqual(matrix_row(report, "systematic-debugging")["counts"]["primary"]["total"], 0)
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
                        '{"name":"Skill","input":{"skill":"dispatching-parallel-agents"}}',
                        '{"name":"Skill","input":{"skill":"dispatching-parallel-agents"}}',
                        '{"name":"Skill","input":{"skill":"dispatching-parallel-agents"}}',
                        '{"name":"Skill","input":{"skill":"writing-plans"}}',
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
