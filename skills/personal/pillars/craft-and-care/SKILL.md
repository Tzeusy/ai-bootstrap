---
name: craft-and-care
description: >
  MANDATORY for non-trivial changes inside the ai-bootstrap repository. Load
  the repo's execution-quality standards before changing shared skills, tool
  facades, mirrors, generated assets, docs, or tracked config — and before
  claiming any such change is done. Defines verification evidence, review
  obligations, provenance and secret-handling discipline. Only applies inside
  ai-bootstrap; routes to about/craft-and-care/ rather than restating it.
---

# ai-bootstrap Engineering Standards — Craft and Care

`about/craft-and-care/` defines who we are when we change the ai-bootstrap
repository: explicit about source of truth, disciplined about verification,
skeptical of silent divergence, careful with local-only state. This skill is a
routing index — read the canonical files; do not rely on summaries of them.

**Consult before:**
- Any non-trivial change to shared skills, facades, mirrors, or structure
- Reviewing a change or preparing one for review
- Adding generated/vendored assets or updating upstream-derived content
- Deciding whether a change is actually done

**Start with `engineering-bar.md`, then load only what the change needs.**

## Document Index

| File | Read when... | Key content |
|------|-------------|-------------|
| `about/craft-and-care/README.md` | Orienting to the pillar | Scope, reading order, relationship to other pillars |
| `about/craft-and-care/engineering-bar.md` | Any non-trivial change | Definition of done, default biases, repo-specific standards |
| `about/craft-and-care/testing-and-verification.md` | Planning or judging evidence | Evidence-scales-with-risk table, required posture, repo-specific checks |
| `about/craft-and-care/interfaces-and-dependencies.md` | Path contracts, mirrors, submodules, forks | Source-of-truth boundaries, interface and dependency hygiene |
| `about/craft-and-care/review-and-documentation.md` | Review or handoff | Author obligations, reviewer blocking findings, documentation discipline |
| `about/craft-and-care/security-and-secrets.md` | Tracked config or anything credential-adjacent | Never-commit list, local-vs-portable standards |

## Quick Reference

| Need | Go to |
|------|-------|
| Why these standards exist | `about/heart-and-soul/` |
| The structural contract being protected | `about/legends-and-lore/` (RFC 0001) |
| The requirements compliance is measured against | `openspec/` |
| Where the affected layers live | `about/lay-and-land/` |
