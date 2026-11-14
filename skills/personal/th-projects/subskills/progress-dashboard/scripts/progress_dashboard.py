#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Private, deterministic progress workspace; no model, tracker writes or shell execution."""
from __future__ import annotations

import argparse
import fcntl
import ipaddress
import json
import os
import re
import secrets
import signal
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import contextmanager
from datetime import UTC, datetime
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import urlopen

SCHEMA = "progress-dashboard/v1"
FILES = ("in-progress.md", "todo.md", "complete.md", "handover.md")
STATUSES = ("in-progress", "todo", "complete")
MAX_JSON = 256 * 1024
FEEDBACK_BATCH_BYTES = 8 * 1024


def now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds")


def text(value, label: str, limit: int = 8000) -> str:
    if not isinstance(value, str) or len(value) > limit:
        raise ValueError(f"{label} must be a string of at most {limit} characters")
    return value


def atomic(path: Path, data: str) -> None:
    if path.is_symlink():
        raise ValueError(f"refusing symlink: {path.name}")
    fd, temporary = tempfile.mkstemp(prefix=".write-", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        Path(temporary).unlink(missing_ok=True)


def save(path: Path, value) -> None:
    atomic(path, json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n")


def load(path: Path, default=None):
    if path.is_symlink():
        raise ValueError(f"refusing symlink: {path.name}")
    if not path.exists():
        if default is not None:
            return default
        raise ValueError(f"missing {path.name}; initialize the workspace first")
    if path.stat().st_size > 4 * 1024 * 1024:
        raise ValueError(f"{path.name} exceeds the state size limit")
    return json.loads(path.read_text(encoding="utf-8"))


@contextmanager
def lock(folder: Path, name="workspace.lock"):
    path = folder / name
    if path.is_symlink():
        raise ValueError(f"refusing symlink: {name}")
    fd = os.open(path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW, 0o600)
    with os.fdopen(fd, "a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX)
        yield


def workspace(slug: str, root: str | Path | None = None, *, create=True) -> Path:
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{0,79}", slug):
        raise ValueError("slug must contain 1–80 lowercase letters, digits or hyphens")
    base = Path(root or "~/.tmp").expanduser().resolve()
    folder = base / slug
    if folder.is_symlink():
        raise ValueError("workspace must not be a symlink")
    if create:
        base.mkdir(parents=True, exist_ok=True)
        folder.mkdir(mode=0o700, exist_ok=True)
    elif not folder.is_dir():
        raise ValueError("workspace does not exist; initialize it first")
    if folder.stat().st_uid != os.getuid():
        raise ValueError("workspace belongs to another user")
    os.chmod(folder, 0o700)
    return folder


def documents(state: dict) -> dict[str, str]:
    result = {}
    for status in STATUSES:
        lines = [f"# {status.replace('-', ' ').title()}", "",
                 f"{state['title']} · revision {state['revision']} · {state['updated_at']}", "",
                 "Generated progress projection; the owning workflow remains authoritative.", ""]
        if status == "in-progress":
            lines.extend([state["summary"] or "No summary published yet.", ""])
        tasks = [t for t in state["tasks"] if t["status"] == status]
        for task in tasks:
            lines.extend([f"## {task['id']} — {task['title']}", "", task["detail"], ""])
            if task["evidence"]:
                lines.extend(["Evidence: " + task["evidence"], ""])
        if not tasks:
            lines.extend(["No tasks in this section.", ""])
        if status == "in-progress" and state["findings"]:
            lines.extend(["## Findings", "", *[f"- {f}" for f in state["findings"]], ""])
        result[status + ".md"] = "\n".join(lines)
    return result


def project(folder: Path, state: dict) -> None:
    for filename, content in documents(state).items():
        path = folder / filename
        if path.is_symlink():
            raise ValueError(f"refusing symlink: {filename}")
        if not path.exists() or path.read_text(encoding="utf-8") != content:
            atomic(path, content)


def initialize(folder: Path, *, title: str, actor: str, repo_root: str, outcome="", feedback=True) -> dict:
    identity = {"actor": text(actor, "actor", 200), "repo_root": str(Path(repo_root).expanduser().resolve())}
    with lock(folder):
        path = folder / "state.json"
        if path.exists():
            state = load(path)
            if any(state[k] != v for k, v in identity.items()):
                raise ValueError("slug already belongs to a different actor or repository")
        else:
            state = {"schema": SCHEMA, "slug": folder.name, **identity,
                     "title": text(title, "title", 300), "outcome": text(outcome, "outcome", 300),
                     "summary": "", "phase": "starting", "revision": 0, "updated_at": now(),
                     "tasks": [], "findings": [], "agents": [], "artifacts": [], "feedback_enabled": feedback}
            save(path, state)
        project(folder, state)
        handover = folder / "handover.md"
        if not handover.exists():
            atomic(handover, "# Handover\n\nNo handover has been requested.\n")
        if not (folder / "feedback.json").exists():
            save(folder / "feedback.json", [])
        (folder / "artifacts").mkdir(mode=0o700, exist_ok=True)
        return state


def artifact_path(folder: Path, relative: str) -> Path:
    text(relative, "artifact path", 300)
    path = Path(relative)
    if path.is_absolute() or not path.parts or any(p.startswith(".") or p in ("secrets", "credentials") for p in path.parts):
        raise ValueError("artifacts require a visible relative path below artifacts/")
    base = folder / "artifacts"
    if base.is_symlink():
        raise ValueError("artifacts directory must not be a symlink")
    target = base / path
    if any(p.is_symlink() for p in [target, *target.parents] if p != folder.parent):
        raise ValueError("artifact symlinks are not supported")
    if not target.resolve().is_relative_to(base.resolve()):
        raise ValueError("artifact escapes its directory")
    if target.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp", ".svg", ".gif", ".excalidraw", ".pdf"):
        raise ValueError("unsupported artifact format; use a rendered image, PDF or Excalidraw source")
    if not target.is_file():
        raise ValueError("artifact does not exist")
    return target


def validate_snapshot(folder: Path, incoming: dict) -> dict:
    if not isinstance(incoming, dict):
        raise ValueError("snapshot must be an object")  # noqa: TRY004 - stable JSON validation API
    allowed = {"summary", "phase", "tasks", "findings", "agents", "artifacts"}
    if set(incoming) - allowed:
        raise ValueError("unknown snapshot fields: " + ", ".join(sorted(set(incoming) - allowed)))
    result = {}
    for key in ("summary", "phase"):
        if key in incoming:
            result[key] = text(incoming[key], key, 8000 if key == "summary" else 100)
    for key, maximum in (("tasks", 200), ("findings", 100), ("agents", 100), ("artifacts", 40)):
        if key not in incoming:
            continue
        rows = incoming[key]
        if not isinstance(rows, list) or len(rows) > maximum:
            raise ValueError(f"{key} must be a list with at most {maximum} entries")
        if key == "findings":
            result[key] = [text(row, "finding") for row in rows]
            continue
        fields = {"tasks": ("id", "title", "status", "detail", "evidence"),
                  "agents": ("id", "name", "role", "status", "task", "summary", "model", "updated_at",
                             "branch", "worktree", "pr_url", "thread_id", "activity"),
                  "artifacts": ("path", "label")}[key]
        cleaned, identities = [], set()
        for row in rows:
            if not isinstance(row, dict) or set(row) - set(fields):
                raise ValueError(f"invalid {key} entry")
            entry = {field: text(row.get(field, ""), field) for field in fields if field != "activity"}
            if key == "agents":
                activity = row.get("activity", [])
                if not isinstance(activity, list) or len(activity) > 8:
                    raise ValueError("agent activity must be a list of at most eight recent reports")
                entry["activity"] = [text(item, "agent activity", 1000) for item in activity]
                if entry["pr_url"]:
                    parsed = urlsplit(entry["pr_url"])
                    if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password:
                        raise ValueError("agent pr_url must be an absolute HTTP(S) URL without credentials")
            ident = entry.get("id", entry.get("path"))
            if not ident or ident in identities:
                raise ValueError(f"{key} entries require unique identities")
            identities.add(ident)
            if key == "tasks" and (entry["status"] not in STATUSES or not entry["title"]):
                raise ValueError("tasks require title and status in-progress, todo or complete")
            if key == "agents" and entry["status"] not in ("running", "waiting", "complete", "failed", "unknown"):
                raise ValueError("invalid agent status")
            if key == "artifacts":
                artifact_path(folder, entry["path"])
            cleaned.append(entry)
        result[key] = cleaned
    return result


def pending(folder: Path, limit=10, after=0) -> dict:
    if type(after) is not int or after < 0:
        raise ValueError("feedback cursor must be a non-negative integer")
    rows = [r for r in load(folder / "feedback.json", []) if r["status"] == "pending"]
    unseen = [row for row in rows if row["id"] > after]
    batch, cursor, used = [], after, 2
    for row in unseen[:limit]:
        item = {key: row[key] for key in ("id", "kind", "target", "revision", "text")}
        size = len(json.dumps(item, ensure_ascii=False).encode()) + 1
        if used + size > FEEDBACK_BATCH_BYTES:
            if batch:
                break
            # Never present a clipped instruction as if it were the full message.
            item.pop("text")
            item["target_preview"] = item.pop("target")[:200]
            item.update(text_preview=row["text"][:200], truncated=True)
            size = len(json.dumps(item, ensure_ascii=False).encode()) + 1
        batch.append(item)
        cursor = row["id"]
        used += size
    return {"pending_count": len(rows), "feedback": batch, "feedback_cursor": cursor,
            "feedback_more": any(row["id"] > cursor for row in unseen)}


def checkpoint(folder: Path, incoming: dict, expected: int, after_feedback=0) -> dict:
    if type(after_feedback) is not int or after_feedback < 0:
        raise ValueError("feedback cursor must be a non-negative integer")
    update = validate_snapshot(folder, incoming)
    with lock(folder):
        state = load(folder / "state.json")
        if state["revision"] != expected:
            raise ValueError(f"revision conflict: current revision is {state['revision']}")
        previous_agents = {row["id"]: row for row in state["agents"]}
        for agent in update.get("agents", []):
            if not agent["updated_at"]:
                previous = previous_agents.get(agent["id"], {})
                unchanged = all(value == previous.get(key) for key, value in agent.items() if key != "updated_at")
                agent["updated_at"] = previous["updated_at"] if unchanged else now()
        if any(state[key] != value for key, value in update.items()):
            state.update(update)
            state.update(revision=expected + 1, updated_at=now())
            # JSON commits the snapshot; projections are repairable from it on resume.
            save(folder / "state.json", state)
        project(folder, state)
        return {"revision": state["revision"], **pending(folder, after=after_feedback)}


def feedback_item(folder: Path, feedback_id: int) -> dict:
    for row in load(folder / "feedback.json", []):
        if row["id"] == feedback_id:
            return {key: value for key, value in row.items() if key != "client_id"}
    raise ValueError("feedback id not found")


def save_feedback(folder: Path, rows: list) -> None:
    serialized = json.dumps(rows, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if len(serialized.encode()) > 3 * 1024 * 1024:
        raise ValueError("feedback history is full; shorten the disposition or start a new workspace")
    atomic(folder / "feedback.json", serialized)


def record_feedback(folder: Path, body: dict) -> dict:
    if not isinstance(body, dict) or set(body) != {"client_id", "kind", "target", "text", "revision"}:
        raise ValueError("feedback requires client_id, kind, target, text and revision")
    client_id = text(body["client_id"], "client_id", 100)
    if not re.fullmatch(r"[A-Za-z0-9-]{8,100}", client_id):
        raise ValueError("invalid feedback idempotency key")
    message = text(body["text"], "feedback").strip()
    if not message or body["kind"] not in ("feedback", "steer", "question"):
        raise ValueError("feedback requires text and a supported kind")
    with lock(folder):
        state = load(folder / "state.json")
        if not state["feedback_enabled"]:
            raise ValueError("feedback is disabled for this workspace")
        rows = load(folder / "feedback.json", [])
        for row in rows:
            if row["client_id"] == client_id:
                if any(row[k] != body[k] for k in ("kind", "target", "revision")) or row["text"] != message:
                    raise ValueError("idempotency key already used for different feedback")
                return row
        if type(body["revision"]) is not int or not 0 <= body["revision"] <= state["revision"]:
            raise ValueError("feedback revision is invalid")
        targets = {"loop", *[r["id"] for r in state["tasks"]], *[r["id"] for r in state["agents"]]}
        if body["target"] not in targets:
            raise ValueError("feedback target no longer exists; select the loop or a current item")
        if len(rows) >= 2000:
            raise ValueError("feedback history is full; start a new workspace")
        row = {**body, "text": message, "id": len(rows) + 1, "created_at": now(),
               "status": "pending", "response": None}
        rows.append(row)
        save_feedback(folder, rows)
        return row


def acknowledge(folder: Path, feedback_id: int, response: str) -> dict:
    response = text(response, "response").strip()
    if not response:
        raise ValueError("acknowledgement requires an explanation of the disposition")
    with lock(folder):
        rows = load(folder / "feedback.json", [])
        for row in rows:
            if row["id"] == feedback_id:
                row.update(status="acknowledged", response=response, acknowledged_at=now())
                save_feedback(folder, rows)
                return {"id": feedback_id, "status": "acknowledged"}
        raise ValueError("feedback id not found")


def handover(folder: Path, content: str, owner_request: str) -> None:
    if not text(owner_request, "owner request").strip():
        raise ValueError("handover requires an explicit owner request")
    with lock(folder):
        load(folder / "state.json")
        atomic(folder / "handover.md", text(content, "handover", MAX_JSON))
        save(folder / "handover-request.json", {"request": owner_request, "recorded_at": now()})


def attach(folder: Path, agent_id: str, provider: str, source: str) -> dict:
    from loop_telemetry import validate_source

    path = Path(source).expanduser().absolute()
    if provider not in ("codex", "claude") or path.suffix != ".jsonl":
        raise ValueError("attach requires codex/claude and an explicit .jsonl transcript")
    if any(p.startswith(".env") or p.lower() in ("secrets", "credentials") for p in path.parts):
        raise ValueError("secret paths cannot be attached")
    if path.is_symlink():
        raise ValueError("transcript must not be a symlink")
    validated = validate_source({"id": agent_id, "provider": provider, "path": str(path)})
    path = Path(validated["path"])
    with lock(folder):
        state = load(folder / "state.json")
        if agent_id not in {state["actor"], *[r["id"] for r in state["agents"]]}:
            raise ValueError("attach the parent actor or a published agent id")
        rows = load(folder / "sources.json", [])
        if any(r["id"] != agent_id and r["path"] == str(path) for r in rows):
            raise ValueError("transcript already attached; refusing to double-count it")
        rows = [r for r in rows if r["id"] != agent_id]
        rows.append({"id": agent_id, "provider": provider, "path": str(path)})
        save(folder / "sources.json", rows)
    return {"attached": agent_id, "provider": provider}


def watch_codex(folder: Path, thread_id: str, home=None) -> dict:
    from runtime_sources import configuration, resolve

    config = configuration(thread_id, home)
    with lock(folder):
        state = load(folder / "state.json")
        existing = load(folder / "runtime.json", {})
        if existing and existing != config:
            raise ValueError("workspace already watches another Codex parent or home")
        # Validate the configured parent and index before committing the locator.
        resolve(config, state["actor"], state["agents"], load(folder / "sources.json", []))
        if existing != config:
            save(folder / "runtime.json", config)
    return {"watching": "codex", "thread_id": config["thread_id"]}


def health(info: dict) -> bool:
    try:
        with urlopen(info["url"] + "api/health", timeout=0.5) as reply:
            return json.load(reply) == {"instance": info["instance"], "pid": info["pid"]}
    except (URLError, OSError, ValueError, KeyError):
        return False


def serve(folder: Path, bind: str, port: int) -> dict:
    address = ipaddress.ip_address(bind)
    if address.version != 4 or not (address.is_loopback or address in ipaddress.ip_network("100.64.0.0/10")):
        raise ValueError("bind must be an IPv4 loopback or explicit Tailscale address")
    with lock(folder, "server.lock"):
        load(folder / "state.json")
        old = load(folder / "server.json", {})
        if old and health(old):
            if old["bind"] != bind or (port and old["port"] != port):
                raise ValueError("server already running on another address; stop it first")
            return {"url": old["url"], "pid": old["pid"], "reused": True}
        instance = secrets.token_urlsafe(24)
        log_path = folder / "server.log"
        if log_path.is_symlink():
            raise ValueError("server log must not be a symlink")
        with open(log_path, "ab") as log:
            process = subprocess.Popen([sys.executable, str(Path(__file__).resolve()),
                "--root", str(folder.parent), "--slug", folder.name, "_serve", "--bind", bind,
                "--port", str(port), "--instance", instance], stdin=subprocess.DEVNULL,
                stdout=log, stderr=log, start_new_session=True)
        deadline = time.monotonic() + 8
        while time.monotonic() < deadline:
            current = load(folder / "server.json", {})
            if current.get("instance") == instance and health(current):
                # Reap the child if this CLI is embedded in a longer-lived caller.
                threading.Thread(target=process.wait, daemon=True).start()
                return {"url": current["url"], "pid": current["pid"], "reused": False}
            if process.poll() is not None:
                raise ValueError(f"server startup failed; see {log_path}")
            time.sleep(0.05)
        process.terminate()
        process.wait(timeout=3)
        raise ValueError(f"server startup timed out; see {log_path}")


def stop(folder: Path) -> dict:
    with lock(folder, "server.lock"):
        info = load(folder / "server.json", {})
        if not info or not health(info):
            return {"stopped": False, "reason": "no verified live server; no process signalled"}
        os.kill(info["pid"], signal.SIGTERM)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if not health(info):
                return {"stopped": True}
            time.sleep(0.05)
        raise ValueError("server did not stop within five seconds; its verified instance was signalled once")


def read_input(source: str) -> str:
    if source == "-":
        raw = sys.stdin.buffer.read(MAX_JSON + 1)
    else:
        with Path(source).open("rb") as stream:
            raw = stream.read(MAX_JSON + 1)
    if len(raw) > MAX_JSON:
        raise ValueError("input exceeds 256KiB")
    return raw.decode("utf-8")


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--slug", required=True)
    p.add_argument("--root", help="workspace parent (default ~/.tmp)")
    commands = p.add_subparsers(dest="command", required=True)
    init = commands.add_parser("init", help="create or resume a workspace without overwriting its content")
    for arg in ("title", "actor", "repo-root"):
        init.add_argument("--" + arg, required=True)
    init.add_argument("--outcome", default="")
    init.add_argument("--no-feedback", action="store_true")
    init.add_argument("--codex-thread", default=os.environ.get("CODEX_THREAD_ID"),
                      help="watch this Codex parent and known children; defaults to CODEX_THREAD_ID")
    init.add_argument("--codex-home", help="runtime home; defaults to CODEX_HOME or ~/.codex")
    update = commands.add_parser("checkpoint", help="merge a small snapshot and return bounded pending feedback")
    update.add_argument("--input", default="-", help="JSON file or - for stdin")
    update.add_argument("--expected-revision", type=int, required=True)
    update.add_argument("--after-feedback", type=int, default=0, help="last surfaced feedback id")
    status = commands.add_parser("status", help="compact checkpoint status, never the full dashboard")
    status.add_argument("--since", type=int)
    status.add_argument("--after-feedback", type=int, default=0)
    inbox = commands.add_parser("inbox", help="read bounded new feedback or one full item; never consumes it")
    inbox.add_argument("--after-feedback", type=int, default=0)
    inbox.add_argument("--id", type=int, help="read one full feedback item before acting on a preview")
    ack = commands.add_parser("ack", help="record the disposition of one feedback item")
    ack.add_argument("--id", type=int, required=True)
    ack.add_argument("--response", required=True)
    manual = commands.add_parser("handover", help="write handover only after a manual owner request")
    manual.add_argument("--input", required=True)
    manual.add_argument("--owner-request", required=True)
    source = commands.add_parser("attach", help="incrementally measure an explicit parent/child transcript")
    source.add_argument("--id", required=True)
    source.add_argument("--provider", choices=("codex", "claude"), required=True)
    source.add_argument("--path", required=True)
    watch = commands.add_parser("watch-codex", help="resolve this parent and its known agents from the runtime index")
    watch.add_argument("--thread-id", default=os.environ.get("CODEX_THREAD_ID"))
    watch.add_argument("--home")
    for command in ("serve", "_serve"):
        server = commands.add_parser(command)
        server.add_argument("--bind", default="127.0.0.1")
        server.add_argument("--port", type=int, default=0)
        if command == "_serve":
            server.add_argument("--instance", required=True)
    commands.add_parser("stop", help="stop only this workspace's verified server")
    return p


def main() -> int:
    os.umask(0o077)
    args = parser().parse_args()
    try:
        folder = workspace(args.slug, args.root, create=args.command == "init")
        if args.command == "init":
            state = initialize(folder, title=args.title, actor=args.actor, repo_root=args.repo_root,
                               outcome=args.outcome, feedback=not args.no_feedback)
            result = {"workspace": str(folder), "revision": state["revision"], "files": FILES}
            if args.codex_thread and not (folder / "runtime.json").exists():
                try:
                    result.update(watch_codex(folder, args.codex_thread, args.codex_home))
                except ValueError as error:
                    result["usage_warning"] = str(error)
        elif args.command == "checkpoint":
            result = checkpoint(folder, json.loads(read_input(args.input)), args.expected_revision, args.after_feedback)
        elif args.command in ("status", "inbox"):
            with lock(folder):
                state = load(folder / "state.json")
                if args.command == "inbox" and args.id is not None:
                    result = {"feedback": feedback_item(folder, args.id)}
                else:
                    result = {"revision": state["revision"], **pending(folder, after=args.after_feedback)}
                    if args.command == "status":
                        result.update(changed=state["revision"] != args.since, phase=state["phase"])
        elif args.command == "ack":
            result = acknowledge(folder, args.id, args.response)
        elif args.command == "handover":
            handover(folder, read_input(args.input), args.owner_request)
            result = {"handover": "updated"}
        elif args.command == "attach":
            result = attach(folder, args.id, args.provider, args.path)
        elif args.command == "watch-codex":
            result = watch_codex(folder, args.thread_id, args.home)
        elif args.command == "serve":
            result = serve(folder, args.bind, args.port)
        elif args.command == "stop":
            result = stop(folder)
        else:
            from dashboard_server import run
            run(folder, args.bind, args.port, args.instance)
            return 0
        print(json.dumps(result, ensure_ascii=False, separators=(",", ":")))
        return 0
    except (ValueError, OSError) as error:
        print(json.dumps({"error": str(error)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
