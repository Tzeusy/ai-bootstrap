# Measured usage

Read for automatic runtime attribution, explicit log attachment or coverage.
Counters come from runtime records; work summaries/status come from native
reports at existing parent checkpoints. No model reads child transcripts.

## Codex parent and known children

`init` automatically watches `CODEX_THREAD_ID` when available. An existing
workspace, missing environment variable or custom runtime home uses:

```bash
uv run "$DASHBOARD" --slug "$SLUG" watch-codex --thread-id "$PARENT_THREAD_ID"
# Optional: --home "$CODEX_RUNTIME_HOME"
```

The [runtime resolver](../scripts/runtime_sources.py) queries only this parent's
indexed spawn relationships in the local read-only `state_5.sqlite` (at most200
sessions). It includes retained/archived descendants and matches only published
roster IDs: thread UUID, full agent path, then unique path basename. Publish an
agent's `thread_id` when names are ambiguous. Future child logs attach at the
next server tick; no per-child command or orchestrator polling is needed.

`runtime.json` pins parent/home; repeat init never changes an existing binding.
A conflicting watch refuses. `init --codex-thread ""` leaves runtime binding
explicit. An unavailable/unsupported index reports a warning; progress/feedback
remain usable. A temporary lookup failure retains previously established
sources and offsets across server restart. `runtime-sources.json` persists only
proven bindings, pinned to that configuration, and changes only with attribution.
Changed explicit thread selectors invalidate old retained attribution.
Current explicit attachments retain precedence during outages; even a damaged
binding cache cannot prune unresolved parser offsets. No transcript-directory crawl, unrelated-session read,
auth-file access or runtime status inference occurs. Runtime model/thread/path
are shown separately from parent-reported work/model/branch/PR context.

## Explicit sources and other runtimes

Known Codex/Claude logs can still attach directly. The ID must be the workspace
actor or a published roster entry:

```bash
uv run "$DASHBOARD" --slug "$SLUG" attach --id "$ACTOR" \
  --provider codex --path "$EXPLICIT_PARENT_TRANSCRIPT"
uv run "$DASHBOARD" --slug "$SLUG" attach --id reviewer-1 \
  --provider claude --path "$EXPLICIT_CHILD_TRANSCRIPT"
```

Explicit nonmatching attachments take precedence over automatic resolution.
Duplicate paths refuse double counting. Missing/unsupported locators remain
unknown; do not guess or crawl other runtime directories to fill them.

## Counters, freshness and efficiency

The [usage adapter](../scripts/loop_telemetry.py) reads at most1MiB per source per
three-second tick. Cache offsets/counters survive restart and unchanged polls do
not rewrite them. New thread-bound attribution may require one bounded catch-up.
Changed file identity/truncation resets measurement; that is not uninterrupted
lifetime use.

Codex native `token_usage_record` thread totals supersede lagging legacy
`event_msg/token_count` totals. Thread IDs and fork-history ordinals exclude
copied parent/foreign records; streams are never added together. Older logs
still use their latest valid cumulative sample. Claude deduplicates streamed
assistant records by hashed message ID. Claude input includes uncached, cache
reads and cache writes; cached input is the read subset, already included in
input. Context tokens describe the latest usage sample, not window capacity.
No inferred token estimates or prices are displayed.

Unknown/error counters stay null; `catching-up` means a bounded read has not
reached its observed EOF. Totals cover measured sources only; expected coverage
includes the parent and published agents. Completed agents retain attribution
and naturally older usage timestamps. HTTP success proves connectivity, not
fresh model activity or complete coverage. Never replace missing counts with
zero or equate cache percentage with measured savings.
