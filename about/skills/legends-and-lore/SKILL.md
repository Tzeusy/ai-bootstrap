---
name: legends-and-lore
description: >
  Load ai-bootstrap's design contracts (RFCs and review records) when working
  in the ai-bootstrap repository on repository shape, distribution, mirroring,
  or source-of-truth questions. Use before changing where shared assets live,
  how tool facades diverge, or how skills are mirrored into tool homes, and
  when checking whether a contract is Draft or Accepted. Only applies inside
  ai-bootstrap; routes to about/legends-and-lore/ rather than restating it.
---

# ai-bootstrap Design Contracts — Legends and Lore

`about/legends-and-lore/` holds the repository's design contracts: numbered
RFCs plus the review rounds that justify their status. This skill is a routing
index — read the canonical files; do not rely on summaries of them.

**Consult before:**
- Changing repository layers, mirror surfaces, or install/distribution flow
- Adding a second copy of shared content anywhere
- Changing an RFC's status (status changes must cite review rounds)

## RFC Index

| RFC | File | Read when... | Key content |
|-----|------|-------------|-------------|
| 0001 | `about/legends-and-lore/rfcs/0001-repository-shape-and-distribution.md` | Any structural, mirroring, or provenance change | Repository layers, source-of-truth rules, distribution model, local-only state, governance lifecycle. **Status: Draft** pending human ratification |

## Review Records

| File | Read when... |
|------|-------------|
| `about/legends-and-lore/reviews/0001/round-1.md` | Checking what RFC 0001's review examined, what was fixed, and what risks remain unresolved |

## Lifecycle Rules

RFC statuses are `Draft` → `Accepted` → `Superseded`. Every status change must
cite the review round(s) and rationale; see RFC 0001 §Governance and Lifecycle
for the authoritative definitions.

## Quick Reference

| Need | Go to |
|------|-------|
| Why these contracts exist | `about/heart-and-soul/` |
| Testable requirements derived from the contracts | `openspec/` |
| Where the contracted layers physically live | `about/lay-and-land/` |
| The execution-quality bar for changing contracts | `about/craft-and-care/` |
