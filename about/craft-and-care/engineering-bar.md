# Engineering Bar

This repository mostly changes documentation, prompt assets, skills, scripts,
and thin tool adapters. "Done" therefore means the source of truth is clearer
and safer after the change, not merely that a file was edited.

## Definition of Done

A non-trivial change is not done until:

- the authoritative layer is updated first (`skills/`, `about/`, `openspec/`,
  or a tool facade when the change is truly tool-specific);
- any required mirror or adapter updates are reconciled, with the source of
  truth still obvious;
- no dead same-repo compatibility path, duplicate prompt copy, or silent
  fallback is left behind without a real external consumer;
- upstream-derived content keeps visible provenance and intentional forks are
  documented;
- generated or vendored outputs still have a checked-in regeneration path;
- docs, specs, RFCs, and standards that changed in meaning are updated in the
  same change; and
- verification evidence matches the risk of the change.

## Default Biases

1. Prefer cleanup over same-repo compatibility cruft. If a rename, move, or
   refactor can be completed atomically inside this repo, finish it instead of
   preserving stale wrappers and duplicate prompt paths.
2. Prefer readability and simplicity over cleverness. This repo is a knowledge
   distribution system; surprising indirection makes both humans and agents
   worse at using it.
3. Prefer explicitness over hidden magic. If two files intentionally diverge,
   state why. If a path is a mirror, say so. If a file is generated, point to
   the regeneration path.
4. Prefer durable fixes over expedient patches. Do not paper over shape drift
   with one-off notes when the actual contract, README, spec, or skill index
   can be corrected directly.
5. Prefer fail-fast structure over quiet ambiguity. If a workflow depends on a
   specific canonical path, naming convention, or ignored-local-state boundary,
   encode that expectation clearly.
6. Prefer same-change documentation updates. Structural changes that are not
   reflected in doctrine, contracts, specs, or local skill routes are
   incomplete changes.

## Repo-Specific Standards

- Edit canonical shared content before touching tool-local mirrors or
  entrypoints.
- Keep in-repo shape navigation (`CLAUDE.md`/`AGENTS.md` routes and the pillar
  READMEs) pointing at canonical docs, never growing into a second authored
  documentation system.
- Keep flattened mirrored skill names understandable from the source tree; do
  not hide provenance behind install-time names alone.
- Treat checked-in baseline config as portable defaults only. Machine-private
  settings, runtime traces, and credentials remain local.
