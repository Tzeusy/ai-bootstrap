#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys


STATUS_QUERY = """
query($threadId:ID!) {
  node(id:$threadId) {
    ... on PullRequestReviewThread {
      id
      isResolved
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


def main():
    parser = argparse.ArgumentParser(description="Resolve a review thread idempotently.")
    parser.add_argument("--thread-id", required=True)
    args = parser.parse_args()

    try:
        status_payload = run_json([
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={STATUS_QUERY}",
            "-F",
            f"threadId={args.thread_id}",
        ])
        node = status_payload["data"]["node"]
        if node["isResolved"]:
            output = {"ok": True, "status": "already-resolved", "thread_id": args.thread_id}
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
        thread = payload["data"]["resolveReviewThread"]["thread"]
        output = {"ok": True, "status": "resolved", "thread_id": thread["id"], "is_resolved": thread["isResolved"]}
        json.dump(output, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "error_code": "resolve-failed"}, indent=2, sort_keys=True), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
