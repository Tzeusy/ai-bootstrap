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
    home = Path(home or os.environ.get("CODEX_HOME") or "~/.codex").expanduser().resolve()
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
    normalized = [validate_source(source) for source in explicit]
    if len({row["id"] for row in normalized}) != len(normalized):
        raise ValueError("usage source agent ids must be unique")
    sources = {row["id"]: row for row in normalized}
    runtime = {}
    for agent_id, row in matches:
        source = validate_source({"id": agent_id, "provider": "codex", "path": row["rollout_path"],
                                  "thread_id": row["id"]})
        prior = sources.get(agent_id)
        if prior and any(prior.get(key) != source[key] for key in ("provider", "path")):
            continue  # Explicit nonmatching sources retain precedence.
        if any(item["path"] == source["path"] for key, item in sources.items() if key != agent_id):
            warnings.append("A runtime log is already attributed to another agent; duplicate measurement refused.")
            continue
        sources[agent_id] = source
        runtime[agent_id] = {"thread_id": row["id"], "agent_path": row["agent_path"],
                             "model": row["model"]}
    return list(sources.values()), runtime, sorted(set(warnings))
