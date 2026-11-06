#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///
"""Cohesive delivery membership, guarded claims and recovery; never closes beads.

A journal is written before each claim, outside tracked files. `recover` rolls
back only incomplete claim attempts, retaining pre-owned claims; `release`
relinquishes an active package explicitly and reopens unfinished work. Neither command deletes code or branches.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

SCHEMA = "beads-delivery/v1"
ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]*\Z")
HOLD_LABELS = {"no-dispatch", "needs-shaping", "owner-held", "human-gate", "held-for-owner", "scope:local-state"}


def validate_delivery(value: object) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema") != SCHEMA:
        raise ValueError("invalid-delivery-schema")
    for key in ("anchor", "owner", "outcome", "base_branch", "packet"):
        if not isinstance(value.get(key), str) or not value[key].strip():
            raise ValueError(f"invalid-delivery-{key}")
    members = value.get("members")
    if not isinstance(members, list) or not members or any(not isinstance(m, str) or not ID.fullmatch(m) for m in members):
        raise ValueError("invalid-delivery-members")
    if len(set(members)) != len(members) or value["anchor"] not in members:
        raise ValueError("duplicate-members-or-missing-anchor")
    if value.get("state", "active") not in {"active", "released"}:
        raise ValueError("invalid-delivery-state")
    return value


def load_delivery(path: str | Path) -> dict[str, Any]:
    return validate_delivery(json.loads(Path(path).read_text(encoding="utf-8")))


def metadata(row: dict[str, Any]) -> dict[str, Any]:
    value = row.get("metadata") or {}
    if isinstance(value, str):
        value = json.loads(value)
    if not isinstance(value, dict):
        raise ValueError("invalid-bead-metadata")
    return value


def package_index(rows: list[dict[str, Any]]) -> dict[str, str]:
    """Validate visible package records and map member IDs to their anchor.

    Callers may supply only live rows: missing historical members are allowed,
    but every visible pointer must resolve to a visible, active anchor.
    """
    if not isinstance(rows, list) or any(not isinstance(row, dict) or not isinstance(row.get("id"), str) for row in rows):
        raise ValueError("invalid-delivery-records")
    by_id = {row["id"]: row for row in rows}
    if len(by_id) != len(rows):
        raise ValueError("duplicate-delivery-records")
    index: dict[str, str] = {}
    for row in rows:
        raw = metadata(row).get("delivery")
        if raw is None:
            continue
        delivery = validate_delivery(raw)
        if delivery["anchor"] != row["id"]:
            raise ValueError("delivery-anchor-mismatch")
        if delivery.get("state", "active") == "released":
            continue
        for member in delivery["members"]:
            if member in index and index[member] != row["id"]:
                raise ValueError("overlapping-delivery-membership")
            index[member] = row["id"]
            visible = by_id.get(member)
            if visible is not None:
                if member != row["id"] and str(visible.get("external_ref") or "").startswith("gh-pr:"):
                    raise ValueError("noncanonical-member-pr-reference")
                pointer = metadata(visible).get("delivery_anchor")
                if pointer != row["id"] and not (member == row["id"] and pointer is None):
                    raise ValueError("missing-or-conflicting-delivery-pointer")
                if visible.get("status") != "closed" and visible.get("assignee") != delivery["owner"]:
                    raise ValueError("delivery-owner-mismatch")
    for row in rows:
        pointer = metadata(row).get("delivery_anchor")
        if pointer is not None and index.get(row["id"]) != pointer:
            raise ValueError("unresolved-delivery-pointer")
    return index


def validate_results(delivery: dict[str, Any], results: object) -> list[dict[str, str]]:
    if not isinstance(results, list):
        raise ValueError("member-results-must-be-array")
    found: set[str] = set()
    for result in results:
        if not isinstance(result, dict) or result.get("id") not in delivery["members"] or result["id"] in found:
            raise ValueError("invalid-or-duplicate-member-result")
        if result.get("status") not in {"satisfied", "partial", "blocked"}:
            raise ValueError("invalid-member-result-status")
        if not isinstance(result.get("evidence"), str) or not result["evidence"].strip():
            raise ValueError("missing-member-result-evidence")
        found.add(result["id"])
    if found != set(delivery["members"]):
        raise ValueError("member-results-do-not-cover-package")
    return results


def closure_plan(delivery: dict[str, Any], results: object, landed_main: bool) -> dict[str, Any]:
    """A recommendation only: merge is necessary, never sufficient for closure."""
    checked = validate_results(delivery, results)
    close = [r["id"] for r in checked if landed_main and r["status"] == "satisfied"]
    return {"close": close, "retain": [m for m in delivery["members"] if m not in close], "outcome": delivery["outcome"], "outcome_complete": False}


def content_verdict_reusable(record: dict[str, Any], inputs: dict[str, str]) -> bool:
    """Only content verdicts with complete, unchanged declared inputs qualify.

    The owner declares the relevant source/spec/tool/config inputs. Runtime
    observations never qualify through this content-only seam.
    """
    return bool(record.get("kind") == "content" and record.get("verdict") == "pass" and record.get("inputs") and record["inputs"] == inputs)


class Beads:
    def __init__(self, repo_root: str, owner: str):
        self.repo_root = str(Path(repo_root).resolve())
        self.prefix = ["bd", "-C", self.repo_root, "--actor", owner]

    def call(self, *args: str) -> Any:
        result = subprocess.run([*self.prefix, *args], capture_output=True, text=True, timeout=30, check=False)
        if result.returncode:
            raise RuntimeError(f"bd-{args[0]}-failed:{result.returncode}")
        return json.loads(result.stdout) if result.stdout.strip() else None

    def show(self, member: str) -> dict[str, Any]:
        value = self.call("show", member, "--json")
        row = value[0] if isinstance(value, list) and len(value) == 1 else value
        if not isinstance(row, dict) or row.get("id") != member:
            raise ValueError("invalid-bead-response")
        return row


def save_journal(path: Path, value: dict[str, Any], *, initial: bool = False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path if initial else path.with_suffix(path.suffix + ".tmp")
    with temp.open("x" if initial else "w", encoding="utf-8") as stream:
        json.dump(value, stream, separators=(",", ":"))
        stream.flush()
        os.fsync(stream.fileno())
    if not initial:
        os.replace(temp, path)
    directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(directory_fd)
    finally:
        os.close(directory_fd)


def check_ready(delivery: dict[str, Any], rows: dict[str, dict[str, Any]], client: Beads) -> None:
    members = set(delivery["members"])
    edges: dict[str, list[str]] = {member: [] for member in members}
    for member, row in rows.items():
        if row.get("status") not in {"open", "in_progress"}:
            raise ValueError(f"member-not-runnable:{member}")
        if row.get("assignee") not in {None, "", delivery["owner"]}:
            raise ValueError(f"foreign-member-owner:{member}")
        if set(row.get("labels") or []) & HOLD_LABELS:
            raise ValueError(f"member-held:{member}")
        meta = metadata(row)
        if meta.get("delivery_anchor") not in {None, delivery["anchor"]}:
            raise ValueError(f"member-already-packaged:{member}")
        previous = meta.get("delivery")
        if previous is not None and previous != delivery:
            previous = validate_delivery(previous)
            if member != delivery["anchor"] or previous.get("state", "active") != "released":
                raise ValueError(f"conflicting-delivery:{member}")
        if member != delivery["anchor"] and str(row.get("external_ref") or "").startswith("gh-pr:"):
            raise ValueError(f"member-has-external-reference:{member}")
        edges[member] = []
        for dep in row.get("dependencies") or []:
            if dep.get("type") != "blocks" or dep.get("issue_id", member) != member:
                continue
            target = dep.get("depends_on_id") or dep.get("id")
            if not isinstance(target, str) or not ID.fullmatch(target):
                raise ValueError("invalid-blocking-dependency")
            if target in members:
                edges[member].append(target)
            elif client.show(target).get("status") != "closed":
                raise ValueError(f"external-blocker:{member}:{target}")
    visiting: set[str] = set()
    done: set[str] = set()

    def walk(member: str) -> None:
        if member in visiting:
            raise ValueError("cyclic-package-dependencies")
        if member in done:
            return
        visiting.add(member)
        for target in edges[member]:
            walk(target)
        visiting.remove(member)
        done.add(member)
    for member in members:
        walk(member)


def release_claims(client: Beads, journal: dict[str, Any], path: Path, *, recovery: bool, rollback: bool = False) -> dict[str, Any]:
    delivery = validate_delivery(journal["delivery"])
    if journal.get("repo_root") != client.repo_root:
        raise ValueError("journal-repository-mismatch")
    if journal.get("state") == "released":
        return {"state": "released", "released": [], "failures": [], "work_preserved": True}
    if recovery and journal.get("state") not in {"claiming", "recovery-incomplete"}:
        raise ValueError("recover-requires-incomplete-claim-attempt-use-release-for-active-package")
    failed: list[str] = []
    released: list[str] = []
    foreign: list[dict[str, str]] = []
    for member in reversed(journal["attempted"]):
        prior = journal["before"][member]
        try:
            current = client.show(member)
            if current.get("assignee") != delivery["owner"]:
                if current.get("assignee") and current.get("assignee") != prior.get("assignee"):
                    foreign.append({"id": member, "assignee": current["assignee"]})
                    if not rollback:
                        failed.append(member)
                continue
            if metadata(current).get("delivery_anchor") not in {None, delivery["anchor"]}:
                raise ValueError("member-now-belongs-to-another-package")
            assignee = (prior.get("assignee") or "") if recovery else ""
            update = ["update", member, "--if-assignee", delivery["owner"], "--assignee", assignee, "--json"]
            if recovery:
                update += ["--status", prior["status"]]
            elif current.get("status") == "in_progress":
                update += ["--if-status", "in_progress", "--status", "open"]
            restore_metadata: dict[str, Any] = {}
            unset_metadata: list[str] = []
            for key in ("delivery_anchor", "delivery"):
                old = metadata(prior).get(key) if recovery else None
                if not recovery and member == delivery["anchor"] and key == "delivery":
                    old = {**delivery, "state": "released"}
                if old is None:
                    unset_metadata += ["--unset-metadata", key]
                else:
                    restore_metadata[key] = old
            # Native bd rejects combining typed --metadata with key deletions.
            # Keep the claim through both metadata operations; relinquish it last.
            metadata_update = ["update", member, "--if-assignee", delivery["owner"], "--json"]
            if unset_metadata:
                client.call(*metadata_update, *unset_metadata)
            if restore_metadata:
                client.call(*metadata_update, "--metadata", json.dumps(restore_metadata, separators=(",", ":")))
            client.call(*update)
            released.append(member)
        except (RuntimeError, ValueError, subprocess.TimeoutExpired):
            failed.append(member)
    journal["state"] = ("recovery-incomplete" if recovery else "release-incomplete") if failed else "released"
    journal["release_failures"] = failed
    journal["foreign_claims"] = foreign
    save_journal(path, journal)
    return {"state": journal["state"], "released": released, "failures": failed, "foreign_claims": foreign, "work_preserved": True}


def claim_delivery(client: Beads, delivery: dict[str, Any], path: Path) -> dict[str, Any]:
    if path.exists():
        raise ValueError("journal-already-exists-use-recover-or-a-new-journal")
    rows = {member: client.show(member) for member in delivery["members"]}
    check_ready(delivery, rows, client)
    journal = {"schema": "beads-delivery-journal/v1", "repo_root": client.repo_root, "delivery": delivery, "before": {m: {"status": row["status"], "assignee": row.get("assignee"), "metadata": {k: v for k, v in metadata(row).items() if k in {"delivery", "delivery_anchor"}}} for m, row in rows.items()}, "attempted": [], "state": "claiming"}
    save_journal(path, journal, initial=True)
    try:
        for member in delivery["members"]:
            journal["attempted"].append(member)
            save_journal(path, journal)
            client.call("update", member, "--claim", "--json")
            # Recheck status and blockers after the atomic ownership operation.
            check_ready(delivery, {member: client.show(member)}, client)
        for member in delivery["members"]:
            package_metadata: dict[str, Any] = {"delivery_anchor": delivery["anchor"]}
            if member == delivery["anchor"]:
                package_metadata["delivery"] = delivery
            client.call("update", member, "--if-assignee", delivery["owner"], "--metadata", json.dumps(package_metadata, separators=(",", ":")), "--json")
        package_index([client.show(member) for member in delivery["members"]])
    except (RuntimeError, ValueError, subprocess.TimeoutExpired):
        release_claims(client, journal, path, recovery=True, rollback=True)
        raise
    journal["state"] = "active"
    save_journal(path, journal)
    return {"state": "active", "anchor": delivery["anchor"], "members": delivery["members"], "branch": f"agent/{delivery['anchor']}"}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "claim", "recover", "release", "closure-plan"))
    parser.add_argument("--delivery-file", type=Path)
    parser.add_argument("--repo-root")
    parser.add_argument("--journal", type=Path)
    parser.add_argument("--results-file", type=Path)
    parser.add_argument("--landed-main", action="store_true", help="Use only after independently confirming landing on main; never inferred from an integration branch merge.")
    args = parser.parse_args()
    try:
        if args.command in {"recover", "release"}:
            if not args.repo_root or not args.journal:
                raise ValueError("repo-root-and-journal-required")
            journal = json.loads(args.journal.read_text(encoding="utf-8"))
            delivery = validate_delivery(journal["delivery"])
            result = release_claims(Beads(args.repo_root, delivery["owner"]), journal, args.journal, recovery=args.command == "recover")
        else:
            if not args.delivery_file:
                raise ValueError("delivery-file-required")
            delivery = load_delivery(args.delivery_file)
            if args.command == "validate":
                result = delivery
            elif args.command == "closure-plan":
                if not args.results_file:
                    raise ValueError("results-file-required")
                result = closure_plan(delivery, json.loads(args.results_file.read_text(encoding="utf-8")), args.landed_main)
            else:
                if not args.repo_root or not args.journal:
                    raise ValueError("repo-root-and-journal-required")
                result = claim_delivery(Beads(args.repo_root, delivery["owner"]), delivery, args.journal)
        print(json.dumps(result, separators=(",", ":")))
        return 1 if result.get("failures") else 0
    except (OSError, ValueError, RuntimeError, KeyError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({"status": "blocked", "reason": str(exc)}, separators=(",", ":")))
        return 1


if __name__ == "__main__":
    sys.exit(main())
