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
import fcntl
from contextlib import contextmanager
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



def delivery_branch(delivery: dict[str, Any]) -> str:
    """Return the accepted literal head; absence retains the strict anchor default."""
    return delivery.get("branch", f"agent/{delivery['anchor']}")


def validate_branch(branch: object, base_branch: str) -> None:
    """Validate a literal local branch name, never a ref expression or override.

    This is the branch-name subset of git-check-ref-format plus the package's
    protected-base and independent-review boundaries. No Git process is needed
    while validating tracker evidence.
    """
    if (
        not isinstance(branch, str)
        or not branch
        or branch in {"@", "HEAD", "main", "master", base_branch}
        or branch.startswith(("-", "refs/", "review/"))
        or ".." in branch
        or "@{" in branch
        or any(ord(char) <= 32 or ord(char) == 127 or char in "~^:?*[\\" for char in branch)
        or any(
            not part or part.startswith(".") or part.endswith((".", ".lock"))
            for part in branch.split("/")
        )
    ):
        raise ValueError("invalid-delivery-branch")


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
    validate_branch(delivery_branch(value), value["base_branch"])
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
        self.owner = owner
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


def blocking_targets(member: str, value: object) -> list[str]:
    """Accept nested bd-show and legacy edge rows, rejecting equivocal identity."""
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("invalid-dependency-collection")
    targets = []
    for dep in value:
        if not isinstance(dep, dict):
            raise ValueError("invalid-dependency-record")
        kinds = [dep[key] for key in ("dependency_type", "type") if key in dep]
        ids = [dep[key] for key in ("depends_on_id", "id") if key in dep]
        if (not kinds or any(not isinstance(kind, str) or not kind or kind.strip() != kind for kind in kinds)
            or len(set(kinds)) != 1 or not ids
            or any(not isinstance(target, str) or not ID.fullmatch(target) for target in ids)
            or len(set(ids)) != 1 or ("issue_id" in dep and dep["issue_id"] != member)):
            raise ValueError("invalid-or-contradictory-dependency")
        if kinds[0] == "blocks":
            targets.append(ids[0])
    return targets


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
        for target in blocking_targets(member, row.get("dependencies")):
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
    if not recovery and not rollback:
        reconciliation = journal.get("branch_reconciliation")
        if reconciliation is not None and (not isinstance(reconciliation, dict)
            or reconciliation.get("schema") != "beads-branch-reconciliation/v1"
            or reconciliation.get("phase") != "complete" or reconciliation.get("to") != delivery):
            raise ValueError("branch-reconciliation-incomplete-resume-first")
        current = metadata(client.show(delivery["anchor"])).get("delivery")
        if current not in (delivery, {**delivery, "state": "released"}):
            raise ValueError("journal-delivery-mismatch-reconcile-before-release")
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
    return {"state": "active", "anchor": delivery["anchor"], "members": delivery["members"], "branch": delivery_branch(delivery)}



@contextmanager
def journal_lock(path: Path):
    """Serialize journal consumers; coordinator repository custody is also required."""
    with path.with_suffix(path.suffix + ".lock").open("a") as stream:
        fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
        yield


