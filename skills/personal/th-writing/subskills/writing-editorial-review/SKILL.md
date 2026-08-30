---
name: writing-editorial-review
description: Review a blog post for publication readiness across narrative, structure, scannability, factual risk, tone, and reader usefulness. Return evidence-backed findings without silent rewrites.
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
    - OpenAI Codex
  status: active
  last_reviewed: "2026-08-31"
---

# Writing Editorial Review

Review an existing blog post as an editor. Preserve the author's voice and
separate findings from mutation: quote the relevant passage, explain the
reader impact, and suggest the smallest useful fix. Apply edits only when the
user explicitly asks for them.

## Resolve the draft

- Use the supplied text or path. If none is supplied, inspect likely post
  locations (`blog/`, `posts/`, `content/`, and `index.md`/`index.mdx`).
- When several plausible drafts remain, ask one narrow selection question.
- Read project publishing conventions before judging frontmatter or assets.
- Infer genre, audience, and reader goal from the draft; ask only when a real
  ambiguity would change the review.

## Review pass

Check the following in one coherent pass, scaling depth to the draft:

1. **Publication blockers** — invalid or incomplete required frontmatter,
   placeholder links/content, broken structure, or claims that create serious
   factual or safety risk.
2. **Narrative and structure** — opening stakes, logical order, useful
   headings, repetition, paragraph rhythm, and an ending that lands the point.
3. **Reader usefulness** — whether the promised audience can understand and
   act; flag missing timelines, examples, checklists, diagrams, or context only
   when they serve that reader.
4. **Voice and tone** — preserve intentional style; mark uncertainty rather
   than normalizing distinctive language. Flag accidental salesmanship,
   overstatement, or sensitivity risks.
5. **Language mechanics** — identify consequential grammar, tense, pronoun,
   and spelling problems without turning the report into an exhaustive lint
   dump.
6. **Factual risk** — identify surprising, contentious, numerical, absolute,
   or load-bearing claims. Distinguish personal experience from general claims.

Verify only the highest-impact factual claims when the user requests fact
checking or publication readiness requires it. Prefer current primary or
authoritative sources, state uncertainty, and classify each checked claim as
supported, partly supported, disputed, contradicted, or unverifiable. Never
invent a citation. Keep quoted source text brief.

## Report

Lead with a verdict: **ready**, **needs revision**, or **major rework**. Then
group findings by severity:

- **Critical**: publication blocker or materially misleading claim.
- **Recommended**: meaningful improvement to comprehension, structure, or
  trust.
- **Optional**: polish that does not determine readiness.

For every finding include the heading or location, a short excerpt, why it
matters, and a concrete fix direction. End with counts by severity and the
smallest next pass. If there are no findings, say so directly; do not manufacture
work to fill the report.
