#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Produce a transcript-minimizing skill-usage decision matrix.

The audit consumes the canonical catalog manifest emitted by
``scripts/link-ai-skills.sh --catalog-manifest``. It reads transcript files
only while streaming structured usage events into aggregate counters; it never
writes transcript-derived text, identifiers, filenames, projects, or absolute
paths into its report.
"""

import argparse
import hashlib
import json
import os
import stat
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Tuple


UTC = timezone.utc

PROFILE_RATIONALE: Dict[str, Tuple[str, str]] = dict((name, (trigger, overlap)) for name, trigger, overlap in (
    (
        "using-superpowers",
        "Session-start discovery guard for selecting applicable workflows.",
        "Native catalog injection can satisfy this guard without an observable file read.",
    ),
    (
        "brainstorming",
        "Clarify intent and design before creative implementation work.",
        "Complements implementation planning; it does not prescribe execution checkpoints.",
    ),
    (
        "writing-plans",
        "Turn an accepted design into a staged implementation plan.",
        "Distinct from brainstorming and from executing an already-written plan.",
    ),
    (
        "executing-plans",
        "Carry out a written plan with checkpoints in a separate session.",
        "Complements plan authoring rather than replacing independent-task dispatch.",
    ),
    (
        "using-git-worktrees",
        "Create isolated workspaces before risky or parallel implementation.",
        "Provides workspace isolation, not task delegation or review discipline.",
    ),
    (
        "test-driven-development",
        "Drive feature and bug-fix behavior from a failing test.",
        "Complements verification by defining implementation order rather than final evidence.",
    ),
    (
        "systematic-debugging",
        "Diagnose unexpected behavior before proposing a repair.",
        "Applies to failure analysis, not feature planning or test-first delivery.",
    ),
    (
        "verification-before-completion",
        "Collect current evidence before claiming a change is complete.",
        "Complements test-driven development with final exact-state verification.",
    ),
    (
        "dispatching-parallel-agents",
        "Dispatch two or more independent tasks that have no shared state.",
        "Distinct from subagent-driven-development: this coordinates independent work, not plan checkpoints.",
    ),
    (
        "subagent-driven-development",
        "Execute a written implementation plan with task and whole-branch review checkpoints.",
        "Distinct from dispatching-parallel-agents: this protects sequential plan execution and review.",
    ),
    (
        "finishing-a-development-branch",
        "Choose a safe integration path after a verified implementation is complete.",
        "Focuses on handoff and integration rather than code review itself.",
    ),
    (
        "requesting-code-review",
        "Request an independent quality pass for a completed change.",
        "Distinct from receiving-code-review, which evaluates and applies feedback.",
    ),
    (
        "receiving-code-review",
        "Evaluate code-review feedback rigorously before changing code.",
        "Distinct from requesting-code-review, which initiates the independent review.",
    ),
))

CODEX_SKILL_READ_FUNCTION = "skills.read"
MAX_RECORD_BYTES = 1_048_576
MAX_JSON_DEPTH = 64
MAX_CONTAINER_MEMBERS = 1_024
_SOURCE_DESCRIPTOR_FLAGS = (
    getattr(os, "O_NOFOLLOW", None),
    getattr(os, "O_DIRECTORY", None),
    getattr(os, "O_NONBLOCK", None),
)
_SOURCE_DESCRIPTORS_SUPPORTED = (
    all(isinstance(flag, int) and flag != 0 for flag in _SOURCE_DESCRIPTOR_FLAGS)
    and os.open in os.supports_dir_fd
    and os.scandir in os.supports_fd
)
_CANDIDATE_NAMES = tuple(PROFILE_RATIONALE)
_CANDIDATE_BYTES = tuple(name.encode("ascii") for name in _CANDIDATE_NAMES)


def configure_candidates(names: Sequence[str]) -> None:
    """Install only manifest-provided names in the byte-level matchers."""
    global _CANDIDATE_NAMES, _CANDIDATE_BYTES
    ordered = tuple(sorted(names))
    if not ordered or any(not name.isascii() for name in ordered):
        raise ValueError("catalog manifest contains unsupported skill names")
    _CANDIDATE_NAMES = ordered
    _CANDIDATE_BYTES = tuple(name.encode("ascii") for name in ordered)


def default_repo_root() -> Path:
    """Return the repository root when this script is run from its source tree."""
    return Path(__file__).resolve().parents[6]


def parse_utc_timestamp(value: str) -> datetime:
    """Accept only an explicit zero-offset timestamp for reproducible windows."""
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("--as-of must be an explicit UTC timestamp") from exc
    if parsed.tzinfo is None or parsed.utcoffset() != timedelta(0):
        raise argparse.ArgumentTypeError("--as-of must be an explicit UTC timestamp")
    return parsed.astimezone(UTC)


def timestamp_text(value: Optional[datetime]) -> Optional[str]:
    if value is None:
        return None
    return value.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def safe_source_path(repo_root: Path, source: Any) -> Optional[Path]:
    """Resolve a manifest source only when it remains a repo-relative skill path."""
    if not isinstance(source, str):
        return None
    candidate = Path(source)
    if candidate.is_absolute() or candidate.parts[:1] != ("skills",) or ".." in candidate.parts:
        return None
    resolved_root = repo_root.resolve()
    resolved = (resolved_root / candidate).resolve()
    try:
        resolved.relative_to(resolved_root)
    except ValueError:
        return None
    return resolved


def load_catalog_manifest(repo_root: Path, manifest_path: Optional[Path]) -> Dict[str, Dict[str, str]]:
    """Load a linker manifest without passing its raw filesystem inputs through."""
    if manifest_path is None:
        linker = repo_root / "scripts" / "link-ai-skills.sh"
        try:
            result = subprocess.run(
                ["bash", str(linker), "--catalog-manifest", str(repo_root)],
                capture_output=True,
                text=True,
                timeout=30,
                check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            raise ValueError("catalog manifest generation failed") from exc
        if result.returncode != 0:
            raise ValueError("catalog manifest generation failed")
        raw_manifest = result.stdout
    else:
        try:
            raw_manifest = manifest_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise ValueError("catalog manifest unavailable") from exc

    try:
        payload = json.loads(raw_manifest)
    except json.JSONDecodeError as exc:
        raise ValueError("catalog manifest is invalid") from exc
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError("catalog manifest is invalid")
    if not isinstance(payload.get("selection_rule"), str):
        raise ValueError("catalog manifest is invalid")
    if not isinstance(payload.get("excluded_names"), list) or any(
        not isinstance(name, str) for name in payload["excluded_names"]
    ):
        raise ValueError("catalog manifest is invalid")
    if not isinstance(payload.get("surfaces"), list) or any(
        not isinstance(surface, str) for surface in payload["surfaces"]
    ):
        raise ValueError("catalog manifest is invalid")
    entries = payload.get("skills")
    if not isinstance(entries, list):
        raise ValueError("catalog manifest is invalid")

    catalog: Dict[str, Dict[str, str]] = {}
    for entry in entries:
        if not isinstance(entry, dict):
            raise ValueError("catalog manifest is invalid")
        name = entry.get("name")
        source = entry.get("source")
        ownership = entry.get("ownership")
        if (
            not isinstance(name, str)
            or not name
            or not isinstance(source, str)
            or safe_source_path(repo_root, source) is None
            or ownership not in {"repo", "submodule"}
            or name in catalog
        ):
            raise ValueError("catalog manifest is invalid")
        catalog[name] = {"source": source, "ownership": ownership}
    configure_candidates(tuple(catalog))
    return catalog


def frontmatter_tokens(skill_dir: Optional[Path]) -> Optional[int]:
    """Estimate catalog cost from the frontmatter actually exposed by the linker."""
    if skill_dir is None:
        return None
    chars = 0
    fences = 0
    try:
        for line in (skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="ignore").splitlines():
            if line.strip() == "---":
                fences += 1
                if fences == 2:
                    break
            elif fences == 1:
                chars += len(line) + 1
    except OSError:
        return None
    return chars // 4


@dataclass(frozen=True)
class JsonSpan:
    """A byte range inside one bounded JSONL record, never a decoded value."""

    start: int
    end: int


class JsonInputError(ValueError):
    """A malformed or over-bounded input record that must hold coverage open."""


@dataclass
class ScanOutcome:
    """Aggregate counters plus fail-closed source-read evidence."""

    primary_counts: Counter
    sensitivity_counts: Counter
    input_errors: int = 0
    records_scanned: int = 0
    bytes_scanned: int = 0
    cache_hit: bool = False

    @property
    def input_complete(self) -> bool:
        return self.input_errors == 0

    def __getitem__(self, name: str) -> int:
        """Keep direct extractor checks focused on primary aggregate counters."""
        return int(self.primary_counts[name])


@dataclass(frozen=True)
class SourceIdentity:
    """The stable filesystem identity required for a source-bound descriptor."""

    device: int
    inode: int
    file_type: int
    size: int
    modified_ns: int


@dataclass(frozen=True)
class BoundDirectory:
    """A source-root-relative directory path with every ancestor identity."""

    parts: Tuple[str, ...]
    identities: Tuple[SourceIdentity, ...]


@dataclass(frozen=True)
class BoundTranscript:
    """A discovered regular JSONL file that must reopen to its original inode."""

    root: Path
    parent: BoundDirectory
    name: str
    identity: SourceIdentity


def _span_matches(data: bytes, span: Optional[JsonSpan], expected: bytes) -> bool:
    """Compare only a small registered JSON string without decoding raw input."""
    if span is None or span.end - span.start != len(expected) + 2:
        return False
    return data[span.start + 1 : span.end - 1] == expected


def _candidate_from_span(data: bytes, span: Optional[JsonSpan]) -> Optional[str]:
    for name, encoded in zip(_CANDIDATE_NAMES, _CANDIDATE_BYTES):
        if _span_matches(data, span, encoded):
            return name
    return None


class JsonCursor:
    """Validate JSON syntax while retaining only spans for registered fields."""

    def __init__(self, data: bytes, start: int = 0, end: Optional[int] = None) -> None:
        self.data = data
        self.position = start
        self.end = len(data) if end is None else end

    def finish(self) -> None:
        self._skip_whitespace()
        if self.position != self.end:
            raise JsonInputError("trailing input")

    def parse_value(self, depth: int = 0) -> JsonSpan:
        if depth > MAX_JSON_DEPTH:
            raise JsonInputError("maximum JSON depth exceeded")
        self._skip_whitespace()
        start = self.position
        if start >= self.end:
            raise JsonInputError("missing JSON value")
        value = self.data[self.position]
        if value == ord('"'):
            self._parse_string()
        elif value == ord("{"):
            self._skip_object(depth + 1)
        elif value == ord("["):
            self._skip_array(depth + 1)
        elif value in b"-0123456789":
            self._skip_number()
        elif self.data.startswith(b"true", self.position):
            self.position += 4
        elif self.data.startswith(b"false", self.position):
            self.position += 5
        elif self.data.startswith(b"null", self.position):
            self.position += 4
        else:
            raise JsonInputError("invalid JSON value")
        return JsonSpan(start, self.position)

    def parse_object_fields(self, wanted: Sequence[bytes], depth: int = 0) -> Dict[bytes, JsonSpan]:
        """Capture only whitelisted object values and skip everything else."""
        if depth > MAX_JSON_DEPTH:
            raise JsonInputError("maximum JSON depth exceeded")
        self._skip_whitespace()
        self._expect(ord("{"))
        self._skip_whitespace()
        fields: Dict[bytes, JsonSpan] = {}
        if self._consume(ord("}")):
            return fields
        members = 0
        while True:
            if members >= MAX_CONTAINER_MEMBERS:
                raise JsonInputError("too many object members")
            key = self._parse_string()
            known_key = next((item for item in wanted if _span_matches(self.data, key, item)), None)
            self._skip_whitespace()
            self._expect(ord(":"))
            value = self.parse_value(depth + 1)
            if known_key is not None:
                if known_key in fields:
                    raise JsonInputError("duplicate registered field")
                fields[known_key] = value
            members += 1
            self._skip_whitespace()
            if self._consume(ord("}")):
                return fields
            self._expect(ord(","))
            self._skip_whitespace()

    def _skip_object(self, depth: int) -> None:
        self._expect(ord("{"))
        self._skip_whitespace()
        if self._consume(ord("}")):
            return
        members = 0
        while True:
            if members >= MAX_CONTAINER_MEMBERS:
                raise JsonInputError("too many object members")
            self._parse_string()
            self._skip_whitespace()
            self._expect(ord(":"))
            self.parse_value(depth + 1)
            members += 1
            self._skip_whitespace()
            if self._consume(ord("}")):
                return
            self._expect(ord(","))
            self._skip_whitespace()

    def _skip_array(self, depth: int) -> None:
        self._expect(ord("["))
        self._skip_whitespace()
        if self._consume(ord("]")):
            return
        members = 0
        while True:
            if members >= MAX_CONTAINER_MEMBERS:
                raise JsonInputError("too many array members")
            self.parse_value(depth + 1)
            members += 1
            self._skip_whitespace()
            if self._consume(ord("]")):
                return
            self._expect(ord(","))
            self._skip_whitespace()

    def _parse_string(self) -> JsonSpan:
        start = self.position
        self._expect(ord('"'))
        while self.position < self.end:
            value = self.data[self.position]
            if value == ord('"'):
                self.position += 1
                return JsonSpan(start, self.position)
            if value < 0x20:
                raise JsonInputError("control character in JSON string")
            if value != ord("\\"):
                self.position += 1
                if value >= 0x80:
                    self._consume_utf8_sequence(value)
                continue
            self.position += 1
            if self.position >= self.end:
                raise JsonInputError("unterminated JSON escape")
            escaped = self.data[self.position]
            self.position += 1
            if escaped in b'"\\/bfnrt':
                continue
            if escaped != ord("u") or self.position + 4 > self.end:
                raise JsonInputError("invalid JSON escape")
            if any(byte not in b"0123456789abcdefABCDEF" for byte in self.data[self.position : self.position + 4]):
                raise JsonInputError("invalid unicode escape")
            self.position += 4
        raise JsonInputError("unterminated JSON string")

    def _consume_utf8_sequence(self, leading: int) -> None:
        """Validate one raw UTF-8 scalar without decoding or retaining it."""
        if 0xC2 <= leading <= 0xDF:
            self._consume_utf8_continuation()
        elif leading == 0xE0:
            self._consume_utf8_continuation(0xA0)
            self._consume_utf8_continuation()
        elif 0xE1 <= leading <= 0xEC or 0xEE <= leading <= 0xEF:
            self._consume_utf8_continuation()
            self._consume_utf8_continuation()
        elif leading == 0xED:
            self._consume_utf8_continuation(0x80, 0x9F)
            self._consume_utf8_continuation()
        elif leading == 0xF0:
            self._consume_utf8_continuation(0x90)
            self._consume_utf8_continuation()
            self._consume_utf8_continuation()
        elif 0xF1 <= leading <= 0xF3:
            self._consume_utf8_continuation()
            self._consume_utf8_continuation()
            self._consume_utf8_continuation()
        elif leading == 0xF4:
            self._consume_utf8_continuation(0x80, 0x8F)
            self._consume_utf8_continuation()
            self._consume_utf8_continuation()
        else:
            raise JsonInputError("invalid UTF-8 in JSON string")

    def _consume_utf8_continuation(self, lower: int = 0x80, upper: int = 0xBF) -> None:
        if self.position >= self.end or not lower <= self.data[self.position] <= upper:
            raise JsonInputError("invalid UTF-8 in JSON string")
        self.position += 1

    def _skip_number(self) -> None:
        if self._consume(ord("-")) and self.position >= self.end:
            raise JsonInputError("invalid JSON number")
        if self._consume(ord("0")):
            pass
        elif self.position < self.end and self.data[self.position] in b"123456789":
            while self.position < self.end and self.data[self.position] in b"0123456789":
                self.position += 1
        else:
            raise JsonInputError("invalid JSON number")
        if self._consume(ord(".")):
            start = self.position
            while self.position < self.end and self.data[self.position] in b"0123456789":
                self.position += 1
            if self.position == start:
                raise JsonInputError("invalid JSON number")
        if self.position < self.end and self.data[self.position] in b"eE":
            self.position += 1
            if self.position < self.end and self.data[self.position] in b"+-":
                self.position += 1
            start = self.position
            while self.position < self.end and self.data[self.position] in b"0123456789":
                self.position += 1
            if self.position == start:
                raise JsonInputError("invalid JSON number")

    def _skip_whitespace(self) -> None:
        while self.position < self.end and self.data[self.position] in b" \t\r\n":
            self.position += 1

    def _expect(self, expected: int) -> None:
        if self.position >= self.end or self.data[self.position] != expected:
            raise JsonInputError("unexpected JSON token")
        self.position += 1

    def _consume(self, expected: int) -> bool:
        if self.position < self.end and self.data[self.position] == expected:
            self.position += 1
            return True
        return False


def _object_fields(data: bytes, span: Optional[JsonSpan], wanted: Sequence[bytes]) -> Optional[Dict[bytes, JsonSpan]]:
    if span is None or span.start >= span.end or data[span.start] != ord("{"):
        return None
    cursor = JsonCursor(data, span.start, span.end)
    fields = cursor.parse_object_fields(wanted)
    cursor.finish()
    return fields


def _array_spans(data: bytes, span: Optional[JsonSpan]) -> Optional[List[JsonSpan]]:
    if span is None or span.start >= span.end or data[span.start] != ord("["):
        return None
    cursor = JsonCursor(data, span.start, span.end)
    cursor._expect(ord("["))
    cursor._skip_whitespace()
    entries: List[JsonSpan] = []
    if cursor._consume(ord("]")):
        cursor.finish()
        return entries
    while True:
        if len(entries) >= MAX_CONTAINER_MEMBERS:
            raise JsonInputError("too many array members")
        entries.append(cursor.parse_value())
        cursor._skip_whitespace()
        if cursor._consume(ord("]")):
            cursor.finish()
            return entries
        cursor._expect(ord(","))
        cursor._skip_whitespace()


def _root_object_fields(data: bytes, wanted: Sequence[bytes]) -> Optional[Dict[bytes, JsonSpan]]:
    """Validate the complete record before inspecting its registered envelope."""
    cursor = JsonCursor(data)
    span = cursor.parse_value()
    cursor.finish()
    return _object_fields(data, span, wanted)


class JsonStringReader:
    """Read one JSON string's encoded bytes one scalar at a time, without joining it."""

    def __init__(self, data: bytes, span: JsonSpan) -> None:
        self.data = data
        self.position = span.start + 1
        self.end = span.end - 1
        self.buffered: Optional[int] = None

    def read(self) -> Optional[int]:
        if self.buffered is not None:
            value = self.buffered
            self.buffered = None
            return value
        if self.position >= self.end:
            return None
        value = self.data[self.position]
        self.position += 1
        if value != ord("\\"):
            return value
        if self.position >= self.end:
            raise JsonInputError("unterminated JSON escape")
        escaped = self.data[self.position]
        self.position += 1
        escapes = {
            ord('"'): ord('"'),
            ord("\\"): ord("\\"),
            ord("/"): ord("/"),
            ord("b"): 0x08,
            ord("f"): 0x0C,
            ord("n"): 0x0A,
            ord("r"): 0x0D,
            ord("t"): 0x09,
        }
        if escaped in escapes:
            return escapes[escaped]
        if escaped != ord("u") or self.position + 4 > self.end:
            raise JsonInputError("invalid JSON escape")
        digits = self.data[self.position : self.position + 4]
        if any(byte not in b"0123456789abcdefABCDEF" for byte in digits):
            raise JsonInputError("invalid unicode escape")
        self.position += 4
        codepoint = int(digits, 16)
        return codepoint if codepoint <= 0x7F else 0x80

    def peek(self) -> Optional[int]:
        if self.buffered is None:
            self.buffered = self.read()
        return self.buffered


