#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.9"
# dependencies = []
# ///
"""Self-test for audit_skill.py against the checked-in adversarial fixtures.

Runs the audit as a subprocess on tests/fixtures/* and asserts that each
deliberate defect is reported (and that exemptions stay silent). Finishes by
auditing the skill-standards package itself in --strict mode, which must PASS.

Usage:
  uv run tests/run_tests.py

Exit codes: 0 = all assertions hold, 1 = at least one failed.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PACKAGE = HERE.parent
AUDIT = PACKAGE / "scripts" / "audit_skill.py"
FIXTURES = HERE / "fixtures"

failures: list[str] = []


def run_audit(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["uv", "run", str(AUDIT), *args],
        capture_output=True, text=True,
    )


def check(cond: bool, msg: str) -> None:
    print(f"{'ok  ' if cond else 'FAIL'} {msg}")
    if not cond:
        failures.append(msg)


def main() -> int:
    # --- broken-skill: standard-package defects ---
    res = run_audit(str(FIXTURES / "broken-skill"))
    out = res.stdout
    check(res.returncode == 1, "broken-skill exits 1")
    check("name 'Broken_Skill' is not lowercase" in out, "bad name casing is an ERROR")
    check("description contains placeholder text" in out, "placeholder description is an ERROR")
    check("links to missing file './references/nope.md'" in out, "broken link is an ERROR")
    check("scripts/run_thing.py lacks PEP 723" in out, "top-level script without PEP 723 is an ERROR")
    check("scripts/pkg/nested_main.py lacks PEP 723" in out, "nested __main__ script without PEP 723 is an ERROR")
    check("__init__.py lacks PEP 723" not in out, "__init__.py is exempt from PEP 723")
    check("library_module.py lacks PEP 723" not in out, "nested library module is exempt from PEP 723")
    check("references/orphan.md is never linked" in out, "orphan reference is a WARN")
    check("scripts/run_thing.py is never linked" in out, "orphan top-level script is a WARN")
    check("assets/orphan-asset.txt is never linked" in out, "orphan asset is a WARN")
    check("deep-chain.md is linked only transitively" in out, "deep reference chain is a WARN")
    check("unexpected top-level directory tests/" not in out, "tests/ is an accepted directory")
    check("unexpected top-level directory evals/" not in out, "evals/ is an accepted directory")

    # --- broken-superskill: router and subskill defects ---
    res = run_audit(str(FIXTURES / "broken-superskill"))
    out = res.stdout
    check(res.returncode == 1, "broken-superskill exits 1")
    check("no routing-table link to subskills/sub-b/SKILL.md" in out,
          "fence-only mention of a subskill does not count as routing")
    check("no routing-table link to subskills/sub-a/SKILL.md" not in out,
          "markdown-linked subskill passes the routing check")
    check("duplicates broken-superskill/subskills/sub-a" in out, "duplicate subskill name is an ERROR")

    # --- batch + JSON over the fixtures root ---
    res = run_audit("--all", str(FIXTURES), "--json")
    check(res.returncode == 1, "--all over fixtures exits 1")
    try:
        report = json.loads(res.stdout)
        check(report["status"] == "FAIL", "JSON status is FAIL")
        check(sorted(p["name"] for p in report["packages"]) == ["broken-skill", "broken-superskill"],
              "JSON discovers exactly the two fixture packages")
    except (json.JSONDecodeError, KeyError) as exc:
        check(False, f"--json output parses: {exc}")

    # --- the package itself must hold its own bar ---
    res = run_audit(str(PACKAGE), "--strict")
    check(res.returncode == 0, "skill-standards itself passes --strict")

    print(f"\n{len(failures)} failure(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