def inspect_branch_binding(repo_root: str, worktree: str, delivery: dict[str, Any], pr: int, head: str) -> dict[str, Any]:
    """Read actual Git and current same-repository PR identity; never trust a receipt."""
    if type(pr) is not int or pr <= 0 or (not isinstance(head, str) or not re.fullmatch(r"[0-9a-f]{40}", head)):
        raise ValueError("invalid-reconciliation-pr-or-head")
    root, source = Path(repo_root).resolve(), Path(worktree).resolve()

    def read(argv: list[str], cwd: Path) -> str:
        environment = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        environment.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
        result = subprocess.run(argv, cwd=cwd, env=environment, capture_output=True, text=True, timeout=30, check=False)
        if result.returncode:
            raise RuntimeError("reconciliation-binding-read-failed")
        return result.stdout.strip()

    if read(["git", "rev-parse", "--show-toplevel"], root) != str(root):
        raise ValueError("reconciliation-repository-root-mismatch")
    if read(["git", "rev-parse", "--show-toplevel"], source) != str(source):
        raise ValueError("reconciliation-worktree-root-mismatch")
    common = read(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], root)
    if common != read(["git", "rev-parse", "--path-format=absolute", "--git-common-dir"], source):
        raise ValueError("reconciliation-foreign-worktree")
    if read(["git", "symbolic-ref", "--short", "HEAD"], source) != delivery_branch(delivery):
        raise ValueError("reconciliation-branch-mismatch")
    if read(["git", "rev-parse", "HEAD"], source) != head:
        raise ValueError("reconciliation-head-mismatch")
    if read(["git", "status", "--porcelain=v1", "--untracked-files=no"], source):
        raise ValueError("reconciliation-tracked-source-dirty")
    repo = read(["gh", "repo", "view", "--json", "nameWithOwner", "--jq", ".nameWithOwner"], root)
    if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", repo):
        raise ValueError("invalid-reconciliation-repository")
    data = json.loads(read(["gh", "pr", "view", str(pr), "--repo", repo, "--json",
        "number,state,headRefName,headRefOid,baseRefName,isCrossRepository,headRepository,headRepositoryOwner"], root))
    if not isinstance(data, dict) or type(data.get("number")) is not int or data["number"] != pr:
        raise ValueError("reconciliation-pr-mismatch")
    if (data.get("state") != "OPEN" or data.get("isCrossRepository") is not False
        or data.get("headRefName") != delivery_branch(delivery) or data.get("headRefOid") != head
        or data.get("baseRefName") != delivery["base_branch"]
        or not isinstance(data.get("headRepository"), dict)
        or data["headRepository"].get("name") != repo.split("/")[1]
        or not isinstance(data.get("headRepositoryOwner"), dict)
        or data["headRepositoryOwner"].get("login") != repo.split("/")[0]):
        raise ValueError("reconciliation-pr-binding-mismatch")
    return {"repo_root": str(root), "worktree": str(source), "common_dir": common,
            "repository": repo, "pr": pr, "head": head, "branch": delivery_branch(delivery),
            "base_branch": delivery["base_branch"]}