def _consume_ascii(reader: JsonStringReader, expected: bytes) -> bool:
    return all(reader.read() == value for value in expected)


def _skip_string_whitespace(reader: JsonStringReader) -> None:
    while reader.peek() in (ord(" "), ord("\t"), ord("\r"), ord("\n")):
        reader.read()


def _skip_until(reader: JsonStringReader, end_marker: bytes) -> bool:
    matched = 0
    while True:
        value = reader.read()
        if value is None:
            return False
        if value == end_marker[matched]:
            matched += 1
            if matched == len(end_marker):
                return True
        else:
            matched = 1 if value == end_marker[0] else 0


def _candidate_until_tag(reader: JsonStringReader, end_tag: bytes) -> Optional[str]:
    active = (1 << len(_CANDIDATE_BYTES)) - 1
    length = 0
    while True:
        value = reader.read()
        if value is None:
            return None
        if value == ord("<"):
            if not _consume_ascii(reader, end_tag[1:]):
                return None
            break
        for index, candidate in enumerate(_CANDIDATE_BYTES):
            if active & (1 << index) and (length >= len(candidate) or candidate[length] != value):
                active &= ~(1 << index)
        length += 1
    for index, candidate in enumerate(_CANDIDATE_BYTES):
        if active & (1 << index) and length == len(candidate):
            return _CANDIDATE_NAMES[index]
    return None


