#!/usr/bin/env python3
"""Resolve a review thread idempotently after validating the terminal reply."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any

from review_text_policy import terminal_reply_kind, validate_review_text


THREAD_QUERY = """
query($threadId:ID!, $after:String) {
  node(id:$threadId) {
    ... on PullRequestReviewThread {
      id
      isResolved
      comments(first:100, after:$after) {
        nodes {
          id
          databaseId
          body
          author { login }
          url
        }
        pageInfo {
          hasNextPage
          endCursor
        }
      }
    }
  }
}
""".strip()

RESOLVE_QUERY = """
mutation($threadId:ID!) {
  resolveReviewThread(input:{threadId:$threadId}) {
    thread { id isResolved }
  }
}
""".strip()


def run_json(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "command failed")
    return json.loads(result.stdout)


def fetch_thread(thread_id: str) -> dict[str, Any]:
    comments: list[dict[str, Any]] = []
    after = None
    thread: dict[str, Any] | None = None

    while True:
        cmd = [
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={THREAD_QUERY}",
            "-F",
            f"threadId={thread_id}",
        ]
        if after:
            cmd.extend(["-F", f"after={after}"])
        payload = run_json(cmd)
        thread = payload["data"]["node"]
        if thread is None:
            raise RuntimeError("unknown review thread")

        connection = thread["comments"]
        comments.extend(connection["nodes"])
        if not connection["pageInfo"]["hasNextPage"]:
            thread["comments"]["nodes"] = comments
            return thread
        after = connection["pageInfo"]["endCursor"]


def main():
    parser = argparse.ArgumentParser(description="Resolve a review thread idempotently.")
    parser.add_argument("--thread-id", required=True)
    args = parser.parse_args()

    try:
        thread = fetch_thread(args.thread_id)
        comments = thread.get("comments", {}).get("nodes", []) or []
        latest = comments[-1] if comments else None
        if latest is None:
            raise RuntimeError("review thread has no comments")

        problems = validate_review_text(latest.get("body", ""), "reply")
        if problems:
            raise RuntimeError("; ".join(problems))

        if thread["isResolved"]:
            output = {
                "ok": True,
                "status": "already-resolved",
                "thread_id": args.thread_id,
                "terminal_reply_kind": terminal_reply_kind(latest.get("body", "")),
            }
            json.dump(output, sys.stdout, indent=2, sort_keys=True)
            sys.stdout.write("\n")
            return

        payload = run_json([
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={RESOLVE_QUERY}",
            "-F",
            f"threadId={args.thread_id}",
        ])
        thread_payload = payload["data"]["resolveReviewThread"]["thread"]
        output = {
            "ok": True,
            "status": "resolved",
            "thread_id": thread_payload["id"],
            "is_resolved": thread_payload["isResolved"],
            "terminal_reply_kind": terminal_reply_kind(latest.get("body", "")),
        }
        json.dump(output, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    except Exception as exc:
        print(
            json.dumps(
                {"ok": False, "error": str(exc), "error_code": "resolve-failed"},
                indent=2,
                sort_keys=True,
            ),
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
