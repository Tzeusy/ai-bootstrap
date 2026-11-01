#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Parallel-coordinator registry kept in the Beads kv store.

The pure readers (`registrations`, `live_coordinator_ids`, `lane_budget`) are
shared by `rank_ready_work.py` and `beads-cleanup/scripts/cleanup_scan.py`, so
both judge coordinator liveness and the global lane budget identically.

The command line is the only writer, run by the coordinator for its own key
(`references/runtime-and-safety.md` → "Parallel Coordinators"). It computes
timestamps itself, because a hand-written `expires_at` is how a dead
coordinator stays "live" for a day or a live one reads as dead:

    uv run scripts/coordinator_registry.py new-id --runtime claude
    uv run scripts/coordinator_registry.py register --repo-root "$REPO_ROOT" \
        --id "$COORDINATOR_ID" --wake-minutes 30 [--startup] [--extra-lanes N]
    uv run scripts/coordinator_registry.py deregister --repo-root "$REPO_ROOT" --id "$COORDINATOR_ID"

`register` writes `{"expires_at": now + wake + 15m}` (plus `extra_lanes`) only
when the stored entry would lapse before the next wake or its `extra_lanes`
changed, so routine wakes add no tracker history. `--startup` refuses an id
that is already live: two sessions sharing an id share every claim.

