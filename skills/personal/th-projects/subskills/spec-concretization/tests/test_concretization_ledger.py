"""Seam tests for concretization-ledger.py: run the real CLI on a fixture repo."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / "scripts" / "concretization-ledger.py"
REPO = HERE / "fixtures" / "ledger-repo"
BEADS = REPO / "beads.json"


def run(*args, state_root, path=None):
    env = {**os.environ, "QUESTIONNAIRE_STATE_ROOT": str(state_root)}
    if path is not None:
        env["PATH"] = path
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                          text=True, env=env)


def ledger(tmp_path, repo=REPO, beads=BEADS):
    out = run(str(repo), "--beads-json", str(beads), "--json", state_root=tmp_path)
    assert out.returncode == 0, out.stderr
    return json.loads(out.stdout)


def test_ownership_comes_from_requirements_lines_and_normalizes_ids(tmp_path):
    rows = {(r["id"], r["change"]): r for r in ledger(tmp_path)["requirements"]}
    main_001 = rows[("REQ-core-config-001", None)]
    assert main_001["tested"] and main_001["owners"] == ["fx-1(closed)", "fx-9(open,epic)"]
    # underscore/upper-case form owns the same ID; pinned counts as live
    assert rows[("REQ-core-config-004", None)]["owners"] == ["fx-7(pinned)", "fx-8(open)"]
    # last spec-concretization note SHA is surfaced so re-runs can skip duplicate notes
    assert rows[("REQ-core-config-003", "add-reload")]["owners"] == ["fx-2(open,noted@abc1234)"]


def test_unsigned_delta_does_not_govern_and_archive_is_excluded(tmp_path):
    data = ledger(tmp_path)
    main_001 = next(r for r in data["requirements"] if r["id"] == "REQ-core-config-001" and not r["change"])
    assert "UNSIGNED" in main_001["governed_by"]
    assert not any(r["id"] == "REQ-core-config-005" for r in data["requirements"])
    changes = {c["change"]: c for c in data["active_changes"]}
    assert changes["add-reload"]["signed"] and changes["add-reload"]["tasks_done"] == 1
    assert changes["add-reload"]["beads"] == ["fx-12(open)"]
    assert not changes["tighten-load"]["signed"] and changes["tighten-load"]["tasks_total"] is None


def test_backlog_side_buckets_are_exclusive(tmp_path):
    data = ledger(tmp_path)
    first = lambda key: [line.split()[0] for line in data[key]]
    assert first("orphan_beads") == ["fx-3"]
    assert first("closeout_paths") == ["fx-10"]
    assert first("spec_linked_beads") == ["fx-4", "fx-12"]
    # REQ-...-0011 is not REQ-...-001; a foreign openspec tree is not this capability
    assert first("other_live_beads") == ["fx-5", "fx-11"]
    assert first("recently_closed_unmatched") == ["fx-6"]
    assert data["overlaps"] == ["REQ-core-config-004: fx-7(pinned) fx-8(open)"]


def test_summary_counts_distinct_in_scope_ids(tmp_path):
    s = ledger(tmp_path)["summary"]
    assert (s["requirements"], s["v1_mandatory"], s["v1_mandatory_untested"]) == (4, 3, 2)
    assert s["untested_main_no_live_owner"] == 0


def test_closed_only_owner_does_not_count_as_live(tmp_path):
    beads = [b for b in json.loads(BEADS.read_text()) if b["id"] not in ("fx-7", "fx-8")]
    dump = tmp_path / "beads.json"
    dump.write_text(json.dumps(beads + [{"id": "fx-99", "status": "closed",
                                         "design": "Requirements: REQ-core-config-004"}]))
    assert ledger(tmp_path, beads=dump)["summary"]["untested_main_no_live_owner"] == 1


def test_prior_state_and_decisions(tmp_path):
    packet = tmp_path / "ledger-repo-2026-10-01-spec-concretization"
    packet.mkdir()
    (packet / "packet.md").write_text(
        "| # | Decision ID | Priority | Decision state | Recommended direction |\n"
        "|---:|---|---:|---|---|\n"
        "| 1 | `concretize:adopt:core-config/cli:load--strict` | P2 | Agreed | Adopt |\n")
    prior = ledger(tmp_path)["prior"]
    assert prior["last_record"][0].startswith("Concretized: abc1234")
    assert prior["decisions"]["concretize:adopt:core-config/cli:load--strict"].startswith("Agreed")


def test_markdown_render_and_spec_only_mode(tmp_path):
    out = run(str(REPO), "--no-beads", state_root=tmp_path)
    assert out.returncode == 0, out.stderr
    assert "Beads: not loaded (--no-beads)" in out.stdout
    assert "REQ-core-config-004 v1-mandatory UNTESTED main" in out.stdout


def fake_bd(tmp_path, body):
    bindir = tmp_path / "bin"
    bindir.mkdir()
    script = bindir / "bd"
    script.write_text("#!/bin/sh\n" + body)
    script.chmod(0o755)
    return f"{bindir}{os.pathsep}{os.environ['PATH']}"


def test_empty_bd_output_fails_closed(tmp_path):
    repo = tmp_path / "repo"
    shutil.copytree(REPO, repo)
    body = f'case "$1" in where) echo "{repo}/.beads";; *) exit 0;; esac\n'
    out = run(str(repo), state_root=tmp_path, path=fake_bd(tmp_path, body))
    assert out.returncode == 2 and "refusing to treat the backlog as empty" in out.stderr


def test_foreign_database_fails_closed(tmp_path):
    body = 'case "$1" in where) echo "/somewhere/else/.beads";; *) echo "[]";; esac\n'
    out = run(str(REPO), state_root=tmp_path, path=fake_bd(tmp_path, body))
    assert out.returncode == 2 and "outside" in out.stderr


def test_malformed_beads_json_exits_2(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text('{"id": "not-a-list"}')
    out = run(str(REPO), "--beads-json", str(bad), state_root=tmp_path)
    assert out.returncode == 2 and "unexpected beads JSON shape" in out.stderr
    bad.write_text("not json")
    assert run(str(REPO), "--beads-json", str(bad), state_root=tmp_path).returncode == 2


def test_fails_closed_without_openspec(tmp_path):
    out = run(str(tmp_path), "--no-beads", state_root=tmp_path)
    assert out.returncode == 2 and "no openspec/" in out.stderr


def test_unsigned_added_requirements_are_out_of_scope(tmp_path):
    repo = tmp_path / "repo"
    shutil.copytree(REPO, repo)
    (repo / "openspec/changes/add-reload/proposal.md").write_text("Why: hot reload.\n")
    data = ledger(tmp_path, repo=repo)
    assert data["summary"]["v1_mandatory"] == 2 and data["summary"]["in_signed_changes"] == 0
    assert "(UNSIGNED)" in run(str(repo), "--no-beads", state_root=tmp_path).stdout