def _slash_command_from_span(data: bytes, span: Optional[JsonSpan]) -> Optional[str]:
    if span is None or span.start >= span.end or data[span.start] != ord('"'):
        return None
    reader = JsonStringReader(data, span)
    _skip_string_whitespace(reader)
    if not _consume_ascii(reader, b"<command-message>"):
        return None
    if not _skip_until(reader, b"</command-message>"):
        return None
    _skip_string_whitespace(reader)
    if not _consume_ascii(reader, b"<command-name>/"):
        return None
    name = _candidate_until_tag(reader, b"</command-name>")
    if name is None:
        return None
    _skip_string_whitespace(reader)
    if reader.peek() == ord("<"):
        if not _consume_ascii(reader, b"<command-args>"):
            return None
        if not _skip_until(reader, b"</command-args>"):
            return None
        _skip_string_whitespace(reader)
    return name if reader.read() is None else None


class EmbeddedJsonCursor:
    """Parse registered fields in encoded Codex arguments without joining them."""

    def __init__(self, reader: JsonStringReader) -> None:
        self.reader = reader

    def parse_path(self) -> Optional[str]:
        self._skip_whitespace()
        self._expect(ord("{"))
        self._skip_whitespace()
        found_path = False
        path: Optional[str] = None
        if self._consume(ord("}")):
            self._finish()
            return None
        members = 0
        while True:
            if members >= MAX_CONTAINER_MEMBERS:
                raise JsonInputError("too many object members")
            key = self._read_string_match(((b"path", "path"),))
            self._skip_whitespace()
            self._expect(ord(":"))
            self._skip_whitespace()
            if key == "path":
                if found_path:
                    raise JsonInputError("duplicate registered field")
                found_path = True
                if self._peek() == ord('"'):
                    path = self._read_path_candidate()
                else:
                    self._skip_value()
            else:
                self._skip_value()
            members += 1
            self._skip_whitespace()
            if self._consume(ord("}")):
                self._finish()
                return path
            self._expect(ord(","))
            self._skip_whitespace()

    def parse_skill(self) -> Optional[str]:
        """Accept only an exact manifest skill in a structured ``skill`` field."""
        self._skip_whitespace()
        self._expect(ord("{"))
        self._skip_whitespace()
        found = False
        skill: Optional[str] = None
        if self._consume(ord("}")):
            self._finish()
            return None
        members = 0
        while True:
            if members >= MAX_CONTAINER_MEMBERS:
                raise JsonInputError("too many object members")
            key = self._read_string_match(((b"skill", "skill"),))
            self._skip_whitespace()
            self._expect(ord(":"))
            self._skip_whitespace()
            if key == "skill":
                if found:
                    raise JsonInputError("duplicate registered field")
                found = True
                if self._peek() == ord('"'):
                    skill = self._read_string_match(tuple(zip(_CANDIDATE_BYTES, _CANDIDATE_NAMES)))
                else:
                    self._skip_value()
            else:
                self._skip_value()
            members += 1
            self._skip_whitespace()
            if self._consume(ord("}")):
                self._finish()
                return skill
            self._expect(ord(","))
            self._skip_whitespace()

    def _skip_value(self, depth: int = 0) -> None:
        if depth > MAX_JSON_DEPTH:
            raise JsonInputError("maximum JSON depth exceeded")
        self._skip_whitespace()
        value = self._peek()
        if value == ord('"'):
            self._read_string_match(())
        elif value == ord("{"):
            self._skip_object(depth + 1)
        elif value == ord("["):
            self._skip_array(depth + 1)
        elif value in (ord("-"), ord("0"), ord("1"), ord("2"), ord("3"), ord("4"), ord("5"), ord("6"), ord("7"), ord("8"), ord("9")):
            self._skip_number()
        elif value == ord("t"):
            self._expect_literal(b"true")
        elif value == ord("f"):
            self._expect_literal(b"false")
        elif value == ord("n"):
            self._expect_literal(b"null")
        else:
            raise JsonInputError("invalid JSON value")

    def _skip_object(self, depth: int) -> None:
        self._expect(ord("{"))
        self._skip_whitespace()
        if self._consume(ord("}")):
            return
        members = 0
        while True:
            if members >= MAX_CONTAINER_MEMBERS:
                raise JsonInputError("too many object members")
            self._read_string_match(())
            self._skip_whitespace()
            self._expect(ord(":"))
            self._skip_value(depth + 1)
            members += 1
            self._skip_whitespace()
            if self._consume(ord("}")):
                return
            self._expect(ord(","))
            self._skip_whitespace()

    def _skip_array(self, depth: int) -> None:
        self._expect(ord("["))
        self._skip_whitespace()
        if self._consume(ord("]")):
            return
        members = 0
        while True:
            if members >= MAX_CONTAINER_MEMBERS:
                raise JsonInputError("too many array members")
            self._skip_value(depth + 1)
            members += 1
            self._skip_whitespace()
            if self._consume(ord("]")):
                return
            self._expect(ord(","))
            self._skip_whitespace()

    def _read_string_match(self, targets: Sequence[Tuple[bytes, str]]) -> Optional[str]:
        self._expect(ord('"'))
        active = (1 << len(targets)) - 1
        length = 0
        while True:
            value = self.reader.read()
            if value is None:
                raise JsonInputError("unterminated JSON string")
            if value == ord('"'):
                for index, (candidate, result) in enumerate(targets):
                    if active & (1 << index) and length == len(candidate):
                        return result
                return None
            if value == ord("\\"):
                value = self._read_escape()
            elif value < 0x20:
                raise JsonInputError("control character in JSON string")
            for index, (candidate, _result) in enumerate(targets):
                if active & (1 << index) and (length >= len(candidate) or candidate[length] != value):
                    active &= ~(1 << index)
            length += 1

    def _read_path_candidate(self) -> Optional[str]:
        self._expect(ord('"'))
        matcher = SafePathMatcher()
        while True:
            value = self.reader.read()
            if value is None:
                raise JsonInputError("unterminated JSON string")
            if value == ord('"'):
                return matcher.finish()
            if value == ord("\\"):
                value = self._read_escape()
            elif value < 0x20:
                raise JsonInputError("control character in JSON string")
            matcher.push(value)

    def _read_escape(self) -> int:
        escaped = self.reader.read()
        if escaped is None:
            raise JsonInputError("unterminated JSON escape")
        escapes = {
            ord('"'): ord('"'),
            ord("\\"): ord("\\"),
            ord("/"): ord("/"),
            ord("b"): 0x08,
            ord("f"): 0x0C,
            ord("n"): 0x0A,
            ord("r"): 0x0D,
            ord("t"): 0x09,
        }
        if escaped in escapes:
            return escapes[escaped]
        if escaped != ord("u"):
            raise JsonInputError("invalid JSON escape")
        digits = [self.reader.read() for _ in range(4)]
        if any(value is None or value not in b"0123456789abcdefABCDEF" for value in digits):
            raise JsonInputError("invalid unicode escape")
        codepoint = int(bytes(digits), 16)
        return codepoint if codepoint <= 0x7F else 0x80

    def _skip_number(self) -> None:
        if self._consume(ord("-")) and self._peek() is None:
            raise JsonInputError("invalid JSON number")
        if self._consume(ord("0")):
            pass
        elif self._peek() in (ord("1"), ord("2"), ord("3"), ord("4"), ord("5"), ord("6"), ord("7"), ord("8"), ord("9")):
            while self._peek() in (ord("0"), ord("1"), ord("2"), ord("3"), ord("4"), ord("5"), ord("6"), ord("7"), ord("8"), ord("9")):
                self.reader.read()
        else:
            raise JsonInputError("invalid JSON number")
        if self._consume(ord(".")):
            start = self._peek()
            if start not in (ord("0"), ord("1"), ord("2"), ord("3"), ord("4"), ord("5"), ord("6"), ord("7"), ord("8"), ord("9")):
                raise JsonInputError("invalid JSON number")
            while self._peek() in (ord("0"), ord("1"), ord("2"), ord("3"), ord("4"), ord("5"), ord("6"), ord("7"), ord("8"), ord("9")):
                self.reader.read()
        if self._peek() in (ord("e"), ord("E")):
            self.reader.read()
            if self._peek() in (ord("+"), ord("-")):
                self.reader.read()
            if self._peek() not in (ord("0"), ord("1"), ord("2"), ord("3"), ord("4"), ord("5"), ord("6"), ord("7"), ord("8"), ord("9")):
                raise JsonInputError("invalid JSON number")
            while self._peek() in (ord("0"), ord("1"), ord("2"), ord("3"), ord("4"), ord("5"), ord("6"), ord("7"), ord("8"), ord("9")):
                self.reader.read()

    def _skip_whitespace(self) -> None:
        while self._peek() in (ord(" "), ord("\t"), ord("\r"), ord("\n")):
            self.reader.read()

    def _finish(self) -> None:
        self._skip_whitespace()
        if self._peek() is not None:
            raise JsonInputError("trailing input")

    def _expect(self, expected: int) -> None:
        if self.reader.read() != expected:
            raise JsonInputError("unexpected JSON token")

    def _consume(self, expected: int) -> bool:
        if self._peek() == expected:
            self.reader.read()
            return True
        return False

    def _expect_literal(self, expected: bytes) -> None:
        for value in expected:
            self._expect(value)

    def _peek(self) -> Optional[int]:
        return self.reader.peek()


