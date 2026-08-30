---
name: writing-publish-hardening
description: Harden an existing blog post for build and publication through safe mechanical edits to frontmatter, Markdown or MDX, structure, links, and assets while preserving voice and meaning.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
---

# Writing Publish Hardening

Make an existing post compile, render, and conform to its repository's
publishing conventions. This workflow authorizes safe mechanical edits, not
editorial rewrites, claim changes, section deletion, or subjective reordering.
Report anything requiring judgment instead of changing it.

## Resolve conventions and target

- Use the supplied path or inspect likely post locations. Ask one narrow
  question only if multiple plausible targets remain.
- Read the site's schema, neighboring posts, build configuration, and asset
  conventions before normalizing anything. Repository rules override generic
  defaults.
- Detect whether the post is standalone or a bundle with colocated assets.

## Harden the post

1. Parse frontmatter and validate required fields, types, date formats, and
   project-specific naming. Repair syntax and obvious type mistakes; flag
   uncertain content instead of inventing it.
2. Check heading hierarchy, code fences, inline code, emphasis, links, tables,
   and HTML/JSX balance. Apply only unambiguous syntax repairs.
3. For MDX, inspect prose outside code spans and fences for characters or tags
   that the project's compiler will interpret. Prefer semantic inline code to
   blind escaping, and preserve intended components.
4. Verify referenced assets exist, paths follow local conventions, and images
   have useful alt text. Rename generic asset filenames only when meaning and
   every reference are clear; otherwise report them.
5. Find placeholders and unfinished markers. Keep them in place and report
   them as publish blockers; do not convert or delete author intent.
6. Add structural scaffolding only when requested or mechanically derivable
   from existing headings. Never generate filler bullets or prose.

Run the repository's narrowest relevant parser, formatter, or content build
while iterating, then its required publication gate once before completion.
Route verbose output to a log and report the exit status plus a concise failure
tail rather than dumping the whole log.

## Report

Summarize files and assets changed, mechanical fixes applied, unresolved
publish blockers, editorial questions handed off, and verification commands
with results. If no edits are safe, leave the files unchanged and explain why.
