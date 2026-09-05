# /// script
# requires-python = ">=3.10"
# ///

"""Independent structural oracle for candidate evidence 0003.

It reads only the fully synthetic sibling fixture, receives no command-line
input, starts no subprocess, and performs no network or source traversal.
"""

from __future__ import annotations

from dataclasses import dataclass
import copy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Mapping


FIXTURE_PATH = Path(__file__).with_name("fixture_0003.json")
PINNED_VERSION = "2.1.227"
PINNED_SHA256 = "6832dc3f1797b890b71116e5f2dbbf9a83fd3d0498c235b4b0f9cd0e6e499ad6"
EXPECTED_FIXTURE_SHA256 = "11bc385d4dbb5fb59aea2e53bd3134b42a6aea351ab39146388de3bf6d531b4e"
EXPECTED_CASE_IDS = frozenset(
    {
        "exact-replay",
        "one-request-progressive-stream",
        "changed-timestamp",
        "monotone-counter",
        "decreasing-counter",
        "malformed-record",
        "incomplete-record",
        "nonconforming-identity-reuse",
    }
)
CASE_KEYS = {
    "case_id",
    "record_shape",
    "native_pair_relation",
    "timestamp_relation",
    "message_relation",
    "model_relation",
    "counter_direction",
    "expected_disposition",
}


@dataclass(frozen=True)
class OracleResult:
    case_count: int
    deliberate_mutation_rejections: int


def require(condition: bool, code: str) -> None:
    if not condition:
        raise AssertionError(code)


def load_fixture() -> dict[str, Any]:
    raw = FIXTURE_PATH.read_bytes()
    require(len(raw) <= 16_384, "fixture-size")
    require(hashlib.sha256(raw).hexdigest() == EXPECTED_FIXTURE_SHA256, "fixture-digest")
    value = json.loads(raw)
    require(isinstance(value, dict), "fixture-object")
    return value


def _classify(case: Mapping[str, object]) -> str:
    if case["record_shape"] == "malformed":
        return "recognized-malformed"
    if case["record_shape"] == "incomplete":
        return "incomplete-tail"
    if (
        case["native_pair_relation"] == "same"
        and case["timestamp_relation"] == "same"
        and case["message_relation"] == "same"
        and case["model_relation"] == "same"
        and case["counter_direction"] == "same"
    ):
        return "duplicate"
    if (
        case["native_pair_relation"] == "same"
        and case["timestamp_relation"] == "changed"
        and case["message_relation"] == "same"
        and case["model_relation"] == "same"
        and case["counter_direction"] == "monotone-increase"
    ):
        return "confirmed-contract-gap"
    return "identity-collision"


def _verify_shape(value: Mapping[str, Any]) -> None:
    require(set(value) == {"schema", "build", "probe_contract", "cases"}, "fixture-keys")
    require(value["schema"] == "claude-progressive-probe-fixture@1", "fixture-schema")
    require(value["build"] == {"version": PINNED_VERSION, "sha256": PINNED_SHA256}, "fixture-build")
    contract = value["probe_contract"]
    require(isinstance(contract, dict), "fixture-contract-object")
    require(
        contract
        == {
            "target_invocation_count": 1,
            "namespace_types": ["user", "pid", "net"],
            "network_scope": "loopback-only",
            "output_scope": "sandbox-tmpfs-only",
            "disposition_on_insufficient_evidence": "unresolved",
        },
        "fixture-contract",
    )
    cases = value["cases"]
    require(isinstance(cases, list), "fixture-cases-object")
    seen: set[str] = set()
    for case in cases:
        require(isinstance(case, dict), "case-object")
        require(set(case) == CASE_KEYS, "case-keys")
        case_id = case["case_id"]
        require(isinstance(case_id, str) and case_id not in seen, "case-id")
        seen.add(case_id)
        require(case["expected_disposition"] == _classify(case), "case-disposition")
    require(seen == EXPECTED_CASE_IDS, "case-coverage")


def _assert_mutation_rejected(value: Mapping[str, Any], mutate) -> None:
    candidate = copy.deepcopy(value)
    mutate(candidate)
    try:
        _verify_shape(candidate)
    except AssertionError:
        return
    raise AssertionError("mutation-accepted")


def _verify_deliberate_mutations(value: Mapping[str, Any]) -> int:
    mutations = (
        lambda candidate: candidate.update({"unregistered_scalar": "synthetic-only"}),
        lambda candidate: next(item for item in candidate["cases"] if item["case_id"] == "exact-replay").update(
            {"timestamp_relation": "changed"}
        ),
        lambda candidate: next(
            item for item in candidate["cases"] if item["case_id"] == "one-request-progressive-stream"
        ).update({"message_relation": "changed"}),
        lambda candidate: candidate.update({"cases": candidate["cases"][:-1]}),
    )
    for mutation in mutations:
        _assert_mutation_rejected(value, mutation)
    return len(mutations)


def verify_fixture(value: Mapping[str, Any]) -> OracleResult:
    _verify_shape(value)
    return OracleResult(
        case_count=len(value["cases"]),
        deliberate_mutation_rejections=_verify_deliberate_mutations(value),
    )


def main() -> int:
    require(len(sys.argv) == 1, "no-cli-input")
    result = verify_fixture(load_fixture())
    print(
        "candidate-0003 structural oracle: PASS; "
        f"{result.case_count} predeclared cases; "
        f"{result.deliberate_mutation_rejections} deliberate mutations rejected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
