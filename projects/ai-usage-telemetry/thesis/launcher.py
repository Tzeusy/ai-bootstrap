"""Disposable launcher for the synthetic thesis only.

``launch`` constructs the harness, whose preflight runs before the manifest,
fixture, database, or any other resource is opened.  No production caller
imports this module.
"""

from __future__ import annotations

from .harness import HarnessConfig, RunResult, ThesisHarness


def launch(config: HarnessConfig) -> RunResult:
    """Run one qualified synthetic record after side-effect-free preflight."""

    return ThesisHarness(config).run_once()
