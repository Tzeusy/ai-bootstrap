# Review Protocol: Subagent-Based Independent Review

Generated shape docs must be reviewed by independent agents to catch context bias — the same LLM that wrote a doc overlooks its own blind spots.

## Why Independent Review Matters

An LLM that writes vision.md then reviews it is primed by its own generation context. It will:
- Overlook gaps it didn't think of during generation
- Accept its own framings as natural rather than questioning them
- Miss cross-doc contradictions because it holds the "intended meaning" in context

Independent review breaks this — give a fresh agent only the document, not the generation context.

Same principle one step earlier: partition substantive generation/curation too. A dedicated pillar worker with a tighter context window produces cleaner doctrine, contracts, specs, topology, and standards than one monolithic agent carrying all pillars.

## Generation And Curation Partitioning

When the task justifies dispatch, prefer one investigation/refinement subagent per pillar, or per coherent doc cluster within a pillar:

- `heart-and-soul/vision.md` + `v1.md` → one doctrine worker
- `legends-and-lore/rfcs/0001-*.md` + review notes → one contracts worker
- `lay-and-land/components.md` + `data-flow.md` → one topology worker
- `craft-and-care/engineering-bar.md` + `testing-and-verification.md` → one standards worker

Don't split so aggressively the coordinator spends more time stitching than the workers save. Targeted context windows, not maximal fan-out.

## Review Architecture

<!-- [DIAGRAM: review-architecture]
Style: conceptual, simple. Use /th-engineering (excalidraw-diagram).
Layout: vertical pipeline with fan-out and convergence.
Elements:
  - Top: hero rectangle "Generator Agent" labeled "(highest capability model, max thinking)", warm/primary color
  - Arrow down labeled "produces draft document"
  - Fan-out to 3 parallel review agents (side-by-side rectangles, all in a cool/secondary color):
    - "Review Agent 1: Coherence" — subtitle "fresh context, no generation history"
    - "Review Agent 2: Adversarial" — subtitle "fresh context, no generation history"
    - "Review Agent 3: Cross-Pillar" — subtitle "fresh context, reads all pillars"
  - Each has a downward arrow labeled "findings"
  - Convergence: all 3 findings arrows merge into a single arrow pointing down
  - Bottom: "Generator Agent: incorporates findings, revises" — same color as top
  - Dashed cycle arrow from bottom back to the fan-out, labeled "Optional: second round if major issues"
Argument: Independence is the key — review agents have NO access to generation context. The fan-out ensures parallel, unbiased evaluation.
-->

## Subagent Specifications

### Review Agent 1: Coherence Review

**Prompt pattern:**
```
You are reviewing a project shape document. You have NOT seen the conversation
that produced this document. Read it with completely fresh eyes.

Document type: [heart-and-soul/vision.md | legends-and-lore/rfc | etc.]
Document: [full content]

Evaluate:
1. CLARITY — Can a new contributor understand this without additional context?
   Flag any sentence that requires insider knowledge to parse.
2. COMPLETENESS — Are there obvious questions this document should answer but doesn't?
   List them.
3. INTERNAL CONSISTENCY — Does the document contradict itself anywhere?
   Quote the contradicting passages.
4. TESTABILITY — For each principle/rule/requirement: could you write a test or
   construct a scenario that would detect a violation? If not, it's too vague.
5. VOICE — Does this read like doctrine (human-authored conviction) or like
   LLM-generated filler? Flag any passage that sounds generic or platitudinous.

Output format:
- PASS items (brief)
- FINDINGS (numbered, with quoted evidence and specific fix suggestions)
- VERDICT: ACCEPT / REVISE (with priority-ordered revision list)
```

### Review Agent 2: Adversarial Review

**Prompt pattern:**
```
You are a skeptical reviewer. Your job is to find problems, not confirm quality.
You have NOT seen the conversation that produced this document.

Document type: [type]
Document: [full content]

Attack vectors:
1. CONTRADICTIONS — Find statements that conflict with each other.
2. ESCAPE HATCHES — Find principles that are so vague they permit anything.
   A good non-negotiable has a clear violation case.
3. MISSING TRADE-OFFS — Find places where two goals are stated without
   acknowledging the tension between them.
4. SCOPE LEAKS — Find places where v1 scope implicitly requires deferred items.
5. WISHFUL THINKING — Find claims about the system that aren't grounded in
   technical reality (e.g., "real-time" without latency budgets).
6. CARGO CULT — Find principles copied from other projects that don't fit this one.

For each finding, provide:
- The specific text
- Why it's a problem
- A concrete question the author should answer to fix it

VERDICT: List the top 3 issues that would cause the most downstream damage if unfixed.
```

