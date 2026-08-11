"""The disposable one-record Synthetic-to-SQLite thesis.

The parser projects registered scalars only.  Unknown values are skipped by a
structural scanner and are never handed to a JSON decoder, application object,
or fingerprint function.
"""

from __future__ import annotations

import hashlib
import json
import mmap
import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .authorization import ValidationError, validate_synthetic_authorization


FIXTURE_ROOT = Path(__file__).parents[1] / "tests" / "fixtures" / "synthetic-thesis"
_FORBIDDEN_MARKER = object()
_FORBIDDEN_SENTINEL = b"THESIS_FORBIDDEN_CONTENT_SENTINEL"
_FORBIDDEN_DIGEST = hashlib.sha256(_FORBIDDEN_SENTINEL).hexdigest()


class CaptureViolation(RuntimeError):
    """A guarded thesis boundary observed a forbidden test mutation."""

    def __init__(self, lane: str, stats: ProjectionStats):
        self.lane = lane
        self.stats = stats
        super().__init__(f"{lane}: forbidden capture")


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
class FramingEvidence:
    """Evidence that the parser receives a view, not a copied JSONL line."""

    line_is_memoryview: bool
    shares_source_buffer: bool
    source_is_mmap: bool


@dataclass(frozen=True)
class RunResult:
    status: str
    rejection_code: str | None = None
    forbidden_decoder_calls: int = 0
    forbidden_materializer_calls: int = 0
    forbidden_fingerprint_calls: int = 0
    public_capture: dict[str, Any] | None = None
    capture_canaries: dict[str, str] | None = None
    capture_observations: dict[str, tuple[str, ...]] | None = None
    framing: FramingEvidence | None = None


@dataclass(frozen=True)
class ExerciseEvidence:
    passed: bool
    elapsed_seconds: int
    read_commands: tuple[str, ...]
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


class _FramedValidationError(ValidationError):
    """A content-free parser failure paired with safe framing evidence."""

    def __init__(self, code: str, framing: FramingEvidence):
        super().__init__(code)
        self.framing = framing


class _CaptureAudit:
    """Observe real capture-boundary inputs without retaining their values."""

    def __init__(self, lanes: tuple[str, ...]):
        self._canaries = {
            lane: f"capture-canary-{position}-{lane}"
            for position, lane in enumerate(lanes, start=1)
        }
        self._observations: dict[str, list[str]] = {lane: [] for lane in lanes}
        self._forbidden_decoder_calls = 0
        self._forbidden_materializer_calls = 0
        self._forbidden_fingerprint_calls = 0

    @property
    def canaries(self) -> dict[str, str]:
        return dict(self._canaries)

    @property
    def observations(self) -> dict[str, tuple[str, ...]]:
        return {
            lane: tuple(observations)
            for lane, observations in self._observations.items()
        }

    @property
    def stats(self) -> ProjectionStats:
        return ProjectionStats(
            forbidden_decoder_calls=self._forbidden_decoder_calls,
            forbidden_materializer_calls=self._forbidden_materializer_calls,
            forbidden_fingerprint_calls=self._forbidden_fingerprint_calls,
        )

    def canary(self, lane: str) -> str:
        return self._canaries[lane]

    def observe(self, lane: str, value: object, *, kind: str | None = None) -> None:
        """Record a canary only when that exact value reaches its real boundary."""

        if self._contains_forbidden(value):
            if kind == "decoder":
                self._forbidden_decoder_calls += 1
            elif kind == "materializer":
                self._forbidden_materializer_calls += 1
            elif kind == "fingerprint":
                self._forbidden_fingerprint_calls += 1
            raise CaptureViolation(lane, self.stats)
        if value == self._canaries[lane]:
            self._observations[lane].append(self._canaries[lane])

    @classmethod
    def _contains_forbidden(cls, value: object) -> bool:
        if value is _FORBIDDEN_MARKER:
            return True
        if isinstance(value, str):
            return (
                _FORBIDDEN_SENTINEL.decode("ascii") in value
                or _FORBIDDEN_DIGEST in value
            )
        if isinstance(value, bytes):
            return (
                _FORBIDDEN_SENTINEL in value
                or _FORBIDDEN_DIGEST.encode("ascii") in value
            )
        if isinstance(value, _Record):
            return any(
                cls._contains_forbidden(item)
                for item in (
                    value.request_id,
                    value.message_id,
                    value.model,
                    value.source_time,
                    value.cwd,
                    value.project,
                    value.amounts,
                    value.fingerprint,
                )
            )
        if isinstance(value, dict):
            return any(
                cls._contains_forbidden(item) for pair in value.items() for item in pair
            )
        if isinstance(value, (list, tuple)):
            return any(cls._contains_forbidden(item) for item in value)
        return False