class SafePathMatcher:
    """Recognize only an allowed SKILL.md path and retain its known catalog name."""

    def __init__(self) -> None:
        self.after_skills = False
        self.at_start = True
        self.invalid = False
        self.last_candidate: Optional[str] = None
        self.last_was_skill_file = False
        self.terminal_candidate: Optional[str] = None
        self._reset_component()

    def push(self, value: int) -> None:
        if value in (ord("/"), ord("\\")):
            if self.component_length == 0:
                if self.at_start:
                    self.at_start = False
                    return
                self.invalid = True
                return
            self._finish_component()
            self.at_start = False
            self._reset_component()
            return
        self.at_start = False
        allowed = b"ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789._-"
        if not self.after_skills:
            allowed += b"~:"
        if value not in allowed:
            self.invalid = True
        for index, candidate in enumerate(_CANDIDATE_BYTES):
            if self.candidate_mask & (1 << index) and (
                self.component_length >= len(candidate) or candidate[self.component_length] != value
            ):
                self.candidate_mask &= ~(1 << index)
        if self.component_length >= len(b"skills") or b"skills"[self.component_length] != value:
            self.skills_matches = False
        if self.component_length >= len(b"SKILL.md") or b"SKILL.md"[self.component_length] != value:
            self.skill_file_matches = False
        self.component_length += 1

    def finish(self) -> Optional[str]:
        if self.component_length == 0:
            self.invalid = True
        else:
            self._finish_component()
        if self.invalid or not self.after_skills or not self.last_was_skill_file:
            return None
        return self.terminal_candidate

    def _reset_component(self) -> None:
        self.component_length = 0
        self.candidate_mask = (1 << len(_CANDIDATE_BYTES)) - 1
        self.skills_matches = True
        self.skill_file_matches = True

    def _finish_component(self) -> None:
        if not self.after_skills:
            if self.skills_matches and self.component_length == len(b"skills"):
                self.after_skills = True
            return
        is_skill_file = self.skill_file_matches and self.component_length == len(b"SKILL.md")
        if is_skill_file:
            self.terminal_candidate = self.last_candidate
            self.last_was_skill_file = True
            return
        self.last_candidate = None
        for index, candidate in enumerate(_CANDIDATE_BYTES):
            if self.candidate_mask & (1 << index) and self.component_length == len(candidate):
                self.last_candidate = _CANDIDATE_NAMES[index]
                break
        self.last_was_skill_file = False


