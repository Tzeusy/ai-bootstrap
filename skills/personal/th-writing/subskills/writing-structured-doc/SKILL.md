---
name: writing-structured-doc
description: Coauthor substantial reader-facing documents such as proposals, decision docs, RFCs, and design docs by gathering only missing context, drafting directly, refining surgically, and testing comprehension proportionally.
metadata:
  owner: tze
  authors:
    - Anthropic (upstream)
    - tze
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
---

# Writing Structured Documents

Coauthor a document that must work for readers beyond the current
conversation. Preserve the user's intent and voice while making audience,
decision, evidence, trade-offs, and requested action easy to recover.

## Provenance

This workflow is tuned from Anthropic's `doc-coauthoring` skill. It preserves
the durable context-to-draft-to-reader-test loop while removing assumptions
about a particular platform, fixed multi-turn ceremonies, and named tools.

## Establish the document contract

Determine the document type, audience, desired reader outcome, source material,
template, and constraints. Use context already supplied. If intent is clear,
state the inferred contract briefly and draft immediately; do not force a
workflow preamble or repeat answered questions.

Ask only for missing information that would materially change the document.
Batch tightly related gaps when that is faster for the user, and accept notes,
links, files, or shorthand answers. Never search private sources or external
systems without the access and authorization the task requires.

If the request is actually a codebase-doc correctness audit or project-spec
reconciliation, return to the router; this workflow owns writing, not technical
verification or governance.

## Draft and refine

1. Choose a structure suited to the reader and document type. Put the core
   decision, proposal, or approach before supporting detail; write summaries
   after the body when practical.
2. Create or edit the artifact using available workspace operations. Respect
   an existing template and local conventions. Do not invent unavailable
   integrations or require a particular document platform.
3. Draft at the smallest useful granularity: a complete short document, or the
   highest-uncertainty section first for a long document. Mark genuine unknowns
   explicitly instead of filling them with plausible prose.
4. Refine from concrete feedback with surgical edits. Preserve accepted
   sections and the author's vocabulary unless consistency or correctness
   requires a change.
5. Re-read the whole artifact for flow, duplication, contradictions, assumed
   context, unsupported claims, and whether every section serves the intended
   reader outcome.

Keep factual verification distinct from prose refinement. Cite supplied
evidence accurately; when new research is requested, use current authoritative
sources and label inference or uncertainty.

## Fresh-reader pass

Run one comprehension pass proportional to document risk:

- **Low risk** (short internal note, reversible decision): simulate a fresh
  reader from the document alone and check the intended action and open gaps.
- **Moderate risk** (proposal, design doc, cross-team decision): use a fresh
  context when available; ask realistic reader questions and check ambiguity,
  hidden assumptions, and contradictions.
- **High risk** (irreversible, public, legal, security, or safety impact): use
  an independent reviewer when available and require source verification or
  domain review appropriate to the risk. Do not imply that prose review proves
  substantive correctness.

Perform one pass, fix material gaps, and report what changed. Repeat only when
the first pass found consequential problems or the user asks; do not turn
reader testing into an automatic ceremony.

## Completion

Return the artifact or path, a concise change summary, unresolved decisions,
and verification limits. Recommend human review only where ownership, factual
risk, or impact warrants it.
