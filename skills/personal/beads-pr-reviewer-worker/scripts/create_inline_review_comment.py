#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys


def run_json(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "command failed")
    return json.loads(result.stdout)


def existing_comments(owner, repo, pr_number):
    comments = []
    page = 1
    while True:
        payload = run_json([
            "gh",
            "api",
            f"repos/{owner}/{repo}/pulls/{pr_number}/comments",
            "-F",
            "per_page=100",
            "-F",
            f"page={page}",
        ])
        if not payload:
            return comments
        comments.extend(payload)
        if len(payload) < 100:
            return comments
        page += 1


def main():
    parser = argparse.ArgumentParser(description="Create an inline review comment idempotently.")
    parser.add_argument("--owner", required=True)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--pr-number", required=True, type=int)
    parser.add_argument("--commit-id", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--line", required=True, type=int)
    parser.add_argument("--body", required=True)
    parser.add_argument("--dedupe-key", required=True)
    args = parser.parse_args()

    try:
        comments = existing_comments(args.owner, args.repo, args.pr_number)
        for comment in comments:
            if (
                comment.get("path") == args.path
                and (comment.get("line") == args.line or comment.get("original_line") == args.line)
                and args.dedupe_key in (comment.get("body") or "")
            ):
                output = {
                    "ok": True,
                    "status": "duplicate-skipped",
                    "comment_id": comment.get("id"),
                    "comment_url": comment.get("html_url") or comment.get("url"),
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
            "-f",
            f"commit_id={args.commit_id}",
            "-f",
            f"path={args.path}",
            "-F",
            "side=RIGHT",
            "-F",
            f"line={args.line}",
        ])
        output = {
            "ok": True,
            "status": "created",
            "comment_id": payload.get("id"),
            "comment_url": payload.get("html_url") or payload.get("url"),
        }
        json.dump(output, sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
    except Exception as exc:
        print(json.dumps({"ok": False, "error": str(exc), "error_code": "inline-comment-failed"}, indent=2, sort_keys=True), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