def _extract_claude_record(data: bytes) -> Sequence[str]:
    root = _root_object_fields(data, (b"type", b"message"))
    if root is None:
        return ()
    record_type = root.get(b"type")
    message = _object_fields(data, root.get(b"message"), (b"role", b"content"))
    if message is None:
        return ()
    if _span_matches(data, record_type, b"assistant") and _span_matches(data, message.get(b"role"), b"assistant"):
        blocks = _array_spans(data, message.get(b"content"))
        if blocks is None:
            return ()
        counted: List[str] = []
        for block in blocks:
            block_fields = _object_fields(data, block, (b"type", b"name", b"input"))
            if block_fields is None:
                continue
            if not _span_matches(data, block_fields.get(b"type"), b"tool_use"):
                continue
            if not _span_matches(data, block_fields.get(b"name"), b"Skill"):
                continue
            tool_input = _object_fields(data, block_fields.get(b"input"), (b"skill",))
            skill = _candidate_from_span(data, tool_input.get(b"skill") if tool_input is not None else None)
            if skill is not None:
                counted.append(skill)
        return counted
    if _span_matches(data, record_type, b"user") and _span_matches(data, message.get(b"role"), b"user"):
        name = _slash_command_from_span(data, message.get(b"content"))
        return (name,) if name is not None else ()
    return ()


def _extract_codex_record(data: bytes) -> Sequence[str]:
    root = _root_object_fields(data, (b"type", b"payload"))
    if root is None or not _span_matches(data, root.get(b"type"), b"response_item"):
        return ()
    payload = _object_fields(data, root.get(b"payload"), (b"type", b"name", b"arguments"))
    if payload is None:
        return ()
    if not _span_matches(data, payload.get(b"type"), b"function_call"):
        return ()
    if _span_matches(data, payload.get(b"name"), b"read_file"):
        raise JsonInputError("unsupported retired Codex skill event schema")
    if not _span_matches(data, payload.get(b"name"), CODEX_SKILL_READ_FUNCTION.encode("ascii")):
        return ()
    arguments = payload.get(b"arguments")
    if arguments is None or data[arguments.start] != ord('"'):
        return ()
    name = EmbeddedJsonCursor(JsonStringReader(data, arguments)).parse_skill()
    return (name,) if name is not None else ()


def _source_identity(metadata: os.stat_result) -> SourceIdentity:
    """Keep only inode identity and file type needed to bind source handles."""
    return SourceIdentity(
        device=int(metadata.st_dev),
        inode=int(metadata.st_ino),
        file_type=stat.S_IFMT(metadata.st_mode),
        size=int(metadata.st_size),
        modified_ns=int(metadata.st_mtime_ns),
    )


def _matches_identity(metadata: os.stat_result, expected: SourceIdentity, expected_type: int) -> bool:
    """Require the discovered inode and expected regular-file or directory type."""
    return expected.file_type == expected_type and _source_identity(metadata) == expected


def _source_descriptors_supported() -> bool:
    """Require the non-following descriptor primitives; never fall back to paths."""
    return _SOURCE_DESCRIPTORS_SUPPORTED


def _open_nonfollowing(path: Any, directory: bool, dir_fd: Optional[int] = None) -> int:
    """Open one source path component without following links or blocking on swaps."""
    if not _source_descriptors_supported():
        raise OSError("non-following source descriptors are unavailable")
    flags = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK
    if directory:
        flags |= os.O_DIRECTORY
    if dir_fd is None:
        return os.open(path, flags)
    return os.open(path, flags, dir_fd=dir_fd)


def _snapshot_root(root: Path) -> BoundDirectory:
    """Bind the configured source root before traversal can inspect a child."""
    root_fd = _open_nonfollowing(root, directory=True)
    try:
        identity = _source_identity(os.fstat(root_fd))
        if identity.file_type != stat.S_IFDIR:
            raise OSError("configured source is not a directory")
        return BoundDirectory((), (identity,))
    finally:
        os.close(root_fd)