A failed `bd` call prints `{"action": "failed", "step": ..., "error": <code>,
"detail": <last stderr line>, "attempts": N}`. `classify_failure` names the
code: `server-timeout` (a transient Dolt server blip, retried up to three
attempts in all), `connection-refused` (never retried: on the shared server it
means the host override is missing, not a blip), or `command-failed`.
`cleanup_scan.py` reuses the classifier for its sanitized error codes.
"""

from __future__ import annotations

import argparse
import json
import re
import secrets
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

REGISTRY_PREFIX = "beads.coordinator."
BUDGET_KEY = "beads.max_lanes"
DEFAULT_LANE_BUDGET = 4
GRACE = timedelta(minutes=15)
RENEW_MARGIN = timedelta(minutes=5)
# No legitimate registration reaches this far ahead (the longest wake is 60
# minutes plus grace), so a value beyond it is a bad write and is not live.
MAX_AHEAD = timedelta(hours=3)
RUNTIME_RE = re.compile(r"[a-z][a-z0-9-]{0,15}\Z")
# Seconds slept between attempts of a `bd` call that hit a transient server
# error; three attempts in all. Tests patch `sleep`.
RETRY_DELAYS = (1.0, 2.0)
DETAIL_LIMIT = 200
REFUSED_MARKERS = ("connection refused",)
TRANSIENT_MARKERS = (
    "i/o timeout",
    "deadline exceeded",
    "context deadline",
    "timed out",
    "connection reset",
    "broken pipe",
    "unexpected eof",
    "bad connection",
    "invalid connection",
)
sleep = time.sleep


def parse_time(value: object) -> datetime | None:
    if not isinstance(value, str) or not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return None
    return parsed.astimezone(timezone.utc)


def format_time(value: datetime) -> str:
    return value.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def registrations(kv: dict[str, Any], now: datetime) -> dict[str, dict[str, Any]]:
    """Map each registered coordinator id to `{expires_at, live, extra_lanes}`.

    A value is either a JSON object carrying `expires_at` (and optionally
    `extra_lanes`, lanes the tracker cannot see, such as Team Lead subworkers)
    or a bare RFC 3339 timestamp. An unparseable value, or one further ahead
    than `MAX_AHEAD`, registers the id as not live, so a malformed write can
    never make a dead coordinator look alive.
    """
    found: dict[str, dict[str, Any]] = {}
    for key, raw in kv.items():
        if not isinstance(key, str) or not key.startswith(REGISTRY_PREFIX):
            continue
        coordinator_id = key[len(REGISTRY_PREFIX):]
        if not coordinator_id:
            continue
        value: object = raw
        if isinstance(raw, str) and raw.lstrip().startswith("{"):
            try:
                value = json.loads(raw)
            except json.JSONDecodeError:
                value = None
        expires_text = value.get("expires_at") if isinstance(value, dict) else value
        expires = parse_time(expires_text)
        extra = value.get("extra_lanes") if isinstance(value, dict) else 0
        found[coordinator_id] = {
            "expires_at": expires_text if expires is not None else None,
            "extra_lanes": extra if isinstance(extra, int) and not isinstance(extra, bool) and extra > 0 else 0,
            "live": expires is not None and now < expires <= now + MAX_AHEAD,
        }
    return found


def live_coordinator_ids(kv: dict[str, Any], now: datetime) -> set[str]:
    return {cid for cid, entry in registrations(kv, now).items() if entry["live"]}


def lane_budget(kv: dict[str, Any], override: int | None = None) -> tuple[int, str]:
    """Return the global lane budget and where it came from."""
    if override is not None and override >= 1:
        return override, "flag"
    raw = kv.get(BUDGET_KEY)
    try:
        value = int(str(raw).strip())
    except (TypeError, ValueError):
        return DEFAULT_LANE_BUDGET, "default"
    if value < 1:
        return DEFAULT_LANE_BUDGET, "default"
    return value, "kv"


def new_id(runtime: str, now: datetime) -> str:
    return f"coordinator:{runtime}-{now.strftime('%Y%m%d')}-{secrets.token_hex(4)}"


def plan_registration(
    kv: dict[str, Any], coordinator_id: str, *, now: datetime, wake: timedelta, extra_lanes: int, startup: bool
) -> tuple[str, dict[str, Any] | None]:
    """Decide what `register` should do: `refuse`, `skip`, or `write` a value."""
    current = registrations(kv, now).get(coordinator_id)
    if startup and current and current["live"]:
        return "refuse", None
    value: dict[str, Any] = {"expires_at": format_time(now + wake + GRACE)}
    if extra_lanes > 0:
        value["extra_lanes"] = extra_lanes
    if current and current["live"] and current["extra_lanes"] == extra_lanes:
        stored = parse_time(current["expires_at"])
        if stored is not None and stored >= now + wake + RENEW_MARGIN:
            return "skip", None
    return "write", value


def classify_failure(returncode: int | None, stderr: str | None) -> str:
    """Name a failed command's cause with a sanitized code.

    `returncode` is the exit status, or None when the command never started.
    Only `server-timeout` is worth retrying.
    """
    message = (stderr or "").lower()
    if returncode is not None and any(marker in message for marker in REFUSED_MARKERS):
        return "connection-refused"
    if returncode is not None and any(marker in message for marker in TRANSIENT_MARKERS):
        return "server-timeout"
    return "command-failed"


def last_line(text: str | None) -> str:
    lines = [line.strip() for line in (text or "").splitlines() if line.strip()]
    return lines[-1][:DETAIL_LIMIT] if lines else ""


def failure_text(result: subprocess.CompletedProcess[str]) -> str:
    # bd reports most errors on stderr; fall back to stdout when it stays silent.
    return result.stderr if (result.stderr or "").strip() else (result.stdout or "")


def bd(argv: list[str], repo_root: Path, actor: str) -> tuple[subprocess.CompletedProcess[str], int]:
    """Run one `bd` call, retrying transient server errors; return it and the attempt count."""
    attempts = 0
    while True:
        attempts += 1
        result = subprocess.run(
            ["bd", "-C", str(repo_root), "--actor", actor, *argv],
            capture_output=True,
            cwd=repo_root,
            text=True,
            check=False,
        )
        retryable = classify_failure(result.returncode, failure_text(result)) == "server-timeout"
        if result.returncode == 0 or not retryable or attempts > len(RETRY_DELAYS):
            return result, attempts
        sleep(RETRY_DELAYS[attempts - 1])


def failure(step: str, coordinator_id: str, result: subprocess.CompletedProcess[str], attempts: int) -> dict[str, Any]:
    text = failure_text(result)
    return {
        "action": "failed",
        "attempts": attempts,
        "detail": last_line(text),
        "error": classify_failure(result.returncode, text),
        "id": coordinator_id,
        "step": step,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Write this coordinator's registry entry.")
    sub = parser.add_subparsers(dest="command", required=True)
    make = sub.add_parser("new-id", help="Print a fresh COORDINATOR_ID.")
    make.add_argument("--runtime", required=True, help="Short runtime name, e.g. claude or codex.")
    for name in ("register", "deregister"):
        command = sub.add_parser(name)
        command.add_argument("--repo-root", required=True, type=Path)
        command.add_argument("--id", required=True, help="This coordinator's COORDINATOR_ID.")
        if name == "register":
            command.add_argument("--wake-minutes", required=True, type=int, help="Minutes until the next planned wake.")
            command.add_argument("--extra-lanes", type=int, default=0, help="Lanes the tracker cannot see (Team Lead subworkers).")
            command.add_argument("--startup", action="store_true", help="Refuse if this id is already live.")
    args = parser.parse_args()
    now = datetime.now(timezone.utc)

    if args.command == "new-id":
        if not RUNTIME_RE.fullmatch(args.runtime):
            print(json.dumps({"error": "invalid-runtime"}))
            return 2
        print(new_id(args.runtime, now))
        return 0

    if not args.id.startswith("coordinator:"):
        print(json.dumps({"error": "id-must-start-with-coordinator"}))
        return 2
    key = REGISTRY_PREFIX + args.id
    repo_root = args.repo_root.resolve()
    if args.command == "deregister":
        result, attempts = bd(["kv", "clear", key], repo_root, args.id)
        if result.returncode != 0:
            print(json.dumps(failure("kv-clear", args.id, result, attempts)))
            return 1
        print(json.dumps({"action": "cleared", "id": args.id}))
        return 0

    listing, attempts = bd(["kv", "list", "--json"], repo_root, args.id)
    if listing.returncode != 0:
        print(json.dumps(failure("kv-list", args.id, listing, attempts)))
        return 1
    try:
        kv = json.loads(listing.stdout)
    except json.JSONDecodeError:
        kv = None
    if not isinstance(kv, dict):
        print(json.dumps({"action": "failed", "attempts": attempts, "detail": "", "error": "invalid-json", "id": args.id, "step": "kv-list"}))
        return 1
    action, value = plan_registration(
        kv,
        args.id,
        now=now,
        wake=timedelta(minutes=max(args.wake_minutes, 0)),
        extra_lanes=max(args.extra_lanes, 0),
        startup=args.startup,
    )
    if action == "refuse":
        print(json.dumps({"action": "refused", "error": "id-already-live", "id": args.id}))
        return 3
    if action == "skip":
        print(json.dumps({"action": "skipped", "id": args.id}))
        return 0
    result, attempts = bd(["kv", "set", key, json.dumps(value, separators=(",", ":"))], repo_root, args.id)
    if result.returncode != 0:
        print(json.dumps({**failure("kv-set", args.id, result, attempts), **(value or {})}))
        return 1
    print(json.dumps({"action": "written", "id": args.id, **(value or {})}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