def reconcile_branch(client: Beads, journal: dict[str, Any], path: Path,
                     target: dict[str, Any], *, worktree: str, pr: int, head: str) -> dict[str, Any]:
    """One-time branch-only amendment of an ACTIVE package, with durable resume.

    Caller holds repository custody and journal_lock. No claim/release, status,
    member pointer, arbitrary identity amendment or caller-supplied binding proof.
    """
    target = validate_delivery(target)
    if (journal.get("schema") != "beads-delivery-journal/v1" or journal.get("state") != "active"
        or journal.get("repo_root") != client.repo_root):
        raise ValueError("reconciliation-requires-exact-active-journal")
    current_delivery = validate_delivery(journal["delivery"])
    saved = journal.get("branch_reconciliation")
    old = validate_delivery(saved["from"]) if isinstance(saved, dict) and "from" in saved else current_delivery
    if ("branch" in old or "branch" not in target or target != {**old, "branch": target["branch"]}
        or target.get("state", "active") != "active" or client.owner != old["owner"]
        or journal.get("attempted") != old["members"]
        or not isinstance(journal.get("before"), dict) or set(journal["before"]) != set(old["members"])):
        raise ValueError("reconciliation-identity-change-forbidden")
    if any(not isinstance(prior, dict) or set(prior) != {"status", "assignee", "metadata"}
           or prior.get("status") not in {"open", "in_progress", "blocked", "closed"}
           or prior.get("assignee") is not None and not isinstance(prior["assignee"], str)
           or not isinstance(prior.get("metadata"), dict) for prior in journal["before"].values()):
        raise ValueError("invalid-reconciliation-claim-history")
    binding = inspect_branch_binding(client.repo_root, worktree, target, pr, head)
    if saved is not None:
        if (not isinstance(saved, dict) or set(saved) != {"schema", "from", "to", "binding", "phase"}
            or saved.get("schema") != "beads-branch-reconciliation/v1" or saved.get("to") != target
            or saved.get("binding") != binding or saved.get("phase") not in {"prepared", "tracker-written", "complete"}
            or current_delivery != (target if saved["phase"] == "complete" else old)):
            raise ValueError("conflicting-branch-reconciliation")

    def rows_for(allowed: tuple[dict[str, Any], ...]) -> dict[str, dict[str, Any]]:
        rows = {member: client.show(member) for member in old["members"]}
        for member, row in rows.items():
            if (row.get("assignee") != old["owner"] or row.get("status") not in {"in_progress", "blocked", "closed"}
                or set(row.get("labels") or []) & HOLD_LABELS):
                raise ValueError("reconciliation-member-owner-state-or-hold-mismatch")
        anchor = rows[old["anchor"]]
        if (metadata(anchor).get("delivery") not in allowed
            or anchor.get("external_ref") != f"gh-pr:{pr}"):
            raise ValueError("reconciliation-anchor-delivery-or-pr-mismatch")
        package_index(list(rows.values()))
        return rows

    allowed = (old,) if saved is None else (old, target) if saved["phase"] == "prepared" else (target,)
    rows = rows_for(allowed)
    if saved is None:
        saved = {"schema": "beads-branch-reconciliation/v1", "from": old, "to": target,
                 "binding": binding, "phase": "prepared"}
        journal["branch_reconciliation"] = saved
        save_journal(path, journal)
    if saved["phase"] == "complete":
        return {"state": "active", "branch": target["branch"], "reconciliation": "complete", "resumed": True}
    # Re-read all claims and the current provider/Git binding after durable intent.
    rows = rows_for((old, target) if saved["phase"] == "prepared" else (target,))
    if inspect_branch_binding(client.repo_root, worktree, target, pr, head) != binding:
        raise ValueError("reconciliation-binding-changed")
    anchor = rows[old["anchor"]]
    if metadata(anchor)["delivery"] == old:
        client.call("update", old["anchor"], "--if-assignee", old["owner"],
                    "--if-status", anchor["status"], "--metadata", json.dumps({"delivery": target}, separators=(",", ":")), "--json")
    rows_for((target,))
    saved["phase"] = "tracker-written"
    save_journal(path, journal)
    if inspect_branch_binding(client.repo_root, worktree, target, pr, head) != binding:
        raise ValueError("reconciliation-binding-changed")
    rows_for((target,))
    journal["delivery"] = target
    saved["phase"] = "complete"
    save_journal(path, journal)
    return {"state": "active", "branch": target["branch"], "reconciliation": "complete", "resumed": False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("validate", "claim", "recover", "release", "reconcile-branch", "closure-plan"))
    parser.add_argument("--delivery-file", type=Path)
    parser.add_argument("--repo-root")
    parser.add_argument("--journal", type=Path)
    parser.add_argument("--results-file", type=Path)
    parser.add_argument("--worktree")
    parser.add_argument("--pr-number", type=int)
    parser.add_argument("--expected-head")
    parser.add_argument("--landed-main", action="store_true", help="Use only after independently confirming landing on main; never inferred from an integration branch merge.")
    args = parser.parse_args()
    try:
        if args.command in {"recover", "release", "reconcile-branch"}:
            if not args.repo_root or not args.journal:
                raise ValueError("repo-root-and-journal-required")
            with journal_lock(args.journal):
                journal = json.loads(args.journal.read_text(encoding="utf-8"))
                delivery = validate_delivery(journal["delivery"])
                client = Beads(args.repo_root, delivery["owner"])
                if args.command == "reconcile-branch":
                    if not args.delivery_file or not args.worktree or not args.pr_number or not args.expected_head:
                        raise ValueError("reconciliation-delivery-worktree-pr-head-required")
                    result = reconcile_branch(client, journal, args.journal, load_delivery(args.delivery_file),
                                              worktree=args.worktree, pr=args.pr_number, head=args.expected_head)
                else:
                    result = release_claims(client, journal, args.journal, recovery=args.command == "recover")
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
