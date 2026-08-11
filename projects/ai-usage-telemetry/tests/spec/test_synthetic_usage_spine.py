"""Behavior-executing tests for the disposable Synthetic-to-SQLite thesis.

These six tests deliberately exercise the thesis launcher and SQLite seam. The
fixtures are synthetic, and the assertions never inspect thesis private tables
directly; ``stable_view`` is the public oracle.
"""

from __future__ import annotations

import hashlib
import importlib
import io
import json
import sqlite3
from pathlib import Path

import pytest

from thesis.harness import (
    CaptureViolation,
    HarnessConfig,
    ThesisHarness,
    ValidationError,
)
from thesis.launcher import launch


ROOT = Path(__file__).parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "synthetic-thesis"
QUALIFIED = FIXTURES / "qualified-claude.jsonl"
MANIFEST = FIXTURES / "manifest.json"
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


class _NoWholePayloadDecode(bytes):
    """Permit byte scanning but fail if the complete raw record becomes text."""

    def decode(self, *args: object, **kwargs: object) -> str:
        raise AssertionError("the complete skipped payload was decoded")

    def splitlines(self, *args: object, **kwargs: object) -> list[bytes]:
        return [self]


def config(tmp_path: Path, **overrides: object) -> HarnessConfig:
    values: dict[str, object] = {
        "fixture_path": QUALIFIED,
        "manifest_path": MANIFEST,
        "database_path": tmp_path / "thesis.sqlite3",
    }
    values.update(overrides)
    return HarnessConfig(**values)


def test_req_synthetic_usage_spine_001(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
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

    drifted_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    drifted_manifest["required_fields"] = ["requestId"]
    drifted_manifest_database = tmp_path / "drifted-manifest" / "thesis.sqlite3"
    original_open = Path.open

    def open_drifted_manifest(path: Path, *args: object, **kwargs: object) -> object:
        if path == MANIFEST:
            return io.StringIO(json.dumps(drifted_manifest))
        return original_open(path, *args, **kwargs)

    with monkeypatch.context() as manifest_patch:
        manifest_patch.setattr(Path, "open", open_drifted_manifest)
        with pytest.raises(ValidationError) as error:
            launch(config(tmp_path, database_path=drifted_manifest_database))
    assert error.value.code == "manifest_invalid"
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


def test_req_synthetic_usage_spine_003(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    original_read_bytes = Path.read_bytes

    def guarded_read_bytes(path: Path) -> bytes:
        payload = original_read_bytes(path)
        return _NoWholePayloadDecode(payload) if path == QUALIFIED else payload

    monkeypatch.setattr(Path, "read_bytes", guarded_read_bytes)
    harness = ThesisHarness(config(tmp_path))
    result = harness.run_privacy()
    assert result.status == "accepted"
    assert result.forbidden_decoder_calls == 0
    assert result.forbidden_materializer_calls == 0
    assert result.forbidden_fingerprint_calls == 0
    assert result.public_capture == EXPECTED_STABLE_VIEW
    captured_bytes = json.dumps(
        {
            "public_capture": result.public_capture,
            "capture_canaries": result.capture_canaries,
            "capture_observations": result.capture_observations,
        },
        sort_keys=True,
    ).encode("utf-8")
    forbidden_sentinel = b"THESIS_FORBIDDEN_CONTENT_SENTINEL"
    assert forbidden_sentinel not in captured_bytes
    assert (
        hashlib.sha256(forbidden_sentinel).hexdigest().encode("ascii")
        not in captured_bytes
    )
    expected_lanes = json.loads(MANIFEST.read_text(encoding="utf-8"))[
        "capture_canaries"
    ]
    assert set(result.capture_canaries) == set(expected_lanes)
    assert len(set(result.capture_canaries.values())) == len(expected_lanes)
    assert result.capture_observations == {
        lane: (result.capture_canaries[lane],) for lane in expected_lanes
    }
    for mutation, lane in (
        ("leak", "application_value"),
        ("decoder", "parser_instrumentation"),
        ("materializer", "application_value"),
        ("fingerprint", "application_value"),
        ("network", "network"),
    ):
        with pytest.raises(CaptureViolation, match=lane):
            ThesisHarness(config(tmp_path / mutation)).run_privacy(mutation=mutation)


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
