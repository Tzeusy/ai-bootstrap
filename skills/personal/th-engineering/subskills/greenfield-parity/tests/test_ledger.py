"""Seam tests for ledger.sh: run the real script against a fake bd and real questionnaire state."""

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
LEDGER = HERE.parent / "scripts" / "ledger.sh"
Q_SCRIPTS = HERE.parents[3] / "th-projects" / "subskills" / "user-questionnaire" / "scripts"
sys.path.insert(0, str(Q_SCRIPTS))
import questionnaire_web  # noqa: E402

# Honors --limit like bd: default 50, 0 = unlimited. 60 open beads, 3 closed.
FAKE_BD = r'''#!/usr/bin/env python3
import json, sys
a = sys.argv[1:]
if a[0] == "search":
    sys.exit(0)
limit = int(a[a.index("--limit") + 1]) if "--limit" in a else 50
if "--status" in a:
    rows = [{"id": f"c-{i}", "status": "closed", "closed_at": f"2026-11-0{i}", "title": f"done {i}"}
            for i in (3, 2, 1)]
else:
    rows = [{"id": f"o-{i}", "status": "open", "title": f"open {i}"} for i in range(60)]
print(json.dumps(rows[:limit] if limit else rows))
'''


def run_ledger(tmp_path, repo, qroot, *args):
    bindir = tmp_path / "bin"
    bindir.mkdir(exist_ok=True)
    bd = bindir / "bd"
    bd.write_text(FAKE_BD)
    bd.chmod(0o755)
    env = {**os.environ, "PATH": f"{bindir}{os.pathsep}{os.environ['PATH']}",
           "QUESTIONNAIRE_STATE_ROOT": str(qroot)}
    out = subprocess.run(["bash", str(LEDGER), str(repo), *args], capture_output=True, text=True, env=env)
    assert out.returncode == 0, out.stderr
    return out.stdout


def test_lists_every_open_bead_and_newest_closed(tmp_path):
    repo = tmp_path / "proj"
    repo.mkdir()
    out = run_ledger(tmp_path, repo, tmp_path / "q", "2")
    open_section = out.split("## Open / in-progress")[1].split("##")[0]
    assert len(open_section.strip().splitlines()) == 60
    closed = out.split("## Recently closed (last 2)")[1].split("##")[0].split()
    assert closed[0] == "c-3" and "c-1" not in closed


def test_reports_answers_from_questionnaire_state_dir(tmp_path, monkeypatch):
    repo, qroot = tmp_path / "proj", tmp_path / "q"
    repo.mkdir()
    answered = qroot / "proj-2026-11-09-greenfield" / "packet.md"
    pending = qroot / "proj-2026-11-01-greenfield" / "packet.md"
    for p in (answered, pending):
        p.parent.mkdir(parents=True)
        p.write_text("# packet\n")
    monkeypatch.setenv("QUESTIONNAIRE_STATE_ROOT", str(qroot))
    state = questionnaire_web.state_dir_for(answered)
    state.mkdir(parents=True)
    (state / "answers.json").write_text(json.dumps(
        {"completed_at": "2026-11-09T10:00:00Z", "apply_now": True, "items": {"a": {}, "b": {}}}))

    out = run_ledger(tmp_path, repo, qroot).split("## Prior owner questionnaires")[1]
    assert "packet.md: completed: 2026-11-09T10:00:00Z apply_now: true answered: 2" in out
    assert "packet.md: no answers recorded" in out
    assert out.count("proj-2026-11-09-greenfield") == 1  # each packet dir listed once