class _CaptureBoundaries:
    """Concrete no-egress capture boundaries used by the disposable thesis."""

    def __init__(self, audit: _CaptureAudit):
        self._audit = audit

    @property
    def stats(self) -> ProjectionStats:
        return self._audit.stats

    def application_value(self, value: object, *, kind: str | None = None) -> None:
        self._audit.observe("application_value", value, kind=kind)

    def parser_instrumentation(self, value: object) -> None:
        self._audit.observe("parser_instrumentation", value, kind="decoder")

    def log(self, value: object) -> None:
        self._audit.observe("log", value)

    def exception(self, value: object) -> None:
        self._audit.observe("exception", value)

    def crash(self, value: object) -> None:
        self._audit.observe("crash", value)

    def sqlite(self, value: object) -> None:
        self._audit.observe("sqlite", value)

    def sink(self, value: object) -> None:
        self._audit.observe("sink", value)

    def image(self, value: object) -> None:
        self._audit.observe("image", value)

    def environment(self, value: object) -> None:
        self._audit.observe("environment", value)

    def network(self, value: object) -> None:
        self._audit.observe("network", value)

    def exercise_positive_controls(self, sqlite_probe: Any) -> None:
        """Send each harmless canary through its actual guarded boundary."""

        self.application_value(self._audit.canary("application_value"))
        self.parser_instrumentation(self._audit.canary("parser_instrumentation"))
        self.log(self._audit.canary("log"))
        self.exception(self._audit.canary("exception"))
        self.crash(self._audit.canary("crash"))
        sqlite_probe(self._audit.canary("sqlite"))
        self.sink(self._audit.canary("sink"))
        self.image(self._audit.canary("image"))
        self.environment(self._audit.canary("environment"))
        self.network(self._audit.canary("network"))


