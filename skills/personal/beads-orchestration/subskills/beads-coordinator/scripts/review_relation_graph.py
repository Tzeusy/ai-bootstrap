#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate normalized PR-review task relations without side effects."""

from __future__ import annotations

from collections.abc import Iterable


def review_relation_error(relations: Iterable[tuple[str, str]]) -> str | None:
    """Return a safe error code when review-task relations are ambiguous or cyclic.

    A relation points from a review-task ID to the original ID returned by the
    canonical resolver. Original IDs that are not review tasks are terminal
    nodes. The caller owns identifier-format validation; this seam validates
    only the graph shape and deliberately performs no I/O.
    """
    relations_by_review: dict[str, str] = {}
    for review_id, original_id in relations:
        if not isinstance(review_id, str) or not review_id:
            return "invalid-review-relation"
        if not isinstance(original_id, str) or not original_id:
            return "invalid-review-relation"
        if review_id == original_id:
            return "self-referential-review-id"
        if review_id in relations_by_review:
            return "ambiguous-review-relation"
        relations_by_review[review_id] = original_id

    visited: set[str] = set()
    for start_review_id in sorted(relations_by_review):
        if start_review_id in visited:
            continue
        path: set[str] = set()
        review_id = start_review_id
        while review_id in relations_by_review and review_id not in visited:
            if review_id in path:
                return "cyclic-review-relation"
            path.add(review_id)
            review_id = relations_by_review[review_id]
        visited.update(path)
    return None
