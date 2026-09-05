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
CODEX_SOURCE_REFS = (
    "https://github.com/openai/codex/blob/be6e8eac029b183056b7e4402879f15d2c85f61b/codex-rs/core/src/thread_manager.rs#L1027-L1097",
    "https://github.com/openai/codex/blob/be6e8eac029b183056b7e4402879f15d2c85f61b/codex-rs/core/src/session/mod.rs#L1359-L1396",
    "https://github.com/openai/codex/blob/be6e8eac029b183056b7e4402879f15d2c85f61b/codex-rs/rollout/src/recorder.rs#L832-L871",
    "https://github.com/openai/codex/blob/be6e8eac029b183056b7e4402879f15d2c85f61b/codex-rs/rollout/src/recorder.rs#L1715-L1734",
)
CAPTURE_CONTROL_EVIDENCE = {
    "positive_canary_execution": "executed-isolated-content-free-harness",
    "negative_control_execution": "executed-isolated-content-free-harness",
    "rejection_boundary": "before-synthetic-value-touch-or-external-operation",
    "scope": "candidate-only-no-production-parser-or-producer",
    "limitation": "does-not-prove-producer-or-production-parser-behavior",
}


def require(condition: bool, code: str) -> None:
    if not condition:
        raise AssertionError(code)


def require_exact_keys(value: Any, expected: set[str], code: str) -> dict[str, Any]:
    require(isinstance(value, dict), f"{code}-object")
    require(set(value) == expected, code)
    return value


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


def verify_fixture_shape(data: dict[str, Any]) -> None:
    require_exact_keys(
        data,
        {
            "format",
            "fixture_id",
            "fixture_class",
            "safety",
            "pins",
            "oracles",
            "claude_cases",
            "codex_cases",
        },
        "fixture-top-level-keys",
    )
    safety = require_exact_keys(
        data["safety"],
        {
            "personal_source_opened",
            "credential_material_opened",
            "real_mount_opened",
            "sink_or_network_executed",
            "content_bearing_values_present",
            "canary_lanes",
            "negative_mutations",
            "capture_control_evidence",
        },
        "fixture-safety-keys",
    )
    require_exact_keys(safety["canary_lanes"], set(CANARY_LANES), "fixture-canary-keys")
    require_exact_keys(
        safety["capture_control_evidence"],
        set(CAPTURE_CONTROL_EVIDENCE),
        "fixture-capture-control-evidence-keys",
    )

    pins = require_exact_keys(data["pins"], {"claude_code", "codex", "tokscale"}, "fixture-pin-keys")
    require_exact_keys(
        pins["claude_code"],
        {"version", "executable_sha256", "producer_execution", "public_source_refs"},
        "fixture-claude-pin-keys",
    )
    require_exact_keys(
        pins["codex"],
        {
            "version",
            "executable_sha256",
            "annotated_tag",
            "tag_object",
            "peeled_commit",
            "public_source_refs",
        },
        "fixture-codex-pin-keys",
    )
    require_exact_keys(pins["tokscale"], {"commit", "role"}, "fixture-tokscale-pin-keys")

    oracles = require_exact_keys(
        data["oracles"],
        {"claude_collision_oracle", "codex_fork_neutrality_oracle"},
        "fixture-oracle-keys",
    )
    for oracle in oracles.values():
        require_exact_keys(oracle, {"oracle_id", "result"}, "fixture-oracle-entry-keys")

    require(isinstance(data["claude_cases"], list), "fixture-claude-cases-list")
    claude_case_keys = {
        "claude-exact-replay": {
            "case_id",
            "record_identity",
            "message_consistency",
            "source_time",
            "model",
            "amount_movement",
            "producer_confirmation",
            "expected_current_contract",
        },
        "claude-progressive-monotone-unconfirmed": {
            "case_id",
            "record_identity",
            "message_consistency",
            "source_time",
            "model",
            "amount_movement",
            "producer_confirmation",
            "expected_current_contract",
            "candidate_disposition",
        },
        "claude-progressive-nonmonotone-unconfirmed": {
            "case_id",
            "record_identity",
            "message_consistency",
            "source_time",
            "model",
            "amount_movement",
            "producer_confirmation",
            "expected_current_contract",
            "candidate_disposition",
        },
        "claude-progressive-decrease-incomplete": {
            "case_id",
            "record_identity",
            "message_consistency",
            "source_time",
            "model",
            "amount_movement",
            "producer_confirmation",
            "expected_current_contract",
            "candidate_disposition",
        },
        "claude-identity-reuse": {
            "case_id",
            "record_identity",
            "message_consistency",
            "source_time",
            "model",
            "amount_movement",
            "producer_confirmation",
            "expected_current_contract",
        },
        "claude-producer-confirmed-progressive-counterfactual": {
            "case_id",
            "record_identity",
            "message_consistency",
            "source_time",
            "model",
            "amount_movement",
            "producer_confirmation",
            "expected_current_contract",
            "if_confirmed_disposition",
        },
    }
    for case in data["claude_cases"]:
        require(isinstance(case, dict), "fixture-claude-case-object")
        case_id = case.get("case_id")
        require(isinstance(case_id, str) and case_id in claude_case_keys, "fixture-claude-case-id")
        require_exact_keys(case, claude_case_keys[case_id], "fixture-claude-case-keys")

    codex = require_exact_keys(
        data["codex_cases"],
        {
            "source_observation",
            "parent",
            "forks",
            "archived_live_relocation",
            "cumulative_regression",
            "gap_falsifiers",
        },
        "fixture-codex-case-keys",
    )
    require_exact_keys(
        codex["parent"],
        {"case_id", "session", "cumulative_landmark", "semantic_contribution"},
        "fixture-codex-parent-keys",
    )
    require(isinstance(codex["forks"], list), "fixture-codex-forks-list")
    for fork in codex["forks"]:
        require_exact_keys(
            fork,
            {
                "case_id",
                "fork_kind",
                "child_session",
                "child_ownership",
                "copied_parent_landmark",
                "copied_semantic_contribution",
                "timestamp_relation",
                "expected_current_contract",
            },
            "fixture-codex-fork-keys",
        )
    require_exact_keys(
        codex["archived_live_relocation"],
        {"case_id", "identity_inputs", "hypothesis_status", "hypothesis", "expected_current_contract"},
        "fixture-codex-relocation-keys",
    )
    require_exact_keys(
        codex["cumulative_regression"],
        {"case_id", "prior_landmark_rank", "current_landmark_rank", "expected_current_contract"},
        "fixture-codex-regression-keys",
    )


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
    require(safety["capture_control_evidence"] == CAPTURE_CONTROL_EVIDENCE, "capture-control-evidence")


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
    require(tuple(codex["public_source_refs"]) == CODEX_SOURCE_REFS, "codex-source-ref-set")
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
    verify_fixture_shape(data)
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
        lambda altered: altered.update({"unregistered_scalar": "synthetic-only"}),
    )
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
    print("aib-kwx source-semantics structural oracle: PASS; 4 deliberate mutations rejected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
