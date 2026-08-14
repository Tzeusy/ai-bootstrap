#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Validate normalized PR-review task relations without side effects."""

from __future__ import annotations


def review_relation_error(relations: object) -> str | None:
    """Return a safe error code for one complete collection of task relations.

    A relation is exactly a ``(review_id, original_id)`` tuple. Reusing an
    original as a target for distinct review tasks is valid dedupe evidence;
    a review ID may never also be an original role. The caller owns Bead-ID
    syntax validation, while this pure seam owns collection shape and global
    role/graph validation without raising or performing I/O.
    """
    if not isinstance(relations, (list, tuple)):
        return "invalid-review-relation"

    relations_by_review: dict[str, str] = {}
    original_ids: set[str] = set()
    for relation in relations:
        if not isinstance(relation, tuple) or len(relation) != 2:
            return "invalid-review-relation"
        review_id, original_id = relation
        if not isinstance(review_id, str) or not review_id:
            return "invalid-review-relation"
        if not isinstance(original_id, str) or not original_id:
            return "invalid-review-relation"
        if review_id == original_id:
            return "self-referential-review-id"
        if review_id in relations_by_review:
            return "ambiguous-review-relation"
        relations_by_review[review_id] = original_id
        original_ids.add(original_id)

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
    if set(relations_by_review) & original_ids:
        return "cross-role-review-relation"
    return None


def normalized_finding_relation_error(findings: object) -> str | None:
    """Validate raw normalized findings before cleanup preserves a recommendation."""
    if not isinstance(findings, list):
        return "invalid-review-relation"
    relations: list[object] = []
    for finding in findings:
        if not isinstance(finding, dict):
            return "invalid-review-relation"
        if finding.get("kind") == "original":
            continue
        relations.append((finding.get("review_id"), finding.get("original_id")))
    return review_relation_error(relations)
