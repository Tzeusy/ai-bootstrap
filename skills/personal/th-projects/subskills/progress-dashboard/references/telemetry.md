# Measured usage

Read when attaching a known runtime log or explaining usage coverage. Counters
come from runtime records; agent status comes from the parent's native results.
Neither requires another model reading or summarizing child transcripts.
The fixed [usage adapter](../scripts/loop_telemetry.py) owns parsing and offsets;
inspect it only when maintaining collector behavior.

Attach explicitly known non-secret JSONL locators once per parent/child. The ID
must be the workspace actor or an already-published roster entry:

```bash
uv run "$DASHBOARD" --slug "$SLUG" attach --id "$ACTOR" \
  --provider codex --path "$EXPLICIT_PARENT_TRANSCRIPT"
uv run "$DASHBOARD" --slug "$SLUG" attach --id reviewer-1 \
  --provider claude --path "$EXPLICIT_CHILD_TRANSCRIPT"
```

If a locator is unavailable, leave usage unknown. Do not discover logs by
crawling private runtime state; no launch/checkpoint/background scan or auth-file
read is needed. Duplicate paths refuse to prevent double counting.

The collector consumes at most 1MiB per source per three-second server tick.
`telemetry-cache.json` retains offsets/counters across restart and is rewritten
only when changed. Completed agents retain attribution. Changed file identity or
truncation resets the source measurement; that is not uninterrupted lifetime use.

Codex uses the latest cumulative `event_msg/token_count` totals; repeated samples
do not add tokens. Claude deduplicates streamed assistant records by hashed
message ID. Claude input includes uncached input, cache reads and cache writes;
cached input is the read subset, already included in input. Context tokens mean
latest usage sample, not context-window capacity. No prices or inferred token
estimates are displayed.

Unknown/error sources have null counters. `catching-up` means a bounded read has
not reached EOF. Aggregate totals cover measured sources only; coverage includes
the parent and known agents even when unattached. Read per-source timestamps
before claiming freshness. HTTP success proves reachability, not fresh model
activity or complete usage coverage. Report measured versus unknown usage when
relevant; never fill gaps with guesses.
