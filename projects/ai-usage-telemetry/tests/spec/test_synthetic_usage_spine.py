"""Behavior-executing tests for the disposable Synthetic-to-SQLite thesis.

These six tests deliberately exercise the thesis launcher and SQLite seam. The
fixtures are synthetic. Public accounting assertions use ``stable_view`` while
the privacy harness scans every private table, public view, and durable DB page.
"""

from __future__ import annotations

import importlib
import json
import shutil
import sqlite3
import subprocess
import sys
from pathlib import Path

import pytest

from thesis.harness import (
    CaptureViolation,
    HarnessConfig,
    ProjectionStats,
    ThesisHarness,
    ValidationError,
)
from thesis.launcher import launch


ROOT = Path(__file__).parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "synthetic-thesis"
QUALIFIED = FIXTURES / "qualified-claude.jsonl"
MANIFEST = FIXTURES / "manifest.json"
DECISION_0002 = (
    ROOT
    / "about"
    / "heart-and-soul"
    / "decisions"
    / "0002-accept-v1-capability-contracts.md"
)
SYNTHETIC_SPEC = (
    ROOT
    / "openspec"
    / "changes"
    / "establish-ai-usage-telemetry-v1"
    / "specs"
    / "synthetic-usage-spine"
    / "spec.md"
)
FORBIDDEN_SENTINEL = b"THESIS_FORBIDDEN_CONTENT_SENTINEL"
FORBIDDEN_SENTINEL_DIGEST = (
    b"0fe97be8663ee8538bd2b44dca59652a69847c3b9dd95ce13a3bf6267611507a"
)
ESCAPED_FORBIDDEN_SENTINEL = b"".join(
    f"\\u{byte:04x}".encode("ascii") for byte in FORBIDDEN_SENTINEL
)
EXPECTED_AMOUNTS = {
    "input_tokens": 11,
    "output_tokens": 7,
    "cache_read_tokens": 3,
    "cache_write_tokens": 2,
}
EXPECTED_STABLE_VIEW = {
    "events": [
        {
            "tool": "synthetic-claude",
            "request_id": "synthetic-request-001",
            "message_id": "synthetic-message-001",
            "model": "claude-synthetic-v1",
            "source_time": "2026-01-02T03:04:05Z",
            "cwd": "/synthetic/project",
            "project": "synthetic-project",
            "ledger_seq": 1,
        }
    ],
    "amounts": EXPECTED_AMOUNTS,
    "logical_requests": ["synthetic-request-001"],
    "sequences": [1],
    "aggregates": EXPECTED_AMOUNTS,
    "obligations": [{"ledger_seq": 1, "obligation": "synthetic"}],
    "cursors": {"synthetic": 1},
}
EMPTY_STABLE_VIEW = {
    "events": [],
    "amounts": {},
    "logical_requests": [],
    "sequences": [],
    "aggregates": {},
    "obligations": [],
    "cursors": {},
}
DOCUMENTED_READ_COMMANDS = (
    "usage_events",
    "usage_event_amounts",
    "logical_requests",
    "synthetic_aggregates",
    "ledger_health",
    "health",
)
FIXTURE_ORACLE = {
    "tool": "synthetic-claude",
    "source_time": "2026-01-02T03:04:05Z",
    "model": "claude-synthetic-v1",
    "project": "synthetic-project",
    "categories": "input_tokens,output_tokens,cache_read_tokens,cache_write_tokens",
    "amounts": "11,7,3,2",
    "logical_request": "1",
    "replay_counts": "unchanged",
    "health": "healthy",
}


def config(tmp_path: Path, **overrides: object) -> HarnessConfig:
    values: dict[str, object] = {
        "fixture_path": QUALIFIED,
        "manifest_path": MANIFEST,
        "database_path": tmp_path / "thesis.sqlite3",
    }
    values.update(overrides)
    return HarnessConfig(**values)


