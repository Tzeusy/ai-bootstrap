#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Incrementally project explicit runtime JSONL sources into usage counters.

Only counters, timestamps, byte offsets and hashed message IDs survive parsing.
No discovery, model calls, transcript output, or transcript content in the cache.
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
import stat as stat_module
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import UUID

MAX_BYTES_PER_POLL = 1024 * 1024
MAX_LINE_BYTES = 256 * 1024
MAX_MESSAGES = 50_000
COUNTERS = ("input_tokens", "cached_input_tokens", "output_tokens", "total_tokens")


def _now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def _timestamp(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value)
        if parsed.tzinfo is None:
            return None
        return parsed.astimezone(UTC).isoformat(timespec="seconds")
    except (ValueError, OverflowError):
        return None


def _count(value: Any) -> bool:
    return type(value) is int and 0 <= value <= 2**63 - 1


def validate_source(source: dict[str, Any]) -> dict[str, str]:
    """Validate an explicitly attached log, without reading its contents."""
    if not isinstance(source, dict):
        raise ValueError("usage source must be an object")  # noqa: TRY004 - stable JSON validation API
    if not isinstance(source.get("id"), str) or not 1 <= len(source["id"]) <= 256:
        raise ValueError("usage source needs an agent id")
    if source.get("provider") not in {"codex", "claude"}:
        raise ValueError("unsupported usage provider")
    if not isinstance(source.get("path"), str):
        raise ValueError("usage source needs an absolute JSONL path")  # noqa: TRY004 - stable JSON validation API
    original = Path(source["path"]).expanduser()
    if not original.is_absolute():
        raise ValueError("usage source needs an absolute JSONL path")
    if original.is_symlink():
        raise ValueError("usage source must not be a symlink")
    try:
        path = original.resolve()
    except (OSError, RuntimeError):
        raise ValueError("usage source path cannot be resolved") from None
    for candidate in (original, path):
        if candidate.suffix.lower() != ".jsonl" or any(
            part.lower() == "secrets"
            or part.lower().startswith(".env")
            or "credential" in part.lower()
            or "token" in part.lower()
            for part in candidate.parts
        ):
            raise ValueError("usage sources must be non-secret JSONL logs")
    result = {"id": source["id"], "provider": source["provider"], "path": str(path)}
    if "thread_id" in source:
        try:
            result["thread_id"] = str(UUID(source["thread_id"]))
        except (ValueError, TypeError, AttributeError):
            raise ValueError("usage source thread_id must be a UUID") from None
    return result


def _empty(source: dict[str, str], identity: list[int]) -> dict[str, Any]:
    return {
        **source,
        "identity": identity,
        "offset": 0,
        "size_seen": 0,
        "tail_digest": "",
        "discard_partial": False,
        "usage": None,
        "context_tokens": None,
        "observed_at": None,
        "messages": {},
        "invalid_events": 0,
        "skipped_lines": 0,
        "thread_id": source.get("thread_id"),
        "history_start_ordinal": None,
        "usage_format": "legacy",
    }


