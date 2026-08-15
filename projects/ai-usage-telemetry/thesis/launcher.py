"""Disposable launcher for the synthetic thesis only.

``launch`` validates Decision 0002's accepted synthetic-spec binding before it
constructs the harness. The harness then preflights before the manifest,
fixture, database, or any other thesis resource is opened. No production caller
imports this module.
"""

from __future__ import annotations

from .authorization import validate_synthetic_authorization
from .harness import HarnessConfig, RunResult, ThesisHarness


def launch(config: HarnessConfig) -> RunResult:
    """Run one qualified synthetic record after side-effect-free preflight."""

    validate_synthetic_authorization()
    return ThesisHarness(config).run_once()
