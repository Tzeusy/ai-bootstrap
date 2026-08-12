
## butlers: session-link-guard fails if the session URL is in the PR body
The butlers `session-link-guard` CI check HARD-FAILS when `https://claude.ai/code/session_...` or a `Claude-Session:` label appears in the PR **title/body** (or non-trailer commit text). It is allowed ONLY as the exact `Claude-Session:` commit **trailer**. The generic harness instruction to "end PR bodies with the Generated-with-Claude-Code + session URL footer" therefore BREAKS butlers PRs. In worker-dispatch prompts for butlers: keep the commit trailer, but tell workers NOT to append the session-URL footer to the PR body. Fix a tripped PR with `gh pr edit <PR#> --body-file <body-without-footer>` (re-triggers the guard, no head change).
EOF2
echo "known-errors updated"