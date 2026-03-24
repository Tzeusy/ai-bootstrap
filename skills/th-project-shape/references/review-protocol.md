# Review Protocol: Subagent-Based Independent Review

Generated shape documents must be reviewed by independent agents to catch context bias — the tendency for the same LLM that wrote a document to overlook its own blind spots.

## Why Independent Review Matters

When an LLM writes vision.md and then reviews it, it is primed by its own generation context. It will:
- Overlook gaps it didn't think of during generation
- Accept its own framings as natural rather than questioning them
- Miss contradictions between documents because it holds the "intended meaning" in context

Independent review breaks this by giving a fresh agent only the document, not the generation context.

## Review Architecture

```
Generator Agent (highest capability model, max thinking)
  ↓ produces draft document
  ↓
Review Agent 1: Coherence (fresh context, no generation history)
  ↓ findings
Review Agent 2: Adversarial (fresh context, no generation history)
  ↓ findings
Review Agent 3: Cross-Pillar (fresh context, reads all pillars)
  ↓ findings
  ↓
Generator Agent: incorporates findings, revises
  ↓
[Optional: second review round if major issues found]
```

## Subagent Specifications

### Review Agent 1: Coherence Review

**Prompt pattern:**
```
You are reviewing a project shape document. You have NOT seen the conversation
that produced this document. Read it with completely fresh eyes.

Document type: [heart-and-soul/vision.md | law-and-lore/rfc | etc.]
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
- [docs/heart-and-soul/vision.md]: [content]
- [docs/heart-and-soul/v1.md]: [content]
- [docs/law-and-lore/rfcs/...]: [content]
- [docs/lay-and-land/components.md]: [content]
- [openspec/...]: [content if exists]

Evaluate:
1. TRACEABILITY — Can every RFC design decision trace to a doctrine principle?
   List orphaned decisions (no doctrine backing) and orphaned principles (no RFC implements them).
2. SCOPE ALIGNMENT — Does v1.md scope match what the RFCs define? Are there
   RFCs for deferred features or missing RFCs for v1 features?
3. TOPOLOGY-DOCTRINE FIT — Does the component map reflect the architectural
   principles? If doctrine says "X must never Y," does the topology enforce that?
4. VOCABULARY — Are terms used consistently across documents? Flag any term
   that means different things in different pillars.
5. GAPS — What questions does a new contributor still have after reading all of these?

Output: Ranked list of cross-pillar issues, each with affected documents and fix guidance.
```

## Execution Protocol

### For New Projects (bootstrapping)

1. **Generate** — Use the consultative bootstrapping protocol to produce each document
2. **Review sequentially** — After each document, run Review Agents 1 and 2 on it
3. **Revise** — Incorporate findings, re-synthesize if needed
4. **Cross-review** — After all pillars exist, run Review Agent 3
5. **Present to user** — Show the reviewed documents with a summary of what changed during review

### For Existing Projects (maintenance)

1. **Detect drift** — When code changes diverge from docs, flag for review
2. **Update** — Generate updated sections
3. **Review the delta** — Run Review Agents 1 and 2 on just the changed sections
4. **Cross-check** — Run Review Agent 3 if changes affect cross-pillar coherence
5. **Present to user** — Show diff with review findings

### Iteration Rules

- **First round**: Always run both Coherence and Adversarial reviews
- **Second round**: Only if first round produced REVISE verdicts on major items
- **Third round**: Stop. If three rounds haven't converged, the issue is upstream (unclear user intent) — return to consultative interview
- **Cross-pillar**: Run after every pillar is added or substantially changed

## Model Configuration for Review Agents

- Review agents should use a capable model but don't need extended thinking — they're evaluating, not generating
- The key requirement is **fresh context** — the review agent must NOT have access to the generation conversation
- Use `Agent` tool with a clean prompt (no conversation history) to ensure independence
- Each review agent runs in its own invocation — do not batch reviews in a single agent

## Anti-Patterns

- **Self-review** — The generator reviewing its own output in the same context. This catches typos, not blind spots.
- **Rubber-stamp reviews** — Review agents that say "looks good" without evidence. A useful review always has findings.
- **Review without mandate** — Running reviews but not incorporating findings. Every REVISE verdict must be addressed or explicitly overruled by the user.
- **Infinite review loops** — More than 2 rounds means the problem is upstream. Stop reviewing and return to the user.
