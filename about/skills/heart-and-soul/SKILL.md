---
name: heart-and-soul
description: >
  Load ai-bootstrap's doctrine before making structural or placement decisions
  in the ai-bootstrap repository (the portable AI-assistant config and skills
  repo). Use when deciding where an artifact belongs, whether content is shared
  or tool-specific, how provenance must be preserved, what the repo is
  optimizing for, or what it refuses to become. Only applies inside
  ai-bootstrap; routes to about/heart-and-soul/ rather than restating it.
---

# ai-bootstrap Doctrine — Heart and Soul

`about/heart-and-soul/` is the doctrine layer of the ai-bootstrap repository.
It defines what the repo is, what it is not, and which boundaries are
constitutional. This skill is a routing index — read the canonical files; do
not rely on summaries of them.

**Consult before:**
- Deciding where a new skill, prompt, config, or doc belongs
- Introducing tool-specific copies of shared content
- Changing provenance, mirroring, or local-only-state boundaries
- Proposing scope changes to what the repository covers

## Document Index

| File | Read when... | Key content |
|------|-------------|-------------|
| `about/heart-and-soul/vision.md` | Any placement or scope question | Thesis, anti-thesis, the seven numbered non-negotiable rules, success criteria |
| `about/heart-and-soul/v1.md` | Scoping work; judging whether something is deferred | What v1 ships, deliberately defers, platform targets |
| `about/heart-and-soul/development.md` | Contributing or reviewing a change | Contribution rules, review questions, anti-patterns |
| `about/heart-and-soul/README.md` | Orienting to the pillar | Reading order |

The seven non-negotiable rules live in `vision.md` — they are the doctrine of
record. Do not quote them from memory; read them.

## Quick Reference

| Need | Go to |
|------|-------|
| How shape decisions are made durable (RFCs) | `about/legends-and-lore/` |
| What must remain true (normative requirements) | `openspec/` |
| Where layers, mirrors, and install targets live | `about/lay-and-land/` |
| How changes must be carried out well | `about/craft-and-care/` |
