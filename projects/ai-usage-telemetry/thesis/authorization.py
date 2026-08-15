"""Immutable authorization binding for the disposable synthetic thesis."""

from __future__ import annotations

import hashlib
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]
DECISION_0002_PATH = (
    PROJECT_ROOT
    / "about"
    / "heart-and-soul"
    / "decisions"
    / "0002-accept-v1-capability-contracts.md"
)
SYNTHETIC_SPEC_PATH = (
    PROJECT_ROOT
    / "openspec"
    / "changes"
    / "establish-ai-usage-telemetry-v1"
    / "specs"
    / "synthetic-usage-spine"
    / "spec.md"
)
_SYNTHETIC_ROW = re.compile(
    r"^\|\s*`synthetic-usage-spine`\s*\|\s*`(?P<state>[^`|]+)`\s*\|\s*"
    r"`(?P<digest>[0-9a-f]{64})`\s*\|\s*$",
    re.MULTILINE,
)


class ValidationError(ValueError):
    """Content-free preflight or fixture rejection."""

    def __init__(self, code: str):
        self.code = code
        super().__init__(code)


def validate_synthetic_authorization(
    decision_path: Path = DECISION_0002_PATH,
    spec_path: Path = SYNTHETIC_SPEC_PATH,
) -> None:
    """Require Decision 0002's one accepted binding for the synthetic spec."""

    try:
        decision_bytes = decision_path.read_bytes()
    except OSError:
        raise ValidationError("synthetic_authorization_missing") from None
    try:
        decision = decision_bytes.decode("utf-8")
    except UnicodeDecodeError:
        raise ValidationError("synthetic_authorization_invalid") from None

    rows = tuple(_SYNTHETIC_ROW.finditer(decision))
    if not rows:
        raise ValidationError("synthetic_authorization_missing")
    if len(rows) != 1:
        raise ValidationError("synthetic_authorization_invalid")
    row = rows[0]
    if row.group("state") != "accepted":
        raise ValidationError("synthetic_authorization_not_accepted")

    try:
        spec_bytes = spec_path.read_bytes()
    except OSError:
        raise ValidationError("synthetic_authorization_binding_missing") from None
    actual_digest = hashlib.sha256(spec_bytes).hexdigest()
    if actual_digest != row.group("digest"):
        raise ValidationError("synthetic_authorization_digest_mismatch")
