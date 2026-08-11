# /// script
# requires-python = ">=3.10"
# ///

"""Verify the content-free structural oracle for candidate evidence 0002.

This checker reads only its sibling synthetic fixture. It does not inspect a
client installation, environment, source tree, mount, credential store, or
network endpoint.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any, Callable


FIXTURE_PATH = Path(__file__).with_name("0002-source-semantics-fixtures.json")
EXPECTED_FIXTURE_SHA256 = "ee1504d3327088e00c8fdcaa07009f99ef80ad37cbc037858c25a2563a37c31b"
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
FORBIDDEN_KEYS = {
    "prompt",
    "response",
    "message",
    "transcript",
    "record_bytes",
    "credential",
    "secret_value",
    "local_path",
}


def require(condition: bool, code: str) -> None:
    if not condition:
        raise AssertionError(code)


def load_fixture() -> dict[str, Any]:
    require(len(sys.argv) == 1, "no-cli-input")
    raw = FIXTURE_PATH.read_bytes()
    require(len(raw) <= 32_768, "fixture-size-bound")
    digest = hashlib.sha256(raw).hexdigest()
    require(digest == EXPECTED_FIXTURE_SHA256, "fixture-digest")
    value = json.loads(raw)
    require(isinstance(value, dict), "fixture-object")
    return value


def assert_content_free(value: Any) -> None:
    if isinstance(value, dict):
        require(not (FORBIDDEN_KEYS & set(value)), "forbidden-fixture-key")
        for child in value.values():
            assert_content_free(child)
    elif isinstance(value, list):
        for child in value:
            assert_content_free(child)
    else:
        require(isinstance(value, (str, int, bool)), "fixture-scalar")


def verify_safety(data: dict[str, Any]) -> None:
    safety = data["safety"]
    for key in (
        "personal_source_opened",
        "credential_material_opened",
        "real_mount_opened",
        "sink_or_network_executed",
        "content_bearing_values_present",
    ):
        require(safety[key] is False, "unsafe-evidence-boundary")
    canaries = safety["canary_lanes"]
    require(tuple(canaries) == CANARY_LANES, "canary-lane-set")
    for lane in CANARY_LANES:
        require(canaries[lane] == f"canary-{lane.replace('_', '-')}", "canary-label")
    require(
        safety["negative_mutations"]
        == [
            "content-decode",
            "forbidden-decoder-materializer",
            "sentinel-egress",
            "credential-access",
            "broad-root-access",
            "unexpected-network",
        ],
        "negative-mutation-set",
    )


def verify_pins(data: dict[str, Any]) -> None:
    pins = data["pins"]
    claude = pins["claude_code"]
    codex = pins["codex"]
    require(claude["version"] == "2.1.227", "claude-version")
    require(len(claude["executable_sha256"]) == 64, "claude-digest-shape")
    require(claude["producer_execution"] == "not-run", "claude-execution-boundary")
    require(codex["version"] == "0.147.0", "codex-version")
    require(codex["annotated_tag"] == "rust-v0.147.0", "codex-tag")
    require(len(codex["peeled_commit"]) == 40, "codex-commit-shape")
    require(len(codex["public_source_refs"]) == 4, "codex-source-ref-set")
    require(
        pins["tokscale"] == {
            "commit": "9814fa49e8ba32b19d94ef2b1545b66b17944435",
            "role": "comparative-only-not-downloaded-or-executed",
        },
        "tokscale-boundary",
    )


def verify_claude(data: dict[str, Any]) -> None:
    cases = {case["case_id"]: case for case in data["claude_cases"]}
    expected_ids = {
        "claude-exact-replay",
        "claude-progressive-monotone-unconfirmed",
        "claude-progressive-nonmonotone-unconfirmed",
        "claude-progressive-decrease-incomplete",
        "claude-identity-reuse",
        "claude-producer-confirmed-progressive-counterfactual",
    }
    require(set(cases) == expected_ids, "claude-case-set")

    replay = cases["claude-exact-replay"]
    require(
        all(replay[field] == "same" for field in ("message_consistency", "source_time", "model", "amount_movement")),
        "claude-replay-structure",
    )
    require(replay["expected_current_contract"] == "duplicate", "claude-replay-outcome")

    for case_id in (
        "claude-progressive-monotone-unconfirmed",
        "claude-progressive-nonmonotone-unconfirmed",
    ):
        case = cases[case_id]
        require(case["producer_confirmation"] == "required-not-present", "claude-unresolved-proof")
        require(case["expected_current_contract"] == "identity-collision", "claude-current-contract")
        require(case["candidate_disposition"] == "unresolved-no-admission", "claude-no-admission")

    incomplete = cases["claude-progressive-decrease-incomplete"]
    require(incomplete["amount_movement"] == "decrease", "claude-decrease-case")
    require(incomplete["expected_current_contract"] == "incomplete-tail-hold", "claude-incomplete-hold")

    reused = cases["claude-identity-reuse"]
    require(reused["expected_current_contract"] == "identity-collision", "claude-reuse-collision")
    counterfactual = cases["claude-producer-confirmed-progressive-counterfactual"]
    require(counterfactual["producer_confirmation"] == "counterfactual-only", "claude-counterfactual-boundary")
    require(counterfactual["if_confirmed_disposition"] == "requires-contract-amendment", "claude-amendment-gate")


def verify_oracles(data: dict[str, Any]) -> None:
    oracles = data["oracles"]
    require(
        oracles["claude_collision_oracle"]
        == {"oracle_id": "claude-collision-oracle", "result": "unresolved"},
        "claude-oracle-disposition",
    )
    require(
        oracles["codex_fork_neutrality_oracle"]
        == {"oracle_id": "codex-fork-neutrality-oracle", "result": "confirmed-contract-gap"},
        "codex-oracle-disposition",
    )


def verify_codex(data: dict[str, Any]) -> None:
    codex = data["codex_cases"]
    parent = codex["parent"]
    require(codex["source_observation"] == "confirmed-public-source", "codex-source-observation")
    require(parent["case_id"] == "codex-original-contribution", "codex-original-case")
    require(len(codex["forks"]) == 3, "codex-fork-case-count")
    for fork in codex["forks"]:
        native_identity = (fork["child_session"], fork["copied_parent_landmark"])
        parent_native_identity = (parent["session"], parent["cumulative_landmark"])
        semantic_identity = (fork["copied_semantic_contribution"], fork["copied_parent_landmark"])
        parent_semantic_identity = (parent["semantic_contribution"], parent["cumulative_landmark"])
        require(native_identity != parent_native_identity, "codex-child-native-identity")
        require(semantic_identity == parent_semantic_identity, "codex-copied-semantic-identity")
        require(fork["child_ownership"] == "first-child-owned", "codex-child-ownership")
        require(fork["expected_current_contract"] == "contract-gap", "codex-contract-gap")
    relocation = codex["archived_live_relocation"]
    require(relocation["hypothesis_status"] == "unresolved", "codex-relocation-limit")
    require(
        relocation["expected_current_contract"] == "requires-reconciliation-evidence",
        "codex-relocation-outcome",
    )
    require(relocation["hypothesis"] == "archived-live-duplication", "codex-duplication-hypothesis")
    regression = codex["cumulative_regression"]
    require(regression["current_landmark_rank"] < regression["prior_landmark_rank"], "codex-regression-shape")
    require(regression["expected_current_contract"] == "recognized-malformed-hold", "codex-regression-outcome")
    require(len(codex["gap_falsifiers"]) == 3, "codex-falsifier-set")


def verify_structure(data: dict[str, Any]) -> None:
    require(data["format"] == "aiut-source-semantics-fixture/v1", "fixture-format")
    require(data["fixture_class"] == "synthetic-structural-content-free", "fixture-class")
    assert_content_free(data)
    verify_safety(data)
    verify_pins(data)
    verify_claude(data)
    verify_oracles(data)
    verify_codex(data)


def assert_rejected_mutation(data: dict[str, Any], mutate: Callable[[dict[str, Any]], None]) -> None:
    altered = deepcopy(data)
    mutate(altered)
    try:
        verify_structure(altered)
    except AssertionError:
        return
    raise AssertionError("mutation-not-rejected")


def verify_mutation_oracles(data: dict[str, Any]) -> None:
    assert_rejected_mutation(
        data,
        lambda altered: altered["codex_cases"]["forks"][0].update(
            {"child_session": altered["codex_cases"]["parent"]["session"]}
        ),
    )
    assert_rejected_mutation(
        data,
        lambda altered: altered["safety"]["canary_lanes"].update({"decoder": "mutated"}),
    )
    assert_rejected_mutation(
        data,
        lambda altered: next(
            case for case in altered["claude_cases"] if case["case_id"] == "claude-exact-replay"
        ).update({"source_time": "changed"}),
    )


def main() -> int:
    data = load_fixture()
    verify_structure(data)
    verify_mutation_oracles(data)
    print("aib-kwx source-semantics structural oracle: PASS; 3 deliberate mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