class _Projector:
    """Project registered scalars after a bounded, byte-only structural scan."""

    REGISTERED_BY_TOKEN = {
        b'"requestId"': "requestId",
        b'"messageId"': "messageId",
        b'"model"': "model",
        b'"sourceTime"': "sourceTime",
        b'"cwd"': "cwd",
        b'"project"': "project",
        b'"amounts"': "amounts",
    }
    AMOUNT_BY_TOKEN = {
        b'"input_tokens"': "input_tokens",
        b'"output_tokens"': "output_tokens",
        b'"cache_read_tokens"': "cache_read_tokens",
        b'"cache_write_tokens"': "cache_write_tokens",
    }
    AMOUNT_KEYS = frozenset(AMOUNT_BY_TOKEN.values())
    MAX_RECORD_BYTES = 64 * 1024
    MAX_CONTAINER_DEPTH = 32
    NUMBER = re.compile(rb"-?(0|[1-9][0-9]*)(\.[0-9]+)?([eE][+-]?[0-9]+)?")

    def __init__(
        self,
        boundaries: _CaptureBoundaries | None = None,
        *,
        mutation: str | None = None,
    ) -> None:
        self._boundaries = boundaries
        self._mutation = mutation

    def project(self, payload: memoryview) -> _Record:
        if len(payload) > self.MAX_RECORD_BYTES:
            raise ValidationError("record_limit")
        index = self._skip_ws(payload, 0)
        if index >= len(payload) or payload[index] != ord("{"):
            raise ValidationError("schema_inconsistent")
        locations, index = self._scan_object_members(payload, index + 1)
        if self._skip_ws(payload, index) != len(payload):
            raise ValidationError("schema_inconsistent")

        values: dict[str, Any] = {}
        for field in (
            "requestId",
            "messageId",
            "model",
            "sourceTime",
            "cwd",
            "project",
        ):
            if field in locations:
                values[field], _ = self._decode_registered_string(
                    payload, locations[field]
                )
        amounts_invalid = False
        if "amounts" in locations:
            amounts, amounts_invalid = self._project_amounts(
                payload, locations["amounts"]
            )
            values["amounts"] = amounts

        required = ("requestId", "messageId", "model", "sourceTime", "amounts")
        if any(not isinstance(values.get(field), str) for field in required[:-1]):
            raise ValidationError(
                "missing_identity"
                if not isinstance(values.get("requestId"), str)
                else "projected_type"
            )
        amounts = values.get("amounts")
        if amounts_invalid or not isinstance(amounts, dict):
            raise ValidationError("projected_type")
        if set(amounts) != self.AMOUNT_KEYS or any(
            not isinstance(value, str) for value in amounts.values()
        ):
            raise ValidationError("projected_type")
        try:
            parsed_amounts = {
                key: self._amount(value) for key, value in amounts.items()
            }
        except (TypeError, ValueError):
            raise ValidationError("projected_type") from None

        fingerprint_doc = {
            "amounts": parsed_amounts,
            "message_id": values["messageId"],
            "model": values["model"],
            "request_id": values["requestId"],
            "source_time": values["sourceTime"],
        }
        if self._boundaries is not None:
            self._boundaries.application_value(
                _FORBIDDEN_MARKER
                if self._mutation == "fingerprint"
                else fingerprint_doc,
                kind="fingerprint",
            )
        fingerprint = hashlib.sha256(
            json.dumps(fingerprint_doc, sort_keys=True, separators=(",", ":")).encode(
                "utf-8"
            )
        ).hexdigest()
        record = _Record(
            request_id=values["requestId"],
            message_id=values["messageId"],
            model=values["model"],
            source_time=values["sourceTime"],
            cwd=values.get("cwd") if isinstance(values.get("cwd"), str) else None,
            project=values.get("project")
            if isinstance(values.get("project"), str)
            else None,
            amounts=parsed_amounts,
            fingerprint=fingerprint,
        )
        if self._boundaries is not None:
            self._boundaries.application_value(
                _FORBIDDEN_MARKER
                if self._mutation in {"leak", "materializer"}
                else record,
                kind="materializer" if self._mutation == "materializer" else None,
            )
        return record

    def _scan_object_members(
        self, payload: memoryview, index: int
    ) -> tuple[dict[str, int], int]:
        locations: dict[str, int] = {}
        index = self._skip_ws(payload, index)
        if index < len(payload) and payload[index] == ord("}"):
            return locations, index + 1
        while True:
            if index >= len(payload) or payload[index] != ord('"'):
                raise ValidationError("schema_inconsistent")
            key_start = index
            key_end = self._skip_string(payload, index)
            key = self._registered_key(payload, key_start, key_end)
            index = self._skip_ws(payload, key_end)
            if index >= len(payload) or payload[index] != ord(":"):
                raise ValidationError("schema_inconsistent")
            index = self._skip_ws(payload, index + 1)
            if key is not None:
                if key in locations:
                    raise ValidationError("duplicate_registered_key")
                locations[key] = index
            index = self._skip_value(payload, index)
            index = self._skip_ws(payload, index)
            if index >= len(payload):
                raise ValidationError("schema_inconsistent")
            if payload[index] == ord("}"):
                return locations, index + 1
            if payload[index] != ord(","):
                raise ValidationError("schema_inconsistent")
            index = self._skip_ws(payload, index + 1)

    def _project_amounts(
        self, payload: memoryview, index: int
    ) -> tuple[dict[str, Any] | None, bool]:
        if index >= len(payload):
            raise ValidationError("schema_inconsistent")
        if payload[index] != ord("{"):
            self._skip_value(payload, index)
            return None, True
        locations: dict[str, int] = {}
        invalid = False
        index = self._skip_ws(payload, index + 1)
        if index < len(payload) and payload[index] == ord("}"):
            return {}, invalid
        while True:
            if index >= len(payload) or payload[index] != ord('"'):
                raise ValidationError("schema_inconsistent")
            key_start = index
            key_end = self._skip_string(payload, index)
            key = self._amount_key(payload, key_start, key_end)
            index = self._skip_ws(payload, key_end)
            if index >= len(payload) or payload[index] != ord(":"):
                raise ValidationError("schema_inconsistent")
            index = self._skip_ws(payload, index + 1)
            if key is None:
                invalid = True
            elif key in locations:
                raise ValidationError("duplicate_registered_key")
            else:
                locations[key] = index
            index = self._skip_value(payload, index)
            index = self._skip_ws(payload, index)
            if index >= len(payload):
                raise ValidationError("schema_inconsistent")
            if payload[index] == ord("}"):
                break
            if payload[index] != ord(","):
                raise ValidationError("schema_inconsistent")
            index = self._skip_ws(payload, index + 1)
        if invalid:
            return None, True
        return {
            key: self._decode_registered_string(payload, value_index)[0]
            for key, value_index in locations.items()
        }, False

    @classmethod
    def _registered_key(cls, payload: memoryview, start: int, end: int) -> str | None:
        return cls._matched_key(payload, start, end, cls.REGISTERED_BY_TOKEN)

    @classmethod
    def _amount_key(cls, payload: memoryview, start: int, end: int) -> str | None:
        return cls._matched_key(payload, start, end, cls.AMOUNT_BY_TOKEN)

    @staticmethod
    def _matched_key(
        payload: memoryview, start: int, end: int, registry: dict[bytes, str]
    ) -> str | None:
        for token, name in registry.items():
            if _Projector._matches(payload, start, end, token):
                return name
        return None

    @staticmethod
    def _matches(payload: memoryview, start: int, end: int, token: bytes) -> bool:
        return end - start == len(token) and all(
            payload[start + offset] == expected for offset, expected in enumerate(token)
        )

    @staticmethod
    def _amount(value: str) -> int:
        if not value.isdigit() or (len(value) > 1 and value.startswith("0")):
            raise ValueError(value)
        result = int(value)
        if result < 0 or result > 9_223_372_036_854_775_807:
            raise ValueError(value)
        return result

    def _decode_registered_string(
        self, payload: memoryview, index: int
    ) -> tuple[str | None, int]:
        if index >= len(payload):
            raise ValidationError("schema_inconsistent")
        if payload[index] != ord('"'):
            return None, self._skip_value(payload, index)
        end = self._skip_string(payload, index)
        try:
            value = json.loads(bytes(payload[index:end]).decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            raise ValidationError("schema_inconsistent") from None
        if self._boundaries is not None:
            self._boundaries.parser_instrumentation(
                _FORBIDDEN_MARKER if self._mutation == "decoder" else value
            )
        return value if isinstance(value, str) else None, end

    @staticmethod
    def _skip_ws(payload: memoryview, index: int) -> int:
        while index < len(payload) and payload[index] in b" \t\r\n":
            index += 1
        return index

    def _skip_value(self, payload: memoryview, index: int) -> int:
        """Walk unknown JSON structurally with an explicit bounded stack."""

        index = self._skip_ws(payload, index)
        stack: list[int] = []
        state = "value"
        while True:
            if state == "value":
                if index >= len(payload):
                    raise ValidationError("schema_inconsistent")
                char = payload[index]
                if char == ord('"'):
                    index = self._skip_string(payload, index)
                    state = "after_value"
                    continue
                if char in (ord("{"), ord("[")):
                    if len(stack) >= self.MAX_CONTAINER_DEPTH:
                        raise ValidationError("record_limit")
                    stack.append(char)
                    index = self._skip_ws(payload, index + 1)
                    closer = ord("}") if char == ord("{") else ord("]")
                    if index < len(payload) and payload[index] == closer:
                        stack.pop()
                        index += 1
                        state = "after_value"
                    else:
                        state = "object_key" if char == ord("{") else "value"
                    continue
                end = index
                while end < len(payload) and payload[end] not in b",}] \t\r\n":
                    end += 1
                if end == index:
                    raise ValidationError("schema_inconsistent")
                if (
                    not any(
                        self._matches(payload, index, end, token)
                        for token in (b"true", b"false", b"null")
                    )
                    and self.NUMBER.fullmatch(payload[index:end]) is None
                ):
                    raise ValidationError("schema_inconsistent")
                index = end
                state = "after_value"
                continue

            if state == "object_key":
                if index >= len(payload) or payload[index] != ord('"'):
                    raise ValidationError("schema_inconsistent")
                index = self._skip_ws(payload, self._skip_string(payload, index))
                if index >= len(payload) or payload[index] != ord(":"):
                    raise ValidationError("schema_inconsistent")
                index = self._skip_ws(payload, index + 1)
                state = "value"
                continue

            if not stack:
                return index
            index = self._skip_ws(payload, index)
            container = stack[-1]
            closer = ord("}") if container == ord("{") else ord("]")
            if index < len(payload) and payload[index] == closer:
                stack.pop()
                index += 1
                state = "after_value"
                continue
            if index >= len(payload) or payload[index] != ord(","):
                raise ValidationError("schema_inconsistent")
            index = self._skip_ws(payload, index + 1)
            state = "object_key" if container == ord("{") else "value"

    @staticmethod
    def _skip_string(payload: memoryview, index: int) -> int:
        if index >= len(payload) or payload[index] != ord('"'):
            raise ValidationError("schema_inconsistent")
        index += 1
        escaped = False
        while index < len(payload):
            current = payload[index]
            if escaped:
                if current == ord("u"):
                    if index + 4 >= len(payload) or any(
                        digit not in b"0123456789abcdefABCDEF"
                        for digit in payload[index + 1 : index + 5]
                    ):
                        raise ValidationError("schema_inconsistent")
                    index += 5
                    escaped = False
                    continue
                if current not in b'"\\/bfnrt':
                    raise ValidationError("schema_inconsistent")
                escaped = False
            elif current == ord("\\"):
                escaped = True
            elif current == ord('"'):
                return index + 1
            elif current < 0x20:
                raise ValidationError("schema_inconsistent")
            index += 1
        raise ValidationError("schema_inconsistent")


class ThesisHarness:
    """Disposable single-record, single-writer thesis harness."""

    WRITE_BOUNDARIES = (
        "event",
        "amount",
        "request",
        "sequence",
        "aggregate",
        "obligation",
        "cursor",
    )
    MANIFEST_REQUIRED_FIELDS = (
        "requestId",
        "messageId",
        "model",
        "sourceTime",
        "amounts",
    )
    MANIFEST_ALLOWED_AMOUNTS = (
        "input_tokens",
        "output_tokens",
        "cache_read_tokens",
        "cache_write_tokens",
    )
    CAPTURE_LANES = (
        "application_value",
        "parser_instrumentation",
        "log",
        "exception",
        "crash",
        "sqlite",
        "sink",
        "image",
        "environment",
        "network",
    )
    DOCUMENTED_READ_COMMANDS = (
        "usage_events",
        "usage_event_amounts",
        "logical_requests",
        "synthetic_aggregates",
        "ledger_health",
        "health",
    )
    PRIVATE_BASE_TABLES = frozenset(
        {
            "ledger_events",
            "ledger_amounts",
            "ledger_requests",
            "ledger_sequences",
            "ledger_aggregates",
            "ledger_obligations",
            "ledger_cursors",
            "ledger_stream_state",
        }
    )

    def __init__(self, config: HarnessConfig):
        self.config = config
        validate_synthetic_authorization()
        self._preflight_done = False
        self._stats = ProjectionStats()
        self._initial_record: _Record | None = None
        self._initialize()

    def _initialize(self) -> None:
        self._preflight()
        self._initial_record, self._stats, _ = self._read_record(
            self.config.fixture_path
        )
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
            CREATE TABLE IF NOT EXISTS ledger_stream_state (stream TEXT PRIMARY KEY, state TEXT NOT NULL);
            CREATE VIEW IF NOT EXISTS usage_events AS
                SELECT 'synthetic-claude' AS tool, request_id, message_id, model, source_time, cwd, project, ledger_seq
                FROM ledger_events;
            CREATE VIEW IF NOT EXISTS usage_event_amounts AS SELECT request_id, category, amount FROM ledger_amounts;
            CREATE VIEW IF NOT EXISTS logical_requests AS SELECT request_id FROM ledger_requests;
            CREATE VIEW IF NOT EXISTS synthetic_sequences AS SELECT ledger_seq FROM ledger_sequences;
            CREATE VIEW IF NOT EXISTS synthetic_aggregates AS SELECT category, total FROM ledger_aggregates;
            CREATE VIEW IF NOT EXISTS synthetic_obligations AS SELECT ledger_seq, obligation FROM ledger_obligations;
            CREATE VIEW IF NOT EXISTS synthetic_cursors AS SELECT stream, position FROM ledger_cursors;
            CREATE VIEW IF NOT EXISTS source_health AS
                SELECT 'synthetic' AS stream,
                    COALESCE((SELECT state FROM ledger_stream_state WHERE stream = 'synthetic'), 'healthy') AS state;
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
        if not fixture.is_relative_to(
            FIXTURE_ROOT.absolute()
        ) or not manifest.is_relative_to(FIXTURE_ROOT.absolute()):
            raise ValidationError("forbidden_configuration")

    def _manifest(self) -> dict[str, Any]:
        expected_manifest = (FIXTURE_ROOT / "manifest.json").resolve()
        if self.config.manifest_path.resolve(strict=False) != expected_manifest:
            raise ValidationError("manifest_invalid")
        try:
            with self.config.manifest_path.open(encoding="utf-8") as handle:
                payload = json.load(handle)
        except (OSError, json.JSONDecodeError):
            raise ValidationError("manifest_invalid") from None
        fixtures = payload.get("fixtures") if isinstance(payload, dict) else None
        capture_canaries = (
            payload.get("capture_canaries") if isinstance(payload, dict) else None
        )
        if (
            not isinstance(payload, dict)
            or payload.get("version") != "synthetic-thesis@1"
            or payload.get("synthetic") is not True
            or not isinstance(fixtures, dict)
            or payload.get("required_fields") != list(self.MANIFEST_REQUIRED_FIELDS)
            or payload.get("allowed_amounts") != list(self.MANIFEST_ALLOWED_AMOUNTS)
            or payload.get("max_record_bytes") != _Projector.MAX_RECORD_BYTES
            or payload.get("max_container_depth") != _Projector.MAX_CONTAINER_DEPTH
            or not isinstance(capture_canaries, list)
            or tuple(capture_canaries) != self.CAPTURE_LANES
            or len(set(capture_canaries)) != len(capture_canaries)
        ):
            raise ValidationError("manifest_invalid")
        return payload

    def _read_record(
        self,
        fixture_path: Path,
        boundaries: _CaptureBoundaries | None = None,
        *,
        line_number: int = 1,
        mutation: str | None = None,
    ) -> tuple[_Record, ProjectionStats, FramingEvidence]:
        if not fixture_path.resolve(strict=False).is_relative_to(
            FIXTURE_ROOT.resolve()
        ):
            raise ValidationError("forbidden_configuration")
        manifest = self._manifest()
        entries = manifest["fixtures"]
        entry = entries.get(fixture_path.name)
        if not isinstance(entry, dict) or not isinstance(entry.get("sha256"), str):
            raise ValidationError("unregistered_fixture")
        try:
            source_file = fixture_path.open("rb")
        except OSError:
            raise ValidationError("unregistered_fixture") from None
        try:
            mapped = mmap.mmap(source_file.fileno(), 0, access=mmap.ACCESS_READ)
        except (OSError, ValueError):
            source_file.close()
            raise ValidationError("unregistered_fixture") from None
        source = memoryview(mapped)
        line: memoryview | None = None
        try:
            digest = hashlib.sha256(source).hexdigest()
            if digest != entry["sha256"]:
                raise ValidationError("digest_mismatch")
            line, framing = self._single_line_view(source, line_number)
            projector = _Projector(boundaries, mutation=mutation)
            try:
                record = projector.project(line)
            except ValidationError as error:
                raise _FramedValidationError(error.code, framing) from None
            return (
                record,
                boundaries.stats if boundaries is not None else ProjectionStats(),
                framing,
            )
        finally:
            if line is not None:
                line.release()
            source.release()
            mapped.close()
            source_file.close()

    @staticmethod
    def _single_line_view(
        payload: memoryview, line_number: int
    ) -> tuple[memoryview, FramingEvidence]:
        """Return one JSONL record as a source-buffer view without a line copy."""

        if line_number != 1:
            raise ValidationError("schema_inconsistent")
        newline = next(
            (index for index, byte in enumerate(payload) if byte == ord("\n")), -1
        )
        if newline == -1:
            end = len(payload)
        else:
            if newline != len(payload) - 1:
                raise ValidationError("schema_inconsistent")
            end = (
                newline - 1
                if newline > 0 and payload[newline - 1] == ord("\r")
                else newline
            )
        line = memoryview(payload)[:end]
        return line, FramingEvidence(
            line_is_memoryview=isinstance(line, memoryview),
            shares_source_buffer=line.obj is payload.obj,
            source_is_mmap=isinstance(payload.obj, mmap.mmap),
        )

    def run_once(self, *, fail_at: str | None = None) -> RunResult:
        if self._initial_record is None:
            raise RuntimeError("qualified record missing after preflight")
        return self._run_record(self._initial_record, fail_at=fail_at)

    def run_fixture(
        self, fixture_path: Path, *, fail_at: str | None = None
    ) -> RunResult:
        return self.run_file(fixture_path, fail_at=fail_at)

    def run_line(
        self, fixture_path: Path, *, line_number: int, fail_at: str | None = None
    ) -> RunResult:
        if not self._preflight_done:
            self._preflight()
        record, stats, _ = self._read_record(fixture_path, line_number=line_number)
        self._stats = stats
        return self._run_record(record, fail_at=fail_at)

    def run_file(self, fixture_path: Path, *, fail_at: str | None = None) -> RunResult:
        return self.run_line(fixture_path, line_number=1, fail_at=fail_at)

    def rescan_file(self, fixture_path: Path) -> RunResult:
        return self.run_file(fixture_path)

    def _run_record(
        self,
        record: _Record,
        *,
        fail_at: str | None = None,
        capture_boundaries: _CaptureBoundaries | None = None,
    ) -> RunResult:
        try:
            with self.connection:
                existing = self._execute(
                    "SELECT accounting_fingerprint FROM ledger_events WHERE request_id = ?",
                    (record.request_id,),
                    capture_boundaries=capture_boundaries,
                ).fetchone()
                if existing:
                    if existing[0] != record.fingerprint:
                        self._execute(
                            "INSERT INTO ledger_stream_state(stream, state) VALUES ('synthetic', 'identity_collision') "
                            "ON CONFLICT(stream) DO UPDATE SET state = excluded.state",
                            capture_boundaries=capture_boundaries,
                        )
                        return RunResult("identity_collision")
                    self._execute(
                        "INSERT OR REPLACE INTO ledger_cursors(stream, position) VALUES ('synthetic', 1)",
                        capture_boundaries=capture_boundaries,
                    )
                    return RunResult("accepted")
                self._write(
                    fail_at,
                    "event",
                    "INSERT INTO ledger_events VALUES (?,?,?,?,?,?,?,?)",
                    (
                        record.request_id,
                        record.message_id,
                        record.model,
                        record.source_time,
                        record.cwd,
                        record.project,
                        record.fingerprint,
                        1,
                    ),
                    capture_boundaries=capture_boundaries,
                )
                for category, amount in record.amounts.items():
                    self._write(
                        fail_at,
                        "amount",
                        "INSERT INTO ledger_amounts VALUES (?,?,?)",
                        (record.request_id, category, amount),
                        capture_boundaries=capture_boundaries,
                    )
                self._write(
                    fail_at,
                    "request",
                    "INSERT INTO ledger_requests VALUES (?)",
                    (record.request_id,),
                    capture_boundaries=capture_boundaries,
                )
                self._write(
                    fail_at,
                    "sequence",
                    "INSERT INTO ledger_sequences VALUES (?)",
                    (1,),
                    capture_boundaries=capture_boundaries,
                )
                for category, amount in record.amounts.items():
                    self._execute(
                        "INSERT INTO ledger_aggregates(category,total) VALUES (?,?) ON CONFLICT(category) DO UPDATE SET total=total+excluded.total",
                        (category, amount),
                        capture_boundaries=capture_boundaries,
                    )
                if fail_at == "aggregate":
                    raise sqlite3.IntegrityError("injected failure at aggregate")
                self._write(
                    fail_at,
                    "obligation",
                    "INSERT INTO ledger_obligations VALUES (?,?)",
                    (1, "synthetic"),
                    capture_boundaries=capture_boundaries,
                )
                self._write(
                    fail_at,
                    "cursor",
                    "INSERT INTO ledger_cursors VALUES (?,?)",
                    ("synthetic", 1),
                    capture_boundaries=capture_boundaries,
                )
        except sqlite3.IntegrityError:
            raise
        return RunResult("accepted")

    def _write(
        self,
        fail_at: str | None,
        boundary: str,
        query: str,
        parameters: tuple[Any, ...],
        *,
        capture_boundaries: _CaptureBoundaries | None = None,
    ) -> None:
        if fail_at == boundary:
            raise sqlite3.IntegrityError(f"injected failure at {boundary}")
        self._execute(query, parameters, capture_boundaries=capture_boundaries)

    def _execute(
        self,
        query: str,
        parameters: tuple[Any, ...] = (),
        *,
        capture_boundaries: _CaptureBoundaries | None = None,
    ) -> sqlite3.Cursor:
        if capture_boundaries is not None:
            capture_boundaries.sqlite(query)
        return self.connection.execute(query, parameters)

    def snapshot(self) -> dict[str, int]:
        stable = self.stable_view()
        return {
            "usage_events": len(stable["events"]),
            "usage_event_amounts": len(stable["amounts"]),
            "logical_requests": len(stable["logical_requests"]),
            "ledger_sequences": len(stable["sequences"]),
            "aggregates": len(stable["aggregates"]),
            "obligations": len(stable["obligations"]),
            "cursor": len(stable["cursors"]),
        }

    def stable_view(self) -> dict[str, Any]:
        """Return the disposable harness's content-free public view contract."""
        events = [
            {
                "tool": tool,
                "request_id": request_id,
                "message_id": message_id,
                "model": model,
                "source_time": source_time,
                "cwd": cwd,
                "project": project,
                "ledger_seq": int(ledger_seq),
            }
            for tool, request_id, message_id, model, source_time, cwd, project, ledger_seq in self.connection.execute(
                "SELECT tool, request_id, message_id, model, source_time, cwd, project, ledger_seq "
                "FROM usage_events ORDER BY ledger_seq"
            )
        ]
        return {
            "events": events,
            "amounts": {
                category: int(amount)
                for category, amount in self.connection.execute(
                    "SELECT category, amount FROM usage_event_amounts ORDER BY category"
                )
            },
            "logical_requests": [
                request_id
                for (request_id,) in self.connection.execute(
                    "SELECT request_id FROM logical_requests ORDER BY request_id"
                )
            ],
            "sequences": [
                int(ledger_seq)
                for (ledger_seq,) in self.connection.execute(
                    "SELECT ledger_seq FROM synthetic_sequences ORDER BY ledger_seq"
                )
            ],
            "aggregates": {
                category: int(total)
                for category, total in self.connection.execute(
                    "SELECT category, total FROM synthetic_aggregates ORDER BY category"
                )
            },
            "obligations": [
                {"ledger_seq": int(ledger_seq), "obligation": obligation}
                for ledger_seq, obligation in self.connection.execute(
                    "SELECT ledger_seq, obligation FROM synthetic_obligations ORDER BY ledger_seq"
                )
            ],
            "cursors": {
                stream: int(position)
                for stream, position in self.connection.execute(
                    "SELECT stream, position FROM synthetic_cursors ORDER BY stream"
                )
            },
        }

    def health(self) -> dict[str, str]:
        state = self.connection.execute(
            "SELECT state FROM source_health WHERE stream = 'synthetic'"
        ).fetchone()
        return {"stream_state": str(state[0])}

    def close(self) -> None:
        self.connection.close()

    def run_privacy(
        self,
        *,
        fixture_path: Path | None = None,
        mutation: str | None = None,
    ) -> RunResult:
        """Exercise actual guarded capture boundaries against one fixture vector."""

        if mutation not in {
            None,
            "leak",
            "decoder",
            "materializer",
            "fingerprint",
            "network",
        }:
            raise ValidationError("unknown_mutation")
        manifest = self._manifest()
        audit = _CaptureAudit(tuple(manifest["capture_canaries"]))
        boundaries = _CaptureBoundaries(audit)
        boundaries.exercise_positive_controls(
            lambda canary: self._sqlite_positive_control(boundaries, canary)
        )
        if mutation == "network":
            boundaries.network(_FORBIDDEN_MARKER)
        target = self.config.fixture_path if fixture_path is None else fixture_path
        try:
            record, _, framing = self._read_record(
                target,
                boundaries,
                mutation=mutation,
            )
        except ValidationError as error:
            boundaries.exception(error.code)
            public_capture = self.stable_view()
            boundaries.application_value(public_capture)
            self._stats = audit.stats
            return RunResult(
                "rejected",
                rejection_code=error.code,
                forbidden_decoder_calls=audit.stats.forbidden_decoder_calls,
                forbidden_materializer_calls=audit.stats.forbidden_materializer_calls,
                forbidden_fingerprint_calls=audit.stats.forbidden_fingerprint_calls,
                public_capture=public_capture,
                capture_canaries=audit.canaries,
                capture_observations=audit.observations,
                framing=getattr(error, "framing", None),
            )
        result = self._run_record(record, capture_boundaries=boundaries)
        public_capture = self.stable_view()
        boundaries.application_value(public_capture)
        self._stats = audit.stats
        return RunResult(
            result.status,
            rejection_code=None,
            forbidden_decoder_calls=audit.stats.forbidden_decoder_calls,
            forbidden_materializer_calls=audit.stats.forbidden_materializer_calls,
            forbidden_fingerprint_calls=audit.stats.forbidden_fingerprint_calls,
            public_capture=public_capture,
            capture_canaries=audit.canaries,
            capture_observations=audit.observations,
            framing=framing,
        )

    def _sqlite_positive_control(
        self, boundaries: _CaptureBoundaries, canary: str
    ) -> None:
        """Observe a harmless SQL parameter without storing a capture artifact."""

        boundaries.sqlite(canary)
        self.connection.execute("SELECT ?", (canary,)).fetchone()

    def documented_exercise(
        self, *, elapsed_seconds: int, requested_reads: tuple[str, ...] | None = None
    ) -> ExerciseEvidence:
        """Execute the six documented stable-view/health reads after one setup run."""
        read_plan = (
            self.DOCUMENTED_READ_COMMANDS
            if requested_reads is None
            else requested_reads
        )
        self.run_once()
        before_replay = self.stable_view()
        self.run_file(self.config.fixture_path)
        after_replay = self.stable_view()

        reads: dict[str, Any] = {}
        private_table_reads = 0
        disallowed_read = False
        for command in read_plan:
            if command in self.DOCUMENTED_READ_COMMANDS:
                reads[command] = self._read_documented_command(command)
            else:
                disallowed_read = True
                if command in self.PRIVATE_BASE_TABLES:
                    private_table_reads += 1

        answers = self._answers_from_documented_reads(
            reads, before_replay, after_replay
        )
        required_answers = {
            "tool",
            "source_time",
            "model",
            "project",
            "categories",
            "amounts",
            "logical_request",
            "replay_counts",
            "health",
        }
        passed = (
            elapsed_seconds <= 600
            and len(read_plan) <= 6
            and private_table_reads == 0
            and not disallowed_read
            and set(answers) == required_answers
            and answers.get("replay_counts") == "unchanged"
        )
        return ExerciseEvidence(
            passed, elapsed_seconds, tuple(read_plan), answers, private_table_reads
        )

    def _read_documented_command(self, command: str) -> Any:
        if command == "usage_events":
            return [
                {
                    "tool": tool,
                    "source_time": source_time,
                    "model": model,
                    "project": project,
                }
                for tool, source_time, model, project in self.connection.execute(
                    "SELECT tool, source_time, model, project FROM usage_events ORDER BY ledger_seq"
                )
            ]
        if command == "usage_event_amounts":
            return [
                {"category": category, "amount": int(amount)}
                for category, amount in self.connection.execute(
                    "SELECT category, amount FROM usage_event_amounts ORDER BY "
                    "CASE category "
                    "WHEN 'input_tokens' THEN 1 "
                    "WHEN 'output_tokens' THEN 2 "
                    "WHEN 'cache_read_tokens' THEN 3 "
                    "WHEN 'cache_write_tokens' THEN 4 END"
                )
            ]
        if command == "logical_requests":
            return [
                request_id
                for (request_id,) in self.connection.execute(
                    "SELECT request_id FROM logical_requests ORDER BY request_id"
                )
            ]
        if command == "synthetic_aggregates":
            return {
                category: int(total)
                for category, total in self.connection.execute(
                    "SELECT category, total FROM synthetic_aggregates ORDER BY category"
                )
            }
        if command == "ledger_health":
            state, accepted_events = self.connection.execute(
                "SELECT state, accepted_events FROM ledger_health"
            ).fetchone()
            return {"state": state, "accepted_events": int(accepted_events)}
        if command == "health":
            return {"schema": "aiut.health/v1", **self.health()}
        raise ValidationError("unrecognized_read_command")

    @staticmethod
    def _answers_from_documented_reads(
        reads: dict[str, Any],
        before_replay: dict[str, Any],
        after_replay: dict[str, Any],
    ) -> dict[str, str]:
        answers: dict[str, str] = {}
        events = reads.get("usage_events")
        amounts = reads.get("usage_event_amounts")
        aggregates = reads.get("synthetic_aggregates")
        logical_requests = reads.get("logical_requests")
        health = reads.get("health")
        if isinstance(events, list) and len(events) == 1:
            event = events[0]
            if all(
                isinstance(event.get(key), str)
                for key in ("tool", "source_time", "model", "project")
            ):
                answers.update(
                    {
                        "tool": event["tool"],
                        "source_time": event["source_time"],
                        "model": event["model"],
                        "project": event["project"],
                    }
                )
        if isinstance(amounts, list) and isinstance(aggregates, dict):
            amount_map = {row["category"]: row["amount"] for row in amounts}
            if amount_map == aggregates and all(
                isinstance(row.get("category"), str)
                and isinstance(row.get("amount"), int)
                for row in amounts
            ):
                answers["categories"] = ",".join(row["category"] for row in amounts)
                answers["amounts"] = ",".join(str(row["amount"]) for row in amounts)
        if isinstance(logical_requests, list) and len(logical_requests) == 1:
            answers["logical_request"] = "1"
        if before_replay == after_replay:
            answers["replay_counts"] = "unchanged"
        if isinstance(health, dict) and health.get("schema") == "aiut.health/v1":
            state = health.get("stream_state")
            if isinstance(state, str):
                answers["health"] = state
        return answers
