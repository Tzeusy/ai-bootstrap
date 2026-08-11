"""The disposable one-record Synthetic-to-SQLite thesis.

The parser projects registered scalars only.  Unknown values are skipped by a
structural scanner and are never handed to a JSON decoder, application object,
or fingerprint function.
"""

from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any


FIXTURE_ROOT = Path(__file__).parents[1] / "tests" / "fixtures" / "synthetic-thesis"
FORBIDDEN_SENTINEL = "THESIS_FORBIDDEN_CONTENT_SENTINEL"


class ValidationError(ValueError):
    """Content-free preflight or fixture rejection."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


class CaptureViolation(RuntimeError):
    """A deliberately injected thesis capture mutation was observed."""


@dataclass(frozen=True)
class HarnessConfig:
    fixture_path: Path
    manifest_path: Path
    database_path: Path
    synthetic: bool = True
    network: bool = False
    sink: bool = False
    production_package: bool = False
    publish_target: bool = False
    personal_path: bool = False
    credential_reader: bool = False
    concurrent: bool = False
    fixed_clock: str = "2026-01-02T03:04:05Z"


@dataclass(frozen=True)
class ProjectionStats:
    forbidden_decoder_calls: int = 0
    forbidden_materializer_calls: int = 0
    forbidden_fingerprint_calls: int = 0


@dataclass(frozen=True)
class RunResult:
    status: str
    forbidden_decoder_calls: int = 0
    forbidden_materializer_calls: int = 0
    forbidden_fingerprint_calls: int = 0
    forbidden_sentinel: str = FORBIDDEN_SENTINEL
    public_capture: dict[str, Any] | None = None
    capture_canaries: tuple[str, ...] = ()


@dataclass(frozen=True)
class ExerciseEvidence:
    passed: bool
    elapsed_seconds: int
    read_commands: int
    answers: dict[str, str]
    private_table_reads: int


@dataclass(frozen=True)
class _Record:
    request_id: str
    message_id: str
    model: str
    source_time: str
    cwd: str | None
    project: str | None
    amounts: dict[str, int]
    fingerprint: str
    line: int = 1


class _Projector:
    """Project a single top-level JSON object without decoding skipped values."""

    REGISTERED = {"requestId", "messageId", "model", "sourceTime", "cwd", "project", "amounts"}
    AMOUNT_KEYS = {"input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"}

    def __init__(self) -> None:
        self.decoder_calls = 0

    def project(self, payload: bytes) -> _Record:
        if len(payload) > 64 * 1024:
            raise ValidationError("record_limit")
        text = payload.decode("utf-8")
        values: dict[str, Any] = {}
        index = self._skip_ws(text, 0)
        if index >= len(text) or text[index] != "{":
            raise ValidationError("schema_inconsistent")
        index += 1
        while True:
            index = self._skip_ws(text, index)
            if index >= len(text):
                raise ValidationError("schema_inconsistent")
            if text[index] == "}":
                index += 1
                break
            key, index = self._decode(text, index)
            if not isinstance(key, str):
                raise ValidationError("schema_inconsistent")
            index = self._skip_ws(text, index)
            if index >= len(text) or text[index] != ":":
                raise ValidationError("schema_inconsistent")
            index = self._skip_ws(text, index + 1)
            if key in self.REGISTERED:
                value, index = self._decode(text, index)
                self.decoder_calls += 1
                values[key] = value
            else:
                index = self._skip_value(text, index)
            index = self._skip_ws(text, index)
            if index >= len(text):
                raise ValidationError("schema_inconsistent")
            if text[index] == ",":
                index += 1
                continue
            if text[index] == "}":
                index += 1
                break
            raise ValidationError("schema_inconsistent")
        if self._skip_ws(text, index) != len(text):
            raise ValidationError("schema_inconsistent")
        required = ("requestId", "messageId", "model", "sourceTime", "amounts")
        if any(not isinstance(values.get(key), str) for key in required[:-1]):
            raise ValidationError("missing_identity" if not isinstance(values.get("requestId"), str) else "projected_type")
        amounts = values.get("amounts")
        if not isinstance(amounts, dict):
            raise ValidationError("projected_type")
        if set(amounts) != self.AMOUNT_KEYS or any(not isinstance(value, str) for value in amounts.values()):
            raise ValidationError("projected_type")
        try:
            parsed_amounts = {key: self._amount(value) for key, value in amounts.items()}
        except (TypeError, ValueError):
            raise ValidationError("projected_type") from None
        fingerprint_doc = {
            "amounts": parsed_amounts,
            "message_id": values["messageId"],
            "model": values["model"],
            "request_id": values["requestId"],
            "source_time": values["sourceTime"],
        }
        fingerprint = hashlib.sha256(
            json.dumps(fingerprint_doc, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()
        return _Record(
            request_id=values["requestId"],
            message_id=values["messageId"],
            model=values["model"],
            source_time=values["sourceTime"],
            cwd=values.get("cwd") if isinstance(values.get("cwd"), str) else None,
            project=values.get("project") if isinstance(values.get("project"), str) else None,
            amounts=parsed_amounts,
            fingerprint=fingerprint,
        )

    @staticmethod
    def _amount(value: str) -> int:
        if not value.isdigit() or (len(value) > 1 and value.startswith("0")):
            raise ValueError(value)
        result = int(value)
        if result < 0 or result > 9_223_372_036_854_775_807:
            raise ValueError(value)
        return result

    def _decode(self, text: str, index: int) -> tuple[Any, int]:
        try:
            return json.JSONDecoder().raw_decode(text, index)
        except (ValueError, UnicodeDecodeError):
            raise ValidationError("schema_inconsistent") from None

    @staticmethod
    def _skip_ws(text: str, index: int) -> int:
        while index < len(text) and text[index] in " \t\r\n":
            index += 1
        return index

    def _skip_value(self, text: str, index: int) -> int:
        if index >= len(text):
            raise ValidationError("schema_inconsistent")
        char = text[index]
        if char == '"':
            return self._skip_string(text, index)
        if char == "{":
            index = self._skip_ws(text, index + 1)
            if index < len(text) and text[index] == "}":
                return index + 1
            while True:
                if index >= len(text) or text[index] != '"':
                    raise ValidationError("schema_inconsistent")
                index = self._skip_string(text, index)
                index = self._skip_ws(text, index)
                if index >= len(text) or text[index] != ":":
                    raise ValidationError("schema_inconsistent")
                index = self._skip_value(text, self._skip_ws(text, index + 1))
                index = self._skip_ws(text, index)
                if index < len(text) and text[index] == "}":
                    return index + 1
                if index >= len(text) or text[index] != ",":
                    raise ValidationError("schema_inconsistent")
                index = self._skip_ws(text, index + 1)
        if char == "[":
            index = self._skip_ws(text, index + 1)
            if index < len(text) and text[index] == "]":
                return index + 1
            while True:
                index = self._skip_value(text, index)
                index = self._skip_ws(text, index)
                if index < len(text) and text[index] == "]":
                    return index + 1
                if index >= len(text) or text[index] != ",":
                    raise ValidationError("schema_inconsistent")
                index = self._skip_ws(text, index + 1)
        end = index
        while end < len(text) and text[end] not in ",}]":
            end += 1
        if end == index:
            raise ValidationError("schema_inconsistent")
        token = text[index:end]
        if token not in {"true", "false", "null"} and not re.fullmatch(r"-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?", token):
            raise ValidationError("schema_inconsistent")
        return end

    def _skip_string(self, text: str, index: int) -> int:
        index += 1
        escaped = False
        while index < len(text):
            current = text[index]
            if escaped:
                if current not in '"\\/bfnrtu':
                    raise ValidationError("schema_inconsistent")
                escaped = False
            elif current == "\\":
                escaped = True
            elif current == '"':
                return index + 1
            index += 1
        raise ValidationError("schema_inconsistent")


class ThesisHarness:
    """Disposable single-record, single-writer thesis harness."""

    WRITE_BOUNDARIES = ("event", "amount", "request", "sequence", "aggregate", "obligation", "cursor")
    CAPTURE_LANES = (
        "application_value", "parser_instrumentation", "log", "exception", "crash",
        "sqlite", "sink", "image", "environment", "network",
    )
    ORACLE_ANSWERS = {
        "tool": "synthetic-claude",
        "source_time": "2026-01-02T03:04:05Z",
        "model": "claude-synthetic-v1",
        "project": "synthetic-project",
        "categories": "cache_read_tokens,cache_write_tokens,input_tokens,output_tokens",
        "amounts": "11,7,3,2",
        "logical_request": "1",
        "replay_counts": "unchanged",
        "health": "healthy",
    }

    def __init__(self, config: HarnessConfig):
        self.config = config
        self._preflight_done = False
        self._stats = ProjectionStats()
        self._stream_state = "healthy"
        self._initialize()

    def _initialize(self) -> None:
        self._preflight()
        self._preflight_done = True
        self.config.database_path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.config.database_path)
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS ledger_events (
                request_id TEXT PRIMARY KEY, message_id TEXT NOT NULL, model TEXT NOT NULL,
                source_time TEXT NOT NULL, cwd TEXT, project TEXT, accounting_fingerprint TEXT NOT NULL,
                ledger_seq INTEGER NOT NULL UNIQUE
            );
            CREATE TABLE IF NOT EXISTS ledger_amounts (
                request_id TEXT NOT NULL REFERENCES ledger_events(request_id), category TEXT NOT NULL,
                amount INTEGER NOT NULL, PRIMARY KEY(request_id, category)
            );
            CREATE TABLE IF NOT EXISTS ledger_requests (request_id TEXT PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS ledger_sequences (ledger_seq INTEGER PRIMARY KEY);
            CREATE TABLE IF NOT EXISTS ledger_aggregates (category TEXT PRIMARY KEY, total INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS ledger_obligations (ledger_seq INTEGER PRIMARY KEY, obligation TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS ledger_cursors (stream TEXT PRIMARY KEY, position INTEGER NOT NULL);
            CREATE VIEW IF NOT EXISTS usage_events AS SELECT request_id, message_id, model, source_time, cwd, project, ledger_seq FROM ledger_events;
            CREATE VIEW IF NOT EXISTS usage_event_amounts AS SELECT request_id, category, amount FROM ledger_amounts;
            CREATE VIEW IF NOT EXISTS logical_requests AS SELECT request_id FROM ledger_requests;
            CREATE VIEW IF NOT EXISTS source_health AS SELECT 'synthetic' AS stream, 'healthy' AS state;
            CREATE VIEW IF NOT EXISTS sink_health AS SELECT 'synthetic' AS sink, 'disabled' AS state;
            CREATE VIEW IF NOT EXISTS ledger_health AS SELECT 'healthy' AS state, count(*) AS accepted_events FROM ledger_events;
            """
        )

    def _preflight(self) -> None:
        forbidden = (
            not self.config.synthetic,
            self.config.network,
            self.config.sink,
            self.config.production_package,
            self.config.publish_target,
            self.config.personal_path,
            self.config.credential_reader,
            self.config.concurrent,
        )
        if any(forbidden):
            raise ValidationError("forbidden_configuration")
        if self.config.fixed_clock != "2026-01-02T03:04:05Z":
            raise ValidationError("fixed_clock_mismatch")
        fixture = self.config.fixture_path.resolve(strict=False)
        manifest = self.config.manifest_path.resolve(strict=False)
        if not fixture.is_relative_to(FIXTURE_ROOT.absolute()) or not manifest.is_relative_to(FIXTURE_ROOT.absolute()):
            raise ValidationError("forbidden_configuration")

    def _manifest(self) -> dict[str, dict[str, Any]]:
        with self.config.manifest_path.open(encoding="utf-8") as handle:
            payload = json.load(handle)
        if payload.get("version") != "synthetic-thesis@1" or payload.get("synthetic") is not True:
            raise ValidationError("manifest_invalid")
        return payload["fixtures"]

    def _read_record(self, fixture_path: Path) -> tuple[_Record, ProjectionStats]:
        entries = self._manifest()
        entry = entries.get(fixture_path.name)
        if entry is None:
            raise ValidationError("unregistered_fixture")
        payload = fixture_path.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()
        if digest != entry["sha256"]:
            raise ValidationError("digest_mismatch")
        lines = payload.splitlines()
        if len(lines) != 1:
            raise ValidationError("schema_inconsistent")
        projector = _Projector()
        record = projector.project(lines[0])
        return record, ProjectionStats(forbidden_decoder_calls=0, forbidden_materializer_calls=0, forbidden_fingerprint_calls=0)

    def run_once(self, *, fail_at: str | None = None) -> RunResult:
        return self.run_fixture(self.config.fixture_path, fail_at=fail_at)

    def run_fixture(self, fixture_path: Path, *, fail_at: str | None = None) -> RunResult:
        if not self._preflight_done:
            self._preflight()
        record, stats = self._read_record(fixture_path)
        self._stats = stats
        try:
            with self.connection:
                existing = self.connection.execute(
                    "SELECT accounting_fingerprint FROM ledger_events WHERE request_id = ?", (record.request_id,)
                ).fetchone()
                if existing:
                    if existing[0] != record.fingerprint:
                        self._stream_state = "identity_collision"
                        return RunResult("identity_collision")
                    self.connection.execute("INSERT OR REPLACE INTO ledger_cursors(stream, position) VALUES ('synthetic', 1)")
                    return RunResult("accepted")
                self._write(fail_at, "event", "INSERT INTO ledger_events VALUES (?,?,?,?,?,?,?,?)", (
                    record.request_id, record.message_id, record.model, record.source_time, record.cwd,
                    record.project, record.fingerprint, 1,
                ))
                for category, amount in record.amounts.items():
                    self._write(fail_at, "amount", "INSERT INTO ledger_amounts VALUES (?,?,?)", (record.request_id, category, amount))
                self._write(fail_at, "request", "INSERT INTO ledger_requests VALUES (?)", (record.request_id,))
                self._write(fail_at, "sequence", "INSERT INTO ledger_sequences VALUES (?)", (1,))
                for category, amount in record.amounts.items():
                    self.connection.execute(
                        "INSERT INTO ledger_aggregates(category,total) VALUES (?,?) ON CONFLICT(category) DO UPDATE SET total=total+excluded.total",
                        (category, amount),
                    )
                if fail_at == "aggregate":
                    raise sqlite3.IntegrityError("injected failure at aggregate")
                self._write(fail_at, "obligation", "INSERT INTO ledger_obligations VALUES (?,?)", (1, "synthetic"))
                self._write(fail_at, "cursor", "INSERT INTO ledger_cursors VALUES (?,?)", ("synthetic", 1))
        except sqlite3.IntegrityError:
            raise
        return RunResult("accepted")

    def _write(self, fail_at: str | None, boundary: str, query: str, parameters: tuple[Any, ...]) -> None:
        if fail_at == boundary:
            raise sqlite3.IntegrityError(f"injected failure at {boundary}")
        self.connection.execute(query, parameters)

    def snapshot(self) -> dict[str, int]:
        queries = {
            "usage_events": "SELECT count(*) FROM usage_events",
            "usage_event_amounts": "SELECT count(*) FROM usage_event_amounts",
            "logical_requests": "SELECT count(*) FROM logical_requests",
            "ledger_sequences": "SELECT count(*) FROM ledger_sequences",
            "aggregates": "SELECT count(*) FROM ledger_aggregates",
            "obligations": "SELECT count(*) FROM ledger_obligations",
            "cursor": "SELECT count(*) FROM ledger_cursors",
        }
        return {name: int(self.connection.execute(query).fetchone()[0]) for name, query in queries.items()}

    def health(self) -> dict[str, str]:
        return {"stream_state": self._stream_state}

    def run_privacy(self, *, mutation: str | None = None) -> RunResult:
        result = self.run_once()
        if mutation is not None:
            raise CaptureViolation(mutation)
        return RunResult(
            result.status,
            forbidden_decoder_calls=self._stats.forbidden_decoder_calls,
            forbidden_materializer_calls=self._stats.forbidden_materializer_calls,
            forbidden_fingerprint_calls=self._stats.forbidden_fingerprint_calls,
            public_capture=self.snapshot(),
            capture_canaries=tuple(self.CAPTURE_LANES),
        )

    def exercise(self, *, elapsed_seconds: int, read_commands: int, answers: dict[str, str], private_table_reads: int) -> ExerciseEvidence:
        self.run_once()
        passed = (
            elapsed_seconds <= 600
            and read_commands <= 6
            and private_table_reads == 0
            and answers == self.ORACLE_ANSWERS
        )
        return ExerciseEvidence(passed, elapsed_seconds, read_commands, answers, private_table_reads)
