# /// script
# requires-python = ">=3.10"
# ///

"""Execute the isolated content-free capture controls for candidate evidence 0002.

This is deliberately not a source producer, parser, mount, credential reader,
or network client. It exercises the candidate's safe canary registry and each
negative-control rejection before an opaque synthetic value can be touched.
"""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable


FIXTURE_PATH = Path(__file__).with_name("0002-source-semantics-fixtures.json")
EXPECTED_FIXTURE_SHA256 = "4c8c4f16609bf719d22c888197be2c9a37ac64fe3978b1750ecddf9fc7086568"
CANARY_LANES = (
    "application_value",
    "decoder",
    "parser",
    "log",
    "exception",
    "output_capture",
    "crash_output",
    "sqlite",
    "otlp",
    "postgresql",
    "image_layer",
    "filesystem",
    "environment",
    "packet_network",
)
NEGATIVE_CONTROLS = (
    "content-decode",
    "forbidden-decoder-materializer",
    "sentinel-egress",
    "credential-access",
    "broad-root-access",
    "unexpected-network",
)
CONTROL_EVIDENCE = {
    "positive_canary_execution": "executed-isolated-content-free-harness",
    "negative_control_execution": "executed-isolated-content-free-harness",
    "rejection_boundary": "before-synthetic-value-touch-or-external-operation",
    "scope": "candidate-only-no-production-parser-or-producer",
    "limitation": "does-not-prove-producer-or-production-parser-behavior",
}


def require(condition: bool, code: str) -> None:
    if not condition:
        raise AssertionError(code)


def load_fixture() -> dict[str, Any]:
    raw = FIXTURE_PATH.read_bytes()
    require(len(raw) <= 32_768, "fixture-size-bound")
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_FIXTURE_SHA256, "fixture-digest")
    value = json.loads(raw)
    require(isinstance(value, dict), "fixture-object")
    return value


class ControlRejected(RuntimeError):
    """A candidate-only guard rejected an action before its value was observed."""


class OpaqueSyntheticValue:
    """Fails visibly if a guard tries to materialize the value it must reject."""

    def __init__(self) -> None:
        self.touches = 0

    def _touch(self) -> None:
        self.touches += 1
        raise AssertionError("synthetic-value-touched")

    def __bytes__(self) -> bytes:
        self._touch()

    def __repr__(self) -> str:
        self._touch()

    def __str__(self) -> str:
        self._touch()


@dataclass(frozen=True)
class CaptureControlResult:
    positive_canary_lanes: tuple[str, ...]
    rejected_controls: tuple[str, ...]
    synthetic_value_touches: int


class ContentFreeCaptureHarness:
    def __init__(self) -> None:
        self.positive_canary_lanes: list[str] = []
        self.rejected_controls: list[str] = []

    def observe_canary(self, lane: str, value: str) -> None:
        require(lane in CANARY_LANES, "unknown-canary-lane")
        require(value == f"canary-{lane.replace('_', '-')}", "unexpected-canary-value")
        self.positive_canary_lanes.append(lane)

    def reject_before_value_touch(self, control: str, value: OpaqueSyntheticValue) -> None:
        require(control in NEGATIVE_CONTROLS, "unknown-negative-control")
        del value
        self.rejected_controls.append(control)
        raise ControlRejected(f"{control}-rejected-before-touch")

    def reject_content_decode(self, value: OpaqueSyntheticValue) -> None:
        self.reject_before_value_touch("content-decode", value)

    def reject_forbidden_decoder_materializer(self, value: OpaqueSyntheticValue) -> None:
        self.reject_before_value_touch("forbidden-decoder-materializer", value)

    def reject_sentinel_egress(self, value: OpaqueSyntheticValue) -> None:
        self.reject_before_value_touch("sentinel-egress", value)

    def reject_credential_access(self, value: OpaqueSyntheticValue) -> None:
        self.reject_before_value_touch("credential-access", value)

    def reject_broad_root_access(self, value: OpaqueSyntheticValue) -> None:
        self.reject_before_value_touch("broad-root-access", value)

    def reject_unexpected_network(self, value: OpaqueSyntheticValue) -> None:
        self.reject_before_value_touch("unexpected-network", value)

    def negative_operations(self) -> dict[str, Callable[[OpaqueSyntheticValue], None]]:
        return {
            "content-decode": self.reject_content_decode,
            "forbidden-decoder-materializer": self.reject_forbidden_decoder_materializer,
            "sentinel-egress": self.reject_sentinel_egress,
            "credential-access": self.reject_credential_access,
            "broad-root-access": self.reject_broad_root_access,
            "unexpected-network": self.reject_unexpected_network,
        }


def run_capture_controls() -> CaptureControlResult:
    data = load_fixture()
    safety = data["safety"]
    require(tuple(safety["canary_lanes"]) == CANARY_LANES, "canary-lane-set")
    require(tuple(safety["negative_mutations"]) == NEGATIVE_CONTROLS, "negative-control-set")
    require(safety["capture_control_evidence"] == CONTROL_EVIDENCE, "capture-control-evidence")

    harness = ContentFreeCaptureHarness()
    for lane in CANARY_LANES:
        harness.observe_canary(lane, safety["canary_lanes"][lane])

    total_touches = 0
    for control in NEGATIVE_CONTROLS:
        opaque_value = OpaqueSyntheticValue()
        try:
            harness.negative_operations()[control](opaque_value)
        except ControlRejected as error:
            require(str(error) == f"{control}-rejected-before-touch", "wrong-control-rejection")
        else:
            raise AssertionError("negative-control-accepted")
        require(opaque_value.touches == 0, "synthetic-value-touched")
        total_touches += opaque_value.touches

    require(tuple(harness.positive_canary_lanes) == CANARY_LANES, "canary-not-observed")
    require(tuple(harness.rejected_controls) == NEGATIVE_CONTROLS, "negative-control-not-exercised")
    return CaptureControlResult(
        positive_canary_lanes=tuple(harness.positive_canary_lanes),
        rejected_controls=tuple(harness.rejected_controls),
        synthetic_value_touches=total_touches,
    )


def main() -> int:
    require(len(sys.argv) == 1, "no-cli-input")
    result = run_capture_controls()
    print(
        "aib-kwx content-free capture controls: PASS; "
        f"{len(result.positive_canary_lanes)} canary lanes exercised; "
        f"{len(result.rejected_controls)} negative controls rejected; "
        f"{result.synthetic_value_touches} synthetic value touches"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
