# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Resolve one Codex session's known agents through its read-only runtime index.

No directory traversal, transcript content, tracker queries or model calls.
The runtime index is private input; only matched identities reach the browser.
"""
from __future__ import annotations

import os
import sqlite3
import stat
from contextlib import closing
from pathlib import Path
from uuid import UUID

from loop_telemetry import validate_source

MAX_SESSIONS = 200


def configuration(thread_id: str, home: str | Path | None = None) -> dict:
    try:
        thread_id = str(UUID(thread_id))
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Codex watch requires a runtime thread UUID") from None
    if home is not None and not isinstance(home, (str, Path)):
        raise ValueError("Codex home must be a directory path")
    try:
        home = Path(home or os.environ.get("CODEX_HOME") or "~/.codex").expanduser().resolve()
    except (OSError, RuntimeError):
        raise ValueError("Codex home cannot be resolved") from None
    return {"provider": "codex", "thread_id": thread_id, "home": str(home)}


def _sessions(config: dict) -> list[dict]:
    """Use indexed spawn edges, including retained/archived descendants."""
    if not isinstance(config, dict) or config.get("provider") != "codex":
        raise ValueError("unsupported runtime watch configuration")
    clean = configuration(config.get("thread_id"), config.get("home"))
    index = Path(clean["home"]) / "state_5.sqlite"
    try:
        if not stat.S_ISREG(index.lstat().st_mode):
            raise ValueError("Codex runtime index must be a regular non-symlink file")
        with closing(sqlite3.connect(index.as_uri() + "?mode=ro", uri=True, timeout=0.2)) as database:
            database.row_factory = sqlite3.Row
            # UNION prevents cycles; LIMIT bounds both traversal and projection.
            rows = database.execute("""
                WITH RECURSIVE owned(id) AS (
                    SELECT id FROM threads WHERE id = ?
                    UNION
                    SELECT edge.child_thread_id FROM thread_spawn_edges AS edge
                    JOIN owned ON edge.parent_thread_id = owned.id
                    LIMIT ?
                )
                SELECT thread.id, thread.rollout_path, thread.agent_path, thread.model
                FROM owned JOIN threads AS thread ON thread.id = owned.id
                """, (clean["thread_id"], MAX_SESSIONS + 1)).fetchall()
    except (OSError, sqlite3.Error):
        raise ValueError("Codex runtime index unavailable or unsupported; check the configured home") from None
    if len(rows) > MAX_SESSIONS:
        raise ValueError("Codex runtime descendants exceed the bounded lookup limit")
    if not any(row["id"] == clean["thread_id"] for row in rows):
        raise ValueError("configured Codex parent is absent from its runtime index")
    return [dict(row) for row in rows]


def resolve(config: dict, actor: str, agents: list[dict], explicit: list[dict]) -> tuple[list[dict], dict, list[str]]:
    """Match only published IDs; ambiguity never silently selects a session."""
    sessions = _sessions(config)
    parent_id = configuration(config["thread_id"], config.get("home"))["thread_id"]
    parent = next(row for row in sessions if row["id"] == parent_id)
    children = [row for row in sessions if row["id"] != parent["id"]]
    matches = [(actor, parent)]
    warnings = []
    for agent in agents:
        if agent["id"] == actor:
            raise ValueError("parent and child agent ids must be distinct")
        identity = agent.get("thread_id") or agent["id"]
        candidates = [row for row in children if identity in (row["id"], row["agent_path"])]
        if not candidates and not agent.get("thread_id"):
            candidates = [row for row in children if isinstance(row["agent_path"], str)
                          and row["agent_path"].rsplit("/", 1)[-1] == identity]
        if len(candidates) == 1:
            matches.append((agent["id"], candidates[0]))
        elif len(candidates) > 1:
            warnings.append("An agent name matches multiple owned sessions; publish its thread_id.")
    bindings = []
    for agent_id, row in matches:
        source = validate_source({"id": agent_id, "provider": "codex", "path": row["rollout_path"],
                                  "thread_id": row["id"]})
        bindings.append((source, {"thread_id": row["id"], "agent_path": row["agent_path"],
                                  "model": row["model"]}))
    sources, runtime, merged_warnings = _merge(bindings, explicit)
    return sources, runtime, sorted(set(warnings + merged_warnings))


def _merge(bindings: list[tuple[dict, dict]], explicit: list[dict]) -> tuple[list[dict], dict, list[str]]:
    normalized = [validate_source(source) for source in explicit]
    if len({row["id"] for row in normalized}) != len(normalized):
        raise ValueError("usage source agent ids must be unique")
    sources = {row["id"]: row for row in normalized}
    runtime, warnings = {}, []
    for source, metadata in bindings:
        agent_id = source["id"]
        prior = sources.get(agent_id)
        if prior and any(prior.get(key) != source[key] for key in ("provider", "path")):
            continue  # Explicit nonmatching sources retain precedence.
        if any(item["path"] == source["path"] for key, item in sources.items() if key != agent_id):
            warnings.append("A runtime log is already attributed to another agent; duplicate measurement refused.")
            continue
        sources[agent_id] = source
        runtime[agent_id] = metadata
    return list(sources.values()), runtime, sorted(set(warnings))


def retain(config: dict, actor: str, agents: list[dict], saved: dict, explicit: list[dict]) -> tuple[list[dict], dict, list[str]]:
    """Reuse proven bindings across restart; current explicit attachments win."""
    if (not isinstance(saved, dict) or saved.get("config") != config
        or not isinstance(saved.get("sources"), list) or len(saved["sources"]) > MAX_SESSIONS
        or not isinstance(saved.get("metadata"), dict)):
        raise ValueError("retained runtime bindings are invalid; restore the runtime index")
    expected = {actor, *[agent["id"] for agent in agents]}
    selectors = {agent["id"]: agent.get("thread_id") for agent in agents}
    bindings = []
    for row in saved["sources"]:
        source = validate_source(row)
        metadata = saved["metadata"].get(source["id"])
        if (source["provider"] != "codex" or not source.get("thread_id")
            or not isinstance(metadata, dict) or set(metadata) != {"thread_id", "agent_path", "model"}
            or metadata["thread_id"] != source["thread_id"]
            or any(metadata[key] is not None and not isinstance(metadata[key], str)
                   for key in ("agent_path", "model"))):
            raise ValueError("retained runtime identity is invalid; restore the runtime index")
        selector = selectors.get(source["id"])
        if source["id"] in expected and (not selector or selector == source["thread_id"]):
            bindings.append((source, metadata))
    return _merge(bindings, explicit)
