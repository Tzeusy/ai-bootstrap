#!/usr/bin/env python3
"""Shared validation helpers for review text in the PR reviewer worker."""

from __future__ import annotations

import re

_TERMINAL_ACCEPTED_RE = re.compile(
    r"^Accepted in [0-9a-f]{7,40}\.\nReason: [^\n]+\Z",
)
_TERMINAL_WONTFIX_RE = re.compile(
    r"^Wontfix\.\nReason: [^\n]+\Z",
)

_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
_JWT_RE = re.compile(r"\beyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\b")
_BEARER_RE = re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]{16,}\b", re.IGNORECASE)
_API_KEY_RE = re.compile(
    r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|"
    r"sk-[A-Za-z0-9]{16,}|AIza[0-9A-Za-z_-]{20,}|AKIA[0-9A-Z]{16})\b"
)
_DB_URL_RE = re.compile(r"\b(?:postgres|mysql|mongodb|redis|amqp|amqps)://\S+\b")
_ABSOLUTE_PATH_RE = re.compile(
    r"(?:(?<!\w)/(?:Users|home|var|tmp|private|mnt|etc|opt|Volumes|Applications|Library)/\S+|"
    r"[A-Za-z]:\\\\\S+)"
)
_IPV4_RE = re.compile(
    r"\b(?:25[0-5]|2[0-4]\d|1?\d?\d)"
    r"(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}\b"
)
_PRIVATE_KEY_RE = re.compile(r"-----BEGIN [A-Z0-9 ]+PRIVATE KEY-----")

# Matches the trailing dedupe annotation appended by reply_to_review_thread.py.
# Format: "\n\ndedupe-key: <value>" at the end of a stored comment body.
_DEDUPE_SUFFIX_RE = re.compile(r"\n\ndedupe-key: \S+\s*\Z")

_SENSITIVE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("email address", _EMAIL_RE),
    ("JWT or bearer token", _JWT_RE),
    ("Bearer token", _BEARER_RE),
    ("API key or access token", _API_KEY_RE),
    ("database URL", _DB_URL_RE),
    ("absolute filesystem path", _ABSOLUTE_PATH_RE),
    ("IPv4 address", _IPV4_RE),
    ("private key material", _PRIVATE_KEY_RE),
)


def strip_dedupe_suffix(text: str) -> str:
    """Strip the trailing dedupe annotation added by reply_to_review_thread.py.

    Comments posted by the worker have the form::

        <body>\n\ndedupe-key: <value>

    When reading back from GitHub, this suffix is present verbatim. Strip it
    before any validation so that dedupe metadata does not interfere with the
    terminal-reply format check.
    """
    return _DEDUPE_SUFFIX_RE.sub("", text or "")


def is_terminal_reply(text: str) -> bool:
    """Return True when the reply uses the worker's terminal closure format."""

    stripped = strip_dedupe_suffix(text).strip()
    return bool(
        _TERMINAL_ACCEPTED_RE.match(stripped) or _TERMINAL_WONTFIX_RE.match(stripped)
    )


def terminal_reply_kind(text: str) -> str | None:
    """Classify a terminal reply body."""

    stripped = strip_dedupe_suffix(text).strip()
    if _TERMINAL_ACCEPTED_RE.match(stripped):
        return "Accepted"
    if _TERMINAL_WONTFIX_RE.match(stripped):
        return "Wontfix"
    return None


def validate_review_text(text: str, kind: str) -> list[str]:
    """Validate text for PII/secrets and, for replies, terminal closure shape.

    The dedupe-key suffix appended by reply_to_review_thread.py is stripped
    before validation so it does not interfere with the terminal-reply check
    or be mistakenly flagged by sensitive-pattern rules.
    """

    stripped = strip_dedupe_suffix(text).strip()
    problems: list[str] = []

    if not stripped:
        problems.append("text is empty")

    for label, pattern in _SENSITIVE_PATTERNS:
        if pattern.search(stripped):
            problems.append(f"contains {label}")

    if kind == "reply":
        if not is_terminal_reply(stripped):
            problems.append(
                "reply must use Accepted in <sha>.\\nReason: ... or Wontfix.\\nReason: ..."
            )
    elif kind not in {"comment", "commit", "pr-text"}:
        problems.append(f"unsupported validation kind: {kind}")

    return problems
