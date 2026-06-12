#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys


THREADS_QUERY = """
query($owner:String!, $repo:String!, $number:Int!, $after:String) {
  repository(owner:$owner, name:$repo) {
    pullRequest(number:$number) {
      reviewThreads(first:50, after:$after) {
        nodes {
          id
          isResolved
          isOutdated
          comments(first:100) {
            nodes {
              id
              databaseId
              body
              path
              line
              originalLine
              url
              createdAt
              author { login }
            }
            pageInfo {
              hasNextPage
              endCursor
            }
          }
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

THREAD_COMMENTS_QUERY = """
query($threadId:ID!, $after:String) {
  node(id:$threadId) {
    ... on PullRequestReviewThread {
      comments(first:100, after:$after) {
        nodes {
          id
          databaseId
          body
          path
          line
          originalLine
          url
          createdAt
          author { login }
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


def fail(code, message, **extra):
    payload = {"ok": False, "error_code": code, "error": message}
    payload.update(extra)
    print(json.dumps(payload, indent=2, sort_keys=True), file=sys.stderr)
    sys.exit(1)


def run_json(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "command failed")
    return json.loads(result.stdout)


def fetch_all_comments(thread_id, seed_comments, page_info):
    comments = list(seed_comments)
    after = page_info.get("endCursor")
    while page_info.get("hasNextPage"):
        payload = run_json([
            "gh",
            "api",
            "graphql",
            "-f",
            f"query={THREAD_COMMENTS_QUERY}",
            "-F",
            f"threadId={thread_id}",
            "-F",
            f"after={after}",
        ])
        comment_connection = payload["data"]["node"]["comments"]
        comments.extend(comment_connection["nodes"])
        page_info = comment_connection["pageInfo"]
        after = page_info.get("endCursor")
    return comments


def main():
    parser = argparse.ArgumentParser(description="List review threads for a pull request.")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr-number", required=True, type=int)
    args = parser.parse_args()

    try:
        threads = []
        after = None

        while True:
            cmd = [
                "gh",
                "api",
                "graphql",
                "-f",
                f"query={THREADS_QUERY}",
                "-F",
                f"owner={args.owner}",
                "-F",
                f"repo={args.repo}",
                "-F",
                f"number={args.pr_number}",
            ]
            if after:
                cmd.extend(["-F", f"after={after}"])

            payload = run_json(cmd)
            review_threads = payload["data"]["repository"]["pullRequest"]["reviewThreads"]
            for node in review_threads["nodes"]:
                comment_connection = node["comments"]
                node["comments"]["nodes"] = fetch_all_comments(
                    node["id"],
                    comment_connection["nodes"],
                    comment_connection["pageInfo"],
                )
                threads.append(node)

            if not review_threads["pageInfo"]["hasNextPage"]:
                break
            after = review_threads["pageInfo"]["endCursor"]

        unresolved = [thread for thread in threads if not thread["isResolved"]]
        output = {
            "ok": True,
            "thread_count": len(threads),
            "unresolved_count": len(unresolved),
            "threads": threads,
        }
        json.dump(output, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    except RuntimeError as exc:
        fail("command-failed", str(exc))
    except Exception as exc:
        fail("unexpected-error", str(exc))


if __name__ == "__main__":
    main()
