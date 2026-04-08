#!/usr/bin/env python3
"""Validate tmux-oriented dev bootstrap scripts generated from this skill."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


def has(pattern: str, text: str) -> bool:
    return re.search(pattern, text, re.MULTILINE) is not None


PLACEHOLDER_RE = re.compile(r"__[A-Z0-9_]+__")


def non_comment_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.strip() and not line.lstrip().startswith("#")]


def active_wait_calls(lines: list[str]) -> list[str]:
    calls: list[str] = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("wait_for_port()") or stripped.startswith("wait_for_http()"):
            continue
        if re.search(r"\bwait_for_(?:port|http)\b", stripped):
            calls.append(stripped)
    return calls


def pane_counts_by_window(lines: list[str]) -> dict[str, int]:
    pane_to_window: dict[str, str] = {}
    counts: defaultdict[str, int] = defaultdict(int)

    for line in lines:
        new_match = re.search(
            r'^(?P<pane>[A-Z0-9_]+)=\$\(\s*tmux new-window .* -n "(?P<window>[^"]+)" .*#\{pane_id\}',
            line,
        )
        if new_match:
            pane = new_match.group("pane")
            window = new_match.group("window")
            pane_to_window[pane] = window
            counts[window] += 1
            continue

        split_match = re.search(
            r'^(?P<pane>[A-Z0-9_]+)=\$\(\s*tmux split-window -t "\$(?P<target>[A-Z0-9_]+)" .*#\{pane_id\}',
            line,
        )
        if split_match:
            pane = split_match.group("pane")
            target = split_match.group("target")
            window = pane_to_window.get(target)
            if window:
                pane_to_window[pane] = window
                counts[window] += 1

    return dict(counts)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate a generated dev bootstrap script for required tmux/bootstrap invariants."
    )
    parser.add_argument("script", help="Path to the generated dev bootstrap script")
    parser.add_argument(
        "--expect-multi-window",
        action="store_true",
        help="Require evidence of multiple tmux windows",
    )
    parser.add_argument(
        "--expect-tailscale",
        action="store_true",
        help="Require opt-in Tailscale support",
    )
    parser.add_argument(
        "--allow-placeholders",
        action="store_true",
        help="Allow template placeholders like __CMD_API__ instead of treating them as errors",
    )
    args = parser.parse_args()

    script_path = Path(args.script)
    if not script_path.is_file():
        print(
            json.dumps(
                {"ok": False, "errors": [f"Script not found: {script_path}"], "warnings": []},
                indent=2,
            )
        )
        return 1

    text = script_path.read_text(encoding="utf-8")
    active_lines = non_comment_lines(text)
    active_text = "\n".join(active_lines)
    errors: list[str] = []
    warnings: list[str] = []
    checks: dict[str, bool] = {}

    required_checks = {
        "header_layout_comment": r"(?m)^# Layout",
        "strict_mode": r"(?m)^set -euo pipefail$",
        "session_detection": r'\$\{TMUX:-\}|display-message -p',
        "idempotent_window_teardown": r'tmux kill-window -t "\$\{SESSION\}:',
        "pane_id_capture": r"-P -F '#\{pane_id\}'",
        "log_latest_symlink": r"LOGS_LATEST_LINK=.*logs/\$\{?latest|\$\{LOGS_ROOT\}/latest",
        "pipe_pane_o": r"tmux pipe-pane -o",
        "send_keys": r"tmux send-keys -t",
        "readiness_helper": r"wait_for_port|wait_for_http",
        "local_url_output": r"Local frontend URL:|Local backend API base URL:",
        "post_split_delay": r"sleep 0\.[0-9]+",
    }

    forbidden_checks = {
        "numeric_pane_select": r"tmux select-pane -t [0-9]+\b",
        "numeric_pane_send_keys": r"tmux send-keys -t [0-9]+\b",
    }

    for name, pattern in required_checks.items():
        matched = has(pattern, text)
        checks[name] = matched
        if not matched:
            errors.append(f"Missing required pattern: {name}")

    for name, pattern in forbidden_checks.items():
        matched = has(pattern, text)
        checks[name] = not matched
        if matched:
            errors.append(f"Forbidden numeric pane targeting detected: {name}")

    placeholders = sorted(set(PLACEHOLDER_RE.findall(text)))
    checks["placeholders_replaced"] = not placeholders
    if placeholders and not args.allow_placeholders:
        errors.append(f"Unreplaced placeholders detected: {', '.join(placeholders)}")

    env_cmd_defined = has(r'(?m)^ENV_CMD=', text)
    env_cmd_used = has(r'tmux send-keys -t "\$PANE_[^"]+" "\$\{ENV_CMD\}', active_text)
    checks["env_cmd_used"] = (not env_cmd_defined) or env_cmd_used
    if env_cmd_defined and not env_cmd_used:
        errors.append("ENV_CMD is defined but not visibly prefixed into active tmux send-keys commands")

    send_keys_count = len(re.findall(r"tmux send-keys -t", active_text))
    wait_calls = active_wait_calls(active_lines)
    checks["active_readiness_calls"] = bool(wait_calls)
    if send_keys_count > 1 and not wait_calls and not args.allow_placeholders:
        errors.append("No active readiness calls found for a multi-service script")

    pane_counts = pane_counts_by_window(active_lines)
    checks["pane_limit_per_window"] = bool(pane_counts) and all(count <= 4 for count in pane_counts.values())
    if pane_counts and any(count > 4 for count in pane_counts.values()):
        over = ", ".join(f"{window}={count}" for window, count in sorted(pane_counts.items()) if count > 4)
        errors.append(f"More than 4 panes detected in one or more windows: {over}")

    if args.expect_multi_window:
        multi_window_ok = len(pane_counts) >= 2
        checks["multi_window"] = multi_window_ok
        if not multi_window_ok:
            errors.append("Expected multi-window scaffold, but did not find one")

    if args.expect_tailscale:
        tailscale_ok = (
            has(r"ENABLE_TAILSCALE_SERVE", text)
            and has(r"--enable-tailscale-serve", text)
            and has(r'if \[ "\$ENABLE_TAILSCALE_SERVE" = "true" \]', text)
            and has(r"ensure_tailscale_serve", text)
        )
        checks["tailscale_opt_in"] = tailscale_ok
        if not tailscale_ok:
            errors.append("Expected opt-in Tailscale support, but did not find it")

    result = {
        "ok": not errors,
        "errors": errors,
        "warnings": warnings,
        "checks": checks,
        "pane_counts_by_window": pane_counts,
        "script": str(script_path),
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
