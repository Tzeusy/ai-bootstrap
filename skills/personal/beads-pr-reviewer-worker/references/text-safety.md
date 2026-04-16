# Text Safety

Load this reference before drafting PR text, review replies, inline comments, or
commit messages for the PR reviewer worker.

## Default Rule

Treat review-visible text as potentially public. Do not include personal data or
secrets unless there is no safe alternative and the text has been redacted.

## Block Or Redact At Minimum

- email addresses
- phone numbers
- IP addresses
- bearer tokens, JWTs, OAuth tokens, bot tokens, and session cookies
- API keys, access tokens, database URLs, and secret-bearing connection strings
- private key material
- absolute filesystem paths that reveal usernames or machine-specific layout
- internal hostnames or service names
- user-message excerpts or reviewer text that would identify a person or system

## Drafting Rules

- Prefer paraphrase over quotation when preserving the point is sufficient.
- If a reviewer message contains sensitive material, do not repeat it verbatim.
- Keep commit messages and replies specific but narrow; do not smuggle context
  into them that belongs in the code, tests, or review thread itself.
- If a draft contains anything sensitive, rewrite or redact it before posting.

## Validation

Use the bundled validator before posting manually written text:

```bash
python3 scripts/validate_review_text.py --kind reply --text "..."
python3 scripts/validate_review_text.py --kind comment --text "..."
python3 scripts/validate_review_text.py --kind commit --text "..."
```

For terminal replies, the body must be exactly one of:

- `Accepted in <commit>.`
  followed by `Reason: ...`
- `Wontfix.`
  followed by `Reason: ...`

The validator enforces the shape and the common secret/PII patterns above. If it
rejects a draft, rewrite the draft rather than bypassing the check.
