---
name: th-writing
description: >
  Use for blog-post editorial review or publish hardening, and for
  collaboratively drafting structured documents such as proposals, decision
  docs, specs, and RFCs. Route to one hidden writing workflow. Do not use for
  codebase-documentation audits or project-governance/spec reconciliation.
metadata:
  owner: tze
  authors:
    - tze
    - Anthropic (upstream)
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
---

# TH Writing

Route writing work without loading every workflow. The three subskills under
`subskills/` are package-internal and discovered lazily; load one for an
ordinary task.

## Routing table

| Task intent | Subskill | Typical trigger |
|---|---|---|
| Judge a blog post's publication readiness: narrative, structure, scannability, tone, factual risk, and reader value. Return findings; do not silently rewrite. | [subskills/writing-editorial-review/SKILL.md](subskills/writing-editorial-review/SKILL.md) | "review my post", "is this ready to publish?", "critique this draft" |
| Make an existing blog post compile, render, and conform through safe mechanical edits: frontmatter, Markdown/MDX, structure, and assets. | [subskills/writing-publish-hardening/SKILL.md](subskills/writing-publish-hardening/SKILL.md) | "format this for the blog", "fix the frontmatter", "make this MDX build" |
| Coauthor a substantial structured document: proposal, decision document, RFC, design document, or similar reader-facing artifact. | [subskills/writing-structured-doc/SKILL.md](subskills/writing-structured-doc/SKILL.md) | "draft a proposal", "help write this RFC", "turn these notes into a decision doc" |

## Routing rules

- **Judgment vs. mutation**: review/readiness asks route to editorial review;
  explicit build/conformance edits route to publish hardening. A full publish
  pass runs those two workflows sequentially, preserving each boundary.
- **Blog vs. structured document**: posts and articles use the blog workflows;
  proposals, decisions, RFCs, and design documents use structured-doc.
- **Writing vs. engineering or governance**: audit documentation against code
  with `th-engineering`; reconcile project doctrine or normative specs with
  `th-projects`. Route here only when the artifact's writing is the work.
- **Ambiguous asks**: if "edit" could mean critique or file mutation, ask one
  narrow question before loading a subskill. If no row fits, continue without
  a subskill.

Example triggers: "review my blog post", "make this post publishable", "fix
this MDX frontmatter", "draft an RFC from these notes", "coauthor a proposal".
Non-trigger example: "audit whether our README matches the implementation".

The routing cases in [evals/routing-cases.json](evals/routing-cases.json) test
selection from this router alone; do not load subskill bodies to classify them.
