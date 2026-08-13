from __future__ import annotations

import importlib.util
import re
from pathlib import Path

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "validate_questionnaire.py"
VALID_PACKET = Path(__file__).parent / "fixtures" / "review-ready.md"


def _load_validator():
    spec = importlib.util.spec_from_file_location("validate_questionnaire", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def validator():
    return _load_validator()


@pytest.fixture
def valid_packet() -> str:
    return VALID_PACKET.read_text(encoding="utf-8")


def test_accepts_a_complete_review_ready_packet(validator, valid_packet):
    assert validator.validate_packet(valid_packet, require_review_ready=True) == []


def test_rejects_review_ready_packet_without_independent_scope_and_recommendation_verdicts(
    validator, valid_packet
):
    packet = valid_packet.replace(
        "- Scope verdict: Pass — bounded to the authority decision.\n"
        "- Recommendation verdict: Pass — option A best fits the cited contract.\n",
        "",
    )

    errors = validator.validate_packet(packet, require_review_ready=True)

    assert any("Scope verdict" in error for error in errors)
    assert any("Recommendation verdict" in error for error in errors)


def test_rejects_duplicate_decision_ids(validator, valid_packet):
    duplicate = valid_packet + valid_packet[valid_packet.index("### `dec-auth`") :]

    errors = validator.validate_packet(duplicate)

    assert any("duplicate decision section id `dec-auth`" in error for error in errors)


def test_rejects_missing_required_section(validator, valid_packet):
    packet = valid_packet.replace("#### Authorization boundary", "#### Boundary")

    errors = validator.validate_packet(packet)

    assert any("missing section: Authorization boundary" in error for error in errors)


@pytest.mark.parametrize("placeholder", ["TODO", "TBD", "<REVIEWER_ID>"])
def test_rejects_unresolved_placeholders(validator, valid_packet, placeholder):
    packet = valid_packet.replace("Choose the sole credential authority.", placeholder)

    errors = validator.validate_packet(packet)

    assert any("unresolved placeholder" in error for error in errors)


def test_require_review_ready_rejects_draft_items(validator, valid_packet):
    packet = valid_packet.replace("Review-ready", "Draft")

    errors = validator.validate_packet(packet, require_review_ready=True)

    assert any("not ready for owner review" in error for error in errors)


def test_rejects_unknown_decision_state(validator, valid_packet):
    packet = valid_packet.replace("Review-ready", "Maybe")

    errors = validator.validate_packet(packet)

    assert any("unknown Decision state" in error for error in errors)


def test_rejects_fewer_than_two_options(validator, valid_packet):
    packet = valid_packet.replace("| B. Local authority | Small change | Reintroduces split brain |\n", "")

    errors = validator.validate_packet(packet)

    assert any("must present 2-4 concrete options" in error for error in errors)


def test_rejects_nonpassing_review_verdict(validator, valid_packet):
    packet = valid_packet.replace(
        "Scope verdict: Pass — bounded to the authority decision.",
        "Scope verdict: Revise — authority boundary is too broad.",
    )

    errors = validator.validate_packet(packet)

    assert any("Scope verdict must be exactly Pass" in error for error in errors)


def test_rejects_pass_prefix_bypass(validator, valid_packet):
    packet = valid_packet.replace("Scope verdict: Pass —", "Scope verdict: Passable —")

    errors = validator.validate_packet(packet)

    assert any("Scope verdict must be exactly Pass" in error for error in errors)


def test_rejects_mismatched_or_pending_reviewer(validator, valid_packet):
    mismatched = valid_packet.replace("- Reviewer: `review-scope-1`", "- Reviewer: `other-reviewer`")
    pending = valid_packet.replace("- Reviewer: `review-scope-1`", "- Reviewer: Pending")

    assert any("reviewer identity does not match" in error for error in validator.validate_packet(mismatched))
    assert any("valid Reviewer" in error for error in validator.validate_packet(pending))


@pytest.mark.parametrize("reserved", ["Pending", "TODO", "TBD", "unknown"])
def test_rejects_reserved_reviewer_ids_even_when_backticked(validator, valid_packet, reserved):
    packet = valid_packet.replace("`review-scope-1`", f"`{reserved}`")

    errors = validator.validate_packet(packet)

    assert any("reserved Reviewer id" in error for error in errors)


@pytest.mark.parametrize("label", ["Material corrections", "Evidence freshness"])
def test_rejects_missing_review_record_fields(validator, valid_packet, label):
    packet = re.sub(rf"^- {label}:.*\n", "", valid_packet, flags=re.MULTILINE)

    errors = validator.validate_packet(packet)

    assert any(label in error for error in errors)


def test_rejects_duplicate_option_labels(validator, valid_packet):
    packet = valid_packet.replace("| B. Local authority", "| A. Local authority")

    errors = validator.validate_packet(packet)

    assert any("duplicate option labels" in error for error in errors)


@pytest.mark.parametrize(
    "row",
    [
        "| A.  | One writer | Requires migration |",
        "| A. Shared authority |  | Requires migration |",
        "| A. Shared authority | One writer |  |",
    ],
)
def test_rejects_blank_option_outcome_pros_or_cons(validator, valid_packet, row):
    packet = valid_packet.replace(
        "| A. Shared authority | One writer | Requires migration |",
        row,
    )

    errors = validator.validate_packet(packet)

    assert any("option A needs non-empty outcome, pros, and cons" in error for error in errors)


def test_rejects_recommendation_for_absent_option(validator, valid_packet):
    packet = valid_packet.replace("Choose **A**", "Choose **C**")

    errors = validator.validate_packet(packet)

    assert any("selects absent option C" in error for error in errors)


def test_rejects_empty_required_body_and_evidence(validator, valid_packet):
    packet = valid_packet.replace("#### Evidence\n\n- `spec.md:42`", "#### Evidence\n")

    errors = validator.validate_packet(packet)

    assert any("Evidence body is empty" in error for error in errors)


def test_agreed_item_requires_complete_owner_decision_record(validator, valid_packet):
    packet = valid_packet.replace("Review-ready", "Agreed")

    errors = validator.validate_packet(packet)

    assert any("owner decision field Actor/channel is still pending" in error for error in errors)


def test_accepts_agreed_item_with_complete_owner_decision_record(validator, valid_packet):
    packet = valid_packet.replace("Review-ready", "Agreed")
    replacements = {
        "Status: Pending owner response": "Status: Agreed",
        "Actor/channel: Pending owner response": "Actor/channel: owner via authenticated chat",
        "Recorded at: Pending owner response": "Recorded at: 2026-08-13T10:00:00+08:00",
        "Choice: Pending owner response": "Choice: A",
        "Post-answer review: Pending owner response": (
            "Post-answer review: Not required — chose an existing option"
        ),
        "Final authorization boundary: Pending owner response": (
            "Final authorization boundary: record and route specification work only"
        ),
        "Canonical destination: Pending owner response": (
            "Canonical destination: project-feature-request"
        ),
    }
    for old, new in replacements.items():
        packet = packet.replace(old, new)

    assert validator.validate_packet(packet, require_review_ready=True) == []


def test_edited_agreement_requires_post_answer_review(validator, valid_packet):
    packet = valid_packet.replace("Review-ready", "Agreed")
    replacements = {
        "Status: Pending owner response": "Status: Agreed",
        "Actor/channel: Pending owner response": "Actor/channel: owner via authenticated chat",
        "Recorded at: Pending owner response": "Recorded at: 2026-08-13T10:00:00+08:00",
        "Choice: Pending owner response": "Choice: Edited: A without restart",
        "Owner edits: None": "Owner edits: Explicitly excluded restart",
        "Final authorization boundary: Pending owner response": (
            "Final authorization boundary: specification work only"
        ),
        "Canonical destination: Pending owner response": (
            "Canonical destination: project-feature-request"
        ),
    }
    for old, new in replacements.items():
        packet = packet.replace(old, new)

    errors = validator.validate_packet(packet)

    assert any("edited owner choice requires a passed post-answer review" in error for error in errors)
