# /// script
# requires-python = ">=3.10"
# ///

"""Exercise every candidate-0003 containment mutation without launching Claude."""

from __future__ import annotations

from dataclasses import dataclass
import importlib.util
from pathlib import Path
import sys


EVIDENCE_DIRECTORY = Path(__file__).resolve().parent
PROBE_PATH = EVIDENCE_DIRECTORY / "claude_progressive_probe_0003.py"


def load_probe():
    spec = importlib.util.spec_from_file_location("claude_progressive_probe_controls", PROBE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("probe-module-unavailable")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


@dataclass(frozen=True)
class CaptureControlResult:
    rejected_mutations: int
    target_launches: int


class RecordingLauncher:
    def __init__(self) -> None:
        self.calls = 0

    def __call__(self, _plan: object) -> None:
        self.calls += 1


def run_capture_controls() -> CaptureControlResult:
    probe = load_probe()
    plan = probe.make_safe_plan(
        target=Path("/exact-target/claude"),
        probe_code=Path("/candidate-only-probe"),
    )
    mutations = (
        lambda value: value.replace(namespaces=frozenset({"user", "pid"})),
        lambda value: value.with_mount(
            probe.MountRule("ro-bind", Path("/host-home/.config"), "/sandbox-home/.config", "forbidden")
        ),
        lambda value: value.with_mount(probe.MountRule("ro-bind", Path("/workspace"), "/source", "forbidden")),
        lambda value: value.replace(forwarded_environment={"HTTPS_PROXY": "synthetic-proxy"}),
        lambda value: value.replace(network_mode="non-loopback-route"),
        lambda value: value.replace(target_output="host-capture"),
        lambda value: value,
    )
    launcher = RecordingLauncher()
    rejected = 0
    for index, mutation in enumerate(mutations):
        try:
            probe.launch_if_safe(
                mutation(plan),
                pin_checker=(lambda _target, index=index: index != len(mutations) - 1),
                launcher=launcher,
            )
        except probe.ContainmentRejected:
            rejected += 1
        else:
            raise AssertionError("mutation-accepted")
    if launcher.calls != 0:
        raise AssertionError("target-launched-during-control")
    return CaptureControlResult(rejected_mutations=rejected, target_launches=launcher.calls)


def main() -> int:
    if len(sys.argv) != 1:
        raise SystemExit("capture-controls-accept-no-arguments")
    result = run_capture_controls()
    print(
        "candidate-0003 capture controls: PASS; "
        f"{result.rejected_mutations} containment mutations rejected; "
        f"{result.target_launches} target launches"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
