#!/usr/bin/env python3
"""Exercise the user installer with fixture clients and isolated tool homes."""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SOURCE = Path(__file__).resolve().parents[1]


class HudInstallTest(unittest.TestCase):
    def test_user_scope_install_and_preservation(self):
        with tempfile.TemporaryDirectory(prefix="hud-install-") as temporary:
            base = Path(temporary)
            bootstrap = base / "ai bootstrap"
            scripts = bootstrap / "scripts"
            scripts.mkdir(parents=True)
            for name in ("install-tze-hud.sh", "link-ai-skills.sh", "sync-mcp.sh"):
                shutil.copyfile(SOURCE / "scripts" / name, scripts / name)
                (scripts / name).chmod(0o755)
            (bootstrap / "skills").mkdir()
            hud = base / "HUD main"
            hud.mkdir()
            subprocess.run(["git", "init", "-q", "-b", "main", str(hud)], check=True)
            adapter = hud / ".claude/skills/user-test/scripts/hud_mcp_stdio.py"
            adapter.parent.mkdir(parents=True)
            adapter.write_text("# fixture adapter; never launched\n")
            for name in ("th-hud-publish", "hud-projection"):
                skill = hud / ".claude/skills" / name
                skill.mkdir()
                (skill / "SKILL.md").write_text(
                    f"---\nname: {name}\ndescription: Fixture product skill.\n---\n\nBody.\n"
                )
            home = base / "home"
            home.mkdir()
            for tool in ("claude", "codex", "gemini"):
                (bootstrap / f".{tool}").mkdir()
                (home / f".{tool}").symlink_to(bootstrap / f".{tool}", target_is_directory=True)
            settings = home / ".gemini/settings.json"
            existing = {"theme": "fixture", "mcpServers": {"unrelated": {"command": "unchanged"}}}
            settings.write_text(json.dumps(existing))
            clients = base / "bin"
            clients.mkdir()
            stub = '''#!/usr/bin/env python3
import json,os,pathlib,sys
name=pathlib.Path(sys.argv[0]).name
home=pathlib.Path(os.environ["HOME"])
args=sys.argv[1:]
state=home/("stub-"+name+".json")
data=json.loads(state.read_text()) if state.exists() else {}
if args[:2]==["mcp","get"]:
    sys.exit(0 if args[2] in data else 1)
if args[:2]!=["mcp","add"]: sys.exit(9)
if os.environ.get("FAIL_CLIENT")==name: sys.exit(7)
server="tze-hud" if "tze-hud" in args else "remote"
data[server]={"args":args,"cwd":os.getcwd()}
state.write_text(json.dumps(data))
'''
            for tool in ("claude", "codex", "gemini"):
                (clients / tool).write_text(stub)
                (clients / tool).chmod(0o755)
            env = os.environ.copy()
            env.pop("TZE_HUD_REPO", None)
            env.pop("CODEX_HOME", None)
            env.update(HOME=str(home), PATH=str(clients) + os.pathsep + env["PATH"], TMPDIR=str(base))

            def run(script, *args, success=True):
                result = subprocess.run(
                    [str(scripts / script), *map(str, args)], cwd=base, env=env,
                    text=True, capture_output=True, timeout=30,
                )
                self.assertEqual(result.returncode == 0, success, result.stdout + result.stderr)
                return result

            # A worktree/development branch is not the accepted main source.
            subprocess.run(["git", "-C", str(hud), "checkout", "-q", "-b", "development"], check=True)
            run("install-tze-hud.sh", hud, success=False)
            self.assertFalse((bootstrap / ".tze-hud-repo").exists())
            self.assertEqual(json.loads(settings.read_text()), existing)
            subprocess.run(["git", "-C", str(hud), "checkout", "-q", "-B", "main"], check=True)

            # Unmanaged skill entries survive a failed install.
            collision = bootstrap / ".claude/skills/hud-projection"
            collision.mkdir(parents=True)
            (collision / "SKILL.md").write_text("owner content\n")
            run("install-tze-hud.sh", hud, success=False)
            self.assertEqual((collision / "SKILL.md").read_text(), "owner content\n")
            shutil.rmtree(collision)

            # CLI failure is observable; it must not be reported as "present".
            env["FAIL_CLIENT"] = "claude"
            result = run("install-tze-hud.sh", hud, success=False)
            self.assertNotIn("present claude", result.stdout)
            self.assertFalse((bootstrap / ".tze-hud-repo").exists())
            env.pop("FAIL_CLIENT")
            run("install-tze-hud.sh", hud)
            self.assertEqual((bootstrap / ".tze-hud-repo").read_text(), str(hud) + "\n")
            command = ["python3", "-u", str(adapter)]
            for tool in ("claude", "codex"):
                state = json.loads((home / f"stub-{tool}.json").read_text())["tze-hud"]
                args = state["args"]
                self.assertEqual(args[args.index("--") + 1:], command)
                if tool == "claude":
                    self.assertEqual(args[:7], ["mcp", "add", "--scope", "user", "--transport", "stdio", "tze-hud"])
                self.assertNotEqual(state["cwd"], str(bootstrap))
                self.assertNotEqual(state["cwd"], str(hud))
            configured = json.loads(settings.read_text())
            self.assertEqual(configured["mcpServers"]["tze-hud"], {"command": "python3", "args": command[1:]})
            self.assertEqual(configured["theme"], existing["theme"])
            self.assertEqual(configured["mcpServers"]["unrelated"], existing["mcpServers"]["unrelated"])
            for name in ("th-hud-publish", "hud-projection"):
                for target in (".claude/skills", ".gemini/skills", ".gemini/antigravity/skills"):
                    link = bootstrap / target / name
                    self.assertTrue(link.is_symlink())
                    self.assertEqual(link.resolve(), hud / ".claude/skills" / name)
                wrapper = bootstrap / ".codex/skills" / name
                self.assertFalse(wrapper.is_symlink())
                self.assertIn(str(hud / ".claude/skills" / name / "SKILL.md"), (wrapper / "SKILL.md").read_text())
                self.assertEqual([p.relative_to(wrapper).as_posix() for p in wrapper.rglob("SKILL.md")], ["SKILL.md"])

            # Re-running and ordinary catalog refresh keep the source and entries.
            before = {p: p.read_bytes() for p in (home / "stub-claude.json", home / "stub-codex.json", settings)}
            run("install-tze-hud.sh", hud)
            run("link-ai-skills.sh", bootstrap)
            for path, content in before.items():
                self.assertEqual(path.read_bytes(), content)
            manifest = json.loads(run("link-ai-skills.sh", "--catalog-manifest", bootstrap).stdout)
            self.assertEqual({s["ownership"] for s in manifest["skills"]}, {"external"})
            self.assertEqual({s["name"] for s in manifest["skills"]}, {"hud-projection", "th-hud-publish"})

            # The pre-existing HTTP manifest interface still registers per-client.
            remote = base / "remote.tsv"
            remote.write_text("remote\tfixture-remote\n")
            run("sync-mcp.sh", remote)
            self.assertEqual(json.loads(settings.read_text())["mcpServers"]["remote"], {"httpUrl": "fixture-remote"})
            self.assertEqual(json.loads((home / "stub-codex.json").read_text())["remote"]["args"], ["mcp", "add", "remote", "--url", "fixture-remote"])

            # Malformed Gemini settings fail without replacing owner content,
            # even if the earlier clients already registered the new entry.
            settings.write_text("{malformed owner settings")
            run("sync-mcp.sh", "--stdio", "new-entry", "python3", success=False)
            self.assertEqual(settings.read_text(), "{malformed owner settings")

            # Missing external source fails clearly on the next ordinary refresh.
            shutil.rmtree(hud)
            run("link-ai-skills.sh", bootstrap, success=False)


if __name__ == "__main__":
    unittest.main()
