# RFC 0001 Review - Round 1

**Reviewer:** Independent review pass
**Date:** 2026-04-08

## Scope

- Checked doctrine, topology, RFC, and OpenSpec alignment for the initial project-shape bootstrap.
- Focused on source-of-truth accuracy, mirrored-skill semantics, and local-only-state boundaries.

## Review Criteria

- Does the RFC match the live repository and the top-level README?
- Are the proposed contracts strong enough to survive future repo changes?
- Are any claims overstated relative to current evidence?

## Findings

- [§3.1, §Integration] The first draft overstated `agents/` as a co-equal canonical layer even though the repo README is skills-first and treats `agents/` as legacy/reference material.
- [§3.2, §3.3] The first draft omitted the in-repo tool skill mirror surfaces and the flattened-name mirroring rule.
- [§3.4] The first draft treated all machine-specific settings as unversioned, but the repo keeps some non-secret baseline defaults in tracked config files.
- [Header] `Accepted` overstated process maturity before any review artifact existed.

## Author Response

- Updated doctrine, topology, RFC, and OpenSpec docs to make `skills/` the primary shared workflow layer and `agents/` a secondary reference corpus.
- Added the mirror-surface and flattened-name rules to RFC 0001 and the topology docs.
- Narrowed the local-only-state rule to secrets, runtime IDs, caches, logs, session artifacts, and per-machine overrides, while allowing versioned non-secret baseline defaults.
- Downgraded RFC 0001 to `Draft` pending future human ratification.

## Unresolved Risks

- Human ratification criteria were not yet codified in the first draft.
- Provenance rules for upstream-derived non-`personal/` skills still needed stronger contract language.

## Next Decision

- Either ratify RFC 0001 after a human confirms the updated draft, or continue iterating until the remaining review findings are resolved and then re-review.
