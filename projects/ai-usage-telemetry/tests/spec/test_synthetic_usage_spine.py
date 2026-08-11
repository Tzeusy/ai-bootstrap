"""Behavior-executing tests for the disposable Synthetic-to-SQLite thesis.

These six tests deliberately exercise the thesis launcher and SQLite seam.  The
fixtures are synthetic, and the assertions never inspect thesis private tables
directly; ``snapshot`` is the stable-view oracle.
"""

from __future__ import annotations

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


ROOT = Path(__file__).parents[2]
FIXTURES = ROOT / "tests" / "fixtures" / "synthetic-thesis"
QUALIFIED = FIXTURES / "qualified-claude.jsonl"
MANIFEST = FIXTURES / "manifest.json"


def config(tmp_path: Path, **overrides: object) -> HarnessConfig:
    values: dict[str, object] = {
        "fixture_path": QUALIFIED,
        "manifest_path": MANIFEST,
        "database_path": tmp_path / "thesis.sqlite3",
    }
    values.update(overrides)
    return HarnessConfig(**values)


def test_req_synthetic_usage_spine_001(tmp_path: Path) -> None:
    accepted = ThesisHarness(config(tmp_path)).run_once()
    assert accepted.status == "accepted"

    for field, value in (
        ("requestId", None),
        ("digest", "000000"),
        ("projected_type", "object"),
    ):
        with pytest.raises(ValidationError) as error:
            ThesisHarness(
                config(tmp_path, fixture_path=FIXTURES / f"negative-{field}.jsonl")
            ).run_once()
        assert error.value.code in {"missing_identity", "digest_mismatch", "projected_type"}

    for forbidden in ("network", "sink", "production_package", "publish_target", "personal_path"):
        with pytest.raises(ValidationError) as error:
            ThesisHarness(config(tmp_path, **{forbidden: True})).run_once()
        assert error.value.code == "forbidden_configuration"


def test_req_synthetic_usage_spine_002(tmp_path: Path) -> None:
    harness = ThesisHarness(config(tmp_path))
    result = harness.run_once()
    assert result.status == "accepted"
    assert harness.snapshot() == {
        "usage_events": 1,
        "usage_event_amounts": 4,
        "logical_requests": 1,
        "ledger_sequences": 1,
        "aggregates": 4,
        "obligations": 1,
        "cursor": 1,
    }

    for boundary in ThesisHarness.WRITE_BOUNDARIES:
        failing = ThesisHarness(config(tmp_path / boundary))
        with pytest.raises(sqlite3.IntegrityError, match="injected"):
            failing.run_once(fail_at=boundary)
        assert failing.snapshot() == {
            "usage_events": 0,
            "usage_event_amounts": 0,
            "logical_requests": 0,
            "ledger_sequences": 0,
            "aggregates": 0,
            "obligations": 0,
            "cursor": 0,
        }
        assert failing.run_once().status == "accepted"


def test_req_synthetic_usage_spine_003(tmp_path: Path) -> None:
    harness = ThesisHarness(config(tmp_path))
    result = harness.run_privacy()
    assert result.status == "accepted"
    assert result.forbidden_decoder_calls == 0
    assert result.forbidden_materializer_calls == 0
    assert result.forbidden_fingerprint_calls == 0
    assert result.forbidden_sentinel not in json.dumps(result.public_capture, sort_keys=True)
    assert set(result.capture_canaries) == set(ThesisHarness.CAPTURE_LANES)
    for mutation in ("leak", "decoder", "materializer", "fingerprint", "network"):
        with pytest.raises(CaptureViolation):
            ThesisHarness(config(tmp_path / mutation)).run_privacy(mutation=mutation)


def test_req_synthetic_usage_spine_004(tmp_path: Path) -> None:
    harness = ThesisHarness(config(tmp_path))
    first = harness.run_once()
    before = harness.snapshot()
    replay = harness.run_once()
    assert first.status == replay.status == "accepted"
    assert harness.snapshot() == before

    collision = harness.run_fixture(FIXTURES / "collision-b.jsonl")
    assert collision.status == "identity_collision"
    assert harness.snapshot() == before
    assert harness.health()["stream_state"] == "identity_collision"


def test_req_synthetic_usage_spine_005(tmp_path: Path) -> None:
    evidence = ThesisHarness(config(tmp_path)).exercise(
        elapsed_seconds=600,
        read_commands=6,
        answers=ThesisHarness.ORACLE_ANSWERS,
        private_table_reads=0,
    )
    assert evidence.passed is True
    assert evidence.elapsed_seconds == 600
    assert evidence.read_commands == 6
    assert evidence.answers == ThesisHarness.ORACLE_ANSWERS

    for kwargs in (
        {"elapsed_seconds": 601},
        {"read_commands": 7},
        {"private_table_reads": 1},
        {"answers": {}},
    ):
        failed = ThesisHarness(config(tmp_path / str(len(kwargs)))).exercise(
            elapsed_seconds=kwargs.get("elapsed_seconds", 600),
            read_commands=kwargs.get("read_commands", 6),
            answers=kwargs.get("answers", ThesisHarness.ORACLE_ANSWERS),
            private_table_reads=kwargs.get("private_table_reads", 0),
        )
        assert failed.passed is False


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
        with pytest.raises(ValidationError, match="forbidden_configuration"):
            ThesisHarness(config(tmp_path, **{field: value})).run_once()

    assert not list((ROOT / "thesis").glob("**/Dockerfile"))
    assert not list((ROOT / "thesis").glob("**/*network*"))
