from __future__ import annotations

import json
from pathlib import Path

import yaml


PACKAGE = Path(__file__).resolve().parents[1]
ROUTER = PACKAGE / "SKILL.md"
SUBSKILLS = PACKAGE / "subskills"


def frontmatter(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    _, raw, _ = text.split("---", 2)
    return yaml.safe_load(raw)


def test_router_has_exactly_three_hidden_subskills() -> None:
    packages = sorted(SUBSKILLS.glob("*/SKILL.md"))
    assert len(packages) == 3
    assert {frontmatter(path)["name"] for path in packages} == {
        "writing-editorial-review",
        "writing-publish-hardening",
        "writing-structured-doc",
    }


def test_router_covers_every_subskill_without_loading_its_body() -> None:
    router = ROUTER.read_text(encoding="utf-8")
    for path in SUBSKILLS.glob("*/SKILL.md"):
        relative = path.relative_to(PACKAGE).as_posix()
        assert f"]({relative})" in router


def test_unloaded_routing_cases_cover_all_classes_and_routes() -> None:
    routing = json.loads((PACKAGE / "evals/routing.json").read_text())
    assert routing["schema_version"] == 1
    assert routing["router"] == "th-writing"
    cases = routing["cases"]
    assert len(cases) == 8
    assert len({case["id"] for case in cases}) == len(cases)
    assert len({case["query"] for case in cases}) == len(cases)
    assert {case["kind"] for case in cases} == {"positive", "negative", "ambiguous"}
    assert {case["expected_routes"][0] for case in cases if case["kind"] == "positive"} == {
        "writing-editorial-review",
        "writing-publish-hardening",
        "writing-structured-doc",
    }
    assert all(case["expected_routes"] == [] for case in cases if case["kind"] == "negative")
    assert all(len(case["expected_routes"]) >= 2 for case in cases if case["kind"] == "ambiguous")


def test_active_package_avoids_obsolete_platform_contracts() -> None:
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in PACKAGE.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    )
    forbidden = (
        "Ask" + "UserQuestion",
        "Web" + "Search",
        "Web" + "Fetch",
        "create" + "_file",
        "str" + "_replace",
        "Reader" + " Claude",
    )
    assert not [term for term in forbidden if term in text]
