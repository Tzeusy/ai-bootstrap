#!/usr/bin/env python3
import argparse
import json
import os
from pathlib import Path


def package_json_commands(root: Path):
    package_json = root / "package.json"
    if not package_json.exists():
        return {}
    payload = json.loads(package_json.read_text())
    scripts = payload.get("scripts") or {}
    commands = {}
    for gate in ("lint", "typecheck", "test", "check"):
        if gate in scripts:
            commands[gate] = f"npm run {gate}"
    return commands


def lines_from(path: Path):
    if not path.exists():
        return []
    return path.read_text().splitlines()


def rule_commands(root: Path, filename: str):
    path = root / filename
    commands = {}
    for line in lines_from(path):
        stripped = line.strip()
        for gate in ("lint", "typecheck", "test", "check"):
            if stripped.startswith(f"{gate}:"):
                commands[gate] = f"{filename}::{gate}"
    return commands


def main():
    argparse.ArgumentParser(description="Discover likely quality-gate commands from common project manifests.").parse_args()
    root = Path(os.getcwd())
    discovered = {}
    sources = {}

    for source_name, source_commands in (
        ("package.json", package_json_commands(root)),
        ("Makefile", rule_commands(root, "Makefile")),
        ("justfile", rule_commands(root, "justfile")),
    ):
        for gate, command in source_commands.items():
            discovered.setdefault(gate, []).append(command)
            sources.setdefault(gate, []).append(source_name)

    output = {
        "ok": True,
        "cwd": str(root),
        "commands": discovered,
        "sources": sources,
        "note": "Use these as candidates when project docs do not specify quality gates explicitly.",
    }
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