### Review Agent 3: Cross-Pillar Review

Only run this after multiple pillars exist. This agent reads all pillars together.

**Prompt pattern:**
```
You are reviewing the coherence BETWEEN project shape documents.
Read all of the following documents, then evaluate their alignment.

Documents:
- [about/heart-and-soul/vision.md]: [content]
- [about/heart-and-soul/v1.md]: [content]
- [about/craft-and-care/...]: [content]
- [about/legends-and-lore/rfcs/...]: [content]
- [about/lay-and-land/components.md]: [content]
- [openspec/...]: [content if exists]

Evaluate:
1. TRACEABILITY — Can every RFC design decision trace to a doctrine principle?
   List orphaned decisions (no doctrine backing) and orphaned principles (no RFC implements them).
2. SCOPE ALIGNMENT — Does v1.md scope match what the RFCs define? Are there
   RFCs for deferred features or missing RFCs for v1 features?
3. TOPOLOGY-DOCTRINE FIT — Does the component map reflect the architectural
   principles? If doctrine says "X must never Y," does the topology enforce that?
4. EXECUTION FIT — Do the doctrine, RFCs, specs, and topology imply verification,
   observability, review, compatibility, documentation, or maintenance obligations
   that are made explicit in `craft-and-care`? List missing or weakly specified standards.
5. VOCABULARY — Are terms used consistently across documents? Flag any term
   that means different things in different pillars.
6. GAPS — What questions does a new contributor still have after reading all of these?

Output: Ranked list of cross-pillar issues, each with affected documents and fix guidance.
```

## Execution Protocol

### For New Projects (bootstrapping)

1. **Generate** — consultative bootstrapping protocol per document, preferring per-pillar subagents when substantial
2. **Review sequentially** — after each doc, run Review Agents 1 and 2
3. **Revise** — incorporate findings, re-synthesize if needed
4. **Cross-review** — after all pillars exist, run Review Agent 3
5. **Present** — reviewed docs + summary of what changed during review

### For Existing Projects (maintenance)

1. **Detect drift** — code diverges from docs → flag for review
2. **Update** — generate updated sections, per-pillar curation subagents when multiple pillars affected
3. **Review the delta** — Review Agents 1 and 2 on changed sections only
4. **Cross-check** — Review Agent 3 if changes affect cross-pillar coherence
5. **Present** — diff + review findings

### Iteration Rules

- **First round**: always run both Coherence and Adversarial
- **Second round**: only if first round produced REVISE verdicts on major items
- **Third round**: stop. Three non-converging rounds means the issue is upstream (unclear user intent) — return to interview
- **Cross-pillar**: after every pillar added or substantially changed

## Model Configuration for Review Agents

- Capable model, no extended thinking needed — evaluating, not generating
- Key requirement: **fresh context** — review agent must NOT see the generation conversation
- Use `Agent` tool with a clean prompt (no history) for independence
- Each review agent runs in its own invocation — do not batch reviews

## Fallback When Subagents Are Unavailable

Do **not** skip review. Lite fallback:

1. **Coherence pass** yourself using Review Agent 1 criteria
2. **Adversarial pass** yourself using Review Agent 2 criteria
3. Summarize top unresolved risks explicitly
4. Present doc + risks to user for validation before treating it as settled

Weaker than true independent review — say so plainly. The fallback preserves rigor by making review modes explicit rather than silently collapsing generation and review.

## Anti-Patterns

- **Self-review** — generator reviewing its own output in-context. Catches typos, not blind spots.
- **Rubber-stamp** — "looks good" without evidence. A useful review always has findings.
- **Review without mandate** — running reviews but not incorporating findings. Every REVISE must be addressed or explicitly overruled by the user.
- **Infinite loops** — >2 rounds means the problem is upstream. Stop and return to the user.
