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
from typing import Any, Callable, Iterable, Mapping


PINNED_VERSION = "2.1.227"
PINNED_SHA256 = "6832dc3f1797b890b71116e5f2dbbf9a83fd3d0498c235b4b0f9cd0e6e499ad6"
EVIDENCE_DIRECTORY = Path(__file__).resolve().parent
FIXTURE_PATH = EVIDENCE_DIRECTORY / "fixture_0003.json"
RUNTIME_DIRECTORY = EVIDENCE_DIRECTORY / "runtime"
INNER_PROBE_PATH = "/probe/runtime/inner_probe_0003.py"
SYNTHETIC_TARGET_PATH = "/opt/claude/claude"
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
        while True:
            key = self._read_key()
            self._skip_whitespace()
            self._expect(ord(":"))
            next_path = _next_safe_path(path, key)
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
        start = self.index
        while self.index < len(self.raw) and self.raw[self.index] in b"0123456789":
            self.index += 1
        if start == self.index:
            raise ValueError("expected-integer")
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
                raise ValueError("invalid-string")
        raise ValueError("unterminated-string")

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
                raise ValueError("invalid-scalar")

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
    raw_markers = ("raw", "stdout", "stderr", "prompt", "response", "header", "session", "requestid", "identity")
    for key in value:
        require(not any(marker in key.casefold() for marker in raw_markers), "summary-privacy-key")


def _parse_summary_bytes(raw: bytes) -> dict[str, object]:
    require(len(raw) <= 16_384, "summary-size")
    try:
        value = json.loads(raw)
    except (UnicodeDecodeError, json.JSONDecodeError) as error:
        raise ContainmentRejected("summary-json") from error
    require(isinstance(value, dict), "summary-object")
    validate_safe_summary(value)
    return value


def _bwrap_argv(plan: ProbePlan, bwrap: str) -> list[str]:
    args = [
        bwrap,
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
    return {
        "schema": "claude-progressive-probe-summary@1",
        "build_pin": {"version": PINNED_VERSION, "sha256": PINNED_SHA256},
        "path_classes": {"execution": "not-started-or-unverified"},
        "type_assertions": {},
        "counts": {},
        "equality_assertions": {},
        "direction_assertions": {},
        "control_totals": {},
        "disposition": "unresolved",
    }


def execute_isolated_probe() -> dict[str, object]:
    try:
        target = resolve_claude_executable()
        verify_pinned_build(target)
        require(RUNTIME_DIRECTORY.is_dir(), "probe-code-missing")
        plan = make_safe_plan(target=target, probe_code=RUNTIME_DIRECTORY)
        require(plan.probe_code.resolve() == RUNTIME_DIRECTORY.resolve(), "probe-code-boundary")
        assert_plan_safe(plan)
        bwrap = shutil.which("bwrap")
        require(bwrap is not None, "bubblewrap-missing")
        completed = subprocess.run(
            _bwrap_argv(plan, bwrap),
            check=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env={},
            timeout=90,
        )
    except (ContainmentRejected, OSError, subprocess.TimeoutExpired):
        return _safe_unresolved_result()
    if completed.returncode != 0:
        return _safe_unresolved_result()
    return _parse_summary_bytes(completed.stdout)


def main() -> int:
    require(sys.argv[1:] == ["--execute"], "cli-contract")
    result = execute_isolated_probe()
    print(json.dumps(result, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