def _open_bound_directory(root: Path, directory: BoundDirectory) -> int:
    """Reopen every ancestor below a non-following root and verify its identity."""
    if len(directory.identities) != len(directory.parts) + 1:
        raise OSError("source directory identity is incomplete")
    directory_fd = _open_nonfollowing(root, directory=True)
    try:
        if not _matches_identity(os.fstat(directory_fd), directory.identities[0], stat.S_IFDIR):
            raise OSError("configured source identity changed")
        for part, expected in zip(directory.parts, directory.identities[1:]):
            child_fd = _open_nonfollowing(part, directory=True, dir_fd=directory_fd)
            try:
                if not _matches_identity(os.fstat(child_fd), expected, stat.S_IFDIR):
                    raise OSError("nested source identity changed")
            except OSError:
                os.close(child_fd)
                raise
            previous_fd = directory_fd
            directory_fd = child_fd
            try:
                os.close(previous_fd)
            except OSError:
                os.close(directory_fd)
                raise
        return directory_fd
    except OSError:
        try:
            os.close(directory_fd)
        except OSError:
            pass
        raise


def _binary_handle_from_fd(fd: int, expected: Optional[SourceIdentity]) -> Any:
    """Validate a non-following descriptor before any transcript bytes are read."""
    try:
        metadata = os.fstat(fd)
        if stat.S_IFMT(metadata.st_mode) != stat.S_IFREG:
            raise OSError("source is not a regular file")
        if expected is not None and not _matches_identity(metadata, expected, stat.S_IFREG):
            raise OSError("source file identity changed")
        return os.fdopen(fd, "rb")
    except OSError:
        try:
            os.close(fd)
        except OSError:
            pass
        raise


def _open_bound_transcript(transcript: BoundTranscript) -> Any:
    """Open only the discovered regular file through identity-bound directories."""
    parent_fd = _open_bound_directory(transcript.root, transcript.parent)
    try:
        file_fd = _open_nonfollowing(transcript.name, directory=False, dir_fd=parent_fd)
    finally:
        os.close(parent_fd)
    return _binary_handle_from_fd(file_fd, transcript.identity)


def _open_unbound_transcript(entry_path: Path) -> Any:
    """Keep direct extractor tests non-following even without an inventory snapshot."""
    parent_fd = _open_nonfollowing(entry_path.parent, directory=True)
    try:
        file_fd = _open_nonfollowing(entry_path.name, directory=False, dir_fd=parent_fd)
    finally:
        os.close(parent_fd)
    return _binary_handle_from_fd(file_fd, None)


def _open_transcript(entry: Any) -> Any:
    """Select the only supported source handles; path fallback remains non-following."""
    if isinstance(entry, BoundTranscript):
        return _open_bound_transcript(entry)
    if isinstance(entry, Path):
        return _open_unbound_transcript(entry)
    raise OSError("source handle is invalid")


def _scan_records(
    files: Sequence[Any],
    sensitivity_files: Sequence[Any],
    extractor: Callable[[bytes], Sequence[str]],
) -> ScanOutcome:
    """Read bounded raw records once, count safe names, and surface every input failure."""
    outcome = ScanOutcome(Counter(), Counter())
    sensitivity = set(sensitivity_files)
    for entry in files:
        try:
            with _open_transcript(entry) as handle:
                while True:
                    raw_line = handle.readline(MAX_RECORD_BYTES + 1)
                    if not raw_line:
                        break
                    record = raw_line[:-1] if raw_line.endswith(b"\n") else raw_line
                    if record.endswith(b"\r"):
                        record = record[:-1]
                    if len(record) > MAX_RECORD_BYTES:
                        outcome.input_errors += 1
                        while raw_line and not raw_line.endswith(b"\n"):
                            raw_line = handle.readline(MAX_RECORD_BYTES + 1)
                        continue
                    if not record:
                        outcome.input_errors += 1
                        continue
                    outcome.records_scanned += 1
                    outcome.bytes_scanned += len(raw_line)
                    try:
                        names = extractor(record)
                    except JsonInputError:
                        outcome.input_errors += 1
                        continue
                    outcome.primary_counts.update(names)
                    if entry in sensitivity:
                        outcome.sensitivity_counts.update(names)
        except OSError:
            outcome.input_errors += 1
    return outcome


def scan_claude(files: Sequence[Any], sensitivity_files: Sequence[Any] = ()) -> ScanOutcome:
    """Count only verified Claude event fields without decoding record bodies."""
    return _scan_records(files, sensitivity_files, _extract_claude_record)


def scan_codex(files: Sequence[Any], sensitivity_files: Sequence[Any] = ()) -> ScanOutcome:
    """Count only verified Codex read_file paths without decoding arguments objects."""
    return _scan_records(files, sensitivity_files, _extract_codex_record)


def _discover_jsonl_files(root: Path, root_directory: BoundDirectory) -> Tuple[List[Tuple[datetime, BoundTranscript]], int]:
    """Discover only non-link JSONL sources whose queued ancestors stay bound."""
    candidates: List[Tuple[datetime, BoundTranscript]] = []
    input_errors = 0
    pending = [root_directory]
    while pending:
        directory = pending.pop()
        try:
            directory_fd = _open_bound_directory(root, directory)
        except OSError:
            input_errors += 1
            continue
        try:
            scan_fd = os.dup(directory_fd)
        except OSError:
            input_errors += 1
            try:
                os.close(directory_fd)
            except OSError:
                pass
            continue
        try:
            with os.scandir(scan_fd) as entries:
                for entry in entries:
                    try:
                        entry_stat = entry.stat(follow_symlinks=False)
                        entry_identity = _source_identity(entry_stat)
                    except (OSError, TypeError, ValueError):
                        input_errors += 1
                        continue
                    if entry_identity.file_type == stat.S_IFLNK:
                        input_errors += 1
                    elif entry_identity.file_type == stat.S_IFDIR:
                        pending.append(
                            BoundDirectory(
                                directory.parts + (entry.name,),
                                directory.identities + (entry_identity,),
                            )
                        )
                    elif entry_identity.file_type == stat.S_IFREG and entry.name.endswith(".jsonl"):
                        try:
                            observed = datetime.fromtimestamp(entry_stat.st_mtime, tz=UTC)
                        except (OSError, OverflowError, ValueError):
                            input_errors += 1
                            continue
                        candidates.append(
                            (
                                observed,
                                BoundTranscript(root, directory, entry.name, entry_identity),
                            )
                        )
        except (OSError, TypeError, ValueError, NotImplementedError):
            input_errors += 1
        finally:
            try:
                os.close(scan_fd)
            except OSError:
                pass
            try:
                os.close(directory_fd)
            except OSError:
                input_errors += 1
    return candidates, input_errors


