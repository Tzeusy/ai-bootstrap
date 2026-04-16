#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys

from review_text_policy import validate_review_text


THREAD_QUERY = """
query($threadId:ID!, $after:String) {
  node(id:$threadId) {
    ... on PullRequestReviewThread {
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


def run_json(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "command failed")
    return json.loads(result.stdout)


def fetch_comments(thread_id):
    comments = []
    after = None
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
        node = payload["data"]["node"]
        connection = node["comments"]
        comments.extend(connection["nodes"])
        if not connection["pageInfo"]["hasNextPage"]:
            return comments
        after = connection["pageInfo"]["endCursor"]


def main():
    parser = argparse.ArgumentParser(description="Reply to a review thread idempotently.")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr-number", required=True, type=int)
    parser.add_argument("--comment-id", required=True, type=int)
    parser.add_argument("--thread-id", required=True)
    parser.add_argument("--body", required=True)
    parser.add_argument("--dedupe-key", required=True)
    args = parser.parse_args()

    try:
        problems = validate_review_text(args.body, "reply")
        if problems:
            raise RuntimeError("; ".join(problems))

        comments = fetch_comments(args.thread_id)
        for comment in comments:
            if args.dedupe_key in (comment.get("body") or ""):
                output = {
                    "ok": True,
                    "status": "duplicate-skipped",
                    "thread_id": args.thread_id,
                    "comment_url": comment.get("url"),
                }
                json.dump(output, sys.stdout, indent=2, sort_keys=True)
                sys.stdout.write("\n")
                return

        payload = run_json([
            "gh",
            "api",
            f"repos/{args.owner}/{args.repo}/pulls/{args.pr_number}/comments",
            "-f",
            f"body={args.body}\n\ndedupe-key: {args.dedupe_key}",
            "-F",
            f"in_reply_to={args.comment_id}",
        ])
        output = {
            "ok": True,
            "status": "created",
            "thread_id": args.thread_id,
            "comment_id": payload.get("id"),
            "comment_url": payload.get("html_url") or payload.get("url"),
        }
        json.dump(output, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "error_code": "reply-failed"}, indent=2, sort_keys=True), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
