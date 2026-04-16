#!/usr/bin/env python3
"""Validate review text for terminal reply shape and secret/PII hygiene."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from review_text_policy import terminal_reply_kind, validate_review_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Validate PR text, review replies, commit messages, or inline comments "
            "for the worker's terminal reply contract and basic secret/PII hygiene."
        )
    )
    parser.add_argument(
        "--kind",
        required=True,
        choices=("reply", "comment", "commit", "pr-text"),
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text")
    group.add_argument("--text-file")
    return parser


def read_text(args: argparse.Namespace) -> str:
    if args.text is not None:
        return args.text
    return Path(args.text_file).read_text(encoding="utf-8")


def main() -> int:
    args = build_parser().parse_args()
    text = read_text(args)
    problems = validate_review_text(text, args.kind)
    output = {
        "ok": not problems,
        "kind": args.kind,
        "is_terminal_reply": terminal_reply_kind(text) is not None,
        "problems": problems,
    }
    json.dump(output, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0 if not problems else 1


if __name__ == "__main__":
    raise SystemExit(main())