def transcript_window(root: Path, as_of: datetime, primary_start: datetime, sensitivity_start: datetime) -> Tuple[Dict[str, Any], List[BoundTranscript], List[BoundTranscript]]:
    """Return only aggregate availability metadata plus file handles for scanning."""
    input_errors = 0
    candidates: List[Tuple[datetime, BoundTranscript]] = []
    try:
        root_directory = _snapshot_root(root)
        available = True
    except OSError:
        available = False
        input_errors += 1
    if available:
        discovered, discovery_errors = _discover_jsonl_files(root, root_directory)
        input_errors += discovery_errors
        candidates = [(observed, transcript) for observed, transcript in discovered if observed <= as_of]

    candidates.sort(key=lambda item: item[0])
    fingerprint = hashlib.sha256()
    for observed, transcript in candidates:
        fingerprint.update(str(int(observed.timestamp() * 1_000_000_000)).encode("ascii"))
        fingerprint.update(b"\0")
        fingerprint.update("/".join(transcript.parent.parts + (transcript.name,)).encode("utf-8"))
        fingerprint.update(b"\0")
        fingerprint.update(str(transcript.identity.device).encode("ascii"))
        fingerprint.update(b":")
        fingerprint.update(str(transcript.identity.inode).encode("ascii"))
        fingerprint.update(b":")
        fingerprint.update(str(transcript.identity.size).encode("ascii"))
        fingerprint.update(b"\0")
    earliest = candidates[0][0] if candidates else None
    primary = [transcript for observed, transcript in candidates if observed >= primary_start]
    sensitivity = [transcript for observed, transcript in candidates if observed >= sensitivity_start]
    metadata = {
        "available": bool(available and input_errors == 0),
        "files_available": len(candidates),
        "files_scanned_primary": len(primary),
        "files_scanned_sensitivity": len(sensitivity),
        "earliest_available": timestamp_text(earliest),
        "input_errors": input_errors,
        "input_complete": input_errors == 0,
        "coverage_complete": bool(
            available and input_errors == 0 and earliest is not None and earliest <= primary_start
        ),
        "source_fingerprint": fingerprint.hexdigest(),
    }
    return metadata, primary, sensitivity


def _apply_scan_coverage(metadata: Mapping[str, Any], scan: ScanOutcome) -> Dict[str, Any]:
    """Turn raw-read failures into aggregate-only availability and coverage holds."""
    updated = dict(metadata)
    input_errors = int(updated["input_errors"]) + scan.input_errors
    input_complete = input_errors == 0
    updated["input_errors"] = input_errors
    updated["input_complete"] = input_complete
    updated["available"] = bool(updated["available"] and input_complete)
    updated["coverage_complete"] = bool(updated["coverage_complete"] and input_complete)
    updated["records_scanned"] = scan.records_scanned
    updated["bytes_scanned"] = scan.bytes_scanned
    updated["checkpoint_hit"] = scan.cache_hit
    return updated


def _checkpoint_key(
    catalog: Mapping[str, Mapping[str, str]],
    as_of: datetime,
    since_days: int,
    sensitivity_days: int,
    codex_event_schema: str,
) -> Dict[str, Any]:
    catalog_hash = hashlib.sha256("\0".join(sorted(catalog)).encode("utf-8")).hexdigest()
    return {
        "catalog_hash": catalog_hash,
        "as_of": timestamp_text(as_of),
        "primary_days": since_days,
        "sensitivity_days": sensitivity_days,
        "codex_event_schema": codex_event_schema,
    }


def _load_checkpoint(path: Optional[Path], key: Mapping[str, Any]) -> Dict[str, Any]:
    if path is None:
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(payload, dict) or payload.get("schema_version") != 1 or payload.get("key") != dict(key):
        return {}
    runtimes = payload.get("runtimes")
    return runtimes if isinstance(runtimes, dict) else {}


def _cached_scan(
    runtime_cache: Any, fingerprint: str, catalog: Mapping[str, Mapping[str, str]]
) -> Optional[ScanOutcome]:
    if not isinstance(runtime_cache, dict) or runtime_cache.get("source_fingerprint") != fingerprint:
        return None
    primary = runtime_cache.get("primary_counts")
    sensitivity = runtime_cache.get("sensitivity_counts")
    if not isinstance(primary, dict) or not isinstance(sensitivity, dict):
        return None
    allowed = set(catalog)
    for counts in (primary, sensitivity):
        if any(name not in allowed or not isinstance(value, int) or value < 0 for name, value in counts.items()):
            return None
    return ScanOutcome(Counter(primary), Counter(sensitivity), cache_hit=True)


def _checkpoint_runtime(fingerprint: str, scan: ScanOutcome) -> Dict[str, Any]:
    return {
        "source_fingerprint": fingerprint,
        "primary_counts": dict(sorted(scan.primary_counts.items())),
        "sensitivity_counts": dict(sorted(scan.sensitivity_counts.items())),
    }


def _write_checkpoint(path: Optional[Path], key: Mapping[str, Any], runtimes: Mapping[str, Any]) -> None:
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps({"schema_version": 1, "key": dict(key), "runtimes": runtimes}, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, path)


def source_freshness(repo_root: Path, source: Optional[str], ownership: str, primary_start: datetime) -> str:
    """Classify age conservatively; unknown history is protected, never actionable."""
    source_path = safe_source_path(repo_root, source)
    if source_path is None or not (source_path / "SKILL.md").is_file() or ownership == "submodule":
        return "unknown-age"
    try:
        inside_repo = subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
        if inside_repo.returncode != 0 or inside_repo.stdout.strip() != "true":
            return "unknown-age"
        relative = source_path.relative_to(repo_root)
        history = subprocess.run(
            ["git", "-C", str(repo_root), "log", "--diff-filter=A", "--follow", "--format=%ct", "--", str(relative)],
            capture_output=True,
            text=True,
            timeout=30,
            check=False,
        )
    except (OSError, subprocess.SubprocessError, ValueError):
        return "unknown-age"
    if history.returncode != 0:
        return "unknown-age"
    timestamps = history.stdout.split()
    if not timestamps:
        return "new"
    try:
        first_added = datetime.fromtimestamp(int(timestamps[-1]), tz=UTC)
    except ValueError:
        return "unknown-age"
    return "new" if first_added >= primary_start else "established"


def counts_for(
    name: str, claude: Counter, codex: Counter, claude_available: bool, codex_available: bool
) -> Dict[str, Optional[int]]:
    claude_count = int(claude[name]) if claude_available else None
    codex_count = int(codex[name]) if codex_available else None
    total = claude_count + codex_count if claude_count is not None and codex_count is not None else None
    return {"claude": claude_count, "codex": codex_count, "total": total}


def disposition_for(name: str, resolved: bool, coverage_complete: bool, freshness: str, primary_count: int) -> Tuple[str, Optional[str]]:
    """Return a review-only disposition; this function never authorizes catalog changes."""
    if name == "using-superpowers":
        return "measurement-limited", "native-limited"
    if not resolved:
        return "insufficient-evidence", "not-in-current-catalog"
    if not coverage_complete:
        return "insufficient-evidence", "incomplete-history"
    if freshness in {"new", "unknown-age"}:
        return "retain", freshness
    if primary_count >= 3:
        return "retain", None
    if primary_count >= 1:
        return "marginal-review", "one-or-two-recorded-uses"
    return "candidate-follow-up", "owner-review-before-any-catalog-change"