def _digest(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(
        character in "0123456789abcdef" for character in value
    )


def _valid_cache_entry(agent_id: str, entry: Any) -> bool:
    """Check persisted parser state before trusting offsets or incremental sums."""
    if not isinstance(entry, dict) or entry.get("id") != agent_id:
        return False
    if entry.get("provider") not in ("codex", "claude") or not isinstance(entry.get("path"), str):
        return False
    identity = entry.get("identity")
    if not isinstance(identity, list) or len(identity) != 2 or not all(map(_count, identity)):
        return False
    if not all(_count(entry.get(key)) for key in (
        "offset", "size_seen", "invalid_events", "skipped_lines"
    )):
        return False
    digest_valid = _digest(entry.get("tail_digest")) if entry["offset"] else entry.get("tail_digest") == ""
    if not digest_valid or type(entry.get("discard_partial")) is not bool:
        return False
    usage = entry.get("usage")
    if "usage" not in entry or (usage is not None and (
        not isinstance(usage, dict)
        or not all(_count(usage.get(key)) for key in ("input_tokens", "output_tokens", "total_tokens"))
        or "cached_input_tokens" not in usage
        or (usage["cached_input_tokens"] is not None and (
            not _count(usage["cached_input_tokens"])
            or usage["cached_input_tokens"] > usage["input_tokens"]
        ))
        or (entry["provider"] == "claude" and usage["cached_input_tokens"] is None)
    )):
        return False
    if "context_tokens" not in entry or (
        entry["context_tokens"] is not None and not _count(entry["context_tokens"])
    ):
        return False
    if "observed_at" not in entry or (
        entry["observed_at"] is not None and _timestamp(entry["observed_at"]) is None
    ):
        return False
    if entry.get("thread_id") is not None and not isinstance(entry["thread_id"], str):
        return False
    if entry.get("history_start_ordinal") is not None and not _count(entry["history_start_ordinal"]):
        return False
    if entry.get("usage_format", "legacy") not in ("legacy", "thread"):
        return False
    messages = entry.get("messages")
    return isinstance(messages, dict) and len(messages) <= MAX_MESSAGES and all(
        _digest(key)
        and isinstance(values, list) and len(values) == 4 and all(map(_count, values))
        for key, values in messages.items()
    )


def _codex_sample(entry: dict[str, Any], usage: Any, context: Any, timestamp: Any) -> None:
    if not isinstance(usage, dict) or not all(_count(usage.get(key)) for key in (
        "input_tokens", "output_tokens", "total_tokens"
    )):
        entry["invalid_events"] += 1
        return
    current = {key: usage.get(key) for key in COUNTERS}
    cached = current["cached_input_tokens"]
    if cached is not None and (not _count(cached) or cached > current["input_tokens"]):
        entry["invalid_events"] += 1
        return
    previous = entry["usage"]
    if previous and any(
        current[key] is not None and previous[key] is not None and current[key] < previous[key]
        for key in COUNTERS
    ):
        # A reset inside the same file is not another additive usage event.
        entry["invalid_events"] += 1
        return
    entry["usage"] = current
    # A complete cumulative sample covers earlier unreadable records. For Codex
    # these counters describe uncertainty since the last authoritative sample;
    # Claude's per-message sums keep uncertainty sticky for the entire file.
    entry["invalid_events"] = 0
    entry["skipped_lines"] = 0
    entry["context_tokens"] = context if _count(context) else None
    timestamp = _timestamp(timestamp)
    entry["observed_at"] = max(filter(None, (entry["observed_at"], timestamp)), default=None)


def _codex(entry: dict[str, Any], record: dict[str, Any]) -> None:
    payload = record.get("payload")
    if not isinstance(payload, dict):
        return
    if record.get("type") == "session_meta":
        identity = payload.get("id")
        if isinstance(identity, str) and entry.get("thread_id") and identity != entry["thread_id"]:
            raise ValueError("Codex source metadata does not match its attached thread")
        if isinstance(identity, str) and not entry.get("thread_id"):
            entry["thread_id"] = identity
        cutoff = payload.get("subagent_history_start_ordinal")
        if identity == entry.get("thread_id") and _count(cutoff):
            entry["history_start_ordinal"] = cutoff
        return
    cutoff = entry.get("history_start_ordinal")
    if cutoff is not None and _count(record.get("ordinal")) and record["ordinal"] <= cutoff:
        return  # A fork's copied parent history is not child usage.
    if record.get("type") == "token_usage_record":
        if not entry.get("thread_id") or payload.get("thread_id") != entry["thread_id"]:
            return
        # Runtime thread totals are authoritative; legacy event emission can lag
        # many requests. Never add the two streams or let lagging events regress it.
        if entry.get("usage_format") != "thread":
            entry["usage"] = None
        current = payload.get("usage")
        context = current.get("total_tokens") if isinstance(current, dict) else None
        _codex_sample(entry, payload.get("thread_token_usage"), context, record.get("timestamp"))
        entry["usage_format"] = "thread"
    elif (record.get("type") == "event_msg" and payload.get("type") == "token_count"
          and entry.get("usage_format", "legacy") != "thread"):
        if cutoff is not None and not _count(record.get("ordinal")):
            return  # Legacy fork records without provenance cannot be attributed.
        info = payload.get("info")
        if info is not None:
            last = info.get("last_token_usage") if isinstance(info, dict) else None
            context = last.get("total_tokens") if isinstance(last, dict) else None
            usage = info.get("total_token_usage") if isinstance(info, dict) else None
            _codex_sample(entry, usage, context, record.get("timestamp"))


def _claude(entry: dict[str, Any], record: dict[str, Any]) -> None:
    message = record.get("message")
    if record.get("type") != "assistant" or not isinstance(message, dict):
        return
    usage = message.get("usage")
    if usage is None:
        return
    message_id = message.get("id")
    keys = ("input_tokens", "cache_read_input_tokens", "cache_creation_input_tokens", "output_tokens")
    if not isinstance(usage, dict) or not isinstance(message_id, str) or not message_id:
        entry["invalid_events"] += 1
        return
    values = [usage.get(key, 0) for key in keys]
    if not all(_count(value) for value in values) or not all(key in usage for key in (
        "input_tokens", "output_tokens"
    )):
        entry["invalid_events"] += 1
        return
    digest = hashlib.sha256(message_id.encode()).hexdigest()
    if digest not in entry["messages"] and len(entry["messages"]) >= MAX_MESSAGES:
        entry["invalid_events"] += 1
        return
    previous = entry["messages"].get(digest, [0, 0, 0, 0])
    current = [max(old, new) for old, new in zip(previous, values)]
    entry["messages"][digest] = current
    if entry["usage"] is None:
        entry["usage"] = dict.fromkeys(COUNTERS, 0)
    delta = [new - old for old, new in zip(previous, current)]
    input_delta = sum(delta[:3])
    entry["usage"]["input_tokens"] += input_delta
    entry["usage"]["cached_input_tokens"] += delta[1]
    entry["usage"]["output_tokens"] += delta[3]
    entry["usage"]["total_tokens"] += input_delta + delta[3]
    # Input includes uncached, cache reads and cache writes. Cached is the read subset.
    entry["context_tokens"] = sum(current[:3]) + current[3]
    timestamp = _timestamp(record.get("timestamp"))
    entry["observed_at"] = max(filter(None, (entry["observed_at"], timestamp)), default=None)


def _consume(entry: dict[str, Any], data: bytes) -> None:
    position = 0
    while position < len(data):
        end = data.find(b"\n", position)
        if end < 0:
            tail = data[position:]
            if entry["discard_partial"] or len(tail) > MAX_LINE_BYTES:
                entry["discard_partial"] = True
                entry["offset"] += len(tail)
            # Short incomplete lines are reread next time; never persist raw text.
            break
        line = data[position:end]
        entry["offset"] += end - position + 1
        position = end + 1
        if entry["discard_partial"]:
            entry["discard_partial"] = False
            entry["skipped_lines"] += 1
            continue
        if len(line) > MAX_LINE_BYTES:
            entry["skipped_lines"] += 1
            continue
        try:
            record = json.loads(line)
        except (ValueError, UnicodeDecodeError):
            entry["invalid_events"] += 1
            continue
        if isinstance(record, dict):
            (_codex if entry["provider"] == "codex" else _claude)(entry, record)


def _tail_digest(stream: Any, offset: int) -> str:
    if not offset:
        return ""
    stream.seek(max(0, offset - 64))
    return hashlib.sha256(stream.read(min(offset, 64))).hexdigest()


def _open_regular(path: Path | str, flags: int) -> int:
    """Reject symlink swaps and nonregular files before any content is read."""
    descriptor = os.open(path, flags | os.O_NONBLOCK | os.O_NOFOLLOW, 0o600)
    if not stat_module.S_ISREG(os.fstat(descriptor).st_mode):
        os.close(descriptor)
        raise OSError("telemetry files must be regular files")
    return descriptor


class UsageCollector:
    """Read at most one bounded append per source per poll; resume across restarts."""

    def __init__(self, workspace: Path):
        self.workspace = Path(workspace)
        self.cache_path = self.workspace / "telemetry-cache.json"

    def _read_source(self, source: dict[str, str], previous: dict[str, Any] | None) -> tuple[dict, dict]:
        base = {key: source[key] for key in ("id", "provider")}
        unknown = {**dict.fromkeys(COUNTERS), "observed_at": None, "context_tokens": None}
        try:
            descriptor = _open_regular(source["path"], os.O_RDONLY)
            with os.fdopen(descriptor, "rb") as stream:
                stat = os.fstat(stream.fileno())
                identity = [stat.st_dev, stat.st_ino]
                entry = previous
                if not entry or any(entry.get(key) != source[key] for key in source) or (
                    entry.get("identity") != identity or stat.st_size < entry.get("size_seen", 0)
                    or entry.get("offset", 0) > stat.st_size
                    or _tail_digest(stream, entry.get("offset", 0)) != entry.get("tail_digest", "")
                ):
                    entry = _empty(source, identity)
                stream.seek(entry["offset"])
                # Keep this sample coherent with fstat; later appends wait for
                # the next tick instead of advancing beyond size_seen.
                _consume(entry, stream.read(min(MAX_BYTES_PER_POLL, stat.st_size - entry["offset"])))
                entry["size_seen"] = stat.st_size
                entry["tail_digest"] = _tail_digest(stream, entry["offset"])
        except OSError:
            return previous, {**base, **unknown, "status": "error", "reason": "unreadable-source"}
        if entry["invalid_events"] or entry["skipped_lines"]:
            return entry, {**base, **unknown, "status": "error", "reason": (
                "oversized-log-line" if entry["skipped_lines"] else "malformed-usage-log"
            )}
        catching_up = entry["offset"] < stat.st_size or entry["discard_partial"]
        status = "catching-up" if catching_up else ("measured" if entry["usage"] is not None else "unknown")
        return entry, {
            **base,
            **(entry["usage"] or dict.fromkeys(COUNTERS)),
            "observed_at": entry["observed_at"],
            "context_tokens": entry["context_tokens"],
            "status": status,
            "reason": "incomplete-log" if catching_up else (
                "no-usage-events" if entry["usage"] is None else None
            ),
        }

    def _save(self, cache: dict[str, Any]) -> None:
        try:
            if not stat_module.S_ISREG(self.cache_path.lstat().st_mode):
                raise ValueError("telemetry cache must be a regular non-symlink file")
        except FileNotFoundError:
            pass
        fd, name = tempfile.mkstemp(prefix=".telemetry-", dir=self.workspace)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as stream:
                json.dump(cache, stream, separators=(",", ":"), sort_keys=True)
                stream.write("\n")
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(name, self.cache_path)
        finally:
            if os.path.exists(name):
                os.unlink(name)

    def _load(self) -> dict[str, Any]:
        try:
            descriptor = _open_regular(self.cache_path, os.O_RDONLY)
        except FileNotFoundError:
            return {"schema": 1, "sources": {}}
        except OSError:
            raise ValueError("telemetry cache must be a regular non-symlink file") from None
        try:
            with os.fdopen(descriptor, "r", encoding="utf-8") as stream:
                cache = json.load(stream)
            if cache.get("schema") != 1 or not isinstance(cache.get("sources"), dict):
                raise ValueError
            if not all(_valid_cache_entry(agent_id, entry)
                       for agent_id, entry in cache["sources"].items()):
                raise ValueError
        except (ValueError, AttributeError):
            raise ValueError("telemetry cache is invalid; restore or remove its local cache") from None
        return cache

    def poll(self, sources: list[dict]) -> dict[str, Any]:
        """Return a redacted projection; missing/error sources never become zero usage."""
        normalized = [validate_source(source) for source in sources]
        if len({source["id"] for source in normalized}) != len(normalized):
            raise ValueError("usage source agent ids must be unique")
        if len({source["path"] for source in normalized}) != len(normalized):
            raise ValueError("usage source log paths must be unique")
        self.workspace.mkdir(parents=True, exist_ok=True)
        try:
            lock_fd = _open_regular(self.workspace / "telemetry-cache.lock", os.O_CREAT | os.O_RDWR)
        except OSError:
            raise ValueError("telemetry cache lock must be a regular non-symlink file") from None
        with os.fdopen(lock_fd, "a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            cache = self._load()
            before = json.dumps(cache, sort_keys=True)
            rows = []
            retained = {}
            for source in normalized:
                entry, row = self._read_source(source, cache["sources"].get(source["id"]))
                if entry is not None:
                    retained[source["id"]] = entry
                rows.append(row)
            cache["sources"] = retained
            if json.dumps(cache, sort_keys=True) != before:
                self._save(cache)
        measured = [row for row in rows if row["status"] == "measured"
                    and row["total_tokens"] is not None]
        totals = {
            key: sum(row[key] for row in measured) if measured and all(
                row[key] is not None for row in measured
            ) else None
            for key in COUNTERS
        }
        return {
            "agents": rows,
            "totals": totals,
            "coverage": {"attached": len(rows), "measured": len(measured)},
            "sampled_at": _now(),
        }
