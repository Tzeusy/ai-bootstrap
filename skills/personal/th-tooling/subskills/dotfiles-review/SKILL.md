---
name: dotfiles-review
description: >
  Use to review the ~/.dotfiles tree — rc files, alias/function files under
  to_source/, home_rcs/, and .config tool dirs — for objective conflicts
  (duplicate or shadowing aliases, mutually exclusive settings, dead
  references) and best-practice recommendations, while never opening secret
  files. Triggers: "review my dotfiles", "clean up my zshrc", "are my
  aliases conflicting", "modernize my shell config".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
compatibility: Assumes the ~/.dotfiles layout (home_rcs/ symlinked to ~, to_source/ auto-sourced by .zshrc); findings verified with zsh.
---

# Dotfiles Review

Dotfiles accumulate cruft for years: aliases for uninstalled tools, two
definitions of the same alias in different files, exports that fight each
other, config for machines that no longer exist. This subskill reviews the
content; whether installed state matches the repo is
[../refresh-snapshots/SKILL.md](../refresh-snapshots/SKILL.md)'s job.

## Secrets boundary (hard stop — establish first)

Never read, quote, or diff: `to_source/machine_specific`,
`to_source/passwords`, `credentials/`, key/token files (`*.pem`, `*_rsa`,
`*.key`), or anything gitignored. When unsure, test before opening:

```bash
git -C ~/.dotfiles check-ignore -v <path>   # ignored => out of bounds
```

You may note that a secret file *exists* and is referenced; never its
contents. If a secret-looking value appears in a tracked file, that is a
P0 finding — report the file and line number only, never the value.

## Review scope

In review-priority order: `home_rcs/` (`.zshrc`, `.gitconfig`, `.vimrc`,
…), `to_source/*` (every file is auto-sourced by `.zshrc` — each one costs
shell-startup time), `.config/*` tool dirs, and `bootstrap.sh` only where
it installs the above.

## Objective checks (mechanical, run these)

```bash
cd ~/.dotfiles
# Duplicate alias/function definitions across sourced files
grep -hoE "^alias [A-Za-z0-9_-]+=" home_rcs/.zshrc to_source/* 2>/dev/null | sort | uniq -d
# Aliases shadowing real binaries or other aliases (review intent)
# References to binaries that are not installed
for b in $(grep -rhoE "^alias [^=]+='?([a-z0-9_-]+)" to_source/ | sed -E "s/^alias [^=]+='?//" | sort -u); do
  command -v "$b" >/dev/null || echo "missing binary: $b"
done
# Conflicting exports (same var set twice with different values)
grep -rhnE "^export [A-Z_]+=" home_rcs/.zshrc to_source/* | sort -t= -k1 | awk -F'[ =]' '{print $2}' | uniq -d
```

Treat hits as candidates, not verdicts — a later definition may deliberately
override an earlier one. Confirm load order (`.zshrc` sources `to_source/*`
in glob order) before calling something a conflict.

## Recommendations (judgment, present — don't apply unasked)

Style and tool choices are personal; frame these as suggestions with a
one-line rationale each: dead config for tools no longer installed,
deprecated option syntax, oh-my-zsh plugins that duplicate aliases defined
manually, slow startup work that could be lazy-loaded, files in `to_source/`
that belong in `machine_specific` (machine-coupled paths or hosts).

## Output contract

Two sections, every finding with `file:line` evidence:

1. **Objective conflicts** — duplicate/shadowed definitions, dead
   references, secret-in-tracked-file; each with a proposed minimal diff.
2. **Recommendations** — best-practice suggestions the user may decline.

After any applied change, verify the shell still loads cleanly:

```bash
zsh -ic exit && echo OK
```