def build_report(
    repo_root: Path,
    catalog: Mapping[str, Mapping[str, str]],
    claude_dir: Path,
    codex_dir: Path,
    as_of: datetime,
    since_days: int,
    sensitivity_days: int,
    checkpoint_path: Optional[Path] = None,
    codex_event_schema: str = "structured-skill-read-v1",
) -> Dict[str, Any]:
    primary_start = as_of - timedelta(days=since_days)
    sensitivity_start = as_of - timedelta(days=sensitivity_days)
    claude_coverage, claude_primary, claude_sensitivity = transcript_window(
        claude_dir, as_of, primary_start, sensitivity_start
    )
    codex_coverage, codex_primary, codex_sensitivity = transcript_window(
        codex_dir, as_of, primary_start, sensitivity_start
    )
    checkpoint_key = _checkpoint_key(
        catalog, as_of, since_days, sensitivity_days, codex_event_schema
    )
    checkpoint = _load_checkpoint(checkpoint_path, checkpoint_key)
    claude_fingerprint = str(claude_coverage.pop("source_fingerprint"))
    codex_fingerprint = str(codex_coverage.pop("source_fingerprint"))
    claude_scan = _cached_scan(checkpoint.get("claude"), claude_fingerprint, catalog)
    if claude_scan is None:
        claude_scan = scan_claude(claude_primary, claude_sensitivity)
    if codex_event_schema == "structured-skill-read-v1":
        codex_scan = _cached_scan(checkpoint.get("codex"), codex_fingerprint, catalog)
        if codex_scan is None:
            codex_scan = scan_codex(codex_primary, codex_sensitivity)
    else:
        codex_scan = ScanOutcome(Counter(), Counter())
    claude_coverage = _apply_scan_coverage(claude_coverage, claude_scan)
    codex_coverage = _apply_scan_coverage(codex_coverage, codex_scan)
    event_schema = {
        "claude": {"name": "claude-structured-skill-v1", "available": True},
        "codex": {
            "name": codex_event_schema,
            "available": codex_event_schema == "structured-skill-read-v1",
        },
    }
    source_coverage_complete = bool(
        claude_coverage["coverage_complete"] and codex_coverage["coverage_complete"]
    )
    event_schema_complete = bool(
        event_schema["claude"]["available"] and event_schema["codex"]["available"]
    )
    coverage_complete = bool(source_coverage_complete and event_schema_complete)
    claude_primary_counts = claude_scan.primary_counts
    codex_primary_counts = codex_scan.primary_counts
    claude_sensitivity_counts = claude_scan.sensitivity_counts
    codex_sensitivity_counts = codex_scan.sensitivity_counts

    if claude_scan.input_complete and codex_scan.input_complete:
        _write_checkpoint(
            checkpoint_path,
            checkpoint_key,
            {
                "claude": _checkpoint_runtime(claude_fingerprint, claude_scan),
                "codex": _checkpoint_runtime(codex_fingerprint, codex_scan),
            },
        )

    matrix: List[Dict[str, Any]] = []
    for name, entry in sorted(catalog.items()):
        resolved = True
        source = entry["source"]
        ownership = entry["ownership"]
        trigger, overlap = PROFILE_RATIONALE.get(
            name,
            (
                "Current catalog entry supplied by the linker manifest.",
                "No maintained overlap rationale; requires owner judgment if usage is marginal.",
            ),
        )
        skill_dir = safe_source_path(repo_root, source)
        freshness = source_freshness(repo_root, source, ownership, primary_start)
        primary_counts = counts_for(
            name,
            claude_primary_counts,
            codex_primary_counts,
            bool(event_schema["claude"]["available"]),
            bool(event_schema["codex"]["available"]),
        )
        sensitivity_counts = counts_for(
            name,
            claude_sensitivity_counts,
            codex_sensitivity_counts,
            bool(event_schema["claude"]["available"]),
            bool(event_schema["codex"]["available"]),
        )
        disposition, protection_reason = disposition_for(
            name, resolved, coverage_complete, freshness, int(primary_counts["total"] or 0)
        )
        row: Dict[str, Any] = {
            "name": name,
            "catalog_status": "resolved" if resolved else "not-in-current-catalog",
            "source": source,
            "ownership": ownership,
            "catalog_token_cost": frontmatter_tokens(skill_dir),
            "freshness": freshness,
            "counts": {"primary": primary_counts, "sensitivity": sensitivity_counts},
            "trigger_rationale": trigger,
            "overlap_rationale": overlap,
            "disposition": disposition,
        }
        if protection_reason is not None:
            row["protection_reason"] = protection_reason
        matrix.append(row)

    return {
        "schema_version": 1,
        "as_of": timestamp_text(as_of),
        "windows": {"primary_days": since_days, "sensitivity_days": sensitivity_days},
        "coverage": {
            "complete": coverage_complete,
            "source_complete": source_coverage_complete,
            "event_schema_complete": event_schema_complete,
            "claude": claude_coverage,
            "codex": codex_coverage,
            "event_schema": event_schema,
        },
        "measurement_policy": {
            "event_types": ["claude-skill", "claude-slash", "codex-structured-skill-read"],
            "transcript_retention": "aggregate-counters-and-source-fingerprints-only",
            "catalog_change_authorization": "none",
        },
        "decision_matrix": matrix,
    }


def render_text(report: Mapping[str, Any]) -> str:
    """Render the same aggregate-only report without emitting filesystem details."""
    lines = [
        "Skill usage audit (measurement only)",
        "as-of: {0}".format(report["as_of"]),
        "coverage complete: {0}".format("yes" if report["coverage"]["complete"] else "no"),
        "",
        "PRIMARY  SENSITIVITY  DISPOSITION           SKILL",
    ]
    for row in report["decision_matrix"]:
        lines.append(
            "{0:>7}  {1:>11}  {2:<20}  {3}".format(
                "n/a" if row["counts"]["primary"]["total"] is None else row["counts"]["primary"]["total"],
                "n/a" if row["counts"]["sensitivity"]["total"] is None else row["counts"]["sensitivity"]["total"],
                row["disposition"],
                row["name"],
            )
        )
    lines.extend(
        [
            "",
            "This is a measurement-only decision matrix; no catalog change is authorized.",
        ]
    )
    return "\n".join(lines)


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=default_repo_root())
    parser.add_argument("--catalog-manifest", type=Path)
    parser.add_argument("--skills-root", type=Path, help=argparse.SUPPRESS)
    parser.add_argument("--claude-dir", type=Path, default=Path.home() / ".claude/projects")
    parser.add_argument("--codex-dir", type=Path, default=Path.home() / ".codex/sessions")
    parser.add_argument("--as-of", type=parse_utc_timestamp, required=True)
    parser.add_argument("--since-days", type=int, default=90)
    parser.add_argument("--sensitivity-days", type=int, default=30)
    parser.add_argument(
        "--codex-event-schema",
        choices=("unavailable", "structured-skill-read-v1"),
        default="unavailable",
        help="Codex schema contract; unavailable fails counts closed instead of reporting zero",
    )
    parser.add_argument(
        "--checkpoint",
        type=Path,
        help="privacy-preserving aggregate checkpoint; unchanged sources are not reread",
    )
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    if args.since_days <= 0 or args.sensitivity_days <= 0:
        parser.error("window lengths must be positive")
    if args.sensitivity_days > args.since_days:
        parser.error("--sensitivity-days cannot exceed --since-days")
    if args.skills_root is not None:
        inferred_root = args.skills_root.resolve().parent
        if args.repo_root.resolve() != default_repo_root().resolve() and args.repo_root.resolve() != inferred_root:
            parser.error("--skills-root must belong to --repo-root")
        args.repo_root = inferred_root
    return args


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    repo_root = args.repo_root.resolve()
    try:
        catalog = load_catalog_manifest(repo_root, args.catalog_manifest)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    report = build_report(
        repo_root,
        catalog,
        args.claude_dir,
        args.codex_dir,
        args.as_of,
        args.since_days,
        args.sensitivity_days,
        args.checkpoint,
        args.codex_event_schema,
    )
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_text(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
