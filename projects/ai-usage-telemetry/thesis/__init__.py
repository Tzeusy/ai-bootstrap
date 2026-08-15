"""Disposable, synthetic-only thesis harness.

This package is intentionally not a production service.  It has no runtime,
sink, network, image, or publish surface and is retained only to preserve the
test and evidence trail for the thesis gate.
"""

from .harness import HarnessConfig, ThesisHarness

__all__ = ["HarnessConfig", "ThesisHarness"]
