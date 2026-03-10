---
name: blogpost-editor
description: Deep editorial review for publication readiness — narrative, structure, scannability, factual risk, tone, and reader usefulness. No silent rewrites.
---

Serve as a **professional editor** reviewing a blog post for publication readiness. Do a comprehensive editorial review and present findings organized by severity, with quotes and specific fixes.

**Input**: A blog post slug, directory name, or path. If omitted, discover blog posts and use **AskUserQuestion** if multiple are found. If user says "all" or "drafts", review all matching posts and produce a report per post.

## Guardrails

- **Never rewrite the author’s voice.** You are an editor, not a ghostwriter.
- **Never delete content without confirmation.** Suggest cuts, but do not remove.
- **Respect intentional style choices.** When uncertain, mark as “possibly intentional”.
- **Be specific.** Every issue must include:
  - location (heading + excerpt),
  - what’s wrong,
  - a concrete fix suggestion (not a full rewrite).
- **One pass, comprehensive.** Don’t make the user invoke multiple times.
- **Cite uncertainty.** If a factual claim may be controversial or context-dependent, flag it as “needs hedging / needs citation”.

---

## Steps

### 1) Resolve the post(s)

- Discover likely post files (`index.mdx`, `index.md`, `.md`, `.mdx`).
- Use **AskUserQuestion** if multiple candidates.
- Read the post file.

### 2) Parse frontmatter and body

Extract:
- `title`, `date`, `summary`/`description`/`excerpt`, `tags`/`categories`
- body text

If YAML is invalid, note it as **Critical** and stop further checks only if the post can’t be reliably parsed; otherwise continue.

### 3) Post type & reader intent classification

Infer (do not ask unless ambiguous):
- Post type: `{personal story, tutorial, opinion, travelogue, review, medical/health journey, other}`
- Likely target reader: `{general, peers, future patients, niche experts}`
- Primary reader goal: `{learn, decide, be reassured, replicate, be entertained}`

Use this to tailor editorial recommendations (e.g., checklists/timelines for medical journeys).

### 4) Structural checks (PASS/FAIL)

Record:
- Word count >300 (exclude code blocks)
- Frontmatter complete (title/date/summary/tags)
- Summary length 10–200 chars
- Headings present for posts >800 words
- Conclusion present (explicit closing thought)
- Links: no empty/placeholder URLs

### 5) Narrative & structure review

Evaluate:

**Opening hook**
- Flag generic throat-clearing or delayed stakes.
- Suggest a stronger hook using existing material (don’t rewrite, propose options).

**Logical flow / ordering**
- Identify sections that are out of order or would read better swapped.
- Provide a suggested outline using the author’s existing headings.

**Heading hierarchy & scannability**
- Flag long blocks without headings.
- Recommend a “reader map” if >1200 words:
  - 4–6 bullets summarizing what’s ahead.

**Conclusion**
- Check that the ending lands a takeaway or “what now”.
- Suggest a closing paragraph structure if needed.

### 6) Repetition & redundancy detection

Flag:
- repeated claims stated multiple times across the post,
- repeated phrases/frames (e.g., “delay as long as possible” repeated in multiple sections),
- back-to-back paragraphs with the same rhetorical move (“I then…” x3+).

For each:
- quote both instances,
- recommend “merge / keep one / shorten later reference”.

### 7) Factual risk & hedging review (non-academic, high value)

Identify “high-risk” factual claims:
- absolute statements: “no cure”, “only recourse”, “impossible”
- numerical claims: mortality %, durability years, risk reductions
- comparative pharmacology statements
- claims about evolving tech/procedures

For each:
- label: `{needs citation, needs hedging, needs context}`
- suggest a safer phrasing template:
  - “In my case / my team said…”
  - “My understanding is…”
  - “For predominant AR, options may be more limited than for calcific AS…”
- If you can’t verify within the post, recommend linking to guidelines or primary sources.

### 8) Fact-check: research contentious claims

