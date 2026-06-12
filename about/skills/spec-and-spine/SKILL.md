---
name: spec-and-spine
description: >
  Ground work in ai-bootstrap's normative OpenSpec requirements when working in
  the ai-bootstrap repository. Use before structural changes, when auditing the
  repo for shape drift, when asked "does the repo still match its spec", or
  when adding requirements or change records under openspec/. Only applies
  inside ai-bootstrap; routes to openspec/ rather than restating it.
---

# ai-bootstrap Capability Specs — Spec and Spine

`openspec/` is the normative requirements layer of the ai-bootstrap
repository: what MUST remain true about its structure, recorded as testable
WHEN/THEN scenarios. This skill is a routing index — read the canonical files;
do not rely on summaries of them.

## Layout

| Path | Read when... | Key content |
|------|-------------|-------------|
| `openspec/config.yaml` | Creating a new change record | Project name, default change prefix |
| `openspec/changes/bootstrap-project-shape/proposal.md` | Understanding why the shape exists | Motivation, impact, non-goals |
| `openspec/changes/bootstrap-project-shape/design.md` | Reviewing the bootstrap's design reasoning | Design notes for the shape bootstrap |
| `openspec/changes/bootstrap-project-shape/tasks.md` | Checking what remains undecided | Task list incl. open RFC-ratification and archival decisions |
| `openspec/changes/bootstrap-project-shape/specs/repository-shape/spec.md` | Any structural change or audit | The repository-shape requirements with WHEN/THEN scenarios and doctrine/RFC source traceability |

## Domain Lookup

| Domain | Spec | Sources |
|--------|------|---------|
| Repository shape | `openspec/changes/bootstrap-project-shape/specs/repository-shape/spec.md` | Doctrine rules 1–7; RFC 0001 |

## Grounding Workflow

1. Identify which requirements the planned work touches; read only those.
2. If no requirement covers the behavior, write or amend the spec first.
3. Treat WHEN/THEN scenarios as acceptance criteria for structural changes.
4. After implementing, re-check the live repo against the affected scenarios.

## Quick Reference

| Need | Go to |
|------|-------|
| Philosophical grounding for a requirement | `about/heart-and-soul/` |
| The design contract a requirement operationalizes | `about/legends-and-lore/` |
| Where a requirement is physically embodied | `about/lay-and-land/` |
| Evidence standards for claiming compliance | `about/craft-and-care/` |
