---
name: dependency-hygiene
description: >
  Use when auditing or designing module boundaries and dependency chains — dependency
  direction, layering, cycles, public surface area, and third-party dependency
  admission or upgrades — in a codebase, package, or proposed change.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-06-12"
---

# Dependency Hygiene

Architecture is mostly the shape of the dependency graph. This subskill keeps
that graph legible: dependencies point one way, modules expose less than they
contain, every third-party package pays rent.

## Use This Skill When

- Auditing a codebase's import/module structure ("untangle these dependencies")
- A change adds an import that feels like it points the wrong way
- Deciding whether to admit a new third-party dependency or upgrade one
- Carving a module boundary: what is public, what is internal
- Cycles, god-modules, or "everything imports utils" complaints

## Do Not Use This Skill For

- Within-function clarity — [code-readability](../code-readability/SKILL.md)
- Retired-interface leftovers — [cruft-cleanup](../cruft-cleanup/SKILL.md)
- Repo-wide topology documentation (lay-and-land pillar) — `/th-projects`

## Core Rule

**Dependencies point from less stable to more stable, never back.**
Policy depends on mechanism, callers depend on interfaces, leaves depend on
core. Any edge pointing the other way — and any cycle, which is both
directions at once — is a finding regardless of whether the code currently
works.

## The Bar

Reviewable expectations — cite the one violated, with module/import evidence:

1. **One direction per layer boundary** — Name the layers the project implies
   (e.g. domain ← application ← interface/infra); verify every import
   crosses boundaries in the sanctioned direction. Invert upward imports
   via an interface owned by the lower layer, never wave them through.
2. **No cycles, at any granularity** — Module- or package-level cycles
   make units untestable in isolation and changes non-local. Break them by
   extracting the shared piece downward or inverting one edge; never by
   deferring imports inside functions to hide the cycle from tooling.
3. **Public surface is deliberate and minimal** — A module exports what its
   contract promises, not whatever happens to be defined. Reaching into
   another module's internals (deep imports, private-by-convention access)
   couples to accidents. Shrinking surface beats documenting it.
4. **No god-modules** — A `utils`/`common`/`helpers` that everything imports
   becomes a cycle hub and change magnet. Split by domain; a helper used by
   one consumer moves to that consumer.
5. **Third-party dependencies pay rent** — Admitting a package is an
   ownership decision: you adopt its security surface, upgrade cadence,
   transitive tree. Before adding one, state what it saves over ~50 lines of
   owned code, check maintenance health, prefer the standard library.
   Wrap volatile or heavy dependencies behind an owned interface at the
   boundary so they stay replaceable; don't wrap stable, idiomatic ones.
   For seam placement by dependency category, the deletion test, and the
   test strategy per category, read
   [`references/seams-and-dependencies.md`](./references/seams-and-dependencies.md).
6. **Versions are pinned, upgrades are deliberate** — Commit lockfiles;
   make each upgrade its own reviewed change with the changelog read,
   not a side effect of unrelated work. Record new dependencies
   wherever the host project documents them (for example, the dotfiles repo
   that ships this skill uses a `DEPENDENCIES.md`).
7. **Test/dev dependencies stay out of production chains** — Fixtures,
   fakes, and tooling must not be importable from shipped code paths.

## Workflow

1. Map before judging: extract the actual import graph (language tooling, or
   `rg`/`grep` over import statements) for the scope under review. For audits,
   render the module graph — `../excalidraw-diagram/SKILL.md` if available,
   otherwise Mermaid — so direction violations are visible, not asserted.
2. Establish intended direction: from the project's stated layering
   (lay-and-land docs, README) or, absent that, from stability — what changes
   most often must depend on what changes least.
3. Walk the edges: flag wrong-direction imports (1), cycles (2), deep
   imports (3), god-module fan-in (4). For each, propose the concrete
   inversion or extraction, smallest first. Judge suspect wrappers and
   layers with the deletion test
   ([`references/seams-and-dependencies.md`](./references/seams-and-dependencies.md)).
4. For each third-party package in scope, apply the rent test (5); check
   pinning/recording (6) and test/prod separation (7).
5. Apply small in-scope fixes (move a helper, narrow an export, pin a
   version) directly; structural inversions get a sequenced proposal with
   the cycle-breaking step first.

## Trigger Sanity Check

- Should trigger: "core imports the HTTP layer and I can't test it alone — untangle this."
- Should trigger: "should we pull in this package or write the ~40 lines ourselves?"
- Should trigger: "everything imports `utils` and every change touches it — is that fine?"
- Should not trigger: "Rename these variables" or "update the lockfile after CI told us to."