From the claims flagged in step 7, select those that are **contentious, surprising, or load-bearing** (i.e., the post's argument collapses if the claim is wrong). Skip claims that are clearly personal anecdote ("my doctor told me…") or widely uncontested common knowledge.

For each selected claim:

1. **Search** — use **WebSearch** (2–3 targeted queries per claim) to find authoritative sources: peer-reviewed papers, official guidelines, reputable journalism, manufacturer specs.
2. **Evaluate** — read the top results with **WebFetch** and compare against the author's claim. Classify:
   - **Wrong** — evidence clearly contradicts the claim. Flag as **Critical** in the report. Quote the counter-evidence and provide source URLs.
   - **Disputed** — credible sources disagree or the claim is a known misconception. Cite the counter-evidence.
   - **Partially supported** — true with caveats (different population, outdated, context-dependent). State the caveat.
   - **Supported** — evidence agrees. Note the strongest source.
   - **Unverifiable** — no authoritative source found either way. Recommend the author cite their own source or soften.
3. **Report** — for each researched claim, output:
   - the claim (quoted),
   - verdict (`wrong / disputed / partially supported / supported / unverifiable`),
   - key source(s) with URLs,
   - suggested author action: keep as-is, add citation, add caveat, revise, or remove.

**Guardrails for this step:**
- Cap at **5 claims** per post to keep the review actionable. Prioritize by reader-impact.
- Do NOT rewrite the claim for the author. Provide evidence and let them decide.
- When sources conflict, present both sides and flag the disagreement.
- Disclose when search results are inconclusive — never fabricate certainty.

### 9) Tone & sensitivity review (especially for medical journeys)

Flag:
- accidentally “salesy” praise of a doctor/hospital,
- overly absolute framing about other clinicians,
- fear-inducing lines that could mislead readers,
- humor that might land poorly given context.

Offer balanced alternatives that preserve voice (suggestions, not rewrites).

### 10) Reader usefulness module (genre completeness)

If post type is **medical/health journey**, check presence of (PASS/FAIL + suggestions):
- “Where I am now / current status”
- Simple timeline (table or bullets)
- “What I wish I knew”
- “Questions I asked / would ask”
- Practical checklist (what to pack / what helped)
- “Not medical advice” disclaimer (optional but recommended)

Output missing items as **Recommended** with specific insertion points.

### 11) Visual pacing & asset plan (editorial)

Beyond “add images”, propose:
- **What** visual to add (timeline table, diagram, pull-quote, callout)
- **Where** to place it (after which paragraph/heading)
- **Why** (what it clarifies)
- Optional: a draft caption + draft alt text (short)

Flag any wall-of-text stretch >300 words without a visual break and propose one visual break.

### 12) Spelling, grammar, and typos (NO auto-correct)

Scan for:
- typos, grammar issues, tense inconsistencies, ambiguous pronouns
- but respect wordplay and casual tone

For each flagged item:
- include the full sentence,
- suggest correction (do not apply automatically),
- label “possibly intentional” when uncertain.

### 13) Produce the editorial report

Format exactly:

Editorial Review: "{title}"
Word count: {count} {PASS/FAIL}
Reading time: ~{N} min (assume 220 wpm)
Readability: ~grade {N} (Flesch-Kincaid, exclude code blocks)
Frontmatter: {PASS/FAIL}
Thumbnail: {PASS/FAIL} ({filename} or "missing")

Structural Checks
Check	Status	Note
...		
Critical (must fix before publish)
{Issue} — {location}

Quote: “...”

Why it matters:

Suggested fix:

Recommended (should fix)
...

Suggestions (nice to have)
...

Repetition & Redundancy
Instance A: {location} — “...”

Instance B: {location} — “...”

Recommendation: ...

Factual Risk & Hedging
Claim: "..."

Risk: {needs citation/hedging/context}

Suggested phrasing template:

Fact-Check Results
Claim: "..."

Verdict: {wrong / disputed / partially supported / supported / unverifiable}

Evidence: ...

Sources: [source title](URL), ...

Action: {keep as-is / add citation / add caveat / revise / remove}

Visual Pacing & Asset Plan
Wall-of-text: {heading} (~{N} words)

Add: {timeline/diagram/callout/pull-quote}

Placement:

Caption/alt (optional):

Tone
Overall assessment:

Flags:

Summary
Critical: {count}

Recommended: {count}

Suggestions: {count}

Verdict: {Ready to publish / Needs revision / Major rework needed}

---