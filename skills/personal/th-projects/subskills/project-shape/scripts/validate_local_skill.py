#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = [
#   "pyyaml>=6,<7",
# ]
# ///
"""Validate the frontmatter that project-shape counts as a local pillar skill."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml
from yaml.constructor import ConstructorError
from yaml.nodes import MappingNode


MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
EXPECTED_KEYS = {"name", "description"}
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
FRONTMATTER_RE = re.compile(r"\A---\n(.*?)\n---(?:\n|\Z)", re.DOTALL)


class UniqueKeySafeLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def construct_unique_mapping(
    loader: UniqueKeySafeLoader, node: MappingNode, deep: bool = False
) -> dict[Any, Any]:
    loader.flatten_mapping(node)
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeySafeLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_unique_mapping
)


def fail(message: str) -> tuple[bool, str]:
    return False, message


def validate(skill_file: Path, expected_name: str) -> tuple[bool, str]:
    try:
        content = skill_file.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        return fail(f"cannot read UTF-8 SKILL.md: {exc}")

    match = FRONTMATTER_RE.match(content)
    if not match:
        return fail("frontmatter must use exact opening and closing --- lines")

    try:
        frontmatter = yaml.load(match.group(1), Loader=UniqueKeySafeLoader)
    except ConstructorError as exc:
        problem = exc.problem or "invalid mapping"
        duplicate = re.fullmatch(r"found duplicate key '([^']+)'", problem)
        if duplicate:
            return fail(f"duplicate {duplicate.group(1)} key")
        return fail(f"invalid YAML frontmatter: {problem}")
    except yaml.YAMLError as exc:
        summary = str(exc).splitlines()[0]
        return fail(f"invalid YAML frontmatter: {summary}")

    if not isinstance(frontmatter, dict):
        return fail("frontmatter must be a YAML mapping")
    if not all(isinstance(key, str) for key in frontmatter):
        return fail("frontmatter keys must be strings")

    keys = set(frontmatter)
    missing = sorted(EXPECTED_KEYS - keys)
    if missing:
        return fail(f"missing required frontmatter key(s): {', '.join(missing)}")
    unsupported = sorted(keys - EXPECTED_KEYS)
    if unsupported:
        return fail(f"unsupported frontmatter key(s): {', '.join(unsupported)}")

    name = frontmatter["name"]
    if not isinstance(name, str):
        return fail("name must be a string")
    name = name.strip()
    if not name:
        return fail("name must be non-empty")
    if not NAME_RE.fullmatch(name):
        return fail(
            "name must use lowercase letters, numbers, and single hyphens only"
        )
    if len(name) > MAX_NAME_LENGTH:
        return fail(f"name exceeds {MAX_NAME_LENGTH} characters")
    if "anthropic" in name or "claude" in name:
        return fail("name uses a reserved word")
    if name != expected_name:
        return fail(f"name must match expected local skill '{expected_name}'")

    description = frontmatter["description"]
    if not isinstance(description, str):
        return fail("description must be a conservative YAML string scalar")
    description = description.strip()
    if not description:
        return fail("description must be non-empty")
    if "<" in description or ">" in description:
        return fail("description cannot contain angle brackets")
    if len(description) > MAX_DESCRIPTION_LENGTH:
        return fail(f"description exceeds {MAX_DESCRIPTION_LENGTH} characters")

    return True, "frontmatter is valid"


def main() -> int:
    if len(sys.argv) != 3:
        print("usage: validate_local_skill.py <SKILL.md> <expected-name>")
        return 2
    valid, message = validate(Path(sys.argv[1]), sys.argv[2])
    print(message if valid else f"invalid skill frontmatter: {message}")
    return 0 if valid else 1


if __name__ == "__main__":
    raise SystemExit(main())