def _isolated_thesis_project(tmp_path: Path) -> Path:
    """Copy only the launcher, fixture, and acceptance inputs for real launch tests."""

    project = tmp_path / "isolated-thesis-project"
    shutil.copytree(
        ROOT / "thesis",
        project / "thesis",
        ignore=shutil.ignore_patterns("__pycache__"),
    )
    shutil.copytree(FIXTURES, project / "tests" / "fixtures" / "synthetic-thesis")
    decision = project / DECISION_0002.relative_to(ROOT)
    decision.parent.mkdir(parents=True)
    shutil.copy2(DECISION_0002, decision)
    spec = project / SYNTHETIC_SPEC.relative_to(ROOT)
    spec.parent.mkdir(parents=True)
    shutil.copy2(SYNTHETIC_SPEC, spec)
    return project


def _run_isolated_launch(
    project: Path,
    *,
    runner: str = "launcher",
    missing_harness_resources: bool = False,
) -> tuple[str, Path]:
    database_path = project / "state" / "thesis.sqlite3"
    program = """
from pathlib import Path
import sys

from thesis.harness import HarnessConfig, ThesisHarness, ValidationError
from thesis.launcher import launch

project = Path.cwd()
missing_harness_resources = sys.argv[2] == "missing"
config = HarnessConfig(
    fixture_path=project / "tests" / "fixtures" / "synthetic-thesis" / (
        "missing-fixture.jsonl" if missing_harness_resources else "qualified-claude.jsonl"
    ),
    manifest_path=project / "tests" / "fixtures" / "synthetic-thesis" / (
        "missing-manifest.json" if missing_harness_resources else "manifest.json"
    ),
    database_path=project / "state" / "thesis.sqlite3",
)
try:
    result = launch(config) if sys.argv[1] == "launcher" else ThesisHarness(config).run_once()
except ValidationError as error:
    print(f"rejected:{error.code}")
else:
    print(f"accepted:{result.status}")
"""
    completed = subprocess.run(
        [
            sys.executable,
            "-c",
            program,
            runner,
            "missing" if missing_harness_resources else "present",
        ],
        cwd=project,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip(), database_path


def _run_durable_fixture_process(
    fixture_path: Path, database_path: Path
) -> dict[str, object]:
    """Run one fixture in a fresh interpreter and report only public state."""

    program = """
import json
from pathlib import Path
import sys

from thesis.harness import HarnessConfig, ThesisHarness

root = Path.cwd()
harness = ThesisHarness(HarnessConfig(
    fixture_path=Path(sys.argv[1]),
    manifest_path=root / "tests" / "fixtures" / "synthetic-thesis" / "manifest.json",
    database_path=Path(sys.argv[2]),
))
result = harness.run_once()
print(json.dumps({
    "status": result.status,
    "stable_view": harness.stable_view(),
    "health": harness.health(),
}, sort_keys=True))
harness.close()
"""
    completed = subprocess.run(
        [sys.executable, "-c", program, str(fixture_path), str(database_path)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return json.loads(completed.stdout)


def _assert_real_privacy_fixture_vector(fixture_path: Path) -> None:
    """Keep the matrix's sentinel and limit claims independent of the harness."""

    payload = fixture_path.read_bytes()
    if fixture_path.name == "privacy-escaped.jsonl":
        assert ESCAPED_FORBIDDEN_SENTINEL in payload
        assert FORBIDDEN_SENTINEL not in payload
    else:
        assert FORBIDDEN_SENTINEL in payload

    if fixture_path.name == "privacy-nested.jsonl":
        assert b'"nested"' in payload
    elif fixture_path.name == "privacy-malformed.jsonl":
        assert b"\\u00ZZ" in payload
    elif fixture_path.name == "privacy-oversized-skip.jsonl":
        assert len(payload) > 65_536
    elif fixture_path.name == "privacy-depth-at-limit.jsonl":
        assert payload.count(b"[") == 32
    elif fixture_path.name == "privacy-depth-over-limit.jsonl":
        assert payload.count(b"[") == 33
    elif fixture_path.name == "privacy-duplicate-registered.jsonl":
        assert payload.count(b'"requestId"') == 2


def test_req_synthetic_usage_spine_001(tmp_path: Path) -> None:
    accepted = launch(config(tmp_path))
    assert accepted.status == "accepted"

    negative_fixtures = {
        "negative-requestId.jsonl": "missing_identity",
        "negative-digest.jsonl": "digest_mismatch",
        "negative-projected_type.jsonl": "projected_type",
    }
    for fixture_name, expected_code in negative_fixtures.items():
        database_path = tmp_path / "rejected" / fixture_name / "thesis.sqlite3"
        with pytest.raises(ValidationError) as error:
            launch(
                config(
                    tmp_path,
                    fixture_path=FIXTURES / fixture_name,
                    database_path=database_path,
                )
            )
        assert error.value.code == expected_code
        assert not database_path.exists()
        assert not database_path.parent.exists()

    invalid_manifest_database = tmp_path / "invalid-manifest" / "thesis.sqlite3"
    with pytest.raises(ValidationError) as error:
        launch(
            config(
                tmp_path,
                manifest_path=FIXTURES / "missing-manifest.json",
                database_path=invalid_manifest_database,
            )
        )
    assert error.value.code == "manifest_invalid"
    assert not invalid_manifest_database.exists()
    assert not invalid_manifest_database.parent.exists()

    isolated_project = _isolated_thesis_project(tmp_path / "drifted-manifest")
    isolated_manifest = (
        isolated_project / "tests" / "fixtures" / "synthetic-thesis" / "manifest.json"
    )
    drifted_manifest = json.loads(isolated_manifest.read_text(encoding="utf-8"))
    drifted_manifest["required_fields"] = ["requestId"]
    isolated_manifest.write_text(json.dumps(drifted_manifest), encoding="utf-8")
    outcome, drifted_manifest_database = _run_isolated_launch(isolated_project)
    assert outcome == "rejected:manifest_invalid"
    assert not drifted_manifest_database.exists()
    assert not drifted_manifest_database.parent.exists()

    empty_harness = ThesisHarness(config(tmp_path / "empty"))
    empty_snapshot = empty_harness.snapshot()
    for fixture_name, expected_code in negative_fixtures.items():
        with pytest.raises(ValidationError) as error:
            empty_harness.run_fixture(FIXTURES / fixture_name)
        assert error.value.code == expected_code
        assert empty_harness.snapshot() == empty_snapshot

    copied_fixture = tmp_path / "outside-fixture-root" / "qualified-claude.jsonl"
    copied_fixture.parent.mkdir()
    copied_fixture.write_bytes(QUALIFIED.read_bytes())
    with pytest.raises(ValidationError) as error:
        empty_harness.run_file(copied_fixture)
    assert error.value.code == "forbidden_configuration"
    assert empty_harness.snapshot() == empty_snapshot

    for forbidden in (
        "network",
        "sink",
        "production_package",
        "publish_target",
        "personal_path",
    ):
        database_path = tmp_path / "forbidden" / forbidden / "thesis.sqlite3"
        with pytest.raises(ValidationError) as error:
            launch(config(tmp_path, database_path=database_path, **{forbidden: True}))
        assert error.value.code == "forbidden_configuration"
        assert not database_path.exists()
        assert not database_path.parent.exists()


@pytest.mark.parametrize(
    ("runner", "case", "expected_code"),
    (
        pytest.param(
            "launcher",
            "missing",
            "synthetic_authorization_missing",
            id="launcher-missing",
        ),
        pytest.param(
            "launcher",
            "not-accepted",
            "synthetic_authorization_not_accepted",
            id="launcher-not-accepted",
        ),
        pytest.param(
            "launcher",
            "digest-drift",
            "synthetic_authorization_digest_mismatch",
            id="launcher-digest-drift",
        ),
        pytest.param(
            "harness",
            "not-accepted",
            "synthetic_authorization_not_accepted",
            id="direct-harness-not-accepted",
        ),
    ),
)
def test_launcher_validates_decision_0002_before_harness_resources(
    tmp_path: Path, runner: str, case: str, expected_code: str
) -> None:
    project = _isolated_thesis_project(tmp_path)
    decision = project / DECISION_0002.relative_to(ROOT)
    spec = project / SYNTHETIC_SPEC.relative_to(ROOT)
    if case == "missing":
        decision.unlink()
    elif case == "not-accepted":
        original = decision.read_text(encoding="utf-8")
        updated = original.replace(
            "| `synthetic-usage-spine` | `accepted` |",
            "| `synthetic-usage-spine` | `rejected` |",
            1,
        )
        assert updated != original
        decision.write_text(updated, encoding="utf-8")
    else:
        spec.write_bytes(spec.read_bytes() + b"\n")

    outcome, database_path = _run_isolated_launch(
        project,
        runner=runner,
        missing_harness_resources=True,
    )
    assert outcome == f"rejected:{expected_code}"
    assert not database_path.exists()
    assert not database_path.parent.exists()


def test_req_synthetic_usage_spine_002(tmp_path: Path) -> None:
    harness = ThesisHarness(config(tmp_path))
    result = harness.run_once()
    assert result.status == "accepted"
    assert harness.stable_view() == EXPECTED_STABLE_VIEW

    for boundary in ThesisHarness.WRITE_BOUNDARIES:
        failing = ThesisHarness(config(tmp_path / boundary))
        with pytest.raises(sqlite3.IntegrityError, match="injected"):
            failing.run_once(fail_at=boundary)
        assert failing.stable_view() == EMPTY_STABLE_VIEW
        assert failing.run_once().status == "accepted"
        assert failing.stable_view() == EXPECTED_STABLE_VIEW


@pytest.mark.parametrize(
    ("fixture_name", "expected_status", "expected_code"),
    (
        pytest.param("privacy-nested.jsonl", "accepted", None, id="nested"),
        pytest.param("privacy-escaped.jsonl", "accepted", None, id="escaped"),
        pytest.param(
            "privacy-malformed.jsonl", "rejected", "schema_inconsistent", id="malformed"
        ),
        pytest.param(
            "privacy-oversized-skip.jsonl", "rejected", "record_limit", id="oversized"
        ),
        pytest.param(
            "privacy-depth-at-limit.jsonl", "accepted", None, id="depth-at-limit"
        ),
        pytest.param(
            "privacy-depth-over-limit.jsonl",
            "rejected",
            "record_limit",
            id="depth-over-limit",
        ),
        pytest.param(
            "privacy-duplicate-registered.jsonl",
            "rejected",
            "duplicate_registered_key",
            id="duplicate-registered-key",
        ),
    ),
)
def test_req_synthetic_usage_spine_003_real_fixture_matrix_stays_content_free(
    tmp_path: Path,
    fixture_name: str,
    expected_status: str,
    expected_code: str | None,
) -> None:
    fixture_path = FIXTURES / fixture_name
    _assert_real_privacy_fixture_vector(fixture_path)
    launcher_database = tmp_path / "launcher" / fixture_name / "thesis.sqlite3"
    if expected_status == "accepted":
        assert (
            launch(
                config(
                    tmp_path,
                    fixture_path=fixture_path,
                    database_path=launcher_database,
                )
            ).status
            == "accepted"
        )
    else:
        with pytest.raises(ValidationError) as error:
            launch(
                config(
                    tmp_path,
                    fixture_path=fixture_path,
                    database_path=launcher_database,
                )
            )
        assert error.value.code == expected_code
        assert not launcher_database.exists()
        assert not launcher_database.parent.exists()

    harness = ThesisHarness(config(tmp_path / "privacy-probe"))
    result = harness.run_privacy(fixture_path=fixture_path)
    assert result.status == expected_status
    assert result.rejection_code == expected_code
    assert result.forbidden_decoder_calls == 0
    assert result.forbidden_materializer_calls == 0
    assert result.forbidden_fingerprint_calls == 0
    assert result.framing is not None
    assert result.framing.line_is_memoryview is True
    assert result.framing.shares_source_buffer is True
    assert result.framing.source_is_mmap is True
    expected_view = (
        EXPECTED_STABLE_VIEW if expected_status == "accepted" else EMPTY_STABLE_VIEW
    )
    assert result.public_capture == expected_view
    assert harness.stable_view() == expected_view

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert manifest["max_record_bytes"] == 65_536
    assert manifest["max_container_depth"] == 32
    expected_lanes = manifest["capture_canaries"]
    assert all("sha256" not in entry for entry in manifest["fixtures"].values())
    assert all(
        "projected_sha256" in entry for entry in manifest["fixtures"].values()
    )
    assert result.capture_canaries is not None
    assert set(result.capture_canaries) == set(expected_lanes)
    assert len(set(result.capture_canaries.values())) == len(expected_lanes)
    assert result.capture_observations == {
        lane: (result.capture_canaries[lane],) for lane in expected_lanes
    }
    assert result.fingerprint_calls == (1 if expected_status == "accepted" else 0)
    assert result.sqlite_bound_parameter_calls >= 1
    assert result.sqlite_objects_scanned == len(ThesisHarness.SQLITE_CAPTURE_OBJECTS) + 1
    captured_bytes = json.dumps(
        {
            "public_capture": result.public_capture,
            "capture_canaries": result.capture_canaries,
            "capture_observations": result.capture_observations,
            "rejection_code": result.rejection_code,
            "framing": {
                "line_is_memoryview": result.framing.line_is_memoryview,
                "shares_source_buffer": result.framing.shares_source_buffer,
                "source_is_mmap": result.framing.source_is_mmap,
            },
        },
        sort_keys=True,
    ).encode("utf-8")
    assert FORBIDDEN_SENTINEL not in captured_bytes
    assert FORBIDDEN_SENTINEL_DIGEST not in captured_bytes
    assert ESCAPED_FORBIDDEN_SENTINEL not in captured_bytes
    assert ".splitlines(" not in (ROOT / "thesis" / "harness.py").read_text(
        encoding="utf-8"
    )


@pytest.mark.parametrize(
    ("mutation", "lane", "expected_stats"),
    (
        pytest.param("leak", "application_value", ProjectionStats(), id="leak"),
        pytest.param(
            "decoder",
            "parser_instrumentation",
            ProjectionStats(forbidden_decoder_calls=1),
            id="decoder",
        ),
        pytest.param(
            "materializer",
            "application_value",
            ProjectionStats(forbidden_materializer_calls=1),
            id="materializer",
        ),
        pytest.param(
            "fingerprint",
            "application_value",
            ProjectionStats(forbidden_fingerprint_calls=1),
            id="fingerprint",
        ),
        pytest.param("sqlite", "sqlite", ProjectionStats(), id="sqlite-parameter"),
        pytest.param(
            "sqlite_escaped", "sqlite", ProjectionStats(), id="sqlite-escaped"
        ),
        pytest.param("network", "network", ProjectionStats(), id="network"),
    ),
)
def test_req_synthetic_usage_spine_003_capture_mutations_fail_before_contribution(
    tmp_path: Path, mutation: str, lane: str, expected_stats: ProjectionStats
) -> None:
    harness = ThesisHarness(config(tmp_path / mutation))
    before = harness.stable_view()
    with pytest.raises(CaptureViolation) as error:
        harness.run_privacy(mutation=mutation)
    assert error.value.lane == lane
    assert error.value.stats == expected_stats
    assert harness.stable_view() == before == EMPTY_STABLE_VIEW


def test_req_synthetic_usage_spine_004(tmp_path: Path) -> None:
    database_path = tmp_path / "durable" / "thesis.sqlite3"
    line_harness = ThesisHarness(config(tmp_path, database_path=database_path))
    first = line_harness.run_line(QUALIFIED, line_number=1)
    assert first.status == "accepted"
    assert line_harness.stable_view() == EXPECTED_STABLE_VIEW
    line_harness.close()

    file_harness = ThesisHarness(config(tmp_path, database_path=database_path))
    file_replay = file_harness.run_file(QUALIFIED)
    assert file_replay.status == "accepted"
    assert file_harness.stable_view() == EXPECTED_STABLE_VIEW

    collision = file_harness.run_file(FIXTURES / "collision-b.jsonl")
    assert collision.status == "identity_collision"
    assert file_harness.stable_view() == EXPECTED_STABLE_VIEW
    assert file_harness.health() == {"stream_state": "identity_collision"}
    file_harness.close()

    rescan_harness = ThesisHarness(config(tmp_path, database_path=database_path))
    replay_after_collision = rescan_harness.rescan_file(QUALIFIED)
    assert replay_after_collision.status == "accepted"
    assert rescan_harness.stable_view() == EXPECTED_STABLE_VIEW
    assert rescan_harness.health() == {"stream_state": "identity_collision"}

    process_database = tmp_path / "process-durable" / "thesis.sqlite3"
    process_a = _run_durable_fixture_process(QUALIFIED, process_database)
    process_b = _run_durable_fixture_process(
        FIXTURES / "collision-b.jsonl", process_database
    )
    process_a_replay = _run_durable_fixture_process(QUALIFIED, process_database)
    assert process_a == {
        "health": {"stream_state": "healthy"},
        "stable_view": EXPECTED_STABLE_VIEW,
        "status": "accepted",
    }
    assert process_b["status"] == "identity_collision"
    assert process_b["stable_view"] == EXPECTED_STABLE_VIEW
    assert process_b["health"] == {"stream_state": "identity_collision"}
    assert process_a_replay["status"] == "accepted"
    assert process_a_replay["stable_view"] == EXPECTED_STABLE_VIEW
    assert process_a_replay["health"] == {"stream_state": "identity_collision"}


def test_req_synthetic_usage_spine_005(tmp_path: Path) -> None:
    evidence = ThesisHarness(config(tmp_path)).documented_exercise(elapsed_seconds=600)
    assert evidence.passed is True
    assert evidence.elapsed_seconds == 600
    assert evidence.read_commands == DOCUMENTED_READ_COMMANDS
    assert evidence.private_table_reads == 0
    assert evidence.answers == FIXTURE_ORACLE

    over_time = ThesisHarness(config(tmp_path / "over-time")).documented_exercise(
        elapsed_seconds=601
    )
    assert over_time.passed is False

    seven_reads = ThesisHarness(config(tmp_path / "seven-reads")).documented_exercise(
        elapsed_seconds=600,
        requested_reads=DOCUMENTED_READ_COMMANDS + ("ledger_health",),
    )
    assert seven_reads.passed is False
    assert len(seven_reads.read_commands) == 7

    private_read = ThesisHarness(config(tmp_path / "private-read")).documented_exercise(
        elapsed_seconds=600,
        requested_reads=DOCUMENTED_READ_COMMANDS[:-1] + ("ledger_events",),
    )
    assert private_read.passed is False
    assert private_read.private_table_reads == 1

    missing_answer = ThesisHarness(
        config(tmp_path / "missing-answer")
    ).documented_exercise(
        elapsed_seconds=600,
        requested_reads=DOCUMENTED_READ_COMMANDS[:-1],
    )
    assert missing_answer.passed is False

    no_reads = ThesisHarness(config(tmp_path / "no-reads")).documented_exercise(
        elapsed_seconds=600,
        requested_reads=(),
    )
    assert no_reads.passed is False


def test_req_synthetic_usage_spine_006(tmp_path: Path) -> None:
    for field, value in (
        ("fixture_path", Path("/private/personal/source.jsonl")),
        ("synthetic", False),
        ("network", True),
        ("sink", True),
        ("production_package", True),
        ("publish_target", True),
        ("credential_reader", True),
        ("concurrent", True),
    ):
        database_path = tmp_path / field / "thesis.sqlite3"
        with pytest.raises(ValidationError, match="forbidden_configuration"):
            launch(config(tmp_path, database_path=database_path, **{field: value}))
        assert not database_path.exists()
        assert not database_path.parent.exists()

    retirement = importlib.import_module("thesis.retirement")
    report = retirement.assert_import_negative(ROOT)
    assert report.production_sources == ()
    assert report.production_package_files == ()

    source_violation = tmp_path / "production-source"
    source_violation.mkdir()
    (source_violation / "service.py").write_text(
        "from thesis.harness import ThesisHarness\n", encoding="utf-8"
    )
    with pytest.raises(ValidationError) as error:
        retirement.assert_import_negative(source_violation)
    assert error.value.code == "production_thesis_import"

    package_violation = tmp_path / "production-package"
    package_violation.mkdir()
    (package_violation / "pyproject.toml").write_text(
        "[project]\nname = 'synthetic-production'\n[tool.setuptools]\npackages = ['thesis']\n",
        encoding="utf-8",
    )
    with pytest.raises(ValidationError) as error:
        retirement.assert_import_negative(package_violation)
    assert error.value.code == "production_thesis_package"
