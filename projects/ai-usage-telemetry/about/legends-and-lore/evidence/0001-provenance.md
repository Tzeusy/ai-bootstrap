# Evidence 0001: Content-Safe Provenance Manifest

**Status:** Accepted provenance manifest for RFC 0001  
**Date:** 2026-08-10  
**Host architecture used for source review:** `x86_64`

This manifest makes the source observations in Evidence 0001 reproducible
without opening personal sessions, global application state, auth stores, or
credentials. It records executable/source identity and safe commands, never
local record paths or values.

## Installed client identity

| Client | Version output | Executable SHA-256 |
|---|---|---|
| Claude Code | `2.1.226 (Claude Code)` | `4e9bec1177ce9690e8bd988b710ac24105e70da428dd094c5adcbbe786a55555` |
| Codex | `codex-cli 0.147.0` | `cb0a15567e9a60a5820d54b0f6ae86d504dc3805c1eab21a47f70e3eb7b73a40` |

Safe commands:

```sh
claude --version
codex --version
sha256sum "$(command -v claude)" "$(command -v codex)"
node --version
python3 --version
uname -m
```

The supporting tool outputs were Node `v24.6.0` and Python `3.10.12`. The
executable hashes identify the reviewed local artifacts; they do not make a
closed-source local JSON layout an upstream compatibility promise.

## Public source identity

Codex observations use annotated tag `rust-v0.147.0`, tag object
`3ed6f04f6bf8b7c46299d1cb1ff99c74ce21a51d`, peeled commit
`be6e8eac029b183056b7e4402879f15d2c85f61b`. The tag was resolved with:

```sh
git ls-remote https://github.com/openai/codex.git 'refs/tags/rust-v0.147.0*'
```

Reviewed public locations:

- [rollout and turn-context protocol](https://github.com/openai/codex/blob/rust-v0.147.0/codex-rs/protocol/src/protocol.rs#L3075-L3410)
- [token usage and rate-limit structures](https://github.com/openai/codex/blob/rust-v0.147.0/codex-rs/protocol/src/protocol.rs#L2064-L2209)
- [token/rate-limit emission behavior](https://github.com/openai/codex/blob/rust-v0.147.0/codex-rs/core/src/session/mod.rs#L3764-L3893)
- [Responses cache-write mapping](https://github.com/openai/codex/blob/rust-v0.147.0/codex-rs/codex-api/src/sse/responses.rs#L122-L147)
- [Claude session storage](https://code.claude.com/docs/en/sessions)
- [Claude application-data boundary](https://code.claude.com/docs/en/claude-directory)
- [Claude Messages token fields](https://platform.claude.com/docs/en/api/messages)
- [Claude inclusive output/thinking semantics](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## Structural-claim ledger

| Claim | Provenance | Authority |
|---|---|---|
| Codex rollout envelope, token usage fields, cache-write field, and optional rate-limit window types | Pinned public source above | Observed for `rust-v0.147.0` |
| A rate-limit-only update may re-emit stored token information | Pinned `session/mod.rs` source | Observed for `rust-v0.147.0` |
| Claude sessions use local JSONL and Claude API counters have documented meanings | Official documentation above | Observed, but insufficient by itself to fix exact local JSON paths or identity |
| Claude quota cache is not an admissible independent source | Official global-state boundary plus absence of a documented sanitized leaf | `unknown/unavailable`; fail closed |
| Claude exact local discriminator/paths/co-occurrence and identity collision | Fully synthetic capture described below plus official globally unique request-ID contract | Observed for client 2.1.226; adapter-versioned |
| Codex counter subset arithmetic and native request identity | Requires pinned behavioral/profile evidence and vectors | Capability remains `unsupported_profile` until proved |

## Synthetic capture boundary

Claude Code 2.1.226 was run in a new user/network namespace with only loopback,
a fresh temporary HOME/XDG/config tree, fake API credential, disabled optional
traffic/telemetry, no tools or MCP servers, and a loopback-only synthetic SSE
Messages API mock. The mock returned three fully synthetic responses with
`request-id` header sequence A/B/A. No external interface or real account was
available.

Safe invocation pattern:

```sh
unshare -Urn bash
ip link set lo up
# Start the synthetic SSE Messages API mock on 127.0.0.1:18765.
env -i \
  PATH="$PATH" \
  HOME="$SYNTH_ROOT/home" \
  XDG_CONFIG_HOME="$SYNTH_ROOT/config" \
  XDG_CACHE_HOME="$SYNTH_ROOT/cache" \
  XDG_DATA_HOME="$SYNTH_ROOT/data" \
  CLAUDE_CONFIG_DIR="$SYNTH_ROOT/home/.claude" \
  ANTHROPIC_API_KEY="$FAKE_API_KEY" \
  ANTHROPIC_BASE_URL="http://127.0.0.1:18765" \
  HTTP_PROXY="http://127.0.0.1:9" \
  HTTPS_PROXY="http://127.0.0.1:9" \
  NO_PROXY="127.0.0.1,localhost" \
  CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC=1 \
  DISABLE_AUTOUPDATER=1 \
  DISABLE_TELEMETRY=1 \
  claude --bare --safe-mode --strict-mcp-config \
    --mcp-config '{"mcpServers":{}}' \
    --disable-slash-commands --tools '' \
    --model claude-sonnet-4-5-20250929 \
    --output-format json \
    --session-id "$SYNTH_SESSION_ID" \
    -p "$SYNTH_PROMPT"
```

Two further invocations used `--resume "$SYNTH_SESSION_ID"`. The mock spoke
only the documented streaming Messages event sequence with hand-authored
message/model/content/usage values and the controlled response header. Prompt
and response literals are intentionally not project evidence.

The resulting temporary JSONL had SHA-256
`ab60adf00978db9ae4e906f13ca2fd1e8cb1984ac20e61a1af3c2d6b23310339`.
Structural assertions found three assistant records, one session identity, two
request identities, header order A/B/A, and one repeated group. Every record
co-contained string `/type`, `/sessionId`, `/requestId`, `/timestamp`, `/cwd`,
`/message/id`, `/message/model`; array `/message/content`; and numeric
`/message/usage/{input_tokens,cache_creation_input_tokens,cache_read_input_tokens,output_tokens}`.
The repeated header value was deliberately non-conforming because the vendor
contract makes request IDs globally unique. Its changed record timestamps make
the A/B/A sequence a negative identity-reuse/collision vector, not proof of
valid replay. Valid replay is tested by repeating the exact synthetic source
record; timestamp remains profile-admitted source time and fingerprint input.

Only structural assertions and the digest were retained. The temporary tree was
moved to operating-system trash after the assertions; no personal session,
global state, credential file, local path, or record value was opened or
published.
