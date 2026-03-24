# Consultative Bootstrapping Protocol

How to extract project shape from a human's head through structured dialogue. This is not a template-filling exercise — it's Socratic extraction followed by adversarial refinement.

## Core Principle

The human knows what they want to build but often can't articulate it precisely. Your job is to:
1. Ask questions that surface implicit assumptions
2. Challenge vague or contradictory answers
3. Synthesize what they *mean* (not just what they *said*)
4. Write docs they recognize as their own thinking, made sharper

## Model and Thinking Configuration

Generating project shape documents demands the highest reasoning quality available. These are constitutional documents — errors cascade into every downstream decision.

- **Use the most capable model available** (e.g., Opus with extended thinking)
- **Enable maximum thinking/reasoning budget** for synthesis steps
- **Never rush generation** — a flawed vision.md costs more than a delayed one
- **Prefer depth over speed** — one excellent document beats three mediocre ones

## Phase 1: Discovery Interview

### The Opening Question

Don't start with "what are you building?" — that gets feature lists. Start with:

> **"What problem exists in the world that shouldn't?"**

or

> **"If this project succeeds perfectly, what changes for the people who use it?"**

These questions surface motivation and values, not features.

### Core Interview Tracks

Run these tracks sequentially. Each track should be 3-5 exchanges deep before moving on.

#### Track 1: Identity (feeds → vision.md)

| Question | Purpose |
|----------|---------|
| "What problem exists that shouldn't?" | Surface core motivation |
| "Who feels this problem most acutely?" | Identify primary user |
| "What do they do today instead?" | Understand the status quo |
| "What would they say if they saw this working?" | Define success in human terms |
| "What is this NOT?" | Prevent scope creep — often more revealing than "what is this" |

**Challenge patterns:**
- If the answer is vague ("make X better"), push: "Better how? For whom? What specifically isn't working?"
- If the answer is a feature ("it'll have a dashboard"), redirect: "What does the dashboard help someone *do* that they can't do now?"
- If the answer is a technology ("we'll use Rust"), redirect: "What property of the system requires that choice?"

#### Track 2: Boundaries (feeds → v1.md)

| Question | Purpose |
|----------|---------|
| "If you could only ship three things, what are they?" | Force prioritization |
| "What would you love to build but shouldn't build first?" | Identify deferrals |
| "What's the smallest thing that would be genuinely useful?" | Find the MVP boundary |
| "What would make you embarrassed to ship?" | Find the quality bar |
| "Who will use v1? How is that different from the eventual audience?" | Scope the user base |

**Challenge patterns:**
- If everything is "v1": "You said X, Y, Z, W are all v1. If you had to cut one, which goes? Why?"
- If nothing is deferred: "What's the hardest thing on this list? What if that took 3x longer than expected — what would you cut?"
- If the quality bar is vague: "Give me a number. Latency under what? Uptime of what?"

#### Track 3: Principles (feeds → vision.md non-negotiables)

| Question | Purpose |
|----------|---------|
| "What's a design decision you'd refuse to compromise on, even under pressure?" | Surface non-negotiables |
| "What's a mistake you've seen other projects make that you want to avoid?" | Surface anti-patterns |
| "If a new contributor made a PR that worked but violated X, would you reject it?" | Test if a principle is actually non-negotiable |
| "Rank these in order: speed, correctness, simplicity, extensibility" | Force trade-off articulation |

**Challenge patterns:**
- If they say "all of them are non-negotiable": "If two conflict — say performance vs simplicity — which wins?"
- If a principle sounds like a platitude ("clean code"): "Give me a concrete example of what 'clean code' means here. What would you reject?"

#### Track 4: Architecture (feeds → about/heart-and-soul/architecture.md, about/lay-and-land/)

| Question | Purpose |
|----------|---------|
| "Draw me the system on a whiteboard — what are the boxes and arrows?" | Surface mental model |
| "Where does data enter? Where does it leave?" | Map data flow |
| "What breaks if this component goes down?" | Find critical paths |
| "What's the trust boundary? What can't talk to what?" | Map security boundaries |

#### Track 5: Design Contracts (feeds → about/law-and-lore/)

Only pursue this track if the project is past the idea stage:

| Question | Purpose |
|----------|---------|
| "What technical decisions have you already made that are hard to reverse?" | Identify load-bearing contracts |
| "What protocols/formats/APIs does this system expose or consume?" | Map integration contracts |
| "What performance budgets matter?" | Extract quantitative constraints |

## Phase 2: Synthesis

After the interview, synthesize — don't transcribe. The human said many things; your job is to find the coherent thread.

### Synthesis Steps

1. **Extract the thesis** — One paragraph that captures what this project IS, distilled from Track 1 answers
2. **Extract the anti-thesis** — What this project IS NOT, from Track 1 "what is this not" + Track 2 deferrals
3. **Extract principles** — 5-7 non-negotiable rules from Track 3, stated as constraints ("X must never Y")
4. **Extract the scope** — V1 ships/defers from Track 2
5. **Extract the topology** — Component map from Track 4

### Synthesis Rules

- **Use the human's language** — If they said "the screen is sovereign," keep that phrase. Don't normalize it to corporate-speak.
- **Make implicit trade-offs explicit** — If they ranked speed > correctness, state it: "When speed and correctness conflict, speed wins."
- **Test each principle** — For every non-negotiable, ask: "Can I construct a scenario where this would be violated? Would the user actually reject that?"
- **Flag contradictions** — If Track 1 says "simple" but Track 4 reveals six interconnected services, name the tension.

## Phase 3: Presentation and Challenge

Present the synthesized documents to the user for review. This is not "does this look right?" — it's adversarial validation.

### Challenge the User's Own Docs

After presenting the synthesis:

1. **"I noticed you said X but also Y — which is it?"** — Surface contradictions you found
2. **"Your non-negotiable #3 would prevent doing Z — is that intentional?"** — Test consequences
3. **"This vision implies A, B, and C as components. Is that the right decomposition?"** — Verify the topology matches the vision
4. **"v1 ships X, but that depends on Y which is deferred. How do you handle that?"** — Find dependency gaps

### Iterate Until Stable

The user should read the docs and feel: "Yes, this is what I mean, but sharper than I could have said it."

If they say "this isn't quite right" — don't patch. Ask *why* it's wrong, return to the relevant interview track, and re-synthesize.

## Phase 4: Independent Review

See `references/review-protocol.md` for the subagent review process. Generated docs must be reviewed by independent agents before being committed.

## Anti-Patterns in Consultative Bootstrapping

- **Template-filling** — Handing the user templates and saying "fill these in." This produces bureaucratic docs, not doctrine.
- **Accepting first answers** — The first answer to "what is this?" is usually a feature list. Push deeper.
- **Writing for the LLM** — Doctrine is for humans first. If it reads like a system prompt, rewrite it.
- **Skipping the NOT** — What a project is NOT is often more valuable than what it is. Always extract this.
- **Consensus without tension** — If everything sounds harmonious, you haven't found the trade-offs yet. Every real project has tensions.
