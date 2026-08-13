# /// script
# requires-python = ">=3.10"
# ///

"""In-namespace execution helper for the candidate-0003 Claude probe.

This helper has no host mount except its own read-only code directory. It never
reads a mock request, target stdout, target stderr, or a content-bearing JSON
field. It emits exactly one schema-limited structural summary to stdout.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
import shutil
import signal
import socket
import subprocess
import sys
import threading
import time
from typing import Mapping


PINNED_VERSION = "2.1.227"
PINNED_SHA256 = "6832dc3f1797b890b71116e5f2dbbf9a83fd3d0498c235b4b0f9cd0e6e499ad6"
SYNTHETIC_HOME = Path("/sandbox-home")
SYNTHETIC_WORK = Path("/sandbox-work")
SYNTHETIC_OUTPUT = Path("/sandbox-output")
SYNTHETIC_TARGET = "/opt/claude/claude"
MOCK_PORT = 18080
MAX_RECORD_BYTES = 1 << 20
SAFE_PROJECTED_PATH_CLASSES = (
    "type",
    "session-id",
    "request-id",
    "timestamp",
    "message-id",
    "model",
    "usage-input-tokens",
    "usage-cache-creation-input-tokens",
    "usage-cache-read-input-tokens",
    "usage-output-tokens",
)
SAFE_TARGET_ENVIRONMENT = {
    "HOME": "/sandbox-home",
    "CLAUDE_CONFIG_DIR": "/sandbox-home/.claude",
    "ANTHROPIC_CONFIG_DIR": "/sandbox-home/.claude",
    "ANTHROPIC_API_KEY": "synthetic-loopback-probe-key",
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:18080",
    "PATH": "/bin:/usr/bin",
}
NESTED_READ_ONLY_PATHS = (
    "/bin",
    "/lib",
    "/lib64",
    "/usr/bin",
    "/usr/lib",
    "/usr/lib64",
    "/opt",
)
NESTED_WRITABLE_SYNTHETIC_PATHS = (
    "/sandbox-home",
    "/sandbox-work",
    "/sandbox-output",
)
_KNOWN_STRUCTURAL_KEYS = (
    b"type",
    b"sessionId",
    b"requestId",
    b"timestamp",
    b"message",
    b"id",
    b"model",
    b"usage",
    b"input_tokens",
    b"cache_creation_input_tokens",
    b"cache_read_input_tokens",
    b"output_tokens",
)
_SAFE_STRING_PATHS = frozenset(
    {
        ("type",),
        ("sessionId",),
        ("requestId",),
        ("timestamp",),
        ("message", "id"),
        ("message", "model"),
    }
)
_SAFE_INTEGER_PATHS = frozenset(
    {
        ("message", "usage", "input_tokens"),
        ("message", "usage", "cache_creation_input_tokens"),
        ("message", "usage", "cache_read_input_tokens"),
        ("message", "usage", "output_tokens"),
    }
)
_PATH_PREFIXES = frozenset(
    path[:index] for path in (*_SAFE_STRING_PATHS, *_SAFE_INTEGER_PATHS) for index in range(1, len(path) + 1)
)


class SafeParseError(ValueError):
    """A structural-only parse could not establish a complete record."""


@dataclass(frozen=True)
class Observation:
    native_pair: tuple[str, str]
    timestamp: str
    message_id: str
    model: str
    amounts: tuple[int, int, int, int]


@dataclass(frozen=True)
class InspectionAnalysis:
    complete_usage_observation_count: int
    malformed_record_count: int
    incomplete_tail_count: int
    stream_count: int
    same_native_pair_group_count: int
    progressive_same_pair_group_count: int
    exact_replay_group_count: int
    changed_timestamp_group_count: int
    decreasing_group_count: int
    nonconforming_reuse_group_count: int


class StructuralJsonScanner:
    """Walk JSON syntax while decoding values only at the fixed safe paths."""

    def __init__(self, raw: bytes) -> None:
        self.raw = raw
        self.index = 0
        self.values: dict[tuple[str, ...], object] = {}

    def parse(self) -> dict[tuple[str, ...], object]:
        self._skip_whitespace()
        self._parse_value(())
        self._skip_whitespace()
        if self.index != len(self.raw):
            raise SafeParseError("trailing-json")
        return self.values

    def _skip_whitespace(self) -> None:
        while self.index < len(self.raw) and self.raw[self.index] in b" \t\r\n":
            self.index += 1

    def _parse_value(self, path: tuple[str, ...] | None) -> None:
        self._skip_whitespace()
        if self.index >= len(self.raw):
            raise SafeParseError("truncated-json")
        if path is None:
            self._skip_value()
            return
        current = self.raw[self.index]
        if current == ord("{"):
            self._parse_object(path)
            return
        if current == ord("["):
            self._parse_array(path)
            return
        if path in _SAFE_STRING_PATHS:
            self.values[path] = self._decode_safe_string()
            return
        if path in _SAFE_INTEGER_PATHS:
            self.values[path] = self._decode_safe_integer()
            return
        self._skip_scalar_or_container()

    def _parse_object(self, path: tuple[str, ...]) -> None:
        self.index += 1
        self._skip_whitespace()
        if self._consume(ord("}")):
            return
        while True:
            key = self._read_structural_key()
            self._skip_whitespace()
            self._expect(ord(":"))
            child_path = _next_safe_path(path, key)
            self._parse_value(child_path)
            self._skip_whitespace()
            if self._consume(ord("}")):
                return
            self._expect(ord(","))

    def _parse_array(self, path: tuple[str, ...]) -> None:
        self.index += 1
        self._skip_whitespace()
        if self._consume(ord("]")):
            return
        while True:
            self._skip_value()
            self._skip_whitespace()
            if self._consume(ord("]")):
                return
            self._expect(ord(","))

    def _read_structural_key(self) -> str | None:
        start, end, escaped = self._scan_string_bounds()
        if escaped:
            return None
        for known in _KNOWN_STRUCTURAL_KEYS:
            if end - start == len(known) and all(self.raw[start + offset] == byte for offset, byte in enumerate(known)):
                return known.decode("ascii")
        return None

    def _decode_safe_string(self) -> str:
        string_start = self.index
        _, _, _ = self._scan_string_bounds()
        literal = self.raw[string_start : self.index]
        try:
            value = json.loads(literal)
        except (UnicodeDecodeError, json.JSONDecodeError) as error:
            raise SafeParseError("invalid-safe-string") from error
        if not isinstance(value, str):
            raise SafeParseError("expected-safe-string")
        return value

    def _decode_safe_integer(self) -> int:
        start = self.index
        while self.index < len(self.raw) and self.raw[self.index] in b"0123456789":
            self.index += 1
        if self.index == start:
            raise SafeParseError("expected-safe-integer")
        return int(self.raw[start : self.index])

    def _scan_string_bounds(self) -> tuple[int, int, bool]:
        self._expect(ord('"'))
        start = self.index
        escaped = False
        has_escape = False
        while self.index < len(self.raw):
            current = self.raw[self.index]
            self.index += 1
            if escaped:
                escaped = False
                continue
            if current == ord("\\"):
                escaped = True
                has_escape = True
                continue
            if current == ord('"'):
                return start, self.index - 1, has_escape
            if current < 0x20:
                raise SafeParseError("invalid-string")
        raise SafeParseError("unterminated-string")

    def _skip_value(self) -> None:
        self._skip_whitespace()
        if self.index >= len(self.raw):
            raise SafeParseError("truncated-json")
        current = self.raw[self.index]
        if current == ord('"'):
            self._scan_string_bounds()
            return
        if current == ord("{"):
            self.index += 1
            self._skip_whitespace()
            if self._consume(ord("}")):
                return
            while True:
                self._scan_string_bounds()
                self._expect(ord(":"))
                self._skip_value()
                self._skip_whitespace()
                if self._consume(ord("}")):
                    return
                self._expect(ord(","))
        if current == ord("["):
            self.index += 1
            self._skip_whitespace()
            if self._consume(ord("]")):
                return
            while True:
                self._skip_value()
                self._skip_whitespace()
                if self._consume(ord("]")):
                    return
                self._expect(ord(","))
        else:
            scalar_start = self.index
            while self.index < len(self.raw) and self.raw[self.index] not in b" \t\r\n,]}":
                self.index += 1
            if scalar_start == self.index:
                raise SafeParseError("invalid-scalar")

    def _expect(self, expected: int) -> None:
        self._skip_whitespace()
        if self.index >= len(self.raw) or self.raw[self.index] != expected:
            raise SafeParseError("invalid-json")
        self.index += 1

    def _consume(self, expected: int) -> bool:
        self._skip_whitespace()
        if self.index < len(self.raw) and self.raw[self.index] == expected:
            self.index += 1
            return True
        return False


def _next_safe_path(parent: tuple[str, ...], key: str | None) -> tuple[str, ...] | None:
    if key is None:
        return None
    candidate = (*parent, key)
    return candidate if candidate in _PATH_PREFIXES else None


def _observation_from_values(values: Mapping[tuple[str, ...], object]) -> Observation | None:
    if values.get(("type",)) != "assistant":
        return None
    required = _SAFE_STRING_PATHS | _SAFE_INTEGER_PATHS
    if not required.issubset(values):
        raise SafeParseError("missing-safe-field")
    safe_strings = (
        values[("sessionId",)],
        values[("requestId",)],
        values[("timestamp",)],
        values[("message", "id")],
        values[("message", "model")],
    )
    if not all(isinstance(value, str) and value for value in safe_strings):
        raise SafeParseError("wrong-safe-string-type")
    amounts = tuple(values[path] for path in sorted(_SAFE_INTEGER_PATHS))
    if not all(isinstance(value, int) and value >= 0 for value in amounts):
        raise SafeParseError("wrong-safe-integer-type")
    return Observation(
        native_pair=(safe_strings[0], safe_strings[1]),
        timestamp=safe_strings[2],
        message_id=safe_strings[3],
        model=safe_strings[4],
        amounts=amounts,
    )


def _consume_file(path: Path) -> tuple[list[Observation], int, int]:
    observations: list[Observation] = []
    malformed = 0
    incomplete = 0
    with path.open("rb") as source:
        while True:
            line = source.readline(MAX_RECORD_BYTES + 1)
            if not line:
                break
            if not line.endswith(b"\n"):
                if len(line) <= MAX_RECORD_BYTES:
                    incomplete += 1
                    break
                malformed += 1
                while line and not line.endswith(b"\n"):
                    line = source.readline(MAX_RECORD_BYTES + 1)
                continue
            try:
                observation = _observation_from_values(StructuralJsonScanner(line).parse())
            except SafeParseError:
                malformed += 1
                continue
            if observation is not None:
                observations.append(observation)
    return observations, malformed, incomplete


def _iter_jsonl_files(root: Path):
    if not root.is_dir():
        return
    for current_root, directories, filenames in os.walk(root, followlinks=False):
        directories[:] = [name for name in directories if not (Path(current_root) / name).is_symlink()]
        for filename in filenames:
            candidate = Path(current_root) / filename
            if filename.endswith(".jsonl") and candidate.is_file() and not candidate.is_symlink():
                yield candidate


def inspect_virtual_home(home: Path) -> InspectionAnalysis:
    streams: list[list[Observation]] = []
    malformed = 0
    incomplete = 0
    for jsonl_file in _iter_jsonl_files(home / ".claude"):
        observations, file_malformed, file_incomplete = _consume_file(jsonl_file)
        streams.append(observations)
        malformed += file_malformed
        incomplete += file_incomplete

    same_pair_groups = 0
    progressive_groups = 0
    exact_replay_groups = 0
    changed_timestamp_groups = 0
    decreasing_groups = 0
    nonconforming_reuse_groups = 0
    for stream in streams:
        grouped: dict[tuple[str, str], list[Observation]] = {}
        for observation in stream:
            grouped.setdefault(observation.native_pair, []).append(observation)
        for records in grouped.values():
            if len(records) < 2:
                continue
            same_pair_groups += 1
            if _is_exact_replay(records):
                exact_replay_groups += 1
                continue
            timestamp_changed = _all_neighbor_timestamps_changed(records)
            same_message_and_model = _same_message_and_model(records)
            directions = _amount_directions(records)
            if timestamp_changed:
                changed_timestamp_groups += 1
            if "decrease" in directions:
                decreasing_groups += 1
            if not same_message_and_model:
                nonconforming_reuse_groups += 1
            if timestamp_changed and same_message_and_model and directions and set(directions) <= {"same", "increase"} and "increase" in directions:
                progressive_groups += 1
    return InspectionAnalysis(
        complete_usage_observation_count=sum(len(stream) for stream in streams),
        malformed_record_count=malformed,
        incomplete_tail_count=incomplete,
        stream_count=len(streams),
        same_native_pair_group_count=same_pair_groups,
        progressive_same_pair_group_count=progressive_groups,
        exact_replay_group_count=exact_replay_groups,
        changed_timestamp_group_count=changed_timestamp_groups,
        decreasing_group_count=decreasing_groups,
        nonconforming_reuse_group_count=nonconforming_reuse_groups,
    )


def _is_exact_replay(records: list[Observation]) -> bool:
    first = records[0]
    return all(record == first for record in records[1:])


def _all_neighbor_timestamps_changed(records: list[Observation]) -> bool:
    return all(left.timestamp != right.timestamp for left, right in zip(records, records[1:]))


def _same_message_and_model(records: list[Observation]) -> bool:
    first = records[0]
    return all(record.message_id == first.message_id and record.model == first.model for record in records[1:])


def _amount_directions(records: list[Observation]) -> tuple[str, ...]:
    directions: list[str] = []
    for left, right in zip(records, records[1:]):
        if any(new < old for old, new in zip(left.amounts, right.amounts)):
            directions.append("decrease")
        elif any(new > old for old, new in zip(left.amounts, right.amounts)):
            directions.append("increase")
        else:
            directions.append("same")
    return tuple(directions)


class LoopbackOnlyMock:
    """A synthetic reply-only loopback server that never reads client bytes."""

    def __init__(self, port: int = 0) -> None:
        self.port = port
        self._listener: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._closed = threading.Event()
        self._connection_event = threading.Event()
        self._lock = threading.Lock()
        self.connection_count = 0
        self.nonloopback_connection_count = 0

    def start(self) -> None:
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind(("127.0.0.1", self.port))
        listener.listen()
        listener.settimeout(0.1)
        self.port = listener.getsockname()[1]
        self._listener = listener
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._thread.start()

    def _serve(self) -> None:
        while not self._closed.is_set():
            assert self._listener is not None
            try:
                connection, address = self._listener.accept()
            except TimeoutError:
                continue
            except OSError:
                return
            try:
                with self._lock:
                    self.connection_count += 1
                    if address[0] != "127.0.0.1":
                        self.nonloopback_connection_count += 1
                    self._connection_event.set()
                # No recv call is permitted: request headers and body remain unread.
                try:
                    connection.sendall(_synthetic_stream_reply())
                except OSError:
                    pass
            finally:
                connection.close()

    def wait_for_connections(self, count: int, timeout: float = 2.0) -> bool:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            with self._lock:
                if self.connection_count >= count:
                    return True
            self._connection_event.wait(0.02)
        with self._lock:
            return self.connection_count >= count

    def close(self) -> None:
        self._closed.set()
        if self._listener is not None:
            self._listener.close()
        if self._thread is not None:
            self._thread.join(timeout=1)


def _synthetic_stream_reply() -> bytes:
    # This is code-owned mock output, not captured target/provider output.
    payload = (
        b"event: message_start\n"
        b'data: {"type":"message_start","message":{"id":"synthetic-message","type":"message","role":"assistant","content":[],"model":"synthetic-model","stop_reason":null,"stop_sequence":null,"usage":{"input_tokens":1,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0}}}\n\n'
        b"event: content_block_start\n"
        b'data: {"type":"content_block_start","index":0,"content_block":{"type":"text","text":""}}\n\n'
        b"event: content_block_stop\n"
        b'data: {"type":"content_block_stop","index":0}\n\n'
        b"event: message_delta\n"
        b'data: {"type":"message_delta","delta":{"stop_reason":"end_turn","stop_sequence":null},"usage":{"output_tokens":1}}\n\n'
        b"event: message_stop\n"
        b'data: {"type":"message_stop"}\n\n'
    )
    return (
        b"HTTP/1.1 200 OK\r\n"
        b"Content-Type: text/event-stream\r\n"
        b"Connection: close\r\n\r\n"
        + payload
    )


def run_loopback_canary(port: int) -> None:
    with socket.create_connection(("127.0.0.1", port), timeout=2):
        pass


def _default_route_count() -> int:
    route_file = Path("/proc/net/route")
    if not route_file.is_file():
        return 1
    count = 0
    with route_file.open("rt", encoding="ascii", errors="strict") as routes:
        next(routes, None)
        for row in routes:
            cells = row.split()
            if len(cells) >= 2 and cells[1] == "00000000":
                count += 1
    return count


def network_state_is_safe(interface_names: tuple[str, ...], default_route_count: int) -> bool:
    return set(interface_names) == {"lo"} and default_route_count == 0


def _prepare_loopback_network() -> tuple[tuple[str, ...], int]:
    command = subprocess.run(
        ["/bin/ip", "link", "set", "lo", "up"],
        check=False,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        env={"PATH": "/bin:/usr/bin"},
    )
    if command.returncode != 0:
        return (), 1
    names = tuple(name for _, name in socket.if_nameindex())
    return names, _default_route_count()


def make_safe_summary(
    analysis: InspectionAnalysis,
    *,
    canary_connections: int,
    target_started_count: int = 1,
    target_completed_count: int = 1,
    nonloopback_interface_count: int = 0,
    default_route_count: int = 0,
    nonloopback_connection_count: int = 0,
    negative_oracles_complete: bool = False,
) -> dict[str, object]:
    controls_complete = (
        target_started_count == 1
        and target_completed_count == 1
        and canary_connections >= 1
        and nonloopback_interface_count == 0
        and default_route_count == 0
        and nonloopback_connection_count == 0
    )
    if controls_complete and analysis.progressive_same_pair_group_count >= 1:
        disposition = "confirmed-contract-gap"
    elif controls_complete and negative_oracles_complete:
        disposition = "confirmed-current-contract"
    else:
        disposition = "unresolved"
    return {
        "schema": "claude-progressive-probe-summary@1",
        "build_pin": {"version": PINNED_VERSION, "sha256": PINNED_SHA256},
        "path_classes": {
            "target": "synthetic-executable",
            "probe_code": "read-only-candidate-code",
            "home": "tmpfs-synthetic",
            "work": "tmpfs-synthetic",
            "output": "tmpfs-only",
            "network": "loopback-only",
        },
        "type_assertions": {
            "structural_projection": "explicit-safe-fields-only",
            "complete_usage_observation": "assistant-with-required-safe-types",
        },
        "counts": {
            "target_started": target_started_count,
            "target_completed": target_completed_count,
            "loopback_mock_connections": canary_connections,
            "complete_usage_observations": analysis.complete_usage_observation_count,
            "malformed_records": analysis.malformed_record_count,
            "incomplete_tails": analysis.incomplete_tail_count,
            "same_native_pair_groups": analysis.same_native_pair_group_count,
            "progressive_same_pair_groups": analysis.progressive_same_pair_group_count,
        },
        "equality_assertions": {
            "exact_replay_groups": analysis.exact_replay_group_count,
            "changed_timestamp_groups": analysis.changed_timestamp_group_count,
            "nonconforming_reuse_groups": analysis.nonconforming_reuse_group_count,
        },
        "direction_assertions": {
            "monotone-increase-groups": analysis.progressive_same_pair_group_count,
            "decreasing-groups": analysis.decreasing_group_count,
        },
        "control_totals": {
            "loopback_canary_connections": 1 if canary_connections >= 1 else 0,
            "nonloopback_interface_count": nonloopback_interface_count,
            "default_route_count": default_route_count,
            "nonloopback_connection_count": nonloopback_connection_count,
        },
        "disposition": disposition,
    }


def _nested_target_argv(nested_bwrap: str) -> list[str]:
    args = [
        nested_bwrap,
        "--die-with-parent",
        "--new-session",
        "--unshare-user",
        "--unshare-pid",
        "--uid",
        "1000",
        "--gid",
        "1000",
        "--clearenv",
        "--proc",
        "/proc",
        "--dev",
        "/dev",
    ]
    for path in NESTED_READ_ONLY_PATHS:
        args.extend(["--ro-bind", path, path])
    for path in NESTED_WRITABLE_SYNTHETIC_PATHS:
        args.extend(["--bind", path, path])
    for name, value in SAFE_TARGET_ENVIRONMENT.items():
        args.extend(["--setenv", name, value])
    return [
        *args,
        "--chdir",
        str(SYNTHETIC_WORK),
        "--",
        SYNTHETIC_TARGET,
        "-p",
        "",
        "--output-format",
        "json",
        "--permission-mode",
        "plan",
    ]


def _run_target() -> tuple[int, int]:
    nested_bwrap = shutil.which("bwrap")
    if nested_bwrap is None:
        raise SafeParseError("nested-bubblewrap-missing")
    process = subprocess.Popen(
        _nested_target_argv(nested_bwrap),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        cwd=SYNTHETIC_WORK,
        env=dict(SAFE_TARGET_ENVIRONMENT),
        start_new_session=True,
        close_fds=True,
    )
    try:
        process.wait(timeout=60)
    except subprocess.TimeoutExpired:
        os.killpg(process.pid, signal.SIGKILL)
        process.wait(timeout=10)
    return 1, 1


def run_probe() -> dict[str, object]:
    SYNTHETIC_HOME.mkdir(mode=0o700, exist_ok=True)
    (SYNTHETIC_HOME / ".claude").mkdir(mode=0o700, exist_ok=True)
    SYNTHETIC_WORK.mkdir(mode=0o700, exist_ok=True)
    SYNTHETIC_OUTPUT.mkdir(mode=0o700, exist_ok=True)
    mock = LoopbackOnlyMock(MOCK_PORT)
    target_started = 0
    target_completed = 0
    interface_names: tuple[str, ...] = ()
    default_routes = 1
    try:
        mock.start()
        interface_names, default_routes = _prepare_loopback_network()
        if not network_state_is_safe(interface_names, default_routes):
            return make_safe_summary(
                InspectionAnalysis(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                canary_connections=mock.connection_count,
                target_started_count=0,
                target_completed_count=0,
                nonloopback_interface_count=len([name for name in interface_names if name != "lo"]),
                default_route_count=default_routes,
                nonloopback_connection_count=mock.nonloopback_connection_count,
            )
        run_loopback_canary(mock.port)
        if not mock.wait_for_connections(1):
            return make_safe_summary(
                InspectionAnalysis(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
                canary_connections=mock.connection_count,
                target_started_count=0,
                target_completed_count=0,
                nonloopback_interface_count=0,
                default_route_count=0,
                nonloopback_connection_count=mock.nonloopback_connection_count,
            )
        target_started, target_completed = _run_target()
        analysis = inspect_virtual_home(SYNTHETIC_HOME)
        return make_safe_summary(
            analysis,
            canary_connections=mock.connection_count,
            target_started_count=target_started,
            target_completed_count=target_completed,
            nonloopback_interface_count=len([name for name in interface_names if name != "lo"]),
            default_route_count=default_routes,
            nonloopback_connection_count=mock.nonloopback_connection_count,
            negative_oracles_complete=False,
        )
    except (OSError, SafeParseError, subprocess.SubprocessError):
        return make_safe_summary(
            InspectionAnalysis(0, 0, 0, 0, 0, 0, 0, 0, 0, 0),
            canary_connections=mock.connection_count,
            target_started_count=target_started,
            target_completed_count=target_completed,
            nonloopback_interface_count=len([name for name in interface_names if name != "lo"]),
            default_route_count=default_routes,
            nonloopback_connection_count=mock.nonloopback_connection_count,
        )
    finally:
        mock.close()


def main() -> int:
    if len(sys.argv) != 1:
        return 2
    print(json.dumps(run_probe(), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
