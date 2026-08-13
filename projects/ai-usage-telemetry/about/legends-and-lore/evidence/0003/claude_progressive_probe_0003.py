# /// script
# requires-python = ">=3.10"
# ///

"""Fail-closed host launcher and structural oracle for candidate evidence 0003.

The only target invocation is routed through Bubblewrap.  This module never
opens a real Claude session source, credential store, home, workspace, or
network connection.  It accepts only the safe structural summary emitted by
the in-sandbox helper; target stdout and stderr remain in the sandbox tmpfs.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import threading
import time
from typing import Any, Callable, Iterable, Mapping


PINNED_VERSION = "2.1.227"
PINNED_SHA256 = "6832dc3f1797b890b71116e5f2dbbf9a83fd3d0498c235b4b0f9cd0e6e499ad6"
EVIDENCE_DIRECTORY = Path(__file__).resolve().parent
FIXTURE_PATH = EVIDENCE_DIRECTORY / "fixture_0003.json"
RUNTIME_DIRECTORY = EVIDENCE_DIRECTORY / "runtime"
INNER_PROBE_PATH = "/probe/runtime/inner_probe_0003.py"
SYNTHETIC_TARGET_PATH = "/opt/claude/claude"
TRUSTED_BWRAP_PATH = Path("/usr/bin/bwrap")
TRUSTED_BWRAP_SHA256 = "d78807229d616606e339c5988392b9e0ab4a6a6998fa51e4590837f426a12fca"
ATTEMPT_GATE_PATH = RUNTIME_DIRECTORY / "attempt_gate_0003.json"
CONSUMED_ATTEMPT_GATE_BYTES = (
    b"{\n"
    b'  "schema": "candidate-0003-attempt-gate@1",\n'
    b'  "state": "consumed"\n'
    b"}\n"
)
CONSUMED_ATTEMPT_GATE_SHA256 = "296d9c192435acb6a65ce0c18766916e329a916f515fb41bb39c4a96b5eb3fec"
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
REQUIRED_NAMESPACES = frozenset({"user", "pid", "net"})
DEFAULT_RUNTIME_MOUNT_SOURCES = (
    Path("/bin"),
    Path("/lib"),
    Path("/lib64"),
    Path("/usr/bin/python3"),
    Path("/usr/lib"),
    Path("/usr/lib64"),
    TRUSTED_BWRAP_PATH,
)
SAFE_ENVIRONMENT = {
    "HOME": "/sandbox-home",
    "CLAUDE_CONFIG_DIR": "/sandbox-home/.claude",
    "ANTHROPIC_CONFIG_DIR": "/sandbox-home/.claude",
    "ANTHROPIC_API_KEY": "synthetic-loopback-probe-key",
    "ANTHROPIC_BASE_URL": "http://127.0.0.1:18080",
    "PATH": "/bin:/usr/bin",
}
SAFE_SUMMARY_KEYS = {
    "schema",
    "build_pin",
    "path_classes",
    "type_assertions",
    "counts",
    "equality_assertions",
    "direction_assertions",
    "control_totals",
    "disposition",
}
SUMMARY_SECTION_KEYS = {
    "path_classes": {"target", "probe_code", "home", "work", "output", "network"},
    "type_assertions": {"structural_projection", "complete_usage_observation"},
    "counts": {
        "target_started",
        "target_completed",
        "loopback_mock_connections",
        "complete_usage_observations",
        "malformed_records",
        "incomplete_tails",
        "same_native_pair_groups",
        "progressive_same_pair_groups",
    },
    "equality_assertions": {
        "exact_replay_groups",
        "changed_timestamp_groups",
        "nonconforming_reuse_groups",
    },
    "direction_assertions": {"monotone-increase-groups", "decreasing-groups"},
    "control_totals": {
        "loopback_canary_connections",
        "nonloopback_interface_count",
        "default_route_count",
        "nonloopback_connection_count",
    },
}
SUMMARY_STRING_SECTION_VALUES = {
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
}
MAX_SAFE_SUMMARY_BYTES = 16_384
SAFE_SUMMARY_CAPTURE_BYTES = MAX_SAFE_SUMMARY_BYTES + 1
SUMMARY_READ_CHUNK_BYTES = 4_096
PROBE_TIMEOUT_SECONDS = 90
PROCESS_STOP_TIMEOUT_SECONDS = 5
MAX_SAFE_SOURCE_COUNTER = (1 << 63) - 1
MAX_SAFE_SUMMARY_INTEGER = MAX_SAFE_SOURCE_COUNTER
_JSON_HEX_DIGITS = frozenset(b"0123456789abcdefABCDEF")


class ContainmentRejected(RuntimeError):
    """Raised before target launch when a required safety predicate is false."""


@dataclass(frozen=True)
class MountRule:
    kind: str
    source: Path
    destination: str
    path_class: str


@dataclass(frozen=True)
class ProbePlan:
    target: Path
    probe_code: Path
    namespaces: frozenset[str]
    mounts: tuple[MountRule, ...]
    synthetic_tmpfs: frozenset[str]
    clear_environment: bool
    synthetic_environment: Mapping[str, str]
    forwarded_environment: Mapping[str, str]
    network_mode: str
    target_output: str

    def replace(self, **changes: object) -> "ProbePlan":
        return replace(self, **changes)

    def with_mount(self, mount: MountRule) -> "ProbePlan":
        return replace(self, mounts=(*self.mounts, mount))


@dataclass(frozen=True)
class PinnedBuild:
    version: str
    sha256: str


@dataclass(frozen=True)
class SafeInspectionSummary:
    complete_usage_observation_count: int
    malformed_record_count: int
    incomplete_tail_count: int
    decoded_path_classes: tuple[str, ...]


def require(condition: bool, code: str) -> None:
    if not condition:
        raise ContainmentRejected(code)


def make_safe_plan(
    *, target: Path, probe_code: Path, runtime_roots: tuple[Path, ...] = DEFAULT_RUNTIME_MOUNT_SOURCES
) -> ProbePlan:
    mounts = tuple(
        MountRule("ro-bind", runtime_root, str(runtime_root), "standard-runtime")
        for runtime_root in runtime_roots
    )
    return ProbePlan(
        target=target,
        probe_code=probe_code,
        namespaces=REQUIRED_NAMESPACES,
        mounts=(
            *mounts,
            MountRule("ro-bind", target, SYNTHETIC_TARGET_PATH, "exact-executable"),
            MountRule("ro-bind", probe_code, "/probe/runtime", "probe-code"),
        ),
        synthetic_tmpfs=frozenset({"/tmp", "/sandbox-home", "/sandbox-work", "/sandbox-output"}),
        clear_environment=True,
        synthetic_environment=dict(SAFE_ENVIRONMENT),
        forwarded_environment={},
        network_mode="loopback-only",
        target_output="sandbox-tmpfs",
    )


def assert_candidate_only_paths(paths: Iterable[str]) -> None:
    root = "projects/ai-usage-telemetry/about/legends-and-lore/evidence/0003/"
    for path in paths:
        require(path.startswith(root), "patch-boundary")


def assert_plan_safe(plan: ProbePlan) -> None:
    require(plan.namespaces == REQUIRED_NAMESPACES, "namespace-contract")
    require(plan.clear_environment, "environment-not-cleared")
    require(not plan.forwarded_environment, "inherited-environment")
    require(plan.synthetic_environment == SAFE_ENVIRONMENT, "synthetic-environment-contract")
    require(plan.network_mode == "loopback-only", "network-contract")
    require(plan.target_output == "sandbox-tmpfs", "raw-output-capture")
    require(
        plan.synthetic_tmpfs == {"/tmp", "/sandbox-home", "/sandbox-work", "/sandbox-output"},
        "tmpfs-contract",
    )
    expected_runtime = set(DEFAULT_RUNTIME_MOUNT_SOURCES)
    target_mounts = [mount for mount in plan.mounts if mount.path_class == "exact-executable"]
    probe_mounts = [mount for mount in plan.mounts if mount.path_class == "probe-code"]
    require(len(target_mounts) == 1, "exact-executable-mount")
    require(len(probe_mounts) == 1, "probe-code-mount")
    for mount in plan.mounts:
        require(mount.kind == "ro-bind", "writeable-bind")
        require(mount.path_class in {"standard-runtime", "exact-executable", "probe-code"}, "mount-class")
        require(mount.source != Path("/"), "broad-root-bind")
        if mount.path_class == "standard-runtime":
            require(mount.source in expected_runtime, "runtime-bind")
        elif mount.path_class == "exact-executable":
            require(mount.source == plan.target, "target-bind")
            require(mount.destination == SYNTHETIC_TARGET_PATH, "target-destination")
        else:
            require(mount.source == plan.probe_code, "probe-code-bind")
            require(mount.destination == "/probe/runtime", "probe-code-destination")


def _sha256_and_version_token(path: Path) -> tuple[str, bool]:
    digest = hashlib.sha256()
    version_token = PINNED_VERSION.encode("ascii")
    previous_tail = b""
    found = False
    with path.open("rb") as executable:
        while True:
            chunk = executable.read(1 << 20)
            if not chunk:
                break
            digest.update(chunk)
            if version_token in previous_tail + chunk:
                found = True
            previous_tail = chunk[-(len(version_token) - 1) :]
    return digest.hexdigest(), found


def verify_pinned_build(target: Path) -> PinnedBuild:
    resolved = target.resolve(strict=True)
    metadata = resolved.stat()
    require(stat.S_ISREG(metadata.st_mode), "build-pin-not-regular-file")
    actual_sha256, version_present = _sha256_and_version_token(resolved)
    require(actual_sha256 == PINNED_SHA256, "build-pin-sha256")
    require(version_present, "build-pin-version")
    return PinnedBuild(version=PINNED_VERSION, sha256=actual_sha256)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while chunk := source.read(1 << 20):
            digest.update(chunk)
    return digest.hexdigest()


def resolve_trusted_bwrap() -> Path:
    resolved = TRUSTED_BWRAP_PATH.resolve(strict=True)
    metadata = resolved.stat()
    require(resolved == TRUSTED_BWRAP_PATH, "bubblewrap-path")
    require(stat.S_ISREG(metadata.st_mode), "bubblewrap-not-regular-file")
    require(metadata.st_mode & stat.S_IXUSR, "bubblewrap-not-executable")
    require(_sha256_file(resolved) == TRUSTED_BWRAP_SHA256, "bubblewrap-sha256")
    return resolved


def assert_attempt_gate_allows_launch() -> None:
    try:
        gate = ATTEMPT_GATE_PATH.read_bytes()
    except OSError as error:
        raise ContainmentRejected("attempt-gate-read") from error
    require(hashlib.sha256(gate).hexdigest() == CONSUMED_ATTEMPT_GATE_SHA256, "attempt-gate-integrity")
    require(gate == CONSUMED_ATTEMPT_GATE_BYTES, "attempt-gate-shape")
    raise ContainmentRejected("attempt-consumed")


def resolve_claude_executable() -> Path:
    candidate = shutil.which("claude")
    require(candidate is not None, "build-pin-executable-missing")
    return Path(candidate).resolve(strict=True)


def launch_if_safe(
    plan: ProbePlan,
    *,
    pin_checker: Callable[[Path], bool] | None = None,
    launcher: Callable[[ProbePlan], None],
) -> None:
    assert_plan_safe(plan)
    if pin_checker is None:
        verify_pinned_build(plan.target)
    else:
        require(pin_checker(plan.target), "build-pin")
    launcher(plan)


def _classify_case(case: Mapping[str, object]) -> str:
    shape = case["record_shape"]
    if shape == "malformed":
        return "recognized-malformed"
    if shape == "incomplete":
        return "incomplete-tail"
    if case["native_pair_relation"] != "same":
        return "identity-collision"
    if (
        case["timestamp_relation"] == "same"
        and case["message_relation"] == "same"
        and case["model_relation"] == "same"
        and case["counter_direction"] == "same"
    ):
        return "duplicate"
    if (
        case["timestamp_relation"] == "changed"
        and case["message_relation"] == "same"
        and case["model_relation"] == "same"
        and case["counter_direction"] == "monotone-increase"
    ):
        return "confirmed-contract-gap"
    return "identity-collision"


def verify_predeclared_oracle_matrix(data: Mapping[str, object]) -> dict[str, str]:
    require(set(data) == {"schema", "build", "probe_contract", "cases"}, "fixture-keys")
    require(data["schema"] == "claude-progressive-probe-fixture@1", "fixture-schema")
    build = data["build"]
    require(isinstance(build, dict), "fixture-build")
    require(build == {"version": PINNED_VERSION, "sha256": PINNED_SHA256}, "fixture-build-pin")
    contract = data["probe_contract"]
    require(isinstance(contract, dict), "fixture-contract")
    require(contract["target_invocation_count"] == 1, "fixture-single-invocation")
    require(contract["namespace_types"] == ["user", "pid", "net"], "fixture-namespaces")
    require(contract["network_scope"] == "loopback-only", "fixture-network")
    require(contract["output_scope"] == "sandbox-tmpfs-only", "fixture-output")
    require(contract["disposition_on_insufficient_evidence"] == "unresolved", "fixture-disposition")
    cases = data["cases"]
    require(isinstance(cases, list) and len(cases) == 8, "fixture-cases")
    outcomes: dict[str, str] = {}
    expected_case_ids = {
        "exact-replay",
        "one-request-progressive-stream",
        "changed-timestamp",
        "monotone-counter",
        "decreasing-counter",
        "malformed-record",
        "incomplete-record",
        "nonconforming-identity-reuse",
    }
    for case in cases:
        require(isinstance(case, dict), "fixture-case-object")
        expected_keys = {
            "case_id",
            "record_shape",
            "native_pair_relation",
            "timestamp_relation",
            "message_relation",
            "model_relation",
            "counter_direction",
            "expected_disposition",
        }
        require(set(case) == expected_keys, "fixture-case-keys")
        case_id = case["case_id"]
        require(isinstance(case_id, str) and case_id in expected_case_ids, "fixture-case-id")
        derived = _classify_case(case)
        require(case["expected_disposition"] == derived, "fixture-case-oracle")
        outcomes[case_id] = derived
    require(set(outcomes) == expected_case_ids, "fixture-case-coverage")
    return outcomes


class _SafeJsonLineScanner:
    """Decode only explicit structural paths while skipping unknown values bytewise."""

    def __init__(self, raw: bytes) -> None:
        self.raw = raw
        self.index = 0
        self.values: dict[tuple[str, ...], object] = {}

    def parse(self) -> dict[tuple[str, ...], object]:
        self._skip_whitespace()
        self._parse_value(())
        self._skip_whitespace()
        if self.index != len(self.raw):
            raise ValueError("trailing-json")
        return self.values

    def _skip_whitespace(self) -> None:
        while self.index < len(self.raw) and self.raw[self.index] in b" \t\r\n":
            self.index += 1

    def _parse_value(self, path: tuple[str, ...] | None) -> None:
        self._skip_whitespace()
        if self.index >= len(self.raw):
            raise ValueError("truncated-json")
        if path is None:
            self._skip_value()
            return
        token = self.raw[self.index]
        if token == ord("{"):
            self._parse_object(path)
            return
        if token == ord("["):
            self._parse_array(path)
            return
        if path in _SAFE_STRING_PATHS:
            self.values[path] = self._decode_string()
            return
        if path in _SAFE_INTEGER_PATHS:
            self.values[path] = self._decode_integer()
            return
        self._skip_scalar_or_container()

    def _parse_object(self, path: tuple[str, ...]) -> None:
        self.index += 1
        self._skip_whitespace()
        if self._consume(ord("}")):
            return
        seen_projected_paths: set[tuple[str, ...]] = set()
        while True:
            key = self._read_key()
            self._skip_whitespace()
            self._expect(ord(":"))
            next_path = _next_safe_path(path, key)
            if next_path is not None:
                if next_path in seen_projected_paths:
                    raise ValueError("duplicate-projected-key")
                seen_projected_paths.add(next_path)
            self._parse_value(next_path)
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

    def _read_key(self) -> str | None:
        start, end, escaped = self._scan_string_bounds()
        if escaped:
            return None
        for known in _KNOWN_STRUCTURAL_KEYS:
            if end - start == len(known) and all(self.raw[start + offset] == byte for offset, byte in enumerate(known)):
                return known.decode("ascii")
        return None

    def _decode_string(self) -> str:
        start = self.index
        self._scan_string_bounds()
        literal = self.raw[start : self.index]
        value = json.loads(literal)
        if not isinstance(value, str):
            raise ValueError("expected-string")
        return value

    def _decode_integer(self) -> int:
        start, end = self._scan_number()
        if self.raw[start] == ord("-") or any(
            self.raw[offset] in b".eE" for offset in range(start, end)
        ):
            raise ValueError("expected-integer")
        value = 0
        for offset in range(start, end):
            value = value * 10 + self.raw[offset] - ord("0")
            if value > MAX_SAFE_SOURCE_COUNTER:
                raise ValueError("source-counter-range")
        return value

    def _scan_string_bounds(self) -> tuple[int, int, bool]:
        self._expect(ord('"'))
        start = self.index
        has_escape = False
        while self.index < len(self.raw):
            current = self.raw[self.index]
            if current == ord('"'):
                self.index += 1
                return start, self.index - 1, has_escape
            if current == ord("\\"):
                self.index += 1
                has_escape = True
                if self.index >= len(self.raw):
                    raise ValueError("unterminated-escape")
                escaped = self.raw[self.index]
                self.index += 1
                if escaped in b'"\\/bfnrt':
                    continue
                if escaped != ord("u"):
                    raise ValueError("invalid-escape")
                for _ in range(4):
                    if self.index >= len(self.raw) or self.raw[self.index] not in _JSON_HEX_DIGITS:
                        raise ValueError("invalid-unicode-escape")
                    self.index += 1
                continue
            if current < 0x20:
                raise ValueError("invalid-string")
            if current < 0x80:
                self.index += 1
                continue
            self._skip_utf8_codepoint()
        raise ValueError("unterminated-string")

    def _skip_utf8_codepoint(self) -> None:
        start = self.index
        first = self.raw[start]

        def continuation(offset: int, lower: int = 0x80, upper: int = 0xBF) -> None:
            position = start + offset
            if position >= len(self.raw) or not lower <= self.raw[position] <= upper:
                raise ValueError("invalid-utf8")

        if 0xC2 <= first <= 0xDF:
            continuation(1)
            self.index += 2
            return
        if first == 0xE0:
            continuation(1, 0xA0, 0xBF)
            continuation(2)
            self.index += 3
            return
        if 0xE1 <= first <= 0xEC or 0xEE <= first <= 0xEF:
            continuation(1)
            continuation(2)
            self.index += 3
            return
        if first == 0xED:
            continuation(1, 0x80, 0x9F)
            continuation(2)
            self.index += 3
            return
        if first == 0xF0:
            continuation(1, 0x90, 0xBF)
            continuation(2)
            continuation(3)
            self.index += 4
            return
        if 0xF1 <= first <= 0xF3:
            continuation(1)
            continuation(2)
            continuation(3)
            self.index += 4
            return
        if first == 0xF4:
            continuation(1, 0x80, 0x8F)
            continuation(2)
            continuation(3)
            self.index += 4
            return
        raise ValueError("invalid-utf8")

    def _skip_value(self) -> None:
        self._skip_whitespace()
        if self.index >= len(self.raw):
            raise ValueError("truncated-json")
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
            return
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
            return
        self._skip_literal_or_number()

    def _skip_literal_or_number(self) -> None:
        for literal in (b"true", b"false", b"null"):
            if self.raw.startswith(literal, self.index):
                self.index += len(literal)
                return
        self._scan_number()

    def _scan_number(self) -> tuple[int, int]:
        start = self.index
        if self.index < len(self.raw) and self.raw[self.index] == ord("-"):
            self.index += 1
        if self.index >= len(self.raw):
            raise ValueError("invalid-number")
        if self.raw[self.index] == ord("0"):
            self.index += 1
            if self.index < len(self.raw) and self.raw[self.index] in b"0123456789":
                raise ValueError("leading-zero-number")
        elif self.raw[self.index] in b"123456789":
            self.index += 1
            while self.index < len(self.raw) and self.raw[self.index] in b"0123456789":
                self.index += 1
        else:
            raise ValueError("invalid-number")
        if self.index < len(self.raw) and self.raw[self.index] == ord("."):
            self.index += 1
            fraction_start = self.index
            while self.index < len(self.raw) and self.raw[self.index] in b"0123456789":
                self.index += 1
            if self.index == fraction_start:
                raise ValueError("invalid-number")
        if self.index < len(self.raw) and self.raw[self.index] in b"eE":
            self.index += 1
            if self.index < len(self.raw) and self.raw[self.index] in b"+-":
                self.index += 1
            exponent_start = self.index
            while self.index < len(self.raw) and self.raw[self.index] in b"0123456789":
                self.index += 1
            if self.index == exponent_start:
                raise ValueError("invalid-number")
        return start, self.index

    def _skip_scalar_or_container(self) -> None:
        """Compatibility wrapper retained only for the fixed safe-path caller."""
        self._skip_value()

    def _expect(self, expected: int) -> None:
        self._skip_whitespace()
        if self.index >= len(self.raw) or self.raw[self.index] != expected:
            raise ValueError("invalid-json")
        self.index += 1

    def _consume(self, expected: int) -> bool:
        self._skip_whitespace()
        if self.index < len(self.raw) and self.raw[self.index] == expected:
            self.index += 1
            return True
        return False


_KNOWN_STRUCTURAL_KEYS = frozenset(
    {
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
    }
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


def _next_safe_path(parent: tuple[str, ...], key: str | None) -> tuple[str, ...] | None:
    if key is None:
        return None
    candidate = (*parent, key)
    prefixes = {path[: len(candidate)] for path in (*_SAFE_STRING_PATHS, *_SAFE_INTEGER_PATHS)}
    return candidate if candidate in prefixes else None


def inspect_jsonl_bytes(raw: bytes) -> SafeInspectionSummary:
    complete = 0
    malformed = 0
    incomplete = 0
    for line in raw.splitlines(keepends=True):
        if not line.endswith(b"\n"):
            incomplete += 1
            continue
        try:
            values = _SafeJsonLineScanner(line).parse()
        except (ValueError, json.JSONDecodeError):
            malformed += 1
            continue
        if _is_complete_usage_record(values):
            complete += 1
    return SafeInspectionSummary(
        complete_usage_observation_count=complete,
        malformed_record_count=malformed,
        incomplete_tail_count=incomplete,
        decoded_path_classes=SAFE_PROJECTED_PATH_CLASSES,
    )


def _is_complete_usage_record(values: Mapping[tuple[str, ...], object]) -> bool:
    required = _SAFE_STRING_PATHS | _SAFE_INTEGER_PATHS
    if not required.issubset(values):
        return False
    return values[("type",)] == "assistant" and all(
        isinstance(values[path], int) and values[path] >= 0 for path in _SAFE_INTEGER_PATHS
    )


def validate_safe_summary(value: Mapping[str, object]) -> None:
    require(set(value) == SAFE_SUMMARY_KEYS, "summary-key")
    require(value["schema"] == "claude-progressive-probe-summary@1", "summary-schema")
    build_pin = value["build_pin"]
    require(build_pin == {"version": PINNED_VERSION, "sha256": PINNED_SHA256}, "summary-build-pin")
    sections = (
        "path_classes",
        "type_assertions",
        "counts",
        "equality_assertions",
        "direction_assertions",
        "control_totals",
    )
    for key in sections:
        require(isinstance(value[key], dict), f"summary-{key}")
    require(value["disposition"] in {"confirmed-contract-gap", "confirmed-current-contract", "unresolved"}, "summary-disposition")
    section_values = {key: value[key] for key in sections}
    if all(not section_values[key] for key in sections):
        require(value["disposition"] == "unresolved", "summary-unresolved-disposition")
        return
    for key in sections:
        section = section_values[key]
        require(set(section) == SUMMARY_SECTION_KEYS[key], f"summary-{key}-keys")
        if key in {"counts", "equality_assertions", "direction_assertions", "control_totals"}:
            require(
                all(isinstance(item, int) and not isinstance(item, bool) and item >= 0 for item in section.values()),
                f"summary-{key}-types",
            )
        else:
            require(all(isinstance(item, str) for item in section.values()), f"summary-{key}-types")
            require(section == SUMMARY_STRING_SECTION_VALUES[key], f"summary-{key}-values")
    raw_markers = ("raw", "stdout", "stderr", "prompt", "response", "header", "session", "requestid", "identity")
    for key in value:
        require(not any(marker in key.casefold() for marker in raw_markers), "summary-privacy-key")


def _has_reachable_inner_analysis_aggregates(
    counts: dict[str, int],
    equality_assertions: dict[str, int],
    direction_assertions: dict[str, int],
) -> bool:
    """Require aggregate relationships that the inner classifier can actually emit."""
    same_pair_groups = counts["same_native_pair_groups"]
    progressive_groups = counts["progressive_same_pair_groups"]
    exact_replay_groups = equality_assertions["exact_replay_groups"]
    changed_timestamp_groups = equality_assertions["changed_timestamp_groups"]
    nonconforming_reuse_groups = equality_assertions["nonconforming_reuse_groups"]
    decreasing_groups = direction_assertions["decreasing-groups"]
    if exact_replay_groups > same_pair_groups:
        return False
    non_exact_pair_groups = same_pair_groups - exact_replay_groups
    return (
        progressive_groups <= non_exact_pair_groups
        and changed_timestamp_groups <= non_exact_pair_groups
        and decreasing_groups <= non_exact_pair_groups
        and nonconforming_reuse_groups <= non_exact_pair_groups
        and progressive_groups <= changed_timestamp_groups
        and progressive_groups + decreasing_groups <= non_exact_pair_groups
        and progressive_groups + nonconforming_reuse_groups <= non_exact_pair_groups
    )


def _has_confirmed_contract_gap_evidence(value: Mapping[str, object]) -> bool:
    """Require the exact primitive relationships emitted by a completed control run."""
    counts = value["counts"]
    equality_assertions = value["equality_assertions"]
    direction_assertions = value["direction_assertions"]
    control_totals = value["control_totals"]
    assert isinstance(counts, dict)
    assert isinstance(equality_assertions, dict)
    assert isinstance(direction_assertions, dict)
    assert isinstance(control_totals, dict)
    assert all(isinstance(item, int) for item in counts.values())
    assert all(isinstance(item, int) for item in equality_assertions.values())
    assert all(isinstance(item, int) for item in direction_assertions.values())
    same_pair_groups = counts["same_native_pair_groups"]
    progressive_groups = counts["progressive_same_pair_groups"]
    return (
        counts["target_started"] == 1
        and counts["target_completed"] == 1
        and counts["loopback_mock_connections"] >= 1
        and counts["complete_usage_observations"] >= 2
        and counts["malformed_records"] == 0
        and counts["incomplete_tails"] == 0
        and same_pair_groups >= 1
        and progressive_groups >= 1
        and counts["complete_usage_observations"] >= 2 * same_pair_groups
        and _has_reachable_inner_analysis_aggregates(
            counts, equality_assertions, direction_assertions
        )
        and direction_assertions["monotone-increase-groups"] == progressive_groups
        and control_totals["loopback_canary_connections"] == 1
        and control_totals["nonloopback_interface_count"] == 0
        and control_totals["default_route_count"] == 0
        and control_totals["nonloopback_connection_count"] == 0
    )


def _derive_summary_disposition(value: Mapping[str, object]) -> str:
    if _has_confirmed_contract_gap_evidence(value):
        return "confirmed-contract-gap"
    return "unresolved"


def normalize_safe_summary(value: dict[str, object]) -> dict[str, object]:
    """Keep only a host-derived confirmation; erase every other untrusted summary."""
    validate_safe_summary(value)
    if all(not value[key] for key in SUMMARY_SECTION_KEYS):
        return value
    derived_disposition = _derive_summary_disposition(value)
    if value["disposition"] == derived_disposition == "confirmed-contract-gap":
        return value
    return _safe_unresolved_result()


class _SafeSummaryAdmissionScanner:
    """Admit only the exact safe-summary grammar without decoding unknown values."""

    def __init__(self, raw: bytes | bytearray) -> None:
        self.raw = raw
        self.index = 0

    def parse(self) -> dict[str, object]:
        self._skip_whitespace()
        summary = self._parse_object()
        self._skip_whitespace()
        require(self.index == len(self.raw), "summary-json")
        validate_safe_summary(summary)
        return summary

    def _parse_object(self) -> dict[str, object]:
        self._expect(ord("{"))
        summary: dict[str, object] = {}
        self._skip_whitespace()
        while not self._consume(ord("}")):
            key = self._read_allowed_key(SAFE_SUMMARY_KEYS, "summary-key")
            require(key not in summary, "summary-key")
            self._expect(ord(":"))
            summary[key] = self._parse_top_level_value(key)
            self._skip_whitespace()
            if self._consume(ord("}")):
                break
            self._expect(ord(","))
        require(set(summary) == SAFE_SUMMARY_KEYS, "summary-key")
        return summary

    def _parse_top_level_value(self, key: str) -> object:
        if key == "schema":
            return self._parse_expected_string("claude-progressive-probe-summary@1", "summary-schema")
        if key == "build_pin":
            return self._parse_fixed_string_object(
                {"version": PINNED_VERSION, "sha256": PINNED_SHA256}, "summary-build-pin"
            )
        if key in SUMMARY_STRING_SECTION_VALUES:
            return self._parse_fixed_string_object(
                SUMMARY_STRING_SECTION_VALUES[key], f"summary-{key}"
            )
        if key in SUMMARY_SECTION_KEYS:
            return self._parse_nonnegative_integer_object(SUMMARY_SECTION_KEYS[key], f"summary-{key}")
        if key == "disposition":
            return self._parse_enum_string(
                {"confirmed-contract-gap", "confirmed-current-contract", "unresolved"},
                "summary-disposition",
            )
        raise ContainmentRejected("summary-key")

    def _parse_fixed_string_object(
        self, expected: Mapping[str, str], code: str
    ) -> dict[str, str]:
        self._expect(ord("{"))
        values: dict[str, str] = {}
        self._skip_whitespace()
        if self._consume(ord("}")):
            return values
        while True:
            key = self._read_allowed_key(expected, f"{code}-keys")
            require(key not in values, f"{code}-keys")
            self._expect(ord(":"))
            values[key] = self._parse_expected_string(expected[key], f"{code}-values")
            self._skip_whitespace()
            if self._consume(ord("}")):
                break
            self._expect(ord(","))
        require(set(values) == set(expected), f"{code}-keys")
        return values

    def _parse_nonnegative_integer_object(
        self, expected: set[str], code: str
    ) -> dict[str, int]:
        self._expect(ord("{"))
        values: dict[str, int] = {}
        self._skip_whitespace()
        if self._consume(ord("}")):
            return values
        while True:
            key = self._read_allowed_key(expected, f"{code}-keys")
            require(key not in values, f"{code}-keys")
            self._expect(ord(":"))
            values[key] = self._parse_nonnegative_integer(code)
            self._skip_whitespace()
            if self._consume(ord("}")):
                break
            self._expect(ord(","))
        require(set(values) == expected, f"{code}-keys")
        return values

    def _read_allowed_key(self, allowed: Iterable[str], code: str) -> str:
        start, end, escaped = self._scan_string_bounds()
        if not escaped:
            for candidate in allowed:
                encoded = candidate.encode("ascii")
                if end - start == len(encoded) and all(
                    self.raw[start + offset] == value for offset, value in enumerate(encoded)
                ):
                    return candidate
        raise ContainmentRejected(code)

    def _parse_expected_string(self, expected: str, code: str) -> str:
        self._skip_whitespace()
        literal_start = self.index
        self._scan_string_bounds()
        expected_literal = b'"' + expected.encode("ascii") + b'"'
        if self.index - literal_start != len(expected_literal) or any(
            self.raw[literal_start + offset] != value for offset, value in enumerate(expected_literal)
        ):
            raise ContainmentRejected(code)
        return expected

    def _parse_enum_string(self, allowed: set[str], code: str) -> str:
        self._skip_whitespace()
        literal_start = self.index
        self._scan_string_bounds()
        for candidate in allowed:
            expected_literal = b'"' + candidate.encode("ascii") + b'"'
            if self.index - literal_start == len(expected_literal) and all(
                self.raw[literal_start + offset] == value for offset, value in enumerate(expected_literal)
            ):
                return candidate
        raise ContainmentRejected(code)

    def _parse_nonnegative_integer(self, code: str) -> int:
        self._skip_whitespace()
        if self.index >= len(self.raw):
            raise ContainmentRejected(code)
        if self.raw[self.index] == ord("0"):
            self.index += 1
            if self.index < len(self.raw) and self.raw[self.index] in b"0123456789":
                raise ContainmentRejected(code)
            return 0
        if self.raw[self.index] not in b"123456789":
            raise ContainmentRejected(code)
        value = 0
        while self.index < len(self.raw) and self.raw[self.index] in b"0123456789":
            value = value * 10 + self.raw[self.index] - ord("0")
            if value > MAX_SAFE_SUMMARY_INTEGER:
                raise ContainmentRejected(code)
            self.index += 1
        if self.index < len(self.raw) and self.raw[self.index] in b".eE":
            raise ContainmentRejected(code)
        return value

    def _scan_string_bounds(self) -> tuple[int, int, bool]:
        self._expect(ord('"'))
        start = self.index
        has_escape = False
        while self.index < len(self.raw):
            current = self.raw[self.index]
            if current == ord('"'):
                self.index += 1
                return start, self.index - 1, has_escape
            if current == ord("\\"):
                self.index += 1
                has_escape = True
                if self.index >= len(self.raw):
                    raise ContainmentRejected("summary-json")
                escaped = self.raw[self.index]
                self.index += 1
                if escaped in b'"\\/bfnrt':
                    continue
                if escaped != ord("u"):
                    raise ContainmentRejected("summary-json")
                for _ in range(4):
                    if self.index >= len(self.raw) or self.raw[self.index] not in _JSON_HEX_DIGITS:
                        raise ContainmentRejected("summary-json")
                    self.index += 1
                continue
            if current < 0x20:
                raise ContainmentRejected("summary-json")
            if current < 0x80:
                self.index += 1
                continue
            self._skip_utf8_codepoint()
        raise ContainmentRejected("summary-json")

    def _skip_utf8_codepoint(self) -> None:
        start = self.index
        first = self.raw[start]

        def continuation(offset: int, lower: int = 0x80, upper: int = 0xBF) -> None:
            position = start + offset
            if position >= len(self.raw) or not lower <= self.raw[position] <= upper:
                raise ContainmentRejected("summary-json")

        if 0xC2 <= first <= 0xDF:
            continuation(1)
            self.index += 2
            return
        if first == 0xE0:
            continuation(1, 0xA0, 0xBF)
            continuation(2)
            self.index += 3
            return
        if 0xE1 <= first <= 0xEC or 0xEE <= first <= 0xEF:
            continuation(1)
            continuation(2)
            self.index += 3
            return
        if first == 0xED:
            continuation(1, 0x80, 0x9F)
            continuation(2)
            self.index += 3
            return
        if first == 0xF0:
            continuation(1, 0x90, 0xBF)
            continuation(2)
            continuation(3)
            self.index += 4
            return
        if 0xF1 <= first <= 0xF3:
            continuation(1)
            continuation(2)
            continuation(3)
            self.index += 4
            return
        if first == 0xF4:
            continuation(1, 0x80, 0x8F)
            continuation(2)
            continuation(3)
            self.index += 4
            return
        raise ContainmentRejected("summary-json")

    def _skip_whitespace(self) -> None:
        while self.index < len(self.raw) and self.raw[self.index] in b" \t\r\n":
            self.index += 1

    def _expect(self, expected: int) -> None:
        self._skip_whitespace()
        if self.index >= len(self.raw) or self.raw[self.index] != expected:
            raise ContainmentRejected("summary-json")
        self.index += 1

    def _consume(self, expected: int) -> bool:
        self._skip_whitespace()
        if self.index < len(self.raw) and self.raw[self.index] == expected:
            self.index += 1
            return True
        return False


def _parse_summary_bytes(raw: bytes | bytearray) -> dict[str, object]:
    require(len(raw) <= MAX_SAFE_SUMMARY_BYTES, "summary-size")
    return normalize_safe_summary(_SafeSummaryAdmissionScanner(raw).parse())


def _bwrap_argv(plan: ProbePlan, bwrap: Path) -> list[str]:
    args = [
        str(bwrap),
        "--die-with-parent",
        "--new-session",
        "--unshare-user",
        "--unshare-pid",
        "--unshare-net",
        "--uid",
        "1000",
        "--gid",
        "1000",
        "--clearenv",
        "--proc",
        "/proc",
        "--dev",
        "/dev",
        "--tmpfs",
        "/tmp",
        "--chmod",
        "1777",
        "/tmp",
        "--tmpfs",
        "/sandbox-home",
        "--chmod",
        "0777",
        "/sandbox-home",
        "--tmpfs",
        "/sandbox-work",
        "--chmod",
        "0777",
        "/sandbox-work",
        "--tmpfs",
        "/sandbox-output",
        "--chmod",
        "0777",
        "/sandbox-output",
        "--dir",
        "/opt",
        "--dir",
        "/opt/claude",
        "--dir",
        "/probe",
        "--dir",
        "/usr",
        "--dir",
        "/usr/bin",
    ]
    for mount in plan.mounts:
        args.extend(["--ro-bind", str(mount.source), mount.destination])
    for name, value in SAFE_ENVIRONMENT.items():
        args.extend(["--setenv", name, value])
    args.extend(["--chdir", "/sandbox-work", "--", "/usr/bin/python3", INNER_PROBE_PATH])
    return args


def _safe_unresolved_result() -> dict[str, object]:
    result = {
        "schema": "claude-progressive-probe-summary@1",
        "build_pin": {"version": PINNED_VERSION, "sha256": PINNED_SHA256},
        "path_classes": {},
        "type_assertions": {},
        "counts": {},
        "equality_assertions": {},
        "direction_assertions": {},
        "control_totals": {},
        "disposition": "unresolved",
    }
    validate_safe_summary(result)
    return result


def _read_bounded_summary(
    stream: Any,
    payload: bytearray,
    overflow: threading.Event,
    read_failed: threading.Event,
    done: threading.Event,
) -> None:
    try:
        while len(payload) < SAFE_SUMMARY_CAPTURE_BYTES:
            chunk = stream.read(min(SUMMARY_READ_CHUNK_BYTES, SAFE_SUMMARY_CAPTURE_BYTES - len(payload)))
            if not chunk:
                return
            payload.extend(chunk)
        overflow.set()
    except Exception:
        read_failed.set()
    finally:
        done.set()


def _stop_process(process: subprocess.Popen[bytes]) -> None:
    if process.poll() is None:
        process.kill()
    try:
        process.wait(timeout=PROCESS_STOP_TIMEOUT_SECONDS)
    except subprocess.TimeoutExpired:
        return


def _run_bwrap_with_bounded_summary(argv: list[str]) -> bytearray | None:
    process = subprocess.Popen(
        argv,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        env={},
        close_fds=True,
        bufsize=0,
    )
    require(process.stdout is not None, "summary-pipe")
    payload = bytearray()
    overflow = threading.Event()
    read_failed = threading.Event()
    done = threading.Event()
    reader = threading.Thread(
        target=_read_bounded_summary,
        args=(process.stdout, payload, overflow, read_failed, done),
        daemon=True,
    )
    reader.start()
    deadline = time.monotonic() + PROBE_TIMEOUT_SECONDS
    while process.poll() is None and not overflow.is_set() and time.monotonic() < deadline:
        time.sleep(0.05)
    if process.poll() is None:
        _stop_process(process)
    else:
        process.wait(timeout=PROCESS_STOP_TIMEOUT_SECONDS)
    done.wait(timeout=PROCESS_STOP_TIMEOUT_SECONDS)
    reader.join(timeout=0)
    if not done.is_set() or overflow.is_set() or read_failed.is_set() or process.returncode != 0:
        return None
    return payload


def execute_isolated_probe() -> dict[str, object]:
    try:
        assert_attempt_gate_allows_launch()
        target = resolve_claude_executable()
        verify_pinned_build(target)
        require(RUNTIME_DIRECTORY.is_dir(), "probe-code-missing")
        plan = make_safe_plan(target=target, probe_code=RUNTIME_DIRECTORY)
        require(plan.probe_code.resolve() == RUNTIME_DIRECTORY.resolve(), "probe-code-boundary")
        assert_plan_safe(plan)
        bwrap = resolve_trusted_bwrap()
        summary = _run_bwrap_with_bounded_summary(_bwrap_argv(plan, bwrap))
    except (ContainmentRejected, OSError, subprocess.TimeoutExpired):
        return _safe_unresolved_result()
    if summary is None:
        return _safe_unresolved_result()
    try:
        return _parse_summary_bytes(summary)
    except ContainmentRejected:
        return _safe_unresolved_result()


def main() -> int:
    require(sys.argv[1:] == ["--execute"], "cli-contract")
    result = execute_isolated_probe()
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
