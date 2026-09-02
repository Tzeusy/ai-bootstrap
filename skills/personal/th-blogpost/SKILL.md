---
name: th-blogpost
description: >
  Use for any work on a blog post — deep editorial review for publication
  readiness (narrative, structure, scannability, factual risk, tone) or
  mechanical publish-hardening (frontmatter normalization, MD/MDX safety
  fixes, structural scaffolding, asset hygiene). Triggers: "review my blog post", "edit this post", "is
  this post ready to publish", "format this post for the blog", "fix the
  frontmatter", "make this MDX build".
metadata:
  owner: tze
  authors:
    - tze
    - Claude Fable 5
  status: active
  last_reviewed: "2026-07-19"
---

# TH Blogpost

Superskill router for blog-post work. Two subskills live under `subskills/`,
each a complete skill package, discovered lazily — load **at most one**
subskill body per task.

The split is editorial judgment vs. mechanical pipeline: the editor changes
nothing silently and reports findings; the formatter changes files but
exercises minimal editorial judgment.

## Routing table

| Task intent | Subskill | Typical trigger |
|---|---|---|
| Editorial review for publication readiness: narrative, structure, scannability, factual risk, tone, reader usefulness. Findings only — no silent rewrites. | [subskills/blogpost-editor/SKILL.md](subskills/blogpost-editor/SKILL.md) | "review/edit my post", "is this ready to publish", "critique this draft" |
| Publish-hardening: frontmatter normalization, MD/MDX safety fixes, structural scaffolding, asset hygiene. Preserves the author's voice and meaning. | [subskills/blogpost-formatter/SKILL.md](subskills/blogpost-formatter/SKILL.md) | "format this for the blog", "fix the frontmatter", "make this build/render" |

## Routing rules

- **Judgment vs. mechanics**: "is the writing good / ready" → editor;
  "make it build / conform" → formatter. A full publish pass runs editor
  first, then formatter — as two sequential subskill loads, not one merged
  pass.
- **Fallback**: writing a post from scratch or non-blog documentation fits
  neither row — draft with general writing guidance, then return here for review and hardening.

## Discover subskills

The routing table above is the primary index. Verify frontmatter only if the
table seems stale:

```bash
PKG="$(dirname "<absolute-path-to-this-SKILL.md>")"
rg -n "^name:|^description:" "$PKG"/subskills/*/SKILL.md
```
